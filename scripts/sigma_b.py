#!/usr/bin/env python3
"""Healthy-period diffusion sigma_B by lagged increments (docs/376).

docs/373 divided the variance of adjacent increments of a 50-sample running
mean by a time step of seconds, and sample noise inflated it to 0.555. Here
V(lag) = Var[m(t+lag) - m(t)] is measured at lags of 0.05 to 0.4 hours; for
a random walk V is linear in the lag with slope sigma_B^2, and the intercept
is what the noise contributes. The direct measure from docs/343 (max minus
min over the healthy stretch, divided by root time) sits beside it.
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
OUT = ROOT / "data" / "sigma_b.tsv"
LAGS = [0.05, 0.1, 0.2, 0.4]
W = 50


def conducting_hours(dev):
    hrs, rid = read_epoch(dev)
    dt = np.diff(hrs, prepend=hrs[0]); dt[dt < 0] = 0; dt[dt > 1 / 60] = 0
    return np.cumsum(dt)


def main() -> None:
    rows = []
    print(f"{'素子':<9}" + "".join(f"{'V(' + str(l) + ')':>10}" for l in LAGS) + f"{'σ_B ラグ法':>11}{'切片':>8}{'log-log 傾き':>13}{'σ_B 直接':>10}")
    for dev in mos.DEVICES:
        y, op, rid, _s, n1 = series(dev)
        t = conducting_hours(dev)
        if len(t) != len(y):
            continue
        fit = np.arange(len(y)) < n1 // 2
        a, b, g = line(y[fit], op[fit])
        x = (y - (a * op + b)) / g
        h = rid <= 4
        xh, th = x[h], t[h]
        m = np.convolve(xh, np.ones(W) / W, mode="valid"); tm = th[W - 1:]
        V = []
        for lag in LAGS:
            j = np.searchsorted(tm, tm + lag)
            ok = j < len(tm)
            d = m[j[ok]] - m[ok]
            V.append(float(np.var(d)) if len(d) > 50 else np.nan)
        V = np.array(V); L = np.array(LAGS)
        okv = np.isfinite(V)
        slope, icpt = np.polyfit(L[okv], V[okv], 1)
        sig_lag = float(np.sqrt(max(slope, 0.0)))
        ll = float(np.polyfit(np.log(L[okv]), np.log(V[okv]), 1)[0])
        T = float(tm.max() - tm.min())
        sig_direct = float((m.max() - m.min()) / np.sqrt(T)) if T > 0 else np.nan
        rows.append((dev, *V, sig_lag, icpt, ll, sig_direct, T))
        print(f"Test_{dev:<4}" + "".join(f"{v:>10.4f}" for v in V) + f"{sig_lag:>11.3f}{icpt:>8.4f}{ll:>13.2f}{sig_direct:>10.3f}")
    sl = np.array([r[5] for r in rows]); ll = np.array([r[7] for r in rows]); sd = np.array([r[8] for r in rows])
    print(f"\n中央値: σ_B ラグ法 {np.median(sl):.3f}、log-log 傾き {np.median(ll):.2f}、直接 {np.median(sd):.3f}（docs/373 は 0.555）")
    print("\n=== 事前登録した予想 ===")
    print(f"  B1 ラグ法 σ_B の中央値 0.15〜0.35 : {np.median(sl):.3f} -> {'PASS' if 0.15 <= np.median(sl) <= 0.35 else 'FAIL'}")
    print(f"  B2 log-log 傾き > 1               : {np.median(ll):.2f} -> {'PASS' if np.median(ll) > 1 else 'FAIL'}")
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["device"] + [f"V_{l}" for l in LAGS] + ["sigma_b_lag", "intercept", "loglog_slope", "sigma_b_direct", "healthy_h"])
        for r in rows:
            w.writerow(r)
    print(f"\n{OUT.relative_to(ROOT)} に書いた（B3・B4 は sibling_wiener.py を直した σ_B で再実行して判定）")


if __name__ == "__main__":
    main()
