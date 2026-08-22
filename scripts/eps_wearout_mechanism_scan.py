#!/usr/bin/env python3
"""Do interconnect wear-out mechanisms actually appear in EPS field recalls? (docs/171)

Unit of analysis is the recall CAMPAIGN (CAMPNO), not the make/model/year
row. One campaign spans many rows, so counting rows multiplies a single
defect into dozens of apparent hits.

docs/170 left gap T: the thermal-degradation chain was demonstrated on a
NASA bench MOSFET, and whether die-attach style wear-out actually occurs in
EPS power electronics in the field was an assumption drawn by analogy.

NHTSA recall records carry a 6000-character defect summary written by the
manufacturer. This scans them for the named wear-out mechanisms, inside
steering vehicle campaigns, and compares EPS-specific campaigns against
steering campaigns generally.

Search terms are mechanism names fixed before running, not tuned to the
counts they produce:

  interconnect wear-out : die attach, solder, bond wire, braze
  thermal driver        : thermal cycl, thermal fatigue, overheat, thermal stress
  crack / separation    : crack, fracture, delamination, separation
  contact degradation   : fretting, corrosion, oxidation, contact resistance
  electrical symptom    : intermittent, open circuit, short circuit, loss of signal

Reference groups, so the numbers mean something:
  EPS      steering campaigns whose component text names ELECTRIC or ASSIST
  STEERING all steering vehicle campaigns
  ALL      all vehicle campaigns (base rate of the vocabulary itself)

Data: NHTSA FLAT_RCL, US government work, public domain.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

csv.field_size_limit(sys.maxsize)

REPO_ROOT = Path(__file__).resolve().parent.parent
RCL = REPO_ROOT / ".nhtsa_flat" / "FLAT_RCL_POST_2010.txt"
OUT_TSV = REPO_ROOT / "data" / "eps_wearout_mechanism_scan.tsv"

I_CAMPNO, I_MAKE, I_MODEL, I_YEAR, I_COMP, I_TYPE, I_RCDATE, I_DESC = 1, 2, 3, 4, 6, 10, 15, 19

GROUPS = {
    "接合部の摩耗故障": ["die attach", "die-attach", "solder", "bond wire", "wire bond", "braze"],
    "熱による駆動": ["thermal cycl", "thermal fatigue", "overheat", "thermal stress", "excessive heat"],
    "割れ・剥離": ["crack", "fracture", "delamination", "separat"],
    "接点の劣化": ["fretting", "corrosion", "oxidation", "contact resistance"],
    "電気的症状": ["intermittent", "open circuit", "short circuit", "loss of signal"],
}


def main() -> None:
    pop = {"EPS": [], "STEERING": [], "ALL": []}
    seen = set()
    with open(RCL, encoding="latin-1") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) <= I_DESC or f[I_TYPE] != "V":
                continue
            # one row per (make, model, year); the unit of analysis is the CAMPAIGN.
            # Counting rows inflates a single campaign into dozens of hits -- the
            # first run of this scan did exactly that and reported 14 solder hits
            # that were two campaigns.
            key = f[I_CAMPNO]
            if key in seen:
                continue
            seen.add(key)
            desc = f[I_DESC].lower()
            comp = f[I_COMP].upper()
            pop["ALL"].append((f, desc))
            if "STEERING" in comp:
                pop["STEERING"].append((f, desc))
                if "ELECTRIC" in comp or "ASSIST" in comp:
                    pop["EPS"].append((f, desc))

    print("母集団(重複除去済みキャンペーン数): " +
          "  ".join(f"{k}={len(v):,}" for k, v in pop.items()))
    print()
    print(f"{'機構グループ':<18}" + "".join(f"{k:>12}" for k in pop) + f"{'EPS/ALL比':>12}")
    print("-" * 68)
    rows = []
    for gname, terms in GROUPS.items():
        share = {}
        for pname, recs in pop.items():
            hit = sum(1 for _, d in recs if any(t in d for t in terms))
            share[pname] = hit / len(recs) if recs else 0.0
        lift = share["EPS"] / share["ALL"] if share["ALL"] else float("nan")
        print(f"{gname:<18}" + "".join(f"{share[k]:>11.1%}" for k in pop) + f"{lift:>11.2f}x")
        rows.append((gname, share["EPS"], share["STEERING"], share["ALL"], lift))

    print("\n=== 語別の内訳(EPSキャンペーン内) ===")
    c = Counter()
    for _, d in pop["EPS"]:
        for terms in GROUPS.values():
            for t in terms:
                if t in d:
                    c[t] += 1
    n = len(pop["EPS"])
    for t, v in c.most_common(18):
        print(f"  {t:<20} {v:>4} / {n}  ({v/n:>5.1%})")

    print("\n=== 接合部の摩耗故障に該当したEPSキャンペーンの例 ===")
    terms = GROUPS["接合部の摩耗故障"]
    shown = 0
    for f, d in pop["EPS"]:
        if any(t in d for t in terms):
            hits = [t for t in terms if t in d]
            snippet = re.sub(r"\s+", " ", f[I_DESC])[:190]
            print(f"  [{'/'.join(hits)}] {f[I_MAKE]} {f[I_MODEL][:22]} {f[I_YEAR]} ({f[I_RCDATE][:4]})")
            print(f"      {snippet}")
            shown += 1
            if shown >= 6:
                break
    if not shown:
        print("  該当なし")

    with OUT_TSV.open("w") as fh:
        fh.write("mechanism_group\tshare_eps\tshare_steering\tshare_all\tlift_eps_over_all\n")
        for r in rows:
            fh.write(f"{r[0]}\t{r[1]:.5f}\t{r[2]:.5f}\t{r[3]:.5f}\t{r[4]:.4f}\n")
        fh.write(f"n_eps\t{len(pop['EPS'])}\tn_steering\t{len(pop['STEERING'])}\tn_all\t{len(pop['ALL'])}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
