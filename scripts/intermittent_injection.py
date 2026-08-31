#!/usr/bin/env python3
"""Inject intermittent events and measure the specified recorder (docs/243 -> docs/244).

Executes the protocol pre-registered in docs/243 without modification.

docs/225 left detection probability blank for want of ground truth. Injection
supplies ground truth by construction, which is R13; it cannot supply R12, so
this measures whether the specified recorder would catch an event, not whether
events occur.

Real healthy logs carry the injection: a rectangular excursion of amplitude
1-10 times that log's own floor, lasting 0.1-2.0 s. The rectangle is an
assumption -- no public data shows the shape of a real intermittent assist loss.

The comparison is the point. docs/240 argued excursions are counted rather than
averaged, and this tests that where the answer is known:

    mean detector  window mean of the residual   (docs/144, docs/223 lineage)
    max  detector  window maximum |residual|     (docs/240, IPC-9701 spirit)

Both thresholds are set to a 1.0% per-window false-alarm rate on uninjected
logs, fixed in docs/243 before running, and detection is compared there.

Data: commaSteeringControl, comma.ai, MIT License. 10 Hz, 5 s windows.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / ".public_log_cache"
OUT_TSV = REPO_ROOT / "data" / "intermittent_injection.tsv"

WIN = 50                      # 5 s at 10 Hz, the docs/225 window
AMPS = [1, 2, 3, 5, 10]       # multiples of the log's own floor, docs/243
DURS = [1, 2, 5, 10, 20]      # samples: 0.1 .. 2.0 s, docs/243
FA_TARGET = 0.010             # 1.0% per window, fixed before running
MIN_SAMPLES = 200
ROBUST = 3.0 * 1.4826
RNG = np.random.default_rng(20260831)


def read_log(path: Path):
    d, l, act, pressed = [], [], [], []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                act.append(row["latActive"] == "True")
                pressed.append(row["steeringPressed"] == "True")
                d.append(float(row["latAccelDesired"]))
                l.append(float(row["latAccelLocalizer"]))
            except (ValueError, KeyError):
                return None
    keep = np.array(act) & ~np.array(pressed)
    if keep.sum() < MIN_SAMPLES:
        return None
    return np.array(l)[keep] - np.array(d)[keep]


def windows(e):
    k = len(e) // WIN
    return e[:k * WIN].reshape(k, WIN) if k else None


def main() -> None:
    residuals, floors = [], []
    for model in sorted(p.name for p in CACHE.iterdir() if p.is_dir()):
        for f in sorted((CACHE / model).glob("*.csv")):
            e = read_log(f)
            if e is None:
                continue
            g = float(ROBUST * np.median(np.abs(e - np.median(e))))
            if g <= 0:
                continue
            residuals.append(e)
            floors.append(g)
    print(f"logs: {len(residuals)}   floor median {np.median(floors):.4f} m/s^2")

    # --- clean statistics, to set both thresholds at the same false-alarm rate
    clean_mean, clean_max = [], []
    for e, g in zip(residuals, floors):
        w = windows(e)
        if w is None:
            continue
        clean_mean.append(np.abs(w.mean(axis=1)) / g)
        clean_max.append(np.abs(w).max(axis=1) / g)
    clean_mean = np.concatenate(clean_mean)
    clean_max = np.concatenate(clean_max)
    t_mean = float(np.quantile(clean_mean, 1 - FA_TARGET))
    t_max = float(np.quantile(clean_max, 1 - FA_TARGET))
    print(f"windows (clean): {clean_mean.size:,}")
    print(f"thresholds at {FA_TARGET:.1%} false alarm, in units of the log's floor:")
    print(f"   mean detector {t_mean:.3f}      max detector {t_max:.3f}")
    print(f"   achieved FA:  mean {np.mean(clean_mean > t_mean):.3%}  "
          f"max {np.mean(clean_max > t_max):.3%}")

    # --- inject one event per log and test the window containing it
    print(f"\n{'':>6}" + "".join(f"{'D=' + str(d) + 'sm':>22}" for d in DURS))
    print(f"{'A/g':>6}" + "".join(f"{'(' + f'{d/10:.1f}' + 's)  mean / max':>22}" for d in DURS))
    rows = []
    for A in AMPS:
        line = f"{A:>6}"
        for D in DURS:
            hit_m = hit_x = n = 0
            for e, g in zip(residuals, floors):
                if len(e) < WIN * 2:
                    continue
                # place the event fully inside one window
                wi = int(RNG.integers(0, len(e) // WIN))
                off = int(RNG.integers(0, max(1, WIN - D)))
                seg = e[wi * WIN:(wi + 1) * WIN].copy()
                seg[off:off + D] += A * g * RNG.choice([-1.0, 1.0])
                n += 1
                hit_m += abs(seg.mean()) / g > t_mean
                hit_x += np.abs(seg).max() / g > t_max
            dm, dx = hit_m / n, hit_x / n
            line += f"{dm:>11.1%}{dx:>11.1%}"
            rows.append((A, D, D / 10, dm, dx, n))
        print(line)

    print("\nM2  smallest amplitude reaching 90% detection, per duration:")
    print(f"{'duration':>10}{'mean detector':>16}{'max detector':>15}{'ratio':>9}")
    for D in DURS:
        def smallest(idx):
            for A in AMPS:
                r = next(r for r in rows if r[0] == A and r[1] == D)
                if r[idx] >= 0.90:
                    return A
            return None
        am, ax = smallest(3), smallest(4)
        f = lambda v: f"{v}x g" if v else f">{AMPS[-1]}x g"
        ratio = f"{am/ax:.1f}x" if am and ax else "-"
        print(f"{D/10:>9.1f}s{f(am):>16}{f(ax):>15}{ratio:>9}")

    wins = sum(1 for D in DURS for A in AMPS
               if (r := next(r for r in rows if r[0] == A and r[1] == D))[4] > r[3] + 0.02)
    print(f"\nM3  max detector better than mean by >2 points: {wins}/{len(rows)} cells")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("amplitude_over_floor\tduration_samples\tduration_s\t"
                "detect_mean\tdetect_max\tn_logs\n")
        for r in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")
    print("This measures the detector, not the phenomenon. The rectangular event")
    print("shape is an assumption (docs/243).")


if __name__ == "__main__":
    main()
