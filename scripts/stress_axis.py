#!/usr/bin/env python3
"""Is the drift on calendar time or on accumulated stress? (docs/311 -> docs/312)

The user pointed out that a vehicle does not run on a schedule. docs/309 put a
drift term on sample index, which in this rig is calendar time and accumulated
stress at the same time because it runs continuously. In a car they separate --
a month parked advances the calendar and not the degradation -- so a
calendar-time term would drift a stationary vehicle into a false alarm.

Three candidate axes, with their collinearity measured first: if the rig makes
them the same to within 0.99 the test says so and declines to rule, per
docs/311.

Data: NASA PCoE MOSFET, public domain.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "stress_axis.tsv"
ROBUST = 3.0 * 1.4826
AXES = ["暦時間", "累積エネルギー", "累積熱負荷"]


def series(dev):
    """Observable, operating point, run id, and the raw parts of each axis."""
    z = zipfile.ZipFile(mos.ZIP) if hasattr(mos, "ZIP") else None
    y, op, rid, power, temp = [], [], [], [], []
    for r in range(1, mos.N_RUNS + 1):
        ron, tp = mos.read_run(z, dev, r)
        ron, tp = np.asarray(ron, float), np.asarray(tp, float)
        y.append(ron); op.append(tp); rid.append(np.full(len(ron), r))
        # Vds/Id is the observable; Vds*Id = (Vds/Id) * Id^2 is not recoverable
        # from the medians alone, so power is taken as the observable times the
        # square of a nominal current -- a monotone transform of the observable
        # would be circular. Instead: dissipated power is proportional to the
        # package-to-ambient rise, so accumulated energy uses the recorded
        # temperature rise, and the two accumulated axes differ only in whether
        # the rise is squared. Documented as a deviation.
        power.append(np.maximum(tp - np.median(tp), 0.0) ** 2)
        temp.append(tp - np.median(tp))
    y = np.concatenate(y); op = np.concatenate(op); rid = np.concatenate(rid)
    axes = np.column_stack([
        np.arange(len(y), dtype=float),
        np.cumsum(np.concatenate(power)),
        np.cumsum(np.concatenate(temp)),
    ])
    return y, op, rid, axes


def fit_resid(y, op, ax, mask):
    A = np.column_stack([op[mask], ax[mask], np.ones(mask.sum())])
    coef, *_ = np.linalg.lstsq(A, y[mask], rcond=None)
    pred = coef[0] * op + coef[1] * ax + coef[2]
    r = y - pred
    g = float(ROBUST * np.median(np.abs(r[mask] - np.median(r[mask]))))
    return r, g


def main() -> None:
    print("=== C0 3 軸の相関（較正区間 run 1〜3）===")
    print(f"{'素子':>8} {'暦×エネルギー':>14} {'暦×熱負荷':>12} {'エネルギー×熱負荷':>16} {'最大':>7}")
    print("-" * 62)
    rows, maxcorr = [], 0.0
    per_dev = {}
    for dev in mos.DEVICES:
        y, op, rid, ax = series(dev)
        n1 = int((rid == 1).sum())
        cal = np.zeros(len(y), bool); cal[n1 // 2:] = True; cal &= (rid <= 3)
        per_dev[dev] = (y, op, rid, ax, cal)
        C = np.corrcoef(ax[cal].T)
        c01, c02, c12 = abs(C[0, 1]), abs(C[0, 2]), abs(C[1, 2])
        m = max(c01, c02, c12); maxcorr = max(maxcorr, m)
        print(f"{dev:>8} {c01:>14.4f} {c02:>12.4f} {c12:>16.4f} {m:>7.4f}")
    print(f"\n  最大の相関 {maxcorr:.4f}  "
          f"{'区別不能（0.99 超）' if maxcorr > 0.99 else '区別できる'}")

    if maxcorr > 0.99:
        print("\n  → docs/311 の規則により、C1〜C3 の判定を出さない。")
        print("     この試験機では、暦時間と累積ストレスが同じものである。")
    else:
        print(f"\n=== C1 run 4 の残差が最も小さい軸 ===")
        print(f"{'素子':>8} " + "".join(f"{a:>16}" for a in AXES) + f"{'最良':>16}")
        print("-" * 78)
        best = {a: 0 for a in AXES}
        for dev in mos.DEVICES:
            y, op, rid, ax, cal = per_dev[dev]
            vals = []
            for k in range(3):
                r, g = fit_resid(y, op, ax[:, k], cal)
                vals.append(float(np.median(np.abs(r[rid == 4]))) / g if g else np.nan)
            b = AXES[int(np.nanargmin(vals))]; best[b] += 1
            print(f"{dev:>8} " + "".join(f"{v:>16.3f}" for v in vals) + f"{b:>16}")
            rows.append((dev, *vals, b))
        print(f"\n  最良の軸: " + "、".join(f"{a} {c}/6" for a, c in best.items()))
        win = max(best, key=best.get)
        print(f"  C1: {win} が {best[win]}/6  "
              f"{'PASS 過半' if best[win] > 3 else 'FAIL 過半に届かない'}")
        print(f"\n=== C3 累積軸が暦時間より良い素子 ===")
        c3 = sum(1 for r in rows if min(r[2], r[3]) < r[1])
        print(f"  {c3}/6  {'PASS 軸を替えるべき' if c3 > 3 else 'FAIL この試験機では差が出ない'}")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("device\tresid_calendar\tresid_energy\tresid_thermal\tbest_axis\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
        if not rows:
            fh.write(f"# C0 max correlation {maxcorr:.4f} > 0.99 -- axes indistinguishable\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
