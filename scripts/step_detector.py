#!/usr/bin/env python3
"""Can a per-session baseline still see an offset that lasts the rest of the drive?
(docs/254 -> docs/255)

Executes the protocol pre-registered in docs/254 against commaSteeringControl,
already inventoried in data/dataset_prospect.tsv. No new acquisition.

docs/253 found the residual returns to zero over a minute, which is why long
averaging beat the white-noise promise -- and is exactly why a per-session
baseline may absorb an offset lasting the whole session. That test injected
over the whole window and so had no pre-event reference. This one does.

Fixed in docs/254 before running:

    injection   a step starting at 10 / 25 / 50 / 75 percent of the log and
                running to its end
    detector    scan every split point, take max |mean(after) - mean(before)|
                over that log's floor. The split point is NOT given, because
                the recorder does not know when the event began
    false alarm 1 per hour, calibrated on the same scanned statistic in
                un-injected logs, so the scan's inflation is priced in
    cohort      the logs holding 600 usable samples, as in docs/252

Criteria: S1 a step at midpoint detected at 1.5 floors or less; S2 how the
figure moves with onset position; S3 what the scan costs against a known
split point.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from intermittent_injection import read_log, CACHE, ROBUST

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "step_detector.tsv"

ONSETS = [0.10, 0.25, 0.50, 0.75]
FA_PER_HOUR, HOUR_SAMPLES = 1.0, 36000
COHORT_MIN = 600
MARGIN = 50            # a split must leave >= 5 s on both sides
AMPS = np.arange(0.5, 40.5, 0.5)
TARGET = 0.90


def scan_stat(e: np.ndarray, g: float) -> float:
    """max |mean(after) - mean(before)| / g over all split points, via prefix sums."""
    n = len(e)
    c = np.concatenate(([0.0], np.cumsum(e)))
    k = np.arange(MARGIN, n - MARGIN + 1)
    before = c[k] / k
    after = (c[n] - c[k]) / (n - k)
    return float(np.max(np.abs(after - before)) / g)


def known_stat(e: np.ndarray, g: float, k: int) -> float:
    return float(abs(e[k:].mean() - e[:k].mean()) / g)


def main() -> None:
    residuals, floors = [], []
    for model in sorted(p.name for p in CACHE.iterdir() if p.is_dir()):
        for f in sorted((CACHE / model).glob("*.csv")):
            e = read_log(f)
            if e is None:
                continue
            g = float(ROBUST * np.median(np.abs(e - np.median(e))))
            if g > 0:
                residuals.append(e)
                floors.append(g)

    cohort = [(e[:COHORT_MIN], g) for e, g in zip(residuals, floors) if len(e) >= COHORT_MIN]
    print(f"全ログ {len(residuals)}   検出を測る集団 {len(cohort)} ログ(600点)")

    # --- thresholds on clean logs, one statistic per log ------------------
    # a whole log is one opportunity to raise an alarm, so the per-log false
    # alarm rate at 1/hour is (log length) / (samples per hour)
    clean_scan, clean_known = [], []
    for e, g in zip(residuals, floors):
        if len(e) < 2 * MARGIN + 1:
            continue
        clean_scan.append(scan_stat(e, g))
        clean_known.append(known_stat(e, g, len(e) // 2))
    clean_scan = np.array(clean_scan)
    clean_known = np.array(clean_known)

    fa_log = FA_PER_HOUR * (COHORT_MIN / HOUR_SAMPLES)     # one 60 s log per hour of driving
    t_scan = float(np.quantile(clean_scan, 1 - fa_log))
    t_known = float(np.quantile(clean_known, 1 - fa_log))
    n_scan = int((clean_scan > t_scan).sum())
    n_known = int((clean_known > t_known).sum())
    print(f"誤検出 1件/時 → ログ1本あたり {fa_log:.4f}")
    print(f"  走査型   閾値 {t_scan:>6.3f} 床   超過 {n_scan} 本 / {clean_scan.size}"
          f"{'  * 薄い' if n_scan < 10 else ''}")
    print(f"  既知分割 閾値 {t_known:>6.3f} 床   超過 {n_known} 本 / {clean_known.size}"
          f"{'  * 薄い' if n_known < 10 else ''}")

    print(f"\n{'開始位置':>8} {'基準区間':>9} {'走査型':>10} {'既知分割':>10} {'走査の損':>10}")
    print("-" * 54)
    rows = []
    for frac in ONSETS:
        k = int(COHORT_MIN * frac)
        min_scan = min_known = None
        for A in AMPS:
            hs = hk = 0
            for e, g in cohort:
                y = e.copy()
                y[k:] += A * g
                if min_scan is None and scan_stat(y, g) > t_scan:
                    hs += 1
                if min_known is None and known_stat(y, g, k) > t_known:
                    hk += 1
            n = len(cohort)
            if min_scan is None and hs / n >= TARGET:
                min_scan = A
            if min_known is None and hk / n >= TARGET:
                min_known = A
            if min_scan is not None and min_known is not None:
                break
        loss = (min_scan / min_known) if (min_scan and min_known) else float("nan")
        print(f"{frac:>7.0%} {k/10:>8.0f}s "
              f"{('%.1f' % min_scan) if min_scan else '>40':>10} "
              f"{('%.1f' % min_known) if min_known else '>40':>10} "
              f"{loss:>9.2f}倍")
        rows.append({"onset_frac": frac, "ref_s": k / 10,
                     "min_scan": min_scan, "min_known": min_known, "loss": loss})

    mid = next(r for r in rows if r["onset_frac"] == 0.50)
    print(f"\n=== S1 中央から始まる段差 ===")
    print(f"  走査型の最小検出 {mid['min_scan']} 床   "
          f"{'PASS' if mid['min_scan'] and mid['min_scan'] <= 1.5 else 'FAIL'} (基準: 1.5以下)")
    med_floor = float(np.median(floors))
    if mid["min_scan"]:
        print(f"  床の中央値 {med_floor:.4f} m/s^2 → {mid['min_scan']*med_floor:.2f} m/s^2")
    print(f"\n=== S2 開始位置の影響(記述) ===")
    print("  " + "  ".join(f"{r['onset_frac']:.0%}:{r['min_scan']}" for r in rows))
    print(f"\n=== S3 分割点を知らない代償(記述) ===")
    print("  " + "  ".join(f"{r['onset_frac']:.0%}:{r['loss']:.2f}x" for r in rows))

    with OUT_TSV.open("w") as fh:
        fh.write("onset_frac\treference_s\tthr_scan\tthr_known\tn_exceed_scan\tn_exceed_known\t"
                 "min_amp_scan\tmin_amp_known\tscan_penalty\n")
        for r in rows:
            fh.write(f"{r['onset_frac']}\t{r['ref_s']}\t{t_scan:.4f}\t{t_known:.4f}\t"
                     f"{n_scan}\t{n_known}\t{r['min_scan']}\t{r['min_known']}\t{r['loss']:.3f}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
