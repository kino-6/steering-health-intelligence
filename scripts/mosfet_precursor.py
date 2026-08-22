#!/usr/bin/env python3
"""Failure-precursor analysis on NASA PCoE MOSFET aging data (docs/165 -> docs/166).

Executes the protocol pre-registered in docs/165. For each of the six
devices that have seven runs, computes per-run on-resistance and package
temperature from the steady-state records, referenced to that device's OWN
run 1 -- the per-unit baseline of docs/163, not a population reference.

Conduction gate (protocol defect found in execution, docs/166). The
pre-registered indicator said "median of drainSourceVoltage/drainCurrent
over the steady-state records" and forgot that the device is PWM-driven,
so those records are bimodal: conducting at ~2.3-2.9 A with ~4.9 V across
it, and off at ~0.04-0.07 A with the full supply across it. Taking the
median over both mixes the two, and the mixture ratio -- not degradation
-- drives the number. The gate below keeps only conducting records. It is
defined from the bimodal structure of each run, not from whether it makes
a criterion pass.

Indicators (fixed in docs/165 before any value was read):
    R_on_raw      median(drainSourceVoltage / drainCurrent)
    T_pkg         median(packageTemperature)
    R_on_matched  same ratio, restricted to records whose packageTemperature
                  is within +-2 C of that device's run-1 median

The confound is declared in docs/165: die-attach degradation raises
junction temperature, which raises on-resistance, so a raw rise is partly
thermal. R_on_matched exists to show whether anything survives that.

Data: NASA Prognostics Center of Excellence, public domain.
"""

from __future__ import annotations

import re
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.io as sio
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / ".nasa_pcoe"
ZIP = CACHE / "13. MOSFET Thermal Overstress Aging" / "MOSFET_Thermal_Overstress_Aging_v0.zip"
OUT_TSV = REPO_ROOT / "data" / "mosfet_precursor.tsv"

DEVICES = [8, 9, 10, 11, 12, 14]     # the six devices with seven runs (docs/165)
N_RUNS = 7
TEMP_WIN = 2.0                       # +-2 C matching window (docs/165)
RISE = 0.05                          # +5% over own baseline counts as a sign (docs/165)


def read_run(z, dev: int, run: int):
    name = f"MOSFET_Thermal_Overstress_Aging_v0/Test_{dev}_run_{run}.mat"
    p = CACHE / name
    if not p.exists():
        z.extract(name, CACHE)
    m = sio.loadmat(p, squeeze_me=True, struct_as_record=False)["measurement"]
    cur, vds, tp = [], [], []
    for rec in np.ravel(m.steadyState):
        td = rec.timeDomain
        cur.append(float(td.drainCurrent))
        vds.append(float(td.drainSourceVoltage))
        tp.append(float(td.packageTemperature))
    cur, vds, tp = np.array(cur), np.array(vds), np.array(tp)
    # conduction gate: midpoint between the two modes of this run
    lo, hi = np.percentile(cur, 10), np.percentile(cur, 90)
    on = cur > (lo + hi) / 2
    if on.sum() == 0:
        return np.array([]), np.array([])
    return vds[on] / cur[on], tp[on]


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    per_dev = {}
    for dev in DEVICES:
        runs = {}
        for run in range(1, N_RUNS + 1):
            ron, tpkg = read_run(z, dev, run)
            runs[run] = (ron, tpkg)
        t_ref = float(np.median(runs[1][1]))          # baseline package temperature
        rows = []
        for run in range(1, N_RUNS + 1):
            ron, tpkg = runs[run]
            sel = np.abs(tpkg - t_ref) <= TEMP_WIN
            rows.append({
                "run": run,
                "n": len(ron),
                "R_raw": float(np.median(ron)),
                "T_pkg": float(np.median(tpkg)),
                "n_matched": int(sel.sum()),
                "R_matched": float(np.median(ron[sel])) if sel.sum() else float("nan"),
            })
        per_dev[dev] = rows

    print(f"{'dev':>4} {'run':>4} {'n':>5} {'R_on[ohm]':>11} {'vs base':>9} "
          f"{'T_pkg[C]':>9} {'n_match':>8} {'R_match':>10} {'vs base':>9}")
    print("-" * 82)
    out = []
    for dev, rows in per_dev.items():
        b_raw, b_mat = rows[0]["R_raw"], rows[0]["R_matched"]
        for r in rows:
            xr = r["R_raw"] / b_raw
            xm = r["R_matched"] / b_mat if b_mat == b_mat else float("nan")
            print(f"{dev:>4} {r['run']:>4} {r['n']:>5} {r['R_raw']:>11.5f} {xr:>8.3f}x "
                  f"{r['T_pkg']:>9.2f} {r['n_matched']:>8} {r['R_matched']:>10.5f} {xm:>8.3f}x")
            out.append((dev, r["run"], r["n"], r["R_raw"], xr, r["T_pkg"],
                        r["n_matched"], r["R_matched"], xm))
        print()

    # --- pre-registered criteria -----------------------------------------
    print("=== A1 先行性: 最終run より前に ベースライン比 +5% を超える run があるか ===")
    a1 = 0
    for dev, rows in per_dev.items():
        b = rows[0]["R_raw"]
        early = [r["run"] for r in rows if r["run"] < N_RUNS and r["R_raw"] / b > 1 + RISE]
        ok = bool(early)
        a1 += ok
        print(f"  Test_{dev:<3} {'成立' if ok else '不成立'}  最初に+5%を超えたrun: "
              f"{early[0] if early else '-'}  (最終runの{N_RUNS - early[0] if early else 0}段階前)")
    print(f"  → {a1}/6 デバイス  {'PASS' if a1 >= 4 else 'FAIL'} (基準: 4以上)")

    print("\n=== A2 単調性: run順 vs R_on_raw の Spearman ρ ===")
    a2 = 0
    for dev, rows in per_dev.items():
        rho = stats.spearmanr([r["run"] for r in rows], [r["R_raw"] for r in rows]).statistic
        ok = rho >= 0.8
        a2 += ok
        print(f"  Test_{dev:<3} ρ = {rho:>6.3f}  {'OK' if ok else '-'}")
    print(f"  → {a2}/6 デバイス  {'PASS' if a2 >= 4 else 'FAIL'} (基準: 4以上)")

    print("\n=== A3 温度非依存成分: R_on_matched でも A1 が成立するか(合否判定なし) ===")
    a3 = 0
    for dev, rows in per_dev.items():
        b = rows[0]["R_matched"]
        if b != b:
            print(f"  Test_{dev:<3} 温度整合レコードなし")
            continue
        early = [r["run"] for r in rows
                 if r["run"] < N_RUNS and r["R_matched"] == r["R_matched"]
                 and r["R_matched"] / b > 1 + RISE]
        a3 += bool(early)
        print(f"  Test_{dev:<3} {'成立' if early else '不成立'}  最初のrun: {early[0] if early else '-'}")
    print(f"  → {a3}/6 デバイス")

    print("\n=== B1 ベースライン安定性: 兆候発生前のrunにおける R_on_raw の変動幅 ===")
    for dev, rows in per_dev.items():
        b = rows[0]["R_raw"]
        pre = [r["R_raw"] for r in rows if r["R_raw"] / b <= 1 + RISE]
        if len(pre) >= 2:
            spread = max(pre) / min(pre) - 1
            print(f"  Test_{dev:<3} 兆候前 {len(pre)} run: 変動幅 {spread:>6.1%}")
        else:
            print(f"  Test_{dev:<3} 兆候前 {len(pre)} run: 変動幅は算出不能(run数不足)")

    with OUT_TSV.open("w") as fh:
        fh.write("device\trun\tn_records\tR_on_raw\tR_on_raw_vs_baseline\tT_pkg\t"
                 "n_matched\tR_on_matched\tR_on_matched_vs_baseline\n")
        for r in out:
            fh.write("\t".join(f"{v:.6f}" if isinstance(v, float) else str(v) for v in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
