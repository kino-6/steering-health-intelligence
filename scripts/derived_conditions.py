#!/usr/bin/env python3
"""The virtual circuit again, with conditions derived from the premise
(docs/360) instead of placed.

docs/337 put the 12 V EPS power stage at Ron 50 mOhm and Rth 1 to 4 K/W.
Public datasheets for automotive MOSFETs give Ron 4 to 9 mOhm and a
junction-to-case resistance of 2 to 2.9 K/W alone, so half of the old Rth
grid was physically impossible and Ron was five to twelve times too high.
This sweeps the derived grid. The only measured input is still the six
devices' Ron degradation.
"""

from __future__ import annotations

import csv
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from virtual_circuit import ron_ratio, K_DUTY, N_PATH

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "derived_conditions.tsv"

# docs/360, SOURCES.md S15
V_BUS = [12.0, 14.0]            # ISO 16750-2 UB / UA
TJ_MAX = 175.0                  # datasheets
T_AMB = [85.0, 125.0]           # AEC-Q100 Grade 3 / Grade 1
RON0 = [0.004, 0.009]           # IAUC60N04S6N050H typ / IPB70P04P4-09 max
RTH = [3.0, 6.0, 12.0]          # between RthJC 2.9 and RthJA 35
I_DES = [20.0, 40.0, 60.0]      # up to the device's 60 A DC rating
SW_SHARE = [0.0, 0.25, 0.5, 0.75]


def limits(ratio, v_bus, t_amb, rth, share, i_des, ron0):
    a = (TJ_MAX - t_amb) / rth
    p_cond0 = i_des ** 2 * ron0 * K_DUTY * N_PATH
    p_sw = p_cond0 * share / max(1e-9, 1 - share)
    r_motor = v_bus / i_des - N_PATH * ron0
    if r_motor <= 0:
        return None

    def pair(rr):
        ron = ron0 * rr
        head = a - p_sw
        i_th = np.sqrt(max(head, 0.0) / (ron * K_DUTY * N_PATH)) if head > 0 else 0.0
        i_v = v_bus / (r_motor + N_PATH * ron)
        return i_th, i_v

    th0, v0 = pair(1.0)
    th1, v1 = pair(ratio)
    return min(th0, v0), min(th1, v1), th0, v0


def main() -> None:
    rr = {d: ron_ratio(d) for d in mos.DEVICES}
    rr = {d: v for d, v in rr.items() if v}
    last = {d: max(v) for d, v in rr.items()}
    rows, dropped = [], 0
    for v, ta, ron0, rth, ides, share in itertools.product(V_BUS, T_AMB, RON0, RTH, I_DES, SW_SHARE):
        drops, binds = [], []
        for dev, series in rr.items():
            out = limits(series[last[dev]], v, ta, rth, share, ides, ron0)
            if out is None or out[0] <= 0:
                continue
            o0, o1, th0, v0 = out
            drops.append(1.0 - o1 / o0)
            binds.append("熱" if th0 <= v0 else "電圧")
        if not drops:
            dropped += 1
            continue
        rows.append((v, ta, ron0 * 1e3, rth, ides, share, float(np.median(drops)),
                     max(set(binds), key=binds.count)))

    n = len(rows)
    print(f"導いた条件 {len(V_BUS)*len(T_AMB)*len(RON0)*len(RTH)*len(I_DES)*len(SW_SHARE)} 通り。"
          f"スイッチング損が熱の予算を使い切って落ちた {dropped}、残り {n}\n")
    for b in ("熱", "電圧"):
        v = [r[6] for r in rows if r[7] == b]
        if v:
            print(f"  {b}が拘束  {len(v):>3}/{n}   出力低下 中央値 {np.median(v):.1%}"
                  f"   範囲 {min(v):.1%}〜{max(v):.1%}")
    print("\nR_on 別、電圧拘束の出力低下")
    for ron in RON0:
        v = [r[6] for r in rows if r[7] == "電圧" and abs(r[2] - ron * 1e3) < 1e-9]
        if v:
            print(f"  {ron*1e3:.0f} mΩ: 中央値 {np.median(v):.2%}  範囲 {min(v):.2%}〜{max(v):.2%}  ({len(v)} 条件)")

    print("\n=== 事前登録した予想 ===")
    vv = [r[6] for r in rows if r[7] == "電圧"]
    g1 = bool(vv) and 0.005 <= min(vv) and max(vv) <= 0.025
    print(f"  G1 電圧拘束の低下が 0.5〜2.5%           : {min(vv):.2%}〜{max(vv):.2%} -> {'PASS' if g1 else 'FAIL'}")
    sub = [r for r in rows if r[3] == 12.0 and r[1] == 125.0]
    th = sum(1 for r in sub if r[7] == "熱")
    print(f"  G2 Rth 12・T_amb 125 で熱拘束 100%        : {th}/{len(sub)} -> {'PASS' if th == len(sub) else 'FAIL'}")
    sub = [r for r in rows if r[3] == 3.0 and r[1] == 85.0]
    th = sum(1 for r in sub if r[7] == "熱")
    print(f"  G3 Rth 3・T_amb 85 で熱拘束 0%            : {th}/{len(sub)} -> {'PASS' if th == 0 else 'FAIL'}")
    med = float(np.median([r[6] for r in rows]))
    print(f"  G4 全体の中央値が 2〜11%                : {med:.1%} -> {'PASS' if 0.02 <= med <= 0.11 else 'FAIL'}")
    print("\n何もしない基準（docs/338、R_on 50 mΩ・Rth 1〜4）: 熱 10.8% / 電圧 3.7%")

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["v_bus", "t_amb", "ron0_mohm", "rth", "i_design", "sw_share", "output_drop", "binding"])
        for r in rows:
            w.writerow(r)
    print(f"\n{OUT.relative_to(ROOT)} に書いた")


if __name__ == "__main__":
    main()
