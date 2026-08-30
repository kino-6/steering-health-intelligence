#!/usr/bin/env python3
"""Run the specification over real logs (docs/228 -> docs/229).

Executes the protocol pre-registered in docs/228 without modification.

docs/225 specifies a recorder that declines to declare when it cannot
normalise, and docs/227 showed one drive covers a seventh to a thirty-fifth of
the speed range a vehicle visits. So the question is how often the recorder
stays silent, because one that is silent most of the time is not deployable.

No end-of-line fingerprint exists here, so the first 30% of each log stands in
for one. That substitute carries docs/227's shortfall by construction, so what
this measures is the cost of a NARROW fingerprint, not the performance of a
good one. Widening the span by 1, 2, 5, 10 and 20 gives the requirement curve.

Temperature is absent from this dataset and may well be the main reason a real
operating point falls outside a fingerprint. Not covered.

Data: commaSteeringControl, comma.ai, MIT License.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / ".public_log_cache"
OUT_TSV = REPO_ROOT / "data" / "recorder_simulation.tsv"

FP_FRACTION = 0.30                 # docs/228: first 30% is the fingerprint, fixed
WIDEN = [1, 2, 5, 10, 20]          # docs/228: report all of these
TARGETS = [0.10, 0.01]             # docs/228: both fixed before running
MIN_SAMPLES = 100
ROBUST = 3.0 * 1.4826

# docs/225 says what one declaration carries: deviation, its granularity,
# validity, and the operating point at that instant.
RECORD_FIELDS = ["deviation", "granularity", "validity", "speed", "torque", "temperature"]
RECORD_BYTES = 4 * len(RECORD_FIELDS)


def read_log(path: Path):
    v, s, d, l, act, pressed = [], [], [], [], [], []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                act.append(row["latActive"] == "True")
                pressed.append(row["steeringPressed"] == "True")
                v.append(float(row["vEgo"]))
                s.append(abs(float(row["steeringAngleDeg"])))
                d.append(float(row["latAccelDesired"]))
                l.append(float(row["latAccelLocalizer"]))
            except (ValueError, KeyError):
                return None
    keep = np.array(act) & ~np.array(pressed)
    if keep.sum() < MIN_SAMPLES:
        return None
    return (np.array(v)[keep], np.array(s)[keep],
            np.array(l)[keep] - np.array(d)[keep])


def main() -> None:
    silent = defaultdict(lambda: defaultdict(list))     # model -> widen -> rates
    emitted, floors = defaultdict(list), defaultdict(list)
    for model in sorted(p.name for p in CACHE.iterdir() if p.is_dir()):
        for f in sorted((CACHE / model).glob("*.csv")):
            r = read_log(f)
            if r is None:
                continue
            v, s, e = r
            cut = int(len(v) * FP_FRACTION)
            if cut < 20 or len(v) - cut < 20:
                continue
            fv, fs = v[:cut], s[:cut]
            floors[model].append(ROBUST * float(np.median(np.abs(e[:cut] - np.median(e[:cut])))))
            # fingerprint span: 5th-95th percentile of the fingerprint window
            spans = []
            for arr in (fv, fs):
                lo, hi = np.percentile(arr, 5), np.percentile(arr, 95)
                spans.append((float((lo + hi) / 2), float(hi - lo)))
            ev, es = v[cut:], s[cut:]
            for w in WIDEN:
                inside = np.ones(len(ev), dtype=bool)
                for arr, (mid, width) in zip((ev, es), spans):
                    half = max(width, 1e-9) * w / 2.0
                    inside &= (arr >= mid - half) & (arr <= mid + half)
                silent[model][w].append(1.0 - float(inside.mean()))
                if w == 1:
                    emitted[model].append(int(inside.sum()))

    print(f"{'model':<24}{'logs':>7}" + "".join(f"{'x'+str(w):>10}" for w in WIDEN))
    rows = []
    for model, byw in silent.items():
        n = len(byw[WIDEN[0]])
        med = {w: float(np.median(byw[w])) for w in WIDEN}
        print(f"{model:<24}{n:>7}" + "".join(f"{med[w]:>9.1%}" for w in WIDEN))
        rows.append((model, n, *[med[w] for w in WIDEN]))
    print("  (share of the evaluated samples where the recorder DECLINES to declare)")

    print("\nE3 widening needed to bring silence below each target")
    print(f"{'model':<24}" + "".join(f"{'<'+str(int(t*100))+'%':>12}" for t in TARGETS))
    for model, byw in silent.items():
        med = {w: float(np.median(byw[w])) for w in WIDEN}
        cells = []
        for t in TARGETS:
            hit = next((w for w in WIDEN if med[w] < t), None)
            cells.append(f"x{hit}" if hit else f">x{WIDEN[-1]}")
        print(f"{model:<24}" + "".join(f"{c:>12}" for c in cells))

    print(f"\nE4 output volume, at the specified fingerprint (x1)")
    print(f"   one declaration = {len(RECORD_FIELDS)} float32 = {RECORD_BYTES} bytes "
          f"({', '.join(RECORD_FIELDS)})")
    for model, ns in emitted.items():
        per_drive = float(np.median(ns))
        # a log is 60 s of engaged samples at 10 Hz; the spec keeps a 5 s window,
        # so a declaration is not written per sample -- report both readings.
        print(f"   {model:<24} {per_drive:>6.0f} samples inside the fingerprint per 42 s "
              f"evaluated -> {per_drive*RECORD_BYTES/1024:.1f} KB if every sample were kept,"
              f" {per_drive/50*RECORD_BYTES:.0f} B at one record per 5 s window")

    print("\nfingerprint noise floor taken from the first 30%:")
    for model, fl in floors.items():
        print(f"   {model:<24} {float(np.median(fl)):.4f} m/s^2")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("model\tlogs\t" + "\t".join(f"silent_x{w}" for w in WIDEN) + "\n")
        for r in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
