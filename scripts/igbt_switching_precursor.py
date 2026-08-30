#!/usr/bin/env python3
"""Do switching observables move as an IGBT ages? (docs/233 -> docs/234)

Executes the protocol pre-registered in docs/233 without modification.

docs/231 discarded this folder on a readme warning aimed at collector current
and the steady-state channels. Counting the transients shows about 690
captures across four devices, all populated, 125,000 points each at 8 ns,
timestamped through aging, switching at 1 kHz with temperature HELD at 99-100 C
rather than swept. That is the operating mode docs/199 found absent from S8.

Worse than the readme in one place, and checked rather than assumed: every
steadyState channel is NaN, so temperature cannot be measured and docs/167's
normalisation is impossible here. Collector current is not used either.

So observables are voltage and time only:

    A  turn-on delay      gate signal 50% crossing -> collector-emitter
                          through 50% of its swing. A TIME, so voltage
                          scaling error cannot touch it, and it lengthens
                          when threshold voltage rises -- the precursor the
                          distributor's own paper names.
    B  conduction V_ce    median over the on-window, away from the edges
    C  gate plateau       the Miller plateau level in gate-emitter voltage

Data: NASA PCoE, IGBT Accelerated Aging, public domain.
"""

from __future__ import annotations

import glob
import os
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import scipy.io as sio
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = (REPO_ROOT / ".nasa_igbt" / "IGBTAgingData_04022009" / "Data" /
        "Thermal Overstress Aging with Square Signal at gate and SMU data" / "Aging Data")
OUT_TSV = REPO_ROOT / "data" / "igbt_switching_precursor.tsv"

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_discipline import passes, spearman_exact

BASE_FRAC = 0.20        # docs/233: first 20% is the per-unit baseline
ROBUST = 3.0 * 1.4826


def parse_date(s: str):
    m = re.match(r"(\d+)/(\d+)/(\d+)\s+(\d+):(\d+):(\d+)", str(s))
    if not m:
        return None
    mo, da, yr, h, mi, se = (int(x) for x in m.groups())
    ampm = "PM" in str(s).upper() and h < 12
    return datetime(yr, mo, da, h + (12 if ampm else 0), mi, se)


def features(td):
    """A: turn-on delay [s], B: conduction V_ce [V], C: gate plateau [V]."""
    dt = float(np.ravel(td.dt)[0])
    gs = np.ravel(td.gateSignalVoltage).astype(float)
    ge = np.ravel(td.gateEmitterVoltage).astype(float)
    ce = np.ravel(td.collectorEmitterVoltage).astype(float)
    if gs.size < 1000:
        return None
    g_thr = (gs.max() + gs.min()) / 2.0
    edges = np.flatnonzero((gs[:-1] < g_thr) & (gs[1:] >= g_thr))
    if edges.size == 0:
        return None
    e = int(edges[0])
    lo, hi = np.percentile(ce, 5), np.percentile(ce, 95)
    c_thr = (lo + hi) / 2.0
    after = ce[e:]
    below = np.flatnonzero(after <= c_thr)
    if below.size == 0:
        return None
    delay = float(below[0] * dt)
    # conduction window: from 20% to 80% of the interval between this edge and
    # the next falling edge of the gate signal, so the switching edges are out
    fall = np.flatnonzero((gs[e:-1] >= g_thr) & (gs[e + 1:] < g_thr))
    end = e + int(fall[0]) if fall.size else len(ce)
    a, b = e + int((end - e) * 0.2), e + int((end - e) * 0.8)
    if b - a < 50:
        return None
    vce = float(np.median(ce[a:b]))
    # Miller plateau: the flattest stretch of gate-emitter voltage during the
    # rise, taken as the median of ge over the 10-90% of the turn-on interval
    w = ge[e:e + max(int(delay / dt) * 3, 200)]
    plateau = float(np.median(w[int(len(w) * 0.1):int(len(w) * 0.9)])) if w.size > 20 else float("nan")
    return delay, vce, plateau


def main() -> None:
    devices = sorted({os.path.basename(os.path.dirname(f))
                      for f in glob.glob(str(BASE / "Device */*.mat"))})
    names = ["turn-on delay [ns]", "conduction Vce [V]", "gate plateau [V]"]
    rows, summary = [], {}
    for dev in devices:
        recs = []
        for f in sorted(glob.glob(str(BASE / dev / "*.mat"))):
            if "check" in os.path.basename(f):
                continue                       # not described in the readme
            m = sio.loadmat(f, squeeze_me=True, struct_as_record=False)["measurement"]
            for r in np.ravel(m.transient):
                try:
                    t = parse_date(r.date)
                    v = features(r.timeDomain)
                except Exception:
                    continue
                if t and v:
                    recs.append((t, *v))
        if len(recs) < 20:
            print(f"{dev}: only {len(recs)} usable transients -- skipped")
            continue
        recs.sort(key=lambda x: x[0])
        arr = np.array([[r[1] * 1e9, r[2], r[3]] for r in recs], dtype=float)
        n0 = max(5, int(len(arr) * BASE_FRAC))
        print(f"\n{dev}   {len(arr)} transients, "
              f"{recs[0][0]:%H:%M} .. {recs[-1][0]:%H:%M}   baseline = first {n0}")
        print(f"{'observable':<22}{'baseline':>12}{'final 20%':>12}{'3sd':>10}"
              f"{'margin':>9}{'rho':>8}")
        res = {}
        for j, nm in enumerate(names):
            col = arr[:, j]
            if not np.isfinite(col).all():
                col = np.where(np.isfinite(col), col, np.nan)
            base = col[:n0]
            base = base[np.isfinite(base)]
            fin = col[-n0:]
            fin = fin[np.isfinite(fin)]
            if base.size < 5 or fin.size < 5:
                print(f"{nm:<22}   not extractable")
                continue
            b0 = float(np.median(base))
            sd = float(ROBUST * np.median(np.abs(base - np.median(base))))
            f0 = float(np.median(fin))
            margin = abs(f0 - b0) / sd if sd > 0 else float("nan")
            ok = np.isfinite(col)
            rho = float(spearman_exact(np.arange(ok.sum()), col[ok]))
            print(f"{nm:<22}{b0:>12.4f}{f0:>12.4f}{sd:>10.4f}{margin:>8.1f}x{rho:>+8.3f}")
            res[nm] = dict(base=b0, final=f0, sd=sd, margin=margin, rho=rho)
            rows.append((dev, nm, len(arr), b0, f0, sd, margin, rho))
        summary[dev] = res

    print("\n" + "=" * 76)
    h1 = {}
    for nm in names:
        hits = [d for d, r in summary.items()
                if nm in r and passes(abs(r[nm]["rho"]), 0.8)]
        h1[nm] = hits
        print(f"H1  {nm:<22} monotone in {len(hits)}/{len(summary)}  {hits}")
    best = max(h1, key=lambda k: len(h1[k]))
    ok = len(h1[best]) >= 3
    print(f"\nH1 -> {'PASS' if ok else 'FAIL'}: "
          f"{'at least one observable moves in 3 of 4' if ok else 'no observable moves in 3 of 4'}")
    print("\nH2  which observable crosses its baseline 3sd first, per device:")
    for d, r in summary.items():
        crossed = [(nm, r[nm]["margin"]) for nm in names if nm in r and r[nm]["margin"] > 1]
        crossed.sort(key=lambda x: -x[1])
        print(f"   {d:<10} " + (", ".join(f"{n} ({m:.1f}x)" for n, m in crossed)
                                if crossed else "none crosses its baseline scatter"))

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("device\tobservable\tn\tbaseline\tfinal\tbaseline_3sd\tmargin\trho\n")
        for r in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")
    print("No temperature measurement exists here (all steadyState channels are NaN),")
    print("so any thermal drift is inside these numbers and cannot be separated.")


if __name__ == "__main__":
    main()
