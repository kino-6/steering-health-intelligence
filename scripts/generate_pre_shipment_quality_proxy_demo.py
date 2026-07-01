#!/usr/bin/env python3
"""Generate a Bosch-shaped pre-shipment quality screening proxy demo.

The demo intentionally uses synthetic data. It mirrors the public Bosch Kaggle
task shape: unit-level manufacturing measurements, station/time context, rare
quality fail labels, and a risk-ranked action list.
"""

from __future__ import annotations

import csv
import html
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
GENERATED = ROOT / "generated"

SEED = 20260609
N_UNITS = 6000


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    if not values:
        return 0.0
    idx = (len(values) - 1) * q
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - idx) + values[hi] * (idx - lo)


def zscore(value: float, mean: float, std: float) -> float:
    if std <= 0:
        return 0.0
    return (value - mean) / std


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def generate_units() -> list[dict[str, object]]:
    rng = random.Random(SEED)
    units: list[dict[str, object]] = []
    lines = ["L1", "L2", "L3"]
    shifts = ["A", "B", "C"]
    variants = ["base", "adas", "high_torque", "cold_region"]
    software = ["SW_1.2", "SW_1.3", "SW_1.4"]

    for idx in range(1, N_UNITS + 1):
        line = rng.choices(lines, weights=[0.42, 0.36, 0.22])[0]
        shift = rng.choices(shifts, weights=[0.38, 0.36, 0.26])[0]
        variant = rng.choices(variants, weights=[0.38, 0.27, 0.2, 0.15])[0]
        sw = rng.choices(software, weights=[0.34, 0.46, 0.2])[0]
        hour = (idx // 18) % 24
        lot = 1000 + idx // 80

        # Hidden process drift, similar to a station/lot issue that would be
        # visible only after connecting upstream measurements with EOL labels.
        drift_window = 2400 <= idx <= 3150 and line == "L2"
        late_shift_penalty = shift == "C" and hour in {1, 2, 3, 4, 5}
        high_torque_penalty = variant == "high_torque"

        torque_bias = rng.gauss(0.0, 0.72) + (0.72 if drift_window else 0.0) + (0.18 if high_torque_penalty else 0.0)
        current_margin = rng.gauss(8.0, 1.7) - (1.55 if drift_window else 0.0) - (0.75 if late_shift_penalty else 0.0)
        acoustic_noise = rng.gauss(47.0, 3.2) + (2.1 if line == "L2" and shift == "C" else 0.0)
        can_response = rng.gauss(2.9, 0.55) + (0.55 if sw == "SW_1.4" and line == "L3" else 0.0)
        eol_reserve = rng.gauss(5.2, 1.3) - (0.95 if drift_window else 0.0) - (0.45 if high_torque_penalty else 0.0)

        latent = -5.35
        latent += 0.72 * max(torque_bias - 1.05, 0.0)
        latent += 0.54 * max(6.2 - current_margin, 0.0)
        latent += 0.22 * max(acoustic_noise - 51.0, 0.0)
        latent += 0.62 * max(can_response - 3.65, 0.0)
        latent += 0.54 * max(4.1 - eol_reserve, 0.0)
        latent += 0.55 if drift_window else 0.0
        latent += 0.24 if late_shift_penalty else 0.0
        latent += 0.18 if high_torque_penalty else 0.0

        probability = clamp(sigmoid(latent), 0.001, 0.35)
        failed = 1 if rng.random() < probability else 0
        units.append(
            {
                "unit_id": f"EPS-{idx:05d}",
                "line": line,
                "shift": shift,
                "variant": variant,
                "software": sw,
                "hour": hour,
                "lot": lot,
                "torque_bias": torque_bias,
                "current_margin": current_margin,
                "acoustic_noise": acoustic_noise,
                "can_response": can_response,
                "eol_reserve": eol_reserve,
                "true_fail": failed,
                "latent_probability": probability,
            }
        )
    return units


def score_units(units: list[dict[str, object]]) -> None:
    numeric_cols = ["torque_bias", "current_margin", "acoustic_noise", "can_response", "eol_reserve"]
    stats: dict[str, tuple[float, float]] = {}
    for col in numeric_cols:
        vals = [float(unit[col]) for unit in units]
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        stats[col] = (mean, math.sqrt(var))

    for unit in units:
        risk = -2.7
        risk += 0.95 * max(zscore(float(unit["torque_bias"]), *stats["torque_bias"]), 0.0)
        risk += 0.74 * max(-zscore(float(unit["current_margin"]), *stats["current_margin"]), 0.0)
        risk += 0.38 * max(zscore(float(unit["acoustic_noise"]), *stats["acoustic_noise"]), 0.0)
        risk += 0.48 * max(zscore(float(unit["can_response"]), *stats["can_response"]), 0.0)
        risk += 0.62 * max(-zscore(float(unit["eol_reserve"]), *stats["eol_reserve"]), 0.0)
        risk += 0.32 if unit["line"] == "L2" and unit["shift"] == "C" else 0.0
        risk += 0.22 if unit["variant"] == "high_torque" else 0.0
        unit["risk_score"] = sigmoid(risk)

        reasons = []
        if zscore(float(unit["torque_bias"]), *stats["torque_bias"]) > 1.0:
            reasons.append("calibration torque bias high")
        if zscore(float(unit["current_margin"]), *stats["current_margin"]) < -1.0:
            reasons.append("functional current margin low")
        if zscore(float(unit["acoustic_noise"]), *stats["acoustic_noise"]) > 1.0:
            reasons.append("acoustic station high")
        if zscore(float(unit["can_response"]), *stats["can_response"]) > 1.0:
            reasons.append("electrical communication slow")
        if zscore(float(unit["eol_reserve"]), *stats["eol_reserve"]) < -1.0:
            reasons.append("EOL reserve low")
        if unit["line"] == "L2" and 2400 <= int(unit["unit_id"].split("-")[1]) <= 3150:
            reasons.append("line L2 drift window")
        unit["reason"] = "; ".join(reasons[:4]) or "combined mild deviations"

        primary = str(unit["reason"]).split("; ")[0]
        if "torque" in primary or "line L2" in primary:
            action = "EOL前にcalibration/torque関連を追加確認"
        elif "current" in primary or "reserve" in primary:
            action = "EOL後に再検査または保留判定"
        elif "acoustic" in primary:
            action = "音響/組付工程の工程確認"
        elif "communication" in primary:
            action = "通信応答とsoftware/calibration条件を確認"
        else:
            action = "上位リスク個体として品質確認"
        unit["recommended_action"] = action


def make_summary(units: list[dict[str, object]]) -> list[dict[str, object]]:
    total_fail = sum(int(unit["true_fail"]) for unit in units)
    fail_rate = total_fail / len(units)
    sorted_units = sorted(units, key=lambda row: float(row["risk_score"]), reverse=True)
    summary: list[dict[str, object]] = []
    for pct in [0.01, 0.05, 0.10, 0.20]:
        count = max(1, int(len(sorted_units) * pct))
        bucket = sorted_units[:count]
        hits = sum(int(row["true_fail"]) for row in bucket)
        capture = hits / total_fail if total_fail else 0.0
        precision = hits / count
        lift = precision / fail_rate if fail_rate else 0.0
        summary.append(
            {
                "risk_bucket": f"top_{int(pct * 100)}pct",
                "units_reviewed": count,
                "fail_or_retest_caught": hits,
                "capture_rate": f"{capture:.3f}",
                "precision": f"{precision:.3f}",
                "lift_vs_random": f"{lift:.1f}",
                "operational_read": f"上位{int(pct * 100)}%を先に見るとfail/retest候補の{capture:.1%}を拾う",
            }
        )
    summary.append(
        {
            "risk_bucket": "overall",
            "units_reviewed": len(units),
            "fail_or_retest_caught": total_fail,
            "capture_rate": "1.000",
            "precision": f"{fail_rate:.3f}",
            "lift_vs_random": "1.0",
            "operational_read": "全体母集団。正解率ではなく上位リストの捕捉率を見る",
        }
    )
    return summary


def make_top_units(units: list[dict[str, object]]) -> list[dict[str, object]]:
    top = sorted(units, key=lambda row: float(row["risk_score"]), reverse=True)[:30]
    rows: list[dict[str, object]] = []
    for rank, unit in enumerate(top, start=1):
        rows.append(
            {
                "rank": rank,
                "unit_id": unit["unit_id"],
                "risk_score": f"{float(unit['risk_score']):.3f}",
                "actual_label_in_proxy": "fail/retest" if int(unit["true_fail"]) else "pass",
                "line": unit["line"],
                "shift": unit["shift"],
                "variant": unit["variant"],
                "software": unit["software"],
                "hour": unit["hour"],
                "lot": unit["lot"],
                "reason": unit["reason"],
                "recommended_action": unit["recommended_action"],
            }
        )
    return rows


def make_station_signals(units: list[dict[str, object]]) -> list[dict[str, object]]:
    thresholds = {
        "calibration_torque_bias_high": [unit for unit in units if float(unit["torque_bias"]) >= percentile([float(u["torque_bias"]) for u in units], 0.90)],
        "functional_current_margin_low": [unit for unit in units if float(unit["current_margin"]) <= percentile([float(u["current_margin"]) for u in units], 0.10)],
        "acoustic_noise_high": [unit for unit in units if float(unit["acoustic_noise"]) >= percentile([float(u["acoustic_noise"]) for u in units], 0.90)],
        "electrical_can_response_slow": [unit for unit in units if float(unit["can_response"]) >= percentile([float(u["can_response"]) for u in units], 0.90)],
        "eol_reserve_low": [unit for unit in units if float(unit["eol_reserve"]) <= percentile([float(u["eol_reserve"]) for u in units], 0.10)],
        "line_l2_drift_window": [unit for unit in units if unit["line"] == "L2" and 2400 <= int(str(unit["unit_id"]).split("-")[1]) <= 3150],
    }
    overall = sum(int(unit["true_fail"]) for unit in units) / len(units)
    rows: list[dict[str, object]] = []
    for signal, bucket in thresholds.items():
        rate = sum(int(unit["true_fail"]) for unit in bucket) / len(bucket) if bucket else 0.0
        rows.append(
            {
                "signal_group": signal,
                "units": len(bucket),
                "fail_or_retest_rate": f"{rate:.3f}",
                "lift_vs_overall": f"{(rate / overall if overall else 0.0):.1f}",
                "shop_floor_read": shop_floor_read(signal),
            }
        )
    rows.sort(key=lambda row: float(row["lift_vs_overall"]), reverse=True)
    return rows


def shop_floor_read(signal: str) -> str:
    mapping = {
        "calibration_torque_bias_high": "calibration工程のトルク偏りを追加確認",
        "functional_current_margin_low": "機能検査の電流余裕低下を再検査条件へ",
        "acoustic_noise_high": "音響/組付工程の設備・治具確認",
        "electrical_can_response_slow": "通信応答とsoftware/calibration条件を確認",
        "eol_reserve_low": "EOL reserve低下個体を保留/再検査候補へ",
        "line_l2_drift_window": "L2の時刻/lot/設備ドリフトを工程確認",
    }
    return mapping.get(signal, "工程確認候補")


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def table_html(rows: list[dict[str, object]], columns: list[str]) -> str:
    head = "".join(f"<th>{escape(col)}</th>" for col in columns)
    body_rows = []
    for row in rows:
        body_rows.append("<tr>" + "".join(f"<td>{escape(row.get(col, ''))}</td>" for col in columns) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def bar_svg(summary: list[dict[str, object]]) -> str:
    buckets = [row for row in summary if row["risk_bucket"] != "overall"]
    width = 760
    height = 230
    left = 72
    bottom = 180
    bar_w = 92
    gap = 68
    max_capture = max(float(row["capture_rate"]) for row in buckets)
    scale = 140 / max(max_capture, 0.01)
    rects = []
    labels = []
    for i, row in enumerate(buckets):
        x = left + i * (bar_w + gap)
        h = float(row["capture_rate"]) * scale
        y = bottom - h
        rects.append(f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" fill="#0f766e" rx="4"/>')
        labels.append(f'<text x="{x + bar_w / 2}" y="{bottom + 24}" text-anchor="middle">{escape(row["risk_bucket"])}</text>')
        labels.append(f'<text x="{x + bar_w / 2}" y="{y - 8:.1f}" text-anchor="middle">{float(row["capture_rate"]):.0%}</text>')
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="capture rate chart">'
        f'<line x1="{left - 20}" y1="{bottom}" x2="{width - 40}" y2="{bottom}" stroke="#cbd5e1"/>'
        + "".join(rects)
        + "".join(labels)
        + "</svg>"
    )


def make_html(summary: list[dict[str, object]], top_units: list[dict[str, object]], station_signals: list[dict[str, object]]) -> str:
    overall = next(row for row in summary if row["risk_bucket"] == "overall")
    top5 = next(row for row in summary if row["risk_bucket"] == "top_5pct")
    top10 = next(row for row in summary if row["risk_bucket"] == "top_10pct")
    top_unit_cols = ["rank", "unit_id", "risk_score", "actual_label_in_proxy", "line", "shift", "variant", "reason", "recommended_action"]
    station_cols = ["signal_group", "units", "fail_or_retest_rate", "lift_vs_overall", "shop_floor_read"]
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>出荷前品質スクリーニング proxy</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #5f697a;
      --line: #d8dde8;
      --panel: #f7f9fc;
      --accent: #0f766e;
      --warn: #9a3412;
    }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: #fff; }}
    header, main {{ max-width: 1160px; margin: 0 auto; padding: 32px 24px; }}
    header {{ border-bottom: 1px solid var(--line); }}
    h1 {{ margin: 0 0 12px; font-size: 34px; letter-spacing: 0; }}
    h2 {{ margin: 32px 0 12px; font-size: 22px; letter-spacing: 0; }}
    p {{ color: var(--muted); line-height: 1.75; margin: 0 0 10px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, minmax(150px, 1fr)); gap: 10px; margin-top: 22px; }}
    .metric {{ border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: var(--panel); }}
    .metric strong {{ display: block; font-size: 24px; margin-bottom: 4px; }}
    .metric span {{ color: var(--muted); font-size: 13px; }}
    .note {{ border-left: 4px solid var(--warn); padding: 12px 14px; background: #fff7ed; color: #5c2f0e; margin-top: 20px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px 8px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 600; background: #fbfcfe; white-space: nowrap; }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }}
    .section {{ margin-top: 24px; }}
    svg {{ width: 100%; height: auto; border: 1px solid #e8ecf3; border-radius: 8px; background: linear-gradient(#f9fbff, #ffffff); }}
    code {{ background: #eef3f8; border-radius: 4px; padding: 2px 5px; }}
    @media (max-width: 760px) {{ h1 {{ font-size: 26px; }} .metrics {{ grid-template-columns: repeat(2, minmax(130px, 1fr)); }} header, main {{ padding: 24px 16px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>出荷前品質スクリーニング proxy</h1>
    <p>Bosch Production Line Performance型の構造を、EPSサプライヤの製造・EOL検査に読み替えた小型デモです。</p>
    <p>これはKaggle実データではなく、公開課題から得た構造を再現したsynthetic proxyです。目的は、上位リスク個体と工程グループ説明が、再検査・保留・工程確認に貼れるかを見ることです。</p>
    <div class="metrics">
      <div class="metric"><strong>{N_UNITS:,}</strong><span>synthetic units</span></div>
      <div class="metric"><strong>{escape(overall["fail_or_retest_caught"])}</strong><span>fail / retest labels</span></div>
      <div class="metric"><strong>{float(top5["capture_rate"]):.0%}</strong><span>captured in top 5%</span></div>
      <div class="metric"><strong>{float(top10["capture_rate"]):.0%}</strong><span>captured in top 10%</span></div>
    </div>
    <p class="note">言ってはいけないこと: 出荷後故障予測、EOL検査省略、保証費削減、root cause断定。これは出荷前の再検査・保留・工程確認の優先順位を見るproxyです。</p>
  </header>
  <main>
    <section class="section">
      <h2>上位リスク個体でfail/retest候補をどれだけ拾えるか</h2>
      {bar_svg(summary)}
      <div class="table-wrap">{table_html(summary, ["risk_bucket", "units_reviewed", "fail_or_retest_caught", "capture_rate", "precision", "lift_vs_random", "operational_read"])}</div>
    </section>
    <section class="section">
      <h2>要注意個体リスト</h2>
      <p>現場で見るべき出力は、モデル精度ではなく、このリストを再検査・保留・工程確認に使えるかです。</p>
      <div class="table-wrap">{table_html(top_units[:15], top_unit_cols)}</div>
    </section>
    <section class="section">
      <h2>工程グループ説明</h2>
      <p>匿名化Kaggleでは物理原因を断定できません。EPS実データで価値にするには、工程名、測定名、設備、時刻、ロットを残し、工程確認に転記できる形にする必要があります。</p>
      <div class="table-wrap">{table_html(station_signals, station_cols)}</div>
    </section>
    <section class="section">
      <h2>EPSサプライヤとしての読み方</h2>
      <p>このdemoでProceedを見る条件は、上位リスク個体がfail/retest候補を集め、かつ工程グループ説明が再検査・保留・工程確認に翻訳できることです。</p>
      <p>Kill条件は、上位リスク個体が拾えない、拾えても現場アクションがない、既存SPC/MES/BIで同じ判断ができる、または話が出荷後故障予測に戻ることです。</p>
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    DATA.mkdir(exist_ok=True)
    GENERATED.mkdir(exist_ok=True)
    units = generate_units()
    score_units(units)

    summary = make_summary(units)
    top_units = make_top_units(units)
    station_signals = make_station_signals(units)

    write_tsv(
        DATA / "pre_shipment_quality_proxy_summary.tsv",
        summary,
        ["risk_bucket", "units_reviewed", "fail_or_retest_caught", "capture_rate", "precision", "lift_vs_random", "operational_read"],
    )
    write_tsv(
        DATA / "pre_shipment_quality_proxy_top_units.tsv",
        top_units,
        ["rank", "unit_id", "risk_score", "actual_label_in_proxy", "line", "shift", "variant", "software", "hour", "lot", "reason", "recommended_action"],
    )
    write_tsv(
        DATA / "pre_shipment_quality_proxy_station_signals.tsv",
        station_signals,
        ["signal_group", "units", "fail_or_retest_rate", "lift_vs_overall", "shop_floor_read"],
    )

    html_out = make_html(summary, top_units, station_signals)
    (GENERATED / "pre_shipment_quality_screening_proxy.html").write_text(html_out, encoding="utf-8")


if __name__ == "__main__":
    main()
