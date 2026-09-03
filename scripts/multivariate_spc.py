#!/usr/bin/env python3
"""Does a multivariate view find what the single feature missed? (docs/301 -> docs/302)

Executes the protocol pre-registered in docs/301. Seven features per device,
each compensated against package temperature on runs 1-3 the way the single
observable always was; PCA on the standardised residuals of runs 1-3; Hotelling
T2 and SPE with a running mean of 200; thresholds from runs 1-3 at 1/hour
divided by two (clamped and reported); false alarms judged on run 4 and the
first fire searched from run 5 -- the same interval scheme as docs/297 revised.

Two questions, fixed in advance and kept apart: M1 does it fire, at an
acceptable run-4 rate, on the four devices the single feature did not fire on
for degradation; M2 does anything other than Vds/Id load on the component that
moves at onset.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np
import scipy.io as sio

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from slow_channel import running_mean

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / ".nasa_pcoe" / "MOSFET_Thermal_Overstress_Aging_v0"
OUT = ROOT / "data" / "multivariate_spc.tsv"

FEATS = ["Vds/Id", "supplyV", "flange-pkg", "gate_rise", "gate_plateau",
         "cond_drop", "Id_peak"]
N_MEAN = 200
HOUR = 36000
ROBUST = 3.0 * 1.4826
MISSED = {9, 10, 11, 12}          # docs/299: not fired on degradation itself


def gate_rise(v):
    lo, hi = v.min(), v.max()
    if hi - lo <= 0:
        return np.nan
    a = np.argmax(v >= lo + 0.1 * (hi - lo)); b = np.argmax(v >= lo + 0.9 * (hi - lo))
    return float(b - a) if b > a else np.nan


def load_device(dev):
    """Per steady-state record: 7 features, package temperature, run id."""
    rows = []
    for run in range(1, 8):
        m = sio.loadmat(DATA / f"Test_{dev}_run_{run}.mat", squeeze_me=True,
                        struct_as_record=False)["measurement"]
        # transient features indexed by time
        tt, tf = [], []
        for e in m.transient.flat:
            d = e.timeDomain
            vgs = np.asarray(d.gateSourceVoltage, float); vds = np.asarray(d.drainSourceVoltage, float)
            idr = np.asarray(d.drainCurrent, float)
            if vgs.size < 10:
                continue
            n = len(vgs); mid = vgs[n // 3: 2 * n // 3]
            sel = idr > idr.max() / 2 if idr.max() > 0 else np.zeros(n, bool)
            tt.append(float(e.timeEpoch))
            tf.append([gate_rise(vgs), float(np.median(mid)),
                       float(np.median(vds[sel])) if sel.any() else np.nan,
                       float(idr.max())])
        tt = np.array(tt); tf = np.array(tf); order = np.argsort(tt); tt, tf = tt[order], tf[order]
        for e in m.steadyState.flat:
            d = e.timeDomain
            if d.drainCurrent <= 0.01:
                continue
            j = int(np.clip(np.searchsorted(tt, float(e.timeEpoch)), 0, len(tt) - 1))
            rows.append([d.drainSourceVoltage / d.drainCurrent, d.supplyVoltage,
                         d.flangeTemperature - d.packageTemperature, *tf[j],
                         d.packageTemperature, run])
    a = np.array(rows, float)
    return a[:, :7], a[:, 7], a[:, 8].astype(int)


def main() -> None:
    print(f"特徴 {len(FEATS)}: {', '.join(FEATS)}   運用: 較正 run1-3 / 誤報 run4 / 探索 run5-\n")
    print(f"{'素子':>8} {'主成分':>5} {'達成率(OR)':>11} {'run4誤報 T2/SPE':>16} {'初発火 T2':>9} {'初発火 SPE':>10} "
          f"{'run5で動くPC':>11} {'Vds/Id以外の最大負荷':>22}")
    print("-" * 104)
    rows = []; m1 = 0; m2 = 0; m3 = 0
    uni_fire = {8: 5, 9: 6, 10: None, 11: 6, 12: 6, 14: 5}   # docs/299 diagnostic: true onset run
    for dev in mos.DEVICES:
        X, T, rid = load_device(dev)
        ok = np.isfinite(X).all(axis=1); X, T, rid = X[ok], T[ok], rid[ok]
        cal = rid <= 3
        # per-feature temperature compensation on runs 1-3
        R = np.empty_like(X)
        for k in range(7):
            a, b = np.polyfit(T[cal], X[cal, k], 1)
            R[:, k] = X[:, k] - (a * T + b)
        mu, sd = R[cal].mean(0), R[cal].std(0) + 1e-12
        Z = (R - mu) / sd
        U, S, Vt = np.linalg.svd(Z[cal], full_matrices=False)
        var = S**2 / (S**2).sum(); npc = int(np.searchsorted(np.cumsum(var), 0.90) + 1)
        P = Vt[:npc].T; lam = (S[:npc]**2) / (cal.sum() - 1)
        scores = Z @ P
        t2 = (scores**2 / lam).sum(1)
        spe = ((Z - scores @ P.T)**2).sum(1)
        stats = {"T2": running_mean(t2, N_MEAN), "SPE": running_mean(spe, N_MEAN)}
        rid_m = rid[N_MEAN - 1:]                      # running mean attributed to window end
        res = {}
        for nm, s in stats.items():
            c = s[rid_m <= 3]; q = min(1 - 1 / (2 * HOUR), 1 - 1 / len(c)); thr = float(np.quantile(c, q))
            ach = (1 - q) * HOUR
            r4 = s[rid_m == 4]
            # Test_10 loses run 4 entirely to feature NaNs; that is "not
            # evaluable", not zero and not infinity, and it does not count for M1
            fa = float(np.mean(r4 > thr)) * HOUR if r4.size else float("nan")
            srch = np.where((rid_m >= 5) & (s > thr))[0]
            fire_run = int(rid_m[srch[0]]) if srch.size else None
            res[nm] = (thr, ach, fa, fire_run)
        ach_or = sum(r[1] for r in res.values())
        fa_ok = all(np.isfinite(r[2]) and r[2] <= 3 * 1.0 for r in res.values())
        fired = [r[3] for r in res.values() if r[3] is not None]
        first = min(fired) if fired else None
        # M2: which PC moves most at run 5 vs runs 1-3, and its loadings
        d5 = np.abs(scores[rid == 5].mean(0) - scores[cal].mean(0)) / np.sqrt(lam)
        pc = int(np.argmax(d5)); load = np.abs(P[:, pc]); other = load.copy(); other[0] = 0
        top = FEATS[int(np.argmax(other))]; topv = float(other.max())
        m2_hit = topv >= 0.4
        if dev in MISSED and first is not None and fa_ok:
            m1 += 1
        m2 += m2_hit
        if first is not None and uni_fire[dev] is not None and first < uni_fire[dev]:
            m3 += 1
        fa_txt = "評価不能" if not np.isfinite(res['T2'][2]) else f"{res['T2'][2]:.0f}/{res['SPE'][2]:.0f}"
        print(f"{dev:>8} {npc:>5} {ach_or:>9.1f}/h {fa_txt:>16} "
              f"{str(res['T2'][3]):>9} {str(res['SPE'][3]):>10} {'PC'+str(pc+1):>11} {top:>14} {topv:>6.2f}")
        rows.append((dev, npc, ach_or, res["T2"][2], res["SPE"][2], res["T2"][3], res["SPE"][3], pc + 1, top, topv))
    print(f"\n=== M1 単変量が取り逃した4素子で、run4誤報3倍以内のまま鳴った ===\n  {m1}/4  {'PASS' if m1 >= 2 else 'FAIL'} (基準 2 以上)")
    print(f"=== M2 run5で動く主成分に Vds/Id 以外の負荷 >= 0.4 ===\n  {m2}/6  {'PASS' if m2 > 3 else 'FAIL'} (基準 過半)")
    print(f"=== M3 多変量の初発火が単変量の本物の立ち上がりより早い ===\n  {m3}/6")
    with OUT.open("w") as fh:
        fh.write("device\tn_pc\tachieved_or_per_hour\tfa_run4_T2_per_hour\tfa_run4_SPE_per_hour\tfire_run_T2\tfire_run_SPE\tpc_moving_at_run5\ttop_non_vdsid_feature\ttop_loading\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
