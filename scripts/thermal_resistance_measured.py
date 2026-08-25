#!/usr/bin/env python3
"""Measure thermal resistance directly, instead of inferring it (docs/189).

docs/170 turned the precursor into lost assist headroom through three
inference steps, and docs/180 listed "a calculation, not a measurement" as
a standing limit. The dataset makes the measurement possible: the
steady-state records carry drain-source voltage, drain current, package
temperature AND flange temperature, so the thermal path across the
die-attach can be measured directly rather than reconstructed from a
temperature coefficient.

    P    = V_DS * I_D                       power dissipated in the device
    Rth  = (T_package - T_flange) / P       thermal resistance across the path
                                            that die-attach degradation sits in

Die-attach degradation worsens heat transfer from die to flange, so Rth
must rise with aging if that is the mechanism. This is measured per run
against each device's own run 1, matching the per-unit baseline of
docs/163.

Only conducting records are used, gated as in scripts/mosfet_precursor.py,
because the device dissipates nothing while off.

Data: NASA PCoE MOSFET Thermal Overstress Aging, public domain.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
import scipy.io as sio
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / ".nasa_pcoe"
ZIP = CACHE / "13. MOSFET Thermal Overstress Aging" / "MOSFET_Thermal_Overstress_Aging_v0.zip"
OUT_TSV = REPO_ROOT / "data" / "thermal_resistance_measured.tsv"

DEVICES = [8, 9, 10, 11, 12, 14]
N_RUNS = 7


def read_run(z, dev: int, run: int):
    name = f"MOSFET_Thermal_Overstress_Aging_v0/Test_{dev}_run_{run}.mat"
    p = CACHE / name
    if not p.exists():
        z.extract(name, CACHE)
    m = sio.loadmat(p, squeeze_me=True, struct_as_record=False)["measurement"]
    v, i, tp, tf = [], [], [], []
    for rec in np.ravel(m.steadyState):
        td = rec.timeDomain
        v.append(float(td.drainSourceVoltage))
        i.append(float(td.drainCurrent))
        tp.append(float(td.packageTemperature))
        tf.append(float(td.flangeTemperature))
    v, i, tp, tf = map(np.asarray, (v, i, tp, tf))
    lo, hi = np.percentile(i, 10), np.percentile(i, 90)
    on = i > (lo + hi) / 2          # conduction gate, as in mosfet_precursor.py
    if on.sum() == 0:
        return None
    p_diss = v[on] * i[on]
    dT = tp[on] - tf[on]
    ok = p_diss > 0
    return p_diss[ok], dT[ok], tp[on][ok], tf[on][ok]


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    print(f"{'dev':>4} {'run':>4} {'P[W]':>8} {'T_pkg':>8} {'T_flg':>8} {'dT[C]':>8} "
          f"{'Rth[C/W]':>10} {'vs run1':>9}")
    print("-" * 68)
    out, rhos, finals = [], [], []
    for dev in DEVICES:
        base = None
        for run in range(1, N_RUNS + 1):
            got = read_run(z, dev, run)
            if not got:
                continue
            p_diss, dT, tp, tf = got
            rth = float(np.median(dT / p_diss))
            if run == 1:
                base = rth
            ratio = rth / base if base else float("nan")
            print(f"{dev:>4} {run:>4} {np.median(p_diss):>8.3f} {np.median(tp):>8.1f} "
                  f"{np.median(tf):>8.1f} {np.median(dT):>8.2f} {rth:>10.4f} {ratio:>8.3f}x")
            out.append((dev, run, float(np.median(p_diss)), float(np.median(tp)),
                        float(np.median(tf)), float(np.median(dT)), rth, ratio))
        g = [o for o in out if o[0] == dev]
        rho = stats.spearmanr([o[1] for o in g], [o[6] for o in g]).statistic
        rhos.append(rho)
        finals.append(g[-1][7])
        print(f"     run順 vs Rth の Spearman ρ = {rho:.3f}   最終run {g[-1][7]:.2f}倍\n")

    n_mono = sum(1 for r in rhos if r >= 0.8)
    print("=== まとめ ===")
    print(f"  単調増加(ρ≥0.8): {n_mono}/{len(DEVICES)} デバイス")
    print(f"  最終runの熱抵抗: 自身のrun1比 {min(finals):.2f} 〜 {max(finals):.2f} 倍 "
          f"(中央値 {np.median(finals):.2f} 倍)")
    print(f"  → 持続可能電力は 1/k なので、熱余裕の損失は "
          f"{1 - 1/max(finals):.0%} 〜 {1 - 1/min(finals):.0%}")

    with OUT_TSV.open("w") as fh:
        fh.write("device\trun\tP_W\tT_package_C\tT_flange_C\tdeltaT_C\tRth_C_per_W\tRth_vs_run1\n")
        for o in out:
            fh.write("\t".join(f"{v:.6f}" if isinstance(v, float) else str(v) for v in o) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
