"""What the measured Ron rise does to output, on a defined circuit (docs/337).

docs/331 got 11 percent at failure from conduction loss alone, with no circuit
behind it. This defines one and puts the same measured Ron degradation through
it, with switching loss and the thermal path included.

Two constraints can limit the output and they do not have the same sensitivity
to Ron, which turns out to matter more than the loss split does:

    thermal      Tj = T_amb + (I^2 Ron k + P_sw) Rth <= Tj_max
    bus voltage  V_bus = I (R_motor + 2 Ron)      at stall, no back-EMF

Every parameter except the Ron degradation is chosen, and the ranges are in
docs/337. The Ron degradation is the six NASA devices, measured.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from assist_capability import capability

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "virtual_circuit.tsv"

V_BUS = 13.5          # V, 12 V system nominal
TJ_MAX, T_AMB = 150.0, 85.0
F_SW = [10e3, 20e3, 40e3]
I_DES = [20.0, 40.0, 60.0]
RTH = [1.0, 2.0, 4.0]
SW_SHARE = [0.0, 0.25, 0.50, 0.75]     # switching loss share at the design point
K_DUTY = 0.5          # conduction duty factor for one device in a leg
N_PATH = 2            # devices in series in the current path


def ron_ratio(dev):
    """Ron(t)/Ron(healthy) per run, from capability: C = sqrt(base/Ron)."""
    C, _t, _s = capability(dev)
    if C is None:
        return None
    return {r: 1.0 / (c * c) for r, c in C.items()}


def limits(ratio, rth, share, i_des, ron0):
    """Max current under each constraint, healthy and degraded."""
    a = (TJ_MAX - T_AMB) / rth                       # total loss budget, W
    p_cond0 = i_des ** 2 * ron0 * K_DUTY * N_PATH
    p_sw = p_cond0 * share / max(1e-9, 1 - share)    # fixed, independent of Ron
    r_motor = max(1e-4, V_BUS / i_des - N_PATH * ron0)

    def pair(rr):
        ron = ron0 * rr
        head = a - p_sw
        i_th = np.sqrt(max(head, 0.0) / (ron * K_DUTY * N_PATH)) if head > 0 else 0.0
        i_v = V_BUS / (r_motor + N_PATH * ron)
        return i_th, i_v

    th0, v0 = pair(1.0)
    th1, v1 = pair(ratio)
    return min(th0, v0), min(th1, v1), th0, v0, th1, v1


def main() -> None:
    ron0 = 0.05          # ohm, healthy on-resistance. Chosen; see docs/337
    print("測った R_on 劣化を、定義した回路に通す。出力＝出せる電流\n")
    rr = {d: ron_ratio(d) for d in mos.DEVICES}
    last = {d: max(v) for d, v in rr.items() if v}

    rows, by_share, exceed = [], {}, []
    for f, i_des, rth, share in itertools.product(F_SW, I_DES, RTH, SW_SHARE):
        drops, binds = [], []
        for dev, series in rr.items():
            if not series:
                continue
            ratio = series[last[dev]]
            o0, o1, th0, v0, th1, v1 = limits(ratio, rth, share, i_des, ron0)
            if o0 <= 0:
                continue
            drops.append(1.0 - o1 / o0)
            binds.append("熱" if th0 <= v0 else "電圧")
        if not drops:
            continue
        d = float(np.median(drops))
        b = max(set(binds), key=binds.count)
        by_share.setdefault(share, []).append(d)
        if d > 0.11:
            exceed.append((f / 1e3, i_des, rth, share, d, b))
        rows.append((f / 1e3, i_des, rth, share, d, b))

    print(f"{'スイッチング損の割合':>20} {'出力低下 中央値':>16} {'範囲':>18} {'条件数':>7}")
    for s in SW_SHARE:
        v = by_share.get(s, [])
        if v:
            print(f"{s:>19.0%} {np.median(v):>15.1%} "
                  f"{min(v):>8.1%}–{max(v):<8.1%} {len(v):>7}")

    print(f"\n拘束がどちらかの内訳")
    for b in ("熱", "電圧"):
        n = sum(1 for r in rows if r[5] == b)
        v = [r[4] for r in rows if r[5] == b]
        if v:
            print(f"  {b}が拘束  {n:>3}/{len(rows)} 条件   出力低下 中央値 {np.median(v):.1%}"
                  f"   範囲 {min(v):.1%}–{max(v):.1%}")

    print(f"\n=== 事前登録した予想 ===")
    z = by_share.get(0.0, [])
    w1 = z and abs(np.median(z) - 0.11) <= 0.02
    print(f"  W1 スイッチング損 0% で 11% を ±2 ポイント: "
          f"{np.median(z):.1%} → {'PASS' if w1 else 'FAIL'}")
    h = by_share.get(0.75, [])
    w2 = h and np.median(h) <= 0.055
    print(f"  W2 スイッチング損 75% で半分以下(5.5% 以下): "
          f"{np.median(h):.1%} → {'PASS' if w2 else 'FAIL'}")
    print(f"  W3 11% を超える条件: {len(exceed)}/{len(rows)}")
    for e in exceed[:6]:
        print(f"     f_sw {e[0]:.0f} kHz / I {e[1]:.0f} A / Rth {e[2]} K/W / "
              f"損失割合 {e[3]:.0%} → {e[4]:.1%} ({e[5]}が拘束)")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("f_sw_khz\ti_design_a\trth\tsw_share\toutput_drop\tbinding\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
