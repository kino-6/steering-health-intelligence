#!/usr/bin/env python3
"""Steering failure-mode split by model (docs/157).

docs/151 matched the top-rate models against public defect records and found
TWO types: (1) a known defect family (Vauxhall Corsa -- EPS column) and
(2) usage-driven wear (Vivaro / Trafic vans -- track rod ends). It left
Fiat 500X and Jeep Renegade unmatched, refusing to fill them by guessing.

Rather than guess from press coverage, this classifies the actual MOT
failure ITEMS. Each steering reason-for-rejection maps to a mode from the
DVSA item hierarchy, so 500X / Renegade can be placed on the same axis as
the reference models -- from data, reproducibly.

Modes (from Vehicle > Steering > ... hierarchy, fixed before running):
  linkage_wear    track rod end / drag link end / ball joint / linkage
  column_coupling steering column / shaft / coupling  (the Corsa family)
  rack_gear       steering rack / box / gear
  power_steering  pump / rams / pipes / PAS operation
  other_steering  everything else under Steering

Only fail-tier records count (rfr_type_code F or P), matching docs/150.
Data: DVSA MOT test and item extracts 2025 (OGL v3.0).
"""

from __future__ import annotations

import csv
import io
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

csv.field_size_limit(sys.maxsize)

REPO_ROOT = Path(__file__).resolve().parent.parent
D = REPO_ROOT / ".dvsa_mot"
OUT_TSV = REPO_ROOT / "data" / "dvsa_mot_mode_split_2025.tsv"

FAIL_TYPES = {"F", "P"}
TARGETS = {  # (make, model prefix) -> label
    ("FIAT", "500X"): "Fiat 500X (照合対象)",
    ("JEEP", "RENEGADE"): "Jeep Renegade (照合対象)",
    ("VAUXHALL", "CORSA"): "Vauxhall Corsa (参照:欠陥型)",
    ("VAUXHALL", "VIVARO"): "Vauxhall Vivaro (参照:摩耗型)",
    ("RENAULT", "TRAFIC"): "Renault Trafic (参照:摩耗型)",
}
# CORSAVAN is a van derivative: excluded, because separating van usage from
# passenger-car usage is the whole point of this comparison.
EXCLUDE_MODELS = {("VAUXHALL", "CORSAVAN")}
MODE_ORDER = ["linkage_wear", "column_coupling", "rack_gear", "power_steering", "other_steering"]
AGE_MIN, AGE_MAX = 3, 10   # matches the population docs/151 ranked models on


def classify(chain_names: list[str], desc: str = "") -> str:
    """Classify by the DVSA item hierarchy path only.

    The free-text inspection manual is NOT used: many column/rack entries
    mention "linkage" in prose, which silently folded them into the wear
    bucket in the first run."""
    blob = " > ".join(chain_names).lower()
    if any(w in blob for w in ("track rod", "drag link", "ball joint", "linkage")):
        return "linkage_wear"
    if any(w in blob for w in ("steering column", "steering shaft", "coupling", "universal joint")):
        return "column_coupling"
    if any(w in blob for w in ("steering rack", "steering box", "steering gear")):
        return "rack_gear"
    if "power steering" in blob:
        return "power_steering"
    return "other_steering"


def build_rfr_modes():
    groups = {}
    for row in csv.DictReader(open(D / "item_group.csv")):
        groups[(row["test_item_id"], row["test_class_id"])] = (row["parent_id"], row["item_name"])

    def chain(item_id, cls):
        names, seen, cur = [], set(), item_id
        while True:
            k = (cur, cls)
            if k in seen or k not in groups:
                break
            seen.add(k)
            parent, name = groups[k]
            names.append(name)
            if parent == cur:
                break
            cur = parent
        return list(reversed(names))

    modes, descs = {}, {}
    for row in csv.DictReader(open(D / "item_detail.csv")):
        if row["test_class_id"] != "4":
            continue
        ch = chain(row["test_item_id"], "4")
        blob = " | ".join(ch).lower() + " | " + row["rfr_insp_manual_desc"].lower() + " | " + row["rfr_desc"].lower()
        if "steering" not in blob:
            continue
        modes[row["rfr_id"]] = classify(ch)
        descs[row["rfr_id"]] = " > ".join(ch[1:]) + ": " + row["rfr_desc"]
    print(f"steering rfr_ids (class 4): {len(modes)}")
    return modes, descs


def scan_items(modes):
    """test_id -> set of (mode, rfr_id) for fail-tier steering items."""
    out = defaultdict(set)
    zf = zipfile.ZipFile(D / "dft_test_item_extracts_2025.zip")
    for name in [n for n in zf.namelist() if n.endswith(".csv")]:
        fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
        r = csv.reader(fh)
        header = [h.strip().lower() for h in next(r)]
        i_t, i_r, i_ty = header.index("test_id"), header.index("rfr_id"), header.index("rfr_type_code")
        for row in r:
            m = modes.get(row[i_r])
            if m and row[i_ty] in FAIL_TYPES:
                out[row[i_t]].add((m, row[i_r]))
        print(f"  items {name}: cum tests with steering fail {len(out):,}")
    return out


def scan_results(test_modes):
    tests = defaultdict(int)
    fails = defaultdict(int)
    mode_cnt = defaultdict(lambda: defaultdict(int))
    item_cnt = defaultdict(lambda: defaultdict(int))
    zf = zipfile.ZipFile(D / "dft_test_result_extracts_2025.zip")
    for name in [n for n in zf.namelist() if n.endswith(".csv")]:
        fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
        r = csv.reader(fh)
        header = [h.strip().lower() for h in next(r)]
        ix = {k: header.index(k) for k in ("test_id", "test_class_id", "test_type", "test_result",
                                           "make", "model", "test_date", "first_use_date")}
        for row in r:
            if row[ix["test_class_id"]] != "4" or row[ix["test_type"]] != "NT":
                continue
            if row[ix["test_result"]] not in ("P", "F", "PRS"):
                continue
            try:
                age = int(row[ix["test_date"]][:4]) - int(row[ix["first_use_date"]][:4])
            except Exception:
                continue
            if not (AGE_MIN <= age <= AGE_MAX):
                continue
            mk, md = row[ix["make"]].strip().upper(), row[ix["model"]].strip().upper()
            if (mk, md) in EXCLUDE_MODELS:
                continue
            label = None
            for (tm, tmd), lab in TARGETS.items():
                if mk == tm and md.startswith(tmd):
                    label = lab
                    break
            if label is None:
                continue
            tests[label] += 1
            ms = test_modes.get(row[ix["test_id"]])
            if ms:
                fails[label] += 1
                for m, rid in ms:
                    mode_cnt[label][m] += 1
                    item_cnt[label][rid] += 1
        print(f"  results {name}: cum matched tests {sum(tests.values()):,}")
    return tests, fails, mode_cnt, item_cnt


def main() -> None:
    modes, descs = build_rfr_modes()
    test_modes = scan_items(modes)
    tests, fails, mode_cnt, item_cnt = scan_results(test_modes)

    with OUT_TSV.open("w") as fh:
        fh.write("model\ttests\tsteering_fails\tfail_rate\t" + "\t".join(f"{m}_share" for m in MODE_ORDER) + "\n")
        print(f"\n{'model':<30}{'tests':>9}{'fails':>8}{'rate':>8}   " + "".join(f"{m:>16}" for m in MODE_ORDER))
        for lab in TARGETS.values():
            n, f = tests[lab], fails[lab]
            if n == 0:
                continue
            tot_modes = sum(mode_cnt[lab].values()) or 1
            shares = [mode_cnt[lab][m] / tot_modes for m in MODE_ORDER]
            counts = [mode_cnt[lab][m] for m in MODE_ORDER]
            print(f"{lab:<30}{n:>9,}{f:>8,}{f/n:>8.2%}   "
                  + "".join(f"{c:>7,}({s:>5.1%}) " for c, s in zip(counts, shares)))
            fh.write(f"{lab}\t{n}\t{f}\t{f/n:.5f}\t" + "\t".join(f"{s:.4f}" for s in shares) + "\n")
        print()
        for lab in TARGETS.values():
            if tests[lab] == 0:
                continue
            cover = sum(c for rid, c in item_cnt[lab].items() if "dust cover" in descs.get(rid, "").lower())
            play = sum(c for rid, c in item_cnt[lab].items()
                       if ("play" in descs.get(rid, "").lower() or "worn" in descs.get(rid, "").lower()))
            ratio = cover / play if play else float("inf")
            print(f"[{lab}] ダストカバー系 {cover:,} / ガタ・摩耗系 {play:,} = {ratio:.2f}")
            top = sorted(item_cnt[lab].items(), key=lambda kv: -kv[1])[:5]
            print(f"[{lab}] 上位の不合格項目")
            for rid, c in top:
                print(f"   {c:>7,}  {descs.get(rid, rid)[:96]}")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
