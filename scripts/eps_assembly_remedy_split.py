#!/usr/bin/env python3
"""What does "replace the assembly" actually mean? (docs/190)

docs/189 counted EPS steering recalls whose corrective action mentioned
replacing an assembly and reported 23 campaigns / 1,398,556 vehicles. That
match was too loose: it accepted any campaign whose remedy text contained
both "replac" and "assembl" anywhere, which swept in 14V153000 (1,373,177
vehicles) whose remedy is "dealers will perform one of four bulletins" --
not an assembly replacement at all. That single campaign was 98% of the
count.

This tightens the match to remedies that name the steering gear or rack
assembly as the thing replaced, then splits them by whether the remedy is
applied to every vehicle or only to vehicles that pass a check.

Fixed before any count was read:

  population  vehicle recalls, component name contains ELECTRIC POWER and
              STEERING, remedy names a gear/rack assembly replacement
  metric      campaigns and POTAFF, split unconditional vs conditional
  conditional remedy text contains inspect / as necessary / if necessary /
              as needed / if found / any that / that are not
  unit        the campaign (CAMPNO), not the row

A limit that cannot be removed: POTAFF is vehicles potentially affected,
not vehicles actually repaired, and a short remedy sentence that omits the
part name is not counted. Both push the figure down, so it is a floor.

Data: NHTSA FLAT_RCL_POST_2010, US government work, public domain.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RCL = REPO_ROOT / ".nhtsa_flat" / "FLAT_RCL_POST_2010.txt"
OUT_TSV = REPO_ROOT / "data" / "eps_assembly_remedy_split.tsv"

I_CAMP, I_MAKE, I_MODEL, I_YEAR, I_COMP, I_TYPE, I_POT, I_ACT = 1, 2, 3, 4, 6, 10, 11, 21

GEAR_FIRST = re.compile(r"replac\w*[^.]{0,120}\b(gear|rack)\s*(and pinion\s*)?assembl", re.I)
GEAR_LAST = re.compile(r"\b(steering gear|rack)\s*(and pinion\s*)?assembl\w*[^.]{0,80}\breplac", re.I)
# "conditional" means the remedy is applied to some vehicles, not all: either
# an inspection step, an "as necessary" hedge, or an if-clause governing the
# replacement. The if-clause arm matters -- 14V286000 replaces the rack only
# "if a vehicle shows a history of a loss of motor position sensor signal",
# which the hedge words alone do not catch.
CONDITIONAL = re.compile(
    r"\binspect\w*|as necessary|if necessary|as needed|if needed|if found"
    r"|any that\b|that (are|is) not\b"
    r"|\bif\b[^.]{0,250}?\breplac|\breplac\w*[^.]{0,80}?\bif\b",
    re.I,
)
# What the check is made against, when the remedy is conditional.
LOT_BASIS = re.compile(r"serial number|lot code|part number|production (date|range)", re.I)
HISTORY_BASIS = re.compile(r"history of|stored|logged|diagnostic trouble code|\bDTC\b", re.I)


def main() -> None:
    camps: dict[str, tuple] = {}
    with open(RCL, encoding="latin-1") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < 25 or f[I_TYPE] != "V":
                continue
            comp = f[I_COMP].upper()
            if "STEERING" not in comp or "ELECTRIC POWER" not in comp:
                continue
            act = f[I_ACT]
            if not (GEAR_FIRST.search(act) or GEAR_LAST.search(act)):
                continue
            try:
                pot = int(f[I_POT])
            except ValueError:
                pot = 0
            cond = bool(CONDITIONAL.search(act))
            basis = ""
            if cond:
                if HISTORY_BASIS.search(act):
                    basis = "operating history"
                elif LOT_BASIS.search(act):
                    basis = "manufacturing lot"
                else:
                    basis = "unstated"
            # A campaign spans several model rows; POTAFF repeats on each.
            camps.setdefault(f[I_CAMP], (f[I_MAKE], f[I_MODEL], f[I_YEAR], pot, cond, basis, act))

    rows = sorted(camps.items(), key=lambda kv: -kv[1][3])
    total = sum(v[3] for v in camps.values())
    cond_n = sum(1 for v in camps.values() if v[4])
    cond_u = sum(v[3] for v in camps.values() if v[4])

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("campno\tmake\tmodel\tyear\tpotaff\tconditional\tbasis\tcorrective_action\n")
        for c, (mk, md, yr, pot, cond, basis, act) in rows:
            act1 = " ".join(act.split())
            out.write(f"{c}\t{mk}\t{md}\t{yr}\t{pot}\t{int(cond)}\t{basis}\t{act1}\n")

    print(f"campaigns {len(camps)}  vehicles {total:,}")
    print(f"  conditional (checked first) {cond_n:>3}  {cond_u:>10,}")
    print(f"  unconditional (all units)   {len(camps)-cond_n:>3}  {total-cond_u:>10,}")
    print()
    for c, (mk, md, yr, pot, cond, basis, act) in rows:
        tag = f"cond/{basis}" if cond else "all"
        print(f"{c}  {mk:<10} {yr}  {pot:>9,}  {tag}")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
