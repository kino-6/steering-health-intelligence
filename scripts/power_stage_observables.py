#!/usr/bin/env python3
"""Do the unopened power-stage observables fire? (docs/272 -> docs/273)

Executes the protocol pre-registered in docs/272.

docs/271 concluded the power stage does not fire, using one quantity from the
steady-state records -- which docs/199 had already shown is not an
on-resistance. The transient records in the same dataset carry gate voltage and
current waveforms that no analysis in this repository has opened. T14 says not
to declare absence before changing the search axis.

Three candidates, fixed in docs/272 before running, and no fourth afterwards:

    gate rise time      samples for gate-source voltage to go 10% to 90%
    gate plateau        median gate-source voltage across the middle of the wave
    conduction drop     median drain-source voltage while drain current is
                        above half its maximum

Each is run through the same machinery as the recorder: first third as
fingerprint, running mean on the rest, threshold from the healthy stretch at
one alarm per hour.

Data: NASA PCoE MOSFET, public domain.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np
import scipy.io as sio

sys.path.insert(0, str(Path(__file__).resolve().parent))
import element_v2 as el
import mosfet_precursor as mos
from slow_channel import slow_deviation

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / ".nasa_pcoe" / "MOSFET_Thermal_Overstress_Aging_v0"
OUT = ROOT / "data" / "power_stage_observables.tsv"

FP_FRAC = 1 / 3
NS = [20, 50, 100, 200]
FA_PER_HOUR, HOUR_SAMPLES = 1.0, 36000
HEALTHY_FRAC = 0.25


def gate_rise(vgs):
    lo, hi = np.min(vgs), np.max(vgs)
    if hi - lo <= 0:
        return np.nan
    a, b = lo + 0.1 * (hi - lo), lo + 0.9 * (hi - lo)
    ia = np.argmax(vgs >= a)
    ib = np.argmax(vgs >= b)
    return float(ib - ia) if ib > ia else np.nan


def gate_plateau(vgs):
    n = len(vgs)
    return float(np.median(vgs[n // 3: 2 * n // 3]))


def conduction_drop(vds, idr):
    m = np.max(idr)
    if m <= 0:
        return np.nan
    sel = idr > m / 2
    return float(np.median(vds[sel])) if sel.any() else np.nan


def transients(dev):
    """Every transient of a device, with the package temperature beside it.

    The rig ramps its setpoint, and four analyses in this repo died by reading
    that ramp as degradation (docs/199, 203, 234, 257). A fingerprint fitted
    against record order cannot normalise it, so each transient is matched to
    the nearest steady-state record in time and carries that temperature.
    """
    rows = []
    for run in (1, 2, 3):
        f = DATA / f"Test_{dev}_run_{run}.mat"
        if not f.exists():
            continue
        m = sio.loadmat(f, squeeze_me=True, struct_as_record=False)["measurement"]
        ss_t = np.array([e.timeEpoch for e in m.steadyState.flat])
        ss_T = np.array([e.timeDomain.packageTemperature for e in m.steadyState.flat])
        order = np.argsort(ss_t)
        ss_t, ss_T = ss_t[order], ss_T[order]
        for e in m.transient.flat:
            d = e.timeDomain
            vgs = np.asarray(d.gateSourceVoltage, dtype=float)
            vds = np.asarray(d.drainSourceVoltage, dtype=float)
            idr = np.asarray(d.drainCurrent, dtype=float)
            if vgs.size < 10:
                continue
            te = float(e.timeEpoch)
            j = int(np.clip(np.searchsorted(ss_t, te), 0, len(ss_T) - 1))
            rows.append((te, gate_rise(vgs), gate_plateau(vgs),
                         conduction_drop(vds, idr), float(ss_T[j])))
    rows.sort(key=lambda r: r[0])
    a = np.array(rows, dtype=float)
    return a


def evaluate(name, col, per_dev, op_col=0):
    """Fire count over devices for one quantity, best over the N grid.

    op_col picks what the fingerprint is fitted against: column 0 is record
    order, column 4 is the matched package temperature. Comparing the two is
    the whole point -- if a quantity only fires when the rig's own ramp is left
    in, it is the ramp that is firing.
    """
    best = None
    for n in NS:
        pool, series = [], {}
        for dev, a in per_dev.items():
            y = a[:, col]
            ok = np.isfinite(y)
            y = y[ok]
            if len(y) < 4 * n:
                continue
            op = (np.arange(len(y), dtype=float) if op_col == 0
                  else a[ok, op_col])
            cut = int(len(y) * FP_FRAC)
            fp = el.take_fingerprint(y[:cut], op[:cut])
            if fp.floor <= 0:
                continue
            d = slow_deviation(y[cut:], op[cut:], fp, n)
            if d is None:
                continue
            series[dev] = d
            pool.append(d[:max(1, int(len(d) * HEALTHY_FRAC))])
        if not pool:
            continue
        pool = np.concatenate(pool)
        q = min(1 - FA_PER_HOUR / HOUR_SAMPLES, 1 - 1.0 / len(pool))
        thr = float(np.quantile(pool, q))
        fired = sum(1 for d in series.values() if (d > thr).any())
        fa = float(np.mean([np.mean(d[:max(1, int(len(d) * HEALTHY_FRAC))] > thr)
                            for d in series.values()]))
        rec = {"quantity": name, "n": n, "thr": thr, "devices": len(series),
               "fired": fired, "fa": fa}
        if best is None or fired > best["fired"]:
            best = rec
    return best


def main() -> None:
    per_dev = {}
    for dev in mos.DEVICES:
        a = transients(dev)
        if a.size:
            per_dev[dev] = a
    print(f"素子 {len(per_dev)}、過渡記録 "
          f"{ {d: len(a) for d, a in per_dev.items()} }\n")

    cols = [("ゲート立ち上がり時間", 1), ("ゲート平坦部の高さ", 2), ("導通時の電圧降下", 3)]
    print(f"{'観測量':>22} {'指紋の当て先':>14} {'平均長':>7} {'閾値':>9} "
          f"{'素子':>5} {'発火':>5} {'誤報/判定':>11}")
    print("-" * 82)
    rows, best_overall = [], None
    for name, c in cols:
        for label, oc in (("記録順", 0), ("パッケージ温度", 4)):
            r = evaluate(name, c, per_dev, oc)
            if r is None:
                print(f"{name:>22} {label:>14}  評価できる素子が無い")
                continue
            r["fit_against"] = label
            print(f"{name:>22} {label:>14} {r['n']:>7} {r['thr']:>9.3f} "
                  f"{r['devices']:>5} {r['fired']:>5} {r['fa']:>11.5f}")
            rows.append(r)
            if oc == 4 and (best_overall is None or r["fired"] > best_overall["fired"]):
                best_overall = r

    print(f"\n=== P1 6中3以上が発火する量があるか(温度で正規化したもののみ) ===")
    if best_overall:
        print(f"  最良: {best_overall['quantity']}  "
              f"{best_overall['fired']}/{best_overall['devices']}  "
              f"{'PASS' if best_overall['fired'] >= 3 else 'FAIL'} (基準 6中3)")
        print(f"  比較: 定常記録の1量では 6中1 (docs/271)")
    print(f"\n=== P2 3素子以上で一貫するか ===")
    if best_overall:
        print(f"  {best_overall['fired']} 素子  "
              f"{'PASS' if best_overall['fired'] >= 3 else 'FAIL'} (基準 3素子)")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("quantity\tfit_against\tn_samples\tthreshold\tdevices\tfired\t"
                 "false_alarm\n")
        for r in rows:
            fh.write(f"{r['quantity']}\t{r.get('fit_against','')}\t{r['n']}\t"
                     f"{r['thr']:.5f}\t{r['devices']}\t{r['fired']}\t{r['fa']:.6f}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
