#!/usr/bin/env python3
"""兆候→翌年故障の先行性検証(個体連結、docs/150)。

問い: 2024年の車検で操舵系の「不合格未満の記録」(advisory/minor)だけが付いた
個体は、2024年がクリーンだった個体に比べ、2025年に操舵系で不合格になる率が
何倍か。——「小さな兆候は後の故障に先行する」の、実個体・実データでの検証。

分類の事前固定(実行前に本ヘッダで宣言):
  fail(不合格相当)   = rfr_type_code F(不合格) または P(検査中に是正=欠陥は存在した)
  sign(不合格未満の兆候) = rfr_type_code A(advisory) または M(minor)
  2024年グループ: fail24(操舵fail相当あり) / sign24(signのみ) / clean24(操舵記録なし)
  2025年結果: 操舵系fail相当の有無
  対象: 乗用車クラス(4)・通常検査(NT)・両年受検の個体。年齢帯別に層別。

出力: 群別×年齢帯の翌年不合格率と相対リスク。
"""

from __future__ import annotations

import csv
import io
import sys
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np

csv.field_size_limit(sys.maxsize)

REPO_ROOT = Path(__file__).resolve().parent.parent
D = REPO_ROOT / ".dvsa_mot"
OUT_TSV = REPO_ROOT / "data" / "mot_advisory_longitudinal.tsv"

FAIL_TYPES = {"F", "P"}
SIGN_TYPES = {"A", "M"}
AGE_BANDS = [(4, 7), (8, 11), (12, 15), (16, 25)]


def build_steering_rfr():
    groups = {}
    for row in csv.DictReader(open(D / "item_group.csv")):
        groups[(row["test_item_id"], row["test_class_id"])] = (row["parent_id"], row["item_name"])

    def chain(item_id, cls):
        names, seen, cur = [], set(), item_id
        while True:
            k = (cur, cls)
            if k in seen or k not in groups:
                break
            seen.add(k)
            parent, name = groups[k]
            names.append(name.lower())
            if parent == cur:
                break
            cur = parent
        return names

    steer = set()
    for row in csv.DictReader(open(D / "item_detail.csv")):
        if row["test_class_id"] != "4":
            continue
        blob = " | ".join(chain(row["test_item_id"], "4")) + " | " + row["rfr_insp_manual_desc"].lower() + " | " + row["rfr_desc"].lower()
        if "steering" in blob:
            steer.add(row["rfr_id"])
    print(f"steering rfr_ids (class 4): {len(steer)}")
    return steer


def scan_items(year: str, steer_rfr):
    """test_id sets: steering fail-tier and sign-tier."""
    fail_t, sign_t = set(), set()
    zf = zipfile.ZipFile(D / f"dft_test_item_extracts_{year}.zip")
    for name in [n for n in zf.namelist() if n.endswith(".csv")]:
        fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
        r = csv.reader(fh)
        header = [h.strip().lower() for h in next(r)]
        i_t, i_r, i_ty = header.index("test_id"), header.index("rfr_id"), header.index("rfr_type_code")
        for row in r:
            if row[i_r] in steer_rfr:
                ty = row[i_ty]
                if ty in FAIL_TYPES:
                    fail_t.add(row[i_t])
                elif ty in SIGN_TYPES:
                    sign_t.add(row[i_t])
    print(f"{year}: steering fail-tier tests {len(fail_t):,}, sign-tier {len(sign_t):,}")
    return fail_t, sign_t


def scan_results_2024(fail_t, sign_t):
    """vehicle_id arrays: all tested, fail24 vehicles, sign24 vehicles."""
    all_v, fail_v, sign_v = [], set(), set()
    zf = zipfile.ZipFile(D / "dft_test_result_extracts_2024.zip")
    for name in [n for n in zf.namelist() if n.endswith(".csv")]:
        fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
        r = csv.reader(fh)
        header = [h.strip().lower() for h in next(r)]
        ix = {k: header.index(k) for k in ("test_id", "vehicle_id", "test_class_id", "test_type", "test_result")}
        for row in r:
            try:
                if row[ix["test_class_id"]] != "4" or row[ix["test_type"]] != "NT":
                    continue
                if row[ix["test_result"]] not in ("P", "F", "PRS"):
                    continue
                vid = int(row[ix["vehicle_id"]])
            except Exception:
                continue
            all_v.append(vid)
            tid = row[ix["test_id"]]
            if tid in fail_t:
                fail_v.add(vid)
            elif tid in sign_t:
                sign_v.add(vid)
        print(f"  2024 {name}: cum vehicles {len(all_v):,}")
    arr = np.unique(np.array(all_v, dtype=np.int64))
    sign_v -= fail_v  # sign-only
    print(f"2024 unique class-4 NT vehicles: {len(arr):,}; fail24 {len(fail_v):,}; sign24(only) {len(sign_v):,}")
    return arr, fail_v, sign_v


def scan_results_2025(all24, fail_v24, sign_v24, steer_fail25):
    counts = defaultdict(lambda: [0, 0])  # (group, band) -> [n, fail25]
    zf = zipfile.ZipFile(D / "dft_test_result_extracts_2025.zip")
    for name in [n for n in zf.namelist() if n.endswith(".csv")]:
        fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
        r = csv.reader(fh)
        header = [h.strip().lower() for h in next(r)]
        ix = {k: header.index(k) for k in ("test_id", "vehicle_id", "test_class_id", "test_type", "test_result", "test_date", "first_use_date")}
        for row in r:
            try:
                if row[ix["test_class_id"]] != "4" or row[ix["test_type"]] != "NT":
                    continue
                if row[ix["test_result"]] not in ("P", "F", "PRS"):
                    continue
                vid = int(row[ix["vehicle_id"]])
                age = (date.fromisoformat(row[ix["test_date"]]) - date.fromisoformat(row[ix["first_use_date"]])).days / 365.25
            except Exception:
                continue
            i = np.searchsorted(all24, vid)
            if i >= len(all24) or all24[i] != vid:
                continue  # not tested in 2024
            band = next((f"{lo}-{hi}" for lo, hi in AGE_BANDS if lo <= age <= hi), None)
            if band is None:
                continue
            group = "fail24" if vid in fail_v24 else ("sign24" if vid in sign_v24 else "clean24")
            rec = counts[(group, band)]
            rec[0] += 1
            rec[1] += row[ix["test_id"]] in steer_fail25
        print(f"  2025 {name}")
    return counts


def main() -> None:
    steer_rfr = build_steering_rfr()
    fail24_t, sign24_t = scan_items("2024", steer_rfr)
    all24, fail_v24, sign_v24 = scan_results_2024(fail24_t, sign24_t)
    steer_fail25 = set((D / "cache_steer_tests.txt").read_text().split())
    counts = scan_results_2025(all24, fail_v24, sign_v24, steer_fail25)

    lines = ["group\tage_band\tvehicles\tsteer_fail_2025\trate\trelative_risk_vs_clean"]
    print(f"{'group':>8} {'band':>7} {'n':>9} {'fail25':>7} {'rate':>8} {'RR':>6}")
    for lo, hi in AGE_BANDS:
        band = f"{lo}-{hi}"
        base_n, base_f = counts.get(("clean24", band), (0, 0))
        base = base_f / base_n if base_n else float("nan")
        for g in ("clean24", "sign24", "fail24"):
            n, f = counts.get((g, band), (0, 0))
            if n == 0:
                continue
            rate = f / n
            rr = rate / base if base > 0 else float("nan")
            print(f"{g:>8} {band:>7} {n:>9,} {f:>7,} {rate:>8.4%} {rr:>6.1f}")
            lines.append(f"{g}\t{band}\t{n}\t{f}\t{rate:.5f}\t{rr:.2f}")
    OUT_TSV.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
