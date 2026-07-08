#!/usr/bin/env python3
"""Engineer report: steering-response signs machine-read from public logs (v2).

Top-down report structure (docs/139):
  1. which part of the vehicle this is about (EPS) and what failure looks like
  2. which signals we use and why, and what NORMAL looks like
  3. validity gates (learned from v1: the pipeline first catches its own
     method artifacts — model-domain violations and insufficient excitation)
  4. what remains after gating = response-sign candidates
  5. conversion to boundary-guarded payload + SOTIF operation-phase language

v2 changes over v1:
  - model-domain gate: samples with |steering angle| > ANGLE_DOMAIN excluded;
    segments dominated by them are classified "model_domain", not flagged
  - data-quality gate: residual jumps beyond JUMP_MAX classify the segment
    as "data_quality", not as a response sign
  - excitation gate: gain/lag/asymmetry require minimum lateral excitation;
    otherwise those features are NaN (v1 flagged regression noise here)
  - every detection carries a class: data_quality / model_domain /
    response_candidate — "what did we actually catch" is now explicit

Data: commaSteeringControl (comma.ai, MIT). NOT fault detection: healthy
fleet, road/driver/load/sensor confounded. No RUL, no root cause.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / ".public_log_cache" / "FORD_MAVERICK_1ST_GEN"
OUT_HTML = REPO_ROOT / "generated" / "steering_log_sign_extraction.html"
OUT_TSV = REPO_ROOT / "data" / "steering_log_sign_extraction.tsv"

PLATFORM = "FORD_MAVERICK_1ST_GEN"
MIN_SPEED = 5.0
MIN_VALID = 300
ANGLE_SPLIT = 2.0
ANGLE_DOMAIN = 45.0      # deg; beyond this the linear vehicle model is out of domain
DOMAIN_FRACTION = 0.10   # >10% out-of-domain samples -> model_domain class
JUMP_MAX = 2.0           # m/s^2 per sample (10 Hz); beyond -> data_quality class
EXCITATION_MIN = 0.15    # m/s^2 std of implied latAccel required for gain/lag
Z_FLAG = 4.0
DT = 0.1

FEATURES = ["bias", "drift", "asymmetry", "lag", "gain_dev", "hf_noise"]
FEATURE_JA = {
    "bias": "応答バイアス", "drift": "60秒内ドリフト", "asymmetry": "左右非対称",
    "lag": "応答遅れ", "gain_dev": "ゲイン偏差", "hf_noise": "高周波不整合",
}
FEATURE_HYP = {
    "bias": "定常的な応答オフセット。片流れ・アライメント・センサ零点ずれ系の訴えに対応し得る",
    "drift": "60秒の中で応答関係が変わっていく。温度・負荷での特性変化に対応し得る",
    "asymmetry": "左右で応答が違う。片効き・機構の非対称摩耗に対応し得る",
    "lag": "操舵入力に対する実挙動の遅れ。摩擦増・ガタ・制御応答変化に対応し得る",
    "gain_dev": "同じ舵角に対する効きの大小。アシスト特性の変化に対応し得る",
    "hf_noise": "入出力の細かい不整合。ガタ・摩耗・センサノイズに対応し得る",
}


def segment_metrics(df: pd.DataFrame) -> dict | None:
    m = (df["vEgo"] > MIN_SPEED) & df["latAccelLocalizer"].notna() & df["latAccelSteeringAngle"].notna()
    d = df[m]
    if len(d) < MIN_VALID:
        return None
    angle = d["steeringAngleDeg"].to_numpy()
    out_of_domain = float(np.mean(np.abs(angle) > ANGLE_DOMAIN))
    in_dom = np.abs(angle) <= ANGLE_DOMAIN
    d = d[in_dom]
    if len(d) < MIN_VALID:
        return {"cls": "model_domain", "out_of_domain": out_of_domain}
    implied = d["latAccelSteeringAngle"].to_numpy()
    actual = d["latAccelLocalizer"].to_numpy()
    angle = d["steeringAngleDeg"].to_numpy()
    t = d["t"].to_numpy()
    r = actual - implied
    max_jump = float(np.max(np.abs(np.diff(r)))) if len(r) > 1 else 0.0

    cls = "candidate_pool"
    if out_of_domain > DOMAIN_FRACTION:
        cls = "model_domain"
    elif max_jump > JUMP_MAX:
        cls = "data_quality"

    excitation = float(np.std(implied))
    bias = float(np.mean(r))
    drift = float(np.polyfit(t, r, 1)[0]) if len(np.unique(t)) > 2 else 0.0
    left = r[angle > ANGLE_SPLIT]
    right = r[angle < -ANGLE_SPLIT]
    asym = float(np.mean(left) - np.mean(right)) if (len(left) >= 20 and len(right) >= 20 and excitation >= EXCITATION_MIN) else np.nan
    if excitation >= EXCITATION_MIN:
        a = implied - implied.mean()
        b = actual - actual.mean()
        best_shift, best_corr = 0, -np.inf
        for s in range(-5, 6):
            c = np.dot(a[: len(a) - s], b[s:]) if s >= 0 else np.dot(a[-s:], b[: len(b) + s])
            if c > best_corr:
                best_corr, best_shift = c, s
        lag = best_shift * DT
        gain = float(np.dot(a, b) / np.dot(a, a))
        gain_dev = gain - 1.0
    else:
        lag, gain_dev = np.nan, np.nan
    hf = float(np.std(np.diff(r)))
    return {
        "cls": cls, "out_of_domain": out_of_domain, "max_jump": max_jump,
        "excitation": excitation, "bias": bias, "drift": drift, "asymmetry": asym,
        "lag": lag, "gain_dev": gain_dev, "hf_noise": hf,
        "n_valid": int(len(d)), "v_mean": float(d["vEgo"].mean()),
    }


def compute() -> pd.DataFrame:
    rows = []
    for csv in sorted(DATA_DIR.glob("*.csv")):
        df = pd.read_csv(csv, usecols=["vEgo", "steeringAngleDeg", "t", "roll",
                                       "latAccelSteeringAngle", "latAccelLocalizer"])
        met = segment_metrics(df)
        if met:
            met["segment"] = csv.stem
            rows.append(met)
    table = pd.DataFrame(rows).set_index("segment")
    pool = table["cls"] == "candidate_pool"
    for f in FEATURES:
        v = table.loc[pool, f].to_numpy(dtype=float)
        med = np.nanmedian(v)
        mad = np.nanmedian(np.abs(v - med))
        scale = 1.4826 * mad if mad > 1e-12 else np.nanstd(v)
        z = np.full(len(table), np.nan)
        z[pool.to_numpy()] = (v - med) / scale if scale > 1e-12 else 0.0
        table[f"z_{f}"] = z
    zmat = table[[f"z_{f}" for f in FEATURES]].to_numpy(dtype=float)
    max_z = np.full(len(table), np.nan)
    top_f = [""] * len(table)
    for i, row in enumerate(np.abs(zmat)):
        if not np.all(np.isnan(row)):
            max_z[i] = np.nanmax(row)
            top_f[i] = FEATURES[int(np.nanargmax(row))]
    table["max_abs_z"] = max_z
    table["top_feature"] = top_f
    table.loc[pool & (table["max_abs_z"] >= Z_FLAG), "cls"] = "response_candidate"
    return table


# ---------------------------------------------------------------------------
# rendering helpers
# ---------------------------------------------------------------------------

def eps_diagram() -> str:
    boxes = [
        (10, "ハンドル"), (150, "トルク/舵角センサ"), (330, "EPS ECU"),
        (460, "モータ+減速機"), (630, "ラック"), (760, "タイヤ"),
    ]
    parts = ["<svg viewBox='0 0 880 120' role='img' aria-label='EPSの構成図'>"]
    prev_end = None
    for x, label in boxes:
        w = 110 if len(label) <= 5 else 150
        parts.append(f"<rect x='{x}' y='30' width='{w}' height='40' rx='8' class='dbox'/>")
        parts.append(f"<text x='{x + w/2}' y='55' text-anchor='middle' class='dlabel2'>{label}</text>")
        if prev_end is not None:
            parts.append(f"<line x1='{prev_end}' y1='50' x2='{x}' y2='50' class='darrow' marker-end='url(#ah)'/>")
        prev_end = x + w
    parts.insert(1, "<defs><marker id='ah' markerWidth='8' markerHeight='8' refX='7' refY='4' orient='auto'>"
                    "<path d='M0,0 L8,4 L0,8 z' class='darrowhead'/></marker></defs>")
    parts.append("<text x='215' y='100' class='dnote'>入力側: 操舵角(本デモで使用)</text>")
    parts.append("<text x='620' y='100' class='dnote'>出力側: 車両の実挙動=横加速度(本デモで使用)</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def seg_figure(seg: str, caption: str) -> str:
    df = pd.read_csv(DATA_DIR / f"{seg}.csv",
                     usecols=["vEgo", "t", "steeringAngleDeg", "latAccelSteeringAngle", "latAccelLocalizer"])
    d = df[(df["vEgo"] > MIN_SPEED) & (df["steeringAngleDeg"].abs() <= ANGLE_DOMAIN)]
    t = d["t"].to_numpy()
    implied = d["latAccelSteeringAngle"].to_numpy()
    actual = d["latAccelLocalizer"].to_numpy()
    r = actual - implied
    width, h1, h2 = 880, 190, 120
    pad_l, pad_r, pad_t, gap = 48, 16, 24, 14
    plot_w = width - pad_l - pad_r
    lo = float(min(implied.min(), actual.min())); hi = float(max(implied.max(), actual.max()))
    span = (hi - lo) or 1.0; lo -= span * .08; hi += span * .08
    rlo, rhi = float(np.percentile(r, 0.5)), float(np.percentile(r, 99.5))
    rspan = (rhi - rlo) or 0.1; rlo -= rspan * .2; rhi += rspan * .2
    xs = lambda tt: pad_l + plot_w * tt / 60.0
    y1 = lambda v: pad_t + (h1 - pad_t - 8) * (1 - (v - lo) / (hi - lo))
    y2 = lambda v: h1 + gap + (h2 - 28) * (1 - (v - rlo) / (rhi - rlo))
    parts = [f"<svg viewBox='0 0 {width} {h1 + gap + h2}' role='img' aria-label='segment {seg}'>"]
    parts.append(f"<text x='{pad_l}' y='14' class='htitle'>{caption}</text>")
    parts.append(f"<line x1='{pad_l}' y1='{y1(0):.1f}' x2='{pad_l+plot_w}' y2='{y1(0):.1f}' class='grid'/>")
    for series, cls in ((implied, "s0"), (actual, "s1")):
        pts = " ".join(f"{xs(tt):.1f},{y1(v):.1f}" for tt, v in zip(t, series))
        parts.append(f"<polyline points='{pts}' fill='none' class='{cls}' stroke-width='1.5'/>")
    parts.append(f"<text x='{pad_l-6}' y='{y1(hi-span*.08)+4:.1f}' class='tick' text-anchor='end'>{hi:.1f}</text>")
    parts.append(f"<text x='{pad_l-6}' y='{y1(lo+span*.08)+4:.1f}' class='tick' text-anchor='end'>{lo:.1f}</text>")
    parts.append(f"<text x='{pad_l}' y='{h1+gap-2}' class='tick'>残差 r(t) = 実測 − 含意 [m/s²]</text>")
    parts.append(f"<line x1='{pad_l}' y1='{y2(0):.1f}' x2='{pad_l+plot_w}' y2='{y2(0):.1f}' class='grid'/>")
    pts = " ".join(f"{xs(tt):.1f},{y2(max(min(v, rhi), rlo)):.1f}" for tt, v in zip(t, r))
    parts.append(f"<polyline points='{pts}' fill='none' class='s2' stroke-width='1.3'/>")
    parts.append(f"<text x='{pad_l-6}' y='{y2(rhi-rspan*.2)+4:.1f}' class='tick' text-anchor='end'>{rhi:.2f}</text>")
    parts.append(f"<text x='{pad_l-6}' y='{y2(rlo+rspan*.2)+4:.1f}' class='tick' text-anchor='end'>{rlo:.2f}</text>")
    parts.append(f"<text x='{pad_l}' y='{h1+gap+h2-4}' class='tick'>0s</text>")
    parts.append(f"<text x='{pad_l+plot_w}' y='{h1+gap+h2-4}' class='tick' text-anchor='end'>60s</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def hist_svg(values, flags, title, unit, width=420, height=160) -> str:
    v = values[~np.isnan(values)]
    fl = flags[~np.isnan(values)]
    if len(v) == 0:
        return ""
    lo, hi = np.percentile(v, 0.5), np.percentile(v, 99.5)
    pad = (hi - lo) * 0.05 or 1e-6
    lo, hi = lo - pad, hi + pad
    nbins = 40
    edges = np.linspace(lo, hi, nbins + 1)
    counts, _ = np.histogram(np.clip(v, lo, hi), bins=edges)
    fcounts, _ = np.histogram(np.clip(v[fl], lo, hi), bins=edges)
    pad_l, pad_b, pad_t = 8, 24, 22
    plot_w, plot_h = width - 2 * pad_l, height - pad_b - pad_t
    max_c = counts.max() or 1
    parts = [f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='{title}'>"]
    parts.append(f"<text x='{pad_l}' y='14' class='htitle'>{title} <tspan class='hunit'>[{unit}]</tspan></text>")
    bw = plot_w / nbins
    for i, (c, fc) in enumerate(zip(counts, fcounts)):
        if c == 0:
            continue
        h = plot_h * c / max_c
        cls = "hbar-f" if fc > 0 else "hbar"
        parts.append(f"<rect x='{pad_l + i*bw:.1f}' y='{pad_t + plot_h - h:.1f}' width='{max(bw-1,1):.1f}' height='{h:.1f}' class='{cls}' rx='2'/>")
    parts.append(f"<line x1='{pad_l}' y1='{pad_t+plot_h}' x2='{pad_l+plot_w}' y2='{pad_t+plot_h}' class='axis'/>")
    parts.append(f"<text x='{pad_l}' y='{height-6}' class='tick'>{lo:.3g}</text>")
    parts.append(f"<text x='{pad_l+plot_w}' y='{height-6}' class='tick' text-anchor='end'>{hi:.3g}</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def payload_for(seg: str, row: pd.Series) -> dict:
    feat = row["top_feature"]
    return {
        "component": "steering / EPS (public-log stand-in)",
        "observed_context": f"steering-response consistency deviation: {feat} at robust-z {row['max_abs_z']:.1f} vs platform population (after validity gates)",
        "relation_to_function": "lateral response differed from steering-angle-implied response within normal operation",
        "monitor_status": "below any fault threshold; population-referenced statistical sign only",
        "recurrence": "single 60 s segment; per-vehicle recurrence not trackable in this dataset",
        "retained_fields": {f: (None if pd.isna(row[f]) else round(float(row[f]), 4)) for f in FEATURES},
        "confidence": "low (healthy public fleet; road, driver, load, sensor confounded)",
        "recommended_read": "inside an EPS: read recurrence across key cycles and co-occurring supply-voltage / temperature / assist-state context before any component conclusion",
        "boundary": "not fault detection, not a vehicle verdict, not root cause, not RUL",
        "sotif_mapping": {
            "triggering_condition_candidate": f"sustained {feat} deviation of steering response under normal driving",
            "eooc_use": "component-side observed rate for validating the assumed occurrence rate of steering functional insufficiencies (ISO 21448 operation phase)",
        },
    }


def render_html(table: pd.DataFrame) -> str:
    pool = table[table["cls"].isin(["candidate_pool", "response_candidate"])]
    cand = table[table["cls"] == "response_candidate"].sort_values("max_abs_z", ascending=False)
    n_all = len(table)
    counts = table["cls"].value_counts().to_dict()
    # normal exemplar: well-excited, near-median z
    well = pool[(pool["excitation"] >= EXCITATION_MIN)].copy()
    normal_seg = (well["max_abs_z"] - well["max_abs_z"].median()).abs().idxmin()
    hists = []
    flags = (pool["cls"] == "response_candidate").to_numpy()
    for f in FEATURES:
        unit = {"bias": "m/s²", "drift": "m/s²/s", "asymmetry": "m/s²",
                "lag": "s", "gain_dev": "-", "hf_noise": "m/s²"}[f]
        hists.append(hist_svg(pool[f].to_numpy(dtype=float), flags, FEATURE_JA[f], unit))
    hist_grid = "\n".join(f"<div class='hcell'>{h}</div>" for h in hists if h)

    hyp_rows = "\n".join(
        f"<tr><td>{FEATURE_JA[f]}</td><td>{FEATURE_HYP[f]}</td></tr>" for f in FEATURES
    )
    well_excited = cand[cand["excitation"] >= 0.25]
    top = well_excited.head(2) if len(well_excited) >= 2 else cand.head(2)
    cand_figs = "\n".join(
        f"<div class='card'>{seg_figure(seg, f'応答オフセット候補 segment {seg} — {FEATURE_JA[row.top_feature]} z={row.max_abs_z:.1f}')}"
        f"<p class='note'>上段: 青=操舵角が含意する横加速度 / 緑=実測。下段: 残差r(t)。目視では上段の2本はほぼ重なって見えるが、"
        f"残差の統計量が母集団から外れている。</p></div>"
        for seg, row in top.iterrows()
    )
    payloads_html = "\n".join(
        f"<pre>{json.dumps(payload_for(seg, row), ensure_ascii=False, indent=2)}</pre>" for seg, row in top.iterrows()
    )
    cand_rows = "\n".join(
        f"<tr><td>{seg}</td><td>{FEATURE_JA[r['top_feature']]}</td><td class='num'>{r['max_abs_z']:.1f}</td>"
        f"<td class='num'>{r['excitation']:.2f}</td><td class='num'>{r['v_mean']:.1f}</td></tr>"
        for seg, r in cand.head(10).iterrows()
    )

    return f"""<meta charset='utf-8'>
<title>操舵応答の兆候抽出レポート — {PLATFORM}</title>
<style>
:root {{ color-scheme: light dark; }}
.viz-root {{
  --surface-1:#fcfcfb; --page:#f9f9f7; --ink-1:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --s0:#2a78d6; --s1:#1baf7a; --s2:#4a3aa7; --flag:#e34948;
}}
@media (prefers-color-scheme: dark) {{
  .viz-root {{ --surface-1:#1a1a19; --page:#0d0d0d; --ink-1:#ffffff; --ink-2:#c3c2b7;
    --grid:#2c2c2a; --axis:#383835; --s0:#3987e5; --s1:#199e70; --s2:#9085e9; --flag:#e66767; }}
}}
.viz-root {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: var(--page);
  color: var(--ink-1); margin: 0 auto; max-width: 64rem; padding: 2rem 1.5rem; line-height: 1.7; }}
h1 {{ font-size: 1.3rem; }} h2 {{ font-size: 1.1rem; margin-top: 2.4rem; border-bottom: 2px solid var(--grid); padding-bottom: .3rem; }}
.card {{ background: var(--surface-1); color: var(--ink-1); border: 1px solid var(--grid); border-radius: 8px; padding: 1rem 1.2rem; margin: 1rem 0; }}
.note {{ font-size: .88rem; color: var(--ink-2); }}
svg {{ width: 100%; height: auto; display: block; }}
.grid {{ stroke: var(--grid); }} .axis {{ stroke: var(--axis); }}
.tick {{ fill: var(--muted); font-size: 11px; }}
.htitle {{ fill: var(--ink-1); font-size: 13px; font-weight: 600; }} .hunit {{ fill: var(--muted); font-weight: 400; }}
.hbar {{ fill: var(--s0); opacity: .85; }} .hbar-f {{ fill: var(--flag); }}
.s0 {{ stroke: var(--s0); }} .s1 {{ stroke: var(--s1); }} .s2 {{ stroke: var(--s2); }}
.dbox {{ fill: var(--surface-1); stroke: var(--axis); }} .dlabel2 {{ fill: var(--ink-1); font-size: 13px; }}
.darrow {{ stroke: var(--muted); stroke-width: 1.5; }} .darrowhead {{ fill: var(--muted); }}
.dnote {{ fill: var(--ink-2); font-size: 12px; }}
.hgrid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr)); gap: .8rem; }}
.hcell {{ background: var(--surface-1); border: 1px solid var(--grid); border-radius: 8px; padding: .5rem; }}
table {{ border-collapse: collapse; width: 100%; background: var(--surface-1); color: var(--ink-1); font-size: .9rem; }}
th, td {{ border: 1px solid var(--grid); padding: .45rem .7rem; text-align: left; color: var(--ink-1); }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
th {{ color: var(--ink-2); font-weight: 600; }}
pre {{ background: var(--surface-1); color: var(--ink-1); border: 1px solid var(--grid); border-radius: 8px;
  padding: .8rem; overflow-x: auto; font-size: .78rem; }}
.boundary {{ border-left: 3px solid var(--axis); padding-left: .8rem; }}
code {{ background: var(--surface-1); color: var(--ink-1); padding: .05rem .3rem; border-radius: 4px; }}
.lede {{ font-size: .95rem; }}
</style>
<div class='viz-root'>
<h1>操舵応答の兆候抽出 — 公開走行logによる実証({PLATFORM})</h1>

<h2>1. これは車両のどの部分の話か</h2>
<p class='lede'>電動パワーステアリング(EPS)は、運転者のハンドル操作をセンサで読み取り、電気モータの力で操舵を補助する装置である。
現代の乗用車のほぼ全てに搭載され、車を「曲げる」機能の実行部品にあたる。</p>
<div class='card'>{eps_diagram()}</div>

<h2>2. 故障すると何が起きるか</h2>
<p class='lede'>EPSの補助が失われると、ハンドルは突然重くなる。特に低速での取り回し中に起きると危険で、
米国では「低速旋回中に約1秒だけ補助が消えて突然戻る」事象がリコールになった実例がある(GM 17V-414)。
さらに厄介なのは、<b>故障コード(DTC)が残らない一過性の事象</b>で、この場合は入庫しても「異常なし」となり、
再発と誤診(不要な部品交換)が公式文書に記録されるほど繰り返された(Ford 15S18、GM TSB 17-NA-158)。
故障として確定する前の「普段と違う」を捕まえる手段が、実務に存在しないことが問題の核心である。</p>

<h2>3. どの信号を見るか、正常はどう見えるか</h2>
<p class='lede'>公開logには、<b>入力側</b>(操舵角)と<b>出力側</b>(車両が実際にした横方向の運動=横加速度)の両方が入っている。
操舵角を車両モデルに通すと「この舵角ならこの横加速度になるはず」という<b>含意値</b>が計算でき、実測との差
<code>r(t) = 実測 − 含意</code> が<b>操舵系の応答一貫性</b>を表す。正常なら2本の波形はほぼ重なり、残差は小さくゼロ中心で構造を持たない。</p>
<div class='card'>{seg_figure(normal_seg, f'正常の見本 segment {normal_seg}(母集団の典型)')}
<p class='note'>上段: 青=含意横加速度 / 緑=実測。下段: 残差。正常時の残差は±0.2 m/s²程度に収まり、時間構造(片寄り・ドリフト・遅れ)を持たない。</p></div>
<p class='note'>残差そのものは人間にも見える。<b>人間に見えないのは母集団との比較</b>である——938セグメントの残差統計の中で、
どのセグメントの偏りが「同じ車種・同じ速度域の普段」から統計的に外れているかは、目視では判定できない。</p>

<h2>4. 異常(兆候)はどの形で現れ得るか</h2>
<p class='note'>残差を6つの特徴量に圧縮する。各特徴と、それが対応し得る壊れ方の<b>仮説</b>(断定ではない):</p>
<table><tr><th>特徴量</th><th>物理的な読み(仮説)</th></tr>{hyp_rows}</table>

<h2>5. 妥当性ゲート — 手法がまず拾うのは手法自身の欠陥である</h2>
<p class='lede'>v1の検出上位を検分した結果、大半は部品の兆候ではなく<b>手法のアーティファクト</b>だった(このレポートの誠実性の核なのでそのまま書く):
①大舵角(|角度|&gt;{ANGLE_DOMAIN:.0f}°)では車両モデル自体が適用域外(検分例: 舵角−286°で残差ジャンプ19 m/s²)。
②ほぼ直進(励起不足)ではゲイン推定が数値的に暴れる(検分例: 舵角±3°でz=16)。
そこでv2では、モデル適用域ゲート・データ品質ゲート(残差ジャンプ&gt;{JUMP_MAX:.0f} m/s²/sample)・励起ゲート(含意std&ge;{EXCITATION_MIN} m/s²)を前段に入れ、
検出を<b>クラス分け</b>して報告する。</p>
<table>
<tr><th>クラス</th><th>意味</th><th>件数</th></tr>
<tr><td>model_domain</td><td>大舵角が多くモデル適用域外(兆候とは呼ばない)</td><td class='num'>{counts.get('model_domain', 0)}</td></tr>
<tr><td>data_quality</td><td>物理的にあり得ない残差ジャンプ=データ/モデル品質問題</td><td class='num'>{counts.get('data_quality', 0)}</td></tr>
<tr><td>candidate_pool</td><td>ゲート通過・母集団の通常範囲</td><td class='num'>{counts.get('candidate_pool', 0)}</td></tr>
<tr><td><b>response_candidate</b></td><td><b>ゲート通過後もrobust |z|≥{Z_FLAG:.0f}が残る=応答兆候の候補</b></td><td class='num'><b>{counts.get('response_candidate', 0)}</b></td></tr>
</table>

<h2>6. ゲート通過後に残った応答兆候の候補</h2>
<div class='hgrid'>{hist_grid}</div>
<p class='note'>赤=response_candidateを含むbin。全{n_all}セグメント中、ゲート通過は{counts.get('candidate_pool',0)+counts.get('response_candidate',0)}件、うち候補{counts.get('response_candidate',0)}件。</p>
<table>
<tr><th>segment</th><th>主特徴</th><th>robust z</th><th>励起 [m/s²]</th><th>平均車速 [m/s]</th></tr>
{cand_rows}
</table>
<p class='note'>正直な注記: ゲイン偏差の候補は励起がゲート下限({EXCITATION_MIN} m/s²)付近に集中しており、
推定分散の裾を拾っている可能性がまだ高い(励起が小さいほどゲイン推定は不安定)。
<b>現時点で最も信用できる候補は、十分に励起されたセグメントのドリフト・非対称系</b>であり、下の見本はそこから選んだ。
ゲート値の1点調整で候補が入れ替わること自体が、運用閾値には結果ラベルが要るという限界4の実例である。</p>
{cand_figs}

<h2>7. 兆候を「言葉」に変換する — payloadとSOTIF</h2>
<p class='note'>候補セグメントは、原因を断定しない状態説明(payload)へ機械変換される。boundaryフィールドが禁止主張を遮断し、
sotif_mappingがISO 21448運用フェーズ監視(SOTIF-EooCの仮定発生率検証)への部品側インプットの形を与える。</p>
{payloads_html}

<h2>8. 限界</h2>
<p class='note boundary'>
1. <b>これは故障検出ではない。</b>健全な公開fleetのlogであり、候補に残った偏りも路面(カント)・運転者・積載・センサ状態と交絡している。
切り分けには、EPS内部信号(供給電圧・温度・アシスト状態)との同時観測が必要で、それがEPS内部実装(docs/122)の役割である。<br>
2. 車両モデルの誤差、roll補正の簡略化。<br>
3. 車両個体が区別できないため、再発(同一個体での繰り返し)は追えない。<br>
4. 閾値(z={Z_FLAG:.0f}、ゲート値)はデモ値であり、運用値の設定には結果ラベルが要る。
</p>
<p class='note'>データ: <a href='https://huggingface.co/datasets/commaai/commaSteeringControl'>commaSteeringControl</a>(comma.ai、MIT license)。
再現: <code>python3 scripts/steering_log_sign_extraction.py</code></p>
</div>
"""


def main() -> None:
    table = compute()
    print(table["cls"].value_counts().to_string())
    cand = table[table["cls"] == "response_candidate"].sort_values("max_abs_z", ascending=False)
    print(cand[["top_feature", "max_abs_z", "excitation", "v_mean"]].head(10).to_string())
    cols = ["cls", "out_of_domain", "max_jump", "excitation"] + FEATURES + [f"z_{f}" for f in FEATURES] + ["max_abs_z", "top_feature", "n_valid", "v_mean"]
    cols = [c for c in cols if c in table.columns]
    table[cols].round(5).to_csv(OUT_TSV, sep="\t")
    OUT_HTML.write_text(render_html(table), encoding="utf-8")
    print(f"wrote {OUT_TSV.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_HTML.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
