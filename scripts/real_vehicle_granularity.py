#!/usr/bin/env python3
"""The per-unit method on real vehicle logs (docs/220 -> docs/221).

Executes the protocol pre-registered in docs/220 without modification.

Per-unit baselining with operating-point normalisation has only been tried on
test rigs here. commaSteeringControl is real driving, so this measures what
the method's noise floor looks like on a road rather than a bench.

    e      = latAccelLocalizer - latAccelDesired      requested vs achieved
    g      = 3 * 1.4826 * MAD(e)                      this log's own floor
    e_norm = e minus a linear fit on speed and |steering angle|, fitted
             WITHIN the log -- that fit is what makes it per-unit
    g_norm = 3 * 1.4826 * MAD(e_norm)

No fault labels exist, so nothing here measures detection. It measures
granularity. And the residual is not an EPS quantity: it carries controller
tracking error, road disturbance and estimator error, and says whether the
requested lateral acceleration appeared.

Data: commaSteeringControl, comma.ai, MIT License.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / ".public_log_cache"
OUT_TSV = REPO_ROOT / "data" / "real_vehicle_granularity.tsv"

MIN_SAMPLES = 100          # a log needs enough engaged samples to fit anything
ROBUST = 3.0 * 1.4826


def mad_g(x: np.ndarray) -> float:
    return float(ROBUST * np.median(np.abs(x - np.median(x))))


def read_log(path: Path):
    v, s, d, l, act, pressed = [], [], [], [], [], []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                act.append(row["latActive"] == "True")
                pressed.append(row["steeringPressed"] == "True")
                v.append(float(row["vEgo"]))
                s.append(float(row["steeringAngleDeg"]))
                d.append(float(row["latAccelDesired"]))
                l.append(float(row["latAccelLocalizer"]))
            except (ValueError, KeyError):
                return None
    a = np.array
    keep = a(act) & ~a(pressed)
    if keep.sum() < MIN_SAMPLES:
        return None
    return a(v)[keep], np.abs(a(s)[keep]), a(l)[keep] - a(d)[keep]


def main() -> None:
    rows = []
    print(f"{'model':<24}{'logs':>7}{'g median':>12}{'g_norm median':>16}"
          f"{'reduction':>11}{'tail rate':>11}{'max/g':>9}")
    for model in sorted(p.name for p in CACHE.iterdir() if p.is_dir()):
        gs, gns, tails, maxes = [], [], [], []
        for f in sorted((CACHE / model).glob("*.csv")):
            r = read_log(f)
            if r is None:
                continue
            v, sa, e = r
            g = mad_g(e)
            X = np.column_stack([v, sa, np.ones(len(v))])
            try:
                coef, *_ = np.linalg.lstsq(X, e, rcond=None)
            except np.linalg.LinAlgError:
                continue
            en = e - X @ coef
            gn = mad_g(en)
            if g <= 0 or gn <= 0:
                continue
            gs.append(g)
            gns.append(gn)
            tails.append(float(np.mean(np.abs(en) > gn)))
            maxes.append(float(np.max(np.abs(en)) / gn))
        if not gs:
            print(f"{model:<24}{0:>7}   (no usable logs)")
            continue
        mg, mgn = float(np.median(gs)), float(np.median(gns))
        red = 1.0 - mgn / mg
        print(f"{model:<24}{len(gs):>7}{mg:>12.4f}{mgn:>16.4f}{red:>10.1%}"
              f"{np.median(tails):>11.2%}{np.median(maxes):>9.1f}")
        rows.append((model, len(gs), mg, mgn, red,
                     float(np.median(tails)), float(np.median(maxes))))

    print()
    ok = [r for r in rows if r[4] >= 0.10]
    print(f"R2 normalisation cuts granularity by >= 10%: {len(ok)}/{len(rows)} models "
          f"-> {'PASS' if len(ok) == len(rows) and rows else 'FAIL'} (needs all)")
    if rows:
        print(f"R1 granularity on real vehicles: g_norm median "
              f"{min(r[3] for r in rows):.4f} .. {max(r[3] for r in rows):.4f} m/s^2")
        print(f"R3 tail: {min(r[5] for r in rows):.2%} .. {max(r[5] for r in rows):.2%} "
              f"of samples beyond the log's own floor; "
              f"max excursion {min(r[6] for r in rows):.1f} .. {max(r[6] for r in rows):.1f} x")
    print("\nNo fault labels exist. Nothing here is a detection result.")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("model\tlogs\tg_median\tg_norm_median\treduction\ttail_rate\tmax_over_g\n")
        for r in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
