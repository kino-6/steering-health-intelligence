#!/usr/bin/env python3
"""Translate the measured precursor into thermal headroom loss (docs/170).

docs/169 identified the gap that keeps docs/167 from being a SOTIF claim:
a parameter drift is not yet a functional insufficiency. This closes that
step for the thermal path, using only quantities already measured.

The chain:

  1. docs/167's indicator is the residual of on-resistance after each
     device's OWN temperature coefficient is removed. Since on-resistance
     rises with junction temperature, a residual at constant package
     temperature means the junction is running hotter for the same
     dissipation -- i.e. the junction-to-package thermal resistance grew.

  2. Dividing the residual by the measured temperature coefficient turns
     it into that extra junction temperature rise, in degrees.

  3. Thermal derating limits sustained assist. If thermal resistance rises
     by factor k, the power that reaches the same limit falls to 1/k, so
     the sustainable assist power falls by (1 - 1/k).

Step 3 needs the healthy junction-to-package rise, which this dataset does
not report, so it is swept rather than assumed at one value.

Validity check available inside the data: the measured temperature
coefficient should land in the range published for silicon MOSFETs
(roughly 0.5-0.8 %/degC). If it does not, the interpretation in step 1 is
wrong and the rest does not follow.

Data: NASA PCoE, public domain.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "thermal_headroom_translation.tsv"
DTJ0_SWEEP = (20.0, 40.0, 60.0)      # healthy junction-to-package rise [degC], swept
SI_TEMPCO = (0.5, 0.8)               # published range for silicon MOSFETs [%/degC]


def main() -> None:
    rows = [r for r in csv.DictReader(open(REPO_ROOT / "data" / "mosfet_precursor_v2.tsv"),
                                      delimiter="\t")]
    for r in rows:
        r["device"], r["run"] = int(float(r["device"])), int(float(r["run"]))
        for k in ("R_on", "T_pkg", "delta_vs_baseline"):
            r[k] = float(r[k])

    out = []
    print(f"{'dev':>4} {'tempco[%/C]':>12} | " +
          " ".join(f"{'run'+str(r):>18}" for r in (5, 6, 7)))
    print(f"{'':>4} {'':>12} | " + " ".join(f"{'dTj / headroom':>18}" for _ in (5, 6, 7)))
    print("-" * 76)
    tempcos = []
    for dev in sorted({r["device"] for r in rows}):
        g = [r for r in rows if r["device"] == dev]
        fit = [r for r in g if r["run"] <= 3]
        a, b = np.polyfit([r["T_pkg"] for r in fit], [r["R_on"] for r in fit], 1)
        base = a * g[0]["T_pkg"] + b
        tempco = a / base * 100.0
        tempcos.append(tempco)
        cells = []
        for run in (5, 6, 7):
            d = [r for r in g if r["run"] == run][0]["delta_vs_baseline"]
            dtj = d * 100.0 / tempco
            # headroom loss at the mid sweep point, reported per point in the TSV
            k = 1 + dtj / DTJ0_SWEEP[1]
            cells.append(f"{dtj:>6.1f}C /{1 - 1 / k:>7.0%}")
            for dtj0 in DTJ0_SWEEP:
                kk = 1 + dtj / dtj0
                out.append((dev, run, tempco, d, dtj, dtj0, 1 - 1 / kk))
        print(f"{dev:>4} {tempco:>12.3f} | " + " ".join(f"{c:>18}" for c in cells))

    lo, hi = min(tempcos), max(tempcos)
    ok = SI_TEMPCO[0] <= lo and hi <= SI_TEMPCO[1]
    print(f"\n妥当性チェック: 実測tempco {lo:.3f}〜{hi:.3f} %/degC  "
          f"(Si MOSFET公表値 {SI_TEMPCO[0]}〜{SI_TEMPCO[1]}) → "
          f"{'整合' if ok else '要検討: 一部が公表範囲外'}")

    print("\n=== アシスト熱余裕の損失（健全時の接合温度上昇ΔTj_0を掃引）===")
    print(f"{'run':>5} " + "".join(f"{'ΔTj_0=' + str(int(v)) + 'C':>16}" for v in DTJ0_SWEEP))
    for run in (5, 6, 7):
        cells = []
        for dtj0 in DTJ0_SWEEP:
            v = [o[6] for o in out if o[1] == run and o[5] == dtj0]
            cells.append(f"{min(v):>6.0%}..{max(v):<7.0%}")
        print(f"{run:>5} " + "".join(f"{c:>16}" for c in cells))

    with OUT_TSV.open("w") as fh:
        fh.write("device\trun\ttempco_pct_per_C\tdelta\tdelta_Tj_C\t"
                 "assumed_healthy_dTj_C\theadroom_loss\n")
        for o in out:
            fh.write("\t".join(f"{v:.6f}" if isinstance(v, float) else str(v) for v in o) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
