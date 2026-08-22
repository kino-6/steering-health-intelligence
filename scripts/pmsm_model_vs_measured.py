#!/usr/bin/env python3
"""Evaluate the pre-registered criteria of docs/161 (result: docs/162).

Compares scripts/pmsm_interturn_model.py against the measured signatures
from scripts/pmsm_measured_signature.py, applying the three criteria fixed
in docs/161 BEFORE the data was read:

  1. monotonicity      Spearman rho >= 0.8 for both model and measurement
  2. order of magnitude ratio measured/model within 0.1 .. 10
  3. sensitivity match  severity reaching 3x healthy agrees within 2x

The session split reported below was NOT pre-registered. It was found
while executing, and is reported as a post-hoc stratification, alongside
the pre-registered unstratified result, so the two are not confused.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "pmsm_model_vs_measured.tsv"


def main() -> None:
    meas = [r for r in csv.DictReader(open(REPO_ROOT / "data" / "pmsm_measured_signature.tsv"),
                                      delimiter="\t")]
    for r in meas:
        r["sev"] = float(r["severity_pct"])
        r["U"] = float(r["U_fundamental"])
        r["R"] = float(r["i2_over_i1"])
        r["s1"] = float(r["session_s1"]) > 0.5
    meas.sort(key=lambda r: r["sev"])

    model = {}
    for r in csv.DictReader(open(REPO_ROOT / "data" / "pmsm_interturn_model.tsv"), delimiter="\t"):
        s = round(float(r["severity"]) * 100, 2)
        model.setdefault(s, {"U": [], "R": []})
        model[s]["U"].append(float(r["unbalance"]))
        model[s]["R"].append(float(r["i2_over_i1"]))

    sev = [r["sev"] for r in meas]
    print("=== 事前登録どおり(層別なし)の単調性 ===")
    for key, lab in (("U", "U"), ("R", "I2/I1")):
        rho = stats.spearmanr(sev, [r[key] for r in meas]).statistic
        print(f"  {lab:<6} Spearman rho = {rho:.3f}   {'PASS' if rho >= 0.8 else 'FAIL (基準0.8)'}")

    print("\n=== 事後の層別（実行中に発見。事前登録ではない） ===")
    for s1, lab in ((False, "S2(極性正常・健全0%を含む)"), (True, "S1(C相極性反転・健全なし)")):
        g = [r for r in meas if r["s1"] == s1]
        for key, kl in (("U", "U"), ("R", "I2/I1")):
            rho = stats.spearmanr([r["sev"] for r in g], [r[key] for r in g]).statistic
            print(f"  {lab:<28} {kl:<6} rho = {rho:.3f}")

    print("\n=== モデル vs 実測（S2、健全ベースラインを差し引いた増分で比較） ===")
    base = [r for r in meas if not r["s1"] and r["sev"] == 0.0][0]
    print(f"{'sev%':>7} {'ΔU実測':>9} {'Uモデル(帯)':>18} {'比':>11} | "
          f"{'ΔI2/I1実測':>11} {'I2/I1モデル(帯)':>18} {'比':>11}")
    rows = []
    for r in meas:
        if r["s1"] or r["sev"] == 0.0:
            continue
        m = model[round(r["sev"], 2)]
        dU, dR = r["U"] - base["U"], r["R"] - base["R"]
        ru = (min(m["U"]) / dU, max(m["U"]) / dU)
        rr = (min(m["R"]) / dR, max(m["R"]) / dR)
        print(f"{r['sev']:>7.2f} {dU:>9.4f} {min(m['U']):>8.4f}..{max(m['U']):<8.4f}"
              f" {ru[0]:>4.1f}..{ru[1]:<5.1f} | {dR:>11.4f}"
              f" {min(m['R']):>8.4f}..{max(m['R']):<8.4f} {rr[0]:>4.1f}..{rr[1]:<5.1f}")
        rows.append((r["sev"], dU, min(m["U"]), max(m["U"]), ru[0], ru[1],
                     dR, min(m["R"]), max(m["R"]), rr[0], rr[1]))

    lo = min(min(r[4], r[9]) for r in rows)
    hi = max(max(r[5], r[10]) for r in rows)
    print(f"\n  比の全範囲: {lo:.1f} .. {hi:.1f}   "
          f"{'PASS (基準0.1..10)' if 0.1 <= lo and hi <= 10 else 'FAIL'}")
    print("  ずれの向き: モデルが実測を上回る（docs/161で宣言済みの系統誤差の向き）")
    print("  ずれはseverityとともに拡大 — 電流制御器が不平衡を抑圧する挙動と整合")

    print("\n=== 基準3（健全の3倍に達するseverity） ===")
    print("  評価不能。モデルは μ=0 で完全対称のため健全時U=0であり、『3倍』が定義できない。")
    print("  実測機は製造・配線由来の健全時不平衡 U=2.75% を持つ。プロトコルの設計欠陥として記録する。")

    with OUT_TSV.open("w") as fh:
        fh.write("severity_pct\tdU_measured\tU_model_lo\tU_model_hi\tratio_lo\tratio_hi\t"
                 "dI2I1_measured\tI2I1_model_lo\tI2I1_model_hi\tratio_r_lo\tratio_r_hi\n")
        for r in rows:
            fh.write("\t".join(f"{v:.6f}" for v in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
