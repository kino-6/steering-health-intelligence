#!/usr/bin/env python3
"""Does the SOTIF-shaped case appear in the recall record at all? (docs/191)

docs/190 found that 1,346,528 vehicles had their replace/do-not-replace
decision routed through a record held inside the EPS ECU -- stored fault
codes and torque-sensor signal loss. That decision is a fault decision, so
it sits under ISO 26262, not ISO 21448.

The SOTIF-shaped case is different: the part has not failed, no code is
set, but its performance envelope has moved enough that a vehicle-level
function relying on that envelope no longer gets what it assumed. This
asks whether that shape appears anywhere in the US recall record.

Fixed before any count was read:

  population  vehicle recalls whose component name contains STEERING
  markers     driver-assistance dependency (lane keep / centering, ADAS,
              adaptive cruise, park assist, automated driving)
              degradation over time (degrad / wear / deteriorate / over time)
              absence of a fault code (no diagnostic/fault/trouble code,
              without setting a code, does not set a)
  unit        the campaign (CAMPNO), not the row
  strata      EPS (component name contains ELECTRIC POWER) vs all steering

A limit that cannot be removed, and it is the whole point: a recall records
a DEFECT. A SOTIF functional insufficiency is by definition not a defect,
so it is out of this instrument's scope by construction. A zero here means
"this instrument cannot see it", NOT "it does not happen". What a zero does
establish is that no EPS recall to date has been driven by an
assisted-function dependency -- which is a statement about where the money
and the decisions are today.

Data: NHTSA FLAT_RCL_POST_2010, US government work, public domain.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RCL = REPO_ROOT / ".nhtsa_flat" / "FLAT_RCL_POST_2010.txt"
OUT_TSV = REPO_ROOT / "data" / "eps_sotif_shape_scan.tsv"

I_CAMP, I_MAKE, I_COMP, I_TYPE, I_DEF, I_CON, I_ACT = 1, 2, 6, 10, 19, 20, 21

MARKERS = {
    "driver_assistance": re.compile(
        r"lane keep|lane centering|lane depart|driver assist|advanced driver"
        r"|adaptive cruise|park assist|parking assist|automated driving|autopilot|\bADAS\b",
        re.I,
    ),
    "degradation_over_time": re.compile(
        r"degrad\w+|\bwear\w*|deteriorat\w+|reduced (assist|performance)|over time", re.I
    ),
    "no_fault_code": re.compile(
        r"without (setting|any) (a )?(diagnostic|fault|trouble)"
        r"|no (diagnostic|fault|trouble) code|does not set a",
        re.I,
    ),
}


def main() -> None:
    camps: dict[str, tuple] = {}
    with open(RCL, encoding="latin-1") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < 25 or f[I_TYPE] != "V":
                continue
            comp = f[I_COMP].upper()
            if "STEERING" not in comp:
                continue
            txt = " ".join([f[I_DEF], f[I_CON], f[I_ACT]])
            hits = tuple(k for k, rx in MARKERS.items() if rx.search(txt))
            camps.setdefault(f[I_CAMP], (f[I_MAKE], "ELECTRIC POWER" in comp, hits, txt))

    eps = {k: v for k, v in camps.items() if v[1]}
    print(f"steering campaigns {len(camps)}   of which EPS {len(eps)}\n")
    print(f"{'marker':<24}{'all steering':>14}{'EPS':>8}")
    for k in MARKERS:
        a = sum(1 for v in camps.values() if k in v[2])
        e = sum(1 for v in eps.values() if k in v[2])
        print(f"{k:<24}{a:>14}{e:>8}")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("campno\tmake\tis_eps\tmarkers\texcerpt\n")
        for c, (mk, is_eps, hits, txt) in sorted(camps.items()):
            if not hits:
                continue
            out.write(f"{c}\t{mk}\t{int(is_eps)}\t{','.join(hits)}\t{' '.join(txt.split())[:300]}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
