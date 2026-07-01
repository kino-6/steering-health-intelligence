#!/usr/bin/env python3
"""Extract low-speed / high-steering-demand proxy windows from commaSteeringControl.

This script intentionally treats the result as a driving-context proxy, not an
EPS degradation or failure signal.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DATASET_URL = "https://huggingface.co/datasets/commaai/commaSteeringControl"
README_URL = "https://huggingface.co/datasets/commaai/commaSteeringControl/raw/main/README.md"


@dataclass
class Window:
    window_id: str
    source_file: str
    start_s: float
    end_s: float
    duration_s: float
    sample_count: int
    mean_speed_mps: float
    max_speed_mps: float
    mean_abs_steer_filtered: float
    max_abs_steer_filtered: float
    mean_abs_steering_angle_deg: float
    max_abs_steering_angle_deg: float
    mean_abs_lat_accel_desired: float
    max_abs_lat_accel_desired: float
    mean_abs_lat_accel_steering_angle: float
    max_abs_lat_accel_steering_angle: float
    steering_pressed_ratio: float
    lat_active_ratio: float
    eps_fw_version: str
    proxy_score: float
    rank: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, type=Path, help="Downloaded vehicle zip from commaSteeringControl")
    parser.add_argument("--vehicle", default="CHRYSLER_PACIFICA_2018")
    parser.add_argument("--low-speed-mps", default=8.0, type=float)
    parser.add_argument("--steer-threshold", default=0.25, type=float)
    parser.add_argument("--min-duration-s", default=1.0, type=float)
    parser.add_argument("--top-windows", default=12, type=int)
    parser.add_argument("--timeseries-windows", default=5, type=int)
    parser.add_argument("--out-dir", default=Path("data"), type=Path)
    parser.add_argument("--generated-dir", default=Path("generated"), type=Path)
    return parser.parse_args()


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    lowered = series.astype(str).str.lower()
    return lowered.isin(["true", "1", "yes"])


def find_runs(mask: list[bool]) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for index, value in enumerate(mask):
        if value and start is None:
            start = index
        elif not value and start is not None:
            runs.append((start, index))
            start = None
    if start is not None:
        runs.append((start, len(mask)))
    return runs


def clean_fw(value: object) -> str:
    text = str(value)
    if text.startswith("b'") and text.endswith("'"):
        return text[2:-1]
    return text


def score_window(frame: pd.DataFrame, source_file: str, start: int, end: int, vehicle: str) -> Window:
    part = frame.iloc[start:end].copy()
    duration = float(part["t"].iloc[-1] - part["t"].iloc[0]) if len(part) > 1 else 0.0
    duration = max(duration, 0.1 * len(part))
    speed = part["vEgo"].astype(float)
    steer = part["steerFiltered"].astype(float).abs()
    angle = part["steeringAngleDeg"].astype(float).abs()
    lat_desired = part["latAccelDesired"].astype(float).abs()
    lat_angle = part["latAccelSteeringAngle"].astype(float).abs()
    steering_pressed = as_bool(part["steeringPressed"])
    lat_active = as_bool(part["latActive"])
    mean_speed = float(speed.mean())
    max_steer = float(steer.max())
    mean_steer = float(steer.mean())
    max_angle = float(angle.max())
    mean_angle = float(angle.mean())
    mean_lat_desired = float(lat_desired.mean())
    max_lat_desired = float(lat_desired.max())
    mean_lat_angle = float(lat_angle.mean())
    max_lat_angle = float(lat_angle.max())
    effort_component = mean_steer * 100.0
    angle_component = min(max_angle / 35.0, 2.5)
    speed_component = 1.0 / (1.0 + mean_speed / 8.0)
    accel_component = 1.0 + min(max_lat_desired, 2.0) / 2.0
    duration_component = min(duration / 4.0, 2.0)
    proxy_score = effort_component * (1.0 + angle_component) * speed_component * accel_component * duration_component
    return Window(
        window_id="",
        source_file=source_file,
        start_s=float(part["t"].iloc[0]),
        end_s=float(part["t"].iloc[-1]),
        duration_s=duration,
        sample_count=len(part),
        mean_speed_mps=mean_speed,
        max_speed_mps=float(speed.max()),
        mean_abs_steer_filtered=mean_steer,
        max_abs_steer_filtered=max_steer,
        mean_abs_steering_angle_deg=mean_angle,
        max_abs_steering_angle_deg=max_angle,
        mean_abs_lat_accel_desired=mean_lat_desired,
        max_abs_lat_accel_desired=max_lat_desired,
        mean_abs_lat_accel_steering_angle=mean_lat_angle,
        max_abs_lat_accel_steering_angle=max_lat_angle,
        steering_pressed_ratio=float(steering_pressed.mean()),
        lat_active_ratio=float(lat_active.mean()),
        eps_fw_version=clean_fw(part["epsFwVersion"].mode().iloc[0]) if "epsFwVersion" in part else "",
        proxy_score=float(proxy_score),
    )


def load_candidates(args: argparse.Namespace) -> tuple[list[Window], dict[str, float]]:
    windows: list[Window] = []
    total_files = 0
    total_samples = 0
    low_speed_samples = 0
    high_demand_samples = 0

    with zipfile.ZipFile(args.zip) as archive:
        names = [name for name in archive.namelist() if name.endswith(".csv")]
        for name in names:
            total_files += 1
            with archive.open(name) as handle:
                frame = pd.read_csv(handle)
            if frame.empty:
                continue
            total_samples += len(frame)
            lat_active = as_bool(frame["latActive"])
            steering_pressed = as_bool(frame["steeringPressed"])
            speed = frame["vEgo"].astype(float)
            steer = frame["steerFiltered"].astype(float).abs()
            low_speed = speed <= args.low_speed_mps
            active_not_pressed = lat_active & ~steering_pressed
            high_demand = steer >= args.steer_threshold
            low_speed_samples += int(low_speed.sum())
            high_demand_samples += int((low_speed & active_not_pressed & high_demand).sum())
            mask = (low_speed & active_not_pressed & high_demand).tolist()
            for start, end in find_runs(mask):
                if end - start < 2:
                    continue
                duration = float(frame["t"].iloc[end - 1] - frame["t"].iloc[start])
                if duration < args.min_duration_s:
                    continue
                windows.append(score_window(frame, name, start, end, args.vehicle))

    windows.sort(key=lambda item: item.proxy_score, reverse=True)
    for rank, window in enumerate(windows, start=1):
        window.rank = rank
        window.window_id = f"LSHSD-{rank:03d}"

    summary = {
        "total_files": float(total_files),
        "total_samples": float(total_samples),
        "low_speed_samples": float(low_speed_samples),
        "high_demand_samples": float(high_demand_samples),
        "candidate_windows": float(len(windows)),
    }
    return windows, summary


def write_windows(path: Path, windows: list[Window], limit: int) -> None:
    fields = list(Window.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for window in windows[:limit]:
            writer.writerow({field: getattr(window, field) for field in fields})


def write_timeseries(path: Path, args: argparse.Namespace, windows: list[Window]) -> dict[str, list[dict[str, float | str]]]:
    selected = windows[: args.timeseries_windows]
    by_id: dict[str, list[dict[str, float | str]]] = {}
    with zipfile.ZipFile(args.zip) as archive, path.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "window_id",
            "source_file",
            "t_s",
            "vEgo_mps",
            "steerFiltered",
            "steeringAngleDeg",
            "latAccelDesired",
            "latAccelSteeringAngle",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        for window in selected:
            with archive.open(window.source_file) as source:
                frame = pd.read_csv(source)
            part = frame[(frame["t"] >= window.start_s) & (frame["t"] <= window.end_s)].copy()
            rows: list[dict[str, float | str]] = []
            for _, row in part.iterrows():
                record = {
                    "window_id": window.window_id,
                    "source_file": window.source_file,
                    "t_s": round(float(row["t"]), 3),
                    "vEgo_mps": round(float(row["vEgo"]), 5),
                    "steerFiltered": round(float(row["steerFiltered"]), 5),
                    "steeringAngleDeg": round(float(row["steeringAngleDeg"]), 5),
                    "latAccelDesired": round(float(row["latAccelDesired"]), 5),
                    "latAccelSteeringAngle": round(float(row["latAccelSteeringAngle"]), 5),
                }
                writer.writerow(record)
                rows.append(record)
            by_id[window.window_id] = rows
    return by_id


def points(values: list[float], width: int, height: int, lower: float | None = None, upper: float | None = None) -> str:
    if not values:
        return ""
    lo = min(values) if lower is None else lower
    hi = max(values) if upper is None else upper
    if math.isclose(lo, hi):
        lo -= 1.0
        hi += 1.0
    coords = []
    for index, value in enumerate(values):
        x = index * width / max(1, len(values) - 1)
        y = height - ((value - lo) / (hi - lo) * height)
        coords.append(f"{x:.1f},{y:.1f}")
    return " ".join(coords)


def sparkline(rows: list[dict[str, float | str]], key: str, color: str, lower: float | None = None, upper: float | None = None) -> str:
    width = 680
    height = 120
    values = [float(row[key]) for row in rows]
    line = points(values, width, height, lower, upper)
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(key)} trend">'
        f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{line}"/>'
        "</svg>"
    )


def write_html(path: Path, args: argparse.Namespace, windows: list[Window], summary: dict[str, float], series: dict[str, list[dict[str, float | str]]]) -> None:
    top = windows[: args.top_windows]
    rows_html = []
    for window in top:
        rows_html.append(
            "<tr>"
            f"<td>{window.rank}</td>"
            f"<td>{html.escape(window.window_id)}</td>"
            f"<td>{html.escape(Path(window.source_file).name)}</td>"
            f"<td>{window.start_s:.1f}-{window.end_s:.1f}</td>"
            f"<td>{window.duration_s:.1f}</td>"
            f"<td>{window.mean_speed_mps:.2f}</td>"
            f"<td>{window.max_abs_steer_filtered:.2f}</td>"
            f"<td>{window.max_abs_steering_angle_deg:.1f}</td>"
            f"<td>{window.proxy_score:.1f}</td>"
            "</tr>"
        )

    chart_cards = []
    for window in top[: args.timeseries_windows]:
        rows = series.get(window.window_id, [])
        chart_cards.append(
            f"""
            <section class="chart-card">
              <div class="chart-title">
                <h3>{html.escape(window.window_id)} / {html.escape(Path(window.source_file).name)}</h3>
                <p>{window.start_s:.1f}-{window.end_s:.1f}s, mean speed {window.mean_speed_mps:.2f} m/s, score {window.proxy_score:.1f}</p>
              </div>
              <div class="legend"><span class="blue"></span> steerFiltered <span class="red"></span> steeringAngleDeg <span class="green"></span> vEgo</div>
              <div class="plot">
                {sparkline(rows, "steerFiltered", "#2563eb", -1.0, 1.0)}
                {sparkline(rows, "steeringAngleDeg", "#dc2626")}
                {sparkline(rows, "vEgo_mps", "#16a34a", 0.0, args.low_speed_mps)}
              </div>
            </section>
            """
        )

    payload = {
        "dataset": DATASET_URL,
        "vehicle": args.vehicle,
        "low_speed_mps": args.low_speed_mps,
        "steer_threshold": args.steer_threshold,
        "summary": summary,
    }

    content = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Low-speed high-steering-demand proxy</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #5d667a;
      --line: #d8dde8;
      --panel: #f7f9fc;
      --accent: #0f766e;
      --warn: #b45309;
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #ffffff;
    }}
    header, main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 24px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: 34px;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 32px 0 12px;
      font-size: 22px;
      letter-spacing: 0;
    }}
    h3 {{
      margin: 0;
      font-size: 17px;
      letter-spacing: 0;
    }}
    p {{
      color: var(--muted);
      line-height: 1.7;
      margin: 0 0 10px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(5, minmax(120px, 1fr));
      gap: 10px;
      margin-top: 22px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      background: var(--panel);
    }}
    .metric strong {{
      display: block;
      font-size: 22px;
      margin-bottom: 4px;
    }}
    .metric span {{
      color: var(--muted);
      font-size: 13px;
    }}
    .note {{
      border-left: 4px solid var(--warn);
      padding: 12px 14px;
      background: #fff7ed;
      color: #5c3b10;
      margin-top: 20px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 8px;
      text-align: right;
      white-space: nowrap;
    }}
    th:nth-child(2), td:nth-child(2), th:nth-child(3), td:nth-child(3) {{
      text-align: left;
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
      background: #fbfcfe;
    }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .chart-card {{
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 14px 0;
      padding: 16px;
      background: #fff;
    }}
    .chart-title {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: baseline;
      margin-bottom: 10px;
    }}
    .legend {{
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }}
    .legend span {{
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin: 0 4px 0 12px;
    }}
    .legend .blue {{ background: #2563eb; margin-left: 0; }}
    .legend .red {{ background: #dc2626; }}
    .legend .green {{ background: #16a34a; }}
    .plot {{
      display: grid;
      gap: 8px;
    }}
    svg {{
      width: 100%;
      height: 78px;
      background: linear-gradient(#f9fbff, #ffffff);
      border: 1px solid #e8ecf3;
      border-radius: 6px;
    }}
    code {{
      background: #eef3f8;
      border-radius: 4px;
      padding: 2px 5px;
    }}
    @media (max-width: 760px) {{
      h1 {{ font-size: 26px; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(120px, 1fr)); }}
      .chart-title {{ display: block; }}
      header, main {{ padding: 24px 16px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Low-speed high-steering-demand proxy</h1>
    <p>commaSteeringControlのCHRYSLER_PACIFICA_2018から、低速かつ操舵要求が高い代表windowを抽出した試作ビューです。</p>
    <p>判定条件: <code>vEgo <= {args.low_speed_mps:g} m/s</code>, <code>|steerFiltered| >= {args.steer_threshold:g}</code>, <code>latActive=True</code>, <code>steeringPressed=False</code>.</p>
    <div class="metrics">
      <div class="metric"><strong>{int(summary["total_files"]):,}</strong><span>CSV segments scanned</span></div>
      <div class="metric"><strong>{int(summary["total_samples"]):,}</strong><span>samples scanned</span></div>
      <div class="metric"><strong>{int(summary["low_speed_samples"]):,}</strong><span>low-speed samples</span></div>
      <div class="metric"><strong>{int(summary["high_demand_samples"]):,}</strong><span>low-speed high-demand samples</span></div>
      <div class="metric"><strong>{int(summary["candidate_windows"]):,}</strong><span>candidate windows</span></div>
    </div>
    <p class="note">これは故障予測ではありません。EPSサプライヤ視点では「市場不具合で問題になりやすい低速・高操舵負荷文脈を、公開走行データで再現できるか」を見るproxyです。</p>
  </header>
  <main>
    <h2>代表window</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>rank</th><th>window</th><th>file</th><th>time s</th><th>duration</th><th>mean vEgo</th><th>max |steer|</th><th>max |angle|</th><th>score</th></tr></thead>
        <tbody>{''.join(rows_html)}</tbody>
      </table>
    </div>
    <h2>可視化</h2>
    {''.join(chart_cards)}
    <h2>検証メモ</h2>
    <p>データセット説明上、<code>steerFiltered</code>は正規化・rate limitedされた操舵トルク入力、<code>vEgo</code>は車速、<code>latActive</code>はopenpilotの横制御有効状態です。ここでは低速・高操舵要求の抽出にのみ使い、DTCや劣化兆候とは結びつけていません。</p>
    <script type="application/json" id="provenance">{html.escape(json.dumps(payload, ensure_ascii=False))}</script>
  </main>
</body>
</html>
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.generated_dir.mkdir(parents=True, exist_ok=True)
    windows, summary = load_candidates(args)
    if not windows:
        raise SystemExit("No candidate windows found. Lower --steer-threshold or --min-duration-s.")
    write_windows(args.out_dir / "low_speed_high_steering_proxy_windows.tsv", windows, args.top_windows)
    series = write_timeseries(args.out_dir / "low_speed_high_steering_proxy_timeseries.tsv", args, windows)
    write_html(args.generated_dir / "low_speed_high_steering_proxy.html", args, windows, summary, series)
    summary_path = args.out_dir / "low_speed_high_steering_proxy_summary.tsv"
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["metric", "value"])
        writer.writerow(["dataset_url", DATASET_URL])
        writer.writerow(["readme_url", README_URL])
        writer.writerow(["vehicle", args.vehicle])
        writer.writerow(["low_speed_mps", args.low_speed_mps])
        writer.writerow(["steer_threshold", args.steer_threshold])
        for key, value in summary.items():
            writer.writerow([key, int(value)])
    print(f"wrote {len(windows)} candidate windows")
    print(args.out_dir / "low_speed_high_steering_proxy_windows.tsv")
    print(args.out_dir / "low_speed_high_steering_proxy_timeseries.tsv")
    print(args.generated_dir / "low_speed_high_steering_proxy.html")


if __name__ == "__main__":
    main()
