#!/usr/bin/env python3
"""Does the replacement actually fix it? (docs/187)

The money argument of docs/186 runs: a symptom with no code arrives, the
dealer cannot reproduce it, the assembly gets replaced anyway, it does not
fix anything, and warranty pays twice. docs/185 measured the second step
and the recall record covers the third. This measures the fourth, which is
the one the argument stands or falls on -- if replacement fixes it, there
is no repeat cost and no wasted part.

Fixed before any count was read:

  population  complaints whose text mentions a replacement (replac*)
  metric      share of those that also say it did not hold -- still, again,
              same problem, did not fix, persists, continues, came back,
              second time, another
  strata      whether the complaint describes intermittent behaviour, the
              family this work targets
  compare     EPS against all steering and against all complaints

Unit is the complaint (ODINO), not the row.

A limit that cannot be removed: a complaint is written by an owner, so
"replaced and still broken" is their account, not a repair record. This
measures how often owners report a replacement failing to fix, not the
true rate at which replacements fail.

Data: NHTSA FLAT_CMPL, US government work, public domain.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CMPL = REPO_ROOT / ".nhtsa_flat" / "FLAT_CMPL.txt"
OUT_TSV = REPO_ROOT / "data" / "replacement_no_fix_scan.tsv"

I_ODINO, I_COMP, I_DESC = 1, 11, 19

REPLACED = re.compile(r"\breplac\w+", re.I)
PERSIST = ["still", "again", "same problem", "same issue", "did not fix", "didn't fix",
           "does not fix", "problem persist", "issue persist", "continues", "continued",
           "has not fixed", "no change", "came back", "second time", "another"]
INTERMITTENT = ["intermittent", "intermittently", "comes and goes", "on and off",
                "sporadic", "randomly", "at times"]


def main() -> None:
    # (is_eps, is_steering, mentions_replacement, says_not_fixed, is_intermittent)
    #
    # One complaint spans several component rows, so the component flags are
    # OR-ed across the rows of a complaint. Assigning per row would let a
    # later non-steering row erase the steering flag -- which it did, losing
    # 8,005 EPS complaints down to 5,875 before this was fixed.
    rec = {}
    with open(CMPL, encoding="latin-1") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) <= I_DESC:
                continue
            comp, desc = f[I_COMP].upper(), f[I_DESC].lower()
            cur = (
                "STEERING" in comp and ("ELECTRIC" in comp or "POWER ASSIST" in comp),
                "STEERING" in comp,
                bool(REPLACED.search(desc)),
                any(t in desc for t in PERSIST),
                any(t in desc for t in INTERMITTENT),
            )
            prev = rec.get(f[I_ODINO])
            rec[f[I_ODINO]] = cur if prev is None else tuple(a or b for a, b in zip(prev, cur))

    def cut(sel):
        g = [v for v in rec.values() if sel(v)]
        repl = [v for v in g if v[2]]
        nofix = [v for v in repl if v[3]]
        return len(g), len(repl), len(nofix), (len(nofix) / len(repl) if repl else 0.0)

    print(f"苦情件数(ODINO重複除去): {len(rec):,}")
    print(f"\n{'母集団':<28}{'件数':>10}{'交換の記述':>12}{'直らない':>10}{'率':>9}")
    print("-" * 70)
    rows = []
    for lab, sel in [
        ("全苦情", lambda v: True),
        ("操舵全般", lambda v: v[1]),
        ("EPS", lambda v: v[0]),
        ("EPS × 断続的あり", lambda v: v[0] and v[4]),
        ("EPS × 断続的なし", lambda v: v[0] and not v[4]),
        ("操舵全般 × 断続的あり", lambda v: v[1] and v[4]),
    ]:
        n, r, nf, rate = cut(sel)
        print(f"{lab:<28}{n:>10,}{r:>12,}{nf:>10,}{rate:>8.1%}")
        rows.append((lab, n, r, nf, rate))

    base = rows[0][4]
    print(f"\n全苦情の基準率 {base:.1%} に対する比:")
    for lab, n, r, nf, rate in rows[1:]:
        print(f"  {lab:<28}{rate/base:>6.2f}倍")

    ei = next(r for r in rows if r[0] == "EPS × 断続的あり")[4]
    en = next(r for r in rows if r[0] == "EPS × 断続的なし")[4]
    print(f"\nEPS内の比: 断続あり / 断続なし = {ei/en:.2f}倍")

    with OUT_TSV.open("w") as fh:
        fh.write("population\tn_complaints\tn_mention_replacement\tn_not_fixed\tshare_not_fixed\tlift_vs_all\n")
        for lab, n, r, nf, rate in rows:
            fh.write(f"{lab}\t{n}\t{r}\t{nf}\t{rate:.5f}\t{rate/base:.4f}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
