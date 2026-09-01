#!/usr/bin/env python3
"""Does a slow channel fire on real ageing? (docs/270 -> docs/271)

Executes the protocol pre-registered in docs/270.

docs/269 ran the recorder over real degradation and it never fired: docs/167's
precursor is 20 to 300 times a noise measured after averaging a 36-minute run,
while the five-second window sees a floor 150 times larger. docs/225 arms a
five-second window and extends it only on firing, so a degradation visible only
in minutes of averaging is unreachable by construction.

This adds a second, independent time scale -- a running mean over N samples,
evaluated against the same per-unit fingerprint, never waiting on the fast
side. Its threshold is derived from the same one-alarm-per-hour condition on
healthy data rather than carried over, because the sample count differs; that
was fixed in docs/270 before running so it cannot read as tuning after a
failure.

Criteria: D1 five of six devices fire before the record ends; D2 the false
alarms stay within three times the design rate; D3 two of three machines fire
on real fault severity.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import element_v2 as el
import mosfet_precursor as mos
import pmsm_measured_signature as sig
from capability_second_mechanism import headroom
from real_degradation import device_series, FP_FRAC

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "slow_channel.tsv"

NS = [100, 200, 500, 1000, 2000, 5000]     # docs/270, an assumed grid
FA_PER_HOUR, HOUR_SAMPLES = 1.0, 36000
HEALTHY_FRAC = 0.25                        # the first quarter, as in docs/269


def running_mean(x, n):
    if len(x) < n:
        return None
    c = np.concatenate(([0.0], np.cumsum(x)))
    return (c[n:] - c[:-n]) / n


def slow_deviation(y, op, fp, n):
    resid = (y - (fp.slope * op + fp.intercept)) / fp.floor
    m = running_mean(resid, n)
    return None if m is None else np.abs(m)


def main() -> None:
    units = {}
    for dev in mos.DEVICES:
        y, t, run_of = device_series(dev)
        cut = int(int((run_of == 1).sum()) * FP_FRAC)
        fp = el.take_fingerprint(y[:cut], t[:cut])
        units[f"Test_{dev}"] = (fp, y[cut:], t[cut:])

    print("=== D1/D2  遅い側。本物の劣化。注入なし ===")
    print(f"{'N':>7} {'閾値':>9} {'発火した素子':>13} {'初発火の位置(中央値)':>22} "
          f"{'誤報/窓':>10} {'設計比':>8}")
    print("-" * 76)

    rows, best = [], None
    for n in NS:
        # threshold from the healthy stretch of every unit, at one alarm/hour.
        # one decision per sample, so the rate per decision is 1/36000.
        pool = []
        for name, (fp, y, op) in units.items():
            d = slow_deviation(y, op, fp, n)
            if d is None:
                continue
            h = max(1, int(len(d) * HEALTHY_FRAC))
            pool.append(d[:h])
        if not pool:
            print(f"{n:>7}  標本が足りない")
            continue
        pool = np.concatenate(pool)
        q = 1 - FA_PER_HOUR / HOUR_SAMPLES
        if q > 1 - 1.0 / len(pool):        # never a quantile outside the sample
            q = 1 - 1.0 / len(pool)
        thr = float(np.quantile(pool, q))

        fired, pos, fa = 0, [], []
        for name, (fp, y, op) in units.items():
            d = slow_deviation(y, op, fp, n)
            if d is None:
                continue
            h = max(1, int(len(d) * HEALTHY_FRAC))
            fa.append(float(np.mean(d[:h] > thr)))
            hit = np.argmax(d > thr) if (d > thr).any() else None
            if hit is not None:
                fired += 1
                pos.append(hit / len(d))
        design = FA_PER_HOUR / HOUR_SAMPLES
        obs = float(np.mean(fa))
        print(f"{n:>7} {thr:>9.3f} {fired:>10}/6 "
              f"{(f'{np.median(pos):.0%}' if pos else '—'):>22} "
              f"{obs:>10.5f} {obs/design:>7.1f}倍")
        rows.append({"n": n, "thr": thr, "fired": fired,
                     "pos": float(np.median(pos)) if pos else None,
                     "fa": obs, "ratio": obs / design})
        if fired >= 5 and obs <= design * 3 and best is None:
            best = rows[-1]

    print(f"\n=== D1 6中5以上が発火するN ===")
    if best:
        print(f"  N = {best['n']} 標本 (= {best['n']/10:.0f} 秒)  "
              f"{best['fired']}/6  PASS")
    else:
        ok = [r for r in rows if r["fired"] >= 5]
        print(f"  誤報条件を満たすNは無い。"
              f"{'発火だけなら N=' + str(ok[0]['n']) if ok else '発火するNも無い'}  FAIL")

    print(f"\n=== D2 誤報 ===")
    if best:
        print(f"  N={best['n']} で {best['ratio']:.1f}倍  "
              f"{'PASS' if best['ratio'] <= 3 else 'FAIL'} (基準 3倍以内)")

    # ---- D3 real fault severity, three machines --------------------------
    print(f"\n=== D3 モータ3機体、実故障重症度 ===")
    n_use = best["n"] if best else NS[len(NS) // 2]
    print(f"  N = {n_use} で評価")
    hits = {}
    for zp in sorted(sig.ZIP.parent.glob("*.zip")):
        z = zipfile.ZipFile(zp)
        cur = [c for c in z.namelist() if "current" in c]

        def sev(nm):
            m = re.search(r"W_(\d+)[_.](\d+)_current", nm.split("/")[-1])
            return float(f"{m.group(1)}.{m.group(2)}") if m else None

        def series(nm):
            p = sig.CACHE / nm
            if not p.exists():
                z.extract(nm, sig.CACHE)
            ph = sig.load_phases(p)
            f0 = sig.find_f0(ph)
            k = len(ph[0]) // 200
            return np.array([headroom([x[i*k:(i+1)*k] for x in ph], f0)
                             for i in range(200)])

        healthy = [c for c in cur if sev(c) == 0.0]
        faulty = sorted([c for c in cur if sev(c) not in (None, 0.0)], key=sev)
        if not healthy or not faulty:
            continue
        h0 = series(healthy[0])
        op0 = np.arange(len(h0), dtype=float)
        fp = el.take_fingerprint(h0, op0)
        # slow side over the sub-window series; N scaled to its length
        nn = max(2, min(len(h0) // 4, n_use // 25))
        base = slow_deviation(h0, op0, fp, nn)
        thr = float(np.quantile(base, 1 - 1.0 / len(base)))
        hit = None
        for nm in faulty:
            h = series(nm)
            d = slow_deviation(h, op0[:len(h)], fp, nn)
            if d is not None and (d > thr).any():
                hit = sev(nm)
                break
        hits[zp.stem] = hit
        print(f"  {zp.stem:>7}  平均長 {nn:>4}  "
              f"{(f'{hit}% で発火' if hit is not None else '全重症度で鳴らず')}")
    n_ok = sum(1 for v in hits.values() if v is not None)
    print(f"  {n_ok}/3 機体  {'PASS' if n_ok >= 2 else 'FAIL'} (基準 3中2)")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("n_samples\tthreshold\tdevices_fired\tfirst_fire_frac\t"
                 "false_alarm_per_decision\tratio_to_design\n")
        for r in rows:
            pos = "" if r["pos"] is None else f"{r['pos']:.4f}"
            fh.write(f"{r['n']}\t{r['thr']:.5f}\t{r['fired']}\t{pos}\t"
                     f"{r['fa']:.6f}\t{r['ratio']:.3f}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
