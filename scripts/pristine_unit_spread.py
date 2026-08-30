#!/usr/bin/env python3
"""How far do PRISTINE parts differ? (docs/231 -> docs/232)

Executes the protocol pre-registered in docs/231 without modification.

The one methodological claim still standing in this work is that a baseline
must be per unit. Its support so far is indirect: a population threshold
firing on a healthy device (docs/193) and measurement-campaign steps swamping
fault effects (docs/203). This measures the thing directly, on 40 real parts
that have not been degraded at all -- 20 MOSFET IRF520Npbf and 20 IGBT
IRG4BC30K, characterised for threshold, breakdown and leakage.

    S = 1.4826 * MAD of the extracted value across the 20 parts of a family
    R = the measurement's own uncertainty on that value, from the local
        scatter of the I-V curve propagated through the local slope
    S / R = how many measurement widths apart brand-new parts already sit

A population threshold has to straddle S. So the larger S/R is, the smaller
the degradation a population threshold can never see, and S/R is exactly what
a per-unit baseline recovers.

Extraction points are set by the sweep design, not by the results: threshold
at the 250 uA compliance both families reach, breakdown at the largest current
every part in the family reaches, leakage at the highest voltage every part in
the family reaches. Nothing here is chosen after seeing a spread.

The pristine parts are not degraded, so this measures SPREAD, not a precursor.

Data: NASA PCoE, IGBT Accelerated Aging, public domain.
"""

from __future__ import annotations

import re
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
ZIP = REPO_ROOT / ".nasa_igbt" / "8. IGBT Accelerated Aging" / "IGBTAgingData_04022009.zip"
OUT_TSV = REPO_ROOT / "data" / "pristine_unit_spread.tsv"

VTH_LEVEL = 250e-6          # the compliance both families' Turn On sweeps reach
WIN = 10                    # points either side, for the local fit
ROBUST = 1.4826


def load(z, name):
    a = []
    for line in z.read(name).decode("latin-1").splitlines():
        p = line.split(",")
        if len(p) == 2:
            try:
                a.append((float(p[0]), float(p[1])))
            except ValueError:
                pass
    return np.array(a)


def v_at_current(d, level):
    """Voltage where |I| first reaches `level`, plus the measurement's own
    uncertainty on that voltage: local scatter of log10|I| about a straight
    fit, divided by the local slope."""
    v, i = d[:, 0], np.abs(d[:, 1])
    idx = np.flatnonzero(i >= level)
    if idx.size == 0:
        return None, None
    k = int(idx[0])
    lo, hi = max(0, k - WIN), min(len(v), k + WIN + 1)
    vv, ii = v[lo:hi], i[lo:hi]
    good = ii > 0
    if good.sum() < 4:
        return float(v[k]), None
    li = np.log10(ii[good])
    slope, inter = np.polyfit(vv[good], li, 1)
    resid = li - (slope * vv[good] + inter)
    if abs(slope) < 1e-12:
        return float(v[k]), None
    return float(v[k]), float(np.std(resid, ddof=1) / abs(slope))


def i_at_voltage(d, volt):
    """log10 of |I| at `volt`, and the local residual scatter in log10 units."""
    v, i = d[:, 0], np.abs(d[:, 1])
    k = int(np.argmin(np.abs(v - volt)))
    lo, hi = max(0, k - WIN), min(len(v), k + WIN + 1)
    vv, ii = v[lo:hi], i[lo:hi]
    good = ii > 0
    if good.sum() < 4 or i[k] <= 0:
        return None, None
    li = np.log10(ii[good])
    slope, inter = np.polyfit(vv[good], li, 1)
    resid = li - (slope * vv[good] + inter)
    return float(np.log10(i[k])), float(np.std(resid, ddof=1))


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    files = defaultdict(dict)
    for n in z.namelist():
        m = re.search(r"new devices/([^/]+)/Part ([^/]+)/(Turn On|LeakageIV|Breakdown)\.csv$", n)
        if m:
            files[(m.group(1), m.group(2))][m.group(3)] = n

    fams = sorted({k[0] for k in files})
    rows = []
    for fam in fams:
        parts = sorted(k[1] for k in files if k[0] == fam)
        curves = {p: {k: load(z, v) for k, v in files[(fam, p)].items()} for p in parts}

        # extraction points fixed by the sweep design, before any spread is seen
        br_level = min(np.abs(curves[p]["Breakdown"][:, 1]).max() for p in parts)
        lk_volt = min(curves[p]["LeakageIV"][:, 0].max() for p in parts)
        print(f"\n{'='*74}\n{fam}   {len(parts)} pristine parts")
        print(f"  extraction: Vth at {VTH_LEVEL*1e6:.0f} uA, "
              f"breakdown at {br_level*1e6:.2f} uA, leakage at {lk_volt:.1f} V")

        specs = [("threshold V", "Turn On", lambda d: v_at_current(d, VTH_LEVEL), "V"),
                 ("breakdown V", "Breakdown", lambda d: v_at_current(d, br_level), "V"),
                 ("leakage log10 A", "LeakageIV", lambda d: i_at_voltage(d, lk_volt), "dec")]
        for label, kind, fn, unit in specs:
            vals, uncs = [], []
            for p in parts:
                val, unc = fn(curves[p][kind])
                if val is not None:
                    vals.append(val)
                    if unc is not None and unc > 0:
                        uncs.append(unc)
            if len(vals) < 5 or not uncs:
                print(f"  {label:<16} not extractable")
                continue
            vals = np.array(vals)
            S = float(ROBUST * np.median(np.abs(vals - np.median(vals))))
            R = float(np.median(uncs))
            ratio = S / R if R > 0 else float("nan")
            print(f"  {label:<16} n={len(vals):2d}  median {np.median(vals):10.4f} {unit}"
                  f"   S={S:.5f}  R={R:.5f}   S/R = {ratio:6.1f}"
                  f"   span {vals.min():.4f}..{vals.max():.4f}")
            rows.append((fam, label, len(vals), float(np.median(vals)), S, R, ratio,
                         float(vals.min()), float(vals.max())))

    print(f"\n{'='*74}")
    big = [r for r in rows if r[6] >= 3.0]
    print(f"G2  parameters with S/R >= 3 : {len(big)}/{len(rows)}")
    for r in rows:
        mark = "  <-- population threshold cannot see below this" if r[6] >= 3 else ""
        print(f"    {r[0]:<20}{r[1]:<16} S/R = {r[6]:7.1f}{mark}")
    if rows:
        print(f"\nG3  a per-unit baseline recovers a factor of "
              f"{min(r[6] for r in rows):.1f} to {max(r[6] for r in rows):.1f}")
    print("\nThese parts are pristine. This is SPREAD, not a precursor, and a large")
    print("S/R says a population threshold is handicapped -- not that a per-unit one detects.")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("family\tparameter\tn\tmedian\tS_unit_spread\tR_meas_noise\tS_over_R\tmin\tmax\n")
        for r in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
