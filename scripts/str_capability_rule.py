#!/usr/bin/env python3
"""STR capability derivation rule (docs/192 protocol -> docs/193).

Executes the protocol pre-registered in docs/192 without modification.

Capability is defined from the thermal limit on sustained assist. With
conduction-dominated loss the deliverable current goes as 1/sqrt(R_on), so
against the unit's own temperature-normalised baseline:

    C(t) = sqrt( R_hat_on(base) / R_hat_on(t) )

Rth, Tj_max and T_amb cancel in the ratio, which is why this is computable
after docs/189 failed to measure the thermal resistance directly. The
assumption that Rth is constant makes C an upper bound -- optimistic -- and
that is declared on the sheet, not hidden here.

Three monitors are run so that the per-unit contribution is separated from
the temperature-compensation contribution:

    M0  raw R_on                      vs population threshold
    M1  population temperature coeff  vs population threshold
    M2  per-unit temperature coeff    vs the unit's own baseline

The primary criterion is M2 against M1. Beating M0 would only show that
temperature compensation works, which is not the claim being tested.

A monitor that never fires is scored as firing after the last run. That is
the only reading of "fires at least one run earlier" that is defined when a
comparator stays silent, and it is stated in the output rather than folded
in silently.

Data: NASA Prognostics Center of Excellence, public domain.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np

import mosfet_precursor as v1

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "str_capability_rule.tsv"
FIT_RUNS = (1, 2, 3)          # docs/166, unchanged
NEVER = v1.N_RUNS + 1         # score for a monitor that never fires


def pop_threshold(vals: np.ndarray) -> float:
    """median + 3 * 1.4826 * MAD, as fixed in docs/192."""
    med = float(np.median(vals))
    mad = float(np.median(np.abs(vals - med)))
    return med + 3.0 * 1.4826 * mad


def first_fire(series: dict[int, float], thr: float) -> int:
    for r in range(1, v1.N_RUNS + 1):
        if series[r] > thr:
            return r
    return NEVER


def main() -> None:
    z = zipfile.ZipFile(v1.ZIP)

    # ---- per-device medians -------------------------------------------------
    med: dict[int, dict[int, tuple[float, float]]] = {}
    for dev in v1.DEVICES:
        med[dev] = {}
        for run in range(1, v1.N_RUNS + 1):
            ron, tpkg = v1.read_run(z, dev, run)
            med[dev][run] = (float(np.median(ron)), float(np.median(tpkg)))

    # ---- M1: one temperature coefficient for the whole population ----------
    # Regress within-device-centred R on within-device-centred T over the
    # baseline runs, so device-to-device offsets do not enter the slope.
    dr, dt = [], []
    for dev in v1.DEVICES:
        R = np.array([med[dev][r][0] for r in FIT_RUNS])
        T = np.array([med[dev][r][1] for r in FIT_RUNS])
        dr.append(R - R.mean())
        dt.append(T - T.mean())
    a_pop = float(np.polyfit(np.concatenate(dt), np.concatenate(dr), 1)[0])
    t_ref_pop = float(np.median([med[dev][1][1] for dev in v1.DEVICES]))

    def m1_value(dev: int, run: int) -> float:
        r, t = med[dev][run]
        return r - a_pop * (t - t_ref_pop)

    thr_m0 = pop_threshold(np.array([med[d][r][0] for d in v1.DEVICES for r in FIT_RUNS]))
    thr_m1 = pop_threshold(np.array([m1_value(d, r) for d in v1.DEVICES for r in FIT_RUNS]))

    print(f"population temperature coefficient a_pop = {a_pop:.5f} ohm/degC "
          f"(reference {t_ref_pop:.1f} degC)")
    print(f"M0 threshold {thr_m0:.4f} ohm    M1 threshold {thr_m1:.4f} ohm")
    print(f"(six devices; both are point estimates with no interval -- docs/192)\n")

    rows, summary = [], {}
    for dev in v1.DEVICES:
        # ---- M2: per-unit coefficient, per-unit baseline -------------------
        R = np.array([med[dev][r][0] for r in FIT_RUNS])
        T = np.array([med[dev][r][1] for r in FIT_RUNS])
        a_dev, _ = np.polyfit(T, R, 1)
        t_ref = med[dev][1][1]
        rhat = {r: med[dev][r][0] - a_dev * (med[dev][r][1] - t_ref)
                for r in range(1, v1.N_RUNS + 1)}
        base = float(np.mean([rhat[r] for r in FIT_RUNS]))
        cap = {r: float(np.sqrt(base / rhat[r])) for r in rhat}
        g = 3.0 * float(np.std([cap[r] for r in FIT_RUNS], ddof=1))

        # first run below 1-g that stays below for every later run
        fire_m2 = NEVER
        for r in range(1, v1.N_RUNS + 1):
            if all(cap[k] < 1.0 - g for k in range(r, v1.N_RUNS + 1)):
                fire_m2 = r
                break

        fire_m0 = first_fire({r: med[dev][r][0] for r in rhat}, thr_m0)
        fire_m1 = first_fire({r: m1_value(dev, r) for r in rhat}, thr_m1)
        drop = (1.0 - cap[fire_m2]) if fire_m2 <= v1.N_RUNS else 0.0

        summary[dev] = dict(a_dev=float(a_dev), g=g, fire_m0=fire_m0, fire_m1=fire_m1,
                            fire_m2=fire_m2, drop=drop, ratio=(drop / g if g > 0 else 0.0),
                            c_final=cap[v1.N_RUNS], cap=cap)

        print(f"--- Test_{dev}   a_dev = {a_dev:.5f} ohm/degC   declared granularity g = {g:.4%}")
        print("      run     " + "".join(f"{r:>9}" for r in range(1, v1.N_RUNS + 1)))
        print("      C       " + "".join(f"{cap[r]:>9.4f}" for r in range(1, v1.N_RUNS + 1)))
        print("      1-C     " + "".join(f"{1-cap[r]:>+9.2%}" for r in range(1, v1.N_RUNS + 1)))
        f = lambda x: "never" if x > v1.N_RUNS else f"run {x}"
        print(f"      fires:  M0 {f(fire_m0):<7}  M1 {f(fire_m1):<7}  M2 {f(fire_m2):<7}"
              f"   drop at M2 fire {drop:.2%} = {drop/g if g else 0:.1f} x g\n")
        for r in range(1, v1.N_RUNS + 1):
            rows.append((dev, r, med[dev][r][0], med[dev][r][1], rhat[r], cap[r],
                         g, fire_m0, fire_m1, fire_m2))

    # ---- criteria ----------------------------------------------------------
    p1 = sum(1 for d in summary if summary[d]["fire_m2"] <= summary[d]["fire_m1"] - 1)
    p2 = sum(1 for d in summary if summary[d]["ratio"] >= 3.0)
    print("=" * 72)
    print(f"P1  M2 fires at least one run before M1 : {p1}/6  "
          f"-> {'PASS' if p1 >= 4 else 'FAIL'} (needs 4)")
    print(f"P2  drop at that run >= 3 x granularity : {p2}/6  "
          f"-> {'PASS' if p2 >= 4 else 'FAIL'} (needs 4)")
    gs = [summary[d]["g"] for d in summary]
    print(f"P3  declared granularity g              : {min(gs):.3%} .. {max(gs):.3%} "
          f"(reported, no threshold)")
    print()
    win = [summary[d]["fire_m1"] - summary[d]["fire_m2"] for d in summary]
    print(f"window M1-M2 in runs   : {win}")
    print(f"capability at last run : "
          + ", ".join(f"Test_{d} {summary[d]['c_final']:.3f}" for d in summary))
    m1_silent = sum(1 for d in summary if summary[d]["fire_m1"] > v1.N_RUNS)
    m0_silent = sum(1 for d in summary if summary[d]["fire_m0"] > v1.N_RUNS)
    print(f"never fires before end : M0 {m0_silent}/6, M1 {m1_silent}/6")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("device\trun\tr_on\tt_pkg\tr_on_normalised\tcapability\t"
                  "granularity\tfire_m0\tfire_m1\tfire_m2\n")
        for r in rows:
            out.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x) for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
