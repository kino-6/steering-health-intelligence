#!/usr/bin/env python3
"""NASA's exponential degradation model, fitted in an identifiable form
(docs/367), and the population grown from it.

docs/366 fitted a*(exp(b(t-t0))-1) to seven run-level points and got a
pinned at its bound on five devices. Here the fit uses every sample, and a is
tied to the measured time t10 at which dR/R0 first crosses 0.10, so only b
and t0 are free. A device whose b or t0 lands on a grid edge is an
identification failure and is not used. Fewer than four identified devices
stops the population step.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line
from lifetime_simulation import read_epoch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "calibrated_population_v2.tsv"
POP = ROOT / "data" / "population.tsv"

Y10, Y_FAIL = 0.10, 0.25            # dR/R0 at the anchor and at failure (C = 0.894)
SMOOTH = 50
B_GRID = np.logspace(np.log10(0.001), np.log10(5.0), 60)
WIN_PER_H, ENROL, TARGET = 720, 720, 2.7
NOISE_W = (1.0 / 3.0) / np.sqrt(50)
DRIFT = 0.351
N_UNITS, MAX_H, SEED = 1000, 200.0, 367


def conducting_hours(dev):
    hrs, rid = read_epoch(dev)
    dt = np.diff(hrs, prepend=hrs[0]); dt[dt < 0] = 0; dt[dt > 1 / 60] = 0
    return np.cumsum(dt), rid


def model(b, t0, t10, t):
    a = Y10 / (np.exp(b * (t10 - t0)) - 1.0)
    return a, np.where(t >= t0, a * (np.exp(b * np.clip(t - t0, 0, None)) - 1.0), 0.0)


def fit_device(dev):
    y, op, rid, _s, n1 = series(dev)
    t, rid2 = conducting_hours(dev)
    if len(t) != len(y):
        return dict(dev=dev, ok=False, why=f"時刻 {len(t)} 点と観測 {len(y)} 点が合わない")
    fit = np.arange(len(y)) < n1 // 2
    aT, bT, g = line(y[fit], op[fit])
    t_ref = float(np.median(op[fit]))
    S = (aT * t_ref + bT) / g
    rel = ((y - (aT * op + bT)) / g) / S          # dR/R0 per sample
    m = np.convolve(rel, np.ones(SMOOTH) / SMOOTH, mode="same")
    over = np.flatnonzero(m >= Y10)
    if not len(over):
        return dict(dev=dev, ok=False, why="ΔR/R0 が 0.10 に達しない")
    t10 = float(t[over[0]])
    t0_grid = np.linspace(0.0, t10 * 0.98, 50)
    best = None
    for b in B_GRID:
        for t0 in t0_grid:
            a, yhat = model(b, t0, t10, t)
            sse = float(np.sum((m - yhat) ** 2))
            if best is None or sse < best[0]:
                best = (sse, b, t0, a)
    sse, b, t0, a = best
    pinned = (b <= B_GRID[0] * 1.001 or b >= B_GRID[-1] * 0.999
              or t0 <= t0_grid[0] + 1e-9 or t0 >= t0_grid[-1] - 1e-9)
    healthy_h = float(t[rid <= 4].max()) if (rid <= 4).any() else float("nan")
    t_fail = t0 + np.log(Y_FAIL / a + 1.0) / b
    return dict(dev=dev, ok=not pinned, why="境界に張り付いた" if pinned else "", b=b, t0=t0, t10=t10,
                a=a, t_fail=t_fail, sse=sse, healthy_h=healthy_h, S=S, n=len(y))


def main() -> None:
    fits = [fit_device(d) for d in mos.DEVICES]
    print("標本ごとの当てはめ。a は t10 で縛り、自由なのは b と t0\n")
    print(f"{'素子':<9}{'同定':>5}{'b [1/h]':>9}{'t0 [h]':>8}{'t10 [h]':>8}{'a':>9}{'t_fail [h]':>11}{'健全期 [h]':>10}  理由")
    for f in fits:
        if "b" in f:
            print(f"Test_{f['dev']:<4}{'○' if f['ok'] else '×':>5}{f['b']:>9.4f}{f['t0']:>8.2f}{f['t10']:>8.2f}"
                  f"{f['a']:>9.4f}{f['t_fail']:>11.1f}{f['healthy_h']:>10.1f}  {f['why']}")
        else:
            print(f"Test_{f['dev']:<4}{'×':>5}  {f['why']}")
    ok = [f for f in fits if f["ok"]]
    print(f"\n同定できた素子: {len(ok)} / 6")
    with OUT.open("w", encoding="utf-8", newline="") as fo:
        w = csv.writer(fo, delimiter="\t")
        w.writerow(["kind", "id", "ok", "b", "t0", "t10", "a", "t_fail", "healthy_h", "S", "why"])
        for f in fits:
            w.writerow(["fit", f["dev"], int(f["ok"]), f.get("b"), f.get("t0"), f.get("t10"), f.get("a"),
                        f.get("t_fail"), f.get("healthy_h"), f.get("S"), f["why"]])

    print("\n=== 事前登録した予想 ===")
    v1 = len(ok) >= 5
    print(f"  V1 同定できる素子 >= 5/6        : {len(ok)} -> {'PASS' if v1 else 'FAIL'}")
    if len(ok) >= 2:
        bs = np.array([f["b"] for f in ok]); v2 = bs.max() / bs.min()
        print(f"  V2 b の最大/最小 <= 10          : {v2:.2f} -> {'PASS' if v2 <= 10 else 'FAIL'}")
    if len(ok) < 4:
        print("  同定できた素子が 4 未満なので、事前登録どおり個体群の段は走らせない。V3・V4 は判定しない")
        return

    # ---- population from the identified devices
    rng = np.random.default_rng(SEED)
    pop = []
    with POP.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            pop.append((float(r["sigma"]), float(r["S"])))
    lb = np.log([f["b"] for f in ok]); lg = np.log([f["t10"] - f["t0"] for f in ok])
    healthy_h = float(np.median([f["healthy_h"] for f in ok]))
    q = min(TARGET / WIN_PER_H, 1.0 - 1.0 / ENROL)
    det, fa, rows = [], [], []
    for i in range(N_UNITS):
        sigma, S = pop[rng.integers(len(pop))]
        degrading = i % 2 == 1
        b = float(np.exp(rng.normal(lb.mean(), lb.std(ddof=1))))
        gap = float(np.exp(rng.normal(lg.mean(), lg.std(ddof=1))))     # t10 - t0
        a = Y10 / (np.exp(b * gap) - 1.0)
        if degrading:
            t0 = float(rng.uniform(0.5, healthy_h))
            t_fail = t0 + np.log(Y_FAIL / a + 1.0) / b
            run_h = min(t_fail + 1.0, MAX_H)
        else:
            t0, t_fail, run_h = float("nan"), float("nan"), healthy_h
        n_run = int(run_h * WIN_PER_H); n = ENROL + n_run
        step = DRIFT / np.sqrt(healthy_h * WIN_PER_H)
        w = np.cumsum(rng.normal(0, step, n)) + rng.normal(0, NOISE_W, n)
        t_h = (np.arange(n) - ENROL) / WIN_PER_H
        if degrading:
            w = w + S * np.where(t_h >= t0, a * (np.exp(b * np.clip(t_h - t0, 0, None)) - 1.0), 0.0)
        thr = float(np.quantile(np.abs(w[:ENROL]), 1 - q))
        fired = np.abs(w[ENROL:]) > thr
        if degrading:
            idx = np.flatnonzero(fired)
            t_alarm = idx[0] / WIN_PER_H if len(idx) else float("inf")
            det.append(t_alarm < t_fail <= MAX_H)
        else:
            fa.append(fired.sum() / run_h)
    det, fa = np.array(det), np.array(fa)
    print(f"\n仮想個体 {N_UNITS}、健全期 {healthy_h:.1f} 時間、線 {TARGET} 件/時、故障 C = 0.894")
    print(f"  故障前に警報      : {det.mean():.1%}")
    print(f"  健全の誤検知 中央値 : {np.median(fa):.2f} 件/時（10% {np.percentile(fa,10):.2f}、90% {np.percentile(fa,90):.2f}）")
    print(f"  V3 故障前に警報 >= 90%          : {det.mean():.1%} -> {'PASS' if det.mean() >= 0.9 else 'FAIL'}")
    print(f"  V4 健全の誤検知 中央値 <= 5.4/h   : {np.median(fa):.2f} -> {'PASS' if np.median(fa) <= 2 * TARGET else 'FAIL'}")
    with OUT.open("a", encoding="utf-8", newline="") as fo:
        w = csv.writer(fo, delimiter="\t")
        w.writerow(["summary", "detect_before_fail", det.mean(), "fa_median", np.median(fa), "healthy_h", healthy_h, "", "", "", ""])
    print(f"\n{OUT.relative_to(ROOT)} に書いた")


if __name__ == "__main__":
    main()
