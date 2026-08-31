#!/usr/bin/env python3
"""What timescale does the field report for intermittent assist loss?
(docs/250 -> docs/251)

Executes the protocol pre-registered in docs/250 against NHTSA FLAT_CMPL,
already inventoried in data/dataset_prospect.tsv. No new acquisition.

The injection of docs/243 assumed events of 0.1-2.0 s. That grid was chosen,
not derived. This asks the complaint text which timescale it actually reports,
and what restores the assist.

Selection, fixed in docs/250 before any count was read:

    include   COMPDESC contains STEERING, and CDESCR carries an electric
              marker AND an assist-loss marker AND an intermittency marker
    exclude   hydraulic markers (pump, fluid, hose, belt, reservoir, leak)
              -- hydraulics are out of scope by the user's instruction --
              and external-cause markers (accident, collision, pothole)

Criteria: N1 share of readable elapsed times that are >= 60 s; N2 share of
readable persistence types that persist until a reset; N3 the recovery split,
descriptive only.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CMPL = REPO_ROOT / ".nhtsa_flat" / "FLAT_CMPL.txt"
OUT_TSV = REPO_ROOT / "data" / "field_timescale.tsv"

F_COMPDESC, F_CDESCR = 11, 19          # 1-based fields 12 and 20 in CMPL_layout.txt

ELECTRIC = re.compile(r"ELECTRIC(AL|ALLY)? POWER STEERING|ELECTRONIC POWER STEERING|"
                      r"\bEPS\b|ELECTRIC STEERING|STEERING MOTOR|POWER STEERING")
ASSIST_LOSS = re.compile(r"LOSS OF POWER STEERING|LOST POWER STEERING|POWER STEERING FAIL|"
                         r"NO POWER STEERING|HARD TO STEER|STIFF|HEAVY")
INTERMITTENT = re.compile(r"INTERMITTENT|COMES AND GOES|COME AND GO|ON AND OFF|"
                          r"SOMETIMES|OCCASIONALLY|RANDOMLY|SPORADIC")

HYDRAULIC = re.compile(r"\bPUMP\b|\bFLUID\b|\bHOSE\b|\bBELT\b|RESERVOIR|\bLEAK|HYDRAULIC")
EXTERNAL = re.compile(r"ACCIDENT|COLLISION|POTHOLE")

# elapsed time into the drive, in the three shapes fixed in docs/250
UNIT = r"(SECOND|SEC|MINUTE|MIN|HOUR|HR|MILE)S?"
NUM = r"(\d+(?:\.\d+)?|A HALF|HALF|AN?)"
ELAPSED = [
    re.compile(rf"AFTER (?:DRIVING |DRIVING FOR |ABOUT |APPROXIMATELY |ROUGHLY )*{NUM}[ -]{UNIT}"),
    re.compile(rf"{NUM}[ -]{UNIT} INTO"),
    re.compile(rf"WITHIN (?:ABOUT |APPROXIMATELY )*{NUM}[ -]{UNIT}"),
]

RESET_IGN = re.compile(r"IGNITION|RESTART|RE-START|TURN(ED|ING)? (IT |THE CAR |ENGINE )?OFF|"
                       r"SHUT (IT |THE CAR )?OFF|CYCLE THE KEY|KEY CYCLE")
RESET_COOL = re.compile(r"COOL(ED|S|ING)? ?(DOWN|OFF)?|SAT FOR|WAIT(ED|ING)? |NEXT DAY|"
                        r"NEXT MORNING|LET IT SIT|PARKED FOR")
RECOVER_SELF = re.compile(r"CAME BACK|COMES BACK|RETURN(ED|S)?|RESUMED|RESTORED")
MOMENTARY = re.compile(r"MOMENTARY|MOMENTARILY|BRIEF(LY)?|FOR A SECOND|FOR A FEW SECONDS|"
                       r"INSTANT(LY)?|FLASH|SPLIT SECOND")

TO_SECONDS = {"SECOND": 1, "SEC": 1, "MINUTE": 60, "MIN": 60, "HOUR": 3600, "HR": 3600}


def parse_num(s: str) -> float | None:
    s = s.strip()
    if s in ("A HALF", "HALF"):
        return 0.5
    if s in ("A", "AN"):
        return 1.0
    try:
        return float(s)
    except ValueError:
        return None


def elapsed_seconds(d: str):
    """First elapsed-time expression, in seconds. MILE is not a time -> reported apart."""
    for rx in ELAPSED:
        m = rx.search(d)
        if not m:
            continue
        n = parse_num(m.group(1))
        unit = m.group(2)
        if n is None:
            continue
        if unit.startswith("MILE"):
            return None, "mile"
        base = unit.rstrip("S")
        if base in TO_SECONDS:
            return n * TO_SECONDS[base], "time"
    return None, "none"


def main() -> None:
    if not CMPL.exists():
        sys.exit(f"missing {CMPL}")

    kept, drop_hyd, drop_ext, n_steer, n_marker = [], 0, 0, 0, 0
    with CMPL.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) <= F_CDESCR:
                continue
            if "STEERING" not in f[F_COMPDESC].upper():
                continue
            n_steer += 1
            d = f[F_CDESCR].upper()
            if not (ELECTRIC.search(d) and ASSIST_LOSS.search(d) and INTERMITTENT.search(d)):
                continue
            n_marker += 1
            if HYDRAULIC.search(d):
                drop_hyd += 1
                continue
            if EXTERNAL.search(d):
                drop_ext += 1
                continue

            secs, kind = elapsed_seconds(d)
            ign, cool = bool(RESET_IGN.search(d)), bool(RESET_COOL.search(d))
            selfrec = bool(RECOVER_SELF.search(d))
            mom = bool(MOMENTARY.search(d))

            if ign or cool:
                persist = "until_reset"
            elif mom:
                persist = "momentary"
            else:
                persist = "unreadable"

            if ign:
                recovery = "ignition"
            elif cool:
                recovery = "rest_or_cool"
            elif selfrec:
                recovery = "spontaneous"
            else:
                recovery = "unreadable"

            kept.append({"cmplid": f[0], "elapsed_s": secs, "elapsed_kind": kind,
                         "persist": persist, "recovery": recovery})

    print(f"COMPDESC に STEERING            : {n_steer}")
    print(f"  3つの語をすべて含む           : {n_marker}")
    print(f"  油圧の語で除外                : {drop_hyd}")
    print(f"  外力の語で除外                : {drop_ext}")
    print(f"  **採用**                      : {len(kept)}")
    if not kept:
        sys.exit("該当なし")

    # ---- N1 elapsed time -------------------------------------------------
    times = [r["elapsed_s"] for r in kept if r["elapsed_kind"] == "time"]
    miles = sum(1 for r in kept if r["elapsed_kind"] == "mile")
    print(f"\n=== N1 走り出しからの経過時間 ===")
    print(f"  時間として読めた             : {len(times)} 件 "
          f"(距離で書かれていた {miles} 件は時間に換算せず除外)")
    if times:
        times_sorted = sorted(times)
        over60 = sum(1 for t in times if t >= 60)
        med = times_sorted[len(times_sorted) // 2]
        print(f"  中央値                       : {med:.0f} 秒 (= {med/60:.1f} 分)")
        print(f"  60秒以上                     : {over60}/{len(times)} = {over60/len(times):.0%}"
              f"  {'PASS' if over60 > len(times)/2 else 'FAIL'} (基準: 過半)")
        print(f"  2秒以下(注入格子の範囲)     : "
              f"{sum(1 for t in times if t <= 2.0)}/{len(times)}")
        for lo, hi, lab in [(0, 60, "1分未満"), (60, 600, "1〜10分"),
                            (600, 3600, "10〜60分"), (3600, 1e9, "1時間以上")]:
            c = sum(1 for t in times if lo <= t < hi)
            print(f"    {lab:<10}: {c:>4} 件")

    # ---- N2 persistence --------------------------------------------------
    print(f"\n=== N2 持続の型 ===")
    pc = Counter(r["persist"] for r in kept)
    readable = pc["until_reset"] + pc["momentary"]
    print(f"  読めた                       : {readable} / {len(kept)}")
    if readable:
        print(f"  リセットまで持続             : {pc['until_reset']} "
              f"({pc['until_reset']/readable:.0%})  "
              f"{'PASS' if pc['until_reset'] > readable/2 else 'FAIL'} (基準: 過半)")
        print(f"  瞬間的                       : {pc['momentary']} "
              f"({pc['momentary']/readable:.0%})")

    # ---- N3 recovery -----------------------------------------------------
    print(f"\n=== N3 復帰の仕方(記述のみ) ===")
    rc = Counter(r["recovery"] for r in kept)
    for k in ("ignition", "rest_or_cool", "spontaneous", "unreadable"):
        print(f"  {k:<14}: {rc[k]:>5} ({rc[k]/len(kept):.0%})")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with OUT_TSV.open("w") as fh:
        fh.write("cmplid\telapsed_s\telapsed_kind\tpersist\trecovery\n")
        for r in kept:
            e = "" if r["elapsed_s"] is None else f"{r['elapsed_s']:.0f}"
            fh.write(f"{r['cmplid']}\t{e}\t{r['elapsed_kind']}\t{r['persist']}\t{r['recovery']}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
