#!/usr/bin/env python3
"""How many bits must an ECU resolve for the recorder to work? (docs/260 -> docs/261)

Executes the protocol pre-registered in docs/260 against KAIST PMSM and NASA
MOSFET, both already inventoried. No new acquisition.

docs/225 left the ECU's own noise floor blank and called it unfillable without
data that does not exist. The user pointed out, more than once, that this is
the wrong question. "What is the floor" needs data. "What floor would be good
enough" does not -- the precursor sizes are already measured, so the resolution
they demand can be computed and the answer is a design requirement.

    D  quantize the phase currents to B bits over a full scale, recompute the
       balance headroom, and find the smallest B whose floor stays within 1.5x
       of the laboratory floor
    P  whether persistence buys sensitivity on component-internal signals as
       it does at vehicle level (docs/253)

Criteria: D1 the required resolution is 12 bits or fewer; D2 that floor in
amps; D3 whether a precursor of 20-300 laboratory floors still clears ten
quantized floors; P1 the longest event needs at most half the amplitude of
the shortest.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import internal_signal_injection as isi
from capability_second_mechanism import headroom
import pmsm_measured_signature as sig

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "no_data_decisions.tsv"

BITS = [8, 9, 10, 11, 12, 14, 16]          # pre-registered in docs/260
BITS_POST = [4, 5, 6, 7]                   # post-hoc: the grid above bottomed out
FS_MULT = [1.5, 2.0, 3.0]          # full scale as a multiple of that file's peak
TOLERANCE = 1.5                    # quantized floor within this many lab floors
SUB = isi.SUB
ROBUST = isi.ROBUST
DURS = [1, 2, 5, 10, 20, 40]
FA_PER_HOUR, HOUR_SAMPLES = 1.0, 36000
TARGET, AMPS = 0.90, np.arange(0.5, 60.5, 0.5)   # pre-registered
AMPS_POST = np.arange(0.02, 0.52, 0.02)          # post-hoc: the grid above bottomed out


def floor_of(x: np.ndarray) -> float:
    return float(ROBUST * np.median(np.abs(x - np.median(x))))


def headroom_series(phases, f0):
    n = len(phases[0]) // SUB
    return np.array([headroom([p[i * n:(i + 1) * n] for p in phases], f0)
                     for i in range(SUB)])


def quantize(x: np.ndarray, fs: float, bits: int) -> np.ndarray:
    """Mid-tread uniform quantizer over +-fs, as an ECU's ADC would."""
    q = 2 * fs / (2 ** bits)
    return np.clip(np.round(x / q) * q, -fs, fs)


def part_d(bits_grid) -> list[dict]:
    """All three machines' healthy current records, not just the 1.0 kW one.

    docs/203 showed a conclusion from one machine did not replicate on another,
    so a resolution requirement derived from a single machine would not be
    worth stating.
    """
    rows = []
    for zp in sorted(sig.ZIP.parent.glob("*.zip")):
        z = zipfile.ZipFile(zp)
        names = sorted(n for n in z.namelist() if "current" in n and "_0_00_" in n)
        for name in names:
            p = sig.CACHE / name
            if not p.exists():
                z.extract(name, sig.CACHE)
            ph = sig.load_phases(p)
            f0 = sig.find_f0(ph)
            peak = float(max(np.max(np.abs(a)) for a in ph))
            lab = headroom_series(ph, f0)
            g_lab = floor_of(lab)
            if g_lab <= 0:
                continue
            for mult in FS_MULT:
                fs = peak * mult
                for b in bits_grid:
                    qh = headroom_series([quantize(a, fs, b) for a in ph], f0)
                    rows.append({"file": f"{zp.stem}/{Path(name).stem}", "peak_A": peak,
                                 "fs_mult": mult, "bits": b, "lsb_A": 2 * fs / (2 ** b),
                                 "g_lab": g_lab, "g_q": floor_of(qh)})
    return rows


def part_p(amps=AMPS):
    series = isi.nasa_series() + isi.kaist_series()
    out = []
    for label, s in series:
        n = len(s)
        best = {}
        for W in DURS:
            if n < W * 20:
                continue
            k = n // W
            w = s[:k * W].reshape(k, W)
            g = floor_of(s)
            if g <= 0:
                continue
            cm, cx = np.abs(w.mean(axis=1)) / g, np.abs(w).max(axis=1) / g
            # one alarm per hour, converted to a per-window rate at this length
            fa = FA_PER_HOUR * W / HOUR_SAMPLES
            fa = max(fa, 1.0 / len(cm))          # never ask for a quantile outside the sample
            t_m, t_x = float(np.quantile(cm, 1 - fa)), float(np.quantile(cx, 1 - fa))
            # the pre-registration asks for a 90% detection rate, so every
            # window is a trial -- an earlier version tested only the first
            # window, which measures no rate at all
            hit = None
            for A in amps:
                y = w + A * g
                det = ((np.abs(y.mean(axis=1)) / g > t_m)
                       | (np.abs(y).max(axis=1) / g > t_x))
                if det.mean() >= TARGET:
                    hit = A
                    break
            best[W] = hit
        if best:
            out.append((label, best))
    return out


def main() -> None:
    rows = part_d(BITS)
    print(f"=== D  ECUは何ビット要るか ===")
    print(f"ファイル {len(set(r['file'] for r in rows))} 本、"
          f"相電流ピーク中央値 {np.median([r['peak_A'] for r in rows]):.2f} A\n")
    print(f"{'フルスケール':>12} {'ビット':>6} {'1LSB':>10} {'量子化後の床/実験室の床':>24} {'判定':>6}")
    print("-" * 64)
    need = {}
    for mult in FS_MULT:
        for b in BITS:
            sel = [r for r in rows if r["fs_mult"] == mult and r["bits"] == b]
            if not sel:
                continue
            ratio = float(np.median([r["g_q"] / r["g_lab"] for r in sel]))
            lsb = float(np.median([r["lsb_A"] for r in sel]))
            ok = ratio <= TOLERANCE
            if ok and mult not in need:
                need[mult] = (b, lsb, ratio)
            print(f"{'ピーク×' + str(mult):>12} {b:>6} {lsb:>9.4f}A {ratio:>23.2f} "
                  f"{'ok' if ok else '':>6}")
    print()
    for mult, (b, lsb, ratio) in sorted(need.items()):
        print(f"  フルスケール ピーク×{mult}: **{b}ビット** で足りる "
              f"(1LSB = {lsb*1000:.1f} mA、床は実験室の {ratio:.2f}倍)")
    print("\n--- 事後(事前登録の格子が底を打ったので追加) ---")
    post = part_d(BITS_POST)
    for mult in FS_MULT:
        for b in sorted(BITS_POST):
            sel = [r for r in post if r["fs_mult"] == mult and r["bits"] == b]
            if not sel:
                continue
            ratio = float(np.median([r["g_q"] / r["g_lab"] for r in sel]))
            lsb = float(np.median([r["lsb_A"] for r in sel]))
            print(f"{'ピーク×' + str(mult):>12} {b:>6} {lsb:>9.4f}A {ratio:>23.2f} "
                  f"{'ok' if ratio <= TOLERANCE else '':>6}")
    rows += post

    base = need.get(2.0)
    print(f"\n=== D1 12ビット以下か ===")
    if base:
        print(f"  必要 {base[0]} ビット  {'PASS' if base[0] <= 12 else 'FAIL'} (基準: 12以下)")
    else:
        print("  16ビットでも許容に入らない  FAIL")
    print(f"\n=== D3 前駆は量子化後の床の10倍を超えるか ===")
    if base:
        b, lsb, ratio = base
        print(f"  量子化後の床は実験室の床の {ratio:.2f}倍")
        print(f"  前駆は実験室の床の 20〜300倍 (docs/167)")
        print(f"  → 量子化後の床に対して {20/ratio:.1f}〜{300/ratio:.0f}倍  "
              f"{'PASS' if 20/ratio >= 10 else 'FAIL'} (基準: 10倍以上)")

    print(f"\n=== P  部品内部でも持続は感度を買うか ===")
    pr = part_p()
    pr_post = part_p(np.concatenate([AMPS_POST, AMPS]))
    print(f"{'系列':>26} " + "".join(f"{str(d):>7}" for d in DURS) + f"{'比':>8}")
    print("-" * 80)
    passed = tot = 0
    for label, best in pr:
        ks = sorted(best)
        cells = "".join(f"{(('%.1f' % best[d]) if best.get(d) else '-'):>7}" for d in DURS)
        lo, hi = best.get(ks[0]), best.get(ks[-1])
        if lo and hi:
            tot += 1
            r = lo / hi
            passed += hi <= lo / 2
            print(f"{label:>26} {cells} {r:>7.2f}倍")
        else:
            print(f"{label:>26} {cells} {'—':>8}")
    print(f"\n=== P1 最長が最短の半分以下 ===")
    print(f"  {passed}/{tot} 系列  {'PASS' if tot and passed > tot/2 else 'FAIL'} (基準: 過半)")

    print("\n--- 事後(事前登録の振幅格子が底 0.5 を打ったので細かくした) ---")
    print(f"{'系列':>26} " + "".join(f"{str(d):>7}" for d in DURS) + f"{'比':>8}")
    for label, best in pr_post:
        ks = sorted(best)
        cells = "".join(f"{(('%.2f' % best[d]) if best.get(d) else '-'):>7}" for d in DURS)
        lo, hi = best.get(ks[0]), best.get(ks[-1])
        r = f"{lo/hi:>7.2f}倍" if lo and hi else f"{'—':>8}"
        print(f"{label:>26} {cells} {r}")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with OUT_TSV.open("w") as fh:
        fh.write("kind\tfile_or_series\tfs_mult\tbits\tlsb_A\tfloor_lab\tfloor_quantized\n")
        for r in rows:
            fh.write(f"D\t{r['file']}\t{r['fs_mult']}\t{r['bits']}\t{r['lsb_A']:.6f}\t"
                     f"{r['g_lab']:.6g}\t{r['g_q']:.6g}\n")
        for label, best in pr:
            for d in DURS:
                fh.write(f"P\t{label}\t\t{d}\t\t\t{best.get(d)}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
