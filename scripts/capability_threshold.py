#!/usr/bin/env python3
"""Can the threshold be stated as "tell me at 5 percent lost"? (docs/353)

The threshold sits on deviation -- how many of this unit's own noise floors it
is from its shipping line -- and not on capability, so converting it gives a
different capability for every unit: 0.887 to 0.980, a spread of 0.09.

A receiver would rather say "five percent lost". That translation is algebra
and the shipping baseline already carries every term:

    R_on(d) = R0 + d*g          R0 = slope*T + intercept,  g = floor
    C(d)    = sqrt( R0 / (R0 + d*g) )
    d(C)    = S * (1/C^2 - 1)   S = R0 / g

S is the unit's own signal to noise. What the translation costs is the
question: a common capability threshold gives every unit a different deviation
threshold, and therefore a different false alarm rate.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "capability_threshold.tsv"
REF = ROOT / "data" / "assist_capability.tsv"

FAST = 50                 # 5 second window at 10 Hz, as everywhere else
C_TARGET = 0.95           # chosen, not derived: docs/353, TROUBLES T35
HEALTHY_RUNS = 4


def t_refs() -> dict[str, float]:
    with REF.open(encoding="utf-8") as f:
        return {int(r["device"]): float(r["t_ref"])
                for r in csv.DictReader(f, delimiter="\t")}


def d_of_c(S: float, c: float) -> float:
    """Deviation, in floors, at which capability has fallen to c."""
    return S * (1.0 / (c * c) - 1.0)


def unit(dev: int, t_ref: float):
    """Residual in floors, the healthy stretch, and this unit's S."""
    y, op, rid, _stress, n1 = series(dev)
    fit = np.arange(len(y)) < n1 // 2
    a, b, g = line(y[fit], op[fit])
    if g <= 0:
        return None
    resid = (y - (a * op + b)) / g
    R0 = a * t_ref + b
    healthy = (rid <= HEALTHY_RUNS) & ~fit          # held out from the fit
    late = rid > HEALTHY_RUNS
    return resid, healthy, late, R0 / g


def windows(x: np.ndarray) -> np.ndarray:
    m = len(x) // FAST
    if m == 0:
        return np.empty(0)
    return np.abs(x[: m * FAST].reshape(m, FAST).mean(axis=1))


def main() -> None:
    tr = t_refs()
    rows = []
    print(f"能力の閾値 C = {C_TARGET} を全個体に課す。追加取得ゼロ\n")
    print(f"{'素子':<9}{'S':>9}{'d(C)':>9}{'健全窓':>8}{'誤検知':>8}"
          f"{'件/時':>9}{'検出':>6}")
    for dev in mos.DEVICES:
        u = unit(dev, tr[dev])
        if u is None:
            continue
        resid, healthy, late, S = u
        d_thr = d_of_c(S, C_TARGET)
        wh = windows(resid[healthy])
        wl = windows(resid[late])
        n_fa = int((wh > d_thr).sum())
        hours = len(wh) * FAST / 36000.0            # 10 Hz
        rate = n_fa / hours if hours > 0 else float("nan")
        hit = bool((wl > d_thr).any())
        rows.append((f"Test_{dev}", S, d_thr, len(wh), n_fa, rate, hit, hours))
        print(f"{'Test_' + str(dev):<9}{S:>9.1f}{d_thr:>9.2f}{len(wh):>8}{n_fa:>8}"
              f"{rate:>9.1f}{'  6/6' if hit else '   no':>6}")

    # the other direction: hold the false alarm rate, read out the capability
    print(f"\n{'素子':<9}{'現行の d':>10}{'能力に直すと':>13}{'発火した run':>13}")
    cur = []
    for dev in mos.DEVICES:
        u = unit(dev, tr[dev])
        if u is None:
            continue
        resid, healthy, late, S = u
        wh = windows(resid[healthy])
        hours = len(wh) * FAST / 36000.0
        q = min(1.0 / (len(wh) / hours), 1.0) if hours > 0 else 1.0
        d_cur = float(np.quantile(wh, 1 - q))
        c_cur = float(np.sqrt(S / (S + d_cur)))
        cur.append((dev, d_cur, c_cur))
        print(f"{'Test_' + str(dev):<9}{d_cur:>10.2f}{c_cur:>13.4f}")

    S_all = [r[1] for r in rows]
    rate_all = [r[5] for r in rows if r[5] == r[5]]
    pos = [r for r in rate_all if r > 0]
    det = sum(1 for r in rows if r[6])
    floor_h = min(r[7] for r in rows)

    print(f"\n健全区間は最短で {floor_h:.3f} 時間。"
          f"**{1 / floor_h:.0f} 件/時 より細かい率は区別できない**")

    print("\n=== 事前登録した予想 ===")
    y1 = max(S_all) / min(S_all)
    print(f"  Y1 S の最大/最小 >= 3        : {y1:.2f} 倍 "
          f"({min(S_all):.1f} 〜 {max(S_all):.1f}) -> {'PASS' if y1 >= 3 else 'FAIL'}")
    # a ratio whose denominator can be zero is not a measurement (T41). The
    # spread is reported as the values themselves.
    n_zero = sum(1 for r in rate_all if r == 0)
    print(f"  Y2 誤検知の最大/最小 >= 10   : {n_zero}/{len(rate_all)} 個体が 0 件、"
          f"残りは {max(rate_all):.0f} 件/時。"
          f"**比の分母が 0 なので倍率は定義できない** -> FAIL")
    print(f"  Y3 検出 6/6                  : {det}/{len(rows)} "
          f"-> {'PASS' if det == len(rows) else 'FAIL'}")

    cs = [c for _d, _dc, c in cur]
    print("\n=== 何もしない基準（現行。誤検知率を揃える） ===")
    print(f"  同じ健全区間で 1 件/時 に較正すると、能力の閾値は "
          f"{min(cs):.4f} 〜 {max(cs):.4f}（幅 {max(cs) - min(cs):.4f}）")
    print(f"  逸脱の閾値は {min(d for _x, d, _c in cur):.2f} 〜 "
          f"{max(d for _x, d, _c in cur):.2f} 床")

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["device", "S", "d_at_C", "healthy_windows", "false_alarms",
                    "per_hour", "detected", "healthy_hours"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], int(r[6]), r[7]])
    print(f"\n{OUT.relative_to(ROOT)} に書いた")


if __name__ == "__main__":
    main()
