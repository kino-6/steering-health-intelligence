"""Does the element produce a degradation level continuously, or only at alarms?

docs/331 gave capability at three time points. docs/333 showed it reconstructs
from the record. Neither answered whether the element emits a usable
degradation level all the time, which is what a receiver would need.

The bus frame goes out every 100 ms and carries the deviation, so capability
can be computed on every frame. This measures the resulting trajectory: how
noisy it is, whether it falls monotonically, and how much of the run it is
available at all (the element refuses outside the swept operating range).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "capability_trace.tsv"
WIN = 500                        # frames averaged before reporting, 50 s at 10 Hz
BUS_STEP, BUS_MAX = 0.1, 25.5


def trace(dev):
    y, op, rid, _s, n1 = series(dev)
    fpm = np.arange(len(y)) < n1 // 2
    a, b, g = line(y[fpm], op[fpm])
    if g <= 0:
        return None
    op_lo, op_hi = float(op[fpm].min()), float(op[fpm].max())
    inrange = (op >= op_lo) & (op <= op_hi)

    # what the bus carries, frame by frame
    d = (y - (a * op + b)) / g
    d = np.clip(np.round(np.abs(d) / BUS_STEP) * BUS_STEP, 0, BUS_MAX) * np.sign(d)

    runs = sorted(set(rid.tolist()))
    lo = max(op[rid == r].min() for r in runs)
    hi = min(op[rid == r].max() for r in runs)
    t_ref = float(np.median(op[(op >= lo) & (op <= hi)]))
    base_line = a * t_ref + b

    # capability per averaging window, using only frames the element declares on
    C, R = [], []
    for i in range(0, len(y) - WIN, WIN):
        s = slice(i, i + WIN)
        m = inrange[s]
        if m.sum() < WIN // 4:
            continue
        C.append(base_line + float(np.median(d[s][m])) * g)
        R.append(int(np.median(rid[s])))
    C, R = np.asarray(C), np.asarray(R)
    if len(C) < 8:
        return None
    healthy = float(np.median(C[R <= 4]))
    return np.sqrt(healthy / C), R, float(inrange.mean())


def main() -> None:
    print(f"バスフレームから {WIN} フレーム(50 秒)ごとに能力を出す。連続に出るか\n")
    print(f"{'素子':>8} {'点数':>6} {'判定を出せた割合':>16} "
          f"{'健全期のばらつき':>16} {'run4→7 の低下':>14} {'単調性':>8}")
    print("-" * 82)
    rows = []
    for dev in mos.DEVICES:
        got = trace(dev)
        if got is None:
            print(f"{dev:>8}  出せない")
            continue
        C, R, avail = got
        h = C[R <= 4]
        scatter = float(np.std(h))
        drop = float(np.median(h) - np.median(C[R == max(R)]))
        # run-level medians, then how much of the sequence falls
        med = [float(np.median(C[R == r])) for r in sorted(set(R.tolist())) if (R == r).any()]
        mono = sum(1 for i in range(1, len(med)) if med[i] <= med[i - 1]) / (len(med) - 1)
        print(f"{dev:>8} {len(C):>6} {avail:>15.1%} {scatter:>16.4f} "
              f"{drop:>14.3f} {mono:>7.0%}")
        rows.append((dev, len(C), avail, scatter, drop, mono, *med))

    sc = [r[3] for r in rows]; dr = [r[4] for r in rows]
    print(f"\n健全期のばらつき 中央値 {np.median(sc):.4f}")
    print(f"run4 から run7 への低下 中央値 {np.median(dr):.3f}")
    print(f"信号対ばらつき比 {np.median(dr)/np.median(sc):.0f} 倍")
    print(f"\n各素子の run ごとの能力（中央値）")
    print(f"{'素子':>8} " + " ".join(f"{'run'+str(r):>7}" for r in range(1, 8)))
    for r in rows:
        med = r[6:]
        print(f"{r[0]:>8} " + " ".join(f"{v:>7.3f}" for v in med))

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("device\tn_points\tavailable\thealthy_sd\tdrop\tmonotone\t"
                 + "\t".join(f"C_run{r}" for r in range(1, 8)) + "\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
