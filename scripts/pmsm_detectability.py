#!/usr/bin/env python3
"""Is the winding-fault sign detectable? (docs/162 addendum)

docs/162 recorded that phase-current unbalance only reaches 4x the healthy
value even at 21.69% severity, because the current regulator absorbs it.
That says the change is small. It does NOT say the change is undetectable
-- detectability depends on what the reading is compared against.

This measures the comparison base directly: split each 120 s record into
10 s sub-windows and measure how much U moves within one unit, one
setup, one run. That is the noise a same-unit longitudinal monitor sees.

Data: DS011 (KAIST, CC BY 4.0).
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from nptdms import TdmsFile

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "pmsm_detectability.tsv"
FS, F0, SEG = 100_000.0, 200.0, 10.0
A = np.exp(2j * np.pi / 3)


def fund(x, f0):
    n = len(x)
    t = np.arange(n) / FS
    w = np.hanning(n)
    return 2 * np.sum(x * w * np.exp(-2j * np.pi * f0 * t)) / np.sum(w)


def main() -> None:
    ang = lambda z: (np.degrees(np.angle(z)) + 180) % 360 - 180
    rows = []
    for f in sorted((REPO_ROOT / ".pmsm_fault" / "current").glob("*interturn*.tdms")):
        sev = float(re.search(r"1000W_(\d+)_(\d+)_", f.name).expand(r"\1.\2"))
        ch = [np.asarray(c[:], dtype=float) for c in TdmsFile.read(f)["Log"].channels()]
        n, w = min(len(c) for c in ch), int(SEG * FS)
        us = []
        for k in range(n // w):
            p = [c[k * w:(k + 1) * w] - c[k * w:(k + 1) * w].mean() for c in ch]
            ph = np.array([fund(x, F0) for x in p])
            if abs(ang(ph[2] / ph[0]) - 120) > 45 and abs(ang(-ph[2] / ph[0]) - 120) < 45:
                ph[2] = -ph[2]                      # session with reversed phase-C polarity
            r = np.abs(ph) / np.sqrt(2)
            us.append((r.max() - r.min()) / r.mean())
        us = np.array(us)
        rows.append((sev, float(np.median(us)), float(us.min()), float(us.max()), len(us)))

    rows.sort()
    healthy = [r for r in rows if r[0] == 0.0][0][1]
    spread = max((r[3] - r[2]) / r[1] for r in rows)
    print(f"within-unit spread of U over 10 s windows: up to {spread:.1%}")
    print(f"{'sev%':>7} {'U median':>10} {'x healthy':>10} {'margin over noise':>18}")
    with OUT_TSV.open("w") as fh:
        fh.write("severity_pct\tU_median\tU_min\tU_max\tn_windows\tx_healthy\tmargin_over_noise\n")
        for sev, med, lo, hi, n in rows:
            x = med / healthy
            margin = (x - 1) / spread if spread else float("inf")
            print(f"{sev:>7.2f} {med:>10.4f} {x:>10.1f} {margin:>17.0f}x")
            fh.write(f"{sev:.2f}\t{med:.6f}\t{lo:.6f}\t{hi:.6f}\t{n}\t{x:.4f}\t{margin:.1f}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
