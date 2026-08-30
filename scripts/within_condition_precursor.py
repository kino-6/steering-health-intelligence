#!/usr/bin/env python3
"""Degradation with the stress ramp removed (docs/236 -> docs/237).

Executes the protocol pre-registered in docs/236 without modification.

docs/234 found the observables following the rig's own ramp -- supply 2.5 to
6.0 V, setpoint 100 to 280 C. Holding the operating point fixed and looking at
what remains is the last thing this dataset can be asked.

Group selection is by a rule independent of the outcome: for each device, the
(supply, setpoint) combination carrying the MOST transients, minimum 18.
Observables are unchanged from docs/233. Groups may jump in time; that is a
same-condition, different-time comparison and the intervening history stays in
the device, which docs/236 concedes.

These are setpoints, not measurements: every steadyState channel is NaN, so
two records at one setpoint need not have been at one temperature.

Data: NASA PCoE, IGBT Accelerated Aging, public domain.
"""

from __future__ import annotations

import glob
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import scipy.io as sio

sys.path.insert(0, str(Path(__file__).resolve().parent))
from igbt_switching_precursor import BASE, ensure_extracted, features, parse_date, ROBUST
from lib_discipline import passes, spearman_exact

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "within_condition_precursor.tsv"

MIN_GROUP = 18          # docs/236, fixed
BASE_FRAC = 0.30        # docs/236, fixed
NAMES = ["turn-on delay [ns]", "conduction Vce [V]", "gate plateau [V]"]


def main() -> None:
    ensure_extracted()
    devices = sorted({os.path.basename(os.path.dirname(f))
                      for f in glob.glob(str(BASE / "Device */*.mat"))})
    rows, summary = [], {}
    for dev in devices:
        states, recs = [], []
        for f in sorted(glob.glob(str(BASE / dev / "*.mat"))):
            if "check" in os.path.basename(f):
                continue
            m = sio.loadmat(f, squeeze_me=True, struct_as_record=False)["measurement"]
            for r in np.ravel(m.pwmTempControllerState):
                t = parse_date(r.time)
                if t:
                    states.append((t, float(r.supplyVoltage), float(r.highTemp)))
            for r in np.ravel(m.transient):
                try:
                    t = parse_date(r.date)
                    v = features(r.timeDomain)
                except Exception:
                    continue
                if t and v:
                    recs.append((t, *v))
        states.sort()
        recs.sort(key=lambda x: x[0])

        def cond(t):
            prev = [s for s in states if s[0] <= t]
            return prev[-1][1:] if prev else None

        tagged = [(t, c, a, b, c2) for (t, a, b, c2) in recs
                  if (c := cond(t)) is not None]
        counts = Counter(c for _, c, *_ in tagged)
        if not counts:
            print(f"{dev}: no condition could be assigned -- not evaluable")
            summary[dev] = None
            continue
        best, n = counts.most_common(1)[0]
        if n < MIN_GROUP:
            print(f"{dev}: largest group has {n} < {MIN_GROUP} -- not evaluable")
            summary[dev] = None
            continue
        grp = [r for r in tagged if r[1] == best]
        arr = np.array([[r[2] * 1e9, r[3], r[4]] for r in grp], dtype=float)
        n0 = max(4, int(len(arr) * BASE_FRAC))
        span = f"{grp[0][0]:%H:%M}..{grp[-1][0]:%H:%M}"
        print(f"\n{dev}   condition supply={best[0]} V, setpoint={best[1]} C   "
              f"n={len(arr)}  {span}")
        print(f"{'observable':<22}{'baseline':>12}{'final 30%':>12}{'3sd':>10}"
              f"{'margin':>9}{'rho':>8}")
        res = {}
        for j, nm in enumerate(NAMES):
            col = arr[:, j]
            ok = np.isfinite(col)
            if ok.sum() < MIN_GROUP:
                print(f"{nm:<22}   not extractable")
                continue
            c = col[ok]
            b, f = c[:n0], c[-n0:]
            b0, f0 = float(np.median(b)), float(np.median(f))
            sd = float(ROBUST * np.median(np.abs(b - np.median(b))))
            margin = abs(f0 - b0) / sd if sd > 0 else float("nan")
            rho = float(spearman_exact(np.arange(c.size), c))
            print(f"{nm:<22}{b0:>12.4f}{f0:>12.4f}{sd:>10.4f}{margin:>8.1f}x{rho:>+8.3f}")
            res[nm] = dict(rho=rho, margin=margin)
            rows.append((dev, f"{best[0]}V/{best[1]}C", nm, len(c), b0, f0, sd, margin, rho))
        summary[dev] = res

    ev = {d: r for d, r in summary.items() if r}
    print("\n" + "=" * 76)
    print(f"evaluable devices: {len(ev)}/{len(summary)}")
    hit = {}
    for nm in NAMES:
        h = [d for d, r in ev.items() if nm in r and passes(abs(r[nm]["rho"]), 0.8)]
        hit[nm] = h
        print(f"J1  {nm:<22} monotone in {len(h)}/{len(ev)}  {h}")
    best_n = max((len(v) for v in hit.values()), default=0)
    ok = best_n >= 3
    print(f"\nJ1 -> {'PASS' if ok else 'FAIL'} (needs 3 of the evaluable devices)")
    if not ok:
        print("   docs/236 fixed the conclusion in advance: with the stress ramp removed")
        print("   the observables still do not move, so no precursor can be extracted")
        print("   from this dataset.")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("device\tcondition\tobservable\tn\tbaseline\tfinal\tbaseline_3sd\t"
                "margin\trho\n")
        for r in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
