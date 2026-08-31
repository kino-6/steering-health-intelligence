#!/usr/bin/env python3
"""What a usable false-alarm rate costs in sensitivity (docs/247 -> docs/248).

Executes the protocol pre-registered in docs/247 without modification.

docs/244 measured detection at a 1.0% per-window false alarm and said in the
same breath that this is seven alarms an hour and not deployable. This sweeps
the rate down to one alarm per hour and one per ten hours and reports what the
detection limit becomes.

At 10 Hz with five-second windows there are 720 windows per driving hour, so
one alarm per hundred hours sits at half a window in a 35,000-window sample.
docs/247 declared that outside the sample before running, and it is not
estimated.

Data: commaSteeringControl (MIT) / NASA PCoE (public domain).
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from intermittent_injection import CACHE, WIN, read_log, windows
from internal_signal_injection import nasa_series

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "false_alarm_tradeoff.tsv"

WIN_PER_HOUR = 3600 * 10 / WIN                     # 720
LEVELS = [("L0  7.2/h", 1.0e-2), ("L1  1/h", 1 / WIN_PER_HOUR),
          ("L2  0.1/h", 0.1 / WIN_PER_HOUR), ("L3  0.01/h", 0.01 / WIN_PER_HOUR)]
AMPS = [1, 2, 3, 5, 10, 20, 50]
DURS = [1, 2, 5, 10, 20]
ROBUST = 3.0 * 1.4826
RNG = np.random.default_rng(20260831)


def collect_vehicle():
    res, fl = [], []
    for model in sorted(p.name for p in CACHE.iterdir() if p.is_dir()):
        for f in sorted((CACHE / model).glob("*.csv")):
            e = read_log(f)
            if e is None:
                continue
            g = float(ROBUST * np.median(np.abs(e - np.median(e))))
            if g > 0:
                res.append(e)
                fl.append(g)
    w = [windows(e) for e in res]
    return [(x / g) for x, g in zip(w, fl) if x is not None]


def sweep(label, wins):
    """wins: list of (k, WIN) arrays already divided by their own floor."""
    W = np.vstack(wins)
    n = len(W)
    cm = np.abs(W.mean(axis=1))
    cx = np.abs(W).max(axis=1)
    print(f"\n{label}   windows = {n:,}")
    rows = []
    for name, fa in LEVELS:
        need = 1.0 / fa
        if n < need:
            print(f"  {name:<12} needs {need:,.0f} windows, have {n:,} -- OUTSIDE THE SAMPLE")
            rows.append((label, name, fa, None, None, None))
            continue
        t_m = float(np.quantile(cm, 1 - fa))
        t_x = float(np.quantile(cx, 1 - fa))
        cells = []
        for D in DURS:
            got = None
            for A in AMPS:
                hm = hx = 0
                trials = max(300, min(n, 3000))
                for _ in range(trials):
                    wi = int(RNG.integers(0, n))
                    off = int(RNG.integers(0, max(1, WIN - D)))
                    seg = W[wi].copy()
                    seg[off:off + D] += A * RNG.choice([-1.0, 1.0])
                    hm += abs(seg.mean()) > t_m
                    hx += np.abs(seg).max() > t_x
                if max(hm, hx) / trials >= 0.90:
                    got = A
                    break
            cells.append(got)
        f = lambda c: (f"{c}x" if c else f">{AMPS[-1]}x")
        print(f"  {name:<12} thr mean {t_m:5.2f} max {t_x:6.2f}   "
              f"90% at: " + "  ".join(f"D={D}:{f(c)}" for D, c in zip(DURS, cells)))
        rows.append((label, name, fa, t_m, t_x, cells))
    return rows


def main() -> None:
    print("amplitudes are multiples of each series' own floor")
    rows = []
    veh = collect_vehicle()
    rows += sweep("vehicle level", veh)

    z = zipfile.ZipFile(__import__("mosfet_precursor").ZIP) if False else None
    internal = []
    for lbl, s in nasa_series():
        g = float(ROBUST * np.median(np.abs(s - np.median(s))))
        k = len(s) // WIN
        if g > 0 and k:
            internal.append(s[:k * WIN].reshape(k, WIN) / g)
    rows += sweep("component-internal (NASA, pooled)", internal)

    print("\n" + "=" * 74)
    print("P3  cost of moving from the measurable rate to a usable one")
    for lab in dict.fromkeys(r[0] for r in rows):
        got = {r[1]: r[5] for r in rows if r[0] == lab and r[5]}
        if "L0  7.2/h" in got and "L2  0.1/h" in got:
            a0, a2 = got["L0  7.2/h"][0], got["L2  0.1/h"][0]
            if a0 and a2:
                print(f"  {lab:<34} D=1: {a0}x -> {a2}x   ({a2/a0:.1f}x worse)")
            else:
                print(f"  {lab:<34} D=1: not reached within {AMPS[-1]}x at one of the levels")
        else:
            print(f"  {lab:<34} L2 outside the sample -- cannot be measured")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("source\tlevel\tfa_per_window\tthr_mean\tthr_max\t"
                + "\t".join(f"amp90_D{d}" for d in DURS) + "\n")
        for r in rows:
            cells = r[5] or [None] * len(DURS)
            f.write("\t".join([r[0], r[1], f"{r[2]:.3g}",
                               "" if r[3] is None else f"{r[3]:.4g}",
                               "" if r[4] is None else f"{r[4]:.4g}"]
                              + ["" if c is None else str(c) for c in cells]) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
