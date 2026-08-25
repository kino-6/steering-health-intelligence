#!/usr/bin/env python3
"""What actually limits the declaration (docs/196 -> docs/197).

docs/196 built the element and left two things open. This closes one and
bounds the other. Neither needs data that does not exist.

(A) The fingerprint span requirement was left at "one point is not enough".
    That is measurable: the operating point that each unit actually visits
    over its life is in the data, and so is the span the fingerprint was
    fitted over. The ratio is the requirement.

(B) The constant-Rth assumption was left as "optimistic, magnitude unknown".
    The magnitude does not need measuring, because it is analytic. With

        C = sqrt(R_base / R_hat)   assuming Rth constant

    a thermal resistance that has risen by a factor k gives

        I_max = sqrt((Tj_max - T_amb) / (k * Rth * R_on))
        C_true = C_declared / sqrt(k)

    so the declaration is optimistic by exactly sqrt(k) - 1. That converts an
    unbounded unknown into a row the integrator can evaluate with their own k.

    It also raises a question this work has not asked of itself: the declared
    granularity is 0.08 to 1.0 percent, and the assumption error passes that
    at some k. If k reaches it easily, then the number being declared is the
    resolution of the measurement and not its accuracy, and saying so is part
    of an honest declaration.

Data: NASA PCoE MOSFET thermal overstress ageing, public domain.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np

import mosfet_precursor as mos
from eps_health_element import EOL_RUNS, MAX_EXTRAP

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "capability_declaration_limits.tsv"

# Granularities measured in docs/193 and docs/195, across both mechanisms.
G_MIN, G_MAX = 0.00081, 0.01005
K_GRID = [1.01, 1.02, 1.05, 1.10, 1.20, 1.50, 2.00]


def main() -> None:
    z = zipfile.ZipFile(mos.ZIP)
    rows = []

    print("=" * 78)
    print("(A) how wide the end-of-line fingerprint has to be")
    print("=" * 78)
    print(f"{'unit':>8}{'life range':>14}{'fitted span':>13}{'ratio':>8}"
          f"{'refused':>9}{'max inflation':>15}")
    ratios, infl_max = [], []
    for dev in mos.DEVICES:
        T = {}
        for run in range(1, mos.N_RUNS + 1):
            _, tp = mos.read_run(z, dev, run)
            T[run] = float(np.median(tp))
        life = max(T.values()) - min(T.values())
        fit = np.array([T[r] for r in EOL_RUNS])
        span = float(fit.max() - fit.min())
        refused, inflations = 0, []
        for run in range(1, mos.N_RUNS + 1):
            d_out = max(0.0, fit.min() - T[run], T[run] - fit.max())
            if d_out > MAX_EXTRAP * span:
                refused += 1
            else:
                inflations.append(1.0 + d_out / span)
        ratio = life / span
        ratios.append(ratio)
        infl_max.append(max(inflations))
        print(f"{f'Test_{dev}':>8}{life:>13.1f}C{span:>12.1f}C{ratio:>8.2f}"
              f"{refused:>9}{max(inflations):>14.2f}x")
        rows.append(("A", f"Test_{dev}", life, span, ratio, refused, max(inflations)))

    print(f"\n  the operating point travels {min(ratios):.1f} to {max(ratios):.1f} times "
          f"the span the fingerprint was fitted over")
    print(f"  granularity inflation reaches {max(infl_max):.2f}x, and one unit still "
          f"loses its final point")
    print(f"\n  requirement: sweep the fingerprint over at least the operating range "
          f"expected in service.")
    print(f"  on this data that is {max(ratios):.1f}x wider than what was taken.")

    print("\n" + "=" * 78)
    print("(B) what the constant-Rth assumption costs")
    print("=" * 78)
    print("  C_true = C_declared / sqrt(k)   for a thermal resistance risen by k")
    print(f"\n{'k':>8}{'optimism':>12}{'vs g=0.081%':>14}{'vs g=1.005%':>14}")
    for k in K_GRID:
        opt = np.sqrt(k) - 1.0
        print(f"{k:>8.2f}{opt:>11.2%}{opt/G_MIN:>13.0f}x{opt/G_MAX:>13.1f}x")
        rows.append(("B", f"k={k}", k, opt, opt / G_MIN, opt / G_MAX, 0))

    # ---- how far the assumption could actually be off, from the data -------
    # R_on is itself a junction-temperature sensor. At end of line the
    # dissipation is roughly constant, so d(R_on)/d(T_package) fitted there is
    # the intrinsic coefficient of R_on against junction temperature. If the
    # later rise in temperature-normalised R_on were caused ENTIRELY by the
    # die-attach path degrading rather than by the die itself, the implied
    # junction temperature rise at the same package temperature is
    #
    #     dTj = dR_hat / a
    #
    # That is the extreme case, not an estimate. The other extreme is k = 1,
    # where the declaration is exact. The data cannot separate them -- that is
    # what docs/189 (2) failed to do -- so both ends are printed and the truth
    # lies between.
    print("\n" + "-" * 78)
    print("  how far off could it be? the two extremes, from this data")
    print("-" * 78)
    print(f"{'unit':>8}{'dR_hat/R at end':>18}{'a [ohm/C]':>12}"
          f"{'implied dTj if all thermal':>28}")
    dts = []
    for dev in mos.DEVICES:
        med = {}
        for run in range(1, mos.N_RUNS + 1):
            ron, tp = mos.read_run(z, dev, run)
            med[run] = (float(np.median(ron)), float(np.median(tp)))
        T = np.array([med[r][1] for r in EOL_RUNS])
        R = np.array([med[r][0] for r in EOL_RUNS])
        a, _ = np.polyfit(T, R, 1)
        t_ref = med[1][1]
        rhat = {r: med[r][0] - a * (med[r][1] - t_ref) for r in med}
        base = float(np.mean([rhat[r] for r in EOL_RUNS]))
        d_r = rhat[mos.N_RUNS] - base
        d_tj = d_r / a
        dts.append(d_tj)
        print(f"{f'Test_{dev}':>8}{d_r / base:>17.1%}{a:>12.5f}{d_tj:>27.1f}C")
        rows.append(("B2", f"Test_{dev}", d_r / base, float(a), d_tj, 0, 0))
    print(f"\n  if none of the rise is thermal (k = 1) the declaration is exact.")
    print(f"  if all of it is, the junction sits {min(dts):.0f} to {max(dts):.0f} C hotter")
    print(f"  than the package reading implies, and the capability is worse than declared.")
    print(f"  the data cannot separate the two -- docs/189 (2) tried and failed.")

    k_min = (1 + G_MIN) ** 2
    k_max = (1 + G_MAX) ** 2
    print(f"\n  the assumption error equals the declared granularity at")
    print(f"    k = {k_min:.4f}  ({(k_min-1):.2%} rise in Rth)  for the finest granularity 0.081%")
    print(f"    k = {k_max:.4f}  ({(k_max-1):.2%} rise in Rth)  for the coarsest 1.005%")
    rows.append(("B", "k at which error = g", k_min, k_max, G_MIN, G_MAX, 0))

    print("\n  so a rise in thermal resistance of a fraction of a percent to about two")
    print("  percent already matters more than the resolution being declared.")
    print("  the 0.08-1.0% figure is the RESOLUTION of the measurement.")
    print("  it is not the ACCURACY of the capability value.")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("part\tkey\tv1\tv2\tv3\tv4\tv5\n")
        for r in rows:
            out.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                                for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
