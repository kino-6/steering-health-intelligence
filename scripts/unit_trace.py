"""One real unit, byte for byte: what is written, what is sent (docs/319).

docs/318 sized the layers. This one shows the actual contents for a single
unit, taken from the real inverter recording rather than from an example
made up to look plausible -- the fingerprint that end of line leaves behind,
the frames that go out on the bus during a drive, and the records that are
appended when it deviates.

Data: Bacha et al., inverter-driven PMSM fault dataset, CC BY 4.0.
"""

from __future__ import annotations

import struct
import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eps_health_recorder as ehr
from demo_recorder import SIBLINGS, as_dicts
from inverter_recorder import ZIP, BASE, read
from unit_ledger import bus_frame

ROOT = Path(__file__).resolve().parent.parent


def hexd(b: bytes) -> str:
    return " ".join(f"{x:02X}" for x in b)


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    names = [n for n in z.namelist() if n.startswith(BASE) and n.endswith(".txt")]
    normal = read(z, next(n for n in names if "normal_operation" in n))
    fault = read(z, next(n for n in sorted(names)
                         if "fault_scenarios" in n and "HB1_LOW_SIDE_SC" in n))
    half = len(normal) // 2
    v_en, o_en = as_dicts(normal[:half])
    fp = ehr.enrol(v_en, o_en, siblings=SIBLINGS, alarm_per_hour=1.0)

    print("■ 出荷ラインで 1 回だけ書かれるもの ── 不揮発 448 バイト\n")
    ch = fp.channels["T1"]
    print(f"  チャネル T1（ハーフブリッジ 1 の温度、同種 {','.join(ch.siblings)} を差し引いた後）")
    for lab, v, u in (("動作点に対する傾き", ch.slope, ""),
                      ("基準値", ch.intercept, ""),
                      ("この個体自身の床", ch.floor, "（以後の逸脱はこの単位で数える）"),
                      ("掃引した動作点 下", ch.op_lo, "（外では宣言しない）"),
                      ("掃引した動作点 上", ch.op_hi, ""),
                      ("速い側 平均の閾値", ch.thr_fast_mean, "床"),
                      ("速い側 最大の閾値", ch.thr_fast_max, "床"),
                      ("遅い側の閾値", ch.thr_slow, "床"),
                      ("較正できた誤報 速", ch.alarm_per_hour_fast, "件/時"),
                      ("較正できた誤報 遅", ch.alarm_per_hour_slow, "件/時"),
                      ("傾きの基準", ch.slope_drift, "（遅い側はここからのずれを見る）"),
                      ("そのばらつき", ch.slope_scatter, ""),
                      ("交差検証のずれ", ch.cv_shift, "床"),
                      ("採否", float(ch.admitted), "（1 = 宣言してよい）")):
        print(f"    {lab:<22} {v:>12.4g} {u}")
    print(f"\n  実バイト列（T1 の 56 バイト）:\n    {hexd(ch.pack()[:28])}\n    {hexd(ch.pack()[28:])}")
    print(f"\n  8 チャネルぶんで {len(fp.pack())} バイト。以後、車両寿命のあいだ書き換えない。")
    print(f"  宣言に使うチャネル: {', '.join(fp.admitted)}"
          f"（残り {8-len(fp.admitted)} 本は自分の健全を再現できず除外）")

    v_f, o_f = as_dicts(fault)
    # This unit's enrolment could only be calibrated to 281 alarms/hour, so at
    # the specification's 1/hour every detector stays switched off and the unit
    # writes nothing at all. Both modes are shown because the difference
    # between them is the whole of docs/318's 274-fold spread.
    ask = max(c.alarm_per_hour_slow for c in fp.channels.values())
    silent = ehr.Recorder(fp).run_session(v_f, o_f, siblings=SIBLINGS,
                                          alarm_per_hour=1.0)
    recs = ehr.Recorder(fp).run_session(v_f, o_f, siblings=SIBLINGS,
                                        alarm_per_hour=ask)

    print("\n\n■ 同じ走行（ハーフブリッジ 1 下側の短絡）を 2 通りの要求で流す\n")
    nf_s = sum(1 for r in silent if r.validity and r.flags)
    nf_r = sum(1 for r in recs if r.validity and r.flags)
    print(f"  仕様どおり 1 件/時 を要求  → 発火 {nf_s} 件。"
          f"較正が {ask:.0f} 件/時 までしか届かないので、検出器は動かない")
    print(f"  較正できた {ask:.0f} 件/時 を要求 → 発火 {nf_r} 件")
    print(f"\n  以下は後者。書かれる量の差は、要求する誤報率だけで決まる。")

    print("\n\n■ 走行中、車内バスへ 100 ms ごとに出るもの ── 2 バイト\n")
    print(f"  {'時刻':>8}  {'バイト列':>7}  意味")
    shown, prev = 0, None
    for r in recs[:200]:
        st = (1 if r.validity else 0) | (r.flags << 1)
        f = bus_frame(st, r.deviation)
        if f == prev and shown > 3:
            continue
        prev = f
        d = "宣言しない（動作点が範囲外）" if not r.validity else (
            f"逸脱 {r.deviation:.2f} 床" +
            ("／速い側" if r.flags & ehr.Record.FAST else "") +
            ("／遅い側" if r.flags & ehr.Record.SLOW else ""))
        print(f"  {r.seconds_since_key_on:>6}s  {hexd(f):>7}  {d}")
        shown += 1
        if shown >= 8:
            break
    print("\n  これで全部である。あと何 % 出せるか・残り寿命・どこが壊れたかは乗らない。")

    print("\n\n■ 逸脱したときだけ不揮発に追記されるもの ── 30 バイト/件\n")
    fired = [r for r in recs if r.validity and r.flags]
    for r in fired[:3]:
        print(f"  {r.describe()}")
        print(f"    {hexd(r.pack()[:15])} {hexd(r.pack()[15:])}")
    print(f"\n  この走行で {len(fired)} 件 = {len(fired)*30:,} バイト"
          f"（1 件/時 を要求していれば 0 バイト）。")
    print(f"  キーオフ時に累積ストレス カウンタ 4 バイトを 1 回更新して終わり。")

    print("\n\n■ 入庫時に吸い出されるもの ── 1 回だけ\n")
    print(f"  指紋 {len(fp.pack())} B（出荷時の自分）+ 記録の全量。")
    print(f"  整備側が見るのは「この個体は自分の床の何倍ずれたか」であって、")
    print(f"  「どの部品が悪いか」ではない。部位は名乗らない。")


if __name__ == "__main__":
    main()
