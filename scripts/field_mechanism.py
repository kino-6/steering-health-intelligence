#!/usr/bin/env python3
"""What mechanism do the complaints name? (docs/275 -> docs/276)

Executes the protocol pre-registered in docs/275 against NHTSA FLAT_CMPL,
already inventoried. No new acquisition.

docs/274 found the blank: this project has data for two mechanisms and the
field record names neither. Public data for the mechanism it does name --
intermittent electrical connection -- was searched on four axes and does not
exist. So the question inverts. docs/251 took timescale and recovery out of the
same complaint text; what it never took out is what the repair found, which is
the field's own testimony about mechanism.

Selection is identical to docs/250 and is not changed: steering complaints
carrying an electric, an assist-loss and an intermittency marker, with
hydraulic and external-cause complaints excluded.

Criteria: F1 the share naming wiring or connection, with its lift against all
steering complaints; F2 whether the ranking agrees with the recall analysis of
docs/171; F3 how often motors and windings appear at all.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from field_timescale import (CMPL, F_COMPDESC, F_CDESCR, ELECTRIC, ASSIST_LOSS,
                             INTERMITTENT, HYDRAULIC, EXTERNAL)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "field_mechanism.tsv"

GROUPS = {
    "接続・配線": r"\bWIRING|\bHARNESS|CONNECTOR|TERMINAL|\bPLUG\b|\bPIN\b|\bGROUND\b|CORROSION|\bLOOSE\b",
    "電子制御ユニット": r"\bECU\b|\bMODULE\b|CONTROL UNIT|CIRCUIT BOARD|\bPCB\b|SOLDER",
    "モータ": r"\bMOTOR\b|WINDING|ARMATURE|\bBRUSH|COMMUTATOR",
    "センサ": r"TORQUE SENSOR|\bSENSOR\b|POSITION SENSOR",
    "機械部": r"\bRACK\b|PINION|\bCOLUMN\b|COUPLER|\bSHAFT\b|BEARING",
    "電源": r"\bBATTERY\b|ALTERNATOR|\bFUSE\b|\bRELAY\b|VOLTAGE",
}
RX = {k: re.compile(v) for k, v in GROUPS.items()}


def main() -> None:
    hit_target = Counter()
    hit_all = Counter()
    n_target = n_all = 0
    drop_h = drop_e = 0

    with CMPL.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) <= F_CDESCR:
                continue
            if "STEERING" not in f[F_COMPDESC].upper():
                continue
            d = f[F_CDESCR].upper()
            n_all += 1
            for k, rx in RX.items():
                if rx.search(d):
                    hit_all[k] += 1
            if not (ELECTRIC.search(d) and ASSIST_LOSS.search(d)
                    and INTERMITTENT.search(d)):
                continue
            if HYDRAULIC.search(d):
                drop_h += 1
                continue
            if EXTERNAL.search(d):
                drop_e += 1
                continue
            n_target += 1
            for k, rx in RX.items():
                if rx.search(d):
                    hit_target[k] += 1

    print(f"操舵系の苦情 全体            : {n_all:,}")
    print(f"  断続×アシスト喪失×電動     : {n_target + drop_h + drop_e:,}")
    print(f"  油圧で除外 {drop_h} / 外力で除外 {drop_e}")
    print(f"  **対象**                   : {n_target:,}\n")

    print(f"{'機構':>16} {'対象での言及':>12} {'割合':>8} "
          f"{'操舵系全体':>11} {'割合':>8} {'lift':>7}")
    print("-" * 70)
    rows = []
    for k in GROUPS:
        a, b = hit_target[k], hit_all[k]
        pa, pb = a / n_target, b / n_all
        lift = pa / pb if pb else float("inf")
        rows.append({"group": k, "target": a, "p_target": pa,
                     "all": b, "p_all": pb, "lift": lift})
    for r in sorted(rows, key=lambda x: -x["p_target"]):
        print(f"{r['group']:>16} {r['target']:>12,} {r['p_target']:>7.1%} "
              f"{r['all']:>11,} {r['p_all']:>7.1%} {r['lift']:>6.2f}")

    order = [r["group"] for r in sorted(rows, key=lambda x: -x["p_target"])]
    print(f"\n=== F1 接続・配線への言及 ===")
    w = next(r for r in rows if r["group"] == "接続・配線")
    print(f"  {w['target']:,}/{n_target:,} = {w['p_target']:.1%}  "
          f"操舵系全体の {w['p_all']:.1%} に対し lift {w['lift']:.2f}")

    print(f"\n=== F2 docs/171 のリコール分析と順位が一致するか ===")
    print(f"  苦情の上位2つ  : {order[0]} / {order[1]}")
    print(f"  リコールの上位 : 断続的な電気症状(2.81倍) / 接点の劣化(1.63倍)")
    agree = order[0] in ("接続・配線",) or order[1] in ("接続・配線",)
    print(f"  接続・配線が上位2つに入るか: {'はい' if agree else 'いいえ'}  "
          f"{'PASS' if agree else 'FAIL'}")

    print(f"\n=== F3 モータ・巻線への言及 ===")
    m = next(r for r in rows if r["group"] == "モータ")
    print(f"  {m['target']:,}/{n_target:,} = {m['p_target']:.1%}  lift {m['lift']:.2f}")
    print(f"  **本研究が対象にしている機構である**")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("group\tmentions_target\tshare_target\tmentions_all_steering\t"
                 "share_all\tlift\n")
        for r in rows:
            fh.write(f"{r['group']}\t{r['target']}\t{r['p_target']:.5f}\t"
                     f"{r['all']}\t{r['p_all']:.5f}\t{r['lift']:.4f}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
