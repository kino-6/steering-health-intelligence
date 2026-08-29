#!/usr/bin/env python3
"""Does instability move before the level does? (docs/210 -> docs/211)

Executes the protocol pre-registered in docs/210 without modification.

Every document from docs/165 on collapsed each run to a median. An
intermittent fault is physically instability -- a marginal contact scatters
before its mean moves -- and the NASA set holds 5,191 to 18,351 steady records
per run whose spread has never been looked at.

    residual   r_k = R_on,k - (a * T_pkg,k + b)   a, b fitted on runs 1-3
    level      L   = median(r_k)                  what has been used so far
    dispersion V   = MAD(r_k) / median(R_on,k)    what has not

Dispersion is taken on the temperature-normalised residual, since raw scatter
carries the within-run temperature swing, and with a median absolute deviation
because the record count per run varies more than threefold.

Data: NASA PCoE MOSFET thermal overstress ageing, public domain.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
from scipy import stats

import mosfet_precursor as mos
from lib_discipline import passes, spearman_exact

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "instability_precursor.tsv"
FIT_RUNS = (1, 2, 3)
NEVER = mos.N_RUNS + 1


def fire(series: dict[int, float], base: float, sd: float) -> int:
    """First run whose value exceeds baseline + 3 sd."""
    thr = base + 3.0 * sd
    for r in range(1, mos.N_RUNS + 1):
        if passes(series[r], thr, ">"):
            return r
    return NEVER


def main() -> None:
    z = zipfile.ZipFile(mos.ZIP)
    rows, summary = [], {}
    for dev in mos.DEVICES:
        raw = {}
        for run in range(1, mos.N_RUNS + 1):
            ron, tpkg = mos.read_run(z, dev, run)
            raw[run] = (np.asarray(ron), np.asarray(tpkg))

        # per-unit temperature model on the healthy window
        T = np.array([np.median(raw[r][1]) for r in FIT_RUNS])
        R = np.array([np.median(raw[r][0]) for r in FIT_RUNS])
        a, b = np.polyfit(T, R, 1)

        level, disp, n_rec = {}, {}, {}
        for run in range(1, mos.N_RUNS + 1):
            ron, tp = raw[run]
            r_k = ron - (a * tp + b)
            med = float(np.median(ron))
            level[run] = float(np.median(r_k))
            disp[run] = float(np.median(np.abs(r_k - np.median(r_k))) / med)
            n_rec[run] = len(ron)

        lb = np.array([level[r] for r in FIT_RUNS])
        vb = np.array([disp[r] for r in FIT_RUNS])
        # level is signed; the question is departure from baseline either way
        labs = {r: abs(level[r] - lb.mean()) for r in level}
        f_L = fire(labs, 0.0, float(lb.std(ddof=1)))
        f_V = fire(disp, float(vb.mean()), float(vb.std(ddof=1)))
        rho = float(spearman_exact(list(range(1, mos.N_RUNS + 1)),
                                   [disp[r] for r in range(1, mos.N_RUNS + 1)]))

        print(f"--- Test_{dev}   a = {a:.5f} ohm/degC")
        print(f"{'run':>5}{'records':>9}{'level dev':>12}{'dispersion':>13}"
              f"{'L/base':>9}{'V/base':>9}")
        for run in range(1, mos.N_RUNS + 1):
            print(f"{run:>5}{n_rec[run]:>9,}{labs[run]:>12.5f}{disp[run]:>13.5f}"
                  f"{labs[run]/(3*lb.std(ddof=1)):>9.2f}{disp[run]/vb.mean():>9.2f}")
            rows.append((dev, run, n_rec[run], level[run], labs[run], disp[run],
                         f_L, f_V))
        f = lambda x: "never" if x > mos.N_RUNS else f"run {x}"
        print(f"      level fires {f(f_L):<7}   dispersion fires {f(f_V):<7}   "
              f"rho(run, V) = {rho:+.3f}\n")
        summary[dev] = dict(f_L=f_L, f_V=f_V, rho=rho)

    print("=" * 74)
    d1 = sum(passes(s["rho"], 0.8) for s in summary.values())
    d2 = sum(s["f_V"] <= s["f_L"] for s in summary.values())
    d2b = sum(s["f_V"] < s["f_L"] for s in summary.values())
    for dev, s in summary.items():
        f = lambda x: "never" if x > mos.N_RUNS else str(x)
        print(f"  Test_{dev}  rho={s['rho']:+.3f}  level@{f(s['f_L']):<5} "
              f"dispersion@{f(s['f_V']):<5} "
              f"{'earlier' if s['f_V'] < s['f_L'] else ('same' if s['f_V'] == s['f_L'] else 'later')}")
    print(f"\nD1  dispersion rises, rho >= 0.8      : {d1}/6 -> "
          f"{'PASS' if d1 >= 4 else 'FAIL'} (needs 4)")
    print(f"D2  dispersion fires no later than level: {d2}/6 -> "
          f"{'PASS' if d2 >= 4 else 'FAIL'} (needs 4)")
    print(f"D2b dispersion fires strictly earlier   : {d2b}/6 -> "
          f"{'PASS' if d2b >= 3 else 'FAIL'} (needs 3)")
    if d2 >= 4 and d2b < 3:
        print("    -> simultaneous, not leading. docs/210 forbids reading a tie as a lead.")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("device\trun\tn_records\tlevel_residual\tlevel_deviation\t"
                  "dispersion\tlevel_fire_run\tdispersion_fire_run\n")
        for r in rows:
            out.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                                for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
