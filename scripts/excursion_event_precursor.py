#!/usr/bin/env python3
"""Count excursions instead of averaging them (docs/240 -> docs/241).

Executes the protocol pre-registered in docs/240 without modification.

docs/174 measured a window median and a window IQR on this same dataset and
found essentially nothing. Both statistics destroy what an intermittent fault
looks like: each unit holds 24,000 to 34,000 readings and the excursions sit
in the top 0.1 percent.

Two outside sources set the shape. The connector literature says continuous
high-rate monitoring shows intermittent high-resistance events before the mean
moves, and IPC-9701 defines solder-joint failure by an event detector counting
interruptions rather than by average resistance. Excursions get counted.

Only the observable changes. Same dataset, same unit filter, same ten windows.

    threshold T = median(first 20%) + 6 * 1.4826 * MAD(first 20%)
    E(w)        = share of readings above T in window w
    L(w)        = median of window w              (docs/174's level, unchanged)

SOReDD ends in sticking, not in rising resistance, so more excursions would
not by itself make them a precursor of that ending.

Data: SOReDD, University of Stuttgart, CC BY 4.0.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contact_variance_lead import CACHE, N_WIN, UNPARSEABLE, load
from lib_discipline import passes, spearman_exact

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "excursion_event_precursor.tsv"

BASE_FRAC = 0.20          # docs/240
K_SIGMA = 6.0             # docs/240, deliberately strict, not tuned
E_FIRE = 3.0              # excursion rate above 3x its baseline
L_FIRE = 1.1              # level above 1.1x its baseline (docs/173)
ROBUST = 1.4826


def first_over(x, ratio, base):
    """1-based window index where x first exceeds ratio * base; None if never."""
    if base is None or base <= 0 or not np.isfinite(base):
        return None
    for i in range(1, len(x)):
        if np.isfinite(x[i]) and x[i] / base > ratio:
            return i + 1
    return None


def main() -> None:
    rows = []
    for p in sorted(CACHE.glob("*.json")):
        out = load(p)
        if out is None:
            continue
        m, r = out
        n0 = max(20, int(len(r) * BASE_FRAC))
        base = r[:n0]
        thr = float(np.median(base) + K_SIGMA * ROBUST *
                    np.median(np.abs(base - np.median(base))))
        edges = np.linspace(0, len(r), N_WIN + 1).astype(int)
        E, L = [], []
        for i in range(N_WIN):
            seg = r[edges[i]:edges[i + 1]]
            E.append(float(np.mean(seg > thr)) if seg.size else float("nan"))
            L.append(float(np.median(seg)) if seg.size else float("nan"))
        E, L = np.array(E), np.array(L)
        # the baseline window's own rate; a zero baseline rate cannot be scaled,
        # so it is replaced by the smallest resolvable rate in that window
        e0 = E[0] if E[0] > 0 else 1.0 / max(1, edges[1] - edges[0])
        rho = float(spearman_exact(np.arange(N_WIN), E)) if np.isfinite(E).all() else float("nan")
        kE = first_over(E, E_FIRE, e0)
        kL = first_over(L, L_FIRE, L[0])
        rows.append(dict(unit=p.stem, event=m.get("lastEvent"), n=len(r),
                         thr=thr, med=float(np.median(r)), rho=rho,
                         e_max=float(np.nanmax(E)), e0=float(e0),
                         kE=kE, kL=kL))

    if UNPARSEABLE:
        print(f"unreadable files skipped: {len(UNPARSEABLE)} {UNPARSEABLE[:4]}")
    print(f"\nunits analysed: {len(rows)}")
    print(f"{'unit':<7}{'end':<14}{'n':>7}{'median':>8}{'thr':>8}"
          f"{'E0':>9}{'Emax':>9}{'rho(E)':>9}{'fire E':>8}{'fire L':>8}")
    for r in rows:
        f = lambda k: "-" if r[k] is None else str(r[k])
        print(f"{r['unit']:<7}{r['event']:<14}{r['n']:>7}{r['med']:>8.0f}{r['thr']:>8.0f}"
              f"{r['e0']:>9.2%}{r['e_max']:>9.2%}{r['rho']:>+9.3f}{f('kE'):>8}{f('kL'):>8}")

    ok_rho = [r for r in rows if np.isfinite(r["rho"]) and passes(r["rho"], 0.8)]
    print(f"\nK1 excursion rate rises, rho >= 0.8 : {len(ok_rho)}/{len(rows)} -> "
          f"{'PASS' if len(ok_rho) * 2 >= len(rows) and rows else 'FAIL'} (needs half)")

    both = [r for r in rows if r["kE"] and r["kL"]]
    if len(both) < 3:
        print(f"K2 units where BOTH fired: {len(both)} -- untestable (docs/240 needs 3)")
    else:
        lead = [r for r in both if r["kE"] < r["kL"]]
        print(f"K2 excursions fire before level : {len(lead)}/{len(both)} -> "
              f"{'PASS' if len(lead) * 2 >= len(both) else 'FAIL'} (needs half)")
        for r in both:
            print(f"    {r['unit']}: E@{r['kE']} L@{r['kL']} "
                  f"{'lead' if r['kE'] < r['kL'] else ('same' if r['kE'] == r['kL'] else 'lag')}")

    fired_e = [r for r in rows if r["kE"]]
    print(f"\nK3 units where excursions fired at all: {len(fired_e)}/{len(rows)}")
    print(f"   max excursion rate across units: "
          f"{min(r['e_max'] for r in rows):.2%} .. {max(r['e_max'] for r in rows):.2%}")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("unit\tlast_event\tn\tmedian\tthreshold\tE_baseline\tE_max\trho_E\t"
                "fire_window_E\tfire_window_L\n")
        for r in rows:
            f.write("\t".join(str(x) for x in
                              [r["unit"], r["event"], r["n"], f"{r['med']:.6g}",
                               f"{r['thr']:.6g}", f"{r['e0']:.6g}", f"{r['e_max']:.6g}",
                               f"{r['rho']:.6g}", r["kE"] or "", r["kL"] or ""]) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")
    print("SOReDD ends in sticking; more excursions do not by themselves make them")
    print("a precursor of that ending (docs/240).")


if __name__ == "__main__":
    main()
