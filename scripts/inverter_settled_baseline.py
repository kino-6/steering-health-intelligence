#!/usr/bin/env python3
"""The same test against a settled baseline (docs/218 -> docs/219).

Identical to inverter_signal_requirement.py except for one thing, fixed in
docs/218: only the last 60% of EVERY file is used, normal and fault alike,
using the five-way split docs/215 published before this test existed.

docs/217 failed to identify the affected phase, and the likeliest reason was
the reference -- the normal file's phase B asymmetry ratio was 3.017 where
balance is 1, from the drift docs/215 found. Choosing a baseline after a
failure is how tuning happens, so the window rule is independent of the
outcome, applies to all files, and no other fraction is tried.

docs/217's verdict is not withdrawn. This is a separate test that follows it.

Original header follows.

Do phase currents alone locate an open-circuit fault? (docs/216 -> docs/217)

Executes the protocol pre-registered in docs/216 without modification.

docs/205 answered this on the winding side -- phase current alone was not
enough and an accelerometer was needed. This is the inverter-side
counterpart: can the signals an EPS ECU already carries say WHICH half-bridge
opened and on WHICH side, or is per-half-bridge temperature required.

No classifier is used. One recording per condition, and per docs/215 only the
healthy class is non-stationary, so any separator would be identifying the
recording rather than the fault -- the mistake docs/162, docs/201 and docs/203
each had to correct. The physics fixes a direction instead and the only
question is whether that direction appears.

A half-bridge sources through its high-side switch and sinks through its low
side, so an open switch removes one polarity from that phase. Predictions
fixed in docs/216 before running:

    HB2 high-side open  ->  phase B positive suppressed   (d_B negative)
    HB3 low-side open   ->  phase C negative suppressed   (d_C positive)

Only Ia and Ib are measured; Ic follows from three-phase balance.

10 Hz cannot represent the current waveform and is very likely aliased, so
only the marginal distribution is used. Percentiles survive aliasing; a
waveform does not.

Data: Bacha et al., Data in Brief 58 (2025), CC BY 4.0.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / ".pmsm_inverter" / "PMSM-inverter-fault-diagnosis-1.0.0" / "raw_data"
OUT_TSV = REPO_ROOT / "data" / "inverter_settled_baseline.tsv"
TAIL = 0.60          # docs/218: last 60% of every file, fixed, not tuned

LINE = re.compile(r"(\d+):(\d+):(\d+)\.(\d+)\s*->\s*(.*)")
COLS = ["Ia", "Ib", "Vdc", "Idc", "T1", "T2", "T3", "Vd"]

CONDITIONS = [
    ("NORMAL",           "normal_operation/NORMAL_OP.txt"),
    ("HB2_HIGH_SIDE_OC", "fault_scenarios/HB2_HIGH_SIDE_OC.txt"),
    ("HB3_LOW_SIDE_OC",  "fault_scenarios/HB3_LOW_SIDE_OC.txt"),
    ("HB1_LOW_SIDE_SC",  "fault_scenarios/HB1_LOW_SIDE_SC.txt"),
    ("HB2_HIGH_SIDE_SC", "fault_scenarios/HB2_HIGH_SIDE_SC.txt"),
    ("HB3_HIGH_SIDE_SC", "fault_scenarios/HB3_HIGH_SIDE_SC.txt"),
    ("HB1_OVER_TEMP",    "fault_scenarios/HB1_OVER_TEMP.txt"),
    ("HB1&2_OVER_TEMP",  "fault_scenarios/HB1&2_OVER_TEMP.txt"),
    ("HB3_OVER_TEMP",    "fault_scenarios/HB3_OVER_TEMP.txt"),
]
# docs/216, fixed before running: (condition, affected phase, expected sign of d)
PREDICTIONS = [("HB2_HIGH_SIDE_OC", "B", -1), ("HB3_LOW_SIDE_OC", "C", +1)]


def load(path: Path) -> np.ndarray:
    out = []
    for line in open(path, encoding="latin-1"):
        m = LINE.match(line.strip())
        if not m:
            continue
        v = m.group(5).split()
        if len(v) == 8:
            out.append([int(x) for x in v])
    a = np.array(out, dtype=float)
    return a[int(len(a) * (1.0 - TAIL)):]        # docs/218


def asymmetry(v: np.ndarray) -> dict[str, float]:
    """R = |p90| / |p10| on each phase, after centring on the file's own median."""
    ia = v[:, 0] - np.median(v[:, 0])
    ib = v[:, 1] - np.median(v[:, 1])
    ic = -(ia + ib)                     # three-phase balance, docs/216
    out = {}
    for name, x in (("A", ia), ("B", ib), ("C", ic)):
        hi, lo = np.percentile(x, 90), abs(np.percentile(x, 10))
        out[name] = float(hi / lo) if lo > 0 else float("inf")
    return out


def main() -> None:
    data = {n: load(RAW / p) for n, p in CONDITIONS}
    R = {n: asymmetry(v) for n, v in data.items()}
    base = R["NORMAL"]

    print(f"{'condition':<20}" + "".join(f"{'R_'+p:>9}" for p in "ABC")
          + "".join(f"{'d_'+p:>9}" for p in "ABC") + "   largest |d|")
    rows = []
    for name, _ in CONDITIONS:
        d = {p: float(np.log(R[name][p]) - np.log(base[p])) for p in "ABC"}
        big = max("ABC", key=lambda p: abs(d[p]))
        print(f"{name:<20}" + "".join(f"{R[name][p]:>9.3f}" for p in "ABC")
              + "".join(f"{d[p]:>+9.3f}" for p in "ABC") + f"   {big}")
        rows.append((name, *[R[name][p] for p in "ABC"], *[d[p] for p in "ABC"], big))

    print("\nQ0 is the settled baseline balanced? (each R_p should sit in 1/2 .. 2)")
    q0 = all(0.5 <= base[p] <= 2.0 for p in "ABC")
    print("   " + "  ".join(f"R_{p}={base[p]:.3f}" for p in "ABC")
          + f"   -> {'balanced' if q0 else 'STILL NOT BALANCED'}")

    print("\n" + "=" * 78)
    p1 = p2 = 0
    for cond, phase, sign in PREDICTIONS:
        d = {p: float(np.log(R[cond][p]) - np.log(base[p])) for p in "ABC"}
        big = max("ABC", key=lambda p: abs(d[p]))
        ok1 = np.sign(d[phase]) == sign
        ok2 = big == phase
        p1 += ok1
        p2 += ok2
        want = "negative" if sign < 0 else "positive"
        print(f"{cond}: predicted phase {phase}, {want} d")
        print(f"   d_A={d['A']:+.3f}  d_B={d['B']:+.3f}  d_C={d['C']:+.3f}")
        print(f"   P1 direction {'ok' if ok1 else 'MISMATCH'} (d_{phase}={d[phase]:+.3f})"
              f"   P2 phase identified as {big} -> {'ok' if ok2 else 'MISMATCH'}")
    print(f"\nQ1 predicted direction   : {p1}/2 -> {'PASS' if p1 == 2 else 'FAIL'}")
    print(f"Q2 affected phase largest: {p2}/2 -> {'PASS' if p2 == 2 else 'FAIL'}")
    ok = p1 == 2 and p2 == 2
    print("-> " + ("with a settled baseline, phase currents alone locate the fault"
                   if ok else
                   "even with a settled baseline, phase currents alone do NOT locate it"))
    if ok and not q0:
        print("   NOTE: the baseline is STILL not balanced (Q0 failed). This did not")
        print("   pass because the reference was fixed. docs/218 forbids that reading.")

    print("\nsecondary, reported only: temperatures as the baseline for what they add")
    print(f"{'condition':<20}{'T1':>8}{'T2':>8}{'T3':>8}   hottest vs normal")
    tb = [np.median(data['NORMAL'][:, 4 + i]) for i in range(3)]
    for name, _ in CONDITIONS:
        t = [float(np.median(data[name][:, 4 + i])) for i in range(3)]
        # NTC with a divider: hotter means lower resistance, so the direction is
        # not assumed here -- the raw ADC medians and their deltas are printed.
        dd = [t[i] - tb[i] for i in range(3)]
        big = max(range(3), key=lambda i: abs(dd[i]))
        print(f"{name:<20}" + "".join(f"{x:>8.1f}" for x in t)
              + f"   T{big+1} moves most ({dd[big]:+.1f})")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("condition\tR_A\tR_B\tR_C\td_A\td_B\td_C\tlargest_abs_d\n")
        for r in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
