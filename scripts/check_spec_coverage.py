#!/usr/bin/env python3
"""Every row of the specification is implemented, or explicitly is not (TASKS.md T3).

docs/225 has grown to 38 bolded rows across a dozen revisions, and until now
nothing checked whether the implementation covers them. A row can be in one of
three states and this refuses to let it be in none:

    implemented   names the symbol in scripts/eps_health_recorder.py
    measured      a number the specification states, not code to run
    declined      not implemented, with the reason recorded here

Adding a row to docs/225 without deciding which of the three it is fails the
check, which is the point: the specification cannot quietly outgrow the code.

    python3 scripts/check_spec_coverage.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs" / "225_recorder_specification.md"
IMPL = ROOT / "scripts" / "eps_health_recorder.py"

# spec row -> what covers it. A symbol name must exist in the implementation.
IMPLEMENTED = {
    "電流測定の分解能": "ChannelFingerprint",       # 8 bit verified in docs/261
    "容量": "ChannelFingerprint.pack",
    "同相除去(必須)": "common_mode_reject",
    "チャネルの採否(出荷時)": "admitted",
    "窓長の下限": "FAST_WINDOW",
    "時間尺度は2本要る": "SLOW_WINDOW",
    "キーオフ時の確定": "HELD_TO_KEY_OFF",
    "有効性": "validity",
    "キーオンからの経過時間": "seconds_since_key_on",
    "キーオフまで持続したか": "HELD_TO_KEY_OFF",
    "1件のサイズ": "REC_FMT",
    "検出の統計量": "thr_fast_mean",
    "「壊れる前に教えます」": "forbidden_fields",
    "「本来の何%出せます」": "forbidden_fields",
    "「どこが壊れたか分かります」": "forbidden_fields",
    "「不安定さで早く気づけます」": "forbidden_fields",
    "「動作点で正規化すれば精度が上がります」": "forbidden_fields",
    "「保証費をN%減らします」": "forbidden_fields",
    "「早い段階から検出できます」": "forbidden_fields",
    "掃引幅": "op_lo",
    "機械学習を使わない": "ChannelFingerprint",   # 決定。docs/290
    "誤報率は個体の単位で": "n_tests",             # docs/294
    "漂流と有効期限の軸": "ChannelFingerprint",     # 決定。docs/312
    "再取得の条件": "cv_shift",
}

# rows that state a measured number or a boundary rather than behaviour to run
MEASURED = {
    "コードなし": "docs/190 の市場記録",
    "路面の凹凸": "docs/213 のトリガ条件",
    "現場の時間尺度": "docs/251 の苦情1,697件",
    "人為的な巻線短絡に対しては": "docs/271 の結果",
    "適用範囲": "docs/295 の判断",
    "20秒": "docs/253 の検出限界",
    "20秒の持続": "docs/253 の検出限界",
    "部品内部での検出限界": "docs/246 の結果",
    "本物の劣化に対しては(パワー段)": "docs/269 の結果",
    "車両レベルの横加速度残差": "docs/255 の正規化規則",
    "部品内部のしきい値電圧": "docs/232 の個体差",
    "温度軸の掃引": "docs/263 の100°C",
    "窓長の上限": "docs/253。発火後に伸ばす規則は運用側の判断",
}

# not implemented, with the reason. docs/287 lists these too.
DECLINED = {
    "不揮発への書き出し": "媒体は部品側の実装事項であり、公開データで検証できない",
    "保持期間": "同上。397日という要件は仕様に残る",
    "ECU内部信号の観測床": "分解能では決まらないと確定(docs/261)。アナログ雑音の設計項目",
    "許容できる逸脱の下限": "部品側では決めないと決定(docs/261)",
}


def spec_rows() -> list[str]:
    text = SPEC.read_text(encoding="utf-8")
    return [m.group(1) for m in re.finditer(r"^\| \*\*([^*]+)\*\*", text, re.M)]


def main() -> int:
    impl = IMPL.read_text(encoding="utf-8")
    rows = spec_rows()
    problems, counts = [], {"implemented": 0, "measured": 0, "declined": 0}

    for r in rows:
        if r in IMPLEMENTED:
            sym = IMPLEMENTED[r]
            if sym.split(".")[0] not in impl:
                problems.append(f"{r}: 実装に「{sym}」が無い")
            else:
                counts["implemented"] += 1
        elif r in MEASURED:
            counts["measured"] += 1
        elif r in DECLINED:
            counts["declined"] += 1
        else:
            problems.append(f"{r}: 実装・測定値・見送りのどれにも分類されていない")

    known = set(IMPLEMENTED) | set(MEASURED) | set(DECLINED)
    for r in sorted(known - set(rows)):
        problems.append(f"{r}: 分類表にあるが docs/225 に無い(仕様から消えた?)")

    print(f"仕様の行 {len(rows)}")
    print(f"  実装あり {counts['implemented']}  測定値 {counts['measured']}  "
          f"見送り {counts['declined']}")
    if counts["declined"]:
        print("\n  見送りとその理由:")
        for k, v in DECLINED.items():
            if k in rows:
                print(f"    {k}: {v}")
    for p in problems:
        print(f"  NG  {p}")
    if not problems:
        print("\n  ok  すべての行が分類されている")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
