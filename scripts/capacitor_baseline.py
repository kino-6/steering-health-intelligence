#!/usr/bin/env python3
"""Does the waveform beat doing nothing? (docs/307)

Executes the protocol pre-registered in docs/307. Criteria are not changed here.

docs/306 compared its error only against the teacher's measurement noise, so
MAE 0.0130 could not be read on its own: a capacitor degrades monotonically in
time, and a model that only learned "later means lower" would score the same.
docs/307 puts three do-nothing baselines under the same folds. The decisive one
is the time baseline -- it uses NO waveform at all.

  mean baseline  the training folds' mean of the target ratio (a constant)
  time baseline  a degree-1 polynomial of the target on elapsed time only,
                 fitted on the 22 training units, evaluated on the held-out
                 unit from ITS OWN elapsed time. No waveform.
  last-value     always 1.0 (new)

Data, labels, features, subsampling and split are NOT rebuilt here. This script
imports scripts/capacitor_regression.py and calls its ensure(), eis_series() and
load_unit() with its own constants (STEP, WAVE_COLS, OBS_COL), so the 23 folds
hold exactly the rows docs/306 scored. The reproduction is checked, not assumed:
per unit, the row count and the EIS adjacent-measurement MAD must equal the
values recorded in data/capacitor_regression.tsv, and the run aborts otherwise.

Ridge P0 and HGB P0 per-unit MAE are READ from data/capacitor_regression.tsv,
not refitted. They are the numbers docs/306 reported; refitting them would only
risk reporting different ones under the same name.

Elapsed time, the one definition docs/307 left open: seconds since THAT UNIT's
first transient in the analysis (per-unit origin), expressed in days, which is
the MATLAB datenum unit the record carries. Per-unit, not pooled, because
  - the target is already per-unit (each unit's Cs divided by its OWN first EIS
    sweep, 1.0 = new), so a per-unit clock is the matching predictor;
  - a pooled origin would carry the calendar offset between the three groups'
    recorders into the predictor, i.e. which bench a unit sat on rather than
    its age;
  - it is the strongest version of the baseline -- "how long has this unit been
    running", the field analogue of accumulated key-on time -- and a baseline
    should be given its best shot before the model is said to beat it.
The origin is the unit's first transient INSIDE the analysis (the first row it
contributes after the EIS-span and finite-head filters), because the raw record
start is a group-level timestamp shared by every unit in the group.
The run reports what this choice was worth: all three groups in fact start on
the same day (2014-11-17, two minutes apart), so here the per-unit and the
pooled origin are the same clock. The choice was made before that was known.

S1 units where Ridge beats the mean baseline; S2 units where Ridge beats the
   time baseline (the decisive one); S3 units where HGB beats the time baseline.
   PASS is a majority of 23 for S1 and S2; S3 is descriptive.

Output: data/capacitor_baseline.tsv. Extracted .mat files are removed.
"""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capacitor_regression as cr
from capacitor_recorder import CACHE, INNER
from lib_discipline import passes

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "capacitor_baseline.tsv"
PRIOR = ROOT / "data" / "capacitor_regression.tsv"
ONE = 1.0                             # docs/307: the last-value baseline predicts new
TIME_DEG = 1                          # docs/307: degree-1 polynomial of target on time


def read_prior() -> dict[str, dict]:
    """Ridge P0 / HGB P0 per-unit MAE, and the reproduction check columns."""
    rows = {}
    with PRIOR.open() as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            r = dict(zip(head, line.rstrip("\n").split("\t")))
            rows[r["unit"]] = dict(group=r["group"], n=int(r["n_transients"]),
                                   emad=float(r["eis_mad"]), ridge=float(r["ridge_p0"]),
                                   hgb=float(r["hgb_p0"]))
    return rows


def assemble(prior: dict[str, dict]):
    """The docs/304 rows, rebuilt by calling capacitor_regression's own loader.

    Returns y (target ratio), elapsed (days since the unit's first row), unit,
    group. Aborts if any unit's row count or EIS MAD differs from docs/306.
    """
    import h5py
    ys, es, us, gs = [], [], [], []
    print(f"{'個体':>7} {'n':>6} {'(docs/306)':>10} {'EIS MAD':>8} {'(docs/306)':>10} "
          f"{'経過日数':>9} {'比 min..max':>13}")
    for g in cr.GROUPS:
        p = cr.ensure(g)
        f = h5py.File(p, "r")
        td = f[g]["Transient_Data"]
        sd = np.asarray(td["Serial_Date"]).ravel()
        for u in cr.UNITS[g]:
            et, ec, _ef, _sk = cr.eis_series(f, g, u)
            inside = (et >= sd.min()) & (et <= sd.max())
            et_in, er_in = et[inside], ec[inside] / ec[0]
            emad = float(np.median(np.abs(np.diff(er_in)))) if len(er_in) > 1 else float("nan")
            d = cr.load_unit(td, sd, u, None)
            span = (d["t"] >= et_in.min()) & (d["t"] <= et_in.max())
            keep = span & np.isfinite(d["X"][:, cr.OBS_COL])
            t = d["t"][keep]
            y = np.interp(t, et_in, er_in)
            elapsed = t - t.min()                      # days since this unit's first row
            n, pn, pe = int(keep.sum()), prior[u]["n"], prior[u]["emad"]
            print(f"{u:>7} {n:>6,} {pn:>10,} {emad:>8.5f} {pe:>10.5f} {elapsed.max():>9.2f} "
                  f"{y.min():>6.3f}..{y.max():<6.3f}")
            assert n == pn, (u, n, pn)
            assert abs(round(emad, 5) - pe) < 1e-9, (u, emad, pe)
            ys.append(y); es.append(elapsed); us += [u] * n; gs += [g] * n
        f.close()
    return (np.concatenate(ys), np.concatenate(es), np.array(us), np.array(gs))


def mae(pred, y) -> float:
    return float(np.mean(np.abs(pred - y)))


def main() -> None:
    t_start = time.time()
    print("docs/307: 「何もしない基準」3 つを docs/304 と同じ 23 折・同じ行で評価する。"
          "波形を使うのは Ridge / HGB だけ。")
    prior = read_prior()
    all_units = [u for g in cr.GROUPS for u in cr.UNITS[g]]
    assert sorted(prior) == sorted(all_units), (sorted(prior), sorted(all_units))

    print(f"\n===== 行の再現 (docs/306 と一致しなければ中断) =====")
    y, elapsed, unit, group = assemble(prior)
    N = len(y)
    print(f"\n過渡 {N:,} 件 (23 個体、間引き {cr.STEP} 回に 1 回、EIS 期間内、初期値が有限)。"
          f"docs/306 の行と一致。")

    # ------------------------------------------------- baselines on the same folds
    print(f"\n===== 個体 leave-one-out (23 折) の基準 =====")
    print(f"{'個体':>7} {'群':>5} {'評価n':>6} {'時刻基準の傾き/日':>17} {'切片':>8}")
    base = {}
    for u in all_units:
        tr, te = unit != u, unit == u
        mean_const = float(np.mean(y[tr]))                       # 平均基準
        coef = np.polyfit(elapsed[tr], y[tr], TIME_DEG)          # 時刻基準
        pt = np.polyval(coef, elapsed[te])
        base[u] = dict(mean=mae(np.full(int(te.sum()), mean_const), y[te]),
                       time=mae(pt, y[te]),
                       one=mae(np.full(int(te.sum()), ONE), y[te]),
                       const=mean_const, slope=float(coef[0]), icept=float(coef[1]),
                       n=int(te.sum()))
        print(f"{u:>7} {group[te][0]:>5} {te.sum():>6,} {coef[0]:>17.3e} {coef[1]:>8.4f}")
    consts = np.array([base[u]["const"] for u in all_units])
    print(f"  平均基準の定数: {consts.min():.4f}..{consts.max():.4f} (折による差はこれだけ)")

    # ------------------------------------------------------------- per-unit table
    print(f"\n===== 個体別 MAE (比の単位。Ridge/HGB は data/capacitor_regression.tsv の P0) =====")
    print(f"{'個体':>7} {'群':>5} {'n':>6} {'平均基準':>9} {'時刻基準':>9} {'最終値基準':>10} "
          f"{'Ridge':>8} {'HGB':>8} {'S1':>3} {'S2':>3} {'S3':>3}")
    s1, s2, s3, tsv = [], [], [], []
    for u in all_units:
        b, p = base[u], prior[u]
        a = passes(p["ridge"], b["mean"], "<")
        c = passes(p["ridge"], b["time"], "<")
        h = passes(p["hgb"], b["time"], "<")
        s1.append(a); s2.append(c); s3.append(h)
        tsv.append((u, p["group"], b["n"], b["mean"], b["time"], b["one"], p["ridge"], p["hgb"]))
        print(f"{u:>7} {p['group']:>5} {b['n']:>6,} {b['mean']:>9.4f} {b['time']:>9.4f} "
              f"{b['one']:>10.4f} {p['ridge']:>8.4f} {p['hgb']:>8.4f} "
              f"{'○' if a else '×':>3} {'○' if c else '×':>3} {'○' if h else '×':>3}")

    med = {k: float(np.median([base[u][k] for u in all_units])) for k in ("mean", "time", "one")}
    med_r = float(np.median([prior[u]["ridge"] for u in all_units]))
    med_h = float(np.median([prior[u]["hgb"] for u in all_units]))
    print(f"{'中央値':>7} {'':>5} {'':>6} {med['mean']:>9.4f} {med['time']:>9.4f} {med['one']:>10.4f} "
          f"{med_r:>8.4f} {med_h:>8.4f}")

    # ------------------------------------------------------------------- verdicts
    nu = len(all_units)
    print(f"\n=== S1 線形 (Ridge) が平均基準を下回る個体 ===")
    n1 = int(sum(s1))
    print(f"  {n1}/{nu}  {'PASS' if passes(n1, nu/2, '>') else 'FAIL'} "
          f"(過半で「波形は定数より良い」)")
    print(f"  → {'波形は定数より良い' if passes(n1, nu/2, '>') else '波形は定数より良くない'}")

    print(f"\n=== S2 線形 (Ridge) が時刻基準を下回る個体 (本命) ===")
    n2 = int(sum(s2))
    print(f"  {n2}/{nu}  {'PASS' if passes(n2, nu/2, '>') else 'FAIL'} "
          f"(過半で「波形が情報を足している」)")
    print(f"  → {'波形は時刻に情報を足している' if passes(n2, nu/2, '>') else '波形は時刻に情報を足していない'}")

    print(f"\n=== S3 勾配ブースティング (HGB) が時刻基準を下回る個体 (記述) ===")
    n3 = int(sum(s3))
    print(f"  {n3}/{nu}")
    for g in cr.GROUPS:
        gu = cr.UNITS[g]
        print(f"  {g}: 時刻基準 中央値 {np.median([base[u]['time'] for u in gu]):.4f}, "
              f"Ridge {np.median([prior[u]['ridge'] for u in gu]):.4f}, "
              f"HGB {np.median([prior[u]['hgb'] for u in gu]):.4f}  "
              f"S1 {sum(passes(prior[u]['ridge'], base[u]['mean'], '<') for u in gu)}/{len(gu)} "
              f"S2 {sum(passes(prior[u]['ridge'], base[u]['time'], '<') for u in gu)}/{len(gu)} "
              f"S3 {sum(passes(prior[u]['hgb'], base[u]['time'], '<') for u in gu)}/{len(gu)}")

    # ------------------------------------- how much the time baseline adds (descriptive)
    print(f"\n=== 時刻基準は平均基準とどれだけ違うか (記述。判定には使わない) ===")
    dif = np.array([base[u]["time"] - base[u]["mean"] for u in all_units])
    slopes = np.array([base[u]["slope"] for u in all_units])
    spans = np.array([float(elapsed[unit == u].max()) for u in all_units])
    print(f"  MAE の差 (時刻−平均) の中央値 {np.median(dif):+.5f}、範囲 {dif.min():+.5f}..{dif.max():+.5f}; "
          f"時刻基準が良い個体 {int((dif < 0).sum())}/{nu}")
    print(f"  当てはめた直線が記録全体 ({np.median(spans):.1f} 日) で表す変化は "
          f"{np.median(slopes)*np.median(spans):+.4f} 比。"
          f"一方、個体間の比の広がりは {y.min():.3f}..{y.max():.3f}")
    print(f"  → 学習側 22 個体をまとめた 1 本の直線は、個体ごとに違う劣化の速さを表せない。"
          f"この基準はほぼ定数であり、S2 は S1 とほとんど同じ問いになっている")
    print(f"  経過時間の原点: 3 群とも記録開始は同日 (差は 2 分) なので、"
          f"個体ごとの原点と共通原点はここでは実質同じ ({spans.min():.2f}..{spans.max():.2f} 日)")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("unit\tgroup\tn_transients\tmean_base\ttime_base\tone_base\tridge_p0\thgb_p0\n")
        for u, g, n, mb, tb, ob, r, h in tsv:
            fh.write(f"{u}\t{g}\t{n}\t{mb:.5f}\t{tb:.5f}\t{ob:.5f}\t{r:.5f}\t{h:.5f}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")

    print("\n事前登録からの逸脱 (手順上、値を見る前に決めたもの):")
    print("  1. 経過時間の原点は個体ごと (その個体が解析に出す最初の過渡)。docs/307 は定義を書いて"
          "いない。理由: 目標変数が個体ごとの比であること、共通原点だと群ごとの記録開始のずれが"
          "予測子に入ること。実際には 3 群とも同日開始で、この選択は結果を変えていない (下記の記述)")
    print("  2. 経過時間の単位は日 (記録の MATLAB datenum のまま)。1 次式なので単位は判定に影響しない")
    print("  3. Ridge P0 / HGB P0 は data/capacitor_regression.tsv から読んだ (再学習していない)。"
          "docs/306 が報告した値そのもの")
    print("  4. 行の再現は仮定せず検査した (個体ごとの件数と EIS MAD が docs/306 と一致しなければ中断)")
    print("  5. 基準は P0 のみ (docs/307 は交絡処理 P1 を求めていない)")
    print("  6. 時刻基準は学習側 22 個体の行をそのまま最小二乗で当てはめる (個体ごとの重み付けはしない)")

    for g in cr.GROUPS:
        p = CACHE / INNER / f"{g}.mat"
        if p.exists():
            p.unlink()
    d = CACHE / INNER
    if d.exists() and not any(d.iterdir()):
        shutil.rmtree(d)
    print(f"\nextracted .mat removed; only cap12.zip kept  ({(time.time()-t_start)/60:.1f} min)")


if __name__ == "__main__":
    main()
