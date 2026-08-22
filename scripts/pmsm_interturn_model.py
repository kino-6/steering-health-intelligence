#!/usr/bin/env python3
"""First-order PMSM inter-turn short model, and its signature vs severity.

Implements the standard lumped model of an inter-turn short circuit in one
phase of a star-connected three-phase PMSM with isolated neutral, and
computes the two metrics pre-registered in docs/161:

    U     = phase-current RMS unbalance
    I2/I1 = negative- to positive-sequence current ratio

Fault model. A fraction mu of phase A's turns is bypassed by a fault
resistance Rf. The healthy remainder (1-mu) stays in circuit; the shorted
section (mu) sits in parallel with Rf:

    Z_a = (1-mu)*Z + (mu*Z * Rf) / (mu*Z + Rf)
    E_a = (1-mu)*E + mu*E * Rf / (mu*Z + Rf)

Star, isolated neutral, balanced supply:

    V_n = sum((V_p - E_p)/Z_p) / sum(1/Z_p)
    I_p = (V_p - E_p - V_n) / Z_p

Declared limitation (docs/161): a real drive regulates current and
SUPPRESSES negative sequence. This open-loop voltage-source model
therefore overestimates I2/I1. The primary criterion is monotonicity and
curve shape, not absolute magnitude.

R and L are not published for these motors, so both are swept over the
band declared in docs/161 before the measurement was read.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "pmsm_interturn_model.tsv"

# --- DS011 1.0 kW machine, published specs (docs/161) ---------------------
# The published spec says 'four-pole'; the measured fundamental is 200 Hz at
# 3000 rpm, so the machine has 4 pole pairs. Matching the model to the measured
# fundamental is making the object the same, not fitting the metric (docs/161).
POLE_PAIRS = 4
SPEED_RPM = 3000.0
F_ELEC = SPEED_RPM / 60.0 * POLE_PAIRS      # 200 Hz
RF = 0.1385                                  # published inter-turn fault resistance [ohm]
# evaluated at the severities the dataset actually contains
SEVERITIES = np.array([0.0, 0.0226, 0.0270, 0.0335, 0.0441, 0.0648, 0.1217, 0.2169])

# --- declared sweep band (docs/161, fixed before reading data) ------------
R_BAND = np.array([1.0, 2.0, 3.0, 4.0, 5.0])          # ohm
L_BAND = np.array([5.0, 10.0, 15.0, 20.0]) * 1e-3     # H

A = np.exp(2j * np.pi / 3)


def currents(mu: float, R: float, L: float, V: float = 220.0, E: float = 180.0):
    """Phase currents for a star-connected PMSM with an inter-turn short in phase A."""
    Z = R + 1j * 2 * np.pi * F_ELEC * L
    # supply and back-EMF, balanced, positive sequence
    Vp = V * np.array([1.0, A**2, A])
    Ep = E * np.array([1.0, A**2, A])
    Zp = np.array([Z, Z, Z], dtype=complex)
    if mu > 0:
        zs = mu * Z                                # shorted section impedance
        par = zs * RF / (zs + RF)                  # shorted section in parallel with Rf
        Zp[0] = (1 - mu) * Z + par
        Ep[0] = (1 - mu) * E + mu * E * RF / (zs + RF)
    Vn = np.sum((Vp - Ep) / Zp) / np.sum(1.0 / Zp)   # neutral shift, isolated neutral
    return (Vp - Ep - Vn) / Zp


def metrics(I):
    rms = np.abs(I) / np.sqrt(2)
    U = (rms.max() - rms.min()) / rms.mean()
    I1 = (I[0] + A * I[1] + A**2 * I[2]) / 3
    I2 = (I[0] + A**2 * I[1] + A * I[2]) / 3
    return U, abs(I2) / abs(I1)


def main() -> None:
    rows = []
    print(f"electrical frequency {F_ELEC:.0f} Hz, Rf = {RF} ohm")
    print(f"{'severity':>9} | {'U (band)':>22} | {'I2/I1 (band)':>22}")
    print("-" * 60)
    for mu in SEVERITIES:
        us, rs = [], []
        for R in R_BAND:
            for L in L_BAND:
                U, r = metrics(currents(mu, R, L))
                us.append(U); rs.append(r)
                rows.append((mu, R, L, U, r))
        print(f"{mu:>9.4f} | {min(us):8.5f} .. {max(us):8.5f} | {min(rs):8.5f} .. {max(rs):8.5f}")

    with OUT_TSV.open("w") as fh:
        fh.write("severity\tR_ohm\tL_H\tunbalance\ti2_over_i1\n")
        for mu, R, L, U, r in rows:
            fh.write(f"{mu:.4f}\t{R:.1f}\t{L:.4f}\t{U:.6f}\t{r:.6f}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
