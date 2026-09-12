#!/usr/bin/env python3
"""Bytes against precision and quality, as curves (docs/357).

Every byte figure in this repo -- 2 B frame, 30 B record, 56 B baseline, an
8 to 64 KB allocation -- was one point I chose. An integrator cannot choose
from one point. This sweeps each and measures what the bytes buy:

  A  bus deviation field    bits -> capability reconstruction error
  B  event record floats    format -> reconstruction error
  C  shipping baseline      float32 vs float16 -> threshold translation shift
  D  NVM allocation         KB -> allowed alarm rate, two storage policies

Truth is the same 50-second-window capability computed in float64 with no
quantisation (docs/334). No new data.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line
from capability_threshold import d_of_c, t_refs
from nvm_budget_line import allowed, DRIVING

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "byte_quality_curve.tsv"
WIN = 500
BUS_MAX = 25.5
HELD_SHARE = 0.125                 # docs/213: events that persist to key-off
ALLOCS_KB = [4, 8, 16, 32, 64, 128, 256, 512, 1024]


def q_fixed(d, bits, vmax=BUS_MAX):
    step = vmax / (2 ** bits - 1)
    return np.clip(np.round(np.abs(d) / step) * step, 0, vmax) * np.sign(d)


def q_float16(d):
    return np.asarray(d, dtype=np.float16).astype(np.float64)


def q_int(d, step, bits):
    lim = step * (2 ** (bits - 1) - 1)
    return np.clip(np.round(d / step) * step, -lim, lim)


QUANT_A = [("4 bit", 4, 1 + 0.5, lambda d: q_fixed(d, 4)),
           ("6 bit", 6, 1 + 0.75, lambda d: q_fixed(d, 6)),
           ("8 bit（現行）", 8, 2, lambda d: q_fixed(d, 8)),
           ("10 bit", 10, 1 + 1.25, lambda d: q_fixed(d, 10)),
           ("12 bit", 12, 1 + 1.5, lambda d: q_fixed(d, 12)),
           ("16 bit", 16, 3, lambda d: q_fixed(d, 16)),
           ("float16", 16, 3, q_float16),
           ("float32", 32, 5, lambda d: d.astype(np.float32).astype(np.float64))]
QUANT_B = [("float32（現行）", 24, lambda d: d.astype(np.float32).astype(np.float64)),
           ("float16", 12, q_float16),
           ("int16 0.01 床", 12, lambda d: q_int(d, 0.01, 16)),
           ("int8 0.1 床", 6, lambda d: q_int(d, 0.1, 8))]


def per_device(dev):
    y, op, rid, _s, n1 = series(dev)
    fpm = np.arange(len(y)) < n1 // 2
    a, b, g = line(y[fpm], op[fpm])
    if g <= 0:
        return None
    op_lo, op_hi = float(op[fpm].min()), float(op[fpm].max())
    inrange = (op >= op_lo) & (op <= op_hi)
    d = (y - (a * op + b)) / g
    runs = sorted(set(rid.tolist()))
    lo = max(op[rid == r].min() for r in runs)
    hi = min(op[rid == r].max() for r in runs)
    t_ref = float(np.median(op[(op >= lo) & (op <= hi)]))
    base = a * t_ref + b

    def cap(dq, aa=a, bb=b, gg=g):
        base_q = aa * t_ref + bb
        out = []
        for i in range(0, len(y) - WIN, WIN):
            s = slice(i, i + WIN)
            m = inrange[s]
            if m.sum() < WIN // 4:
                continue
            ron = base_q + float(np.median(dq[s][m])) * gg
            out.append(np.sqrt(base_q / ron) if ron > 0 else np.nan)
        return np.asarray(out)

    truth = cap(d)
    return dict(d=d, cap=cap, truth=truth, a=a, b=b, g=g, t_ref=t_ref, base=base)


def main() -> None:
    devs = {f"Test_{k}": per_device(k) for k in mos.DEVICES}
    devs = {k: v for k, v in devs.items() if v}
    rows = []

    print("A. バスフレームの逸脱フィールド — ビット数と復元誤差\n")
    print(f"{'形式':<14}{'フレーム B':>10}{'誤差 中央値':>12}{'誤差 最大':>11}{'飽和':>8}")
    a_med = {}
    for name, bits, fbytes, q in QUANT_A:
        errs, sat = [], []
        for u in devs.values():
            dq = q(u["d"])
            errs += list(np.abs(u["cap"](dq) - u["truth"]))
            sat.append(float((np.abs(dq) >= BUS_MAX - 1e-9).mean()) if "bit" in name else 0.0)
        med, mx = float(np.nanmedian(errs)), float(np.nanmax(errs))
        a_med[name] = med
        rows.append(("A", name, fbytes, med, mx, float(np.mean(sat))))
        print(f"{name:<14}{fbytes:>10.2f}{med:>12.4f}{mx:>11.4f}{np.mean(sat):>8.1%}")

    print("\nB. 事象記録の実数 — 形式と復元誤差\n")
    print(f"{'形式':<16}{'6 実数 B':>9}{'記録 B':>8}{'誤差 中央値':>12}{'誤差 最大':>11}")
    b_med = {}
    for name, fb, q in QUANT_B:
        errs = []
        for u in devs.values():
            errs += list(np.abs(u["cap"](q(u["d"])) - u["truth"]))
        med, mx = float(np.nanmedian(errs)), float(np.nanmax(errs))
        b_med[name] = med
        rows.append(("B", name, fb + 6, med, mx, 0.0))
        print(f"{name:<16}{fb:>9}{fb + 6:>8}{med:>12.4f}{mx:>11.4f}")

    print("\nC. 出荷時基準値 — float16 に丸めたときの閾値の翻訳\n")
    print(f"{'素子':<9}{'d(0.95) f32':>12}{'d(0.95) f16':>12}{'差 [床]':>9}{'能力の差 中央値':>14}")
    c_shift = {}
    tr = t_refs()
    for name, u in devs.items():
        a16, b16, g16 = (float(np.float16(u["a"])), float(np.float16(u["b"])),
                         float(np.float16(u["g"])))
        S32 = (u["a"] * u["t_ref"] + u["b"]) / u["g"]
        S16 = (a16 * u["t_ref"] + b16) / g16
        d32, d16 = d_of_c(S32, 0.95), d_of_c(S16, 0.95)
        c16 = u["cap"](u["d"], a16, b16, g16)
        cd = float(np.nanmedian(np.abs(c16 - u["truth"])))
        c_shift[name] = abs(d16 - d32)
        rows.append(("C", name, 28, abs(d16 - d32), cd, 0.0))
        print(f"{name:<9}{d32:>12.4f}{d16:>12.4f}{abs(d16 - d32):>9.4f}{cd:>14.5f}")

    print("\nD. 不揮発の割り当て — 許せる誤検知率（件/時）\n")
    lo, hi = min(DRIVING.values()), max(DRIVING.values())
    print(f"{'割り当て':<10}{'全件追記 366h':>13}{'全件追記 127h':>13}{'続いた事象のみ 366h':>18}{'同 127h':>10}")
    d_all = {}
    for kb in ALLOCS_KB:
        r_hi, r_lo = allowed(kb, hi), allowed(kb, lo)
        h_hi, h_lo = r_hi / HELD_SHARE, r_lo / HELD_SHARE
        d_all[kb] = (r_hi, h_hi)
        rows.append(("D", f"{kb} KB", kb * 1024, r_hi, r_lo, h_hi))
        print(f"{kb:>6} KB  {r_hi:>13.1f}{r_lo:>13.1f}{h_hi:>18.1f}{h_lo:>10.1f}")

    print("\n=== 事前登録した予想 ===")
    k1 = a_med["8 bit（現行）"] <= 0.005 and (a_med["8 bit（現行）"] - a_med["12 bit"]) < 0.002
    print(f"  K1 8 bit 中央値 <= 0.005 かつ 12 bit の改善 < 0.002 : "
          f"{a_med['8 bit（現行）']:.4f}, 改善 {a_med['8 bit（現行）'] - a_med['12 bit']:.4f} -> "
          f"{'PASS' if k1 else 'FAIL'}")
    k2 = a_med["4 bit"] > 0.02
    print(f"  K2 4 bit 中央値 > 0.02                          : {a_med['4 bit']:.4f} -> "
          f"{'PASS' if k2 else 'FAIL'}")
    k3 = abs(b_med["float16"] - b_med["float32（現行）"]) < 0.002
    print(f"  K3 記録 float16 と float32 の差 < 0.002          : "
          f"{abs(b_med['float16'] - b_med['float32（現行）']):.5f} -> {'PASS' if k3 else 'FAIL'}")
    k4 = max(c_shift.values()) < 0.05
    print(f"  K4 基準値 float16 で d(0.95) の変化 < 0.05 床    : 最大 {max(c_shift.values()):.4f} -> "
          f"{'PASS' if k4 else 'FAIL'}")
    k5 = d_all[128][0] >= 10 and d_all[128][1] >= 80
    print(f"  K5 128 KB・366h: 全件 >= 10, 続いた事象のみ >= 80  : "
          f"{d_all[128][0]:.1f}, {d_all[128][1]:.1f} -> {'PASS' if k5 else 'FAIL'}")

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["axis", "name", "bytes", "v1", "v2", "v3"])
        for r in rows:
            w.writerow(r)
    print(f"\n{OUT.relative_to(ROOT)} に書いた")


if __name__ == "__main__":
    main()
