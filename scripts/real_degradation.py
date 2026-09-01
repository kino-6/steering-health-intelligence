#!/usr/bin/env python3
"""Does the recorder fire on real ageing, not on injections? (docs/268 -> docs/269)

Executes the protocol pre-registered in docs/268. The recorder is
scripts/element_v2.py, used unchanged.

Every detection figure in this repo so far came from adding a rectangle to a
healthy signal and asking whether the detector saw it. docs/167 measured how
large real precursors are but never ran the recorder over the ageing record
itself. Nothing here is injected: the devices degraded, the rig recorded them,
and the failures happened.

    R1  does it fire before the record ends, on five of six devices
    R2  how many times it fires during the healthy stretch first
    R3  the smallest real fault severity that fires, across three machines
    R4  how much of the record remains after the first firing
    R5  what is lost by replacing the unit's own fingerprint with the fleet's

Data: NASA PCoE MOSFET (public domain), KAIST PMSM (CC BY 4.0).
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

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "real_degradation.tsv"

FP_FRAC = 0.5           # the fingerprint is the first half of run 1, docs/268
WIN = el.WIN


def device_series(dev):
    z = zipfile.ZipFile(mos.ZIP) if hasattr(mos, "ZIP") else None
    y, t, run_of = [], [], []
    for r in (1, 2, 3):
        ron, tp = mos.read_run(z, dev, r)
        y.append(np.asarray(ron))
        t.append(np.asarray(tp))
        run_of.append(np.full(len(ron), r))
    return np.concatenate(y), np.concatenate(t), np.concatenate(run_of)


def first_fire(recs):
    for i, r in enumerate(recs):
        if r.flags:
            return i
    return None


def main() -> None:
    print("=== R1/R2/R4  半導体6素子。注入なし ===")
    print(f"{'素子':>9} {'窓':>6} {'指紋後の窓':>11} {'初発火':>8} "
          f"{'それまでの発火':>13} {'残り':>9}")
    print("-" * 66)

    rows, fired, lead, fa = [], 0, [], []
    fps, runtimes = {}, {}
    for dev in mos.DEVICES:
        y, t, run_of = device_series(dev)
        n1 = int((run_of == 1).sum())
        cut = int(n1 * FP_FRAC)
        fp = el.take_fingerprint(y[:cut], t[:cut])
        yr, tr = y[cut:], t[cut:]
        fps[f"Test_{dev}"] = fp
        runtimes[f"Test_{dev}"] = (yr, tr)
        recs = el.run(yr, tr, fp)
        k = first_fire(recs)
        nwin = len(recs)
        rest = (nwin - k) / nwin if k is not None else 0.0
        pre = k if k is not None else nwin      # firings before the first one: none by definition
        # R2 counts firings inside the healthy stretch, taken as the first
        # quarter of the runtime -- the device is least degraded there
        healthy = max(1, nwin // 4)
        false_alarms = sum(1 for r in recs[:healthy] if r.flags)
        if k is not None:
            fired += 1
            lead.append(rest)
        fa.append(false_alarms / healthy)
        print(f"{dev:>9} {nwin:>6} {nwin:>11} "
              f"{(str(k) if k is not None else '鳴らず'):>8} "
              f"{false_alarms:>13} {(f'{rest:.0%}' if k is not None else '—'):>9}")
        rows.append({"kind": "R1", "unit": f"Test_{dev}", "windows": nwin,
                     "first_fire": k, "false_alarms": false_alarms,
                     "healthy_windows": healthy, "rest_frac": rest})

    print(f"\n=== R1 故障前に発火した素子 ===")
    print(f"  {fired}/{len(mos.DEVICES)}  {'PASS' if fired >= 5 else 'FAIL'} (基準: 6中5)")

    # one alarm per hour at 10 Hz is one per 36000 samples = one per 720 windows
    design = WIN / 36000.0
    obs = float(np.mean(fa))
    print(f"\n=== R2 健全区間での誤報 ===")
    print(f"  設計値 {design:.5f} /窓 (1件/時)   実測 {obs:.5f} /窓")
    print(f"  比 {obs/design if design else float('inf'):.1f}倍  "
          f"{'PASS' if obs <= design * 3 else 'FAIL'} (基準: 3倍以内)")

    print(f"\n=== R4 初発火から記録の最後までの残り ===")
    if lead:
        print(f"  中央値 {np.median(lead):.0%}  範囲 {min(lead):.0%}〜{max(lead):.0%}  "
              f"{'PASS' if np.median(lead) >= 0.10 else 'FAIL'} (基準: 10%以上)")

    # ---- R3 real fault severities ---------------------------------------
    print(f"\n=== R3 モータの実故障重症度。3機体 ===")
    print(f"{'機体':>8} {'指紋(重症度0)':>14} {'最初に発火した重症度':>22}")
    print("-" * 48)
    sev_fire = {}
    for zp in sorted(sig.ZIP.parent.glob("*.zip")):
        z = zipfile.ZipFile(zp)
        cur = [n for n in z.namelist() if "current" in n]
        def sev(n):
            m = re.search(r"W_(\d+)[_.](\d+)_current", n.split("/")[-1])
            return float(f"{m.group(1)}.{m.group(2)}") if m else None
        healthy = [n for n in cur if sev(n) == 0.0]
        faulty = sorted([n for n in cur if sev(n) not in (None, 0.0)], key=sev)
        if not healthy or not faulty:
            continue
        def hs(name):
            p = sig.CACHE / name
            if not p.exists():
                z.extract(name, sig.CACHE)
            ph = sig.load_phases(p)
            f0 = sig.find_f0(ph)
            n = len(ph[0]) // el.WIN
            return np.array([headroom([x[i*n:(i+1)*n] for x in ph], f0)
                             for i in range(el.WIN)])
        h0 = hs(healthy[0])
        op0 = np.arange(len(h0), dtype=float)
        fp = el.take_fingerprint(h0, op0)
        hit = None
        for name in faulty:
            h = hs(name)
            d = np.abs(h - (fp.slope * op0[:len(h)] + fp.intercept)) / fp.floor
            if float(np.max(d)) > el.FIRE:
                hit = sev(name)
                break
        sev_fire[zp.stem] = hit
        print(f"{zp.stem:>8} {len(h0):>14} "
              f"{(f'{hit}%' if hit is not None else '全重症度で鳴らず'):>22}")
        rows.append({"kind": "R3", "unit": zp.stem, "windows": len(h0),
                     "first_fire": hit, "false_alarms": 0,
                     "healthy_windows": 0, "rest_frac": 0})
    vals = [v for v in sev_fire.values() if v]
    if len(vals) >= 2:
        print(f"  最小 {min(vals)}  最大 {max(vals)}  比 {max(vals)/min(vals):.1f}倍  "
              f"{'PASS' if max(vals)/min(vals) <= 2 else 'FAIL'} (基準: 2倍以内)")
    else:
        print(f"  比較できる機体が {len(vals)} しかない  FAIL")

    # ---- R5 fleet fingerprint instead of the unit's own -------------------
    print(f"\n=== R5 母集団基準に差し替えると ===")
    med = el.Fingerprint(
        float(np.median([f.slope for f in fps.values()])),
        float(np.median([f.intercept for f in fps.values()])),
        float(np.median([f.ref_op for f in fps.values()])),
        float(np.median([f.op_lo for f in fps.values()])),
        float(np.median([f.op_hi for f in fps.values()])),
        float(np.median([f.floor for f in fps.values()])),
        float(np.median([f.op_scale for f in fps.values()])), 2.0)
    fa_pop, late = [], 0
    for name, (yr, tr) in runtimes.items():
        recs = el.run(yr, tr, med)
        nwin = len(recs)
        healthy = max(1, nwin // 4)
        fa_pop.append(sum(1 for r in recs[:healthy] if r.flags) / healthy)
        own = first_fire(el.run(yr, tr, fps[name]))
        pop = first_fire(recs)
        if own is not None and (pop is None or pop > own):
            late += 1
    obs_pop = float(np.mean(fa_pop))
    print(f"  誤報 個体基準 {obs:.5f} /窓 → 母集団基準 {obs_pop:.5f} /窓  "
          f"{obs_pop/obs if obs else float('inf'):.1f}倍")
    print(f"  発火が遅れた素子 {late}/{len(runtimes)}")
    worse = (obs and obs_pop >= obs * 2) or late > 0
    print(f"  {'PASS' if worse else 'FAIL'} (基準: 誤報2倍以上 または 発火が遅れる)")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("kind\tunit\twindows\tfirst_fire\tfalse_alarms\thealthy_windows\trest_frac\n")
        for r in rows:
            fh.write(f"{r['kind']}\t{r['unit']}\t{r['windows']}\t{r['first_fire']}\t"
                     f"{r['false_alarms']}\t{r['healthy_windows']}\t{r['rest_frac']:.4f}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
