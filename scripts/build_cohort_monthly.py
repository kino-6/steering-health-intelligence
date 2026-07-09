#!/usr/bin/env python3
"""Aggregate the NHTSA complaints flat file into cohort-monthly counts.

One streaming pass over FLAT_CMPL.txt (~1.6 GB) producing, per cohort
(make, model, model-year) and filed month (LDATE YYYYMM):
    total complaints, steering complaints (COMPDESC starts with STEERING),
    assist-mode steering complaints (frozen keyword list from docs/137).

Output: .nhtsa_flat/cohort_monthly.tsv  (cache, gitignored)
Protocol: docs/140 (pre-registered). This script computes raw counts only.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / ".nhtsa_flat" / "FLAT_CMPL.txt"
OUT = REPO_ROOT / ".nhtsa_flat" / "cohort_monthly.tsv"

# frozen (docs/137 steering_mode_split.py loss_of_assist list)
ASSIST_KEYWORDS = [
    "POWER STEERING ASSIST", "STEERING ASSIST", "LOSS OF POWER STEERING",
    "LOST POWER STEERING", "POWER STEERING FAIL", "POWER STEERING WENT OUT",
    "POWER STEERING STOPPED", "NO POWER STEERING", "HARD TO STEER",
    "HARD TO TURN", "DIFFICULT TO TURN", "DIFFICULT TO STEER", "STIFF",
]


def main() -> None:
    agg = defaultdict(lambda: [0, 0, 0])  # (make, model, year, ym) -> [total, steer, assist]
    bad = 0
    n = 0
    with open(SRC, encoding="latin-1") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < 17:
                bad += 1
                continue
            make, model, year = f[3].strip().upper(), f[4].strip().upper(), f[5].strip()
            comp, ldate = f[11], f[16]
            if not (year.isdigit() and 2005 <= int(year) <= 2022):
                continue
            if len(ldate) < 6 or not ldate[:6].isdigit():
                continue
            ym = ldate[:6]
            key = (make, model, int(year), ym)
            rec = agg[key]
            rec[0] += 1
            if comp.upper().startswith("STEERING"):
                rec[1] += 1
                narrative = f[19].upper() if len(f) > 19 else ""
                if any(k in narrative for k in ASSIST_KEYWORDS):
                    rec[2] += 1
            n += 1
    with open(OUT, "w") as out:
        out.write("make\tmodel\tyear\tym\ttotal\tsteer\tassist\n")
        for (make, model, year, ym), (t, s, a) in agg.items():
            out.write(f"{make}\t{model}\t{year}\t{ym}\t{t}\t{s}\t{a}\n")
    print(f"rows in scope: {n:,}, malformed lines skipped: {bad:,}")
    print(f"cohort-months written: {len(agg):,} -> {OUT}")


if __name__ == "__main__":
    main()
