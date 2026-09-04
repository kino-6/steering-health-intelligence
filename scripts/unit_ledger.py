"""One unit's data ledger, split by layer (docs/318).

The question is what a single ECU accumulates and what it puts out, told
separately for the non-volatile store and for the network, because they are
sized by different things: NVM by the retention period and the alarm rate,
the bus by the cycle time and by what the element is allowed to say.

Every byte count here is measured by packing a real struct, never by adding
up field widths on paper (docs/265). Volume is expressed per assist-active
hour, not per day: the axis is accumulated stress, and a parked car does not
advance it (docs/312).
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eps_health_recorder import ChannelFingerprint, Record, FORBIDDEN

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "unit_ledger.tsv"
CHANNELS = 8                    # docs/286: 3 half-bridge temps, 2 phase currents, +3
RETENTION_D = 397               # docs/227: 90th percentile of the UK MOT interval

# measured alarm rates, unit level, both sides OR-ed
RATES = [
    ("設計値", 1.0, "docs/225 の要求"),
    ("遅い側 傾き変化 実劣化", 18.0, "docs/317 で較正できた上限"),
    ("速い側 実インバータ", 23.6, "docs/286 の保留正常で実測"),
    ("個体単位 全チャネル", 281.2, "docs/294。登録が 17 倍足りない"),
]

# ------------------------------------------------------------------ the bus
# What may be broadcast cyclically is constrained by the seven refusals: the
# standardised destination is named "STR capability information" (docs/183)
# and "capability" is the first forbidden word. So the frame carries no
# capability value -- only whether this unit is currently able to speak about
# itself, and how far it is from its own shipping baseline in its own floors.
BUS_FMT = "<BB"                 # measured below


def bus_frame(state: int, deviation_floors: float) -> bytes:
    """2 bytes. state: bit0 declaring, bit1 fast fired, bit2 slow fired,
    bit3 held to key-off. deviation saturates at 25.5 floors, 0.1 per step."""
    d = max(0, min(255, round(deviation_floors * 10)))
    return struct.pack(BUS_FMT, state & 0x0F, d)


def main() -> None:
    fp_b = len(ChannelFingerprint("x", *([0.0] * 10), 0.0, True).pack())
    rec_b = len(Record(*([0.0] * 6), 0, 0, 0, 1).pack())
    bus_b = len(bus_frame(0b0001, 3.15))
    unit_fp = fp_b * CHANNELS

    print("=== 1 個体・不揮発(NVM) ===")
    print(f"  出荷時に一度だけ書く指紋   {fp_b} B/ch x {CHANNELS} ch = {unit_fp} B")
    print(f"  事象ごとに追記する記録     {rec_b} B/件")
    print(f"  累積ストレス カウンタ      {struct.calcsize('<I')} B。キーオフ時に 1 回だけ更新")
    print(f"\n  保持 {RETENTION_D} 日ぶんの追記量は、暦日ではなくアシスト稼働時間で決まる:")
    print(f"  {'誤報の水準':<24} {'件/時':>8} {'記録 100h':>11} {'500h':>9} {'2000h':>9}")
    rows = []
    for label, rate, src in RATES:
        v = [rate * h * rec_b for h in (100, 500, 2000)]
        f = lambda b: (f"{b/1024:.1f} KiB" if b < 1048576 else f"{b/1048576:.2f} MiB")
        print(f"  {label:<24} {rate:>8.1f} {f(v[0]):>11} {f(v[1]):>9} {f(v[2]):>9}")
        rows.append(("nvm", label, rate, *[int(x) for x in v], src))

    print("\n  不揮発への書き込み回数(消耗はバイト数ではなく回数で決まる):")
    print(f"  {'誤報の水準':<24} {'稼働 500 h':>12} {'2000 h':>12}")
    for label, rate, _ in RATES:
        print(f"  {label:<24} {rate*500:>12,.0f} {rate*2000:>12,.0f}")
    print(f"  {'キーオフの累積カウンタ':<24} {'1 回/走行':>12} {'1 回/走行':>12}")

    print("\n=== 1 個体・ネットワーク ===")
    print(f"  周期送信のフレーム         {bus_b} B。CAN の 8 B ペイロードに収まる")
    print("  検出器は 10 Hz で動くので、100 ms より速い周期は新しい値を運ばない")
    for hz, name in ((100, "10 ms 周期"), (10, "100 ms 周期")):
        per_h = bus_b * hz * 3600
        print(f"    {name:<20} {bus_b*hz:>6} B/s = {per_h/1048576:>6.2f} MiB/稼働時間"
              f"  ({RETENTION_D} 日ぶんは保存しない)")
        rows.append(("bus_cyclic", name, hz, bus_b * hz, per_h, 0, "周期"))
    print(f"\n  入庫時の吸い出し(1 回)     指紋 {unit_fp} B + 記録の全量")
    for label, rate, _ in RATES:
        b = unit_fp + rate * 500 * rec_b
        print(f"    {label:<24} {b/1024:>8.1f} KiB  (稼働 500 h ぶん)")
        rows.append(("diag_readout", label, rate, int(b), 0, 0, "500h"))

    print("\n=== 禁止語の点検 ===")
    print(f"  周期フレームの中身: 宣言可否・どちらの検出器・キーオフまでの持続・"
          f"自分の床いくつぶん離れたか")
    print(f"  {'capability' in FORBIDDEN and 'capability は禁止語。能力値は乗せない' or ''}")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("layer\tcase\trate_or_hz\tv1\tv2\tv3\tsource\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
