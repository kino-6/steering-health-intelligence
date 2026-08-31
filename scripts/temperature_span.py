#!/usr/bin/env python3
"""How wide a temperature span does one straight line hold? (docs/262 -> docs/263)

Executes the protocol pre-registered in docs/262 against NASA PCoE MOSFET
Thermal Overstress Aging (public domain), already inventoried.

The specification's last blank was the temperature range the fingerprint must
be swept over, left empty because commaSteeringControl carries no temperature.
That question needs road data. The question the part can answer instead is how
wide a span a single line holds -- and the 36-byte fingerprint of docs/196
already assumes one line, so the answer either confirms that number or changes
it.

docs/257 closed this dataset for thermal-path degradation. This is not that
question: it asks how linear an electrical observable is in temperature, which
docs/246 already relied on when it compensated for temperature.

Criteria, fixed in docs/262 before any value was read: W1 one line holds 60 C
or more on at least five of six devices, where 60 C is an assumed reference and
the measured spans are reported beside it; W2 the spread across devices; W3 if
W1 fails, how many lines an operating span would need.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "temperature_span.tsv"

SPANS = [10, 20, 40, 60, 80, 100, 140, 180]
ROBUST = 3.0 * 1.4826
TOL = 1.0            # residual may not exceed one floor
MIN_N = 200
W1_SPAN = 60.0       # assumed reference, docs/262


def series(dev: str):
    """Observable and package temperature over that device's whole record."""
    import zipfile
    z = zipfile.ZipFile(mos.ZIP) if hasattr(mos, "ZIP") else None
    y, t = [], []
    for run in (1, 2, 3):
        ron, tp = mos.read_run(z, dev, run)
        y.append(np.asarray(ron))
        t.append(np.asarray(tp))
    return np.concatenate(y), np.concatenate(t)


def residual_sd(y, t, lo, hi):
    sel = (t >= lo) & (t <= hi)
    if sel.sum() < MIN_N:
        return None, int(sel.sum())
    a, b = np.polyfit(t[sel], y[sel], 1)
    r = y[sel] - (a * t[sel] + b)
    return float(np.std(r)), int(sel.sum())


def best_window(y, t, span):
    """The placement of a window of this width holding the most samples.

    An earlier version centred every window on the median temperature. The rig
    soaks near the top of its ramp, so the median sits close to an edge and
    every window wider than 10 C fell outside the data -- the test measured
    nothing.
    """
    lo_grid = np.linspace(t.min(), t.max() - span, 40)
    best = (None, -1, None)
    for lo in lo_grid:
        sd, n = residual_sd(y, t, lo, lo + span)
        if sd is not None and n > best[1]:
            best = (sd, n, lo)
    return best


def noise_floor(y, t):
    """Point-to-point scale, independent of any fit span.

    An earlier version took the residual of a +-5 C fit as the floor, which
    made the 10 C column exactly 1.00 by construction rather than by
    measurement.
    """
    order = np.argsort(t)
    d = np.diff(y[order])
    return float(ROBUST * np.median(np.abs(d - np.median(d))) / np.sqrt(2))


def main() -> None:
    rows, held = [], {}
    print(f"{'素子':>9} {'温度の実測幅':>13} {'床':>11} " +
          "".join(f"{str(s) + 'C':>9}" for s in SPANS))
    print("-" * 96)
    for dev in mos.DEVICES:
        y, t = series(dev)
        full = float(t.max() - t.min())
        # the floor is the residual of the widest fit that stays inside the data
        g = noise_floor(y, t)
        cells, best = [], None
        for sp in SPANS:
            if sp > full:
                cells.append("—")           # never extrapolate past the data
                continue
            sd, n, lo = best_window(y, t, sp)
            if sd is None:
                cells.append("—")
                continue
            ratio = sd / g if g else float("inf")
            cells.append(f"{ratio:.2f}")
            if ratio <= TOL:
                best = sp
            rows.append({"dev": dev, "span": sp, "ratio": ratio, "n": n, "floor": g})
        held[dev] = best
        print(f"{dev:>9} {full:>12.0f}C {g:>11.4g} " + "".join(f"{c2:>9}" for c2 in cells))

    print("\n(数字は 直線1本の残差 ÷ その素子の床。1.00以下なら1本で足りる。— は測定範囲外)")
    print(f"\n{'素子':>9}  1本が持つ幅")
    for dev in mos.DEVICES:
        b = held[dev]
        print(f"{dev:>9}  {(str(b) + ' °C以上') if b else '10 °C未満'}")

    ok = [d for d, b in held.items() if b and b >= W1_SPAN]
    print(f"\n=== W1 1本が {W1_SPAN:.0f} °C 以上持つ素子 ===")
    print(f"  {len(ok)}/{len(mos.DEVICES)}  "
          f"{'PASS' if len(ok) >= 5 else 'FAIL'} (基準: 6中5以上)")
    vals = [b for b in held.values() if b]
    if vals:
        print(f"\n=== W2 幅のばらつき ===")
        print(f"  最小 {min(vals)} °C  最大 {max(vals)} °C  "
              f"比 {max(vals)/min(vals):.1f}倍  "
              f"{'個体ごとに変える必要は薄い' if max(vals)/min(vals) <= 3 else '個体ごとに変える必要がある'}")
        print(f"\n=== W3 190 °C(自動車の -40〜150 °C)を覆うのに要る直線の本数 ===")
        print(f"  最も狭い素子で {int(np.ceil(190 / min(vals)))} 本  "
              f"→ 指紋は 36バイト × {int(np.ceil(190 / min(vals)))} = "
              f"{36 * int(np.ceil(190 / min(vals)))} バイト")
        print(f"  **190 °C は自動車の範囲として置いた仮定であり、測定範囲外への外挿である**")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with OUT_TSV.open("w") as fh:
        fh.write("device\tspan_C\tresidual_over_floor\tn\tfloor\n")
        for r in rows:
            fh.write(f"{r['dev']}\t{r['span']}\t{r['ratio']:.4f}\t{r['n']}\t{r['floor']:.6g}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
