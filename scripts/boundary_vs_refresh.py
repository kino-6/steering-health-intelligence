#!/usr/bin/env python3
"""Refuse beyond the validity range, or re-take the fingerprint? (docs/314 -> docs/315)

Both options can hide what the element exists to find. A boundary on
accumulated stress goes silent exactly where slow degradation lives; a
periodic refresh lets the baseline chase the degradation and absorb it. This
measures which failure is less bad on six devices run to failure.

Intervals, bank and rates are docs/297 as revised. The fingerprint slice is the
first half of run 1, which docs/309 found least prone to false alarms. The
stress axis is the accumulated thermal load of docs/312 -- built from package
temperature, and not the physical quantity its name suggests.

Criteria: V1 the boundary is quiet on run 4 and still fires later, on five of
six; V2 how often the boundary expires before the onset; V3 the same for each
refresh interval; V4 whichever wins, or neither.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "boundary_vs_refresh.tsv"
BANK = [100, 200, 500]
HOUR = 36000
ROBUST = 3.0 * 1.4826


def running_mean(x, n):
    if len(x) < n:
        return None
    c = np.concatenate(([0.0], np.cumsum(x)))
    return (c[n:] - c[:-n]) / n


def series(dev):
    z = zipfile.ZipFile(mos.ZIP) if hasattr(mos, "ZIP") else None
    y, op, rid = [], [], []
    for r in range(1, mos.N_RUNS + 1):
        ron, tp = mos.read_run(z, dev, r)
        y.append(np.asarray(ron, float)); op.append(np.asarray(tp, float))
        rid.append(np.full(len(ron), r))
    y, op, rid = np.concatenate(y), np.concatenate(op), np.concatenate(rid)
    n1 = int((rid == 1).sum())
    ref = float(np.median(op[:n1 // 2]))
    stress = np.cumsum(np.maximum(op - ref, 0.0))    # docs/312 accumulated thermal load
    return y, op, rid, stress, n1


def line(y, op):
    a, b = np.polyfit(op, y, 1)
    r = y - (a * op + b)
    return a, b, float(ROBUST * np.median(np.abs(r - np.median(r))))


def thresholds(resid, cal_mask):
    """One threshold per bank member from the calibration mask."""
    out = {}
    design = 1.0 / HOUR / len(BANK)
    for n in BANK:
        m = running_mean(resid, n)
        if m is None:
            continue
        c = np.abs(m)[cal_mask[n - 1:]]
        if len(c) < 10:
            continue
        q = min(1 - design, 1 - 1.0 / len(c))
        out[n] = (float(np.quantile(c, q)), m)
    return out


def score(resid_arrays, thr, rid, valid):
    """False alarms on run 4 and first fire from run 5, given per-N (thr, mean)."""
    fa_hits = fa_n = 0; fire = None
    for n, (t, m) in thr.items():
        rid_m, val_m = rid[n - 1:], valid[n - 1:]
        r4 = (rid_m == 4) & val_m
        fa_hits += int((np.abs(m)[r4] > t).sum()); fa_n = max(fa_n, int(r4.sum()))
        s = np.where((rid_m >= 5) & val_m & (np.abs(m) > t))[0]
        if s.size and (fire is None or int(rid_m[s[0]]) < fire):
            fire = int(rid_m[s[0]])
    fa = (fa_hits / fa_n * HOUR) if fa_n else float("nan")
    return fa, fire, fa_n


def run_boundary(dev):
    y, op, rid, stress, n1 = series(dev)
    fp = np.arange(len(y)) < n1 // 2
    cal = np.zeros(len(y), bool); cal[n1 // 2:] = True; cal &= (rid <= 3)
    a, b, g = line(y[fp], op[fp])
    if g <= 0:
        return None
    resid = (y - (a * op + b)) / g
    smax = float(stress[cal].max())
    valid = stress <= smax
    thr = thresholds(resid, cal)
    fa, fire, n4 = score(resid, thr, rid, valid)
    # where does the range expire?
    exp_i = int(np.argmax(~valid)) if (~valid).any() else None
    exp_run = int(rid[exp_i]) if exp_i is not None else None
    return {"fa": fa, "fire": fire, "n4": n4, "expire_run": exp_run}


def run_refresh(dev, k_mult):
    y, op, rid, stress, n1 = series(dev)
    cal = np.zeros(len(y), bool); cal[n1 // 2:] = True; cal &= (rid <= 3)
    width = float(stress[cal].max() - stress[cal].min())
    K = width * k_mult
    a0, b0, g0 = line(y[np.arange(len(y)) < n1 // 2], op[np.arange(len(y)) < n1 // 2])
    if g0 <= 0:
        return None
    # walk forward, re-fitting on the previous K of accumulated stress
    resid = np.empty(len(y)); a, b, g = a0, b0, g0
    last = stress[n1 // 2]
    for i in range(len(y)):
        if stress[i] - last >= K:
            w = (stress > stress[i] - K) & (np.arange(len(y)) < i)   # past only
            if w.sum() > 200:
                aa, bb, gg = line(y[w], op[w])
                if gg > 0:
                    a, b, g = aa, bb, gg
            last = stress[i]
        resid[i] = (y[i] - (a * op[i] + b)) / g
    thr = thresholds(resid, cal)
    fa, fire, n4 = score(resid, thr, rid, np.ones(len(y), bool))
    return {"fa": fa, "fire": fire, "n4": n4, "K_mult": k_mult}


def main() -> None:
    rows = []
    print("=== A 境界（累積ストレスの有効範囲を超えたら宣言しない）===")
    print(f"{'素子':>8} {'run4 誤報(件/時)':>16} {'run4 判定数':>11} {'初発火 run':>10} {'範囲が尽きる run':>16}")
    print("-" * 68)
    a_ok = 0
    for dev in mos.DEVICES:
        r = run_boundary(dev)
        if r is None:
            print(f"{dev:>8}  評価不能"); continue
        ok = np.isfinite(r["fa"]) and r["fa"] <= 3.0 and r["fire"] is not None
        a_ok += ok
        print(f"{dev:>8} {r['fa']:>16.1f} {r['n4']:>11,} {str(r['fire']):>10} "
              f"{str(r['expire_run']):>16}{'' if ok else '   NG'}")
        rows.append(("A 境界", dev, r["fa"], r["fire"], r["n4"], r["expire_run"]))
    print(f"\n=== V1 境界: 誤報 3 倍以内 かつ 発火 ===\n  {a_ok}/6  {'PASS' if a_ok >= 5 else 'FAIL'}")
    exps = [r[5] for r in rows if r[5] is not None]
    print(f"=== V2 範囲が run 5 より前に尽きた素子 ===\n  "
          f"{sum(1 for e in exps if e < 5)}/6  (尽きた run: {sorted(set(exps)) if exps else 'なし'})")

    print(f"\n=== B 採り直し ===")
    best_b = 0
    for k in (0.5, 1.0, 2.0):
        print(f"\n  K = 較正幅 × {k}")
        print(f"{'素子':>8} {'run4 誤報(件/時)':>16} {'初発火 run':>10}")
        print("  " + "-" * 40)
        ok_n = 0
        for dev in mos.DEVICES:
            r = run_refresh(dev, k)
            if r is None:
                print(f"{dev:>8}  評価不能"); continue
            ok = np.isfinite(r["fa"]) and r["fa"] <= 3.0 and r["fire"] is not None
            ok_n += ok
            print(f"{dev:>8} {r['fa']:>16.1f} {str(r['fire']):>10}{'' if ok else '   NG'}")
            rows.append((f"B 採り直し×{k}", dev, r["fa"], r["fire"], r["n4"], None))
        print(f"    → {ok_n}/6")
        best_b = max(best_b, ok_n)
    print(f"\n=== V3 採り直し: 最良 ===\n  {best_b}/6  {'PASS' if best_b >= 5 else 'FAIL'}")
    print(f"\n=== V4 どちらを採るか ===")
    if max(a_ok, best_b) < 5:
        print(f"  境界 {a_ok}/6、採り直し {best_b}/6。**どちらも 5 に届かない。この二択では解けない**")
    else:
        print(f"  境界 {a_ok}/6、採り直し {best_b}/6 → "
              f"{'境界' if a_ok >= best_b else '採り直し'} を採る")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("mode\tdevice\tfa_run4_per_hour\tfire_run\trun4_decisions\texpire_run\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
