#!/usr/bin/env python3
"""Split STEERING complaints into coarse failure modes by summary keywords.

Residual candidate #2 (docs/137): does the elevated steering share in the
recalled cohorts specifically reflect LOSS OF ASSIST (the recalled failure
mode), or just more steering complaints of every kind?

Method: keyword buckets over the complaint summary text, priority order.
This is a coarse public-text proxy, not a failure-mode determination.
Uses only the local .nhtsa_cache written by steering_cohort_backtest.py.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / ".nhtsa_cache"
OUT_TSV = REPO_ROOT / "data" / "steering_mode_split.tsv"

VEHICLES = {
    "fusion": [("ford_fusion", y) for y in (2008, 2009, 2010, 2011, 2012, 2013, 2014)],
    "silverado": [("chevrolet_silverado1500", y) for y in (2011, 2012, 2014, 2015, 2016, 2017)],
}

# priority order: first match wins
MODES = [
    ("loss_of_assist", [
        "POWER STEERING ASSIST", "STEERING ASSIST", "LOSS OF POWER STEERING",
        "LOST POWER STEERING", "POWER STEERING FAIL", "POWER STEERING WENT OUT",
        "POWER STEERING STOPPED", "NO POWER STEERING", "HARD TO STEER",
        "HARD TO TURN", "DIFFICULT TO TURN", "DIFFICULT TO STEER", "STIFF",
    ]),
    ("noise_vibration", ["NOISE", "CLUNK", "POP", "SQUEAK", "RATTLE", "VIBRAT", "SHAKE"]),
    ("wander_pull", ["WANDER", "PULL", "DRIFT", "LOOSE", "PLAY IN THE STEERING"]),
    ("column_lock_key", ["COLUMN LOCK", "STEERING LOCK", "IGNITION", "KEY STUCK"]),
]


def classify(summary: str) -> str:
    text = summary.upper()
    for mode, needles in MODES:
        if any(n in text for n in needles):
            return mode
    return "other"


def main() -> None:
    lines = ["vehicle\tcohort\tsteering_total\tloss_of_assist\tnoise_vibration\twander_pull\tcolumn_lock_key\tother\tloss_of_assist_share"]
    for vehicle, cohorts in VEHICLES.items():
        print(f"== {vehicle} ==")
        print(f"{'cohort':<8} {'steer':>6} {'assist':>7} {'noise':>6} {'wander':>7} {'column':>7} {'other':>6}  assist_share")
        for slug, year in cohorts:
            cache = CACHE_DIR / f"{slug}_{year}.json"
            if not cache.exists():
                print(f"MY{year}: cache missing, skip")
                continue
            counts = {m: 0 for m, _ in MODES}
            counts["other"] = 0
            total = 0
            for c in json.loads(cache.read_text()).get("results", []):
                if "STEERING" not in (c.get("components") or "").upper():
                    continue
                total += 1
                counts[classify(c.get("summary") or "")] += 1
            share = counts["loss_of_assist"] / total if total else 0.0
            print(f"MY{year:<6} {total:>6} {counts['loss_of_assist']:>7} {counts['noise_vibration']:>6} "
                  f"{counts['wander_pull']:>7} {counts['column_lock_key']:>7} {counts['other']:>6}  {share:.0%}")
            lines.append(f"{vehicle}\tMY{year}\t{total}\t{counts['loss_of_assist']}\t{counts['noise_vibration']}"
                         f"\t{counts['wander_pull']}\t{counts['column_lock_key']}\t{counts['other']}\t{share:.4f}")
    OUT_TSV.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
