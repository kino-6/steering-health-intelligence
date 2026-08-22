#!/usr/bin/env python3
"""Measured inter-turn signature vs severity from DS011 (docs/162).

Reads the KAIST 1.0 kW PMSM inter-turn current recordings and computes the
two metrics pre-registered in docs/161:

    U     = phase-current RMS unbalance  (max-min)/mean
    I2/I1 = negative- to positive-sequence ratio at the fundamental

Both a total-RMS reading (the literal pre-registered metric) and a
fundamental-only reading are reported. The model in
scripts/pmsm_interturn_model.py is a fundamental-frequency model, so the
two are not interchangeable and both are shown rather than one being
chosen after the fact.

A 20 s window is taken from the middle of each 120 s record, to avoid
start-up and shutdown transients. That choice is fixed here, not per file.

Data: Vibration and current dataset of three-phase PMSM with stator faults
(KAIST, Data in Brief 2023), Mendeley 10.17632/rgn5brrgrn.5, CC BY 4.0.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

import numpy as np
from nptdms import TdmsFile

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / ".pmsm_fault"
ZIP = CACHE / "1.0kW.zip"
OUT_TSV = REPO_ROOT / "data" / "pmsm_measured_signature.tsv"

WINDOW_S = 20.0          # analysis window, taken from the middle of the record
FS = 100_000.0
A = np.exp(2j * np.pi / 3)


def severity_from_name(name: str) -> float:
    m = re.search(r"1000W_(\d+)_(\d+)_current", name)
    return float(f"{m.group(1)}.{m.group(2)}") if m else float("nan")


def load_phases(path: Path):
    tdms = TdmsFile.read(path)
    grp = tdms["Log"]
    chans = [c for c in grp.channels()]
    data = [np.asarray(c[:], dtype=np.float64) for c in chans]
    n = min(len(d) for d in data)
    w = int(WINDOW_S * FS)
    s = (n - w) // 2
    return [d[s:s + w] - d[s:s + w].mean() for d in data]


def fundamental(x, f0_hz):
    """Complex amplitude of x at f0 (single-bin DFT with a Hann window)."""
    n = len(x)
    t = np.arange(n) / FS
    win = np.hanning(n)
    ref = np.exp(-2j * np.pi * f0_hz * t)
    return 2.0 * np.sum(x * win * ref) / np.sum(win)


def find_f0(phases):
    x = phases[0]
    n = 1 << 20
    sp = np.fft.rfft(x[:n] * np.hanning(n))
    fr = np.fft.rfftfreq(n, 1 / FS)
    band = (fr > 40) & (fr < 400)          # the machine runs at 3000 rpm, 2 pole pairs -> ~100 Hz
    return float(fr[band][np.argmax(np.abs(sp[band]))])


def fix_polarity(ph, p):
    """One session has the phase-C sensor wired with reversed polarity.

    Detected geometrically, not per file by hand: in those records phase C
    sits about -66 deg from phase A instead of +120 deg, and flipping its
    sign puts it back on the 120 deg spacing the other records show."""
    d = lambda z: (np.degrees(np.angle(z)) + 180) % 360 - 180
    if abs(d(ph[2] / ph[0]) - 120) > 45 and abs(d(-ph[2] / ph[0]) - 120) < 45:
        return np.array([ph[0], ph[1], -ph[2]]), [p[0], p[1], -p[2]], True
    return ph, p, False


def metrics(phases, f0):
    tot = np.array([np.sqrt(np.mean(p ** 2)) for p in phases])
    U_tot = (tot.max() - tot.min()) / tot.mean()
    ph = np.array([fundamental(p, f0) for p in phases])
    ph, phases, flipped = fix_polarity(ph, phases)
    rms1 = np.abs(ph) / np.sqrt(2)
    U_f = (rms1.max() - rms1.min()) / rms1.mean()
    I1 = (ph[0] + A * ph[1] + A ** 2 * ph[2]) / 3
    I2 = (ph[0] + A ** 2 * ph[1] + A * ph[2]) / 3
    dom, sub = max(abs(I1), abs(I2)), min(abs(I1), abs(I2))
    return U_tot, U_f, sub / dom, tot, rms1, flipped


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    names = sorted(n for n in z.namelist()
                   if "current" in n and "interturn" in n.replace("_", ""))
    rows = []
    print(f"{'severity%':>9} {'f0[Hz]':>8} {'RMS a/b/c [A]':>26} {'U_total':>9} {'U_fund':>9} {'I2/I1':>9}  sess")
    print("-" * 78)
    for name in names:
        p = CACHE / name
        if not p.exists():
            z.extract(name, CACHE)
        phases = load_phases(p)
        f0 = find_f0(phases)
        U_tot, U_f, ratio, tot, rms1, flipped = metrics(phases, f0)
        sev = severity_from_name(name)
        print(f"{sev:>9.2f} {f0:>8.2f} {'/'.join(f'{v:7.3f}' for v in tot):>26}"
              f" {U_tot:>9.4f} {U_f:>9.4f} {ratio:>9.4f}  {'S1' if flipped else 'S2'}")
        rows.append((sev, f0, U_tot, U_f, ratio, int(flipped), *tot))

    rows.sort()
    with OUT_TSV.open("w") as fh:
        fh.write("severity_pct\tf0_hz\tU_total_rms\tU_fundamental\ti2_over_i1\t"
                 "session_s1\trms_a\trms_b\trms_c\n")
        for r in rows:
            fh.write("\t".join(f"{v:.6f}" for v in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
