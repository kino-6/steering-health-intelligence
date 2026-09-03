#!/usr/bin/env python3
"""Fix the two causes docs/299 named, and re-measure (docs/308 -> docs/309).

docs/299 found the bank's six fires were two real detections, three devices
already alarming through run 4 on a slow healthy drift, and one warm-up
transient. Two defects were named and deliberately left unfixed at the time,
because fixing after seeing a result is tuning. They are pre-registered in
docs/308 and fixed here:

    F1  the slow channel never checked the fingerprint's operating range, so a
        run's cold start produced a false excursion. The fast side has always
        declined there; the slow side now does too, refusing any window that
        contains a sample outside the swept range.
    F2  the fingerprint was observable = a*operating_point + b, with no term
        for time, while the healthy runs drift monotonically from -0.05 to
        -0.24 floors. A drift coefficient is fitted on the calibration runs.

Intervals, bank and rates are exactly docs/297 as revised: calibration is the
second half of run 1 plus runs 2-3, run 4 judges false alarms, the search
starts at run 5, the bank is {100, 200, 500}, and the rate is one alarm per
hour divided by three, clamped to what the sample can express and reported.

Criteria: F-A false alarms within three times design on five of six; F-B fires
before the record ends on five of six; F-C both together; F-D which fix did it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from real_degradation import device_series

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "slow_refusal.tsv"

BANK = [100, 200, 500]
HOUR = 36000
ROBUST = 3.0 * 1.4826


def running_mean(x, n):
    if len(x) < n:
        return None
    c = np.concatenate(([0.0], np.cumsum(x)))
    return (c[n:] - c[:-n]) / n


def window_all(mask, n):
    """True where every sample of the n-window ending here satisfies mask."""
    c = np.concatenate(([0], np.cumsum(mask.astype(int))))
    return (c[n:] - c[:-n]) == n


def fit(y, op, t, drift):
    """Fingerprint on the calibration slice: line in operating point, plus
    optionally a term in elapsed time (F2)."""
    A = np.column_stack([op, t, np.ones_like(op)]) if drift else \
        np.column_stack([op, np.ones_like(op)])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    r = y - pred
    g = float(ROBUST * np.median(np.abs(r - np.median(r))))
    return coef, g


def predict(op, t, coef, drift):
    return (coef[0] * op + coef[1] * t + coef[2]) if drift else \
           (coef[0] * op + coef[1])


def evaluate(dev, refuse, drift, fp_slice="cal"):
    """fp_slice picks where the line is fitted.

    docs/308 named the calibration interval for F2's coefficients but never
    named a slice for the line itself, while docs/297 revised had fitted it on
    the first half of run 1. Fitting every mode on the same slice is what makes
    F0/F1/F2 comparable, so "cal" is the default -- and "fp" reproduces
    docs/299 so the difference between the two can be seen rather than assumed.
    """
    y, op, rid = device_series(dev)
    n1 = int((rid == 1).sum())
    cal = np.zeros(len(y), bool); cal[n1 // 2:] = True; cal &= (rid <= 3)
    t = np.arange(len(y), dtype=float) - float(np.argmax(cal))
    fit_on = cal if fp_slice == "cal" else (np.arange(len(y)) < n1 // 2)
    coef, g = fit(y[fit_on], op[fit_on], t[fit_on], drift)
    if g <= 0:
        return None
    resid = (y - predict(op, t, coef, drift)) / g
    lo, hi = float(op[cal].min()), float(op[cal].max())
    inside = (op >= lo) & (op <= hi)

    design = 1.0 / HOUR / len(BANK)
    fired, fa_hits, fa_n = None, 0, 0
    per_n = {}
    for n in BANK:
        m = running_mean(resid, n)
        if m is None:
            continue
        rid_m, cal_m = rid[n - 1:], cal[n - 1:]
        ok = window_all(inside, n) if refuse else np.ones(len(m), bool)
        c = np.abs(m)[cal_m & ok]
        if len(c) < 10:
            continue
        q = min(1 - design, 1 - 1.0 / len(c))
        thr = float(np.quantile(c, q))
        ach = (1 - q) * HOUR
        r4 = (rid_m == 4) & ok
        hits4 = int((np.abs(m)[r4] > thr).sum())
        srch = np.where((rid_m >= 5) & ok & (np.abs(m) > thr))[0]
        f = int(rid_m[srch[0]]) if srch.size else None
        per_n[n] = (thr, ach, hits4, int(r4.sum()), f)
        fa_hits += hits4; fa_n = max(fa_n, int(r4.sum()))
        if f is not None and (fired is None or f < fired):
            fired = f
    if not per_n:
        return None
    fa_rate = (fa_hits / fa_n * HOUR) if fa_n else float("nan")
    return {"fired": fired, "fa_per_hour": fa_rate,
            "ach_or": sum(v[1] for v in per_n.values()),
            "silent4": fa_n, "per_n": per_n}


def main() -> None:
    modes = [("F0' docs/299 の指紋(run1 前半)", False, False, "fp"),
             ("F0 較正区間に当てる", False, False, "cal"),
             ("F1 のみ", True, False, "cal"),
             ("F2 のみ", False, True, "cal"),
             ("F1+F2", True, True, "cal")]
    rows = []
    for label, refuse, drift, sl in modes:
        print(f"\n=== {label} ===")
        print(f"{'素子':>8} {'run4 誤報(件/時)':>16} {'設計比':>8} "
              f"{'run4 判定数':>11} {'初発火 run':>10} {'較正の達成率(OR)':>16}")
        print("-" * 76)
        fired = fa_ok = 0
        for dev in mos.DEVICES:
            r = evaluate(dev, refuse, drift, sl)
            if r is None:
                print(f"{dev:>8}  評価不能"); continue
            ok = np.isfinite(r["fa_per_hour"]) and r["fa_per_hour"] <= 3.0
            fa_ok += ok; fired += r["fired"] is not None
            print(f"{dev:>8} {r['fa_per_hour']:>16.1f} {r['fa_per_hour']:>7.1f}倍 "
                  f"{r['silent4']:>11,} {str(r['fired']):>10} {r['ach_or']:>13.1f}/h"
                  f"{'' if ok else '  NG'}")
            rows.append((label, dev, r["fa_per_hour"], r["fired"], r["silent4"], r["ach_or"]))
        print(f"  誤報 3 倍以内: {fa_ok}/6   故障前に発火: {fired}/6")
        if label == "F1+F2":
            print(f"\n=== F-A 誤報が3倍以内 ===\n  {fa_ok}/6  {'PASS' if fa_ok >= 5 else 'FAIL'} (基準 6中5)")
            print(f"=== F-B 故障前に発火 ===\n  {fired}/6  {'PASS' if fired >= 5 else 'FAIL'} (基準 6中5)")
            print(f"=== F-C 両方 ===\n  {'PASS' if (fa_ok >= 5 and fired >= 5) else 'FAIL'}")
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("mode\tdevice\tfa_run4_per_hour\tfire_run\trun4_decisions\tachieved_or_per_hour\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
