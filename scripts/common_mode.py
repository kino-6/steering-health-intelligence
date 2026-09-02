#!/usr/bin/env python3
"""Reject common-mode change using another channel of the same unit (docs/285 -> docs/286)

Executes the protocol pre-registered in docs/285.

docs/284 found the recorder reports a change shared across every unit as one
unit's deviation. A test bench can catch that by comparing units; a vehicle has
one unit and cannot. What a vehicle does have is several channels of the same
kind -- three half-bridge temperatures, two phase currents -- and a shared
cause moves them together while a fault in one moves one.

Everything except the observable is held identical to docs/278.

Criteria: C1 more channels quiet than the five of docs/278; C2 more detections
among quiet channels than three of eight; C3 the two channels that were broken,
T1 at 75.6% and T2 at 4.7%, come inside three times the design rate.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import element_v2 as el
from slow_channel import slow_deviation
from inverter_recorder import (ZIP, BASE, COLS, FAMILY, OPCOL, NS,
                               FA_PER_HOUR, HOUR_SAMPLES, read)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "common_mode.tsv"

# same-kind groups, docs/285. Vdc, Idc and Vd have no sibling and stay raw.
SIBLINGS = {"T1": ["T2", "T3"], "T2": ["T1", "T3"], "T3": ["T1", "T2"],
            "Ia": ["Ib"], "Ib": ["Ia"]}


def differenced(a, col):
    """This channel minus the median of its siblings; raw if it has none."""
    ci = COLS.index(col)
    sibs = SIBLINGS.get(col)
    if not sibs:
        return a[:, ci], False
    idx = [COLS.index(s) for s in sibs]
    return a[:, ci] - np.median(a[:, idx], axis=1), True


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    names = [n for n in z.namelist() if n.startswith(BASE) and n.endswith(".txt")]
    a_norm = read(z, next(n for n in names if "normal_operation" in n))
    faults = sorted(n for n in names if "fault_scenarios" in n)
    fdata = {Path(f).stem: read(z, f) for f in faults}

    half = len(a_norm) // 2
    design = FA_PER_HOUR / HOUR_SAMPLES
    print(f"正常運転 {len(a_norm)} 点。観測量だけを差分に置き換える\n")
    print(f"{'チャネル':>8} {'差分':>6} {'誤報/判定':>11} {'設計比':>9} "
          f"{'docs/278の設計比':>16} {'発火した故障':>12}")
    print("-" * 74)

    rows, quiet, fired = [], set(), {}
    prev = {"Ia": 0.0, "Ib": 0.0, "Vdc": 16.8, "Idc": 0.0,
            "T1": 27231.4, "T2": 1683.0, "T3": 0.0, "Vd": 134.6}

    for col in COLS:
        oi = COLS.index(OPCOL[col])
        y_fp, diffed = differenced(a_norm[:half], col)
        op_fp = a_norm[:half, oi]
        if np.std(op_fp) == 0:
            continue
        fp = el.take_fingerprint(y_fp, op_fp)
        if fp.floor <= 0:
            continue
        y_ho, _ = differenced(a_norm[half:], col)
        op_ho = a_norm[half:, oi]

        best = None
        for n in NS:
            d0 = slow_deviation(y_fp, op_fp, fp, n)
            if d0 is None:
                continue
            q = min(1 - design, 1 - 1.0 / len(d0))
            thr = float(np.quantile(d0, q))
            dh = slow_deviation(y_ho, op_ho, fp, n)
            fa = float(np.mean(dh > thr)) if dh is not None else 1.0
            if best is None or fa < best["fa"]:
                best = {"n": n, "thr": thr, "fa": fa}
        if best is None:
            continue
        ok = best["fa"] <= design * 3
        if ok:
            quiet.add(col)
        hits = set()
        for tag, af in fdata.items():
            if af is None or len(af) < best["n"] * 2:
                continue
            yf, _ = differenced(af, col)
            d = slow_deviation(yf, af[:, oi], fp, best["n"])
            if d is not None and (d > best["thr"]).any():
                hits.add(tag)
                fired.setdefault(tag, set()).add(col)
        print(f"{col:>8} {('あり' if diffed else '—'):>6} {best['fa']:>11.6f} "
              f"{best['fa']/design:>8.1f}倍 {prev[col]:>15.1f}倍 {len(hits):>11}"
              f"{'' if ok else '  (誤報超過)'}")
        rows.append({"channel": col, "differenced": int(diffed),
                     "fa": best["fa"], "ratio": best["fa"] / design,
                     "prev_ratio": prev[col], "faults": len(hits)})

    print(f"\n=== C1 誤報が基準内のチャネル ===")
    print(f"  {len(quiet)}/{len(COLS)}  (docs/278 では 5)  "
          f"{'PASS' if len(quiet) > 5 else 'FAIL'}")
    print(f"  内訳: {', '.join(sorted(quiet)) if quiet else 'なし'}")

    n_clean = sum(1 for t in fdata if fired.get(t, set()) & quiet)
    print(f"\n=== C2 誤報基準内のチャネルだけで数えた検出 ===")
    for t in sorted(fdata):
        ch = sorted(fired.get(t, set()) & quiet)
        print(f"  {t:>22} {(', '.join(ch) if ch else '—'):>26}")
    print(f"  **{n_clean}/{len(fdata)}**  (docs/278 では 3/8)  "
          f"{'PASS' if n_clean > 3 else 'FAIL'}")

    print(f"\n=== C3 壊れていた2チャネル ===")
    for c in ("T1", "T2"):
        r = next((x for x in rows if x["channel"] == c), None)
        if r:
            print(f"  {c}: {r['prev_ratio']:.1f}倍 → {r['ratio']:.1f}倍  "
                  f"{'PASS' if r['ratio'] <= 3 else 'FAIL'}")

    print(f"\n  C1 と C2 の両方が増えたか: "
          f"{'PASS' if (len(quiet) > 5 and n_clean > 3) else 'FAIL'}")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("channel\tdifferenced\tfalse_alarm\tratio_to_design\t"
                 "ratio_docs278\tfaults_fired\n")
        for r in rows:
            fh.write(f"{r['channel']}\t{r['differenced']}\t{r['fa']:.8f}\t"
                     f"{r['ratio']:.3f}\t{r['prev_ratio']:.1f}\t{r['faults']}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
