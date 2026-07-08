#!/usr/bin/env python3
"""Extract machine-readable steering-response signs from public driving logs.

Engineer-facing demo (docs/139). Business-model role (docs/138, layer 1):
show, end-to-end on public data, that a component-side pipeline can read
signs out of runtime logs that a human cannot see in the raw traces, and
convert them into boundary-guarded state explanations that plug into SOTIF
operation-phase monitoring (EooC assumed-insufficiency-rate language).

Data: commaSteeringControl (comma.ai, MIT license), one platform.
Each 60 s segment @10 Hz carries both:
    latAccelSteeringAngle : lateral accel implied by the steering angle
                            through the vehicle model
    latAccelLocalizer     : lateral accel actually measured (sensor fusion)
Their residual r(t) is the steering-response consistency signal.

Per-segment features (population-referenced robust z-scores):
    bias       mean(r)                       systematic response offset
    drift      d(r)/dt over the segment      within-segment change
    asymmetry  mean(r|angle>+2deg) - mean(r|angle<-2deg)
    lag        argmax xcorr(implied, actual) response delay [s]
    gain       slope of actual ~ implied     response gain deviation from 1
    hf_noise   std of first-difference of r  high-frequency inconsistency

THIS IS NOT FAULT DETECTION. The fleet is healthy; road, driver, load and
sensor effects are confounded with any component state. What the demo
demonstrates is the mechanism: log -> population-referenced sign ->
boundary-guarded component-side statement. No RUL, no root cause, no
vehicle verdicts.
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
MIN_SPEED = 5.0          # m/s; below this the vehicle model is unreliable
MIN_VALID = 300          # of 600 samples
ANGLE_SPLIT = 2.0        # deg, for asymmetry
Z_FLAG = 4.0             # robust-z threshold for flagging
DT = 0.1                 # 10 Hz

FEATURES = ["bias", "drift", "asymmetry", "lag", "gain_dev", "hf_noise"]
FEATURE_JA = {
    "bias": "応答バイアス",
    "drift": "60秒内ドリフト",
    "asymmetry": "左右非対称",
    "lag": "応答遅れ",
    "gain_dev": "ゲイン偏差",
    "hf_noise": "高周波不整合",
}


def segment_features(df: pd.DataFrame) -> dict | None:
    m = (df["vEgo"] > MIN_SPEED) & df["latAccelLocalizer"].notna() & df["latAccelSteeringAngle"].notna()
    d = df[m]
    if len(d) < MIN_VALID:
        return None
    implied = d["latAccelSteeringAngle"].to_numpy()
    actual = d["latAccelLocalizer"].to_numpy()
    r = actual - implied
    t = d["t"].to_numpy()
    angle = d["steeringAngleDeg"].to_numpy()

    bias = float(np.mean(r))
    drift = float(np.polyfit(t, r, 1)[0]) if len(np.unique(t)) > 2 else 0.0
    left = r[angle > ANGLE_SPLIT]
    right = r[angle < -ANGLE_SPLIT]
    asym = float(np.mean(left) - np.mean(right)) if len(left) >= 20 and len(right) >= 20 else np.nan
    # lag via cross-correlation on mean-removed series, +-0.5 s
    a = implied - implied.mean()
    b = actual - actual.mean()
    max_shift = 5
    best_shift, best_corr = 0, -np.inf
    for s in range(-max_shift, max_shift + 1):
        if s >= 0:
            c = np.dot(a[: len(a) - s], b[s:])
        else:
            c = np.dot(a[-s:], b[: len(b) + s])
        if c > best_corr:
            best_corr, best_shift = c, s
    lag = best_shift * DT
    denom = float(np.dot(a, a))
    gain = float(np.dot(a, b) / denom) if denom > 1e-6 else np.nan
    hf = float(np.std(np.diff(r)))
    return {
        "bias": bias, "drift": drift, "asymmetry": asym, "lag": lag,
        "gain_dev": (gain - 1.0) if not math.isnan(gain) else np.nan,
        "hf_noise": hf,
        "n_valid": int(len(d)), "v_mean": float(d["vEgo"].mean()),
    }


def compute() -> tuple[pd.DataFrame, dict]:
    rows = []
    for csv in sorted(DATA_DIR.glob("*.csv")):
        df = pd.read_csv(csv, usecols=["vEgo", "steeringAngleDeg", "t",
                                       "latAccelSteeringAngle", "latAccelLocalizer"])
        feats = segment_features(df)
        if feats:
            feats["segment"] = csv.stem
            rows.append(feats)
    table = pd.DataFrame(rows).set_index("segment")
    zcols = {}
    for f in FEATURES:
        v = table[f].to_numpy(dtype=float)
        med = np.nanmedian(v)
        mad = np.nanmedian(np.abs(v - med))
        scale = 1.4826 * mad if mad > 1e-12 else np.nanstd(v)
        zcols[f"z_{f}"] = (v - med) / scale if scale > 1e-12 else np.zeros_like(v)
    for k, v in zcols.items():
        table[k] = v
    zmat = table[[f"z_{f}" for f in FEATURES]].to_numpy(dtype=float)
    table["max_abs_z"] = np.nanmax(np.abs(zmat), axis=1)
    table["top_feature"] = [FEATURES[i] for i in np.nanargmax(np.abs(zmat), axis=1)]
    flagged = table[table["max_abs_z"] >= Z_FLAG].sort_values("max_abs_z", ascending=False)
    return table, {"flagged": flagged}


def payload_for(seg: str, row: pd.Series) -> dict:
    feat = row["top_feature"]
    return {
        "component": "steering / EPS (public-log stand-in)",
        "observed_context": f"steering-response consistency deviation: {feat} at robust-z {row['max_abs_z']:.1f} vs platform population",
        "relation_to_function": "lateral response differed from steering-angle-implied response within normal operation (no fault code context in this data)",
        "monitor_status": "below any fault threshold; population-referenced statistical sign only",
        "recurrence": "single 60 s segment; recurrence tracking requires longitudinal data per vehicle",
        "retained_fields": {f: (None if pd.isna(row[f]) else round(float(row[f]), 4)) for f in FEATURES},
        "confidence": "low (public healthy-fleet data; road, driver, load and sensor effects are confounded)",
        "recommended_read": "if this sign were produced inside the EPS: read recurrence across key cycles, co-occurring supply-voltage and temperature context, before any component conclusion",
        "boundary": "not a fault detection, not a vehicle verdict, not root cause, not RUL; mechanism demonstration on public data",
        "sotif_mapping": {
            "triggering_condition_candidate": f"sustained {feat} deviation of steering response under normal driving",
            "eooc_use": "component-side observed rate for validating the assumed occurrence rate of steering functional insufficiencies during the operation phase (ISO 21448 field monitoring)",
        },
    }


def hist_svg(values: np.ndarray, flags: np.ndarray, title: str, unit: str,
             width=420, height=170) -> str:
    v = values[~np.isnan(values)]
    fl = flags[~np.isnan(values)]
    lo, hi = np.percentile(v, 0.5), np.percentile(v, 99.5)
    pad = (hi - lo) * 0.05 or 1e-6
    lo, hi = lo - pad, hi + pad
    nbins = 40
    edges = np.linspace(lo, hi, nbins + 1)
    counts, _ = np.histogram(np.clip(v, lo, hi), bins=edges)
    fcounts, _ = np.histogram(np.clip(v[fl], lo, hi), bins=edges)
    pad_l, pad_b, pad_t = 8, 26, 22
    plot_w, plot_h = width - 2 * pad_l, height - pad_b - pad_t
    max_c = counts.max() or 1
    parts = [f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='{title}'>"]
    parts.append(f"<text x='{pad_l}' y='14' class='htitle'>{title} <tspan class='hunit'>[{unit}]</tspan></text>")
    bw = plot_w / nbins
    for i, (c, fc) in enumerate(zip(counts, fcounts)):
        if c == 0:
            continue
        h = plot_h * c / max_c
        x = pad_l + i * bw
        y = pad_t + plot_h - h
        cls = "hbar-f" if fc > 0 else "hbar"
        parts.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{max(bw-1,1):.1f}' height='{h:.1f}' class='{cls}' rx='2'/>")
    parts.append(f"<line x1='{pad_l}' y1='{pad_t+plot_h}' x2='{pad_l+plot_w}' y2='{pad_t+plot_h}' class='axis'/>")
    parts.append(f"<text x='{pad_l}' y='{height-8}' class='tick'>{lo:.3g}</text>")
    parts.append(f"<text x='{pad_l+plot_w}' y='{height-8}' class='tick' text-anchor='end'>{hi:.3g}</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def trace_svg(seg: str, note: str, width=880, height=240) -> str:
    df = pd.read_csv(DATA_DIR / f"{seg}.csv",
                     usecols=["vEgo", "t", "latAccelSteeringAngle", "latAccelLocalizer"])
    m = df["vEgo"] > MIN_SPEED
    d = df[m]
    t = d["t"].to_numpy()
    implied = d["latAccelSteeringAngle"].to_numpy()
    actual = d["latAccelLocalizer"].to_numpy()
    pad_l, pad_r, pad_t, pad_b = 48, 16, 24, 30
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
    lo = float(np.nanmin([implied.min(), actual.min()]))
    hi = float(np.nanmax([implied.max(), actual.max()]))
    span = (hi - lo) or 1.0
    lo, hi = lo - span * 0.08, hi + span * 0.08
    xs = lambda tt: pad_l + plot_w * tt / 60.0
    ys = lambda v: pad_t + plot_h * (1 - (v - lo) / (hi - lo))
    parts = [f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='segment {seg} 波形'>"]
    parts.append(f"<text x='{pad_l}' y='14' class='htitle'>segment {seg} — {note}</text>")
    parts.append(f"<line x1='{pad_l}' y1='{ys(0):.1f}' x2='{pad_l+plot_w}' y2='{ys(0):.1f}' class='grid'/>")
    for series, cls in ((implied, "s0"), (actual, "s1")):
        pts = " ".join(f"{xs(tt):.1f},{ys(v):.1f}" for tt, v in zip(t, series))
        parts.append(f"<polyline points='{pts}' fill='none' class='{cls}' stroke-width='1.6'/>")
    parts.append(f"<text x='{pad_l}' y='{height-6}' class='tick'>0s</text>")
    parts.append(f"<text x='{pad_l+plot_w}' y='{height-6}' class='tick' text-anchor='end'>60s</text>")
    parts.append(f"<text x='{pad_l-6}' y='{ys(hi- span*0.08)+4:.1f}' class='tick' text-anchor='end'>{hi:.1f}</text>")
    parts.append(f"<text x='{pad_l-6}' y='{ys(lo+span*0.08)+4:.1f}' class='tick' text-anchor='end'>{lo:.1f}</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def render_html(table: pd.DataFrame, flagged: pd.DataFrame) -> str:
    n = len(table)
    nf = len(flagged)
    hists = []
    for f in FEATURES:
        unit = {"bias": "m/s²", "drift": "m/s²/s", "asymmetry": "m/s²",
                "lag": "s", "gain_dev": "-", "hf_noise": "m/s²"}[f]
        hists.append(hist_svg(table[f].to_numpy(dtype=float),
                              (table["max_abs_z"] >= Z_FLAG).to_numpy(),
                              FEATURE_JA[f], unit))
    hist_grid = "\n".join(f"<div class='hcell'>{h}</div>" for h in hists)

    top = flagged.head(3)
    traces, payloads = [], []
    for seg, row in top.iterrows():
        note = f"{FEATURE_JA[row['top_feature']]} z={row['max_abs_z']:.1f}"
        traces.append(f"<div class='card'>{trace_svg(seg, note)}"
                      f"<p class='note'>青=操舵角から車両モデルが予測した横加速度 / 緑=実測(localizer)。"
                      f"目視では差が分からない波形でも、母集団参照の統計量には現れる。</p></div>")
        payloads.append(f"<pre>{json.dumps(payload_for(seg, row), ensure_ascii=False, indent=2)}</pre>")
    traces_html = "\n".join(traces)
    payloads_html = "\n".join(payloads)

    flag_rows = "\n".join(
        f"<tr><td>{seg}</td><td>{FEATURE_JA[r['top_feature']]}</td><td class='num'>{r['max_abs_z']:.1f}</td>"
        f"<td class='num'>{r['v_mean']:.1f} m/s</td><td class='num'>{int(r['n_valid'])}</td></tr>"
        for seg, r in flagged.head(10).iterrows()
    )

    return f"""<meta charset='utf-8'>
<title>Steering Log Sign Extraction — {PLATFORM}</title>
<style>
.viz-root {{
  --surface-1:#fcfcfb; --page:#f9f9f7; --ink-1:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --s0:#2a78d6; --s1:#1baf7a; --flag:#e34948;
}}
@media (prefers-color-scheme: dark) {{
  .viz-root {{ --surface-1:#1a1a19; --page:#0d0d0d; --ink-1:#ffffff; --ink-2:#c3c2b7;
    --grid:#2c2c2a; --axis:#383835; --s0:#3987e5; --s1:#199e70; --flag:#e66767; }}
}}
.viz-root {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: var(--page);
  color: var(--ink-1); margin: 0 auto; max-width: 64rem; padding: 2rem 1.5rem; line-height: 1.65; }}
h1 {{ font-size: 1.3rem; }} h2 {{ font-size: 1.05rem; margin-top: 2.2rem; }}
.card {{ background: var(--surface-1); border: 1px solid var(--grid); border-radius: 8px; padding: 1rem 1.2rem; margin: 1rem 0; }}
.note {{ font-size: .88rem; color: var(--ink-2); }}
svg {{ width: 100%; height: auto; display: block; }}
.grid {{ stroke: var(--grid); }} .axis {{ stroke: var(--axis); }}
.tick {{ fill: var(--muted); font-size: 11px; }}
.htitle {{ fill: var(--ink-1); font-size: 13px; font-weight: 600; }} .hunit {{ fill: var(--muted); font-weight: 400; }}
.hbar {{ fill: var(--s0); opacity: .85; }} .hbar-f {{ fill: var(--flag); }}
.s0 {{ stroke: var(--s0); }} .s1 {{ stroke: var(--s1); }}
.hgrid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr)); gap: .8rem; }}
.hcell {{ background: var(--surface-1); border: 1px solid var(--grid); border-radius: 8px; padding: .5rem; }}
table {{ border-collapse: collapse; width: 100%; background: var(--surface-1); font-size: .9rem; }}
th, td {{ border: 1px solid var(--grid); padding: .4rem .7rem; text-align: left; }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
th {{ color: var(--ink-2); font-weight: 600; }}
pre {{ background: var(--surface-1); border: 1px solid var(--grid); border-radius: 8px;
  padding: .8rem; overflow-x: auto; font-size: .78rem; }}
.boundary {{ border-left: 3px solid var(--axis); padding-left: .8rem; }}
code {{ background: var(--surface-1); padding: .05rem .3rem; border-radius: 4px; }}
</style>
<div class='viz-root'>
<h1>公開走行logからの操舵応答兆候の機械抽出 — {PLATFORM}</h1>
<p class='note card'><b>これは何のデモか:</b> 部品側のパイプラインが、runtimeのlogから<b>人間がraw波形を見ても分からない統計的な兆候</b>を読み取り、
原因断定なしの状態説明(payload)とSOTIF運用フェーズ監視の言葉に機械変換できることを、公開データでend-to-endに示す。<br>
<b>これは何でないか:</b> 故障検出ではない。対象は健全な車両群の公開logであり、路面・運転者・積載・センサの影響が交絡する。個車の判定・RUL・原因断定は出力しない(境界はpayload内に機械的に明記される)。</p>

<h2>方法</h2>
<div class='card note'>
残差 <code>r(t) = latAccelLocalizer − latAccelSteeringAngle</code>(実測横加速度 − 操舵角が車両モデル経由で含意する横加速度)を各60秒セグメント(10Hz、有効サンプル{MIN_VALID}以上、車速&gt;{MIN_SPEED:.0f}m/s)で計算し、
6特徴(応答バイアス、60秒内ドリフト、左右非対称、応答遅れ、ゲイン偏差、高周波不整合)へ圧縮。
母集団(同一platform全セグメント)のmedian/MADによるrobust z-scoreで正規化し、|z|≥{Z_FLAG:.0f}を兆候として検出する。学習モデルなし・決定的・全て再現可能。
</div>

<h2>結果: {n}セグメント中 {nf}セグメントに統計的兆候(|z|≥{Z_FLAG:.0f})</h2>
<p class='note'>閾値感度: |z|≥4で{nf}件、|z|≥6で{int((table['max_abs_z']>=6).sum())}件、|z|≥8で{int((table['max_abs_z']>=8).sum())}件。
特徴量の分布は裾が重く、閾値は確定的な線ではない(限界4を参照)。</p>
<div class='hgrid'>
{hist_grid}
</div>
<p class='note'>赤=兆候として検出されたセグメントを含むbin。分布の裾は目視のraw波形では判別できない。</p>

<h2>検出セグメント(上位)</h2>
<table>
<tr><th>segment</th><th>主特徴</th><th>robust z</th><th>平均車速</th><th>有効サンプル</th></tr>
{flag_rows}
</table>

<h2>兆候セグメントの波形と、生成された状態説明(payload)</h2>
{traces_html}
{payloads_html}

<h2>SOTIFへの接続</h2>
<p class='note card'>ISO 21448は市場投入後のフィールド監視を要求し、部品サプライヤはSOTIF-EooCとして「使われ方の前提と機能不足の許容発生率」を仮定として差し出す。
本パイプラインの出力(母集団参照の応答兆候の発生率)は、その<b>仮定発生率が市場で守られているかを検証する部品側の観測</b>にそのまま対応する。
上のpayload内 <code>sotif_mapping</code> がその変換である。</p>

<h2>限界(このデモが誠実であるための明記)</h2>
<p class='note boundary'>
1. 健全fleetのlogであり、検出された兆候は路面・運転者・積載・センサ状態の混合である。部品状態との切り分けは、EPS内部信号(電圧・温度・アシスト状態)との同時観測が要る——それがEPS内部実装(docs/122 payload)の役割。<br>
2. 車両モデル(操舵角→横加速度)の誤差は速度・路面勾配に依存する。roll補正は簡略化している。<br>
3. セグメント間で車両個体が区別できないため、再発(同一個体での繰り返し)は追えない。<br>
4. z閾値{Z_FLAG:.0f}は運用値ではなくデモ値。運用閾値の設定には結果ラベル(整備記録等)が要る。
</p>
<p class='note'>データ: <a href='https://huggingface.co/datasets/commaai/commaSteeringControl'>commaSteeringControl</a>(comma.ai、MIT license)。
再現: <code>python3 scripts/steering_log_sign_extraction.py</code>(platform zipを .public_log_cache/ に展開して実行)。</p>
</div>
"""


def main() -> None:
    table, extra = compute()
    flagged = extra["flagged"]
    print(f"segments analyzed: {len(table)}, flagged (|z|>={Z_FLAG}): {len(flagged)}")
    print(flagged[["top_feature", "max_abs_z", "v_mean"]].head(10).to_string())
    cols = FEATURES + [f"z_{f}" for f in FEATURES] + ["max_abs_z", "top_feature", "n_valid", "v_mean"]
    table[cols].round(5).to_csv(OUT_TSV, sep="\t")
    OUT_HTML.write_text(render_html(table, flagged), encoding="utf-8")
    print(f"wrote {OUT_TSV.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_HTML.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
