#!/usr/bin/env python3
"""What conditions are intermittent steering faults reported under? (docs/212 -> docs/213)

Executes the protocol pre-registered in docs/212 without modification.

The product in docs/188 is capturing the moment a non-reproducing fault
happens, and capturing needs a trigger. This work has never asked what the
complaint corpus says about WHEN the fault occurs -- both prior uses only
counted the rate of a few phrases.

Ten condition categories, word lists fixed in docs/212 before running.
Everything is reported as a lift against the same category's rate across all
complaints, because "bump" may simply be a common word.

Unit is the complaint (ODINO), and the component and text flags are OR-ed
across a complaint's rows -- the bug docs/187 had to fix, where a later
non-steering row erased the steering flag and lost 2,130 complaints.

This measures how often a condition is WRITTEN, not how often it happens.
docs/189 settled that limit and it does not go away here.

Data: NHTSA FLAT_CMPL, US government work, public domain.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CMPL = REPO_ROOT / ".nhtsa_flat" / "FLAT_CMPL.txt"
OUT_TSV = REPO_ROOT / "data" / "trigger_conditions.tsv"

I_ODINO, I_COMP, I_DESC = 1, 11, 19

STEERING = re.compile(r"STEERING", re.I)
INTERMITTENT = re.compile(
    r"intermittent|comes and goes|on and off|sporadic|randomly|at times", re.I)

# docs/212, fixed before running.
CATEGORIES = [
    ("low_speed_parking", r"parking|low speed|slow speed|backing|reverse|u-turn"
                          r"|stop light|standstill"),
    ("highway",           r"highway|freeway|high speed|interstate|merging"),
    ("cold",              r"\bcold\b|cold start|morning|first start|winter|freezing"),
    ("hot",               r"\bhot\b|\bheat\b|summer|after driving|warmed up|long drive"),
    ("start_up",          r"start up|starting the|ignition|turn the key|first start"),
    ("bump_rough_road",   r"\bbump|pothole|rough road|railroad|uneven"),
    ("while_turning",     r"turning|while turning|cornering|\bcurve\b|lock to lock"),
    ("rain_moisture",     r"\brain|\bwet\b|humid|moisture|car wash|puddle"),
    ("momentary",         r"momentar|a second|briefly|instant|split second"),
    ("clears_on_restart", r"restart|turn off and|cycle the ignition|reset itself"),
]
CATS = [(n, re.compile(p, re.I)) for n, p in CATEGORIES]


def main() -> None:
    # per complaint: [is_steering, is_intermittent, cat flags...]
    rec: dict[str, list[bool]] = {}
    with open(CMPL, encoding="latin-1") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) <= I_DESC:
                continue
            odino, comp, desc = f[I_ODINO], f[I_COMP], f[I_DESC]
            cur = [bool(STEERING.search(comp)), bool(INTERMITTENT.search(desc))]
            cur += [bool(rx.search(desc)) for _, rx in CATS]
            prev = rec.get(odino)
            rec[odino] = cur if prev is None else [a or b for a, b in zip(prev, cur)]

    total = len(rec)
    steer_int = [v for v in rec.values() if v[0] and v[1]]
    n_si = len(steer_int)
    print(f"complaints            {total:,}")
    print(f"steering              {sum(1 for v in rec.values() if v[0]):,}")
    print(f"steering + intermittent {n_si:,}   (T3)")
    if not n_si:
        print("no complaints in scope")
        return

    print(f"\n{'category':<20}{'n':>8}{'rate':>9}{'all-complaint rate':>21}{'lift':>8}   verdict")
    rows, candidates = [], []
    for i, (name, _) in enumerate(CATS):
        n = sum(1 for v in steer_int if v[2 + i])
        r = n / n_si
        r_all = sum(1 for v in rec.values() if v[2 + i]) / total
        lift = r / r_all if r_all else float("nan")
        if n < 100:
            verdict = "n < 100: 倍率を語らない"
            shown = "     --"
        else:
            ok = lift >= 2.0
            verdict = "TRIGGER CANDIDATE" if ok else ""
            shown = f"{lift:>7.2f}"
            if ok:
                candidates.append((name, n, r, lift))
        print(f"{name:<20}{n:>8,}{r:>8.1%}{r_all:>20.1%}{shown}   {verdict}")
        rows.append((name, n, r, r_all, lift))

    # ---- post hoc, declared as such --------------------------------------
    # docs/212 fixed "all complaints" as the denominator. But a steering
    # complaint mentions turning for reasons that have nothing to do with
    # intermittency, so a lift computed that way flatters any steering-shaped
    # word. The same numbers against a steering-only denominator isolate what
    # is specific to INTERMITTENCY rather than to steering. Reported after the
    # registered result, not instead of it.
    steer_all = [v for v in rec.values() if v[0]]
    print(f"\npost hoc: same categories against a steering-only denominator "
          f"(n = {len(steer_all):,})")
    print(f"{'category':<20}{'intermittent':>14}{'all steering':>14}{'lift':>8}")
    for i, (name, _) in enumerate(CATS):
        n = sum(1 for v in steer_int if v[2 + i])
        r = n / n_si
        r_s = sum(1 for v in steer_all if v[2 + i]) / len(steer_all)
        print(f"{name:<20}{r:>13.1%}{r_s:>14.1%}"
              + (f"{r/r_s:>8.2f}" if r_s else "      --"))
        rows[i] = rows[i] + (r_s, r / r_s if r_s else float("nan"))

    print()
    if candidates:
        print(f"T2 -> {len(candidates)} trigger candidate(s): "
              + ", ".join(f"{c[0]} ({c[3]:.2f}x, n={c[1]:,})" for c in candidates))
    else:
        print("T2 -> no category reaches 2.0x with n >= 100. No trigger candidate.")
    print("\nThese are rates at which a condition is WRITTEN, not at which it happens")
    print("(docs/189 (4)). A 3x lift means written three times as often.")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("category\tn\trate_in_steering_intermittent\trate_all_complaints\tlift\t"
                  "rate_all_steering\tlift_vs_steering\n")
        for r in rows:
            out.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                                for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
