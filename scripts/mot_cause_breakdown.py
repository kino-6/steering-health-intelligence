#!/usr/bin/env python3
"""Break the MOT precedence down by cause (docs/206 -> docs/207).

Executes the protocol pre-registered in docs/206 without modification.

docs/150 showed that a car carrying only an advisory in the steering group
fails steering the next year at up to 24.1x the clean rate, treating steering
as one undivided thing. docs/189 looked at the nine Electronic power steering
codes alone and found 64 vehicles in 21.77M -- not testable. The 59 general
power-steering codes for cars, 25 of them with paired advisory and fail
wording, had never been used.

    M1  does the precedence rate differ by cause family
    M2  is it cause-specific, S_X = P(fail X | advisory X) / P(fail X | any advisory)
    M3  does a wiring corrosion or damage advisory precede a FUNCTION failure
        -- inoperative, malfunctioning, warning lamp -- which is corrosion
        acting through intermittent contact, reached from the field side

Data: DVSA MOT test extracts 2024/2025, Open Government Licence v3.0.
Contains public sector information licensed under the OGL v3.0.
"""

from __future__ import annotations

import csv
import io
import re
import sys
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np

# Some MOT rows carry a field far past the default 128 KB cap; the working
# precedent (mot_advisory_longitudinal.py) lifts it entirely.
csv.field_size_limit(sys.maxsize)

REPO_ROOT = Path(__file__).resolve().parent.parent
D = REPO_ROOT / ".dvsa_mot"
OUT_TSV = REPO_ROOT / "data" / "mot_cause_breakdown.tsv"

FAIL_TYPES, SIGN_TYPES = {"F", "P"}, {"A", "M"}
AGE_BANDS = [(4, 7), (8, 11), (12, 15), (16, 25)]
N_FLOOR_M2, N_FLOOR_M3 = 1000, 100

# Families, fixed in docs/206. Order matters: first match wins.
FAMILIES = [
    ("corrosion", r"corrod"),
    ("damage", r"damag|fractur|split|cut\b"),
    ("leak", r"leak|seepage|fluid|reservoir"),
    ("security", r"insecure|loose|missing|removed|disconnect"),
    ("function", r"inoperative|malfunction|warning lamp|not working"),
    ("geometry", r"misalign|fouling"),
    ("modification", r"modif|repair"),
]
FAM_IX = {n: i for i, (n, _) in enumerate(FAMILIES)}
WIRING = re.compile(r"wiring")


def build_ps_rfr():
    """rfr_id -> (family bit, is_wiring) for the 59 car power-steering codes."""
    fam, wiring = {}, set()
    for row in csv.DictReader(open(D / "item_detail.csv", encoding="latin-1")):
        if row["test_class_id"] != "4":
            continue
        manual = (row["rfr_insp_manual_desc"] or "").lower()
        desc = (row["rfr_desc"] or "").lower()
        adv = (row["rfr_advisory_text"] or "").lower()
        if "power steering" not in manual and "power steering" not in desc:
            continue
        blob = desc + " " + adv
        for name, pat in FAMILIES:
            if re.search(pat, blob):
                fam[row["rfr_id"]] = FAM_IX[name]
                break
        else:
            fam[row["rfr_id"]] = -1
        if WIRING.search(blob):
            wiring.add(row["rfr_id"])
    print(f"power-steering rfr_ids (class 4): {len(fam)}, wiring-related: {len(wiring)}")
    return fam, wiring


def scan_items(year: str, fam, wiring):
    """test_id -> (fail family mask, sign family mask, sign-is-wiring flag)."""
    f_mask, s_mask, s_wire = defaultdict(int), defaultdict(int), set()
    zf = zipfile.ZipFile(D / f"dft_test_item_extracts_{year}.zip")
    for name in sorted(n for n in zf.namelist() if n.endswith(".csv")):
        fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
        r = csv.reader(fh)
        h = [x.strip().lower() for x in next(r)]
        i_t, i_r, i_ty = h.index("test_id"), h.index("rfr_id"), h.index("rfr_type_code")
        for row in r:
            rid = row[i_r]
            if rid not in fam:
                continue
            fi = fam[rid]
            if fi < 0:
                continue
            bit, ty, tid = 1 << fi, row[i_ty], row[i_t]
            if ty in FAIL_TYPES:
                f_mask[tid] |= bit
            elif ty in SIGN_TYPES:
                s_mask[tid] |= bit
                if rid in wiring:
                    s_wire.add(tid)
    print(f"{year}: PS fail-tier tests {len(f_mask):,}, sign-tier {len(s_mask):,}, "
          f"wiring-sign {len(s_wire):,}")
    return f_mask, s_mask, s_wire


def scan_results_2024(f_mask, s_mask, s_wire):
    all_v, vf, vs, vw = [], {}, {}, set()
    zf = zipfile.ZipFile(D / "dft_test_result_extracts_2024.zip")
    for name in sorted(n for n in zf.namelist() if n.endswith(".csv")):
        fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
        r = csv.reader(fh)
        h = [x.strip().lower() for x in next(r)]
        ix = {k: h.index(k) for k in
              ("test_id", "vehicle_id", "test_class_id", "test_type", "test_result")}
        for row in r:
            try:
                if row[ix["test_class_id"]] != "4" or row[ix["test_type"]] != "NT":
                    continue
                if row[ix["test_result"]] not in ("P", "F", "PRS"):
                    continue
                vid = int(row[ix["vehicle_id"]])
            except Exception:
                continue
            all_v.append(vid)
            tid = row[ix["test_id"]]
            if tid in f_mask:
                vf[vid] = vf.get(vid, 0) | f_mask[tid]
            if tid in s_mask:
                vs[vid] = vs.get(vid, 0) | s_mask[tid]
            if tid in s_wire:
                vw.add(vid)
        print(f"  2024 {Path(name).name}: cum {len(all_v):,}")
    arr = np.unique(np.array(all_v, dtype=np.int64))
    print(f"2024 class-4 NT vehicles {len(arr):,}; PS-fail {len(vf):,}; PS-sign {len(vs):,}")
    return arr, vf, vs, vw


def scan_results_2025(all24, vf24, vs24, vw24, f_mask25):
    # group -> [n, fail_any, per-family fail counts]
    tally = defaultdict(lambda: [0, 0] + [0] * len(FAMILIES))
    zf = zipfile.ZipFile(D / "dft_test_result_extracts_2025.zip")
    for name in sorted(n for n in zf.namelist() if n.endswith(".csv")):
        fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
        r = csv.reader(fh)
        h = [x.strip().lower() for x in next(r)]
        ix = {k: h.index(k) for k in
              ("test_id", "vehicle_id", "test_class_id", "test_type", "test_result",
               "test_date", "first_use_date")}
        for row in r:
            try:
                if row[ix["test_class_id"]] != "4" or row[ix["test_type"]] != "NT":
                    continue
                if row[ix["test_result"]] not in ("P", "F", "PRS"):
                    continue
                vid = int(row[ix["vehicle_id"]])
                age = (date.fromisoformat(row[ix["test_date"]])
                       - date.fromisoformat(row[ix["first_use_date"]])).days / 365.25
            except Exception:
                continue
            i = np.searchsorted(all24, vid)
            if i >= len(all24) or all24[i] != vid:
                continue
            if not any(lo <= age <= hi for lo, hi in AGE_BANDS):
                continue
            m25 = f_mask25.get(row[ix["test_id"]], 0)
            groups = ["all"]
            if vid in vf24:
                groups.append("fail24")
            elif vid in vs24:
                groups.append("sign24")
                for nm, i2 in FAM_IX.items():
                    if vs24[vid] & (1 << i2):
                        groups.append(f"sign24:{nm}")
                if vid in vw24:
                    groups.append("sign24:wiring")
            else:
                groups.append("clean24")
            for g in groups:
                rec = tally[g]
                rec[0] += 1
                rec[1] += bool(m25)
                for nm, i2 in FAM_IX.items():
                    rec[2 + i2] += bool(m25 & (1 << i2))
        print(f"  2025 {Path(name).name}")
    return tally


def main() -> int:
    fam, wiring = build_ps_rfr()
    f24, s24, w24 = scan_items("2024", fam, wiring)
    all24, vf24, vs24, vw24 = scan_results_2024(f24, s24, w24)
    del f24, s24, w24
    f25, _, _ = scan_items("2025", fam, wiring)
    tally = scan_results_2025(all24, vf24, vs24, vw24, f25)

    clean = tally["clean24"]
    base_any = clean[1] / clean[0] if clean[0] else float("nan")
    print("\n" + "=" * 84)
    print(f"{'group':<22}{'n':>12}{'PS fail%':>11}{'lift':>8}   per-family fail%")
    rows = []
    for g in ["clean24", "sign24", "fail24"] + \
             [f"sign24:{n}" for n, _ in FAMILIES] + ["sign24:wiring"]:
        rec = tally.get(g)
        if not rec or rec[0] == 0:
            print(f"{g:<22}{0:>12}   (no vehicles)")
            continue
        rate = rec[1] / rec[0]
        per = "  ".join(f"{n[:4]}={rec[2+i]/rec[0]:.3%}" for n, i in FAM_IX.items())
        print(f"{g:<22}{rec[0]:>12,}{rate:>10.3%}{rate/base_any:>8.1f}   {per}")
        rows.append((g, rec[0], rate, rate / base_any,
                     *[rec[2 + i] / rec[0] for i in range(len(FAMILIES))]))

    print("\nM2 cause specificity  S_X = P(fail X | sign X) / P(fail X | any PS sign)")
    any_sign = tally["sign24"]
    spec, tested = [], 0
    for nm, i in FAM_IX.items():
        rec = tally.get(f"sign24:{nm}")
        if not rec or rec[0] < N_FLOOR_M2:
            print(f"  {nm:<14} n={0 if not rec else rec[0]:>9,}  untestable (n < {N_FLOOR_M2:,})")
            continue
        tested += 1
        num = rec[2 + i] / rec[0]
        den = any_sign[2 + i] / any_sign[0] if any_sign[0] else float("nan")
        s = num / den if den else float("nan")
        spec.append(s >= 2.0)
        print(f"  {nm:<14} n={rec[0]:>9,}  same-family {num:.3%} vs any-sign {den:.3%}"
              f"  S = {s:.2f}")
    if tested:
        print(f"  -> {sum(spec)}/{tested} families at S >= 2.0 : "
              f"{'cause-specific' if sum(spec) * 2 >= tested else 'NOT cause-specific'}")
    else:
        print("  -> no family reaches the n floor; M2 untestable")

    print("\nM3 wiring advisory -> function failure")
    w = tally.get("sign24:wiring")
    fi = FAM_IX["function"]
    if not w or w[0] < N_FLOOR_M3:
        print(f"  n = {0 if not w else w[0]:,} < {N_FLOOR_M3} -> untestable. "
              f"No multiplier is reported.")
    else:
        r_w = w[2 + fi] / w[0]
        r_c = clean[2 + fi] / clean[0]
        lift = r_w / r_c if r_c else float("nan")
        ok = lift >= 3.0
        print(f"  wiring-advisory n = {w[0]:,}  function-fail {r_w:.3%}")
        print(f"  clean           n = {clean[0]:,}  function-fail {r_c:.3%}")
        print(f"  lift = {lift:.1f}x -> {'BRIDGE' if ok else 'no bridge (needs 3.0x)'}")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("group\tn\tps_fail_rate\tlift_vs_clean\t"
                  + "\t".join(f"fail_{n}" for n, _ in FAMILIES) + "\n")
        for r in rows:
            out.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                                for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
