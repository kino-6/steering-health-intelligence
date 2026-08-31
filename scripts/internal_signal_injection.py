#!/usr/bin/env python3
"""The same injection on component-internal signals (docs/245 -> docs/246).

Executes the protocol pre-registered in docs/245 without modification.

docs/244 found vehicle-level detection needs ten floors for a short event.
Whether an internal signal needs the same multiple is unmeasured, and docs/167
gives something to compare against: real precursors at 20 to 300 times the
healthy floor on six of six NASA devices. Both go into the same unit -- that
signal's own floor -- so the sizes can be set side by side.

Healthy segments only. Same rectangle, same two detectors, same 1.0%
per-window false alarm as docs/243.

Windows and durations are in SAMPLES. The two sources sample differently, so
nothing here converts to docs/244's seconds.

docs/167's precursors are excursions of permanent degradation, not intermittent
events. A precursor exceeding a detection threshold is a comparison of
magnitudes, not evidence that an intermittent fault would be caught.

Data: NASA PCoE (public domain) / KAIST PMSM (CC BY 4.0).
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
import pmsm_measured_signature as sig
from capability_second_mechanism import headroom

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "internal_signal_injection.tsv"

WIN = 50
AMPS = [1, 2, 3, 5, 10, 20]
DURS = [1, 2, 5, 10, 20]
FA_TARGET = 0.010
FIT_RUNS = (1, 2, 3)          # docs/166's healthy window, unchanged
ROBUST = 3.0 * 1.4826
SUB = 200                     # sub-window count for the KAIST headroom series
RNG = np.random.default_rng(20260831)


def nasa_series():
    """Temperature-normalised on-state residual over the healthy runs."""
    z = zipfile.ZipFile(mos.ZIP)
    out = []
    for dev in mos.DEVICES:
        med = {}
        for run in FIT_RUNS:
            ron, tp = mos.read_run(z, dev, run)
            med[run] = (float(np.median(ron)), float(np.median(tp)))
        T = np.array([med[r][1] for r in FIT_RUNS])
        R = np.array([med[r][0] for r in FIT_RUNS])
        a, _ = np.polyfit(T, R, 1)
        t_ref = med[1][1]
        seq = []
        for run in FIT_RUNS:
            ron, tp = mos.read_run(z, dev, run)
            seq.append(np.asarray(ron) - a * (np.asarray(tp) - t_ref))
        s = np.concatenate(seq)
        if s.size >= WIN * 5:
            out.append((f"NASA Test_{dev}", s - np.median(s)))
    return out


def kaist_series():
    """Balance headroom over sub-windows of the healthy 1.0 kW records."""
    z = zipfile.ZipFile(sig.ZIP)
    out = []
    for name in sorted(n for n in z.namelist()
                       if "current" in n and "1000W_0_00" in n):
        p = sig.CACHE / name
        if not p.exists():
            z.extract(name, sig.CACHE)
        ph = sig.load_phases(p)
        f0 = sig.find_f0(ph)
        n = len(ph[0]) // SUB
        h = np.array([headroom([x[i * n:(i + 1) * n] for x in ph], f0)
                      for i in range(SUB)])
        if h.size >= WIN * 2:
            out.append((f"KAIST {Path(name).stem[:18]}", h - np.median(h)))
    return out


def evaluate(label, s):
    g = float(ROBUST * np.median(np.abs(s - np.median(s))))
    if g <= 0:
        return None
    k = len(s) // WIN
    w = s[:k * WIN].reshape(k, WIN)
    cm = np.abs(w.mean(axis=1)) / g
    cx = np.abs(w).max(axis=1) / g
    t_m = float(np.quantile(cm, 1 - FA_TARGET))
    t_x = float(np.quantile(cx, 1 - FA_TARGET))
    print(f"\n{label}   n={len(s):,}  windows={k}  floor={g:.6g}")
    print(f"   thresholds at {FA_TARGET:.1%} FA:  mean {t_m:.2f}   max {t_x:.2f}")
    print(f"{'A/g':>5}" + "".join(f"{'D=' + str(d):>16}" for d in DURS))
    rows = []
    for A in AMPS:
        line = f"{A:>5}"
        for D in DURS:
            hm = hx = 0
            trials = max(200, k)
            for _ in range(trials):
                wi = int(RNG.integers(0, k))
                off = int(RNG.integers(0, max(1, WIN - D)))
                seg = w[wi].copy()
                seg[off:off + D] += A * g * RNG.choice([-1.0, 1.0])
                hm += abs(seg.mean()) / g > t_m
                hx += np.abs(seg).max() / g > t_x
            dm, dx = hm / trials, hx / trials
            line += f"{dm:>8.0%}{dx:>8.0%}"
            rows.append((label, A, D, dm, dx))
        print(line)
    return rows


def main() -> None:
    print("columns are  mean / max  detection rate")
    all_rows = []
    series = nasa_series() + kaist_series()
    for label, s in series:
        r = evaluate(label, s)
        if r:
            all_rows.extend(r)

    print("\n" + "=" * 74)
    print("N1  smallest amplitude reaching 90% detection (multiples of the floor)")
    print(f"{'source':<26}" + "".join(f"{'D=' + str(d):>9}" for d in DURS))
    best = {}
    for label in dict.fromkeys(r[0] for r in all_rows):
        cells = []
        for D in DURS:
            got = None
            for A in AMPS:
                r = next(x for x in all_rows if x[0] == label and x[1] == A and x[2] == D)
                if max(r[3], r[4]) >= 0.90:
                    got = A
                    break
            cells.append(got)
            best.setdefault(D, []).append(got)
        print(f"{label:<26}" + "".join(
            f"{(str(c) + 'x' if c else '>' + str(AMPS[-1]) + 'x'):>9}" for c in cells))

    print("\nN2  precursor size vs detection threshold, in the same unit")
    d1 = [c for c in best.get(1, []) if c]
    if d1:
        print(f"   shortest event (D=1) needs {min(d1)}x to {max(d1)}x the floor")
    print(f"   docs/167 measured real precursors at 20x to 300x the floor")
    if d1 and max(d1) <= 20:
        print(f"   -> the precursor exceeds the detection threshold. There is margin.")
    else:
        print(f"   -> the precursor does NOT clearly exceed the threshold on every source.")
    print("   This compares MAGNITUDES. docs/167's precursors are permanent-degradation")
    print("   excursions, not intermittent events (docs/245).")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("source\tamplitude_over_floor\tduration_samples\tdetect_mean\tdetect_max\n")
        for r in all_rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
