#!/usr/bin/env python3
"""SOTIF-EooC operational-phase monitoring demo (docs/158).

Wires three existing pieces into one runnable flow, which is what AGENTS.md
rule 4 asks a demo to show:

  1. DECLARE   the EooC assumption a component supplier offers (docs/153),
               using the per-feature design verified in docs/155
  2. CALIBRATE the population reference on this program (docs/147: the
               method transfers, the thresholds do not -- this step is the
               per-program NRE)
  3. OBSERVE   stream field logs through it and count how often the fleet
               leaves the declared envelope
  4. REPORT    emit the component-side payload (docs/121) for a deviating
               unit, with the boundary of what must not be claimed

The point of the demo is as much what it CANNOT fill as what it can. The
acceptable-rate target (EOOC011) is left blank on purpose: it is allocated
from the vehicle-level safety goal and belongs to the OEM. The demo shows
the OBSERVED rate next to that blank, which is exactly the interface.

Data: commaSteeringControl (comma.ai, MIT). Healthy vehicles only. Nothing
here detects real failures or predicts them -- see docs/158 limitations.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import steering_window_recurrence as swr  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
PLATFORM = sys.argv[1] if len(sys.argv) > 1 else "FORD_MAVERICK_1ST_GEN"
OUT_HTML = REPO_ROOT / "generated" / "sotif_eooc_monitor_demo.html"
OUT_TSV = REPO_ROOT / "data" / "sotif_eooc_monitor_demo.tsv"

# The declared design, from docs/155. Feature -> (window seconds, k, N)
DESIGN = {
    "lag":      (15.0, 2, 4),
    "gain_dev": (60.0, 1, 1),
    "bias":     (15.0, 3, 4),
}
DECLARED_LIMIT = {"lag": "0.3 s", "gain_dev": "0.10", "bias": "0.10 m/s²"}
JA = {"lag": "応答遅れ", "gain_dev": "ゲイン(効き)変化", "bias": "応答バイアス"}
NOT_DECLARED = ["asymmetry", "drift", "hf_noise"]
Z = swr.Z_FLAG


def main() -> None:
    data_dir = REPO_ROOT / ".public_log_cache" / PLATFORM
    segs = []
    for csv in sorted(data_dir.glob("*.csv")):
        s = swr.load_segment(csv)
        if s:
            segs.append((csv.stem, s))
    print(f"fleet: {len(segs)} gated 60 s records from {PLATFORM}")

    # ---- 2. CALIBRATE (per-program; this is the NRE step) ----------------
    # One reference per window length, because feature scale depends on it.
    ref = {}
    for win in {w for w, _, _ in DESIGN.values()}:
        vals = {f: [] for f in swr.FEATURES}
        for _, s in segs:
            for w in swr.split(s, win):
                if not w:
                    continue
                fe = swr.features(w)
                for f in swr.FEATURES:
                    vals[f].append(fe[f])
        ref[win] = {f: swr.robust_stats(vals[f]) for f in swr.FEATURES}
        print(f"calibrated reference for {win:.0f}s windows")

    # ---- 3. OBSERVE -------------------------------------------------------
    # A unit leaves the envelope when a declared feature fires under its own
    # k-of-N rule. Features are judged separately: that is the docs/155 result.
    per_feature = {f: 0 for f in DESIGN}
    deviating, evaluated = [], 0
    for name, s in segs:
        fired = {}
        usable = True
        for feat, (win, k, n) in DESIGN.items():
            wins = swr.split(s, win)
            if any(w is None for w in wins):
                usable = False
                break
            hits = 0
            for w in wins:
                fe = swr.features(w)
                v = fe[feat]
                if v is None or (isinstance(v, float) and np.isnan(v)):
                    continue
                med, sc = ref[win][feat]
                if abs((v - med) / sc) >= Z:
                    hits += 1
            fired[feat] = (hits >= k, hits, n)
        if not usable:
            continue
        evaluated += 1
        for feat, (hit, _, _) in fired.items():
            if hit:
                per_feature[feat] += 1
        if any(h for h, _, _ in fired.values()):
            deviating.append((name, fired))

    rate = len(deviating) / evaluated if evaluated else 0.0
    print(f"evaluated {evaluated} units; outside declared envelope: {len(deviating)} ({rate:.2%})")
    for f, c in per_feature.items():
        print(f"  {f:<10} {c:>5} ({c/evaluated:.2%})")

    # ---- 4. REPORT --------------------------------------------------------
    example = deviating[0] if deviating else None

    with OUT_TSV.open("w") as fh:
        fh.write("field\tvalue\n")
        fh.write(f"platform\t{PLATFORM}\n")
        fh.write(f"units_evaluated\t{evaluated}\n")
        fh.write(f"units_outside_envelope\t{len(deviating)}\n")
        fh.write(f"observed_rate\t{rate:.5f}\n")
        for f, c in per_feature.items():
            fh.write(f"rate_{f}\t{c/evaluated:.5f}\n")
        fh.write("acceptable_rate_target\tBLANK_OEM_TO_FILL\n")

    rows = "\n".join(
        f"<tr><td>{JA[f]}</td><td class='num'>{w:.0f} s</td><td class='num'>{k}/{n}</td>"
        f"<td class='num'>{DECLARED_LIMIT[f]}</td><td class='num'>{per_feature[f]/evaluated:.2%}</td></tr>"
        for f, (w, k, n) in DESIGN.items())
    ex_html = ""
    if example:
        nm, fired = example
        hit_names = "、".join(JA[f] for f, (h, _, _) in fired.items() if h)
        detail = "、".join(f"{JA[f]} {h}/{n}窓" for f, (_, h, n) in fired.items())
        ex_html = f"""
<pre class="payload">component        : steering / EPS
observed_context : 宣言した観測範囲の外れ({html.escape(hit_names)})
event_relation   : assist制限の確定fault未満。機能影響の有無は本payloadでは断定しない
severity_language: context observed / below hard fault threshold
recurrence       : {html.escape(detail)}
confidence       : medium(宣言済みの設計則と較正済み母集団に基づく)
recommended_read : EPS DTC status / reset context / supply voltage context / assist mode / recurrence
boundary         : not a root cause, not a failure prediction, not a replacement timing,
                   not a safety guarantee, not a SOTIF conformity claim
unit             : {html.escape(nm)}</pre>"""

    OUT_HTML.write_text(f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>SOTIF-EooC 運用フェーズ監視デモ</title>
<style>
:root{{--bg:#fbfbfa;--ink:#1a1a19;--ink2:#5a5a55;--line:#e3e3df;--card:#fff;--accent:#0b5;--warn:#b45}}
@media(prefers-color-scheme:dark){{:root{{--bg:#191918;--ink:#eeeeec;--ink2:#a0a09a;--line:#33332f;--card:#222220}}}}
*{{box-sizing:border-box}} body{{margin:0;padding:32px 20px;background:var(--bg);color:var(--ink);
font:15px/1.7 -apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif}}
main{{max-width:860px;margin:0 auto}} h1{{font-size:24px;margin:0 0 4px}} h2{{font-size:17px;margin:32px 0 10px}}
.sub{{color:var(--ink2);margin:0 0 24px}}
.step{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:14px 0}}
.n{{display:inline-block;width:22px;height:22px;line-height:22px;text-align:center;border-radius:50%;
background:var(--ink);color:var(--bg);font-size:12px;font-weight:700;margin-right:8px}}
table{{width:100%;border-collapse:collapse;margin:10px 0;font-size:14px}}
th,td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left}}
th{{color:var(--ink2);font-weight:600}} td.num{{text-align:right;font-variant-numeric:tabular-nums}}
.blank{{background:rgba(180,85,85,.10);border:1px dashed var(--warn);border-radius:8px;padding:14px 16px;margin:12px 0}}
.blank b{{color:var(--warn)}}
pre.payload{{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:14px;
overflow-x:auto;font-size:13px;line-height:1.6}}
.note{{color:var(--ink2);font-size:13px}} ul{{padding-left:20px}} li{{margin:4px 0}}
</style></head><body><main>
<h1>SOTIF-EooC 運用フェーズ監視デモ</h1>
<p class="sub">部品サプライヤが差し出す仮定を宣言し、公開走行logを流して、仮定の範囲内かを判定する。
対象 {html.escape(PLATFORM)}、{evaluated:,} 台分(60秒記録)。</p>

<div class="step"><span class="n">1</span><b>宣言</b>— EooCで差し出す仮定
<table><thead><tr><th>機能不足</th><th>窓長</th><th>判定則</th><th>90%検出下限</th><th>観測された逸脱率</th></tr></thead>
<tbody>{rows}</tbody></table>
<p class="note">設計則は<b>車種不変</b>(4車種で優劣が一致、docs/155)。下限値は<b>program固有</b>で較正が要る(docs/147)。
左右非対称・drift・hf_noiseは<b>宣言しない</b>——この方式では90%検出に届かないため。</p></div>

<div class="step"><span class="n">2</span><b>較正</b>— この program の母集団基準を取る
<p class="note">窓長ごとに中央値とMADを取り直す。手法は移るが閾値は移らないため、この工程が車種ごとに必要になる。
これが診断コンテンツNREの実体である。</p></div>

<div class="step"><span class="n">3</span><b>観測</b>— 宣言した範囲を出た台数
<p style="font-size:22px;margin:6px 0"><b>{rate:.2%}</b>
<span class="note">（{len(deviating):,} / {evaluated:,} 台）</span></p></div>

<div class="blank"><b>ここはOEMが埋める欄（EOOC011）</b><br>
機能不足の<b>許容発生率の目標値</b>は、車両レベルの安全目標からの配分であり、部品側では決められない。
公開情報では原理的に届かない。<br>
部品側が差し出せるのは<b>観測された {rate:.2%} という実測値</b>までで、
これが目標以下かを判定するのはOEMの領域である。<b>この空欄そのものが責任境界の記録</b>である。</div>

<div class="step"><span class="n">4</span><b>報告</b>— 逸脱した1台に対する部品側payload{ex_html}</div>

<h2>このデモが言っていないこと</h2>
<ul>
<li>故障を検出した / 予測した — <b>言っていない</b>。走行logは健全車両のもので、実故障の波形は公開されていない</li>
<li>逸脱した台が異常である — <b>言っていない</b>。母集団基準からの統計的な外れであり、路面・積載・運転操作でも起きる</li>
<li>SOTIF適合を証明した / 安全を保証した — <b>言っていない</b>。適合判断の主語はOEMである</li>
<li>この逸脱率が妥当である — <b>言っていない</b>。妥当性の基準(許容発生率)は上の空欄のままである</li>
</ul>
<p class="note">データ: <a href="https://huggingface.co/datasets/commaai/commaSteeringControl">commaSteeringControl</a>(comma.ai、MIT)。
再現: <code>python3 scripts/sotif_eooc_monitor_demo.py</code>。詳細は docs/158。</p>
</main></body></html>""", encoding="utf-8")
    print(f"wrote {OUT_HTML.relative_to(REPO_ROOT)} / {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
