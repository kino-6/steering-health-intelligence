#!/usr/bin/env python3
"""Is the 23-unit synchronised firing explained by inserted EIS measurements? (docs/298)

Executes the protocol pre-registered in docs/298. Criteria are not changed here.

docs/284 found that all 23 capacitors in three voltage groups fire at the same
sample numbers; docs/294 showed the recording's time gaps do not explain it.
The same .mat files carry an EIS_Data struct: impedance spectroscopy inserted
between charge-discharge cycles, which would touch every unit at once.

What the file actually holds (h5py, MATLAB v7.3), reported as found:
  <ES>/EIS_Data/EIS_Reference_Table          cell (4, 73): date, start, end, test-hours
  <ES>/EIS_Data/<ES>C<n>/EIS_Measurement/    struct with Header, Data, ColumNames,
                                             each cell (73, 1); every element is a cell
                                             of 5 (day 0: 20) sub-measurements
    Header[i][s]   char matrix: EC-Lab ASCII header, 58 lines, containing
                   "Acquisition started on : MM/DD/YYYY HH:MM:SS"   <- the timestamp
    Data[i][s]     double (18, 59): 18 columns x 59 frequency points
    ColumNames     freq/Hz Re(Z)/Ohm -Im(Z)/Ohm |Z|/Ohm Phase(Z)/deg time/s ...
  Some sub-cells are empty (char of shape (2,), value "\\x00\\x00"); they are skipped
  and counted.

E1: median time from each unit's first fire to the nearest EIS timestamp, against
    1,000 random sample indices per group; PASS if <= 1/10 of the control's median.
E2: only if E1 passes -- rerun the 初期値 observable and slow deviation with
    +-k samples around every EIS event removed, k taken from the observed offsets,
    and count unit pairs firing within 3 samples of each other.
E3: if E1 fails, print 未解明 and name one next candidate.

Output: data/eis_sync.tsv. Extracted .mat files are removed afterwards.
"""

from __future__ import annotations

import datetime as dt
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import element_v2 as el
from capacitor_recorder import (CACHE, FA_PER_HOUR, FP_FRAC, HOUR, INNER, NS,
                                SHIFT_MAX, ensure, observables)
from slow_channel import slow_deviation

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "eis_sync.tsv"
GROUPS = ["ES10", "ES12", "ES14"]
N_RANDOM = 1000          # docs/298 step 4
E1_RATIO = 1 / 10        # docs/298 E1
PAIR_SAMPLES = 3         # docs/284 counted pairs within 3 samples
SEED = 298
OBS_COL, OBS_NAME = 1, "初期値"   # the only observable that passed docs/284 X2


def matlab_datenum(t: dt.datetime) -> float:
    """MATLAB datenum: days since year 0, so datenum(0000-01-00) = 0."""
    return (t - dt.datetime(1, 1, 1)).total_seconds() / 86400 + 367


def datenum_to_iso(d: float) -> str:
    return (dt.datetime(1, 1, 1) + dt.timedelta(days=d - 367)).strftime("%Y-%m-%d %H:%M:%S")


def char(f, ref) -> list[str] | str:
    """A MATLAB char stored by v7.3: uint16, transposed. Row-wise strings."""
    a = np.asarray(f[ref])
    if a.ndim == 2 and a.shape[0] > 1 and a.shape[1] > 1:
        return ["".join(chr(c) for c in a[:, j]) for j in range(a.shape[1])]
    return "".join(chr(c) for c in a.ravel())


def eis_times(f, group: str) -> tuple[dict[str, np.ndarray], dict]:
    """Every 'Acquisition started on' timestamp, per EIS unit, as MATLAB datenum."""
    eis = f[group]["EIS_Data"]
    per, info = {}, {"empty": 0, "no_stamp": 0, "shapes": set(), "entries": None}
    for u in sorted(k for k in eis if k.startswith(group + "C")):
        m = eis[u]["EIS_Measurement"]
        H, D = m["Header"], m["Data"]
        info["entries"] = H.shape
        ts = []
        for i in range(H.shape[0]):
            hc, dc = f[H[i, 0]], f[D[i, 0]]
            for s in range(hc.shape[0]):
                lines = char(f, hc[s, 0])
                if isinstance(lines, str):
                    if lines.strip("\x00") == "":
                        info["empty"] += 1
                        continue
                    lines = [lines]
                hit = [l for l in lines if "Acquisition started on" in l]
                if not hit:
                    info["no_stamp"] += 1
                    continue
                stamp = hit[0].split(":", 1)[1].strip()
                ts.append(matlab_datenum(dt.datetime.strptime(stamp, "%m/%d/%Y %H:%M:%S")))
                info["shapes"].add(f[dc[s, 0]].shape)
        per[u] = np.array(sorted(ts))
    return per, info


def nearest_dt_seconds(t: np.ndarray, eis_sorted: np.ndarray) -> np.ndarray:
    """|t - nearest EIS time| in seconds, eis_sorted ascending."""
    j = np.searchsorted(eis_sorted, t)
    lo = eis_sorted[np.clip(j - 1, 0, len(eis_sorted) - 1)]
    hi = eis_sorted[np.clip(j, 0, len(eis_sorted) - 1)]
    return np.minimum(np.abs(t - lo), np.abs(t - hi)) * 86400


def read_fires(group: str) -> dict[str, int]:
    """first_fire is a RUNTIME index in the finite-filtered series (docs/284)."""
    p = ROOT / "data" / f"capacitor_recorder_{group}.tsv"
    out = {}
    with p.open() as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            r = dict(zip(head, line.rstrip("\n").split("\t")))
            if r["observable"] == OBS_NAME and r["passed_cv"] == "1" and r["first_fire"]:
                out[r["unit"]] = int(r["first_fire"])
    return out


def unit_head(td, u: str) -> np.ndarray:
    vo = np.asarray(td[u]["VO"])
    if vo.shape[0] < vo.shape[1]:
        vo = vo.T
    return observables(vo)[:, OBS_COL]


def run_recorder(y: np.ndarray, op: np.ndarray, c_orig: int) -> int | None:
    """docs/283 recorder on one series; op is the ORIGINAL sample index.

    Fingerprint = samples whose original index is below c_orig (same boundary as
    the docs/284 run), so removing samples does not move the boundary.
    Returns the original index of the first fire, or None.
    """
    fp_mask = op < c_orig
    yf, of = y[fp_mask], op[fp_mask]
    fp = el.take_fingerprint(yf, of)
    if fp.floor <= 0:
        return None
    h = len(yf) // 2
    ra = yf[:h] - (fp.slope * of[:h] + fp.intercept)
    rb = yf[h:] - (fp.slope * of[h:] + fp.intercept)
    shift = abs(float(np.median(rb) - np.median(ra))) / fp.floor
    if shift >= SHIFT_MAX:
        return None
    design = FA_PER_HOUR / HOUR
    best = None
    for n in NS:
        d0 = slow_deviation(yf, of, fp, n)
        if d0 is None:
            continue
        thr = float(np.quantile(d0, 1 - design))
        fa = float(np.mean(d0 > thr))
        if best is None or fa < best["fa"]:
            best = {"n": n, "thr": thr, "fa": fa}
    yr, orr = y[~fp_mask], op[~fp_mask]
    d = slow_deviation(yr, orr, fp, best["n"])
    if d is None or not (d > best["thr"]).any():
        return None
    k = int(np.argmax(d > best["thr"]))
    return int(orr[k])          # window start, the same convention as first_fire


def close_pairs(fires: dict[str, int]) -> list[tuple[str, str, int]]:
    us = sorted(fires)
    out = []
    for a in range(len(us)):
        for b in range(a + 1, len(us)):
            d = abs(fires[us[a]] - fires[us[b]])
            if d <= PAIR_SAMPLES:
                out.append((us[a], us[b], d))
    return out


def main() -> None:
    import h5py
    rng = np.random.default_rng(SEED)
    rows, e1 = [], {}
    state = {}   # per group: what E2 needs, kept only if E1 passes
    all_fire_dt, all_rand_dt = [], []

    for g in GROUPS:
        p = ensure(g)
        f = h5py.File(p, "r")
        td = f[g]["Transient_Data"]
        sd = np.asarray(td["Serial_Date"]).ravel()
        n = len(sd)
        neg = int((np.diff(sd) < 0).sum())
        print(f"\n===== {g} =====")
        print(f"Transient_Data: {[k for k in td]}  Serial_Date n={n:,} "
              f"{datenum_to_iso(sd.min())} .. {datenum_to_iso(sd.max())}  "
              f"median step {np.median(np.diff(sd))*86400:.0f}s  "
              f"backward steps {neg}")
        print(f"Initial_Date: {char(f, f[g]['Initial_Date'].ref)}")

        per, info = eis_times(f, g)
        eis_all = np.array(sorted(np.concatenate(list(per.values()))))
        in_range = int(((eis_all >= sd.min()) & (eis_all <= sd.max())).sum())
        print(f"EIS_Data keys: {list(f[g]['EIS_Data'].keys())}")
        print(f"EIS_Reference_Table shape {f[g]['EIS_Data']['EIS_Reference_Table'].shape}; "
              f"Header/Data/ColumNames per unit {info['entries']}; Data cell shapes {sorted(info['shapes'])}")
        print(f"EIS timestamps: " + ", ".join(f"{u} {len(per[u])}" for u in per)
              + f"  | union {len(eis_all)}  (empty cells {info['empty']}, no stamp {info['no_stamp']})")
        print(f"EIS span {datenum_to_iso(eis_all.min())} .. {datenum_to_iso(eis_all.max())}; "
              f"inside the transient record: {in_range}")

        fires = read_fires(g)
        units = sorted(fires)
        heads, masks, fire_orig = {}, {}, {}
        print(f"\n{'個体':>7} {'runtime':>8} {'abs(orig)':>10} {'発火時刻':>20} "
              f"{'最寄りEIS[s]':>13} {'同EIS個体':>9} {'標本差':>7}")
        for u in units:
            y = unit_head(td, u)
            ok = np.isfinite(y)
            c = int(ok.sum() * FP_FRAC)
            orig = int(np.flatnonzero(ok)[fires[u] + c])
            t = sd[orig]
            dts = nearest_dt_seconds(np.array([t]), eis_all)[0]
            # which unit's EIS, and the sample offset to the transient nearest that EIS
            j = int(np.argmin(np.abs(eis_all - t)))
            who = next(uu for uu in per if np.any(per[uu] == eis_all[j]))
            near_idx = int(np.argmin(np.abs(sd - eis_all[j])))
            off = orig - near_idx
            heads[u], masks[u], fire_orig[u] = y, ok, orig
            all_fire_dt.append(dts)
            rows.append((g, u, orig, datenum_to_iso(t), dts, who, off))
            print(f"{u:>7} {fires[u]:>8,} {orig:>10,} {datenum_to_iso(t):>20} "
                  f"{dts:>13,.0f} {who:>9} {off:>+7}")

        c_orig = int(n * FP_FRAC)
        ridx = rng.integers(c_orig, n, size=N_RANDOM)   # the interval where fires can occur
        rdt = nearest_dt_seconds(sd[ridx], eis_all)
        all_rand_dt.extend(rdt.tolist())
        fdt = np.array([r[4] for r in rows if r[0] == g])
        med_f, med_r = float(np.median(fdt)), float(np.median(rdt))
        ok1 = med_f <= E1_RATIO * med_r
        e1[g] = ok1
        print(f"\nE1 {g}: 発火→最寄りEIS 中央値 {med_f:,.0f}s  |  ランダム{N_RANDOM}点(index {c_orig:,}..{n-1:,}) "
              f"中央値 {med_r:,.0f}s  |  比 {med_f/med_r:.3f}  → {'PASS' if ok1 else 'FAIL'}")
        state[g] = dict(sd=sd, eis_all=eis_all, heads=heads, masks=masks,
                        fire_orig=fire_orig, c_orig=c_orig, n=n)
        f.close()

    med_f, med_r = float(np.median(all_fire_dt)), float(np.median(all_rand_dt))
    ok_all = med_f <= E1_RATIO * med_r
    print(f"\n===== E1 overall ({len(all_fire_dt)} units vs {len(all_rand_dt)} random) =====")
    print(f"発火 中央値 {med_f:,.0f}s  ランダム 中央値 {med_r:,.0f}s  比 {med_f/med_r:.3f}  "
          f"→ {'PASS' if ok_all else 'FAIL'}")
    print("per group: " + ", ".join(f"{g} {'PASS' if e1[g] else 'FAIL'}" for g in GROUPS))

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("group\tunit\tfire_abs_index\tfire_time\tnearest_eis_dt_seconds\n")
        for g, u, orig, iso, dts, _, _ in rows:
            fh.write(f"{g}\t{u}\t{orig}\t{iso}\t{dts:.0f}\n")
    print(f"wrote {OUT.relative_to(ROOT)}")

    if ok_all:
        # k from the observed offsets: the largest |sample offset| among the 23 fires
        offs = np.array([r[6] for r in rows])
        k = int(np.max(np.abs(offs)))
        print(f"\n===== E2: EIS 事象の ±k 標本を除いて回し直す  (k = max|標本差| = {k}; "
              f"標本差の分布 min {offs.min():+d} median {np.median(offs):+.0f} max {offs.max():+d}) =====")
        for g in GROUPS:
            s = state[g]
            sd, n = s["sd"], s["n"]
            inside = s["eis_all"][(s["eis_all"] >= sd.min()) & (s["eis_all"] <= sd.max())]
            ev = np.unique([int(np.argmin(np.abs(sd - t))) for t in inside])
            drop = np.zeros(n, bool)
            for j in ev:
                drop[max(0, j - k): j + k + 1] = True
            before = close_pairs(s["fire_orig"])
            after_f = {}
            for u in sorted(s["heads"]):
                keep = s["masks"][u] & ~drop
                r = run_recorder(s["heads"][u][keep], np.flatnonzero(keep).astype(float), s["c_orig"])
                after_f[u] = r
            fired = {u: v for u, v in after_f.items() if v is not None}
            after = close_pairs(fired)
            print(f"\n{g}: EIS 事象 {len(ev)} 点, 除外 {drop.sum():,}/{n:,} 標本")
            for u in sorted(after_f):
                print(f"  {u}: 元 {s['fire_orig'][u]:>7,}  →  除外後 "
                      f"{(f'{after_f[u]:,}' if after_f[u] is not None else '— (鳴らず)'):>10}")
            print(f"  3標本以内の組: 元 {len(before)} {[(a,b,d) for a,b,d in before]}")
            print(f"           除外後 {len(after)} {[(a,b,d) for a,b,d in after]}   "
                  f"発火 {len(fired)}/{len(after_f)}")
    else:
        print("\n===== E3 =====")
        print("未解明")
        a, b = state["ES12"]["sd"], state["ES14"]["sd"]
        same = len(a) == len(b) and bool(np.array_equal(a, b))
        print(f"確認: ES12 と ES14 の Serial_Date は完全一致か → {same} "
              f"(n {len(a):,} / {len(b):,})")
        print("次の候補: ES12 と ES14 は同じ Serial_Date を持つ、つまり同じ記録器で同時に記録されている。"
              "同期の単位は『群』ではなく『記録器』であり、候補は記録器側の事象"
              "(取得ソフトの再起動・ファイル切り替え・較正)である。"
              "docs/294 はギャップを見たが、逆行(ES10 の backward steps)と"
              "サンプル間隔の変化点は見ていない。")

    for g in GROUPS:
        p = CACHE / INNER / f"{g}.mat"
        if p.exists():
            p.unlink()
    d = CACHE / INNER
    if d.exists() and not any(d.iterdir()):
        shutil.rmtree(d)
    print("\nextracted .mat removed; only cap12.zip kept")


if __name__ == "__main__":
    main()
