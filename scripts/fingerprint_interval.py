#!/usr/bin/env python3
"""Pick the fingerprint interval by stationarity (docs/279 -> docs/280).

Executes the protocol pre-registered in docs/279.

docs/278 took the first half of the normal record as the fingerprint and the
recorder then fired on 76% of the held-out half, because the rig warms through
the recording. The rule fixed in docs/279: drift across the interval must be
under one floor, since the recorder measures deviation in floors and any larger
motion inside the interval is baked into the fingerprint itself.

Criteria: W1 how many channels have such an interval at all; W2a how many are
then quiet on held-out normal data, against the five of docs/278; W2b the
detection count among quiet channels, against three of eight.
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
OUT = ROOT / "data" / "fingerprint_interval.tsv"

FRACS = [1 / 2, 1 / 3, 1 / 4, 1 / 6]
DRIFT_MAX = 1.0          # drift over the interval, in floors -- docs/279


def drift_over_floor(y, op):
    """|slope| * span, divided by the residual scale. Both in the same units."""
    if len(y) < 20 or np.std(op) == 0:
        return None
    a, b = np.polyfit(op, y, 1)
    resid = y - (a * op + b)
    g = float(el.ROBUST * np.median(np.abs(resid - np.median(resid))))
    if g <= 0:
        return None
    return abs(a) * (op.max() - op.min()) / g, g


def best_interval(a, ci, oi):
    """Longest interval whose drift stays under one floor."""
    n = len(a)
    best = None
    for fr in FRACS:                      # longest first
        w = int(n * fr)
        if w < 30:
            continue
        for s in range(0, n - w + 1, max(1, w // 4)):
            y, op = a[s:s + w, ci], a[s:s + w, oi]
            r = drift_over_floor(y, op)
            if r is None:
                continue
            d, g = r
            if d < DRIFT_MAX and (best is None or w > best["w"]):
                best = {"s": s, "w": w, "drift": d, "floor": g}
        if best is not None:
            break                          # take the longest fraction that works
    return best


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    names = [n for n in z.namelist() if n.startswith(BASE) and n.endswith(".txt")]
    a_norm = read(z, next(n for n in names if "normal_operation" in n))
    faults = sorted(n for n in names if "fault_scenarios" in n)
    fault_data = {Path(f).stem: read(z, f) for f in faults}

    design = FA_PER_HOUR / HOUR_SAMPLES
    print(f"正常運転 {len(a_norm)} 点。漂流 < 床の {DRIFT_MAX} 倍 の最長区間を探す\n")
    print(f"{'チャネル':>8} {'区間':>16} {'漂流/床':>9} {'誤報/判定':>11} "
          f"{'設計比':>9} {'発火した故障':>12}")
    print("-" * 76)

    rows, quiet, fired = [], set(), {}
    for ci, col in enumerate(COLS):
        oi = COLS.index(OPCOL[col])
        b = best_interval(a_norm, ci, oi)
        if b is None:
            print(f"{col:>8} {'条件を満たす区間なし':>16}")
            rows.append({"channel": col, "start": None, "width": None,
                         "drift": None, "fa": None, "faults": 0})
            continue
        s, w = b["s"], b["w"]
        fp = el.take_fingerprint(a_norm[s:s + w, ci], a_norm[s:s + w, oi])
        # held-out normal: everything outside the fingerprint interval
        hold = np.concatenate([a_norm[:s], a_norm[s + w:]])
        best_n = None
        for n in NS:
            d0 = slow_deviation(a_norm[s:s + w, ci], a_norm[s:s + w, oi], fp, n)
            if d0 is None:
                continue
            q = min(1 - design, 1 - 1.0 / len(d0))
            thr = float(np.quantile(d0, q))
            dh = slow_deviation(hold[:, ci], hold[:, oi], fp, n)
            fa = float(np.mean(dh > thr)) if dh is not None else 1.0
            if best_n is None or fa < best_n["fa"]:
                best_n = {"n": n, "thr": thr, "fa": fa}
        if best_n is None:
            continue
        hits = set()
        for tag, af in fault_data.items():
            if af is None or len(af) < best_n["n"] * 2:
                continue
            d = slow_deviation(af[:, ci], af[:, oi], fp, best_n["n"])
            if d is not None and (d > best_n["thr"]).any():
                hits.add(tag)
                fired.setdefault(tag, set()).add(col)
        ok = best_n["fa"] <= design * 3
        if ok:
            quiet.add(col)
        print(f"{col:>8} {f'{s}..{s+w}':>16} {b['drift']:>8.2f} "
              f"{best_n['fa']:>11.5f} {best_n['fa']/design:>8.1f}倍 "
              f"{len(hits):>11}{'' if ok else '  (誤報超過)'}")
        rows.append({"channel": col, "start": s, "width": w, "drift": b["drift"],
                     "fa": best_n["fa"], "faults": len(hits)})

    print(f"\n=== W1 条件を満たす区間があるチャネル ===")
    have = sum(1 for r in rows if r["width"])
    print(f"  {have}/{len(COLS)}")

    print(f"\n=== W2a 誤報が設計値の3倍以内のチャネル ===")
    print(f"  {len(quiet)}/{len(COLS)}  (docs/278 では 5)  "
          f"{'改善' if len(quiet) > 5 else '改善せず'}")
    print(f"  内訳: {', '.join(sorted(quiet)) if quiet else 'なし'}")

    print(f"\n=== W2b 誤報基準内のチャネルだけで数えた検出 ===")
    n_clean = sum(1 for t in fault_data if fired.get(t, set()) & quiet)
    for t in sorted(fault_data):
        ch = sorted(fired.get(t, set()) & quiet)
        print(f"  {t:>22} {(', '.join(ch) if ch else '—'):>22}")
    print(f"  **{n_clean}/{len(fault_data)}**  (docs/278 では 3/8)  "
          f"{'改善' if n_clean > 3 else '改善せず'}")
    print(f"\n  W2a と W2b の両方が増えたか: "
          f"{'PASS' if (len(quiet) > 5 and n_clean > 3) else 'FAIL'}")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("channel\tstart\twidth\tdrift_over_floor\tfalse_alarm\t"
                 "faults_fired\n")
        for r in rows:
            d = "" if r["drift"] is None else f"{r['drift']:.4f}"
            fa = "" if r["fa"] is None else f"{r['fa']:.6f}"
            fh.write(f"{r['channel']}\t{r['start']}\t{r['width']}\t{d}\t{fa}\t"
                     f"{r['faults']}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
