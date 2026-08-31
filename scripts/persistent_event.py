#!/usr/bin/env python3
"""How small an event is detectable once it persists? (docs/252 -> docs/253)

Executes the protocol pre-registered in docs/252 against commaSteeringControl,
already inventoried in data/dataset_prospect.tsv. No new acquisition.

docs/244 and docs/248 measured detection in a 5 s window because docs/225 had
fixed that window. docs/251 then found that what the field reports is not a
sub-second blip but a state that arrives minutes into a drive and holds until
an ignition cycle. A window shorter than the event throws samples away.

Fixed in docs/252 before running:

    durations   2, 5, 10, 20, 40, 60 s -- the log is 60 s, so nothing longer
                is measured and nothing is extrapolated past it
    window      matched to the event; the 5 s window is reported alongside
    detectors   window mean and window maximum, as in docs/244
    false alarm 1 per hour, the usable rate of docs/248, held fixed across
                window lengths by converting to a per-window rate
    cohort      detection on the 682 logs that hold 600 usable samples, so the
                duration trend is within the same logs; thresholds calibrated
                on all 3,471

Criteria: P1 the 60 s event needs at most half the amplitude of the 2 s event;
P2 what fraction of the 1/sqrt(N) promise is actually collected; P3 whether
the 60 s figure falls below the 20 floors of docs/248.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from intermittent_injection import read_log, CACHE, ROBUST  # same residual and floor

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "persistent_event.tsv"

DURS = [20, 50, 100, 200, 400, 600]      # samples at 10 Hz: 2 .. 60 s
FA_PER_HOUR = 1.0                        # docs/248
HOUR_SAMPLES = 36000                     # 10 Hz
COHORT_MIN = 600                         # docs/252 addendum
AMPS = np.arange(0.5, 40.5, 0.5)         # floors, 0.5 steps
DETECT_TARGET = 0.90


def nonoverlap(e, w):
    k = len(e) // w
    return e[:k * w].reshape(k, w) if k else None


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

    cohort = [(e, g) for e, g in zip(residuals, floors) if len(e) >= COHORT_MIN]
    print(f"全ログ {len(residuals)}  床の中央値 {np.median(floors):.4f} m/s^2")
    print(f"検出を測る集団(600点以上): {len(cohort)} ログ\n")

    rows = []
    print(f"{'長さ':>6} {'窓':>6} {'閾値(平均)':>11} {'超過数':>7} "
          f"{'閾値(最大)':>11} {'超過数':>7} {'最小検出(平均)':>15} {'最小検出(最大)':>15}")
    print("-" * 92)

    for W in DURS:
        fa = FA_PER_HOUR * W / HOUR_SAMPLES          # per-window rate at 1/hour
        cm, cx = [], []
        for e, g in zip(residuals, floors):
            w = nonoverlap(e, W)
            if w is None:
                continue
            cm.append(np.abs(w.mean(axis=1)) / g)
            cx.append(np.abs(w).max(axis=1) / g)
        cm, cx = np.concatenate(cm), np.concatenate(cx)
        t_m = float(np.quantile(cm, 1 - fa))
        t_x = float(np.quantile(cx, 1 - fa))
        n_m, n_x = int((cm > t_m).sum()), int((cx > t_x).sum())

        # detection: the event fills the whole window, so the window it occupies
        # is the first W samples of the cohort log
        min_m = min_x = None
        for A in AMPS:
            hm = hx = 0
            for e, g in cohort:
                seg = e[:W] + A * g                   # rectangular, sign fixed +
                if abs(seg.mean()) / g > t_m:
                    hm += 1
                if np.abs(seg).max() / g > t_x:
                    hx += 1
            n = len(cohort)
            if min_m is None and hm / n >= DETECT_TARGET:
                min_m = A
            if min_x is None and hx / n >= DETECT_TARGET:
                min_x = A
            if min_m is not None and min_x is not None:
                break

        thin_m = "*" if n_m < 10 else " "
        thin_x = "*" if n_x < 10 else " "
        print(f"{W/10:>5.0f}s {W/10:>5.0f}s {t_m:>11.3f} {n_m:>6}{thin_m} "
              f"{t_x:>11.3f} {n_x:>6}{thin_x} "
              f"{('%.1f' % min_m) if min_m else '>40':>15} "
              f"{('%.1f' % min_x) if min_x else '>40':>15}")
        rows.append({"dur_s": W / 10, "win_s": W / 10, "t_mean": t_m, "n_exc_mean": n_m,
                     "t_max": t_x, "n_exc_max": n_x, "min_mean": min_m, "min_max": min_x})

    print("  * = 閾値を超えた窓が10未満。分位点の推定として薄い")

    # ---- the 5 s window, for comparison with docs/244 --------------------
    W5 = 50
    fa5 = FA_PER_HOUR * W5 / HOUR_SAMPLES
    cm5, cx5 = [], []
    for e, g in zip(residuals, floors):
        w = nonoverlap(e, W5)
        if w is None:
            continue
        cm5.append(np.abs(w.mean(axis=1)) / g)
        cx5.append(np.abs(w).max(axis=1) / g)
    cm5, cx5 = np.concatenate(cm5), np.concatenate(cx5)
    t_m5, t_x5 = float(np.quantile(cm5, 1 - fa5)), float(np.quantile(cx5, 1 - fa5))
    print(f"\n5秒窓に固定した場合(docs/244と同じ窓、誤検出1件/時):")
    print(f"  閾値 平均 {t_m5:.3f}  最大 {t_x5:.3f}  (床の倍数)")
    for W in DURS:
        min_m5 = None
        for A in AMPS:
            hm = 0
            for e, g in cohort:
                seg = e[:W5].copy()
                seg[:min(W, W5)] += A * g          # event covers part or all of the window
                if abs(seg.mean()) / g > t_m5:
                    hm += 1
            if hm / len(cohort) >= DETECT_TARGET:
                min_m5 = A
                break
        print(f"    事象 {W/10:>4.0f}s → 5秒窓の平均型で最小検出 "
              f"{('%.1f' % min_m5) if min_m5 else '>40'} 床")
        for r in rows:
            if r["dur_s"] == W / 10:
                r["min_mean_5s"] = min_m5

    # ---- P1..P3 -----------------------------------------------------------
    m2 = next(r for r in rows if r["dur_s"] == 2.0)
    m60 = next(r for r in rows if r["dur_s"] == 60.0)
    best2 = min(v for v in (m2["min_mean"], m2["min_max"]) if v)
    best60 = min(v for v in (m60["min_mean"], m60["min_max"]) if v)
    print(f"\n=== P1 持続は感度を買うか ===")
    print(f"  2秒 {best2:.1f} 床 → 60秒 {best60:.1f} 床   比 {best2/best60:.2f}倍  "
          f"{'PASS' if best60 <= best2 / 2 else 'FAIL'} (基準: 半分以下)")
    print(f"\n=== P2 1/sqrt(N) にどこまで届いたか ===")
    print(f"  標本 30倍 → 白色雑音の約束 {np.sqrt(30):.2f}倍")
    print(f"  実際に取れた                {best2/best60:.2f}倍   "
          f"不足 {np.sqrt(30)/(best2/best60):.2f}倍")
    print(f"\n=== P3 床の20倍(docs/248)を下回るか ===")
    print(f"  60秒の最小検出 {best60:.1f} 床  "
          f"{'PASS' if best60 < 20 else 'FAIL'} (基準: 20未満)")
    print(f"  床の中央値 {np.median(floors):.4f} m/s^2 → {best60*np.median(floors):.2f} m/s^2")

    with OUT_TSV.open("w") as fh:
        fh.write("dur_s\twin_s\tthr_mean\tn_exceed_mean\tthr_max\tn_exceed_max\t"
                 "min_amp_mean\tmin_amp_max\tmin_amp_mean_5s_window\n")
        for r in rows:
            fh.write(f"{r['dur_s']}\t{r['win_s']}\t{r['t_mean']:.4f}\t{r['n_exc_mean']}\t"
                     f"{r['t_max']:.4f}\t{r['n_exc_max']}\t{r['min_mean']}\t{r['min_max']}\t"
                     f"{r.get('min_mean_5s')}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
