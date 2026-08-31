#!/usr/bin/env python3
"""Does the EooC sheet claim anything the element does not do? (docs/266 -> docs/267)

Executes criterion S2 of the protocol pre-registered in docs/266.

The sheet is the work product a component would hand to a vehicle-level SOTIF
argument. docs/249 already found five rows still marked filled after the work
behind them was withdrawn, and check_repo.py stops that now. This is the other
direction: rows that promise an output the running element does not produce.

scripts/element_v2.py is the element. Its record and fingerprint field names
are the whole of what it emits, so anything the sheet promises beyond them is
the sheet overstating the part.
"""

from __future__ import annotations

import csv
import re
import sys
from dataclasses import fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import element_v2 as el

ROOT = Path(__file__).resolve().parent.parent
SHEET = ROOT / "data" / "sotif_eooc_assumption_sheet.tsv"
OUT = ROOT / "data" / "sotif_sheet_audit.tsv"

# claims the element cannot back: withdrawn quantities, and byte counts that
# docs/265 measured to be wrong
WITHDRAWN = {
    "能力値": "docs/203 で機体をまたがず撤回",
    "capability値": "同上",
    "残存能力": "同上",
    "36バイト": "docs/265 の実測は 48バイト",
    "27バイト": "docs/265 の実測は 30バイト",
    "24バイト": "docs/265 の実測は 30バイト",
    "早期警告": "docs/193 で6中3不成立",
    "故障箇所": "docs/217, docs/219 で2回とも不成立",
    "余寿命": "測っていない",
}


def main() -> None:
    if not SHEET.exists():
        sys.exit(f"missing {SHEET}")
    emits = [f.name for f in fields(el.Record)] + [f.name for f in fields(el.Fingerprint)]
    print("要素が実際に出すもの:")
    print("  " + ", ".join(emits))

    rows, bad = [], []
    with SHEET.open() as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            text = " ".join(v or "" for v in r.values())
            for term, why in WITHDRAWN.items():
                if term in text:
                    # a row that names the term only to say it was withdrawn is fine
                    ok = any(w in text for w in ("撤回", "取り下げ", "ではない", "誤り", "訂正"))
                    rows.append({"row": r.get("row_id", "?"), "term": term,
                                 "excused": ok, "why": why})
                    if not ok:
                        bad.append((r.get("row_id", "?"), term, why))

    print(f"\n照合した語 {len(WITHDRAWN)} 件、該当した行 {len(rows)} 件")
    for r in rows:
        mark = "  ok " if r["excused"] else "  NG "
        print(f"{mark}{r['row']:>9}  「{r['term']}」  {r['why']}"
              f"{'  (撤回と併記されている)' if r['excused'] else ''}")

    print(f"\n=== S2 実装が出さないものを出すと書いた行 ===")
    print(f"  {len(bad)} 行  {'PASS' if not bad else 'FAIL'} (基準: 0行)")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("row_id\tterm\texcused\treason\n")
        for r in rows:
            fh.write(f"{r['row']}\t{r['term']}\t{int(r['excused'])}\t{r['why']}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
