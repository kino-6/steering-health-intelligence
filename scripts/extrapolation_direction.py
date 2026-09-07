"""Is the extrapolation failure about distance or about direction (docs/324)?

docs/306 held out each stress group in turn and reported that the model does
not cross groups. Its own numbers say something narrower. Both 10 V and 14 V
are ends of the range, so both are extrapolations, and only the 10 V hold-out
breaks -- 12.6 times the per-unit error against 1.3. Distance cannot explain
that.

What separates them is which way the extrapolation goes. 10 V degrades most
slowly, so holding it out asks the model for less degradation than it has ever
seen. This measures whether the resulting error is a one-signed bias in the
over-predicting-degradation direction, or just scatter.

Loading, features and the linear model are capacitor_regression's, unchanged.
Only the accounting is new: the signed mean of predicted minus measured, per
unit, group-held-out against per-unit leave-one-out.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capacitor_regression as cr
from capacitor_recorder import ensure

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "extrapolation_direction.tsv"
D1_UNITS, D1_FACTOR = 6, 3.0        # docs/324, stated there as having nothing behind them


def build():
    """The same matrix docs/306 fitted, assembled the same way."""
    import h5py
    X, y, u, g = [], [], [], []
    sync = cr.read_eis_sync_fires()
    for grp in cr.GROUPS:
        f = h5py.File(ensure(grp), "r")
        td = f[grp]["Transient_Data"]
        sd = np.asarray(td["Serial_Date"]).ravel()
        fires = cr.read_fires(grp)
        for unit in cr.UNITS[grp]:
            et, ec, _ef, _sk = cr.eis_series(f, grp, unit)
            inside = (et >= sd.min()) & (et <= sd.max())
            et_in, er_in = et[inside], ec[inside] / ec[0]
            d = cr.load_unit(td, sd, unit, fires.get(unit))
            span = (d["t"] >= et_in.min()) & (d["t"] <= et_in.max())
            keep = span & np.isfinite(d["X"][:, cr.OBS_COL])
            if not keep.any():
                continue
            X.append(d["X"][keep])
            y.append(np.interp(d["t"][keep], et_in, er_in))
            u += [unit] * int(keep.sum())
            g += [grp] * int(keep.sum())
        f.close()
    return (np.vstack(X), np.concatenate(y),
            np.array(u), np.array(g))


def main() -> None:
    X, y, u, g = build()
    print(f"読み込み: {len(y):,} 標本 / {len(np.unique(u))} 個体 / {len(np.unique(g))} 群\n")

    # per-unit leave-one-out: the unit's own group stays in training
    loo_bias = {}
    for unit in np.unique(u):
        te = u == unit
        pred, _hgb, _a = cr.fit_predict(X[~te], y[~te], u[~te], X[te])
        loo_bias[unit] = float(np.mean(pred - y[te]))

    # group hold-out: the whole stress level is removed
    grp_bias, grp_pred = {}, {}
    for grp in cr.GROUPS:
        te = g == grp
        pred, _hgb, _a = cr.fit_predict(X[~te], y[~te], u[~te], X[te])
        # the label is a ratio to the unit's own first EIS reading, so 1.0 is
        # as-new and above 1.0 is more capacitance than the part ever had
        grp_pred[grp] = (float(np.median(pred)), float(np.median(y[te])),
                         float(np.mean(pred > 1.0)))
        for unit in np.unique(u[te]):
            m = u[te] == unit
            grp_bias[unit] = float(np.mean(pred[m] - y[te][m]))

    print("群を抜いたときの予測が、物理的な上限（比 1.0 = 新品）を超えていないか")
    print(f"{'群':>6} {'予測 中央値':>12} {'実測 中央値':>12} {'1.0 超えの割合':>15}")
    for grp in cr.GROUPS:
        pm, ym, over = grp_pred[grp]
        print(f"{grp:>6} {pm:>12.4f} {ym:>12.4f} {over:>14.1%}")
    print()

    print(f"符号付き平均（予測 − 実測）。**負 = 劣化しすぎと予測**")
    print(f"{'群':>6} {'個体':>9} {'群を抜く':>12} {'個体LOO':>12} {'倍率':>8}")
    print("-" * 54)
    rows, verdict = [], {}
    for grp in cr.GROUPS:
        us = [x for x in cr.UNITS[grp] if x in grp_bias]
        neg = sum(1 for x in us if grp_bias[x] < 0)
        pos = len(us) - neg
        ratios = []
        for x in us:
            r = abs(grp_bias[x]) / abs(loo_bias[x]) if loo_bias[x] else float("inf")
            ratios.append(r)
            print(f"{grp:>6} {x:>9} {grp_bias[x]:>12.5f} {loo_bias[x]:>12.5f} {r:>7.1f}x")
            rows.append((grp, x, grp_bias[x], loo_bias[x], r))
        same = max(neg, pos)
        med = float(np.median(ratios))
        d1 = same >= D1_UNITS and med >= D1_FACTOR
        d2 = neg > pos
        verdict[grp] = (same, len(us), med, d1, d2)
        print(f"{'':>6} {'→ 同符号':>9} {f'{same}/{len(us)}':>12} {'倍率中央値':>12} {med:>7.1f}x"
              f"   D1 {'成立' if d1 else '不成立'} / 向き {'劣化しすぎ' if d2 else '劣化しなさすぎ'}\n")

    s10, n10, m10, d1_10, d2_10 = verdict["ES10"]
    _s14, _n14, _m14, d1_14, _d2_14 = verdict["ES14"]
    print("=== 事前登録した判定 ===")
    print(f"  D1 ES10 が系統的な偏り（{D1_UNITS}/7 以上 同符号 かつ 中央値 {D1_FACTOR}x 以上）"
          f": {s10}/{n10}、{m10:.1f}x → {'PASS' if d1_10 else 'FAIL'}")
    print(f"  D2 その向きが「劣化しすぎと予測」        : {'PASS' if d2_10 else 'FAIL'}")
    print(f"  D3 ES14 は D1 を満たさない（非対称）      : {'PASS' if not d1_14 else 'FAIL'}")
    if d1_10 and d2_10 and not d1_14:
        print("\n  → 外挿の限界は距離ではなく向きで決まる。"
              "学習より遅く劣化する側へは外挿できず、誤りは「劣化しすぎ」に揃う")
    else:
        print("\n  → 事前登録どおりには揃わなかった。上の表のまま記述する")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("group\tunit\tbias_group_held_out\tbias_unit_loo\tratio\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
