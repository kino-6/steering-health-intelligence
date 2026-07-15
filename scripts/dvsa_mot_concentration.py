#!/usr/bin/env python3
"""Is the steering-failure rate concentrated in particular makes/models/fuels?

Follow-up to docs/148 (user question): (1) how concentrated are failures by
make and by model, (2) do EVs / new-entrant makes show elevated rates once
age is controlled (EV fleets are young, so raw rates mislead).

Single streaming pass over the 2025 result extract, reusing the pass-1
cache of steering-failed test_ids. Aggregations:
  make x age  -> age-adjusted comparison within age 3-10 (MOT mandatory from
                 age 3; 3-10 is where fleets overlap)
  model level -> within-make concentration (top models by failures)
  fuel x age  -> EL (electric) vs PE/DI within same ages
"""

from __future__ import annotations

import csv
import io
import sys
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

csv.field_size_limit(sys.maxsize)

REPO_ROOT = Path(__file__).resolve().parent.parent
D = REPO_ROOT / ".dvsa_mot"
YEAR = "2025"
OUT_TSV = REPO_ROOT / "data" / f"dvsa_mot_concentration_{YEAR}.tsv"
AGE_LO, AGE_HI = 3, 10

NEW_ENTRANTS = {"TESLA", "POLESTAR", "BYD", "MG", "ORA", "GWM ORA", "VINFAST", "NIO", "XPENG", "GENESIS", "CUPRA", "SMART"}


def main() -> None:
    steer_tests = set((D / "cache_steer_tests.txt").read_text().split())
    make_age = defaultdict(lambda: [0, 0])      # (make, age) -> [tests, fails]
    model_cnt = defaultdict(lambda: [0, 0])     # (make, model) -> [tests(3-10), fails]
    fuel_age = defaultdict(lambda: [0, 0])      # (fuel, age) -> [tests, fails]
    zf = zipfile.ZipFile(D / f"dft_test_result_extracts_{YEAR}.zip")
    for name in [n for n in zf.namelist() if n.endswith(".csv")]:
        fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
        reader = csv.reader(fh)
        header = [h.strip().lower() for h in next(reader)]
        ix = {k: header.index(k) for k in ("test_id", "test_class_id", "test_type", "test_result", "test_date", "first_use_date", "make", "model", "fuel_type")}
        for row in reader:
            try:
                if row[ix["test_class_id"]] != "4" or row[ix["test_type"]] != "NT":
                    continue
                if row[ix["test_result"]] not in ("P", "F", "PRS"):
                    continue
                age = (date.fromisoformat(row[ix["test_date"]]) - date.fromisoformat(row[ix["first_use_date"]])).days / 365.25
            except Exception:
                continue
            if not (0 <= age <= 30):
                continue
            a = int(age)
            hit = row[ix["test_id"]] in steer_tests
            mk = row[ix["make"]].strip().upper()
            r = make_age[(mk, a)]; r[0] += 1; r[1] += hit
            fu = row[ix["fuel_type"]].strip().upper()
            f = fuel_age[(fu, a)]; f[0] += 1; f[1] += hit
            if AGE_LO <= a <= AGE_HI:
                md = row[ix["model"]].strip().upper()
                m = model_cnt[(mk, md)]; m[0] += 1; m[1] += hit
        print(f"done {name}")

    lines = []

    # --- age-adjusted make rates (direct standardization to overall age mix, ages 3-10)
    overall_age_tests = defaultdict(int)
    for (mk, a), (t, f) in make_age.items():
        if AGE_LO <= a <= AGE_HI:
            overall_age_tests[a] += t
    tot_ref = sum(overall_age_tests.values())
    weights = {a: overall_age_tests[a] / tot_ref for a in overall_age_tests}
    make_std = {}
    for mk in {m for (m, _) in make_age}:
        cells = {a: make_age[(mk, a)] for a in range(AGE_LO, AGE_HI + 1) if (mk, a) in make_age}
        n = sum(t for t, _ in cells.values())
        if n < 20000 or len(cells) < (AGE_HI - AGE_LO):
            continue
        std = sum(weights[a] * (cells[a][1] / cells[a][0]) for a in cells if cells[a][0] > 0)
        make_std[mk] = (std, n)
    lines.append("== make age-standardized steering-fail rate (ages 3-10, >=20k tests) ==")
    lines.append("make\ttests_3_10\tstd_rate\tnew_entrant")
    for mk, (std, n) in sorted(make_std.items(), key=lambda kv: -kv[1][0]):
        lines.append(f"{mk}\t{n}\t{std:.5f}\t{'YES' if mk in NEW_ENTRANTS else ''}")

    # --- concentration: share of failures carried by top models (ages 3-10)
    tot_fail = sum(f for _, f in model_cnt.values())
    tot_tests = sum(t for t, _ in model_cnt.values())
    top = sorted(model_cnt.items(), key=lambda kv: -kv[1][1])
    cum = 0
    lines.append("")
    lines.append(f"== model concentration (ages {AGE_LO}-{AGE_HI}): total fails {tot_fail}, tests {tot_tests} ==")
    lines.append("rank\tmake\tmodel\ttests\tfails\trate\tcum_fail_share")
    for i, ((mk, md), (t, f)) in enumerate(top[:25], 1):
        cum += f
        lines.append(f"{i}\t{mk}\t{md}\t{t}\t{f}\t{f/t:.5f}\t{cum/tot_fail:.3f}")
    n_models_50 = 0; c = 0
    for (_, _), (t, f) in top:
        c += f; n_models_50 += 1
        if c >= tot_fail * 0.5:
            break
    lines.append(f"models carrying 50% of failures: {n_models_50} (of {len(model_cnt)} models)")

    # --- fuel x age (EL vs PE vs DI)
    lines.append("")
    lines.append("== fuel type x age steering-fail rate ==")
    lines.append("fuel\tage\ttests\tfails\trate")
    for fu in ("EL", "HY", "PE", "DI"):
        for a in range(AGE_LO, AGE_HI + 1):
            t, f = fuel_age.get((fu, a), (0, 0))
            if t >= 5000:
                lines.append(f"{fu}\t{a}\t{t}\t{f}\t{f/t:.5f}")

    OUT_TSV.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:40]))
    print(f"wrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
