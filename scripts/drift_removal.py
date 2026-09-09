"""Can the healthy drift be removed without a sibling channel (docs/345)?

docs/344 left one thing standing: detection fails because the healthy drift
crosses the same threshold, not because the degradation is hard to see. A
sibling channel removes the drift; a channel without one has nothing.

Stated plainly this is separating a random walk from a linear ramp in a single
series. Three methods, fixed in docs/345 before running, and the degradation
rate pinned at the 9.6 the real devices measured.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from virtual_module import (measured_constants, make_units, ENROL, N_SAMP,
                            FAST, HOUR, SEED)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "drift_removal.tsv"
RATE = 9.6                 # the real devices' measured ratio, docs/344
REBASE = [60, 180, 360]    # windows, docs/345
SHORT, LONG = 60, 360


def windows(x):
    n = len(x) // FAST
    return x[: n * FAST].reshape(n, FAST).mean(axis=1)


def m1_level(cal, run):
    """Level threshold. The baseline."""
    return np.abs(cal), np.abs(run)


def m2_rebase(cal, run, k):
    """Subtract a baseline re-fitted on the previous k windows."""
    def f(w):
        out = np.empty(len(w))
        for i in range(len(w)):
            lo = max(0, i - k)
            out[i] = w[i] - (w[lo:i].mean() if i > lo else w[i])
        return np.abs(out)
    return f(cal), f(run)


def m3_two_scale(cal, run):
    """Short-window mean minus long-window mean."""
    def f(w):
        s = np.convolve(w, np.ones(SHORT) / SHORT, mode="same")
        l = np.convolve(w, np.ones(LONG) / LONG, mode="same")
        return np.abs(s - l)
    return f(cal), f(run)


def score(stat_cal, stat_run, degrading, target=1.0):
    n = len(stat_cal)
    hit = np.zeros(n, bool)
    fa = np.zeros(n)
    for i in range(n):
        k = len(stat_cal[i])
        q = max(target / (HOUR / FAST), 1.0 / k)
        thr = float(np.quantile(stat_cal[i], 1 - q))
        fired = stat_run[i] > thr
        hit[i] = bool(fired.any())
        fa[i] = fired.sum() / (len(stat_run[i]) * FAST / HOUR)
    return float(hit[degrading].mean()), float(np.median(fa[~degrading]))


def main() -> None:
    a, g, drift = measured_constants()
    rng = np.random.default_rng(SEED)
    d, base, degrading, onset = make_units(rng, drift, RATE)
    cal_w = [windows(d[i, :ENROL]) for i in range(d.shape[0])]
    run_w = [windows(d[i, ENROL:]) for i in range(d.shape[0])]

    # T41's check, before any threshold: does M3's statistic actually move
    # during degradation?
    i = int(np.where(degrading)[0][0])
    c, r = m3_two_scale(cal_w[i], run_w[i])
    o = (onset[i] - ENROL) // FAST
    print(f"T41 の検査: M3 の統計量は劣化区間で動いているか")
    print(f"  劣化前 中央値 {np.median(r[:o]):.4f} / 劣化後 {np.median(r[o:]):.4f} "
          f"→ 比 {np.median(r[o:])/max(np.median(r[:o]),1e-12):.2f} 倍\n")

    print(f"劣化速度は実素子の実測 D = {RATE}（漂流の何倍か）に固定\n")
    print(f"{'手立て':>22} {'検出率':>9} {'健全群の誤検知':>15} {'W1':>6}")
    print("-" * 58)
    rows = []
    trials = [("M1 水準の閾値（基準）", lambda i: m1_level(cal_w[i], run_w[i]))]
    for k in REBASE:
        trials.append((f"M2 採り直し K={k}", lambda i, k=k: m2_rebase(cal_w[i], run_w[i], k)))
    trials.append((f"M3 2 尺度の差 {SHORT}/{LONG}", lambda i: m3_two_scale(cal_w[i], run_w[i])))

    for name, fn in trials:
        sc, sr = zip(*[fn(i) for i in range(d.shape[0])])
        det, fa = score(list(sc), list(sr), degrading)
        ok = det >= 0.90 and fa <= 1.0
        print(f"{name:>22} {det:>8.1%} {fa:>13.1f}/h {'満たす' if ok else '':>6}")
        rows.append((name, det, fa, int(ok)))

    print()
    passing = [r for r in rows if r[3]]
    if passing:
        print(f"  W1 満たす手立て: {passing[0][0]}")
    else:
        best = min(rows, key=lambda r: r[2])
        print(f"  W1 満たす手立ては無い。**1 本の系列では漂流と劣化を分けられない**")
        print(f"  W2 誤検知が最小: {best[0]} で {best[2]:.1f} 件/時"
              f"（基準 M1 は {rows[0][2]:.1f} 件/時）")
    worse = [r for r in rows[1:] if r[2] > rows[0][2]]
    print(f"  W3 基準より悪化した手立て: "
          f"{', '.join(r[0] for r in worse) if worse else 'なし'}")

    # Not pre-registered. Re-baselining subtracts a recent mean, so it must
    # also subtract a slow enough degradation. This is where that starts, and
    # it is the method's main risk rather than a search for a better number.
    print(f"\n事前登録していない事後の測定: 採り直しは遅い劣化も消すか")
    print(f"{'劣化速度 D':>12} {'M1 検出':>9} {'M2 検出':>9} {'M2 誤検知':>11}")
    for rate in (0.5, 1, 2, 4, 9.6):
        rng2 = np.random.default_rng(SEED + 1)
        dd, _b, deg, _o = make_units(rng2, drift, rate)
        cw = [windows(dd[i, :ENROL]) for i in range(dd.shape[0])]
        rw = [windows(dd[i, ENROL:]) for i in range(dd.shape[0])]
        s1 = [m1_level(cw[i], rw[i]) for i in range(dd.shape[0])]
        d1, _f1 = score([x[0] for x in s1], [x[1] for x in s1], deg)
        s2 = [m2_rebase(cw[i], rw[i], 60) for i in range(dd.shape[0])]
        d2, f2 = score([x[0] for x in s2], [x[1] for x in s2], deg)
        print(f"{rate:>12g} {d1:>8.1%} {d2:>8.1%} {f2:>9.1f}/h")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("method\tdetection\tfalse_per_hour\tmeets_w1\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
