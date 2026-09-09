"""How much of the healthy trend do siblings share (docs/351)?

The answer "detection works where same-kind channels exist" rests on two
results that do not overlap: eight of eight on injected inverter faults, and
two to five of six on real degradation with no sibling available. What decides
whether the sibling difference carries over is how much of the healthy trend
the siblings hold in common.

Part one measures that fraction on the inverter, which has three half-bridge
temperatures and two phase currents. Part two sweeps it in a simulated module
and finds where the difference starts working.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from demo_recorder import as_dicts
from inverter_recorder import ZIP, BASE, read
from virtual_module import measured_constants, ENROL, N_SAMP, FAST, HOUR, SEED

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "shared_drift.tsv"
SMOOTH = 500
SHARE = [0.0, 0.25, 0.5, 0.75, 1.0]
RATE = 9.6
N_UNITS = 200
ROBUST = 3.0 * 1.4826


def trend(x, w=SMOOTH):
    return np.convolve(x, np.ones(w) / w, mode="valid")


def shared_fraction(group, vals, ops):
    """Fraction of each channel's trend variance explained by the common part."""
    ts = []
    for c in group:
        y, o = vals[c], ops[c]
        a, b = np.polyfit(o, y, 1)
        r = (y - (a * o + b))
        g = float(ROBUST * np.median(np.abs(r - np.median(r))))
        ts.append(trend(r / max(g, 1e-9)))
    n = min(len(t) for t in ts)
    T = np.vstack([t[:n] for t in ts])
    common = np.median(T, axis=0)
    out = []
    for i in range(len(group)):
        v = float(np.var(T[i]))
        res = float(np.var(T[i] - common))
        out.append(max(0.0, 1 - res / v) if v > 0 else float("nan"))
    return out, T.shape[1]


def simulate(rng, drift, s, n=N_UNITS):
    """Three siblings sharing fraction s of the trend; channel 0 degrades."""
    run_len = N_SAMP - ENROL
    step = drift / np.sqrt(run_len)
    det = np.zeros(n, bool); fa = np.zeros(n)
    det0 = np.zeros(n, bool); fa0 = np.zeros(n)
    for u in range(n):
        common = np.cumsum(rng.normal(0, step, N_SAMP))
        ch = []
        for k in range(3):
            own = np.cumsum(rng.normal(0, step, N_SAMP))
            t = s * common + (1 - s) * own
            ch.append(t + rng.normal(0, 1.0, N_SAMP))
        deg = (u % 2 == 1)
        if deg:
            o = int(rng.uniform(ENROL + 6000, N_SAMP - 18000))
            ramp = np.zeros(N_SAMP)
            ramp[o:] = np.linspace(0, drift * RATE, N_SAMP - o)
            ch[0] = ch[0] + ramp
        raw = ch[0]
        diff = ch[0] - np.median(np.vstack(ch[1:]), axis=0)
        for series, D, F in ((raw, det0, fa0), (diff, det, fa)):
            k = ENROL // FAST
            w = np.abs(series[:ENROL][: k * FAST].reshape(k, FAST).mean(axis=1))
            q = max(1.0 / (HOUR / FAST), 1.0 / k)
            thr = float(np.quantile(w, 1 - q))
            r = series[ENROL:]
            m = len(r) // FAST
            ww = np.abs(r[: m * FAST].reshape(m, FAST).mean(axis=1))
            hit = ww > thr
            D[u] = bool(hit.any()); F[u] = hit.sum() / (m * FAST / HOUR)
    odd = np.arange(n) % 2 == 1
    return (float(det[odd].mean()), float(np.median(fa[~odd])),
            float(det0[odd].mean()), float(np.median(fa0[~odd])))


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    names = [n for n in z.namelist() if n.startswith(BASE) and n.endswith(".txt")]
    normal = read(z, next(n for n in names if "normal_operation" in n))
    vals, ops = as_dicts(normal)

    print("第 1 部 実測: 同種チャネルで共有される傾向の割合\n")
    rows = []
    for label, grp in (("半ブリッジ温度", ["T1", "T2", "T3"]), ("相電流", ["Ia", "Ib"])):
        fr, npts = shared_fraction(grp, vals, ops)
        print(f"  {label}（{','.join(grp)}、傾向 {npts:,} 点）")
        for c, f in zip(grp, fr):
            print(f"    {c:<4} 共有される割合 {f:.1%}")
        print(f"    中央値 {np.median(fr):.1%}\n")
        rows.append(("measured", label, float(np.median(fr)), npts, 0.0, 0.0))
    s_meas = rows[0][2]

    print("第 2 部 仮想: 共有の割合を振る（劣化速度は実素子の実測 D = 9.6）\n")
    print(f"{'共有 s':>8} {'差分あり 検知':>13} {'差分あり 誤検知':>16} "
          f"{'差分なし 検知':>13} {'差分なし 誤検知':>16}")
    print("-" * 74)
    best = None
    for s in SHARE:
        rng = np.random.default_rng(SEED + int(s * 100))
        a, gg, drift = measured_constants()
        d1, f1, d0, f0 = simulate(rng, drift, s)
        ok = d1 >= 0.90 and f1 <= 1.0
        if ok and best is None:
            best = s
        print(f"{s:>8.2f} {d1:>12.1%} {f1:>14.1f}/h {d0:>12.1%} {f0:>14.1f}/h"
              f"{'   満たす' if ok else ''}")
        rows.append(("sim", f"s={s}", d1, f1, d0, f0))

    print(f"\n=== 事前登録した判定 ===")
    print(f"  P1 実測の共有される割合（半ブリッジ温度）: **{s_meas:.1%}**")
    if best is None:
        print(f"  P2 条件を満たす s: **無い**")
        print(f"  P3 → **差分では届かない。**いまの答えを弱める")
    else:
        print(f"  P2 条件を満たす最小の s: **{best:.2f}**")
        if s_meas >= best:
            print(f"  P3 実測 {s_meas:.1%} は最小 {best:.0%} 以上 "
                  f"→ **本物の劣化にも効く見込みがある**")
        else:
            print(f"  P3 実測 {s_meas:.1%} は最小 {best:.0%} 未満 "
                  f"→ **効かない。いまの答えを弱める**")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("kind\tlabel\tv1\tv2\tv3\tv4\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
