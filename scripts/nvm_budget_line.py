#!/usr/bin/env python3
"""Replace the self-chosen "one alarm per hour" with a line that comes from
outside: the non-volatile memory the alarms actually consume (docs/355).

    NVM needed [B]   = rate [/h] * driving [h/yr] * (397/365) * 30
    allowed rate     = allocation [B] / 30 / (driving * 397/365)

Every input except the allocation share is public and cited in SOURCES.md
S12. The share of a data flash given to this element is the receiver's call,
so it is shown as three rows rather than chosen here.

docs/313 counted 397 days x 24 hours; the recorder only runs while driving,
so that was 20 to 90 times too large. This replaces it.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "nvm_budget_line.tsv"

RECORD_B = 30                      # docs/265, measured by packing
RETENTION_D = 397                  # docs/227, UK MOT interval p90, public
# public statistics, SOURCES.md S12
DRIVING = {"英 NTS 2023 (363 trip × 21 分)": 363 * 21 / 60.0,
           "米 AAA ADS 2022 (60.2 分/日)": 60.2 * 365 / 60.0}
# data flash of three automotive MCU families, SOURCES.md S12
DFLASH_KB = {"NXP S32K3 (S32K344)": 128, "Infineon AURIX TC33x-TC36x DF0": 128,
             "Renesas RH850/F1KH-D8": 256, "Infineon AURIX TC39x DF0": 1024}
ALLOC_KB = [8, 32, 64]             # shown, not chosen
# alarm rates already measured in this repo
RATES = [("私が置いた線", 1.0, "docs/248"),
         ("同種チャネル差分、共有率 1.00", 1.5, "docs/352"),
         ("同種チャネル差分、共有率 0.75", 3.2, "docs/352"),
         ("同種チャネル無し、仮想の下端", 12.0, "docs/344"),
         ("同種チャネル無し、仮想の上端", 39.0, "docs/344")]


def need_kb(rate: float, hours: float) -> float:
    return rate * hours * (RETENTION_D / 365.0) * RECORD_B / 1024.0


def allowed(alloc_kb: float, hours: float) -> float:
    return alloc_kb * 1024.0 / RECORD_B / (hours * RETENTION_D / 365.0)


def main() -> None:
    lo, hi = min(DRIVING.values()), max(DRIVING.values())
    print("年間運転時間（公開統計）")
    for k, v in DRIVING.items():
        print(f"  {k:<32}{v:>7.0f} 時間/年")
    print(f"\n397 日に要する不揮発（30 B/件）。幅は運転時間 {lo:.0f}〜{hi:.0f} 時間/年")
    print(f"{'誤検知の水準':<30}{'件/時':>7}{'最小':>10}{'最大':>10}")
    rows = []
    for name, rate, src in RATES:
        a, b = need_kb(rate, lo), need_kb(rate, hi)
        rows.append(("need", name, rate, a, b, src))
        print(f"{name:<30}{rate:>7.1f}{a:>8.1f} KB{b:>8.1f} KB")

    print(f"\n割り当てから逆算した、許せる誤検知（件/時）")
    print(f"{'割り当て':<12}{'運転 ' + f'{hi:.0f} h/年':>16}{'運転 ' + f'{lo:.0f} h/年':>16}")
    for kb in ALLOC_KB:
        a, b = allowed(kb, hi), allowed(kb, lo)
        rows.append(("allowed", f"{kb} KB", kb, a, b, ""))
        print(f"{kb:>6} KB   {a:>14.1f}{b:>16.1f}")

    print(f"\nデータフラッシュ（公開データシート）")
    for k, v in DFLASH_KB.items():
        print(f"  {k:<34}{v:>6} KB")

    print("\n=== 事前登録した予想 ===")
    n1 = all(100 <= v <= 500 for v in DRIVING.values())
    print(f"  N1 運転時間 2 件とも 100〜500 h/年   : {lo:.0f}, {hi:.0f} -> "
          f"{'PASS' if n1 else 'FAIL'}")
    n2 = need_kb(1.5, hi) < 32
    print(f"  N2 1.5 件/時 が幅の全域で 32 KB 未満  : 最大 {need_kb(1.5, hi):.1f} KB -> "
          f"{'PASS' if n2 else 'FAIL'}")
    n3 = need_kb(39.0, hi) > 128
    print(f"  N3 39 件/時 が幅の上端で 128 KB 超    : {need_kb(39.0, hi):.1f} KB -> "
          f"{'PASS' if n3 else 'FAIL'}")
    fams = {"NXP": 128, "Infineon": 1024, "Renesas": 256}
    n4 = all(v >= 64 for v in fams.values())
    print(f"  N4 3 品種とも 64 KB 以上の品がある      : {fams} -> "
          f"{'PASS' if n4 else 'FAIL'}")

    print("\n=== 何もしない基準（1 件/時 のまま）===")
    print(f"  不揮発に直すと {need_kb(1.0, lo):.1f}〜{need_kb(1.0, hi):.1f} KB。"
          f"docs/313 の 9,528 時間換算は {need_kb(1.0, 397 * 24 / (397 / 365)):.0f} KB だった")

    # write endurance, counted but not made into the line (docs/355)
    yrs = 15
    writes = 39.0 * hi * yrs
    print(f"\n書き換え回数の目安: 39 件/時 × {hi:.0f} h/年 × {yrs} 年 = {writes:,.0f} 回。"
          f"1 セクタ 4 KB に 30 B なら 136 件/セクタで、セクタ消去は {writes / 136:,.0f} 回")

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["kind", "name", "rate_or_alloc", "at_low_hours", "at_high_hours", "source"])
        for r in rows:
            w.writerow(r)
        w.writerow(["driving", "NTS 2023", lo, "", "", "SOURCES S12"])
        w.writerow(["driving", "AAA ADS 2022", hi, "", "", "SOURCES S12"])
        for k, v in DFLASH_KB.items():
            w.writerow(["dflash", k, v, "", "", "SOURCES S12"])
    print(f"\n{OUT.relative_to(ROOT)} に書いた")


if __name__ == "__main__":
    main()
