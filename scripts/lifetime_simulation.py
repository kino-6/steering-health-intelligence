"""Put the accelerated runs on a time axis the reader can convert (docs/339).

Everything measured so far is in units of test runs. This restates it in
accumulated stress -- degree-hours above the unit's own resting temperature,
the axis docs/312 settled on -- and runs the recorder along that axis.

The conversion from accumulated stress to vehicle years needs an activation
energy and a real temperature history, and neither is in this repo's public
data. It is not estimated. A conversion table is printed instead, so a reader
who has those numbers can finish the calculation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line
from assist_capability import capability, first_fire

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "lifetime_simulation.tsv"
HZ = 10.0                # sample rate the recorder runs at
FAST = 50                # 5-second decision window
REC_BYTES = 30


def read_epoch(dev):
    """Real elapsed hours from the dataset's own timestamps.

    The first version of this assumed the recorder's 10 Hz and got 0.1
    degree-hours for a run-to-failure test, which is absurd. The .mat records
    carry timeEpoch (MATLAB datenum) per sample; the sampling is far slower
    than 10 Hz, so the assumed rate understated the elapsed time by orders of
    magnitude. Read the time, do not assume it.
    """
    import zipfile
    import scipy.io as sio
    z = zipfile.ZipFile(mos.ZIP)
    hours, rid = [], []
    t0 = None
    for r in range(1, mos.N_RUNS + 1):
        name = f"MOSFET_Thermal_Overstress_Aging_v0/Test_{dev}_run_{r}.mat"
        p = mos.CACHE / name
        if not p.exists():
            z.extract(name, mos.CACHE)
        m = sio.loadmat(p, squeeze_me=True, struct_as_record=False)["measurement"]
        recs = np.ravel(m.steadyState)
        cur = np.array([float(x.timeDomain.drainCurrent) for x in recs])
        ep = np.array([float(x.timeEpoch) for x in recs])
        lo, hi = np.percentile(cur, 10), np.percentile(cur, 90)
        on = cur > (lo + hi) / 2
        if not on.any():
            continue
        e = ep[on]
        if t0 is None:
            t0 = e[0]
        hours.append((e - t0) * 24.0)
        rid.append(np.full(on.sum(), r))
    return np.concatenate(hours), np.concatenate(rid)


def stress_axis(dev):
    """Accumulated degree-hours above the unit's own resting temperature."""
    y, op, rid, _s, n1 = series(dev)
    hrs, rid2 = read_epoch(dev)
    if len(hrs) != len(op):
        raise SystemExit(f"Test_{dev}: 時刻 {len(hrs)} 点と観測 {len(op)} 点が合わない")
    ref = float(np.median(op[: n1 // 2]))
    dt = np.diff(hrs, prepend=hrs[0])
    dt[dt < 0] = 0.0                       # run boundaries
    s = np.cumsum(np.maximum(op - ref, 0.0) * dt)
    return y, op, rid, s, n1, ref, hrs


def main() -> None:
    print("累積ストレス（°C·時間）で見た、検知と故障の位置\n")
    print(f"{'素子':>8} {'基準値まで':>12} {'検知時点':>12} {'故障直前':>12} "
          f"{'検知→故障の余裕':>16} {'余裕の割合':>11}")
    print("-" * 78)
    rows, det, marg, frac = [], [], [], []
    for dev in mos.DEVICES:
        y, op, rid, s, n1, _ref, hrs = stress_axis(dev)
        f = first_fire(dev)
        s_enrol = float(s[n1 // 2])
        s_end = float(s[-1])
        if f is None:
            print(f"{dev:>8}  検知せず")
            continue
        idx = np.where(rid == f)[0]
        s_det = float(s[idx[0]])
        m = s_end - s_det
        print(f"{dev:>8} {s_enrol:>12.1f} {s_det:>12.1f} {s_end:>12.1f} "
              f"{m:>16.1f} {m/s_end:>10.1%}")
        det.append(s_det); marg.append(m); frac.append(m / s_end)
        rows.append((dev, s_enrol, s_det, s_end, m, m / s_end))

    print(f"\nY1 検知時点の累積ストレス: 中央値 {np.median(det):.1f} °C·時間、"
          f"範囲 {min(det):.1f}–{max(det):.1f}（{max(det)/min(det):.1f} 倍）")
    print(f"Y2 検知から故障までの余裕: 中央値 {np.median(marg):.1f} °C·時間、"
          f"範囲 {min(marg):.1f}–{max(marg):.1f}")
    r = max(marg) / min(marg) if min(marg) > 0 else float("inf")
    if r > 3:
        print("   → 3 倍を超える。**余裕は個体ごとに大きく違う**")

    # NVM, along the same axis
    print(f"\nY3 不揮発の使用量（検知後から故障までに書かれる分）")
    print(f"{'素子':>8} {'記録件数':>10} {'バイト':>10} {'判定を出せた割合':>16}")
    tot = []
    for dev in mos.DEVICES:
        y, op, rid, s, n1, _ref, hrs = stress_axis(dev)
        fpm = np.arange(len(y)) < n1 // 2
        a, b, g = line(y[fpm], op[fpm])
        if g <= 0:
            continue
        d = (y - (a * op + b)) / g
        cal = rid <= 3
        thr = float(np.quantile(np.abs(d[cal]), 1 - 1.0 / int(cal.sum())))
        lo, hi = float(op[fpm].min()), float(op[fpm].max())
        run = np.where(rid >= 5)[0]
        n = len(run) // FAST
        if not n:
            continue
        w = np.abs(d[run[: n * FAST]]).reshape(n, FAST).mean(axis=1)
        ok = ((op[run[: n * FAST]] >= lo) & (op[run[: n * FAST]] <= hi)
              ).reshape(n, FAST).mean(axis=1)
        cnt = int(((w > thr) & (ok > 0.5)).sum())
        tot.append(cnt)
        print(f"{dev:>8} {cnt:>10,} {cnt*REC_BYTES:>9,}B {ok.mean():>15.1%}")
    print(f"  中央値 {np.median(tot):,.0f} 件 = {np.median(tot)*REC_BYTES:,.0f} バイト")

    print(f"\n読み手が年に直すための換算")
    print(f"  検知までに要る累積ストレス S = {np.median(det):.0f} °C·時間（中央値）")
    print(f"  実車が平均 ΔT °C 超過で年 H 時間走るなら、検知は S/(ΔT·H) 年後\n")
    print(f"{'ΔT':>6} " + " ".join(f"{'H='+str(h)+'h':>10}" for h in (100, 300, 600)))
    for dt in (10, 20, 40, 80):
        print(f"{dt:>5}° " + " ".join(
            f"{np.median(det)/(dt*h):>10.1f}年" for h in (100, 300, 600)))
    print("\n  この表は換算の道具であって、実車の値ではない。"
          "ΔT と H は読み手が入れる。加速係数（活性化エネルギー）は含んでいない")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("device\tstress_enrol\tstress_detect\tstress_end\tmargin\tmargin_frac\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
