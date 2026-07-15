#!/usr/bin/env python3
"""Model B: quantify the log-sign pipeline's detection limits by synthetic
degradation injection (docs/144).

Public driving logs contain no failures, so field validation of the waveform
pipeline is impossible publicly. The standard alternative: inject KNOWN
response changes into healthy segments and measure what magnitude the
population-referenced features detect. Output is a sensitivity curve per
degradation type — "a change of X is detected with probability Y at the
z>=4 operating point whose clean false-positive rate is measured".

Injection model (applied to the measured series, preserving real noise):
    residual r(t) = actual - implied   (real, kept as-is)
    lag L      : actual' = r + implied(t - L)
    gain g     : actual' = r + (1+g) * implied
    bias b     : actual' = actual + b
    asymmetry a: actual' = actual + a/2 (angle>+2deg), -a/2 (angle<-2deg)

NOT a claim about real failures: synthetic changes are idealized; real
degradations differ. This bounds the pipeline's sensitivity, nothing more.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
PLATFORM = sys.argv[1] if len(sys.argv) > 1 else "FORD_MAVERICK_1ST_GEN"
_SUFFIX = "" if PLATFORM == "FORD_MAVERICK_1ST_GEN" else "_" + PLATFORM.lower().replace("-", "_")
DATA_DIR = REPO_ROOT / ".public_log_cache" / PLATFORM
OUT_HTML = REPO_ROOT / "generated" / f"steering_synthetic_sensitivity{_SUFFIX}.html"
OUT_TSV = REPO_ROOT / "data" / f"steering_synthetic_sensitivity{_SUFFIX}.tsv"

MIN_SPEED, MIN_VALID, ANGLE_SPLIT = 5.0, 300, 2.0
ANGLE_DOMAIN, DOMAIN_FRACTION, JUMP_MAX, EXCITATION_MIN = 45.0, 0.10, 2.0, 0.15
Z_FLAG, DT = 4.0, 0.1
FEATURES = ["bias", "drift", "asymmetry", "lag", "gain_dev", "hf_noise"]

INJECTIONS = {
    "lag_s": [0.1, 0.2, 0.3, 0.4, 0.5],
    "gain": [0.02, 0.05, 0.10, 0.15, 0.20],
    "bias_ms2": [0.05, 0.10, 0.20, 0.30],
    "asym_ms2": [0.05, 0.10, 0.20, 0.30],
}
INJ_JA = {"lag_s": "応答遅れ [s]", "gain": "ゲイン変化 [-]", "bias_ms2": "応答バイアス [m/s²]", "asym_ms2": "左右非対称 [m/s²]"}


def load_segment(csv: Path):
    df = pd.read_csv(csv, usecols=["vEgo", "steeringAngleDeg", "t", "latAccelSteeringAngle", "latAccelLocalizer"])
    m = (df["vEgo"] > MIN_SPEED) & df["latAccelLocalizer"].notna() & df["latAccelSteeringAngle"].notna()
    d = df[m]
    if len(d) < MIN_VALID:
        return None
    angle = d["steeringAngleDeg"].to_numpy()
    if float(np.mean(np.abs(angle) > ANGLE_DOMAIN)) > DOMAIN_FRACTION:
        return None
    keep = np.abs(angle) <= ANGLE_DOMAIN
    d = d[keep]
    if len(d) < MIN_VALID:
        return None
    implied = d["latAccelSteeringAngle"].to_numpy()
    actual = d["latAccelLocalizer"].to_numpy()
    if np.max(np.abs(np.diff(actual - implied))) > JUMP_MAX:
        return None
    return {"t": d["t"].to_numpy(), "angle": d["steeringAngleDeg"].to_numpy(),
            "implied": implied, "actual": actual}


def features(seg) -> dict | None:
    implied, actual, angle, t = seg["implied"], seg["actual"], seg["angle"], seg["t"]
    r = actual - implied
    excitation = float(np.std(implied))
    bias = float(np.mean(r))
    drift = float(np.polyfit(t, r, 1)[0]) if len(np.unique(t)) > 2 else 0.0
    left, right = r[angle > ANGLE_SPLIT], r[angle < -ANGLE_SPLIT]
    asym = float(np.mean(left) - np.mean(right)) if (len(left) >= 20 and len(right) >= 20 and excitation >= EXCITATION_MIN) else np.nan
    if excitation >= EXCITATION_MIN:
        a = implied - implied.mean(); b = actual - actual.mean()
        best_s, best_c = 0, -np.inf
        for s in range(-5, 6):
            c = np.dot(a[: len(a) - s], b[s:]) if s >= 0 else np.dot(a[-s:], b[: len(b) + s])
            if c > best_c:
                best_c, best_s = c, s
        lag = best_s * DT
        gain_dev = float(np.dot(a, b) / np.dot(a, a)) - 1.0
    else:
        lag, gain_dev = np.nan, np.nan
    return {"bias": bias, "drift": drift, "asymmetry": asym, "lag": lag,
            "gain_dev": gain_dev, "hf_noise": float(np.std(np.diff(r))), "excitation": excitation}


def inject(seg, kind: str, mag: float):
    implied, actual, angle = seg["implied"], seg["actual"], seg["angle"]
    r = actual - implied
    if kind == "lag_s":
        k = int(round(mag / DT))
        shifted = np.concatenate([np.repeat(implied[0], k), implied[:-k]]) if k > 0 else implied
        actual2 = r + shifted
    elif kind == "gain":
        actual2 = r + (1 + mag) * implied
    elif kind == "bias_ms2":
        actual2 = actual + mag
    elif kind == "asym_ms2":
        off = np.where(angle > ANGLE_SPLIT, mag / 2, np.where(angle < -ANGLE_SPLIT, -mag / 2, 0.0))
        actual2 = actual + off
    else:
        raise ValueError(kind)
    return {**seg, "actual": actual2}


def robust_stats(vals):
    v = np.array(vals, dtype=float)
    med = np.nanmedian(v)
    mad = np.nanmedian(np.abs(v - med))
    scale = 1.4826 * mad if mad > 1e-12 else np.nanstd(v)
    return med, (scale if scale > 1e-12 else 1.0)


def max_z(f, stats):
    zs = []
    for name in FEATURES:
        v = f[name]
        if v is None or (isinstance(v, float) and math.isnan(v)):
            continue
        med, sc = stats[name]
        zs.append(abs((v - med) / sc))
    return max(zs) if zs else 0.0


def main() -> None:
    segs = []
    for csv in sorted(DATA_DIR.glob("*.csv")):
        s = load_segment(csv)
        if s:
            segs.append((csv.stem, s))
    print(f"gated clean segments: {len(segs)}")
    feats = {name: features(s) for name, s in segs}
    stats = {f: robust_stats([feats[n][f] for n, _ in segs]) for f in FEATURES}
    clean_flag = {n: max_z(feats[n], stats) >= Z_FLAG for n, _ in segs}
    fpr = float(np.mean(list(clean_flag.values())))
    healthy = [(n, s) for n, s in segs if not clean_flag[n]]
    print(f"clean flag rate at z>={Z_FLAG:.0f} (operating point FPR): {fpr:.1%}; healthy for injection: {len(healthy)}")

    rows = []
    for kind, mags in INJECTIONS.items():
        for mag in mags:
            det = 0; usable = 0
            for name, s in healthy:
                f2 = features(inject(s, kind, mag))
                if kind in ("lag_s", "gain") and (f2["gain_dev"] is None or math.isnan(f2["gain_dev"])):
                    continue  # insufficient excitation for this injection's target feature
                usable += 1
                if max_z(f2, stats) >= Z_FLAG:
                    det += 1
            rate = det / usable if usable else float("nan")
            rows.append({"kind": kind, "mag": mag, "detected": det, "usable": usable, "rate": rate})
            print(f"{kind:>9} {mag:>5}: detection {rate:.1%} ({det}/{usable})")

    with open(OUT_TSV, "w") as out:
        out.write("kind\tmagnitude\tdetected\tusable\tdetection_rate\tclean_fpr\n")
        for r in rows:
            out.write(f"{r['kind']}\t{r['mag']}\t{r['detected']}\t{r['usable']}\t{r['rate']:.4f}\t{fpr:.4f}\n")

    # detection limits: smallest magnitude with rate >= 50% / 90%
    limits = {}
    for kind, mags in INJECTIONS.items():
        rs = [r for r in rows if r["kind"] == kind]
        l50 = next((r["mag"] for r in rs if r["rate"] >= 0.5), None)
        l90 = next((r["mag"] for r in rs if r["rate"] >= 0.9), None)
        limits[kind] = (l50, l90)

    def curves_svg(width=640, height=340):
        pl, pr_, pt, pb = 52, 140, 16, 44
        pw, ph = width - pl - pr_, height - pt - pb
        colors = ["s0", "s1", "s2", "s3"]
        s = [f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='合成劣化量に対する検出率'>"]
        for g in (0.25, 0.5, 0.75, 1.0):
            s.append(f"<line x1='{pl}' y1='{pt+ph*(1-g):.1f}' x2='{pl+pw}' y2='{pt+ph*(1-g):.1f}' class='grid'/>")
            s.append(f"<text x='{pl-8}' y='{pt+ph*(1-g)+4:.1f}' class='tick' text-anchor='end'>{g:.0%}</text>")
        s.append(f"<line x1='{pl}' y1='{pt+ph}' x2='{pl+pw}' y2='{pt+ph}' class='axis'/>")
        s.append(f"<line x1='{pl}' y1='{pt+ph*(1-fpr):.1f}' x2='{pl+pw}' y2='{pt+ph*(1-fpr):.1f}' class='marker'/>")
        s.append(f"<text x='{pl+4}' y='{pt+ph*(1-fpr)-6:.1f}' class='mlabel'>健全時の誤検出率 {fpr:.0%}</text>")
        for ci, (kind, mags) in enumerate(INJECTIONS.items()):
            rs = [r for r in rows if r["kind"] == kind]
            xs = lambda i: pl + pw * i / (len(mags) - 1)
            pts = " ".join(f"{xs(i):.1f},{pt+ph*(1-r['rate']):.1f}" for i, r in enumerate(rs))
            s.append(f"<polyline points='{pts}' fill='none' class='{colors[ci]}' stroke-width='2'/>")
            for i, r in enumerate(rs):
                s.append(f"<circle cx='{xs(i):.1f}' cy='{pt+ph*(1-r['rate']):.1f}' r='4' class='{colors[ci]}f'/>")
            s.append(f"<text x='{pl+pw+8}' y='{pt+ph*(1-rs[-1]['rate'])+4:.1f}' class='dlabel {colors[ci]}t'>{INJ_JA[kind]}</text>")
        for i, frac in enumerate(np.linspace(0, 1, 5)):
            s.append(f"<text x='{pl+pw*frac:.1f}' y='{pt+ph+18}' class='tick' text-anchor='middle'>{'小' if i==0 else ('大' if i==4 else '')}</text>")
        s.append(f"<text x='{pl+pw/2:.0f}' y='{height-6}' class='tick' text-anchor='middle'>注入量(各系列の試験点は等間隔表示。実値は表を参照)</text>")
        s.append("</svg>")
        return "\n".join(s)

    mag_rows = "\n".join(
        f"<tr><td>{INJ_JA[k]}</td><td class='num'>{' / '.join(str(m) for m in INJECTIONS[k])}</td>"
        f"<td class='num'>{limits[k][0] if limits[k][0] is not None else '未達'}</td>"
        f"<td class='num'>{limits[k][1] if limits[k][1] is not None else '未達'}</td></tr>"
        for k in INJECTIONS
    )
    detail_rows = "\n".join(
        f"<tr><td>{INJ_JA[r['kind']]}</td><td class='num'>{r['mag']}</td><td class='num'>{r['rate']:.0%}</td><td class='num'>{r['detected']}/{r['usable']}</td></tr>"
        for r in rows
    )
    html = f"""<meta charset='utf-8'>
<title>波形パイプラインの検出限界(合成劣化注入)</title>
<style>
:root {{ color-scheme: light dark; }}
.viz-root {{ --surface-1:#fcfcfb; --page:#f9f9f7; --ink-1:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --s0:#2a78d6; --s1:#1baf7a; --s2:#eda100; --s3:#4a3aa7; }}
@media (prefers-color-scheme: dark) {{
  .viz-root {{ --surface-1:#1a1a19; --page:#0d0d0d; --ink-1:#ffffff; --ink-2:#c3c2b7;
    --grid:#2c2c2a; --axis:#383835; --s0:#3987e5; --s1:#199e70; --s2:#c98500; --s3:#9085e9; }} }}
.viz-root {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: var(--page);
  color: var(--ink-1); margin: 0 auto; max-width: 62rem; padding: 2rem 1.5rem; line-height: 1.7; }}
h1 {{ font-size: 1.3rem; }} h2 {{ font-size: 1.1rem; margin-top: 2.2rem; border-bottom: 2px solid var(--grid); padding-bottom: .3rem; }}
.card {{ background: var(--surface-1); color: var(--ink-1); border: 1px solid var(--grid); border-radius: 8px; padding: 1rem 1.2rem; margin: 1rem 0; }}
.note {{ font-size: .88rem; color: var(--ink-2); }} .lede {{ font-size: .95rem; }}
svg {{ width: 100%; height: auto; display: block; }}
.grid {{ stroke: var(--grid); }} .axis {{ stroke: var(--axis); }} .tick {{ fill: var(--muted); font-size: 11px; }}
.dlabel {{ font-size: 12px; font-weight: 600; }}
.s0 {{ stroke: var(--s0); }} .s1 {{ stroke: var(--s1); }} .s2 {{ stroke: var(--s2); }} .s3 {{ stroke: var(--s3); }}
.s0f {{ fill: var(--s0); }} .s1f {{ fill: var(--s1); }} .s2f {{ fill: var(--s2); }} .s3f {{ fill: var(--s3); }}
.s0t {{ fill: var(--s0); }} .s1t {{ fill: var(--s1); }} .s2t {{ fill: var(--s2); }} .s3t {{ fill: var(--s3); }}
.marker {{ stroke: var(--muted); stroke-width: 1; stroke-dasharray: 4 3; }} .mlabel {{ fill: var(--ink-2); font-size: 11px; }}
table {{ border-collapse: collapse; width: 100%; background: var(--surface-1); color: var(--ink-1); font-size: .9rem; }}
th, td {{ border: 1px solid var(--grid); padding: .45rem .7rem; text-align: left; color: var(--ink-1); }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; }} th {{ color: var(--ink-2); font-weight: 600; }}
.boundary {{ border-left: 3px solid var(--axis); padding-left: .8rem; }}
</style>
<div class='viz-root'>
<h1>波形パイプラインの検出限界 — 合成劣化注入による定量化</h1>
<h2>1. これは何の実証か</h2>
<p class='lede'>docs/139の兆候抽出パイプラインが「どの大きさの応答変化なら検出できるのか」を数字にする。
公開logに故障車は存在しないため、健全セグメントに<b>既知量の応答変化を合成注入</b>し、
母集団参照の特徴量(z≥{Z_FLAG:.0f}、健全時誤検出率{fpr:.0%})が何%を検出するかを測る。</p>
<h2>2. 結果: 検出率曲線</h2>
<div class='card'>{curves_svg()}</div>
<h2>3. 検出限界(50% / 90%検出に必要な最小注入量)</h2>
<table><tr><th>劣化タイプ</th><th>試験した注入量</th><th>50%検出</th><th>90%検出</th></tr>{mag_rows}</table>
<h2>4. 全数値</h2>
<table><tr><th>タイプ</th><th>注入量</th><th>検出率</th><th>検出/対象</th></tr>{detail_rows}</table>
<h2>5. 限界(誠実性のための明記)</h2>
<p class='note boundary'>合成劣化は理想化された変化であり、実故障の波形とは異なる(実故障の公開波形は存在しない——この検証の存在理由そのもの)。
数字は「この理想化条件下でのパイプライン感度の上限側の目安」であり、実車性能の保証ではない。
1 platform({DATA_DIR.name})・60秒セグメント単位・z閾値はデモ値。実運用は結果ラベルとの突き合わせが必要。</p>
<p class='note'>再現: <code>python3 scripts/steering_synthetic_sensitivity.py</code>。データ: commaSteeringControl (MIT)。</p>
</div>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"wrote {OUT_TSV.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_HTML.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
