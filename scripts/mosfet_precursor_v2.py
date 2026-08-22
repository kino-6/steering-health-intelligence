#!/usr/bin/env python3
"""Precursor analysis v2 — temperature removed per device (docs/166 -> docs/167).

v1 (scripts/mosfet_precursor.py) failed its pre-registered criteria because
on-resistance is dominated by package temperature, which the rig lowers by
about 20 C across the seven runs. v2 removes that per device, using the
protocol committed in docs/166 before this was run:

    fit on runs 1-3 only :  R_on = a * T_pkg + b
    per run              :  residual = median(R_on) - (a * median(T_pkg) + b)
    indicator            :  delta = residual / predicted(T_pkg of run 1)

Runs 1-3 are the fitting window because degradation may enter from run 4;
that boundary was fixed before running. The temperature coefficient a is
estimated per device, matching the per-unit baseline of docs/163.

docs/166 also declares there will be no v3.

Data: NASA Prognostics Center of Excellence, public domain.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
from scipy import stats

import mosfet_precursor as v1

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "mosfet_precursor_v2.tsv"
FIT_RUNS = (1, 2, 3)
RISE = 0.05


def main() -> None:
    z = zipfile.ZipFile(v1.ZIP)
    print(f"{'dev':>4} {'run':>4} {'R_on':>9} {'T_pkg':>8} {'pred':>9} {'resid':>9} {'delta':>9}")
    print("-" * 56)
    per_dev, out = {}, []
    for dev in v1.DEVICES:
        med = {}
        for run in range(1, v1.N_RUNS + 1):
            ron, tpkg = v1.read_run(z, dev, run)
            med[run] = (float(np.median(ron)), float(np.median(tpkg)))
        T = np.array([med[r][1] for r in FIT_RUNS])
        R = np.array([med[r][0] for r in FIT_RUNS])
        a, b = np.polyfit(T, R, 1)
        base_pred = a * med[1][1] + b
        rows = []
        for run in range(1, v1.N_RUNS + 1):
            r, t = med[run]
            pred = a * t + b
            delta = (r - pred) / base_pred
            rows.append({"run": run, "R": r, "T": t, "pred": pred,
                         "resid": r - pred, "delta": delta})
            print(f"{dev:>4} {run:>4} {r:>9.4f} {t:>8.2f} {pred:>9.4f} "
                  f"{r - pred:>+9.4f} {delta:>+8.2%}")
            out.append((dev, run, r, t, pred, r - pred, delta))
        per_dev[dev] = rows
        print(f"     温度係数 a = {a:.5f} Ω/°C   (run1-3で推定)\n")

    print("=== A1' 先行性: 最終run より前に Δ が +5% を超える run があるか ===")
    a1 = 0
    for dev, rows in per_dev.items():
        early = [r["run"] for r in rows if r["run"] < v1.N_RUNS and r["delta"] > RISE]
        a1 += bool(early)
        lead = v1.N_RUNS - early[0] if early else 0
        print(f"  Test_{dev:<3} {'成立' if early else '不成立'}  "
              f"最初に+5%: run {early[0] if early else '-'}  (最終runの{lead}段階前)")
    print(f"  → {a1}/6  {'PASS' if a1 >= 4 else 'FAIL'} (基準: 4以上)")

    print("\n=== A2' 単調性: run4-7 の run順 vs Δ の Spearman ρ ===")
    a2 = 0
    for dev, rows in per_dev.items():
        late = [r for r in rows if r["run"] >= 4]
        rho = stats.spearmanr([r["run"] for r in late], [r["delta"] for r in late]).statistic
        a2 += rho >= 0.8
        print(f"  Test_{dev:<3} ρ = {rho:>6.3f}  {'OK' if rho >= 0.8 else '-'}")
    print(f"  → {a2}/6  {'PASS' if a2 >= 4 else 'FAIL'} (基準: 4以上)")

    print("\n=== B1' 温度を除いた個体基準の安定性: run1-3 の残差の変動幅 ===")
    for dev, rows in per_dev.items():
        d = [r["delta"] for r in rows if r["run"] in FIT_RUNS]
        print(f"  Test_{dev:<3} {max(d) - min(d):>6.2%}")

    with OUT_TSV.open("w") as fh:
        fh.write("device\trun\tR_on\tT_pkg\tR_on_predicted\tresidual\tdelta_vs_baseline\n")
        for r in out:
            fh.write("\t".join(f"{v:.6f}" if isinstance(v, float) else str(v) for v in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
