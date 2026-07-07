#!/usr/bin/env python3
"""Replay documented public EPS cases through the SPD008 minimum payload.

This demo intentionally uses only facts stated in public NHTSA-hosted
documents (recall dealer bulletins / TSBs / SSMs). For each case it shows:

1. what the field practice actually had to work with (per the public document),
2. the component-side state explanation (docs/122 minimum payload) that SPD008
   proposes the EPS could have emitted at runtime,
3. a boundary guard that mechanically REJECTS prohibited claims
   (root cause decisions, replacement timing, no-fault claims, RUL, safety
   guarantees) so the payload cannot drift into forbidden territory.

The payload is a state explanation, not a diagnosis. Nothing here predicts
failure, decides root cause, or judges any OEM's design.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_HTML = REPO_ROOT / "generated" / "spd008_payload_replay.html"
OUT_TSV = REPO_ROOT / "data" / "spd008_payload_replay_cases.tsv"

# ---------------------------------------------------------------------------
# Boundary guard: prohibited claim patterns (docs/122 "boundary" row).
# The guard scans every text field of a candidate payload. If any pattern
# matches, the payload is rejected instead of emitted.
# ---------------------------------------------------------------------------
PROHIBITED_PATTERNS: list[tuple[str, str]] = [
    (r"root\s+cause", "root cause decision"),
    (r"\breplace\b|\breplacement\s+needed\b|交換(して|すべき|時期)", "replacement decision / timing"),
    (r"is\s+(defective|faulty)|故障してい(る|ます)", "component fault verdict"),
    (r"not\s+at\s+fault|no\s+fault\s+of|無罪|問題(あり|ない)と断定", "no-fault (innocence) claim"),
    (r"remaining\s+useful\s+life|\bRUL\b|残寿命", "remaining-useful-life claim"),
    (r"safety\s+is\s+guaranteed|安全を保証", "safety guarantee"),
    (r"warranty\s+cost|保証費", "warranty cost claim"),
    (r"will\s+fail|故障する(だろう|はず)|故障予測", "failure prediction"),
    (r"caused\s+by\s+the\s+(battery|alternator|ECM|external)|原因は.+(バッテリー|電源|外部)", "external root cause decision"),
]


def check_boundary(text: str) -> list[str]:
    """Return the list of prohibited-claim labels found in *text*."""
    hits = []
    for pattern, label in PROHIBITED_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            hits.append(label)
    return hits


# ---------------------------------------------------------------------------
# Case definitions. Every "public_fact" and "actual_practice" line is stated
# in the cited public document. The payload fields follow docs/122.
# ---------------------------------------------------------------------------
@dataclass
class ReplayCase:
    case_id: str
    title: str
    sample: str  # power monitor / communication input validity
    source: str
    source_url: str
    public_fact: str
    actual_practice: str
    payload: dict = field(default_factory=dict)
    state_text_en: str = ""
    state_text_ja: str = ""
    naive_claim: str = ""  # what a careless implementation would say (must be rejected)


CASES: list[ReplayCase] = [
    ReplayCase(
        case_id="gm_17na158",
        title="GM TSB 17-NA-158: 無効な冷却水温signalによるSteering Assist Reduced",
        sample="communication input validity",
        source="GM Service Bulletin 17-NA-158 (May 2017)",
        source_url="https://static.nhtsa.gov/odi/tsbs/2017/MC-10137654-9999.pdf",
        public_fact=(
            "ECMからの冷却水温signalがCAN上で無効になり、EPSの低温グリス硬化補償が停止。"
            "走行約20分後にSteering Assist Reduced表示。DTCはP0128(ECM)とU0401(steering gear)。"
        ),
        actual_practice=(
            "U0401がsteering gearに保存されたため、gearが犯人に見えた。"
            "OEMが『U0401:71でgearを交換するな』『交換しても直らない』とTSBで警告するまで、"
            "直らないgear交換が繰り返された。依存signalと機能影響の関係は、人手のTSBが出て初めて説明された。"
        ),
        payload={
            "component": "steering / EPS",
            "observed_context": "dependency signal invalid: engine coolant temperature received via CAN observed invalid by EPS",
            "relation_to_function": "cold-grease compensation inactive; reduced-assist warning displayed",
            "monitor_status": "dependency-invalid code recorded on steering side; no steering internal fault confirmed",
            "recurrence": "recurs each drive cycle after approx. 20 minutes",
            "retained_fields": "dependency signal name, validity status, compensation state, warning state, key cycle",
            "confidence": "medium",
            "recommended_read": "read the dependency source module status first (engine coolant temperature signal), then steering communication DTC status",
            "boundary": "not an external ECU root-cause decision; not a steering gear service decision; component-side dependency observation only",
        },
        state_text_en=(
            "Steering function reduced its assist compensation while the EPS observed an invalid "
            "engine-coolant-temperature dependency signal. This is a steering-side dependency observation, "
            "not an external ECU root-cause decision and not a steering-gear service decision."
        ),
        state_text_ja=(
            "EPSが受信する冷却水温の依存signalが無効になっている間、操舵側の補償機能が停止した。"
            "これは操舵側から見た依存関係の状態説明であり、外部ECUの原因断定でも、steering gearの整備判断でもない。"
        ),
        naive_claim="Root cause is the ECM coolant signal. The steering gear is not at fault. Replace the thermostat.",
    ),
    ReplayCase(
        case_id="ford_ssm49530",
        title="Ford SSM 49530: 始動時電圧8V未満によるassist喪失(2021年F-150)",
        sample="power monitor",
        source="Ford SSM 49530 (2021)",
        source_url="https://static.nhtsa.gov/odi/tsbs/2021/MC-10187919-0001.pdf",
        public_fact=(
            "始動時にバッテリー電圧が8V未満へ低下し、assist喪失とSteering Assist Fault表示。"
            "PSCMには内部故障系のU3000:96とU3001:68が保存された。電圧12V以上+専用リセットで復帰。"
        ),
        actual_practice=(
            "保存されたcodeは部品内部故障(component internal failure)に見えるため、PSCM交換に向かいやすい。"
            "OEMは人手のSSMで『PSCM交換は不要、原因は始動時の低電圧』と説明する必要があった。"
            "通常のDTC消去では消えず、専用リセット手順も人手の文書で伝えられた。"
        ),
        payload={
            "component": "steering / EPS",
            "observed_context": "short supply-voltage drop below cranking threshold observed by EPS at engine start",
            "relation_to_function": "assist unavailable at start-up; steering fault message displayed",
            "monitor_status": "internal-failure-class codes set during the low-voltage window; power context recorded alongside",
            "recurrence": "same key cycle (start-up event)",
            "retained_fields": "supply voltage min, event phase (cranking), assist availability, code set context, key cycle",
            "confidence": "medium",
            "recommended_read": "read EPS supply-voltage context for the code-set moment first, then vehicle power/charging state, before module internals",
            "boundary": "not a module service decision; not a battery root-cause decision; power-context observation only",
        },
        state_text_en=(
            "Steering assist was unavailable at start-up while the EPS observed supply voltage below its "
            "operating threshold during cranking. This is a steering-side power-context observation, below or "
            "outside hard-fault confirmation, and is not a module or battery service decision."
        ),
        state_text_ja=(
            "始動時、EPSが動作しきい値未満の供給電圧を観測している間、アシストが使用不能だった。"
            "これは操舵側から見たpower contextの状態説明であり、モジュールやバッテリーの整備判断ではない。"
        ),
        naive_claim="The battery is faulty and caused this. PSCM replacement is not needed because the EPS is not at fault.",
    ),
    ReplayCase(
        case_id="ford_15s18",
        title="Ford 15S18: DTCなしの断続的assist喪失(EPASリコール)",
        sample="power monitor (below-DTC recurrence)",
        source="Ford Safety Recall 15S18 dealer letter (July 2015)",
        source_url="https://static.nhtsa.gov/odi/rcl/2015/RCMN-15V340-8835.pdf",
        public_fact=(
            "断続的な電気接続不良によりmotor position sensor signalが失われ得る。"
            "是正はDTC有無で分岐: DTCあり=gear交換(1.6-2.4h+部品)、DTCなし=再プログラムのみ(0.2h)。"
            "assist喪失を訴えてもDTCがなければ延長保証の対象外とし『通常診断へ進め』。"
        ),
        actual_practice=(
            "判断材料は『loss of steering assist系DTCの有無』という1bitだけ。"
            "event時にDTCが残らなかった車両は、症状があっても対象外に落ち、"
            "断続的eventの再発頻度という判断材料は実務に存在しなかった。"
        ),
        payload={
            "component": "steering / EPS",
            "observed_context": "intermittent internal-signal transient below fault maturation observed by EPS",
            "relation_to_function": "momentary assist interruption near the transient",
            "monitor_status": "below hard-fault threshold; no permanent loss-of-assist DTC stored",
            "recurrence": "recurrence count retained across key cycles",
            "retained_fields": "transient class, assist state, recurrence count, key cycle span, DTC status",
            "confidence": "low-medium (depends on retained fields)",
            "recommended_read": "read below-threshold recurrence count together with DTC status, so the service split has a second evidence source beyond DTC presence",
            "boundary": "not a service split decision; not a component fault verdict; recurrence-context observation only",
        },
        state_text_en=(
            "The EPS observed repeated internal-signal transients below fault-maturation threshold, near momentary "
            "assist interruptions, recurring across key cycles. This is a steering-side recurrence observation and "
            "is not a component fault verdict or a service decision."
        ),
        state_text_ja=(
            "EPSは、故障確定に至らない内部signalの過渡的な乱れが、瞬間的なアシスト途切れの近傍で、"
            "key cycleをまたいで繰り返されたことを観測した。これは操舵側から見た再発の状態説明であり、"
            "部品の故障判定でも整備判断でもない。"
        ),
        naive_claim="This gear will fail soon. Replace the steering gear now to avoid warranty cost.",
    ),
]


def build_rows(cases: list[ReplayCase]) -> list[dict]:
    rows = []
    for case in cases:
        payload_text = " ".join(str(v) for v in case.payload.values())
        payload_hits = check_boundary(payload_text + " " + case.state_text_en + " " + case.state_text_ja)
        naive_hits = check_boundary(case.naive_claim)
        rows.append(
            {
                "case": case,
                "payload_ok": not payload_hits,
                "payload_hits": payload_hits,
                "naive_rejected": bool(naive_hits),
                "naive_hits": naive_hits,
            }
        )
    return rows


def render_html(rows: list[dict]) -> str:
    def esc(text: str) -> str:
        return html.escape(text, quote=False)

    parts = [
        "<meta charset='utf-8'>",
        "<title>SPD008 Payload Replay (public cases)</title>",
        "<style>",
        "body{font-family:'Hiragino Sans','Noto Sans JP',sans-serif;margin:2rem auto;max-width:60rem;line-height:1.7;color:#1a1a1a;background:#fafafa}",
        "h1{font-size:1.5rem} h2{font-size:1.15rem;margin-top:2.5rem;border-bottom:2px solid #ccc;padding-bottom:.3rem}",
        "table{border-collapse:collapse;width:100%;margin:1rem 0;background:#fff}",
        "th,td{border:1px solid #ddd;padding:.5rem .7rem;text-align:left;vertical-align:top;font-size:.92rem}",
        "th{background:#f0f0f0;white-space:nowrap}",
        "pre{background:#f6f8fa;border:1px solid #e1e4e8;padding:.8rem;overflow-x:auto;font-size:.85rem}",
        ".ok{color:#0a7a2f;font-weight:bold} .ng{color:#b00020;font-weight:bold}",
        ".note{background:#fff8e1;border:1px solid #e6d9a8;padding:.7rem 1rem;font-size:.9rem}",
        ".src{font-size:.85rem;color:#555}",
        "</style>",
        "<h1>SPD008 Payload Replay — 公開ケースの再演</h1>",
        "<p class='note'><b>このデモが言っていること:</b> 公開文書に記録された実在ケースについて、"
        "SPD008の最小payload(部品側の状態説明)が実装されていたら、その場で何が言えたかを再演する。"
        "<b>言っていないこと:</b> 故障予測、原因断定、交換判断、特定OEMの設計批判。"
        "payloadは境界ガードを通過したものだけが出力され、禁止主張を含む文は機械的に拒否される。</p>",
    ]

    for row in rows:
        case = row["case"]
        parts.append(f"<h2>{esc(case.title)}</h2>")
        parts.append(f"<p class='src'>Sample: {esc(case.sample)} / 出典: <a href='{case.source_url}'>{esc(case.source)}</a></p>")
        parts.append("<table>")
        parts.append(f"<tr><th>公開文書に書かれた事実</th><td>{esc(case.public_fact)}</td></tr>")
        parts.append(f"<tr><th>実務が持っていた判断材料</th><td>{esc(case.actual_practice)}</td></tr>")
        state = esc(case.state_text_ja) + "<br><i>" + esc(case.state_text_en) + "</i>"
        parts.append(f"<tr><th>再演: その場で出せた状態説明</th><td>{state}</td></tr>")
        guard = (
            "<span class='ok'>PASS</span> — 禁止主張を含まない"
            if row["payload_ok"]
            else "<span class='ng'>REJECTED</span> — " + esc(", ".join(row["payload_hits"]))
        )
        parts.append(f"<tr><th>境界ガード(payload)</th><td>{guard}</td></tr>")
        naive = (
            f"<span class='ng'>REJECTED</span> — {esc(', '.join(row['naive_hits']))}<br>"
            f"<i>拒否された文の例: 「{esc(case.naive_claim)}」</i>"
            if row["naive_rejected"]
            else "<span class='ok'>(拒否例なし)</span>"
        )
        parts.append(f"<tr><th>境界ガード(安直な言い方の拒否例)</th><td>{naive}</td></tr>")
        parts.append("</table>")
        parts.append("<pre>" + esc(json.dumps(case.payload, ensure_ascii=False, indent=2)) + "</pre>")

    parts.append(
        "<h2>まとめ</h2><p>3ケースとも、実務の判断材料は「DTCの有無」または「部品内部故障に見えるcode」だけであり、"
        "依存signal・電源context・再発という説明は、後から人手の文書(TSB/SSM)で補われた。"
        "SPD008はその文書と同じ内容を、部品がruntimeで、原因断定なしに出せるようにする提案である。</p>"
    )
    return "\n".join(parts)


def render_tsv(rows: list[dict]) -> str:
    header = [
        "case_id", "sample", "public_fact", "actual_practice",
        "replay_state_text_ja", "payload_guard", "rejected_naive_claim", "source_url",
    ]
    lines = ["\t".join(header)]
    for row in rows:
        case = row["case"]
        lines.append("\t".join([
            case.case_id,
            case.sample,
            case.public_fact,
            case.actual_practice,
            case.state_text_ja,
            "PASS" if row["payload_ok"] else "REJECTED: " + ",".join(row["payload_hits"]),
            case.naive_claim + " => REJECTED(" + ",".join(row["naive_hits"]) + ")",
            case.source_url,
        ]))
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = build_rows(CASES)
    for row in rows:
        case = row["case"]
        status = "PASS" if row["payload_ok"] else f"REJECTED {row['payload_hits']}"
        naive = "REJECTED" if row["naive_rejected"] else "NOT-REJECTED (guard gap!)"
        print(f"{case.case_id}: payload={status}, naive_claim={naive}")
        if not row["payload_ok"]:
            raise SystemExit(f"payload for {case.case_id} violates boundary — fix wording")
        if not row["naive_rejected"]:
            raise SystemExit(f"naive claim for {case.case_id} was not rejected — guard too weak")
    OUT_HTML.write_text(render_html(rows), encoding="utf-8")
    OUT_TSV.write_text(render_tsv(rows), encoding="utf-8")
    print(f"wrote {OUT_HTML.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
