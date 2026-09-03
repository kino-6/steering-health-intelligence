#!/usr/bin/env python3
"""Does the charge-discharge waveform carry the degradation state? (docs/304)

Executes the protocol pre-registered in docs/304. Criteria, inputs, models and
splits are not changed here.

docs/284 built a detector on these capacitors and docs/300 showed its firings
are a recorder-wide event, not degradation. This is the repo's first supervised
question with real scale: 23 units x ~75,000 charge-discharge transients as
input, and the EIS series capacitance (73 sessions per unit) as the teacher.

Teacher: per unit, every EIS sweep inside the transient record's time span
gives Cs/uF at its lowest positive frequency (the first 8 entries of a sweep
are zero padding). Cs is interpolated linearly in time to each transient and
divided by the unit's first EIS Cs -> ratio, 1.0 = new. Transients outside
the EIS time span are dropped.

Inputs (23 dims by protocol): the three docs/283 observables from
capacitor_recorder.observables() plus the VO waveform at every 20th of its
400 columns. No time, recorder id or group.

What the data does to the inputs, reported as found rather than repaired:
  A VO row is a charge transient of 191-390 samples, NaN-padded to 400, so
  observables() returns NaN for 放電の速さ and 終端値 on every transient (this
  is why docs/284 reported 0/7 for them). A feature that is NaN on every
  transient is dropped. Waveform columns past a record's end are NaN; they
  are median-imputed on the training fold and standardised on the training
  fold, and both models get that same matrix.

Runtime: transients are subsampled to every 10th per unit (~7,600 of 75,826).

Splits: leave-one-unit-out (23 folds) and leave-one-group-out (3 folds).
Models: RidgeCV over logspace(-3,3,13), alpha by 5-fold CV inside the training
fold with folds grouped by unit; HistGradientBoostingRegressor with default
parameters (random_state fixed for reproducibility only).
Confounder: P0 nothing; P1 drops transients within +-2,000 samples of the
unit's docs/284 first fire (absolute index, checked against data/eis_sync.tsv).

R1 median LOO MAE of Ridge P0, and units whose MAE is within their EIS
   adjacent-measurement MAD; R2 group-holdout MAE <= 2x LOO MAE; R3 units
   where HGB beats Ridge by >= 10%; R4 units where P1 improves on P0.

Output: data/capacitor_regression.tsv. Extracted .mat files are removed.
"""

from __future__ import annotations

import datetime as dt
import shutil
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capacitor_recorder import CACHE, FP_FRAC, INNER, NAMES, ensure, observables
from eis_sync import char, datenum_to_iso, matlab_datenum
from lib_discipline import passes

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "capacitor_regression.tsv"
GROUPS = ["ES10", "ES12", "ES14"]
UNITS = {"ES10": [f"ES10C{i}" for i in range(1, 8)],
         "ES12": [f"ES12C{i}" for i in range(1, 9)],
         "ES14": [f"ES14C{i}" for i in range(1, 9)]}
STEP = 10                            # every 10th transient per unit (runtime)
WAVE_COLS = np.arange(0, 400, 20)    # docs/304: 400 points thinned to 20
ALPHAS = np.logspace(-3, 3, 13)      # docs/304: Ridge alpha grid
INNER_FOLDS = 5                      # docs/304: alpha by 5-fold CV inside the training fold
CONF_HALF = 2000                     # docs/304 P1: +-2,000 samples around the fire
SEED = 304
R2_FACTOR, R3_FACTOR = 2.0, 0.9      # docs/304 R2, R3
OBS_COL, OBS_NAME = 1, "初期値"       # the observable whose fire docs/284 recorded
FEATURES = list(NAMES) + [f"VO[{c}]" for c in WAVE_COLS]


# ---------------------------------------------------------------- teacher (EIS)

def col_names(f, ds) -> list[str]:
    """ColumNames element: a uint16 char matrix (names down the columns)."""
    a = np.asarray(ds)
    if a.dtype.kind == "O":              # a cell: take its first element
        a = np.asarray(f[a.ravel()[0]])
    if a.ndim != 2:
        return []
    return ["".join(chr(c) for c in a[:, j]).strip("\x00 ") for j in range(a.shape[1])]


def eis_series(f, group: str, unit: str):
    """Per EIS sweep: (datenum, Cs at the lowest positive frequency), sorted by time."""
    m = f[group]["EIS_Data"][unit]["EIS_Measurement"]
    H, D, C = m["Header"], m["Data"], m["ColumNames"]
    ts, cs, fq, skipped = [], [], [], 0
    for i in range(H.shape[0]):
        names = col_names(f, f[C[i, 0]])
        fi = [k for k, n in enumerate(names) if n == "freq/Hz"]
        ci = [k for k, n in enumerate(names) if n.startswith("Cs/")]
        hc, dc = f[H[i, 0]], f[D[i, 0]]
        if not fi or not ci:
            skipped += hc.shape[0]
            continue
        for s in range(hc.shape[0]):
            lines = char(f, hc[s, 0])
            hit = [l for l in lines if "Acquisition started on" in l] if isinstance(lines, list) else []
            d = f[dc[s, 0]]
            if not hit or d.dtype.kind != "f" or d.ndim != 2:
                skipped += 1
                continue
            a = np.asarray(d)
            fr, c = a[fi[0]], a[ci[0]]
            pos = np.isfinite(fr) & (fr > 0) & np.isfinite(c)
            if not pos.any():
                skipped += 1
                continue
            j = np.flatnonzero(pos)[np.argmin(fr[pos])]
            stamp = hit[0].split(":", 1)[1].strip()
            ts.append(matlab_datenum(dt.datetime.strptime(stamp, "%m/%d/%Y %H:%M:%S")))
            cs.append(float(c[j]))
            fq.append(float(fr[j]))
    o = np.argsort(ts)
    return np.array(ts)[o], np.array(cs)[o], np.array(fq)[o], skipped


# ------------------------------------------------------------- inputs (VO)

def read_fires(group: str) -> dict[str, int]:
    """docs/284 first_fire: a RUNTIME index in the finite-filtered 初期値 series."""
    p = ROOT / "data" / f"capacitor_recorder_{group}.tsv"
    out = {}
    with p.open() as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            r = dict(zip(head, line.rstrip("\n").split("\t")))
            if r["observable"] == OBS_NAME and r["passed_cv"] == "1" and r["first_fire"]:
                out[r["unit"]] = int(r["first_fire"])
    return out


def read_eis_sync_fires() -> dict[str, int]:
    p = ROOT / "data" / "eis_sync.tsv"
    out = {}
    if p.exists():
        with p.open() as fh:
            head = fh.readline().rstrip("\n").split("\t")
            for line in fh:
                r = dict(zip(head, line.rstrip("\n").split("\t")))
                out[r["unit"]] = int(r["fire_abs_index"])
    return out


def load_unit(td, sd: np.ndarray, unit: str, first_fire: int | None):
    """Every STEP-th transient: 3 observables + 20 waveform points, time, index.

    The fire's absolute index follows docs/300: first_fire is an index into
    the finite-filtered 初期値 series, offset by the fingerprint length.
    """
    vo = np.asarray(td[unit]["VO"])
    if vo.shape[0] < vo.shape[1]:
        vo = vo.T
    n = vo.shape[0]
    head_all = np.median(vo[:, : max(1, vo.shape[1] // 10)], axis=1)   # docs/284's 初期値, all rows
    ok = np.isfinite(head_all)
    fire_abs = None
    if first_fire is not None:
        c = int(ok.sum() * FP_FRAC)
        fire_abs = int(np.flatnonzero(ok)[first_fire + c])
    idx = np.arange(0, n, STEP)
    sub = vo[idx]
    X = np.column_stack([observables(sub), sub[:, WAVE_COLS]])
    L = np.isfinite(sub).sum(axis=1)
    return dict(n=n, idx=idx, t=sd[idx], X=X, L=L, fire_abs=fire_abs,
                n_nan_rows=int((~ok).sum()))


# ------------------------------------------------------------------ models

def fit_predict(Xtr, ytr, utr, Xte):
    """Impute + standardise on the training fold only; Ridge (alpha by grouped
    5-fold CV inside the fold) and HGB with defaults, on the same matrix."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import GroupKFold
    from sklearn.preprocessing import StandardScaler
    imp = SimpleImputer(strategy="median", keep_empty_features=True).fit(Xtr)
    sc = StandardScaler().fit(imp.transform(Xtr))
    A = sc.transform(imp.transform(Xtr))
    B = sc.transform(imp.transform(Xte))
    splits = list(GroupKFold(n_splits=INNER_FOLDS).split(A, ytr, groups=utr))
    ridge = RidgeCV(alphas=ALPHAS, cv=splits).fit(A, ytr)
    hgb = HistGradientBoostingRegressor(random_state=SEED).fit(A, ytr)
    return ridge.predict(B), hgb.predict(B), float(ridge.alpha_)


def mae(pred, y) -> float:
    return float(np.mean(np.abs(pred - y)))


# -------------------------------------------------------------------- main

def main() -> None:
    import h5py
    t_start = time.time()
    print(f"docs/304: 波形 → EIS 静電容量比の回帰。過渡は各個体 {STEP} 回に 1 回に間引く "
          f"(実行時間のため。事前登録には無い)。")

    all_units = [u for g in GROUPS for u in UNITS[g]]
    eis_sync_fire = read_eis_sync_fires()
    rows_X, rows_y, rows_u, rows_g, rows_keep, rows_t = [], [], [], [], [], []
    info = {}
    fire_mismatch = []

    for g in GROUPS:
        p = ensure(g)
        f = h5py.File(p, "r")
        td = f[g]["Transient_Data"]
        sd = np.asarray(td["Serial_Date"]).ravel()
        eis_units = sorted(k for k in f[g]["EIS_Data"] if k.startswith(g + "C"))
        tr_units = sorted(k for k in td if k.startswith(g + "C"))
        extra = sorted(set(eis_units) - set(tr_units))
        fires = read_fires(g)
        print(f"\n===== {g} =====  過渡記録 {len(sd):,} 点 {datenum_to_iso(sd.min())} .. "
              f"{datenum_to_iso(sd.max())};  過渡あり {len(tr_units)} 個体"
              + (f"; EIS のみ(過渡なし、対象外) {extra}" if extra else ""))
        assert tr_units == UNITS[g], (tr_units, UNITS[g])
        print(f"{'個体':>7} {'EIS総数':>7} {'期間内':>6} {'最低f[Hz]':>9} {'Cs0[µF]':>8} "
              f"{'比 min..max':>13} {'EIS MAD':>8} {'過渡(全)':>8} {'期間内':>7} {'P1除外後':>8} "
              f"{'発火abs':>8} {'skip':>5}")
        for u in UNITS[g]:
            t0 = time.time()
            et, ec, ef, skipped = eis_series(f, g, u)
            cs0 = ec[0]                                   # the unit's FIRST EIS Cs
            inside = (et >= sd.min()) & (et <= sd.max())
            et_in, er_in = et[inside], ec[inside] / cs0
            emad = float(np.median(np.abs(np.diff(er_in)))) if len(er_in) > 1 else float("nan")
            d = load_unit(td, sd, u, fires.get(u))
            span = (d["t"] >= et_in.min()) & (d["t"] <= et_in.max())
            finite_head = np.isfinite(d["X"][:, OBS_COL])
            keep = span & finite_head
            y = np.interp(d["t"][keep], et_in, er_in)
            abs_idx = d["idx"][keep]
            if d["fire_abs"] is None:
                p1 = np.ones(keep.sum(), bool)
            else:
                p1 = np.abs(abs_idx - d["fire_abs"]) > CONF_HALF
                if u in eis_sync_fire and eis_sync_fire[u] != d["fire_abs"]:
                    fire_mismatch.append((u, d["fire_abs"], eis_sync_fire[u]))
            rows_X.append(d["X"][keep]); rows_y.append(y)
            rows_u += [u] * int(keep.sum()); rows_g += [g] * int(keep.sum())
            rows_keep.append(p1); rows_t.append(d["t"][keep])
            info[u] = dict(group=g, n_eis=len(et), n_eis_in=int(inside.sum()), f_low=float(np.median(ef)),
                           cs0=cs0, r_min=float(er_in.min()), r_max=float(er_in.max()), emad=emad,
                           n_all=len(d["idx"]), n=int(keep.sum()), n_p1=int(p1.sum()),
                           fire_abs=d["fire_abs"], n_nan_rows=d["n_nan_rows"],
                           eis_span=(datenum_to_iso(et_in.min()), datenum_to_iso(et_in.max())))
            print(f"{u:>7} {len(et):>7} {inside.sum():>6} {info[u]['f_low']:>9.2f} {cs0:>8.1f} "
                  f"{er_in.min():>6.3f}..{er_in.max():<6.3f} {emad:>8.4f} {len(d['idx']):>8,} "
                  f"{keep.sum():>7,} {p1.sum():>8,} "
                  f"{(d['fire_abs'] if d['fire_abs'] is not None else '—'):>8} {skipped:>5}"
                  f"   ({time.time()-t0:.0f}s)")
        f.close()

    X = np.vstack(rows_X); y = np.concatenate(rows_y)
    unit = np.array(rows_u); group = np.array(rows_g)
    keep_p1 = np.concatenate(rows_keep)
    N = len(y)
    print(f"\n過渡 {N:,} 件 (23 個体、EIS 期間内、初期値が有限)。P1 で残る {keep_p1.sum():,} 件。")
    print(f"docs/284 発火 abs と data/eis_sync.tsv の不一致: {len(fire_mismatch)} {fire_mismatch}")

    nan_frac = np.isnan(X).mean(axis=0)
    print("\n入力の NaN 率 (データ全体):")
    for nm, fr in zip(FEATURES, nan_frac):
        print(f"  {nm:>10}: {fr:7.1%}")
    use = nan_frac < 1.0
    dropped = [nm for nm, k in zip(FEATURES, use) if not k]
    X = X[:, use]
    feat = [nm for nm, k in zip(FEATURES, use) if k]
    print(f"全件 NaN で落とす特徴: {dropped}  → 入力 {len(feat)} 次元 (事前登録 23)")

    # -------------------------------------------------- leave-one-unit-out
    treats = {"P0": np.ones(N, bool), "P1": keep_p1}
    loo = {}                         # (treat, unit) -> dict(ridge, hgb, n, alpha)
    pred_loo = {t: {"ridge": np.full(N, np.nan), "hgb": np.full(N, np.nan)} for t in treats}
    print(f"\n===== 個体 leave-one-out (23 折) × P0/P1 =====")
    print(f"{'処理':>4} {'個体':>7} {'評価n':>6} {'Ridge MAE':>10} {'HGB MAE':>9} {'alpha':>8} {'秒':>4}")
    for tname, base in treats.items():
        for u in all_units:
            t0 = time.time()
            tr = base & (unit != u); te = base & (unit == u)
            pr, ph, alpha = fit_predict(X[tr], y[tr], unit[tr], X[te])
            pred_loo[tname]["ridge"][te] = pr; pred_loo[tname]["hgb"][te] = ph
            loo[(tname, u)] = dict(ridge=mae(pr, y[te]), hgb=mae(ph, y[te]), n=int(te.sum()), alpha=alpha)
            print(f"{tname:>4} {u:>7} {te.sum():>6,} {loo[(tname,u)]['ridge']:>10.4f} "
                  f"{loo[(tname,u)]['hgb']:>9.4f} {alpha:>8.3g} {time.time()-t0:>4.0f}")

    # -------------------------------------------------- leave-one-group-out
    hold = {}                        # (treat, group) -> dict(ridge, hgb, per-unit)
    print(f"\n===== 応力群を丸ごと抜く 3 折 × P0/P1 =====")
    print(f"{'処理':>4} {'抜く群':>6} {'評価n':>6} {'Ridge MAE':>10} {'HGB MAE':>9} {'alpha':>8} {'秒':>4}")
    for tname, base in treats.items():
        for g in GROUPS:
            t0 = time.time()
            tr = base & (group != g); te = base & (group == g)
            pr, ph, alpha = fit_predict(X[tr], y[tr], unit[tr], X[te])
            per = {}
            for u in UNITS[g]:
                m = unit[te] == u
                per[u] = (mae(pr[m], y[te][m]), mae(ph[m], y[te][m]))
            hold[(tname, g)] = dict(ridge=mae(pr, y[te]), hgb=mae(ph, y[te]), per=per, n=int(te.sum()),
                                    loo_ridge=mae(pred_loo[tname]["ridge"][te], y[te]),
                                    loo_hgb=mae(pred_loo[tname]["hgb"][te], y[te]))
            print(f"{tname:>4} {g:>6} {te.sum():>6,} {hold[(tname,g)]['ridge']:>10.4f} "
                  f"{hold[(tname,g)]['hgb']:>9.4f} {alpha:>8.3g} {time.time()-t0:>4.0f}")

    # ------------------------------------------------------- per-unit table
    print(f"\n===== 個体別 (LOO の MAE、比の単位) =====")
    print(f"{'個体':>7} {'群':>5} {'n':>6} {'EIS MAD':>8} {'Ridge P0':>9} {'Ridge P1':>9} {'HGB P0':>8} "
          f"{'HGB P1':>8} {'R1内':>5} {'R3':>3} {'R4':>3} {'群抜きRidge P0':>13}")
    r1_within, r3_hgb, r4_ridge, r4_hgb = [], [], [], []
    tsv = []
    for g in GROUPS:
        for u in UNITS[g]:
            a, b = loo[("P0", u)], loo[("P1", u)]
            emad = info[u]["emad"]
            w = passes(a["ridge"], emad, "<=")
            h = passes(a["hgb"], R3_FACTOR * a["ridge"], "<")
            c = passes(b["ridge"], a["ridge"], "<")
            ch = passes(b["hgb"], a["hgb"], "<")
            r1_within.append(w); r3_hgb.append(h); r4_ridge.append(c); r4_hgb.append(ch)
            tsv.append((u, g, a["n"], emad, a["ridge"], b["ridge"], a["hgb"], b["hgb"]))
            print(f"{u:>7} {g:>5} {a['n']:>6,} {emad:>8.4f} {a['ridge']:>9.4f} {b['ridge']:>9.4f} "
                  f"{a['hgb']:>8.4f} {b['hgb']:>8.4f} {'○' if w else '×':>5} {'○' if h else '×':>3} "
                  f"{'○' if c else '×':>3} {hold[('P0', g)]['per'][u][0]:>13.4f}")

    # ------------------------------------------------------------ verdicts
    nu = len(all_units)
    ridge_p0 = np.array([loo[("P0", u)]["ridge"] for u in all_units])
    ridge_p1 = np.array([loo[("P1", u)]["ridge"] for u in all_units])
    hgb_p0 = np.array([loo[("P0", u)]["hgb"] for u in all_units])
    hgb_p1 = np.array([loo[("P1", u)]["hgb"] for u in all_units])
    emads = np.array([info[u]["emad"] for u in all_units])
    ratio_span = np.array([info[u]["r_min"] for u in all_units])

    print(f"\n=== R1 個体 LOO、線形 (Ridge P0) の MAE の中央値 ===")
    n1 = int(sum(r1_within))
    print(f"  中央値 {np.median(ridge_p0):.4f} (比の単位; 個体の比の最小値の中央値 {np.median(ratio_span):.3f}、"
          f"つまり劣化幅の中央値 {1-np.median(ratio_span):.3f})")
    print(f"  EIS 隣接測定 MAD の中央値 {np.median(emads):.4f}")
    print(f"  誤差が EIS MAD 以内の個体: {n1}/{nu}  "
          f"{'PASS' if passes(n1, nu/2, '>') else 'FAIL'} (過半で「波形は劣化状態を担っている」)")
    print(f"  → {'波形は劣化状態を担っている' if passes(n1, nu/2, '>') else '波形は劣化状態を担っていない'}")

    print(f"\n=== R2 群を抜く 3 折: 抜いた群の MAE ≤ 個体 LOO の MAE × {R2_FACTOR:g} ===")
    r2_ok = {}
    for tname in treats:
        for model in ("ridge", "hgb"):
            oks = []
            for g in GROUPS:
                hv = hold[(tname, g)][model]; lv = hold[(tname, g)][f"loo_{model}"]
                ok = passes(hv, R2_FACTOR * lv, "<=")
                oks.append(ok)
                print(f"  {tname} {model:>5} {g}: 群抜き {hv:.4f} / LOO {lv:.4f} = {hv/lv:5.2f}×  "
                      f"{'PASS' if ok else 'FAIL'}")
            r2_ok[(tname, model)] = all(oks)
    print(f"  判定 (基準の線形、P0): {'PASS 群をまたぐ' if r2_ok[('P0','ridge')] else 'FAIL 群をまたがない'}"
          f"   (HGB P0: {'PASS' if r2_ok[('P0','hgb')] else 'FAIL'}, Ridge P1: {'PASS' if r2_ok[('P1','ridge')] else 'FAIL'}, "
          f"HGB P1: {'PASS' if r2_ok[('P1','hgb')] else 'FAIL'})")

    print(f"\n=== R3 勾配ブースティングが線形の MAE を 10% 以上下回る個体 (P0, LOO) ===")
    n3 = int(sum(r3_hgb))
    print(f"  {n3}/{nu}  {'PASS' if passes(n3, nu/2, '>') else 'FAIL'} "
          f"(過半なら勾配ブースティングが要る; そうでなければ線形で足りる)")
    print(f"  Ridge P0 MAE 中央値 {np.median(ridge_p0):.4f} / HGB P0 MAE 中央値 {np.median(hgb_p0):.4f}")
    print(f"  → {'勾配ブースティングが要る' if passes(n3, nu/2, '>') else '線形で足りる'}")

    print(f"\n=== R4 P1 (発火 ±{CONF_HALF:,} 標本を除く) で MAE が P0 より改善する個体 (記述) ===")
    n4, n4h = int(sum(r4_ridge)), int(sum(r4_hgb))
    print(f"  Ridge {n4}/{nu}, HGB {n4h}/{nu}")
    print(f"  MAE の差 P0−P1 の中央値: Ridge {np.median(ridge_p0-ridge_p1):+.4f}, HGB {np.median(hgb_p0-hgb_p1):+.4f} "
          f"(正なら P1 が良い; これを交絡の大きさとする)")
    print(f"  P1 で除いた過渡: {N-int(keep_p1.sum()):,}/{N:,}")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("unit\tgroup\tn_transients\teis_mad\tridge_p0\tridge_p1\thgb_p0\thgb_p1\n")
        for u, g, n, emad, r0, r1, h0, h1 in tsv:
            fh.write(f"{u}\t{g}\t{n}\t{emad:.5f}\t{r0:.5f}\t{r1:.5f}\t{h0:.5f}\t{h1:.5f}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")

    print("\n事前登録からの逸脱 (手順上、値を見る前に決めたもの):")
    print(f"  1. 過渡を各個体 {STEP} 回に 1 回に間引いた (実行時間)")
    print(f"  2. observables() の 3 特徴のうち全件 NaN のもの {dropped} を落とした "
          f"(VO が NaN 詰めの充電波形であるため; docs/284 の 0/7 と同じ事実)")
    print(f"  3. 波形 20 点の記録終端より後の NaN は学習側の中央値で埋め、両モデルに同じ行列を与えた")
    print(f"  4. Ridge の α を選ぶ 5 折は個体でまとめた (個体内分割をしない規則に合わせた)")
    print(f"  5. HGB は random_state={SEED} だけ固定 (再現性; 容量・学習率などは既定値)")
    print(f"  6. 「最低周波数」は正の最低周波数 (掃引の先頭 8 点は 0 詰め)")

    for g in GROUPS:
        p = CACHE / INNER / f"{g}.mat"
        if p.exists():
            p.unlink()
    d = CACHE / INNER
    if d.exists() and not any(d.iterdir()):
        shutil.rmtree(d)
    print(f"\nextracted .mat removed; only cap12.zip kept  ({(time.time()-t_start)/60:.1f} min)")


if __name__ == "__main__":
    main()
