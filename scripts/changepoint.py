#!/usr/bin/env python3
"""Separate drift from onset by slope change, not level (docs/316 -> docs/317).

docs/315 found the three devices that fail every treatment have a healthy drift
and a real onset of the same size, so no threshold on level can tell them
apart. They differ in shape: the drift holds one slope across four runs, the
onset is an acceleration inside one. This reads the slope instead.

The fingerprint, the residual and the stress axis are exactly docs/315's
boundary arm; only the statistic changes.

Criteria: G1 quiet on run 4 and firing later, five of six; G2 how many of
Test_9, 11 and 12 are rescued -- two is the bar that says shape works where
size does not; G3 where the first fire lands against the level threshold.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "changepoint.tsv"
WINDOWS = [2000, 5000, 10000]
HOUR = 36000
ROBUST = 1.4826
HARD = {9, 11, 12}          # docs/315: fail every treatment


def slopes(resid, stress, w):
    """Rolling slope of residual against accumulated stress, window w."""
    n = len(resid)
    if n < w:
        return None, None
    cs = np.concatenate(([0.0], np.cumsum(stress)))
    cy = np.concatenate(([0.0], np.cumsum(resid)))
    cxy = np.concatenate(([0.0], np.cumsum(stress * resid)))
    cxx = np.concatenate(([0.0], np.cumsum(stress * stress)))
    sx = cs[w:] - cs[:-w]; sy = cy[w:] - cy[:-w]
    sxy = cxy[w:] - cxy[:-w]; sxx = cxx[w:] - cxx[:-w]
    den = w * sxx - sx * sx
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.where(np.abs(den) > 0, (w * sxy - sx * sy) / den, np.nan)
    return a, np.arange(w - 1, n)


def main() -> None:
    design = 1.0 / HOUR / len(WINDOWS)
    rows, g1, rescued = [], 0, 0
    print(f"{'素子':>8} {'run4 誤報(件/時)':>16} {'初発火 run':>10} "
          f"{'鳴った窓':>18} {'達成率(OR)':>12} {'水準では':>9}")
    print("-" * 84)
    for dev in mos.DEVICES:
        y, op, rid, stress, n1 = series(dev)
        fp = np.arange(len(y)) < n1 // 2
        cal = np.zeros(len(y), bool); cal[n1 // 2:] = True; cal &= (rid <= 3)
        a, b, g = line(y[fp], op[fp])
        if g <= 0:
            print(f"{dev:>8}  評価不能"); continue
        resid = (y - (a * op + b)) / g
        fa_hits = fa_n = 0; fire = None; ach = 0.0; hit_w = []
        for w in WINDOWS:
            sl, idx = slopes(resid, stress, w)
            if sl is None:
                continue
            rid_w, cal_w = rid[idx], cal[idx]
            c = sl[cal_w & np.isfinite(sl)]
            if len(c) < 20:
                continue
            a_cal = float(np.median(c))
            s_cal = float(ROBUST * np.median(np.abs(c - a_cal)))
            if s_cal <= 0:
                continue
            stat = np.abs(sl - a_cal) / s_cal
            cs = stat[cal_w & np.isfinite(stat)]
            q = min(1 - design, 1 - 1.0 / len(cs))
            thr = float(np.quantile(cs, q)); ach += (1 - q) * HOUR
            r4 = (rid_w == 4) & np.isfinite(stat)
            fa_hits += int((stat[r4] > thr).sum()); fa_n = max(fa_n, int(r4.sum()))
            s = np.where((rid_w >= 5) & np.isfinite(stat) & (stat > thr))[0]
            if s.size:
                hit_w.append(w)
                r = int(rid_w[s[0]])
                if fire is None or r < fire:
                    fire = r
        fa = (fa_hits / fa_n * HOUR) if fa_n else float("nan")
        ok = np.isfinite(fa) and fa <= 3.0 and fire is not None
        g1 += ok
        if ok and dev in HARD:
            rescued += 1
        lvl = "落ちる" if dev in HARD else "通る"
        print(f"{dev:>8} {fa:>16.1f} {str(fire):>10} {str(hit_w):>18} "
              f"{ach:>9.1f}/h {lvl:>9}{'' if ok else '   NG'}")
        rows.append((dev, fa, fire, ach, int(ok), int(dev in HARD)))

    print(f"\n=== G1 誤報 3 倍以内 かつ発火 ===\n  {g1}/6  {'PASS' if g1 >= 5 else 'FAIL'} (基準 6中5)")
    print(f"=== G2 水準では落ちる 3 素子(9・11・12)を救えたか ===\n  "
          f"{rescued}/3  {'PASS 形で分けられる' if rescued >= 2 else 'FAIL この観測量では分けられない'}")
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("device\tfa_run4_per_hour\tfire_run\tachieved_or_per_hour\tpassed\thard_case\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
