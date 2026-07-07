#!/usr/bin/env python3
"""Point-in-time backtest: could the cohort curve have fired BEFORE the recall?

Phase D (docs/136) and its generalization sweep (docs/137). For half-yearly
cutoff dates, aggregate only the complaints FILED on or before each cutoff —
the information actually available at that time — and ask when a simple,
PRE-REGISTERED detection rule would have flagged the cohorts that were later
recalled, relative to the actual recall announcements.

    fire(cohort, cutoff) :=
        steering_filed >= 30                          (volume floor)
        AND share >= 2 x old-generation baseline      (same cutoff, pooled)
        AND share >= 0.30                             (absolute floor)

Vehicles:
  fusion    — Ford Fusion. EPS cohorts MY2010-2014; baseline MY2008-2009
              (hydraulic PS). Recalls: MY2011-2012 (15V-340, 2015-07).
  silverado — Chevrolet Silverado 1500. EPS cohorts MY2014-2017; baseline
              MY2011-2012 (prior generation, predominantly hydraulic PS).
              Recalls: MY2014 (17V-414, 2017-07), MY2015 (18V-586, 2018-09).

Honesty constraints: filed-date snapshots assume today's database preserves
historical filed dates; the old-generation baseline mixes a technology change
with any defect signal (hence the 2x margin and absolute floor); no
individual-vehicle prediction; no OEM design verdict.

Usage: python3 scripts/steering_cohort_backtest.py [fusion|silverado]
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / ".nhtsa_cache"

MIN_STEERING = 30
BASELINE_MULT = 2.0
SHARE_FLOOR = 0.30

API = "https://api.nhtsa.gov/complaints/complaintsByVehicle?make={make}&model={model}&modelYear={year}"

SERIES_LIGHT = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7"]
SERIES_DARK = ["#3987e5", "#199e70", "#c98500", "#008300", "#9085e9"]


@dataclass
class VehicleConfig:
    key: str
    make: str
    model: str
    eps_cohorts: list[int]
    baseline_cohorts: list[int]
    cohort_note: dict[int, str]
    recall_dates: dict[int, date]  # cohort -> announcement date (lead reference)
    cutoffs: list[date]
    out_suffix: str


def half_yearly(y0: int, y1: int) -> list[date]:
    out = []
    for y in range(y0, y1 + 1):
        out.append(date(y, 6, 30))
        out.append(date(y, 12, 31))
    return out


VEHICLES = {
    "fusion": VehicleConfig(
        key="fusion", make="ford", model="fusion",
        eps_cohorts=[2010, 2011, 2012, 2013, 2014],
        baseline_cohorts=[2008, 2009],
        cohort_note={
            2010: "調査対象 (PE14-030)",
            2011: "リコール対象 (15V-340)",
            2012: "リコール対象 (15V-340)",
            2013: "比較対象",
            2014: "比較対象",
        },
        recall_dates={2011: date(2015, 7, 1), 2012: date(2015, 7, 1)},
        cutoffs=half_yearly(2011, 2015)[:-1],
        out_suffix="",
    ),
    "silverado": VehicleConfig(
        key="silverado", make="chevrolet", model="silverado 1500",
        eps_cohorts=[2014, 2015, 2016, 2017],
        baseline_cohorts=[2011, 2012],
        cohort_note={
            2014: "リコール対象 (17V-414)",
            2015: "リコール対象 (18V-586)",
            2016: "比較対象",
            2017: "比較対象",
        },
        recall_dates={2014: date(2017, 7, 1), 2015: date(2018, 9, 1)},
        cutoffs=half_yearly(2014, 2018),
        out_suffix="_silverado",
    ),
}


def fetch_cohort(cfg: VehicleConfig, year: int) -> dict:
    CACHE_DIR.mkdir(exist_ok=True)
    slug = f"{cfg.make}_{cfg.model.replace(' ', '')}_{year}"
    cache = CACHE_DIR / f"{slug}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    url = API.format(make=cfg.make, model=urllib.parse.quote(cfg.model), year=year)
    last_err: Exception | None = None
    for attempt in range(1, 5):
        print(f"fetch {url} (attempt {attempt})")
        try:
            with urllib.request.urlopen(url, timeout=180) as resp:
                raw = resp.read().decode("utf-8")
            cache.write_text(raw)
            return json.loads(raw)
        except Exception as err:
            last_err = err
            time.sleep(5 * attempt)
    raise SystemExit(f"failed to fetch {url}: {last_err}")


def parse_date(text: str | None) -> date | None:
    if not text:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    return None


def load_filed_events(cfg: VehicleConfig, year: int) -> list[tuple[date, bool]]:
    events = []
    for c in fetch_cohort(cfg, year).get("results", []):
        filed = parse_date(c.get("dateComplaintFiled"))
        if not filed:
            continue
        steering = "STEERING" in (c.get("components") or "").upper()
        events.append((filed, steering))
    return events


def snapshot(events: list[tuple[date, bool]], cutoff: date) -> tuple[int, int]:
    total = sum(1 for d, _ in events if d <= cutoff)
    steering = sum(1 for d, s in events if s and d <= cutoff)
    return total, steering


def lead_months(recall: date, fired: date) -> int:
    return (recall.year - fired.year) * 12 + (recall.month - fired.month)


def analyze(cfg: VehicleConfig) -> dict:
    events = {y: load_filed_events(cfg, y) for y in cfg.baseline_cohorts + cfg.eps_cohorts}
    rows = []
    first_fire: dict[int, date] = {}
    for cutoff in cfg.cutoffs:
        b_total = b_steer = 0
        for y in cfg.baseline_cohorts:
            t, s = snapshot(events[y], cutoff)
            b_total += t
            b_steer += s
        baseline_share = b_steer / b_total if b_total else 0.0
        row = {"cutoff": cutoff.isoformat(), "baseline_share": baseline_share,
               "baseline_n": b_total, "cohorts": {}}
        for y in cfg.eps_cohorts:
            t, s = snapshot(events[y], cutoff)
            share = s / t if t else 0.0
            fired = (s >= MIN_STEERING and baseline_share > 0
                     and share >= BASELINE_MULT * baseline_share and share >= SHARE_FLOOR)
            if fired and y not in first_fire:
                first_fire[y] = cutoff
            row["cohorts"][y] = {"total": t, "steering": s, "share": share, "fired": fired}
        rows.append(row)
    return {"rows": rows, "first_fire": first_fire}


def render_tsv(cfg: VehicleConfig, result: dict) -> str:
    header = ["cutoff", "baseline_share", "baseline_n"]
    for y in cfg.eps_cohorts:
        header += [f"MY{y}_total", f"MY{y}_steering", f"MY{y}_share", f"MY{y}_fired"]
    lines = ["\t".join(header)]
    for row in result["rows"]:
        cells = [row["cutoff"], f"{row['baseline_share']:.4f}", str(row["baseline_n"])]
        for y in cfg.eps_cohorts:
            c = row["cohorts"][y]
            cells += [str(c["total"]), str(c["steering"]), f"{c['share']:.4f}", "FIRE" if c["fired"] else "-"]
        lines.append("\t".join(cells))
    lines.append("")
    lines.append("cohort\trole\tfirst_fire_cutoff\trecall_announced\tlead_time_months")
    for y in cfg.eps_cohorts:
        ff = result["first_fire"].get(y)
        recall = cfg.recall_dates.get(y)
        lines.append("\t".join([
            f"MY{y}", cfg.cohort_note[y],
            ff.isoformat() if ff else "never",
            recall.isoformat() if recall else "-",
            str(lead_months(recall, ff)) if (ff and recall) else "-",
        ]))
    return "\n".join(lines) + "\n"


def render_html(cfg: VehicleConfig, result: dict) -> str:
    width, height = 880, 380
    pad_l, pad_r, pad_t, pad_b = 56, 130, 16, 44
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
    n = len(result["rows"])
    max_y = 0.8
    xs = lambda i: pad_l + plot_w * i / (n - 1)
    ys = lambda v: pad_t + plot_h * (1 - v / max_y)
    svg = [f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='時点区切りごとの操舵系苦情比率(届出ベース)'>"]
    for frac in (0.2, 0.4, 0.6, 0.8):
        svg.append(f"<line x1='{pad_l}' y1='{ys(frac):.1f}' x2='{pad_l+plot_w}' y2='{ys(frac):.1f}' class='grid'/>")
        svg.append(f"<text x='{pad_l-8}' y='{ys(frac)+4:.1f}' class='tick' text-anchor='end'>{int(frac*100)}%</text>")
    svg.append(f"<line x1='{pad_l}' y1='{pad_t+plot_h}' x2='{pad_l+plot_w}' y2='{pad_t+plot_h}' class='axis'/>")
    step = 2 if n > 10 else 1
    for i, row in enumerate(result["rows"]):
        if i % step == 0:
            svg.append(f"<text x='{xs(i):.1f}' y='{pad_t+plot_h+18}' class='tick' text-anchor='middle'>{row['cutoff'][:7]}</text>")
    pts = " ".join(f"{xs(i):.1f},{ys(r['baseline_share']):.1f}" for i, r in enumerate(result["rows"]))
    svg.append(f"<polyline points='{pts}' fill='none' class='baseline' stroke-width='2'/>")
    svg.append(f"<text x='{pad_l+plot_w+6}' y='{ys(result['rows'][-1]['baseline_share'])+4:.1f}' class='mlabel'>旧世代基準</text>")
    svg.append(f"<line x1='{pad_l}' y1='{ys(SHARE_FLOOR):.1f}' x2='{pad_l+plot_w}' y2='{ys(SHARE_FLOOR):.1f}' class='marker'/>")
    svg.append(f"<text x='{pad_l+4}' y='{ys(SHARE_FLOOR)-6:.1f}' class='mlabel'>発火下限 30%</text>")
    for si, y in enumerate(cfg.eps_cohorts):
        seg = [(i, r["cohorts"][y]) for i, r in enumerate(result["rows"]) if r["cohorts"][y]["total"] >= 10]
        if not seg:
            continue
        pts = " ".join(f"{xs(i):.1f},{ys(c['share']):.1f}" for i, c in seg)
        svg.append(f"<polyline points='{pts}' fill='none' class='s{si}' stroke-width='2'/>")
        for i, c in seg:
            if c["fired"]:
                svg.append(f"<circle cx='{xs(i):.1f}' cy='{ys(c['share']):.1f}' r='5' class='s{si}f' stroke='var(--surface-1)' stroke-width='2'/>")
        last_i, last_c = seg[-1]
        svg.append(f"<text x='{pad_l+plot_w+6}' y='{ys(last_c['share'])+4:.1f}' class='dlabel s{si}t'>MY{y}</text>")
    svg.append("</svg>")
    chart = "\n".join(svg)

    fire_rows = []
    for y in cfg.eps_cohorts:
        ff = result["first_fire"].get(y)
        recall = cfg.recall_dates.get(y)
        lead = f"{lead_months(recall, ff)}ヶ月前" if (ff and recall) else ("-" if not recall else "発火せず")
        fire_rows.append(
            f"<tr><td>MY{y}</td><td>{cfg.cohort_note[y]}</td><td>{ff.isoformat() if ff else '発火せず'}</td>"
            f"<td>{recall.isoformat() if recall else '-(非リコール)'}</td><td class='num'>{lead if ff else ('-' if not recall else '検知不能')}</td></tr>"
        )
    table_fire = "\n".join(fire_rows)
    legend = "".join(
        f"<span class='key'><span class='swatch s{i}b'></span>MY{y}</span>" for i, y in enumerate(cfg.eps_cohorts)
    ) + f"<span class='key'><span class='swatch bl'></span>旧世代基準(MY{cfg.baseline_cohorts[0]}-{cfg.baseline_cohorts[-1]%100:02d})</span>"

    css_light = "".join(
        f".s{i} {{ stroke: {c}; }} .s{i}t {{ fill: {c}; }} .s{i}f {{ fill: {c}; }} .s{i}b {{ background: {c}; }}\n"
        for i, c in enumerate(SERIES_LIGHT)
    )
    css_dark = "".join(
        f".s{i} {{ stroke: {c}; }} .s{i}t {{ fill: {c}; }} .s{i}f {{ fill: {c}; }} .s{i}b {{ background: {c}; }}\n"
        for i, c in enumerate(SERIES_DARK)
    )
    title = f"{cfg.make.title()} {cfg.model.title()}"
    return f"""<meta charset='utf-8'>
<title>Steering Cohort Backtest — {title}</title>
<style>
.viz-root {{
  --surface-1:#fcfcfb; --page:#f9f9f7; --ink-1:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7;
}}
{css_light}
@media (prefers-color-scheme: dark) {{
  .viz-root {{ --surface-1:#1a1a19; --page:#0d0d0d; --ink-1:#ffffff; --ink-2:#c3c2b7; --grid:#2c2c2a; --axis:#383835; }}
  {css_dark}
}}
.viz-root {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: var(--page);
  color: var(--ink-1); margin: 0 auto; max-width: 62rem; padding: 2rem 1.5rem; line-height: 1.6; }}
h1 {{ font-size: 1.3rem; }} h2 {{ font-size: 1.05rem; margin-top: 2rem; }}
.card {{ background: var(--surface-1); border: 1px solid var(--grid); border-radius: 8px; padding: 1rem 1.2rem; margin: 1rem 0; }}
.note {{ font-size: .88rem; color: var(--ink-2); }}
svg {{ width: 100%; height: auto; display: block; }}
.grid {{ stroke: var(--grid); stroke-width: 1; }} .axis {{ stroke: var(--axis); stroke-width: 1; }}
.tick {{ fill: var(--muted); font-size: 12px; }} .dlabel {{ font-size: 12px; font-weight: 600; }}
.baseline {{ stroke: var(--muted); stroke-dasharray: 6 4; }} .bl {{ background: var(--muted); }}
.marker {{ stroke: var(--axis); stroke-width: 1; stroke-dasharray: 3 3; }} .mlabel {{ fill: var(--ink-2); font-size: 11px; }}
.legend {{ display: flex; gap: 1rem; flex-wrap: wrap; font-size: .85rem; color: var(--ink-2); margin-top: .4rem; }}
.key {{ display: inline-flex; align-items: center; gap: .35rem; }}
.swatch {{ width: 12px; height: 12px; border-radius: 3px; display: inline-block; }}
table {{ border-collapse: collapse; width: 100%; background: var(--surface-1); font-size: .92rem; }}
th, td {{ border: 1px solid var(--grid); padding: .45rem .7rem; text-align: left; }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
th {{ color: var(--ink-2); font-weight: 600; }}
.boundary {{ border-left: 3px solid var(--axis); padding-left: .8rem; }}
</style>
<div class='viz-root'>
<h1>時点区切りバックテスト — {title}</h1>
<p class='note card'><b>方法:</b> 各cutoff時点までに届出(filed)された苦情だけで操舵系比率を計算。検知ルールは事前固定:
操舵系{MIN_STEERING}件以上 かつ 比率が旧世代基準の{BASELINE_MULT:g}倍以上 かつ {SHARE_FLOOR:.0%}以上。●印=ルール発火。
<b>言っていないこと:</b> 個車の故障予測、原因、OEM設計優劣。</p>
<div class='card'>
{chart}
<div class='legend'>{legend}</div>
</div>
<h2>発火時点とリード</h2>
<table>
<tr><th>年式</th><th>位置づけ</th><th>初回発火cutoff</th><th>リコール公表</th><th>リード</th></tr>
{table_fire}
</table>
<h2>限界</h2>
<p class='note boundary'>現在のDBの届出日が当時のまま保存されている前提。旧世代基準は技術変化(油圧→EPS)を含むため2倍マージン+絶対下限を課している。届出行動に依存するため、届出が遅いcohortは検知できない(Fusion MY2010で確認済みの限界)。</p>
</div>
"""


def main() -> None:
    key = sys.argv[1] if len(sys.argv) > 1 else "fusion"
    cfg = VEHICLES[key]
    result = analyze(cfg)
    print(f"{'cutoff':<12} baseline " + " ".join(f"MY{y:<6}" for y in cfg.eps_cohorts))
    for row in result["rows"]:
        cells = " ".join(
            f"{row['cohorts'][y]['share']:.0%}{'*' if row['cohorts'][y]['fired'] else ' '}".ljust(7)
            for y in cfg.eps_cohorts
        )
        print(f"{row['cutoff']:<12} {row['baseline_share']:.0%}      {cells}")
    for y in cfg.eps_cohorts:
        ff = result["first_fire"].get(y)
        recall = cfg.recall_dates.get(y)
        if ff and recall:
            print(f"MY{y}: first fire {ff} -> {lead_months(recall, ff)} months before recall")
        elif ff:
            print(f"MY{y}: first fire {ff} (no recall for this cohort -> FALSE POSITIVE)")
        elif recall:
            print(f"MY{y}: never fired (recalled cohort -> MISS)")
        else:
            print(f"MY{y}: never fired (correct negative)")
    out_tsv = REPO_ROOT / "data" / f"steering_cohort_backtest{cfg.out_suffix}.tsv"
    out_html = REPO_ROOT / "generated" / f"steering_cohort_backtest{cfg.out_suffix}.html"
    out_tsv.write_text(render_tsv(cfg, result), encoding="utf-8")
    out_html.write_text(render_html(cfg, result), encoding="utf-8")
    print(f"wrote {out_tsv.relative_to(REPO_ROOT)}")
    print(f"wrote {out_html.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
