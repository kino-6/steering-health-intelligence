#!/usr/bin/env python3
"""DVSA MOT 2025: steering failure rate vs vehicle age, WITH denominator.

The NHTSA complaint curves (docs/135-136) had no denominator. UK MOT data
records every periodic test, pass or fail, so true rates are computable.
This is the independent, denominator-based re-check of the group-level
claim, on one year (2025) of tests.

Streaming two-pass over the two zip extracts (no extraction to disk):
  pass 1  failure-item extract: collect test_ids having a FAIL of a
          steering-section item (test class 4 = cars), and the subset
          whose item chain mentions electronic power steering
  pass 2  result extract: for class-4 normal tests, count per vehicle-age
          totals and steering/EPS failures

Public data (Open Government Licence v3.0). Group description only — no
individual-vehicle prediction, no make ranking as design verdicts.
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
OUT_TSV = REPO_ROOT / "data" / f"dvsa_mot_steering_{YEAR}.tsv"
OUT_HTML = REPO_ROOT / "generated" / f"dvsa_mot_steering_{YEAR}.html"
MAX_AGE = 30


def open_zip_csv(zpath: Path):
    zf = zipfile.ZipFile(zpath)
    names = [n for n in zf.namelist() if n.lower().endswith((".csv", ".txt"))]
    for n in names:
        fh = io.TextIOWrapper(zf.open(n), encoding="utf-8", errors="replace")
        reader = csv.reader(fh, delimiter="," if n.lower().endswith(".csv") else "|")
        yield n, reader


def sniff(reader, name):
    header = next(reader)
    if len(header) == 1 and "|" in header[0]:
        raise SystemExit(f"unexpected delimiter in {name}: {header[0][:80]}")
    print(f"  {name}: {header}")
    return [h.strip().lower() for h in header]


def build_steering_item_sets():
    groups = {}
    for row in csv.DictReader(open(D / "item_group.csv")):
        key = (row["test_item_id"], row["test_class_id"])
        groups[key] = (row["parent_id"], row["item_name"])

    def chain_names(item_id: str, cls: str):
        names, seen = [], set()
        cur = item_id
        while True:
            key = (cur, cls)
            if key in seen or key not in groups:
                break
            seen.add(key)
            parent, name = groups[key]
            names.append(name.lower())
            if parent == cur:
                break
            cur = parent
        return names

    steer_rfr, eps_rfr = set(), set()
    for row in csv.DictReader(open(D / "item_detail.csv")):
        if row["test_class_id"] != "4":
            continue
        names = chain_names(row["test_item_id"], "4")
        blob = " | ".join(names) + " | " + row["rfr_insp_manual_desc"].lower() + " | " + row["rfr_desc"].lower()
        if "steering" in blob:
            steer_rfr.add(row["rfr_id"])
            if "electronic power steering" in blob or "electric power steering" in blob or "epas" in blob:
                eps_rfr.add(row["rfr_id"])
    print(f"class-4 steering rfr_ids: {len(steer_rfr)}, EPS-specific: {len(eps_rfr)}")
    return steer_rfr, eps_rfr


def pass1_items(steer_rfr, eps_rfr):
    steer_tests, eps_tests = set(), set()
    zpath = D / f"dft_test_item_extracts_{YEAR}.zip"
    for name, reader in open_zip_csv(zpath):
        header = sniff(reader, name)
        i_test = header.index("test_id")
        i_rfr = header.index("rfr_id")
        i_type = header.index("rfr_type_code") if "rfr_type_code" in header else None
        n = 0
        for row in reader:
            n += 1
            if i_type is not None and row[i_type] not in ("F", "FLT", "D"):
                continue  # count failures (incl. dangerous), not advisories
            rfr = row[i_rfr]
            if rfr in steer_rfr:
                steer_tests.add(row[i_test])
                if rfr in eps_rfr:
                    eps_tests.add(row[i_test])
        print(f"  {name}: {n:,} rows -> steering-fail tests so far {len(steer_tests):,}")
    return steer_tests, eps_tests


def pass2_results(steer_tests, eps_tests):
    per_age = defaultdict(lambda: [0, 0, 0])  # age -> [tests, steer_fail, eps_fail]
    per_make = defaultdict(lambda: [0, 0])    # make -> [tests, steer_fail]
    zpath = D / f"dft_test_result_extracts_{YEAR}.zip"
    skipped = 0
    for name, reader in open_zip_csv(zpath):
        header = sniff(reader, name)
        ix = {k: header.index(k) for k in ("test_id", "test_class_id", "test_type", "test_result", "test_date", "first_use_date", "make")}
        n = 0
        for row in reader:
            n += 1
            try:
                if row[ix["test_class_id"]] != "4" or row[ix["test_type"]] != "NT":
                    continue
                if row[ix["test_result"]] not in ("P", "F", "PRS"):
                    continue
                td, fu = row[ix["test_date"]], row[ix["first_use_date"]]
                age = (date.fromisoformat(td) - date.fromisoformat(fu)).days / 365.25
            except Exception:
                skipped += 1
                continue
            if not (0 <= age <= MAX_AGE):
                continue
            a = int(age)
            tid = row[ix["test_id"]]
            rec = per_age[a]
            rec[0] += 1
            hit = tid in steer_tests
            if hit:
                rec[1] += 1
                if tid in eps_tests:
                    rec[2] += 1
            mk = row[ix["make"]].strip().upper()
            m = per_make[mk]
            m[0] += 1
            if hit:
                m[1] += 1
        print(f"  {name}: {n:,} rows (skipped {skipped:,})")
    return per_age, per_make


def render(per_age, per_make):
    ages = sorted(a for a in per_age if per_age[a][0] >= 1000)
    lines = ["age_years\ttests\tsteering_fail\tsteer_rate\teps_fail\teps_rate"]
    for a in ages:
        t, s, e = per_age[a]
        lines.append(f"{a}\t{t}\t{s}\t{s/t:.5f}\t{e}\t{e/t:.6f}")
    lines.append("")
    lines.append("make\ttests\tsteering_fail\tsteer_rate")
    big = sorted(((m, v) for m, v in per_make.items() if v[0] >= 50000), key=lambda kv: -kv[1][1] / kv[1][0])
    for m, (t, s) in big:
        lines.append(f"{m}\t{t}\t{s}\t{s/t:.5f}")
    OUT_TSV.write_text("\n".join(lines) + "\n", encoding="utf-8")

    max_rate = max(per_age[a][1] / per_age[a][0] for a in ages) * 1.15
    width, height = 720, 360
    pl, pr, pt, pb = 56, 20, 16, 44
    pw, ph = width - pl - pr, height - pt - pb
    xs = lambda a: pl + pw * a / max(ages)
    ys = lambda v: pt + ph * (1 - v / max_rate)
    svg = [f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='車齢に対する操舵系不合格率(2025年・全数検査)'>"]
    for frac in (0.25, 0.5, 0.75, 1.0):
        v = max_rate * frac
        svg.append(f"<line x1='{pl}' y1='{ys(v):.1f}' x2='{pl+pw}' y2='{ys(v):.1f}' class='grid'/>")
        svg.append(f"<text x='{pl-8}' y='{ys(v)+4:.1f}' class='tick' text-anchor='end'>{v:.1%}</text>")
    svg.append(f"<line x1='{pl}' y1='{pt+ph}' x2='{pl+pw}' y2='{pt+ph}' class='axis'/>")
    for a in range(0, max(ages) + 1, 5):
        svg.append(f"<text x='{xs(a):.1f}' y='{pt+ph+18}' class='tick' text-anchor='middle'>{a}年</text>")
    pts = " ".join(f"{xs(a):.1f},{ys(per_age[a][1]/per_age[a][0]):.1f}" for a in ages)
    svg.append(f"<polyline points='{pts}' fill='none' class='s0' stroke-width='2'/>")
    eps_scale = 10
    pts2 = " ".join(f"{xs(a):.1f},{ys(min(per_age[a][2]/per_age[a][0]*eps_scale, max_rate)):.1f}" for a in ages)
    svg.append(f"<polyline points='{pts2}' fill='none' class='s1' stroke-width='2' stroke-dasharray='5 3'/>")
    svg.append(f"<text x='{pl+8}' y='{pt+14}' class='dlabel s0t'>操舵系全体</text>")
    svg.append(f"<text x='{pl+8}' y='{pt+30}' class='dlabel s1t'>電動パワステ項目(×{eps_scale}表示)</text>")
    svg.append(f"<text x='{pl+pw/2:.0f}' y='{height-6}' class='tick' text-anchor='middle'>車齢(初度登録からの年数)</text>")
    svg.append("</svg>")
    chart = "\n".join(svg)

    total_tests = sum(v[0] for v in per_age.values())
    total_steer = sum(v[1] for v in per_age.values())
    total_eps = sum(v[2] for v in per_age.values())
    make_rows = "\n".join(
        f"<tr><td>{m}</td><td class='num'>{t:,}</td><td class='num'>{s/t:.2%}</td></tr>"
        for m, (t, s) in big[:12]
    )
    html = f"""<meta charset='utf-8'>
<title>英国車検 2025 — 車齢×操舵系不合格率(分母つき)</title>
<style>
:root {{ color-scheme: light dark; }}
.viz-root {{ --surface-1:#fcfcfb; --page:#f9f9f7; --ink-1:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --s0:#2a78d6; --s1:#1baf7a; }}
@media (prefers-color-scheme: dark) {{
  .viz-root {{ --surface-1:#1a1a19; --page:#0d0d0d; --ink-1:#ffffff; --ink-2:#c3c2b7;
    --grid:#2c2c2a; --axis:#383835; --s0:#3987e5; --s1:#199e70; }} }}
.viz-root {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: var(--page);
  color: var(--ink-1); margin: 0 auto; max-width: 60rem; padding: 2rem 1.5rem; line-height: 1.7; }}
h1 {{ font-size: 1.25rem; }} h2 {{ font-size: 1.05rem; margin-top: 2rem; border-bottom: 2px solid var(--grid); padding-bottom: .3rem; }}
.card {{ background: var(--surface-1); color: var(--ink-1); border: 1px solid var(--grid); border-radius: 8px; padding: 1rem 1.2rem; margin: 1rem 0; }}
.note {{ font-size: .88rem; color: var(--ink-2); }}
svg {{ width: 100%; height: auto; display: block; }}
.grid {{ stroke: var(--grid); }} .axis {{ stroke: var(--axis); }} .tick {{ fill: var(--muted); font-size: 11px; }}
.dlabel {{ font-size: 12px; font-weight: 600; }} .s0 {{ stroke: var(--s0); }} .s1 {{ stroke: var(--s1); }}
.s0t {{ fill: var(--s0); }} .s1t {{ fill: var(--s1); }}
table {{ border-collapse: collapse; width: 100%; background: var(--surface-1); color: var(--ink-1); font-size: .9rem; }}
th, td {{ border: 1px solid var(--grid); padding: .4rem .7rem; text-align: left; color: var(--ink-1); }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; }} th {{ color: var(--ink-2); font-weight: 600; }}
.boundary {{ border-left: 3px solid var(--axis); padding-left: .8rem; }}
</style>
<div class='viz-root'>
<h1>英国車検 2025 — 車齢に対する操舵系不合格率(全数検査=分母つき)</h1>
<p class='note card'>米国苦情データの群曲線(分母なし・自己申告)に対する独立の再検証。英国の定期車検は対象車両が毎年全数受検するため、
「率」を分母つきで直接計算できる。乗用車クラスの通常検査 {total_tests:,} 件、うち操舵系不合格 {total_steer:,} 件({total_steer/total_tests:.2%})、
電動パワステ項目の不合格 {total_eps:,} 件。</p>
<h2>車齢×不合格率</h2>
<div class='card'>{chart}</div>
<h2>メーカー別(5万件以上、不合格率順)</h2>
<table><tr><th>make</th><th>検査数</th><th>操舵系不合格率</th></tr>{make_rows}</table>
<p class='note'>順位は設計優劣の判定ではない(車齢構成・車種構成・使われ方が混ざる)。年齢調整前の生の率。</p>
<h2>限界</h2>
<p class='note boundary'>英国のみ・2025年のみ/検査項目の「操舵系」は機械系(ラック・ジョイント・ガタ)を広く含み、電動パワステ固有項目は別掲/
検査は年1回のスナップショットであり、途中で修理された故障は数えない(生存バイアス)/率の絶対値は検査制度に依存し、米国苦情データとは定義が異なる——
比べてよいのは「車齢に対する形」だけ。</p>
<p class='note'>データ: DVSA MOT anonymised(OGL v3.0)。再現: <code>python3 scripts/dvsa_mot_steering_rates.py</code></p>
</div>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"wrote {OUT_TSV.relative_to(REPO_ROOT)} and {OUT_HTML.relative_to(REPO_ROOT)}")


def main() -> None:
    cache_s, cache_e = D / "cache_steer_tests.txt", D / "cache_eps_tests.txt"
    if cache_s.exists() and cache_e.exists():
        steer_tests = set(cache_s.read_text().split())
        eps_tests = set(cache_e.read_text().split())
        print(f"pass1 cache: {len(steer_tests):,} steering / {len(eps_tests):,} EPS")
    else:
        steer_rfr, eps_rfr = build_steering_item_sets()
        steer_tests, eps_tests = pass1_items(steer_rfr, eps_rfr)
        cache_s.write_text("\n".join(steer_tests))
        cache_e.write_text("\n".join(eps_tests))
    print(f"tests with steering failure: {len(steer_tests):,} (EPS-specific: {len(eps_tests):,})")
    per_age, per_make = pass2_results(steer_tests, eps_tests)
    render(per_age, per_make)


if __name__ == "__main__":
    main()
