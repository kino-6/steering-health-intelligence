#!/usr/bin/env python3
"""Do EPS-specific signs precede EPS-specific failures? (docs/189)

docs/150 showed that a sub-threshold steering observation in 2024 predicts
a steering failure in 2025 by up to 24.1x, across 17 million vehicles. But
docs/157 then showed those steering failures are 99% ball-joint linkage,
so that result says little about EPS itself, and docs/188 carries "the
sign-to-failure bridge is unproven for EPS" as its first standing limit.

This runs the same linkage restricted to the nine MOT items that name
electronic power steering, which is the closest public proxy available:

    1076   warning lamp indicates a failure in the system
    30806  wiring excessively corroded        (advisory: slightly corroded)
    30807  wiring excessively damaged         (advisory: slightly damaged)
    30808  wiring corroded and steering adversely affected
    30809  wiring damaged and steering adversely affected
    30810  warning lamp indicates a system malfunction
    30811  fly-by-wire steering wheel angle
    30812  fly-by-wire steering wheel angle
    30813  not working

Two of them carry both an advisory wording and a failure wording for the
same defect, which is a sub-threshold observation and its threshold
crossing recorded under one id.

Classification fixed before running, as in docs/150:
    fail = rfr_type_code F or P      sign = rfr_type_code A or M
    sign-only 2024 = a sign with no fail that year

Data: DVSA MOT test and item extracts 2024/2025 (OGL v3.0).
"""

from __future__ import annotations

import csv
import io
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np

csv.field_size_limit(sys.maxsize)

REPO_ROOT = Path(__file__).resolve().parent.parent
D = REPO_ROOT / ".dvsa_mot"
OUT_TSV = REPO_ROOT / "data" / "eps_specific_precedence.tsv"

FAIL_TYPES, SIGN_TYPES = {"F", "P"}, {"A", "M"}
AGE_BANDS = [(4, 7), (8, 11), (12, 15), (16, 25)]


def eps_rfr_ids():
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
            names.append(name)
            if parent == cur:
                break
            cur = parent
        return list(reversed(names))

    ids = set()
    for row in csv.DictReader(open(D / "item_detail.csv")):
        if row["test_class_id"] != "4":
            continue
        if "electronic power steering" in " > ".join(chain(row["test_item_id"], "4")).lower():
            ids.add(row["rfr_id"])
    print(f"EPS固有 rfr_id: {len(ids)} 件")
    return ids


def scan_items(year: str, ids):
    fail_t, sign_t = set(), set()
    zf = zipfile.ZipFile(D / f"dft_test_item_extracts_{year}.zip")
    for name in [n for n in zf.namelist() if n.endswith(".csv")]:
        r = csv.reader(io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace"))
        h = [x.strip().lower() for x in next(r)]
        i_t, i_r, i_ty = h.index("test_id"), h.index("rfr_id"), h.index("rfr_type_code")
        for row in r:
            if row[i_r] in ids:
                if row[i_ty] in FAIL_TYPES:
                    fail_t.add(row[i_t])
                elif row[i_ty] in SIGN_TYPES:
                    sign_t.add(row[i_t])
    print(f"{year}: EPS fail相当のtest {len(fail_t):,} / sign相当 {len(sign_t):,}")
    return fail_t, sign_t


def scan_results(year: str, fail_t, sign_t, want=None):
    """vehicle_id -> (group, age). group: 2=fail, 1=sign-only, 0=clean."""
    fail_v, sign_v, age = set(), set(), {}
    zf = zipfile.ZipFile(D / f"dft_test_result_extracts_{year}.zip")
    for name in [n for n in zf.namelist() if n.endswith(".csv")]:
        r = csv.reader(io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace"))
        h = [x.strip().lower() for x in next(r)]
        ix = {k: h.index(k) for k in ("test_id", "vehicle_id", "test_class_id", "test_type",
                                      "test_result", "test_date", "first_use_date")}
        for row in r:
            if row[ix["test_class_id"]] != "4" or row[ix["test_type"]] != "NT":
                continue
            if row[ix["test_result"]] not in ("P", "F", "PRS"):
                continue
            try:
                vid = int(row[ix["vehicle_id"]])
                a = int(row[ix["test_date"]][:4]) - int(row[ix["first_use_date"]][:4])
            except Exception:
                continue
            if want is not None and vid not in want:
                continue
            age[vid] = a
            tid = row[ix["test_id"]]
            if tid in fail_t:
                fail_v.add(vid)
            elif tid in sign_t:
                sign_v.add(vid)
        print(f"  {year} {name}: 累計 {len(age):,}")
    sign_v -= fail_v
    return age, fail_v, sign_v


def main() -> None:
    ids = eps_rfr_ids()
    f24, s24 = scan_items("2024", ids)
    age24, fail24, sign24 = scan_results("2024", f24, s24)
    print(f"2024 対象車 {len(age24):,} / EPS fail {len(fail24):,} / EPS signのみ {len(sign24):,}")

    f25, _ = scan_items("2025", ids)
    age25, fail25, _ = scan_results("2025", f25, set(), want=set(age24))
    both = set(age24) & set(age25)
    print(f"両年受検 {len(both):,}")

    counts = defaultdict(lambda: [0, 0])
    for vid in both:
        a = age24[vid]
        band = next((f"{lo}-{hi}" for lo, hi in AGE_BANDS if lo <= a <= hi), None)
        if band is None:
            continue
        g = "fail" if vid in fail24 else ("sign" if vid in sign24 else "clean")
        counts[(g, band)][0] += 1
        if vid in fail25:
            counts[(g, band)][1] += 1

    print(f"\n{'2024の状態':<8}" + "".join(f"{f'車齢{lo}-{hi}':>18}" for lo, hi in AGE_BANDS))
    print("-" * 80)
    rows = []
    base = {}
    for g, lab in (("clean", "記録なし"), ("sign", "EPS兆候のみ"), ("fail", "EPS不合格")):
        cells = []
        for lo, hi in AGE_BANDS:
            band = f"{lo}-{hi}"
            n, f = counts[(g, band)]
            rate = f / n if n else float("nan")
            if g == "clean":
                base[band] = rate
            lift = rate / base[band] if base.get(band) else float("nan")
            cells.append(f"{rate:>7.2%}({n:,})" if g == "clean"
                         else f"{rate:>7.2%}[{lift:.1f}x]({n:,})")
            rows.append((lab, band, n, f, rate, lift))
        print(f"{lab:<8}" + "".join(f"{c:>18}" for c in cells))

    with OUT_TSV.open("w") as fh:
        fh.write("group_2024\tage_band\tn\tn_eps_fail_2025\trate\tlift_vs_clean\n")
        for r in rows:
            fh.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]:.6f}\t{r[5]:.4f}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
