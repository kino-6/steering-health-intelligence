#!/usr/bin/env python3
"""Healthy-period statistics on all 42 NASA tests, not just the six that ran
to failure (docs/362).

Six devices gave the noise floor, the drift shape and the signal-to-noise S
that the recorder's claims rest on. Those three need only a healthy run,
and every one of the 42 tests has a run 1. This measures them on all 42 and
puts the six against that distribution. The degradation side stays at six;
nothing here changes that.
"""

from __future__ import annotations

import csv
import re
import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import line

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "population.tsv"
SIX = [8, 9, 10, 11, 12, 14]
MIN_SAMPLES = 400
WINDOWS = [25, 50, 100, 200, 400]


def alpha(resid: np.ndarray) -> float:
    """Growth exponent of the running mean's n-sample change (docs/348)."""
    w = 50
    m = np.convolve(resid, np.ones(w) / w, mode="valid")
    xs, ys = [], []
    for n in WINDOWS:
        if len(m) <= 2 * n:
            continue
        d = m[n:] - m[:-n]
        xs.append(np.log(n)); ys.append(np.log(np.var(d) + 1e-18))
    if len(xs) < 3:
        return float("nan")
    return float(np.polyfit(xs, ys, 1)[0])


def tests_in(z: zipfile.ZipFile) -> list[int]:
    ids = set()
    for n in z.namelist():
        m = re.search(r"Test_(\d+)", n)
        if m:
            ids.add(int(m.group(1)))
    return sorted(ids)


def main() -> None:
    z = zipfile.ZipFile(mos.ZIP)
    rows = []
    for t in tests_in(z):
        try:
            ron, tp = mos.read_run(z, t, 1)
        except Exception:
            continue
        y, op = np.asarray(ron, float), np.asarray(tp, float)
        ok = np.isfinite(y) & np.isfinite(op)
        y, op = y[ok], op[ok]
        if len(y) < MIN_SAMPLES:
            continue
        n1 = len(y)
        fit = np.arange(n1) < n1 // 2
        a, b, g = line(y[fit], op[fit])          # g = 3 sigma (robust)
        if g <= 0:
            continue
        resid = (y - (a * op + b)) / g            # in units of 3 sigma
        held = resid[~fit]
        sigma = float(1.4826 * np.median(np.abs(held - np.median(held)))) * g / 3.0 if len(held) else float("nan")
        t_ref = float(np.median(op))
        S = float((a * t_ref + b) / g)
        al = alpha(resid)
        rows.append((t, n1, a, g / 3.0, S, al, t in SIX))

    N = len(rows)
    print(f"run 1 が {MIN_SAMPLES} 点以上あるテスト: {N} / 42\n")
    S_all = np.array([r[4] for r in rows]); al_all = np.array([r[5] for r in rows])
    sg_all = np.array([r[3] for r in rows]); sl_all = np.array([r[2] for r in rows])
    six = np.array([r[6] for r in rows])
    fin = np.isfinite(al_all)

    def pct(x, v):
        return float((x < v).mean() * 100)

    print(f"{'量':<8}{'42 の中央値':>12}{'10%':>9}{'90%':>9}{'6 素子の中央値':>14}{'6 の位置(pct)':>13}")
    for name, x in (("σ", sg_all), ("S", S_all), ("α", al_all), ("傾き", sl_all)):
        m = np.isfinite(x)
        med6 = float(np.median(x[six & m]))
        print(f"{name:<8}{np.median(x[m]):>12.4f}{np.percentile(x[m],10):>9.4f}{np.percentile(x[m],90):>9.4f}"
              f"{med6:>14.4f}{pct(x[m], med6):>13.0f}")

    neg = int((sl_all < 0).sum())
    s_ratio = float(S_all.max() / S_all.min()) if S_all.min() > 0 else float("nan")
    print(f"\nS の最大/最小 = {s_ratio:.2f}（{S_all.min():.2f} 〜 {S_all.max():.2f}）")
    print(f"傾きが負のテスト: {neg} / {N}  ({', '.join(str(r[0]) for r in rows if r[2] < 0)})")

    print("\n=== 事前登録した予想 ===")
    print(f"  P1 S の最大/最小 <= 3       : {s_ratio:.2f} -> {'PASS' if s_ratio <= 3 else 'FAIL'}")
    amed = float(np.median(al_all[fin]))
    print(f"  P2 α の中央値 1.1〜1.5      : {amed:.2f} -> {'PASS' if 1.1 <= amed <= 1.5 else 'FAIL'}")
    print(f"  P3 傾き負 <= 6 個           : {neg} -> {'PASS' if neg <= 6 else 'FAIL'}")
    inside = []
    for name, x in (("σ", sg_all), ("S", S_all), ("α", al_all)):
        m = np.isfinite(x); med6 = float(np.median(x[six & m]))
        lo, hi = np.percentile(x[m], 10), np.percentile(x[m], 90)
        inside.append(lo <= med6 <= hi)
        print(f"     {name}: 6 素子の中央値 {med6:.4f} は 42 の 10〜90% [{lo:.4f}, {hi:.4f}] の {'中' if inside[-1] else '外'}")
    print(f"  P4 6 素子が 10〜90% の中   : -> {'PASS' if all(inside) else 'FAIL'}")

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["test", "run1_samples", "slope", "sigma", "S", "alpha", "in_six"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], int(r[6])])
    print(f"\n{OUT.relative_to(ROOT)} に書いた")


if __name__ == "__main__":
    main()
