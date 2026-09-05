"""Does a longer end-of-line sweep actually buy a lower alarm rate (docs/320)?

docs/282 says a threshold is a quantile of k samples and cannot express a rate
finer than 1/k, which makes the fix arithmetic: sweep longer. docs/299 says a
lower threshold lets the healthy drift through, and a longer sweep spans more
drift. The two pull opposite ways, so this measures what actually fires on a
held-out healthy run as k grows -- not the quantile's nominal rate.

Only k changes. The statistic, the window bank and the intervals are docs/316's
unaltered.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line
from changepoint import slopes, WINDOWS, HOUR, ROBUST

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "enrolment_length.tsv"
KS = [500, 1000, 2000, 5000, 10000, 20000, None]   # None = the whole interval


def evaluate(dev, k):
    """Calibrate on the first k of the calibration interval; measure run 4."""
    y, op, rid, stress, n1 = series(dev)
    fp = np.arange(len(y)) < n1 // 2
    cal = np.zeros(len(y), bool); cal[n1 // 2:] = True; cal &= (rid <= 3)
    idx_cal = np.where(cal)[0]
    used = len(idx_cal) if k is None else min(k, len(idx_cal))
    keep = np.zeros(len(y), bool); keep[idx_cal[:used]] = True
    a, b, g = line(y[fp], op[fp])
    if g <= 0:
        return None
    resid = (y - (a * op + b)) / g
    design = 1.0 / HOUR / len(WINDOWS)
    fa_hits = fa_n = 0
    fired = False
    for w in WINDOWS:
        sl, ix = slopes(resid, stress, w)
        if sl is None:
            continue
        rid_w, keep_w = rid[ix], keep[ix]
        c = sl[keep_w & np.isfinite(sl)]
        if len(c) < 20:
            continue
        a_cal = float(np.median(c))
        s_cal = float(ROBUST * np.median(np.abs(c - a_cal)))
        if s_cal <= 0:
            continue
        stat = np.abs(sl - a_cal) / s_cal
        cs = stat[keep_w & np.isfinite(stat)]
        q = min(1 - design, 1 - 1.0 / len(cs))
        thr = float(np.quantile(cs, q))
        r4 = (rid_w == 4) & np.isfinite(stat)
        fa_hits += int((stat[r4] > thr).sum()); fa_n = max(fa_n, int(r4.sum()))
        if ((rid_w >= 5) & np.isfinite(stat) & (stat > thr)).any():
            fired = True
    if not fa_n:
        return None
    return used, fa_hits / fa_n * HOUR, fired


def main() -> None:
    print(f"{'k':>8} {'使えた標本':>10} {'実測 誤報(件/時)':>18} "
          f"{'1/k の予測':>12} {'予測比':>8} {'run5-7 で発火':>13}")
    print("-" * 76)
    rows, base = [], None
    for k in KS:
        got = [evaluate(d, k) for d in mos.DEVICES]
        got = [x for x in got if x]
        if not got:
            continue
        used = int(np.median([x[0] for x in got]))
        fa = float(np.mean([x[1] for x in got]))
        fired = sum(x[2] for x in got)
        if base is None:
            base = (used, fa)
        pred = base[1] * base[0] / used
        label = "全部" if k is None else str(k)
        print(f"{label:>8} {used:>10,} {fa:>18.1f} {pred:>12.1f} "
              f"{fa/pred:>8.2f}x {f'{fired}/6':>13}")
        rows.append((label, used, fa, pred, fa / pred, fired))

    print()
    grow = rows[-1][1] / rows[0][1]
    ratio = rows[-1][4]
    print(f"k は {grow:.0f} 倍まで伸ばせた。最大 k での実測は 1/k 予測の {ratio:.2f} 倍。")
    if ratio <= 2.0:
        v = "H1 予算律速 — 掃引を長くすれば届く。必要な長さは計算できる"
    elif ratio >= 5.0:
        v = "H2 漂流律速 — どれだけ掃引しても届かない。仕様の 1 件/時 を書き換える必要がある"
    else:
        v = f"H1 と H2 の間（{ratio:.2f} 倍）。どちらにも寄せない"
    print(f"判定: {v}")
    print(f"最大 k で run 5-7 に鳴り続けたのは {rows[-1][5]}/6 素子")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("k\tused\tfa_per_hour\tpred_per_hour\tratio\tfired_of_6\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
