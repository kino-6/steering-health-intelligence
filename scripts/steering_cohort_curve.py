#!/usr/bin/env python3
"""Group-level steering complaint cohort curves from public NHTSA data.

Phase C demo (docs/135): can public complaint data honestly show a
group-level steering risk trend, validated against a known recall story?

- Cohorts: Ford Fusion MY2010-2014.
  MY2011-2012 were recalled for EPAS loss of assist (15V-340 / 15S18).
  MY2010 was the subject of ODI investigation PE14-030.
  MY2013-2014 serve as the within-model comparison group.
- Curve 1: cumulative STEERING complaints vs vehicle age per cohort.
- Curve 2: monthly filed STEERING complaints (all cohorts) with the recall
  announcement marked — the reporting-bias spike is shown on purpose.

Honesty constraints (docs/134): no fleet denominator exists, so the output
is counts and within-model comparison, never an absolute failure rate; the
group curve describes the observed past and predicts nothing about any
individual vehicle.
"""

from __future__ import annotations

import json
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / ".nhtsa_cache"
OUT_HTML = REPO_ROOT / "generated" / "steering_cohort_curve.html"
OUT_TSV = REPO_ROOT / "data" / "steering_cohort_curve_summary.tsv"

MAKE, MODEL = "ford", "fusion"
COHORT_YEARS = [2010, 2011, 2012, 2013, 2014]
COHORT_NOTE = {
    2010: "調査対象 (PE14-030)",
    2011: "リコール対象 (15V-340)",
    2012: "リコール対象 (15V-340)",
    2013: "比較対象",
    2014: "比較対象",
}
RECALL_ANNOUNCED = date(2015, 7, 1)  # 15S18 owner letters mailed week of 2015-07-13
MAX_AGE_MONTHS = 120

API = "https://api.nhtsa.gov/complaints/complaintsByVehicle?make={make}&model={model}&modelYear={year}"


def fetch_cohort(year: int) -> dict:
    CACHE_DIR.mkdir(exist_ok=True)
    cache = CACHE_DIR / f"{MAKE}_{MODEL}_{year}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    url = API.format(make=MAKE, model=MODEL, year=year)
    last_err: Exception | None = None
    for attempt in range(1, 5):
        print(f"fetch {url} (attempt {attempt})")
        try:
            with urllib.request.urlopen(url, timeout=180) as resp:
                raw = resp.read().decode("utf-8")
            cache.write_text(raw)
            return json.loads(raw)
        except Exception as err:  # 504s from the API are transient
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


def month_diff(later: date, earlier: date) -> int:
    return (later.year - earlier.year) * 12 + (later.month - earlier.month)


def analyze() -> dict:
    cohorts = {}
    monthly_filed: dict[str, int] = {}
    for year in COHORT_YEARS:
        payload = fetch_cohort(year)
        results = payload.get("results", [])
        baseline = date(year, 1, 1)  # fleet-entry proxy; MY sales start earlier — approximation, documented
        steering, total = 0, 0
        by_age = [0] * (MAX_AGE_MONTHS + 1)
        for c in results:
            total += 1
            components = (c.get("components") or "").upper()
            if "STEERING" not in components:
                continue
            steering += 1
            incident = parse_date(c.get("dateOfIncident"))
            filed = parse_date(c.get("dateComplaintFiled"))
            if incident:
                age = month_diff(incident, baseline)
                if 0 <= age <= MAX_AGE_MONTHS:
                    by_age[age] += 1
            if filed:
                key = f"{filed.year}-{filed.month:02d}"
                monthly_filed[key] = monthly_filed.get(key, 0) + 1
        cumulative = []
        run = 0
        for m in range(MAX_AGE_MONTHS + 1):
            run += by_age[m]
            cumulative.append(run)
        cohorts[year] = {
            "total": total,
            "steering": steering,
            "share": steering / total if total else 0.0,
            "cumulative": cumulative,
        }
        print(f"MY{year}: total={total} steering={steering} share={steering/total:.1%}")
    months = sorted(monthly_filed)
    months = [m for m in months if "2009-12" < m <= "2020-12"]
    return {
        "cohorts": cohorts,
        "monthly": [(m, monthly_filed[m]) for m in months],
    }


# ---------------------------------------------------------------------------
# Rendering — palette per dataviz reference instance (validated PASS for the
# 5 slots used, light & dark; contrast WARN relieved by direct labels + table)
# ---------------------------------------------------------------------------
SERIES_LIGHT = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7"]
SERIES_DARK = ["#3987e5", "#199e70", "#c98500", "#008300", "#9085e9"]


def svg_line_chart(data: dict, width=880, height=380) -> str:
    pad_l, pad_r, pad_t, pad_b = 56, 120, 16, 40
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
    years = COHORT_YEARS
    max_y = max(max(data["cohorts"][y]["cumulative"]) for y in years) * 1.05
    xs = lambda m: pad_l + plot_w * m / MAX_AGE_MONTHS
    ys = lambda v: pad_t + plot_h * (1 - v / max_y)
    parts = [f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='車齢に対する操舵系苦情の累積件数(年式cohort別)' id='chart1'>"]
    # gridlines + y ticks
    for frac in (0.25, 0.5, 0.75, 1.0):
        v = max_y * frac
        parts.append(f"<line x1='{pad_l}' y1='{ys(v):.1f}' x2='{pad_l+plot_w}' y2='{ys(v):.1f}' class='grid'/>")
        parts.append(f"<text x='{pad_l-8}' y='{ys(v)+4:.1f}' class='tick' text-anchor='end'>{int(v)}</text>")
    # baseline + x ticks (years of age)
    parts.append(f"<line x1='{pad_l}' y1='{pad_t+plot_h}' x2='{pad_l+plot_w}' y2='{pad_t+plot_h}' class='axis'/>")
    for yr_age in range(0, 11, 2):
        m = yr_age * 12
        parts.append(f"<text x='{xs(m):.1f}' y='{pad_t+plot_h+18}' class='tick' text-anchor='middle'>{yr_age}年</text>")
    parts.append(f"<text x='{pad_l+plot_w/2:.0f}' y='{height-6}' class='tick' text-anchor='middle'>車齢(年式年1月起点の近似)</text>")
    # series
    for i, y in enumerate(years):
        cum = data["cohorts"][y]["cumulative"]
        pts = " ".join(f"{xs(m):.1f},{ys(v):.1f}" for m, v in enumerate(cum))
        parts.append(f"<polyline points='{pts}' class='s{i}' fill='none' stroke-width='2'/>")
        # direct labels: recall/investigated cohorts + 2013 (<=4 per rule); 2014 legend-only
        if y != 2014:
            parts.append(
                f"<text x='{pad_l+plot_w+6}' y='{ys(cum[-1])+4:.1f}' class='dlabel s{i}t'>MY{y} {data['cohorts'][y]['steering']}件</text>"
            )
    parts.append("<line id='xhair' x1='0' y1='%d' x2='0' y2='%d' class='xhair' visibility='hidden'/>" % (pad_t, pad_t + plot_h))
    parts.append(f"<rect id='hover1' x='{pad_l}' y='{pad_t}' width='{plot_w}' height='{plot_h}' fill='transparent'/>")
    parts.append("</svg>")
    meta = {
        "padL": pad_l, "plotW": plot_w, "padT": pad_t, "plotH": plot_h,
        "maxY": max_y, "maxM": MAX_AGE_MONTHS,
        "series": {str(y): data["cohorts"][y]["cumulative"] for y in years},
    }
    return "\n".join(parts), meta


def svg_monthly_chart(monthly: list, width=880, height=300) -> str:
    pad_l, pad_r, pad_t, pad_b = 56, 24, 30, 40
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
    n = len(monthly)
    max_y = max(v for _, v in monthly) * 1.1
    xs = lambda i: pad_l + plot_w * i / max(n - 1, 1)
    ys = lambda v: pad_t + plot_h * (1 - v / max_y)
    parts = [f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='操舵系苦情の月次届出件数と、リコール公表の時点' id='chart2'>"]
    for frac in (0.5, 1.0):
        v = max_y * frac
        parts.append(f"<line x1='{pad_l}' y1='{ys(v):.1f}' x2='{pad_l+plot_w}' y2='{ys(v):.1f}' class='grid'/>")
        parts.append(f"<text x='{pad_l-8}' y='{ys(v)+4:.1f}' class='tick' text-anchor='end'>{int(v)}</text>")
    parts.append(f"<line x1='{pad_l}' y1='{pad_t+plot_h}' x2='{pad_l+plot_w}' y2='{pad_t+plot_h}' class='axis'/>")
    idx = {m: i for i, (m, _) in enumerate(monthly)}
    for year in range(2010, 2021, 2):
        key = f"{year}-01"
        if key in idx:
            parts.append(f"<text x='{xs(idx[key]):.1f}' y='{pad_t+plot_h+18}' class='tick' text-anchor='middle'>{year}</text>")
    # recall marker (annotation, muted ink — not a series color)
    rk = "2015-07"
    if rk in idx:
        x = xs(idx[rk])
        parts.append(f"<line x1='{x:.1f}' y1='{pad_t-4}' x2='{x:.1f}' y2='{pad_t+plot_h}' class='marker'/>")
        parts.append(f"<text x='{x+6:.1f}' y='{pad_t+8}' class='mlabel'>リコール公表 2015-07</text>")
    pts = " ".join(f"{xs(i):.1f},{ys(v):.1f}" for i, (_, v) in enumerate(monthly))
    parts.append(f"<polyline points='{pts}' class='s0' fill='none' stroke-width='2'/>")
    parts.append("<circle id='dot2' r='4' class='s0f' visibility='hidden'/>")
    parts.append(f"<rect id='hover2' x='{pad_l}' y='{pad_t}' width='{plot_w}' height='{plot_h}' fill='transparent'/>")
    parts.append("</svg>")
    meta = {"padL": pad_l, "plotW": plot_w, "padT": pad_t, "plotH": plot_h, "maxY": max_y,
            "labels": [m for m, _ in monthly], "values": [v for _, v in monthly]}
    return "\n".join(parts), meta


def render_html(data: dict) -> str:
    chart1, meta1 = svg_line_chart(data)
    chart2, meta2 = svg_monthly_chart(data["monthly"])
    cohort_rows = "\n".join(
        f"<tr><td>MY{y}</td><td>{COHORT_NOTE[y]}</td><td class='num'>{c['total']:,}</td>"
        f"<td class='num'>{c['steering']:,}</td><td class='num'>{c['share']:.1%}</td></tr>"
        for y, c in ((y, data["cohorts"][y]) for y in COHORT_YEARS)
    )
    total_all = sum(data["cohorts"][y]["total"] for y in COHORT_YEARS)
    steer_all = sum(data["cohorts"][y]["steering"] for y in COHORT_YEARS)
    legend = "".join(
        f"<span class='key'><span class='swatch s{i}b'></span>MY{y}({COHORT_NOTE[y]})</span>"
        for i, y in enumerate(COHORT_YEARS)
    )
    return f"""<meta charset='utf-8'>
<title>Steering Cohort Curve (NHTSA public complaints)</title>
<style>
.viz-root {{
  --surface-1:#fcfcfb; --page:#f9f9f7; --ink-1:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7;
  --s0:{SERIES_LIGHT[0]}; --s1:{SERIES_LIGHT[1]}; --s2:{SERIES_LIGHT[2]}; --s3:{SERIES_LIGHT[3]}; --s4:{SERIES_LIGHT[4]};
}}
@media (prefers-color-scheme: dark) {{
  .viz-root {{
    --surface-1:#1a1a19; --page:#0d0d0d; --ink-1:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --axis:#383835;
    --s0:{SERIES_DARK[0]}; --s1:{SERIES_DARK[1]}; --s2:{SERIES_DARK[2]}; --s3:{SERIES_DARK[3]}; --s4:{SERIES_DARK[4]};
  }}
}}
.viz-root {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: var(--page);
  color: var(--ink-1); margin: 0 auto; max-width: 62rem; padding: 2rem 1.5rem; line-height: 1.6; }}
h1 {{ font-size: 1.35rem; }} h2 {{ font-size: 1.05rem; margin-top: 2.2rem; }}
.card {{ background: var(--surface-1); border: 1px solid var(--grid); border-radius: 8px; padding: 1rem 1.2rem; margin: 1rem 0; }}
.note {{ font-size: .88rem; color: var(--ink-2); }}
.tiles {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
.tile {{ flex: 1 1 10rem; background: var(--surface-1); border: 1px solid var(--grid); border-radius: 8px; padding: .8rem 1rem; }}
.tile .v {{ font-size: 1.7rem; font-weight: 650; }} .tile .k {{ font-size: .8rem; color: var(--ink-2); }}
svg {{ width: 100%; height: auto; display: block; }}
.grid {{ stroke: var(--grid); stroke-width: 1; }} .axis {{ stroke: var(--axis); stroke-width: 1; }}
.tick {{ fill: var(--muted); font-size: 12px; }} .dlabel {{ font-size: 12px; font-weight: 600; }}
.s0 {{ stroke: var(--s0); }} .s1 {{ stroke: var(--s1); }} .s2 {{ stroke: var(--s2); }} .s3 {{ stroke: var(--s3); }} .s4 {{ stroke: var(--s4); }}
.s0t {{ fill: var(--s0); }} .s1t {{ fill: var(--s1); }} .s2t {{ fill: var(--s2); }} .s3t {{ fill: var(--s3); }} .s4t {{ fill: var(--s4); }}
.s0f {{ fill: var(--s0); }}
.s0b {{ background: var(--s0); }} .s1b {{ background: var(--s1); }} .s2b {{ background: var(--s2); }} .s3b {{ background: var(--s3); }} .s4b {{ background: var(--s4); }}
.xhair {{ stroke: var(--muted); stroke-width: 1; stroke-dasharray: 3 3; }}
.marker {{ stroke: var(--muted); stroke-width: 1.5; stroke-dasharray: 5 4; }} .mlabel {{ fill: var(--ink-2); font-size: 12px; }}
.legend {{ display: flex; gap: 1rem; flex-wrap: wrap; font-size: .85rem; color: var(--ink-2); margin: .4rem 0 0; }}
.key {{ display: inline-flex; align-items: center; gap: .35rem; }}
.swatch {{ width: 12px; height: 12px; border-radius: 3px; display: inline-block; }}
table {{ border-collapse: collapse; width: 100%; background: var(--surface-1); font-size: .92rem; }}
th, td {{ border: 1px solid var(--grid); padding: .45rem .7rem; text-align: left; }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
th {{ color: var(--ink-2); font-weight: 600; }}
#tip {{ position: fixed; pointer-events: none; background: var(--surface-1); border: 1px solid var(--axis);
  border-radius: 6px; padding: .4rem .6rem; font-size: .8rem; visibility: hidden; z-index: 9; color: var(--ink-1);
  box-shadow: 0 2px 8px rgba(0,0,0,.12); }}
.boundary {{ border-left: 3px solid var(--axis); padding-left: .8rem; }}
</style>
<div class='viz-root'>
<h1>操舵系苦情のcohort曲線 — Ford Fusion MY2010–2014(NHTSA公開データ)</h1>
<p class='note card'><b>この図が言っていること:</b> 公開苦情データから、車種×年式の群として操舵系不具合の傾向が読めるか。既知のリコール(15V-340: MY2011–2012)・調査(PE14-030: MY2010)のcohortが、比較cohort(MY2013–2014)より実際に浮くかを答え合わせする。<br>
<b>言っていないこと:</b> 個々の車両の故障予測、絶対的な故障率(苦情に分母=稼働台数はない)、特定OEMの設計優劣。</p>
<div class='tiles'>
<div class='tile'><div class='v'>{total_all:,}</div><div class='k'>取得した全苦情(5 cohort)</div></div>
<div class='tile'><div class='v'>{steer_all:,}</div><div class='k'>うち操舵系(STEERING)</div></div>
<div class='tile'><div class='v'>{steer_all/total_all:.1%}</div><div class='k'>操舵系比率(全cohort)</div></div>
</div>
<h2>1. 車齢に対する操舵系苦情の累積件数(年式cohort別)</h2>
<div class='card'>
{chart1}
<div class='legend'>{legend}</div>
<p class='note'>車齢は各年式年の1月1日を艦隊投入の近似起点とする(実際の販売開始は前年秋以降に分布)。件数は正規化していない絶対数であり、cohort間の販売台数差の影響を含む。右の表の操舵系比率が販売規模の影響を部分的に補正した指標。</p>
</div>
<h2>2. 操舵系苦情の月次届出件数と、リコール公表(報告バイアスの可視化)</h2>
<div class='card'>
{chart2}
<p class='note'>届出日(dateComplaintFiled)ベース。リコール公表・通知の後に届出が急増するのは欠陥発生の波形ではなく社会的な波形であり、苦情データを扱うときに必ず補正・注記すべき偏りとして意図的に見せている。</p>
</div>
<h2>3. Cohort別サマリ(テーブル)</h2>
<table>
<tr><th>年式</th><th>位置づけ(公開文書)</th><th>全苦情</th><th>操舵系</th><th>操舵系比率</th></tr>
{cohort_rows}
</table>
<h2>言ってよいこと / いけないこと</h2>
<p class='note boundary'>言ってよい: 「この車種では、リコール対象年式の操舵系苦情比率・累積曲線が比較年式より高い/低いと市場データ上観測された」。<br>
言ってはいけない: 「この年式の個々の車両は故障する」「原因は◯◯である」「保証費を削減できる」「他OEMより設計が劣る」。</p>
<p class='note'>データ: <a href='https://api.nhtsa.gov/complaints/complaintsByVehicle?make=ford&model=fusion&modelYear=2011'>NHTSA complaints API</a>(取得スクリプト: scripts/steering_cohort_curve.py)。答え合わせの根拠文書: NHTSA 15V-340 / 15S18 / PE14-030。</p>
</div>
<div id='tip'></div>
<script>
const M1 = {json.dumps(meta1)};
const M2 = {json.dumps(meta2)};
const tip = document.getElementById('tip');
function showTip(evt, html) {{
  tip.innerHTML = html; tip.style.visibility = 'visible';
  tip.style.left = Math.min(evt.clientX + 14, window.innerWidth - 220) + 'px';
  tip.style.top = (evt.clientY + 14) + 'px';
}}
function hideTip() {{ tip.style.visibility = 'hidden'; }}
const svg1 = document.getElementById('chart1');
const hov1 = document.getElementById('hover1');
const xh = document.getElementById('xhair');
hov1.addEventListener('mousemove', evt => {{
  const r = svg1.getBoundingClientRect();
  const sx = 880 / r.width;
  const px = (evt.clientX - r.left) * sx;
  const m = Math.round((px - M1.padL) / M1.plotW * M1.maxM);
  if (m < 0 || m > M1.maxM) return;
  const x = M1.padL + M1.plotW * m / M1.maxM;
  xh.setAttribute('x1', x); xh.setAttribute('x2', x); xh.setAttribute('visibility', 'visible');
  let rows = Object.entries(M1.series).map(([y, c]) => `MY${{y}}: <b>${{c[m]}}</b>件`).join('<br>');
  showTip(evt, `車齢 ${{Math.floor(m/12)}}年${{m%12}}ヶ月<br>` + rows);
}});
hov1.addEventListener('mouseleave', () => {{ xh.setAttribute('visibility', 'hidden'); hideTip(); }});
const svg2 = document.getElementById('chart2');
const hov2 = document.getElementById('hover2');
const dot2 = document.getElementById('dot2');
hov2.addEventListener('mousemove', evt => {{
  const r = svg2.getBoundingClientRect();
  const sx = 880 / r.width;
  const px = (evt.clientX - r.left) * sx;
  const n = M2.labels.length;
  const i = Math.max(0, Math.min(n - 1, Math.round((px - M2.padL) / M2.plotW * (n - 1))));
  const x = M2.padL + M2.plotW * i / (n - 1);
  const y = M2.padT + M2.plotH * (1 - M2.values[i] / M2.maxY);
  dot2.setAttribute('cx', x); dot2.setAttribute('cy', y); dot2.setAttribute('visibility', 'visible');
  showTip(evt, `${{M2.labels[i]}}<br>操舵系苦情の届出 <b>${{M2.values[i]}}</b>件`);
}});
hov2.addEventListener('mouseleave', () => {{ dot2.setAttribute('visibility', 'hidden'); hideTip(); }});
</script>
"""


def render_tsv(data: dict) -> str:
    lines = ["cohort\trole\ttotal_complaints\tsteering_complaints\tsteering_share\tcum_24m\tcum_48m\tcum_72m\tcum_120m"]
    for y in COHORT_YEARS:
        c = data["cohorts"][y]
        cum = c["cumulative"]
        lines.append(
            f"MY{y}\t{COHORT_NOTE[y]}\t{c['total']}\t{c['steering']}\t{c['share']:.4f}"
            f"\t{cum[24]}\t{cum[48]}\t{cum[72]}\t{cum[120]}"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    data = analyze()
    OUT_HTML.write_text(render_html(data), encoding="utf-8")
    OUT_TSV.write_text(render_tsv(data), encoding="utf-8")
    print(f"wrote {OUT_HTML.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
