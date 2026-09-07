"""Does the alarm threshold affect detection, or only storage (docs/335)?

docs/321 concluded that one alarm per hour costs sixteen line-hours per unit,
and the work stopped there. Two things reopen it. The requirement is one I
wrote myself in docs/248, from a grid I also chose. And docs/334 showed the
receiver reads a continuous level off the bus frame, computed from the
deviation directly, which never passes through the threshold.

So this sweeps the alarm target and measures two things separately: how many
30-byte records get written, and how well the continuous level separates
healthy runs from degraded ones.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "alarm_rate_relevance.tsv"
TARGETS = [1.0, 10.0, 100.0, 281.0, 1000.0]
HOUR = 36000.0                   # decisions per hour at 10 Hz
WIN = 500                        # docs/334's averaging block
FAST = 50                        # the runtime's 5-second window at 10 Hz
X1_FACTOR, X2_FACTOR = 10.0, 1.2


def prepare(dev):
    """The deviation series and the run labels, once per device."""
    y, op, rid, _s, n1 = series(dev)
    fpm = np.arange(len(y)) < n1 // 2
    a, b, g = line(y[fpm], op[fpm])
    if g <= 0:
        return None
    d = (y - (a * op + b)) / g
    return d, rid, (a, b, g), op


def records(d, rid, target):
    """How many 30-byte records the runtime would append in runs 4-7.

    The threshold is the quantile of the enrolment deviation that the target
    rate names, as _calibrate does: k samples cannot express finer than 1/k,
    so the achieved rate is reported alongside.
    """
    cal = rid <= 3
    k = int(cal.sum())
    want = target / HOUR
    q = max(want, 1.0 / k)
    thr = float(np.quantile(np.abs(d[cal]), 1 - q))
    # the runtime writes one record per 5-second window, not per sample
    run = np.where(rid >= 4)[0]
    n = len(run) // FAST
    if not n:
        return 0, q * HOUR, thr
    w = np.abs(d[run[:n * FAST]]).reshape(n, FAST)
    return int((w.mean(axis=1) > thr).sum()), q * HOUR, thr


def separation(d, rid):
    """Effect size between healthy and degraded, on the continuous level.

    This never sees the threshold. It is here to show whether the threshold
    has anything to do with reading the degradation.
    """
    lv, lr = [], []
    for i in range(0, len(d) - WIN, WIN):
        s = slice(i, i + WIN)
        lv.append(float(np.median(d[s])))
        lr.append(int(np.median(rid[s])))
    lv, lr = np.asarray(lv), np.asarray(lr)
    h, g = lv[lr <= 4], lv[lr >= 5]
    if len(h) < 3 or len(g) < 3 or h.std() == 0:
        return float("nan")
    return float(abs(g.mean() - h.mean()) / h.std())


def main() -> None:
    print("誤報の目標を振ったとき、記録の件数と分離の能力はどう動くか\n")
    print(f"{'目標(件/時)':>12} {'達成(件/時)':>12} {'記録件数 中央値':>16} "
          f"{'分離(効果量) 中央値':>20}")
    print("-" * 66)
    prep = {d: prepare(d) for d in mos.DEVICES}
    rows, counts, seps = [], {}, {}
    for t in TARGETS:
        cs, ss, ach = [], [], []
        for dev, p in prep.items():
            if p is None:
                continue
            d, rid, _abg, _op = p
            n, a, _thr = records(d, rid, t)
            cs.append(n); ach.append(a)
            ss.append(separation(d, rid))
            rows.append((t, dev, n, a, ss[-1]))
        counts[t] = float(np.median(cs)); seps[t] = float(np.median(ss))
        print(f"{t:>12.0f} {np.median(ach):>12.1f} {counts[t]:>16,.0f} "
              f"{seps[t]:>20.2f}")

    cmin, cmax = min(counts.values()), max(counts.values())
    smin, smax = min(seps.values()), max(seps.values())
    x1 = cmax / max(cmin, 1e-9) >= X1_FACTOR
    x2 = smax / max(smin, 1e-9) <= X2_FACTOR
    print(f"\n=== 事前登録した判定 ===")
    print(f"  X1 記録量は閾値で動く（{X1_FACTOR:.0f} 倍以上）: "
          f"{cmax/max(cmin,1e-9):.1f} 倍 → {'PASS' if x1 else 'FAIL'}")
    print(f"  X2 分離は閾値で動かない（{X2_FACTOR} 倍以内）  : "
          f"{smax/max(smin,1e-9):.3f} 倍 → {'PASS' if x2 else 'FAIL'}")
    if x1 and x2:
        print("\n  → 誤報率は記憶容量の設計値であって、検出能力の要求ではない。"
              "1 件/時 に較正できないことは、劣化を読めないことを意味しない")
    elif not x2:
        print("\n  → 閾値は検出能力に効いている。16 時間の壁はそのまま残る")
    else:
        print("\n  → 事前登録どおりには揃わなかった。表のまま記述する")

    print(f"\n素子ごとの分離（閾値に依存しないので 1 列）")
    for dev, p in prep.items():
        if p:
            print(f"  Test_{dev:<3} {separation(p[0], p[1]):.2f}")

    # Not pre-registered. X1 failed because the record count is set by how long
    # the deviation stays above the line, not by where the line is -- so the
    # remaining candidate for what the threshold controls is when the first
    # record appears. Measured here and labelled as after the fact.
    print(f"\n最初の記録が書かれる run（事前登録していない事後の測定）")
    print(f"{'素子':>8} " + " ".join(f"{str(int(t))+'件/時':>10}" for t in TARGETS))
    for dev, p in prep.items():
        if p is None:
            continue
        d, rid, _abg, _op = p
        cells = []
        for t in TARGETS:
            _n, _a, thr = records(d, rid, t)
            run = np.where(rid >= 4)[0]
            n = len(run) // FAST
            w = np.abs(d[run[:n * FAST]]).reshape(n, FAST).mean(axis=1)
            hit = np.where(w > thr)[0]
            cells.append(str(int(rid[run[hit[0] * FAST]])) if hit.size else "—")
        print(f"{dev:>8} " + " ".join(f"{c:>10}" for c in cells))

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("target_per_hour\tdevice\trecords\tachieved_per_hour\tseparation\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
