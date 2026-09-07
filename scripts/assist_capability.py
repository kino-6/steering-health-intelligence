"""What the measured Ron degradation costs in assist (docs/330 -> docs/331).

docs/192 already derived the chain and it needs no labels. Conduction-limited,
I_max is the square root of the thermal headroom over Rth times Ron, so assist
torque goes as one over the square root of Ron, and

    C(t) = sqrt( Ron(base) / Ron(t) )

with Tj_max and ambient cancelling out. Ron across seven runs on six devices
has been in hand since docs/295.

The rig lowered its setpoint ten degrees per run and Ron depends on
temperature, so raw Ron compared across runs would read the operator's hand as
degradation (TROUBLES T1, five times). Each run is fitted against package
temperature and read at one reference temperature shared by all runs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series
from changepoint import slopes, WINDOWS, HOUR, ROBUST
from boundary_vs_refresh import line

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "assist_capability.tsv"
EARLY, LATE = 0.95, 0.80          # docs/330's reading, fixed before running


def capability(dev):
    """C per run, read where every run actually has samples.

    The midpoint of the overlapping temperature range is the obvious choice and
    it is wrong: measured, it lands at the 0.4th to 3.6th percentile of each
    run, so 96 percent of the data sits above it and the line is being read in
    a sparse cold tail. The median of the pooled samples inside the overlap is
    used instead, which is dense in every run by construction.
    """
    y, op, rid, _stress, _n1 = series(dev)
    runs = sorted(set(rid.tolist()))
    lo = max(op[rid == r].min() for r in runs)
    hi = min(op[rid == r].max() for r in runs)
    if not hi > lo:
        return None, None, None
    inside = (op >= lo) & (op <= hi)
    t_ref = float(np.median(op[inside]))
    ron, where = {}, {}
    for r in runs:
        m = rid == r
        a, b = np.polyfit(op[m], y[m], 1)
        ron[r] = float(a * t_ref + b)
        where[r] = float((op[m] <= t_ref).mean())
    # base is the healthy interval, not run 1 alone. Run 1's own fit carries
    # the same scatter as any other run's, and dividing by one noisy value
    # pushed five devices a percent above 1.0 -- which reads as "less
    # resistance than new" and is not something degradation can do. Taking the
    # median over runs 1-4 (docs/297's healthy interval) leaves that scatter
    # visible as spread around 1 instead of as a bias.
    healthy = [r for r in runs if r <= 4]
    base = float(np.median([ron[r] for r in healthy]))
    C = {r: float(np.sqrt(base / ron[r])) for r in runs}
    scatter = max(abs(C[r] - 1.0) for r in healthy)
    return C, t_ref, scatter


def first_fire(dev):
    """The run docs/317's slope detector first fires in, recomputed here."""
    y, op, rid, stress, n1 = series(dev)
    fp = np.arange(len(y)) < n1 // 2
    cal = np.zeros(len(y), bool); cal[n1 // 2:] = True; cal &= (rid <= 3)
    a, b, g = line(y[fp], op[fp])
    if g <= 0:
        return None
    resid = (y - (a * op + b)) / g
    design = 1.0 / HOUR / len(WINDOWS)
    fire = None
    for w in WINDOWS:
        sl, ix = slopes(resid, stress, w)
        if sl is None:
            continue
        rid_w, cal_w = rid[ix], cal[ix]
        c = sl[cal_w & np.isfinite(sl)]
        if len(c) < 20:
            continue
        a_cal = float(np.median(c))
        s_cal = float(ROBUST * np.median(np.abs(c - a_cal)))
        if s_cal <= 0:
            continue
        stat = np.abs(sl - a_cal) / s_cal
        cs = stat[cal_w & np.isfinite(stat)]
        thr = float(np.quantile(cs, min(1 - design, 1 - 1.0 / len(cs))))
        s = np.where((rid_w >= 5) & np.isfinite(stat) & (stat > thr))[0]
        if s.size:
            r = int(rid_w[s[0]])
            if fire is None or r < fire:
                fire = r
    return fire


def main() -> None:
    print("アシスト能力 C = √(R_on(健全期の中央値) / R_on(run))。**計算であって測定ではない**")
    print("R_on は全 run が通る基準温度に換算してから比べる（試験機の設定降下を劣化と読まないため）\n")
    hdr = " ".join(f"{'run'+str(r):>7}" for r in range(1, 8))
    print(f"{'素子':>8} {'基準温度':>9} {hdr} {'初発火':>7} {'発火時 C':>9} {'健全散らばり':>10}")
    print("-" * 108)
    rows, at_fire, scat = [], [], []
    for dev in mos.DEVICES:
        C, t_ref, scatter = capability(dev)
        if C is None:
            print(f"{dev:>8}  run 間で重なる温度が無く、換算できない")
            continue
        f = first_fire(dev)
        cf = C.get(f) if f else None
        cells = " ".join(f"{C[r]:>7.3f}" if r in C else f"{'—':>7}"
                         for r in range(1, 8))
        print(f"{dev:>8} {t_ref:>8.1f}° {cells} {str(f):>7} "
              f"{(f'{cf:.3f}' if cf else '—'):>9} {scatter:>9.3f}")
        scat.append(scatter)
        if cf:
            at_fire.append(cf)
        rows.append((dev, t_ref, f, cf, scatter, *[C.get(r) for r in range(1, 8)]))
    print(f"\n  健全期(run 1-4)の散らばりが、この計算自身の雑音である: "
          f"中央値 {np.median(scat):.3f}、最大 {max(scat):.3f}")

    last = [r[-1] for r in rows if r[-1] is not None]
    print(f"\n=== 事前登録した読み方 ===")
    if at_fire:
        m = float(np.median(at_fire))
        print(f"  A2 検出器が鳴った時点の C（中央値）: **{m:.3f}**"
              f"  範囲 {min(at_fire):.3f}〜{max(at_fire):.3f}")
        if m >= EARLY:
            print(f"     → {EARLY} 以上。**検出は機能低下に先行する**")
        elif m < LATE:
            print(f"     → {LATE} 未満。**検出時点で既に機能が落ちている**")
        else:
            print(f"     → {LATE}〜{EARLY} の間。数字のまま報告する")
    if last:
        print(f"  A1 最終 run の C（中央値）        : **{np.median(last):.3f}**"
              f"  範囲 {min(last):.3f}〜{max(last):.3f}")
    if at_fire and last:
        print(f"  A3 発火から最終 run までに失う分   : "
              f"**{np.median(at_fire) - np.median(last):.3f}**"
              f"（{(np.median(at_fire) - np.median(last)) * 100:.1f} 百分点）")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("device\tt_ref\tfire_run\tC_at_fire\thealthy_scatter\t"
                 + "\t".join(f"C_run{r}" for r in range(1, 8)) + "\n")
        for r in rows:
            fh.write("\t".join("" if x is None else str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
