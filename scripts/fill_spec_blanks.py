#!/usr/bin/env python3
"""Fill two of docs/225's six blanks (docs/226 -> docs/227).

Executes the protocol pre-registered in docs/226 without modification.

A. Fingerprint sweep width. docs/197's figure came from the test rig's own
   schedule and does not transfer, so the question is what operating range a
   real vehicle visits. The ratio between what ONE drive covers and what the
   model covers is how far short a single-drive fingerprint falls.

B. Retention. A record has to live until the vehicle is next certain to reach
   a workshop, and the UK MOT is compulsory, so the interval between
   consecutive tests bounds it. docs/226 fixed the 90th percentile as the
   figure to specify, before the distribution was seen.

commaSteeringControl carries no temperature, so the axis a fingerprint most
needs is not determined here. The MOT interval is an upper bound, since cars
visit garages between tests, which makes the retention figure conservative.

Data: commaSteeringControl (MIT) / DVSA MOT extracts 2024-2025 (OGL v3.0).
"""

from __future__ import annotations

import csv
import io
import sys
import zipfile
from datetime import date
from pathlib import Path

import numpy as np

csv.field_size_limit(sys.maxsize)

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS = REPO_ROOT / ".public_log_cache"
MOT = REPO_ROOT / ".dvsa_mot"
OUT_TSV = REPO_ROOT / "data" / "fill_spec_blanks.tsv"

QUANTS = [(5, 95), (0.5, 99.5)]          # ranges covering 90% and 99%
RETENTION_Q = 90                         # docs/226, fixed before running


def part_a():
    print("=" * 78)
    print("A. what operating range does a real vehicle visit?")
    print("=" * 78)
    rows = []
    for model in sorted(p.name for p in LOGS.iterdir() if p.is_dir()):
        v_all, s_all, per_log_v, per_log_s = [], [], [], []
        for f in sorted((LOGS / model).glob("*.csv")):
            v, s = [], []
            with open(f, newline="") as fh:
                for row in csv.DictReader(fh):
                    try:
                        if row["latActive"] != "True" or row["steeringPressed"] == "True":
                            continue
                        v.append(float(row["vEgo"]))
                        s.append(abs(float(row["steeringAngleDeg"])))
                    except (ValueError, KeyError):
                        break
            if len(v) < 100:
                continue
            v_all.extend(v)
            s_all.extend(s)
            per_log_v.append(np.percentile(v, 95) - np.percentile(v, 5))
            per_log_s.append(np.percentile(s, 95) - np.percentile(s, 5))
        if not v_all:
            continue
        v_all, s_all = np.array(v_all), np.array(s_all)
        out = {}
        for lo, hi in QUANTS:
            out[(lo, hi)] = (float(np.percentile(v_all, hi) - np.percentile(v_all, lo)),
                             float(np.percentile(s_all, hi) - np.percentile(s_all, lo)))
        mv, ms = float(np.median(per_log_v)), float(np.median(per_log_s))
        rv, rs = out[(5, 95)]
        print(f"\n{model}   logs {len(per_log_v)}, samples {len(v_all):,}")
        print(f"   speed  : 90% range {rv:7.2f} m/s   99% range {out[(0.5,99.5)][0]:7.2f}")
        print(f"            one drive covers {mv:7.2f} m/s (median)"
              f"  -> short by {rv/mv:.2f}x")
        print(f"   |angle|: 90% range {rs:7.2f} deg   99% range {out[(0.5,99.5)][1]:7.2f}")
        print(f"            one drive covers {ms:7.2f} deg (median)"
              f"  -> short by {rs/ms:.2f}x")
        rows.append(("A", model, len(per_log_v), rv, mv, rv / mv, rs, ms, rs / ms))
    if rows:
        print(f"\nA2 one drive falls short by {min(r[5] for r in rows):.2f}"
              f"-{max(r[5] for r in rows):.2f}x on speed, "
              f"{min(r[8] for r in rows):.2f}-{max(r[8] for r in rows):.2f}x on angle")
    return rows


def part_b():
    print("\n" + "=" * 78)
    print("B. how long until the vehicle is next certain to reach a workshop?")
    print("=" * 78)
    dates = {}
    for year in ("2024", "2025"):
        zf = zipfile.ZipFile(MOT / f"dft_test_result_extracts_{year}.zip")
        for name in sorted(n for n in zf.namelist() if n.endswith(".csv")):
            fh = io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
            r = csv.reader(fh)
            h = [x.strip().lower() for x in next(r)]
            ix = {k: h.index(k) for k in
                  ("vehicle_id", "test_class_id", "test_type", "test_result", "test_date")}
            for row in r:
                try:
                    if row[ix["test_class_id"]] != "4" or row[ix["test_type"]] != "NT":
                        continue
                    if row[ix["test_result"]] not in ("P", "F", "PRS"):
                        continue
                    vid = int(row[ix["vehicle_id"]])
                    d = date.fromisoformat(row[ix["test_date"]])
                except Exception:
                    continue
                cur = dates.get(vid)
                if cur is None:
                    dates[vid] = [d, d]
                else:
                    if d < cur[0]:
                        cur[0] = d
                    if d > cur[1]:
                        cur[1] = d
        print(f"  scanned {year}: {len(dates):,} vehicles so far")
    gaps = np.array([(hi - lo).days for lo, hi in dates.values() if hi > lo])
    print(f"\n  vehicles with two or more tests: {len(gaps):,}")
    q = {p: float(np.percentile(gaps, p)) for p in (50, 75, RETENTION_Q, 95, 99)}
    for p in sorted(q):
        print(f"   p{p:<3} {q[p]:6.0f} days ({q[p]/365.25:.2f} years)")
    print(f"   max  {gaps.max():6d} days")
    print(f"\nB2 retention to specify = p{RETENTION_Q} = {q[RETENTION_Q]:.0f} days "
          f"({q[RETENTION_Q]/365.25:.2f} years), fixed in docs/226 before running")
    print("   p50 would under-serve 50% of vehicles; the max is set by outliers")
    print("   and would inflate the requirement. This is an UPPER bound on the")
    print("   interval -- cars visit garages between tests -- so it is conservative.")
    return [("B", "MOT interval", len(gaps), q[50], q[75], q[RETENTION_Q], q[95], q[99],
             float(gaps.max()))]


def main() -> None:
    rows = part_a() + part_b()
    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("part\tkey\tn\tv1\tv2\tv3\tv4\tv5\tv6\n")
        for r in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
