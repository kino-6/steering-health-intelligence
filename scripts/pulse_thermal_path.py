#!/usr/bin/env python3
"""Pulse self-heating as a measure of the thermal path (docs/198 -> docs/199).

Executes the protocol pre-registered in docs/198 without modification.

Every document from docs/165 onward used only the steadyState block of the
NASA .mat files. The transient block holds 1000-point waveforms at 1 us, and
across the 400 us gate-on pulse the drain current is near constant while Vds
climbs and saturates. That climb is the junction heating itself: mobility
falls with temperature, so holding the current needs more Vds. The device is
its own thermometer.

    t0 = edge + 10 us      after switching settles
    t1 = edge + 390 us     before turn-off
    Rth_pulse = (Vds(t1) - Vds(t0)) / mean(Vds * Id) over [t0, t1]      [V/W]

V/W, not degC/W: no Vds-to-junction calibration is public, so only ratios
between runs of one device carry meaning, and that assumes the calibration
constant is stable. Declared in docs/198, not discovered here.

The steady flange-to-package offset that defeated docs/189 (2) is a DC term.
It shifts where the pulse starts; it does not obstruct the pulse response.

Data: NASA PCoE MOSFET thermal overstress ageing, public domain.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
import scipy.io as sio
from scipy import stats

import mosfet_precursor as mos

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "pulse_thermal_path.tsv"

GATE_HI = 7.0        # gate signal threshold used to find the edge
T0, T1 = 10, 390     # samples after the edge, 1 us each (docs/198)
N_WAVE = 500         # waveforms averaged per run (docs/198)
BASE_RUNS = (1, 2, 3)


def run_pulse(z, dev: int, run: int):
    name = f"MOSFET_Thermal_Overstress_Aging_v0/Test_{dev}_run_{run}.mat"
    p = mos.CACHE / name
    if not p.exists():
        z.extract(name, mos.CACHE)
    tr = np.ravel(sio.loadmat(p, squeeze_me=True, struct_as_record=False)
                  ["measurement"].transient)
    vs, is_ = [], []
    for rec in tr[:N_WAVE]:
        d = rec.timeDomain
        g = np.ravel(d.gateSignalVoltage)
        hi = np.flatnonzero(g > GATE_HI)
        if hi.size == 0:
            continue
        e = int(hi[0])
        v = np.ravel(d.drainSourceVoltage)
        i = np.ravel(d.drainCurrent)
        if e + T1 >= len(v):
            continue
        vs.append(v[e:e + T1 + 1])
        is_.append(i[e:e + T1 + 1])
    if len(vs) < 10:
        return None
    v = np.mean(vs, axis=0)
    i = np.mean(is_, axis=0)
    dv = float(v[T1] - v[T0])
    p_bar = float(np.mean(v[T0:T1 + 1] * i[T0:T1 + 1]))
    # thermal time constant: first sample reaching 63% of the rise
    tgt = v[T0] + 0.632 * dv
    idx = np.flatnonzero(v[T0:T1 + 1] >= tgt)
    tau = float(idx[0]) if idx.size else float("nan")
    return dict(rth=dv / p_bar, dv=dv, p=p_bar, tau=tau,
                v0=float(v[T0]), v1=float(v[T1]), i_mean=float(np.mean(i[T0:T1 + 1])),
                n=len(vs))


def main() -> None:
    z = zipfile.ZipFile(mos.ZIP)
    per_dev, rows = {}, []
    for dev in mos.DEVICES:
        print(f"--- Test_{dev}")
        print(f"{'run':>5}{'Vds(t0)':>10}{'Vds(t1)':>10}{'Id':>8}{'P[W]':>8}"
              f"{'dV[V]':>8}{'Rth[V/W]':>11}{'tau[us]':>9}{'waves':>7}")
        vals = {}
        for run in range(1, mos.N_RUNS + 1):
            r = run_pulse(z, dev, run)
            if r is None:
                print(f"{run:>5}   no usable waveform")
                continue
            vals[run] = r
            print(f"{run:>5}{r['v0']:>10.3f}{r['v1']:>10.3f}{r['i_mean']:>8.3f}"
                  f"{r['p']:>8.2f}{r['dv']:>8.3f}{r['rth']:>11.5f}{r['tau']:>9.0f}{r['n']:>7}")
            rows.append((dev, run, r['v0'], r['v1'], r['i_mean'], r['p'],
                         r['dv'], r['rth'], r['tau']))
        per_dev[dev] = vals
        base = [vals[r]['rth'] for r in BASE_RUNS if r in vals]
        if base and vals:
            b, sd = float(np.mean(base)), float(np.std(base, ddof=1))
            last = max(vals)
            print(f"      baseline {b:.5f} +/- {sd:.5f} (3sd = {3*sd:.5f}), "
                  f"run {last} = {vals[last]['rth']:.5f} "
                  f"({vals[last]['rth']/b - 1:+.1%})\n")

    print("=" * 78)
    t1 = t2 = 0
    ratios = []
    for dev, vals in per_dev.items():
        runs = sorted(vals)
        rho = stats.spearmanr(runs, [vals[r]['rth'] for r in runs]).statistic
        base = [vals[r]['rth'] for r in BASE_RUNS if r in vals]
        b, sd = float(np.mean(base)), float(np.std(base, ddof=1))
        early = vals.get(4)
        lead = bool(early and (early['rth'] - b) > 3 * sd)
        ratio = vals[max(vals)]['rth'] / b
        ratios.append(ratio)
        t1 += rho >= 0.8
        t2 += lead
        print(f"Test_{dev}  rho={rho:+.3f}  run4 above 3sd: {'yes' if lead else 'no ':<3}"
              f"  final/baseline = {ratio:.3f}")
    print(f"\nT1 monotone rise, rho >= 0.8      : {t1}/6 -> {'PASS' if t1 >= 4 else 'FAIL'} (needs 4)")
    print(f"T2 above baseline scatter at run 4 : {t2}/6 -> {'PASS' if t2 >= 4 else 'FAIL'} (needs 4)")
    print(f"T3 final / baseline                : {min(ratios):.3f} .. {max(ratios):.3f}")
    print(f"   docs/197 needs k; this is an OVERESTIMATE of k -- a 400 us pulse sees")
    print(f"   the near-junction path, not the whole steady-state one (docs/198).")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("device\trun\tvds_t0\tvds_t1\tid_mean\tpower_w\tdv_v\trth_v_per_w\ttau_us\n")
        for r in rows:
            out.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                                for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
