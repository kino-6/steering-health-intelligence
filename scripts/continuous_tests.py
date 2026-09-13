#!/usr/bin/env python3
"""NASA's degradation model on NASA's own quantity, axis and devices (docs/369).

R_DS(on) from the transient on-state (V_DS / I_D, median over the samples
where drain current exceeds half its 95th percentile), corrected for the
operating point by a two-variable line (on-state current, package temperature)
fitted on the first ten percent of each test, on the aging-time axis, for the
twelve single-run continuous tests. Exponential with a bound by the measured
t10, against a straight line as the do-nothing baseline.
"""

from __future__ import annotations

import csv
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import scipy.io as sio

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "continuous_tests.tsv"
TESTS = [7, 26, 29, 30, 31, 32, 33, 35, 36, 37, 38, 41]
Y10, Y_FAIL = 0.10, 0.25
SMOOTH = 50
HEALTHY_FRAC = 0.10
B_GRID = np.logspace(np.log10(0.01), np.log10(50.0), 70)


def load(test):
    z = zipfile.ZipFile(mos.ZIP)
    name = [n for n in z.namelist() if re.search(rf"Test_{test}_run_1\.mat$", n)][0]
    p = mos.CACHE / name
    if not p.exists():
        z.extract(name, mos.CACHE)
    m = sio.loadmat(p, squeeze_me=True, struct_as_record=False)["measurement"]
    tr = np.ravel(m.transient); ss = np.ravel(m.steadyState)
    t_tr = np.array([float(x.timeEpoch) for x in tr]); t_ss = np.array([float(x.timeEpoch) for x in ss])
    T_ss = np.array([float(x.timeDomain.packageTemperature) for x in ss])
    R, I, T = [], [], []
    for x in tr:
        i = np.asarray(x.timeDomain.drainCurrent, float); v = np.asarray(x.timeDomain.drainSourceVoltage, float)
        if not np.isfinite(i).any():
            R.append(np.nan); I.append(np.nan); T.append(np.nan); continue
        on = i > 0.5 * np.nanpercentile(i, 95)
        if on.sum() < 20 or np.nanmedian(i[on]) <= 0.5:
            R.append(np.nan); I.append(np.nan); T.append(np.nan); continue
        R.append(float(np.nanmedian(v[on] / i[on]))); I.append(float(np.nanmedian(i[on])))
    R, I = np.array(R), np.array(I)
    # package temperature at each transient record: nearest steady-state sample
    idx = np.searchsorted(t_ss, t_tr).clip(0, len(t_ss) - 1)
    T = T_ss[idx]
    aging_h = (t_tr - t_tr.min()) * 24.0
    ok = np.isfinite(R) & np.isfinite(I) & np.isfinite(T)
    return aging_h[ok], R[ok], I[ok], T[ok]


def relative_rise(aging, R, I, T):
    n = len(R); h = max(50, int(n * HEALTHY_FRAC))
    X = np.column_stack([np.ones(h), I[:h], T[:h]])
    coef, *_ = np.linalg.lstsq(X, R[:h], rcond=None)
    line = coef[0] + coef[1] * I + coef[2] * T
    rel = R / line - 1.0
    return np.convolve(rel, np.ones(SMOOTH) / SMOOTH, mode="same"), float(np.median(R[:h]))


def fit_exp(t, m, t10):
    t0_grid = np.linspace(0.0, t10 * 0.98, 50); best = None
    for b in B_GRID:
        for t0 in t0_grid:
            a = Y10 / (np.exp(b * (t10 - t0)) - 1.0)
            yhat = np.where(t >= t0, a * (np.exp(b * np.clip(t - t0, 0, None)) - 1.0), 0.0)
            sse = float(np.sum((m - yhat) ** 2))
            if best is None or sse < best[0]:
                best = (sse, b, t0, a)
    sse, b, t0, a = best
    pinned = b <= B_GRID[0] * 1.001 or b >= B_GRID[-1] * 0.999 or t0 <= 1e-9 or t0 >= t0_grid[-1] - 1e-9
    return sse, b, t0, a, pinned


def fit_line(t, m, t10):
    best = None
    for t0 in np.linspace(0.0, t10 * 0.98, 50):
        x = np.clip(t - t0, 0, None); c = float(np.sum(x * m) / max(np.sum(x * x), 1e-12))
        sse = float(np.sum((m - c * x) ** 2))
        if best is None or sse < best[0]:
            best = (sse, c, t0)
    return best


def main() -> None:
    rows = []
    print(f"{'test':<8}{'記録':>7}{'時間':>6}{'R0 [Ω]':>8}{'t10 [h]':>8}{'b [1/h]':>9}{'t0':>6}{'指数/直線 SSE':>14}{'判定':>8}")
    for test in TESTS:
        aging, R, I, T = load(test)
        if len(R) < 200:
            print(f"Test_{test:<3} 記録不足 {len(R)}"); rows.append((test, len(R), np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, "記録不足")); continue
        m, R0 = relative_rise(aging, R, I, T)
        over = np.flatnonzero(m >= Y10)
        if not len(over):
            print(f"Test_{test:<3}{len(R):>7}{aging.max():>6.1f}{R0:>8.3f}{'—':>8}{'':>9}{'':>6}{'':>14}{'達せず':>8}")
            rows.append((test, len(R), aging.max(), R0, np.nan, np.nan, np.nan, np.nan, "達せず")); continue
        t10 = float(aging[over[0]])
        sse_e, b, t0, a, pinned = fit_exp(aging, m, t10)
        sse_l, c, t0l = fit_line(aging, m, t10)
        verdict = "同定失敗" if pinned else "同定"
        print(f"Test_{test:<3}{len(R):>7}{aging.max():>6.1f}{R0:>8.3f}{t10:>8.2f}{b:>9.3f}{t0:>6.2f}{sse_e / sse_l:>14.3f}{verdict:>8}")
        rows.append((test, len(R), aging.max(), R0, t10, b, t0, sse_e / sse_l, verdict))
    reached = [r for r in rows if r[8] in ("同定", "同定失敗")]
    ident = [r for r in rows if r[8] == "同定"]
    print(f"\n0.10 に達した: {len(reached)}/{len(TESTS)}   同定: {len(ident)}/{len(reached) if reached else 0}")
    print("\n=== 事前登録した予想 ===")
    print(f"  E1 達するのが 8 本以上          : {len(reached)} -> {'PASS' if len(reached) >= 8 else 'FAIL'}")
    if reached:
        print(f"  E2 達したうち同定が半分以上     : {len(ident)}/{len(reached)} -> {'PASS' if len(ident) * 2 >= len(reached) else 'FAIL'}")
    if ident:
        ratio = float(np.median([r[7] for r in ident])); bs = np.array([r[5] for r in ident])
        print(f"  E3 指数の SSE が直線の 80% 以下  : 中央値 {ratio:.3f} -> {'PASS' if ratio <= 0.8 else 'FAIL'}")
        print(f"  E4 b の最大/最小 <= 10          : {bs.max() / bs.min():.2f} -> {'PASS' if bs.max() / bs.min() <= 10 else 'FAIL'}")
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["test", "records", "aging_h", "R0_ohm", "t10_h", "b", "t0", "sse_exp_over_line", "verdict"])
        for r in rows: w.writerow(r)
    print(f"\n{OUT.relative_to(ROOT)} に書いた")


if __name__ == "__main__":
    main()
