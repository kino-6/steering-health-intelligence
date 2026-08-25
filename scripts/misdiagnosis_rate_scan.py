#!/usr/bin/env python3
"""How often do steering complaints describe misdiagnosis? (docs/185)

docs/184 moved the load-bearing demand argument off the SOTIF/ADS
regulation and back onto the OEM's own quality and warranty economics --
the cost of misdiagnosis and needless replacement, which docs/145 named
but never quantified. This quantifies it from the complaint corpus.

Term groups, fixed before any count was read. They are phrasings a
consumer uses, not tuned to the rates they produce:

  no_fault_found   no trouble found / could not duplicate / no problem found /
                   no fault found / unable to duplicate / no codes
  replaced_no_fix  a replacement followed by the problem continuing
  repeat_visits    multiple trips back to the dealer for the same thing

Populations, so the numbers mean something:
  EPS       COMPDESC names STEERING and ELECTRIC or POWER ASSIST
  STEERING  COMPDESC names STEERING
  ALL       every complaint (base rate of the vocabulary itself)

Unit of analysis is the complaint (ODINO), not the row. One complaint can
appear under several components, and counting rows would inflate it --
the same mistake docs/171 made with recall campaigns.

Data: NHTSA FLAT_CMPL, US government work, public domain.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CMPL = REPO_ROOT / ".nhtsa_flat" / "FLAT_CMPL.txt"
OUT_TSV = REPO_ROOT / "data" / "misdiagnosis_rate_scan.tsv"

I_ODINO, I_COMP, I_DESC = 1, 11, 19

NO_FAULT = ["no trouble found", "no problem found", "no fault found", "nothing found",
            "could not duplicate", "couldn't duplicate", "unable to duplicate",
            "cannot duplicate", "can not duplicate", "could not replicate",
            "no codes", "no fault codes", "no diagnostic codes",
            "could not find the problem", "unable to find the problem"]
REPEAT = ["multiple times", "several times", "three times", "3 times", "four times",
          "4 times", "numerous times", "repeatedly", "over and over",
          "back to the dealer", "returned to the dealer"]
REPLACED = re.compile(r"replac\w+", re.I)
INTERMITTENT = ["intermittent", "intermittently", "comes and goes", "on and off",
                "sporadic", "randomly", "at times"]
PERSIST = ["still", "again", "same problem", "same issue", "did not fix", "didn't fix",
           "does not fix", "problem persist", "issue persist", "continues", "continued",
           "has not fixed", "no change"]


def main() -> None:
    pops = {"EPS": {}, "STEERING": {}, "ALL": {}}
    n_rows = 0
    with open(CMPL, encoding="latin-1") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) <= I_DESC:
                continue
            n_rows += 1
            odino, comp, desc = f[I_ODINO], f[I_COMP].upper(), f[I_DESC].lower()
            hits = (
                any(t in desc for t in NO_FAULT),
                bool(REPLACED.search(desc)) and any(t in desc for t in PERSIST),
                any(t in desc for t in REPEAT),
            )
            pops["ALL"][odino] = hits
            if "STEERING" in comp:
                pops["STEERING"][odino] = hits
                if "ELECTRIC" in comp or "POWER ASSIST" in comp:
                    pops["EPS"][odino] = hits

    print(f"読み込み行数 {n_rows:,}")
    print("重複除去後の苦情件数(ODINO): " + "  ".join(f"{k}={len(v):,}" for k, v in pops.items()))
    print()
    labels = ["原因不明・再現せず", "交換したが直らない", "繰り返し来店"]
    print(f"{'語群':<22}" + "".join(f"{k:>12}" for k in pops) + f"{'EPS/ALL':>10}{'STR/ALL':>10}")
    print("-" * 76)
    rows = []
    for i, lab in enumerate(labels):
        share = {k: (sum(1 for h in v.values() if h[i]) / len(v) if v else 0.0)
                 for k, v in pops.items()}
        le = share["EPS"] / share["ALL"] if share["ALL"] else float("nan")
        ls = share["STEERING"] / share["ALL"] if share["ALL"] else float("nan")
        print(f"{lab:<22}" + "".join(f"{share[k]:>11.2%}" for k in pops)
              + f"{le:>9.2f}x{ls:>9.2f}x")
        rows.append((lab, share["EPS"], share["STEERING"], share["ALL"], le, ls))

    any_share = {k: (sum(1 for h in v.values() if any(h)) / len(v) if v else 0.0)
                 for k, v in pops.items()}
    la = any_share["EPS"] / any_share["ALL"] if any_share["ALL"] else float("nan")
    ls = any_share["STEERING"] / any_share["ALL"] if any_share["ALL"] else float("nan")
    print("-" * 76)
    print(f"{'いずれか':<22}" + "".join(f"{any_share[k]:>11.2%}" for k in pops)
          + f"{la:>9.2f}x{ls:>9.2f}x")
    rows.append(("いずれか", any_share["EPS"], any_share["STEERING"], any_share["ALL"], la, ls))

    # The population-level rates above answer whether EPS as a whole carries more
    # misdiagnosis language. This second cut asks where inside steering it sits,
    # because the family this research targets is the intermittent one.
    print("\n=== 『原因不明・再現せず』の率を、断続性の記述で層別 ===")
    strat = {}
    with open(CMPL, encoding="latin-1") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) <= I_DESC:
                continue
            comp, desc = f[I_COMP].upper(), f[I_DESC].lower()
            if "STEERING" not in comp:
                continue
            strat[f[I_ODINO]] = (
                "ELECTRIC" in comp or "POWER ASSIST" in comp,
                any(t in desc for t in INTERMITTENT),
                any(t in desc for t in NO_FAULT),
            )

    def rate(sel):
        g = [v for v in strat.values() if sel(v)]
        return (sum(1 for v in g if v[2]) / len(g) if g else 0.0), len(g)

    for lab, sel in [("EPS × 断続的の記述あり", lambda v: v[0] and v[1]),
                     ("EPS × 断続的の記述なし", lambda v: v[0] and not v[1]),
                     ("操舵全般 × 断続的あり", lambda v: v[1]),
                     ("操舵全般 × 断続的なし", lambda v: not v[1])]:
        r, n = rate(sel)
        print(f"  {lab:<24} {r:>7.2%}  (n={n:,})")
    ei, _ = rate(lambda v: v[0] and v[1])
    en, _ = rate(lambda v: v[0] and not v[1])
    print(f"  EPS内の比: 断続あり / 断続なし = {ei/en:.2f}倍")
    rows.append(("EPS×断続あり_原因不明率", ei, 0.0, any_share["ALL"], ei/any_share["ALL"], 0.0))

    with OUT_TSV.open("w") as fh:
        fh.write("term_group\tshare_eps\tshare_steering\tshare_all\tlift_eps\tlift_steering\n")
        for r in rows:
            fh.write(f"{r[0]}\t{r[1]:.5f}\t{r[2]:.5f}\t{r[3]:.5f}\t{r[4]:.4f}\t{r[5]:.4f}\n")
        fh.write(f"n\t{len(pops['EPS'])}\t{len(pops['STEERING'])}\t{len(pops['ALL'])}\t-\t-\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
