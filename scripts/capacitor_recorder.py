#!/usr/bin/env python3
"""Does the recorder catch real degradation at a stated alarm rate? (docs/283 -> docs/284)

Executes the protocol pre-registered in docs/283, with observables fixed in its
addendum before any value was read.

This is the first dataset in the repo where the calibration budget is met.
docs/282 showed a threshold is a quantile of the fingerprint interval, so k
samples cannot express a rate finer than 1/k, and one alarm per hour needs
36,000. Every earlier dataset held 50 to 2,147. These capacitors hold 75,826
charge-discharge transients each, over 176 days, at a voltage held at 10 V.

The component is not an EPS part and the document says so. What is being tested
is the method -- per-unit fingerprint, deviation in floors, threshold at a
declared alarm rate -- against real degradation, which is the claim that has
never been verified.

Criteria: X1 samples per fingerprint; X2 units passing cross-validation;
X3 units firing before the record ends; X4 false alarms inside the fingerprint.
"""

from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import element_v2 as el
from slow_channel import slow_deviation

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".nasa_cap"
ZIP = CACHE / "cap12.zip"
INNER = "12. Capacitor Electrical Stress"
# one table per voltage group: capacitor_recorder_ES10.tsv, _ES12, _ES14
OUT = ROOT / "data" / "capacitor_recorder_ES10.tsv"
OUT_ES12 = ROOT / "data" / "capacitor_recorder_ES12.tsv"
OUT_ES14 = ROOT / "data" / "capacitor_recorder_ES14.tsv"

FP_FRAC = 1 / 3
NS = [50, 100, 200, 500]
FA_PER_HOUR, HOUR = 1.0, 36000
SHIFT_MAX = 1.0
NAMES = ["放電の速さ", "初期値", "終端値"]


def ensure(group: str) -> Path:
    """Extract one .mat on demand; extracted copies are not kept in the repo."""
    p = CACHE / INNER / f"{group}.mat"
    if not p.exists():
        with zipfile.ZipFile(ZIP) as z:
            z.extract(f"{INNER}/{group}.mat", CACHE)
    return p


def observables(vo: np.ndarray) -> np.ndarray:
    """Three scalars per transient, fixed in docs/283 before any value was read."""
    n = vo.shape[1]
    head = np.median(vo[:, : max(1, n // 10)], axis=1)
    tail = np.median(vo[:, -max(1, n // 10):], axis=1)
    span = head - tail
    hi = tail + 0.90 * span
    lo = tail + 0.37 * span
    speed = np.full(len(vo), np.nan)
    for i in range(len(vo)):
        w = vo[i]
        a = np.argmax(w <= hi[i]) if (w <= hi[i]).any() else None
        b = np.argmax(w <= lo[i]) if (w <= lo[i]).any() else None
        if a is not None and b is not None and b > a:
            speed[i] = b - a
    return np.column_stack([speed, head, tail])


def main() -> None:
    import h5py
    group = sys.argv[1] if len(sys.argv) > 1 else "ES10"
    p = ensure(group)
    f = h5py.File(p, "r")
    td = f[group]["Transient_Data"]
    units = [k for k in td if k.startswith(group + "C")]
    design = FA_PER_HOUR / HOUR
    print(f"{group}: 個体 {len(units)}  (電圧 {group[2:]} V で保持)")

    rows, cv_ok, fired = [], {n: 0 for n in NAMES}, {n: 0 for n in NAMES}
    fa_worst = {n: 0.0 for n in NAMES}
    n_samp = None

    print(f"\n{'個体':>9} {'観測量':>12} {'標本':>9} {'交差検証':>9} "
          f"{'誤報/判定':>11} {'設計比':>8} {'初発火':>9} {'残り':>7}")
    print("-" * 82)
    for u in units:
        vo = np.asarray(td[u]["VO"])
        if vo.shape[0] < vo.shape[1]:
            vo = vo.T
        obs = observables(vo)
        n_samp = len(obs)
        for j, nm in enumerate(NAMES):
            y = obs[:, j]
            ok = np.isfinite(y)
            if ok.sum() < 1000:
                continue
            y = y[ok]
            op = np.arange(len(y), dtype=float)
            c = int(len(y) * FP_FRAC)
            fp = el.take_fingerprint(y[:c], op[:c])
            if fp.floor <= 0:
                continue
            h = c // 2
            ra = y[:h] - (fp.slope * op[:h] + fp.intercept)
            rb = y[h:c] - (fp.slope * op[h:c] + fp.intercept)
            shift = abs(float(np.median(rb) - np.median(ra))) / fp.floor
            passes = shift < SHIFT_MAX

            best = None
            for n in NS:
                d0 = slow_deviation(y[:c], op[:c], fp, n)
                if d0 is None:
                    continue
                thr = float(np.quantile(d0, 1 - design))
                fa = float(np.mean(d0 > thr))
                if best is None or fa < best["fa"]:
                    best = {"n": n, "thr": thr, "fa": fa}
            if best is None:
                continue
            d = slow_deviation(y[c:], op[c:], fp, best["n"])
            k = int(np.argmax(d > best["thr"])) if (d is not None and (d > best["thr"]).any()) else None
            rest = (len(d) - k) / len(d) if (k is not None and d is not None) else 0.0
            if passes:
                cv_ok[nm] += 1
                fa_worst[nm] = max(fa_worst[nm], best["fa"])
                if k is not None:
                    fired[nm] += 1
            print(f"{u:>9} {nm:>12} {len(y):>9,} {shift:>9.2f} "
                  f"{best['fa']:>11.6f} {best['fa']/design:>7.1f}倍 "
                  f"{(str(k) if k is not None else '—'):>9} "
                  f"{(f'{rest:.0%}' if k is not None else '—'):>7}"
                  f"{'' if passes else '  (交差検証で除外)'}")
            rows.append({"unit": u, "obs": nm, "n": len(y), "shift": shift,
                         "fa": best["fa"], "first": k, "rest": rest,
                         "cv": int(passes)})

    nu = len(units)
    print(f"\n=== X1 指紋区間の標本数 ===")
    c = int(n_samp * FP_FRAC) if n_samp else 0
    print(f"  {c:,} / 個体  (要件 36,000)  {'PASS' if c >= 10000 else 'FAIL'} (基準 10,000以上)")
    print(f"  刻める最小の誤報率 = 1/{c:,} = {1/c*HOUR:.2f} 件/時" if c else "")

    print(f"\n=== X2 交差検証を通る個体 ===")
    for nm in NAMES:
        print(f"  {nm:>12}: {cv_ok[nm]}/{nu}  {'PASS' if cv_ok[nm] > nu/2 else 'FAIL'}")

    print(f"\n=== X3 通った個体のうち発火した数 ===")
    for nm in NAMES:
        if cv_ok[nm]:
            print(f"  {nm:>12}: {fired[nm]}/{cv_ok[nm]}  "
                  f"{'PASS' if fired[nm] > cv_ok[nm]/2 else 'FAIL'}")

    print(f"\n=== X4 指紋区間での誤報 ===")
    for nm in NAMES:
        if cv_ok[nm]:
            r = fa_worst[nm] / design
            print(f"  {nm:>12}: 最悪 {r:.1f}倍  {'PASS' if r <= 3 else 'FAIL'}")

    OUT.parent.mkdir(exist_ok=True)
    out = OUT.with_name(f"capacitor_recorder_{group}.tsv")   # OUT_ES12 / OUT_ES14
    with out.open("w") as fh:
        fh.write("unit\tobservable\tsamples\tcv_shift_floors\tfalse_alarm\t"
                 "first_fire\trest_frac\tpassed_cv\n")
        for r in rows:
            fh.write(f"{r['unit']}\t{r['obs']}\t{r['n']}\t{r['shift']:.4f}\t"
                     f"{r['fa']:.8f}\t{'' if r['first'] is None else r['first']}\t"
                     f"{r['rest']:.4f}\t{r['cv']}\n")
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
