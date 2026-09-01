#!/usr/bin/env python3
"""The recorder on a power stage that switches (docs/281 -> docs/282).

Executes the protocol pre-registered in docs/281.

Every power-stage failure in this repo carries the same caveat: the MOSFET rig
runs its device as a heater in the active region, not as a switch. This dataset
switches at 1 kHz with temperature held, and the recorder has never been run on
it -- so the caveat becomes a test instead of a refrain.

The three observables are the ones docs/234 already defined; no new ones are
invented here. Steady-state channels are all NaN in this dataset, so the
operating point can only be record order, and docs/273 showed that manufactures
false positives on a ramping rig -- which is why only held intervals are used.

Criteria: I1 at least one observable survives the cross-validation rule of
docs/280; I2 a majority of devices fire before their record ends; I3 false
alarms inside the fingerprint interval stay within three times the design rate.
"""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

import numpy as np
import scipy.io as sio

sys.path.insert(0, str(Path(__file__).resolve().parent))
import element_v2 as el
import igbt_switching_precursor as ig
from slow_channel import slow_deviation

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "igbt_recorder.tsv"

NAMES = ["ターンオン遅れ", "導通時の電圧", "ゲート平坦部"]
FP_FRAC = 1 / 3
NS = [5, 10, 20, 50]
FA_PER_HOUR, HOUR_SAMPLES = 1.0, 36000
SHIFT_MAX = 1.0        # docs/280 cross-validation rule


def device_arrays():
    ig.ensure_extracted()
    devs = sorted({os.path.basename(os.path.dirname(f))
                   for f in glob.glob(str(ig.BASE / "Device */*.mat"))})
    out = {}
    for dev in devs:
        recs = []
        for f in sorted(glob.glob(str(ig.BASE / dev / "*.mat"))):
            if "check" in os.path.basename(f):
                continue
            m = sio.loadmat(f, squeeze_me=True,
                            struct_as_record=False)["measurement"]
            for r in np.ravel(m.transient):
                try:
                    t = ig.parse_date(r.date)
                    v = ig.features(r.timeDomain)
                except Exception:
                    continue
                if t and v:
                    recs.append((t, *v))
        if len(recs) < 30:
            continue
        recs.sort(key=lambda x: x[0])
        out[dev] = np.array([[r[1] * 1e9, r[2], r[3]] for r in recs], dtype=float)
    return out


def main() -> None:
    devs = device_arrays()
    print(f"素子 {len(devs)}: " + ", ".join(f"{d}({len(a)})" for d, a in devs.items()))
    design = FA_PER_HOUR / HOUR_SAMPLES

    print(f"\n{'素子':>10} {'観測量':>16} {'交差検証のずれ':>14} {'誤報/判定':>11} "
          f"{'設計比':>8} {'初発火':>8} {'残り':>8}")
    print("-" * 84)
    rows, survived, fired = [], set(), {}

    for dev, a in devs.items():
        cut = int(len(a) * FP_FRAC)
        for j, nm in enumerate(NAMES):
            y = a[:, j]
            ok = np.isfinite(y)
            if ok.sum() < 60:
                continue
            y = y[ok]
            op = np.arange(len(y), dtype=float)
            c = int(len(y) * FP_FRAC)
            fp = el.take_fingerprint(y[:c], op[:c])
            if fp.floor <= 0:
                continue
            # docs/280 cross-validation: split the fingerprint interval in two
            h = c // 2
            ra = y[:h] - (fp.slope * op[:h] + fp.intercept)
            rb = y[h:c] - (fp.slope * op[h:c] + fp.intercept)
            shift = abs(float(np.median(rb) - np.median(ra))) / fp.floor
            passes_cv = shift < SHIFT_MAX

            best = None
            for n in NS:
                d0 = slow_deviation(y[:c], op[:c], fp, n)
                if d0 is None:
                    continue
                q = min(1 - design, 1 - 1.0 / len(d0))
                thr = float(np.quantile(d0, q))
                fa = float(np.mean(d0 > thr))
                if best is None or fa < best["fa"]:
                    best = {"n": n, "thr": thr, "fa": fa}
            if best is None:
                continue
            d = slow_deviation(y[c:], op[c:], fp, best["n"])
            k = int(np.argmax(d > best["thr"])) if (d is not None and (d > best["thr"]).any()) else None
            rest = (len(d) - k) / len(d) if (k is not None and d is not None) else 0.0
            if passes_cv:
                survived.add(nm)
                if k is not None:
                    fired.setdefault(nm, set()).add(dev)
            print(f"{dev:>10} {nm:>16} {shift:>14.2f} {best['fa']:>11.5f} "
                  f"{best['fa']/design:>7.1f}倍 "
                  f"{(str(k) if k is not None else '—'):>8} "
                  f"{(f'{rest:.0%}' if k is not None else '—'):>8}"
                  f"{'' if passes_cv else '  (交差検証で除外)'}")
            rows.append({"device": dev, "obs": nm, "shift": shift,
                         "fa": best["fa"], "first": k, "rest": rest,
                         "cv": int(passes_cv)})

    print(f"\n=== I1 交差検証を通る観測量 ===")
    print(f"  {len(survived)}/{len(NAMES)}  {'PASS' if survived else 'FAIL'} (基準 1つ以上)")
    print(f"  {', '.join(sorted(survived)) if survived else 'なし'}")

    print(f"\n=== I2 通った観測量で、故障前に発火する素子 ===")
    n_dev = len(devs)
    best_obs, best_n = None, 0
    for nm in sorted(survived):
        c = len(fired.get(nm, set()))
        print(f"  {nm:>16}: {c}/{n_dev}")
        if c > best_n:
            best_obs, best_n = nm, c
    print(f"  最良 {best_obs}: {best_n}/{n_dev}  "
          f"{'PASS' if best_n > n_dev / 2 else 'FAIL'} (基準 過半)")

    print(f"\n=== I3 指紋区間での誤報 ===")
    fas = [r["fa"] for r in rows if r["cv"]]
    if fas:
        w = max(fas) / design
        print(f"  最悪 {w:.1f}倍  {'PASS' if w <= 3 else 'FAIL'} (基準 3倍以内)")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("device\tobservable\tcv_shift_floors\tfalse_alarm\tfirst_fire\t"
                 "rest_frac\tpassed_cv\n")
        for r in rows:
            fh.write(f"{r['device']}\t{r['obs']}\t{r['shift']:.4f}\t{r['fa']:.6f}\t"
                     f"{'' if r['first'] is None else r['first']}\t"
                     f"{r['rest']:.4f}\t{r['cv']}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
