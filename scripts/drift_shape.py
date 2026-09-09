"""What shape is the real drift (docs/347)?

docs/346 found a method that gives 1.5 false alarms per hour in simulation and
forty thousand on the real devices. The random walk is wrong; this measures how,
before anyone touches the model.

Three descriptive measurements, no pass criterion. The same three run on the
simulation's healthy units so the two sit on one ruler.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line
from virtual_module import measured_constants, make_units, ENROL, SEED

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "drift_shape.tsv"
NS = [10, 30, 100, 300, 1000, 3000]
SMOOTH = 500     # the drift lives in the running mean, not in the raw samples


def smooth(x, w=SMOOTH):
    """The first run measured alpha and rho on the raw residual and got 0.00
    and -0.445 for both the real and the simulated series. Both are what one
    gets from white noise: the per-sample noise is one floor and the whole
    drift is 0.35 floors, so it drowns the thing being measured, and
    differencing white noise gives rho of -0.5 by construction. The drift is
    the wander of the running mean, so that is what gets measured."""
    if len(x) < w:
        return x
    return np.convolve(x, np.ones(w) / w, mode="valid")


def alpha(x):
    """Slope of log variance of the n-sample change against log n."""
    ns, vs = [], []
    for n in NS:
        if len(x) < 4 * n:
            continue
        d = x[n:] - x[:-n]
        ns.append(n); vs.append(float(np.var(d)))
    if len(ns) < 3:
        return float("nan"), []
    a = np.polyfit(np.log(ns), np.log(vs), 1)[0]
    return float(a), list(zip(ns, vs))


def rho1(x):
    d = np.diff(x)
    if len(d) < 3 or d.std() == 0:
        return float("nan")
    return float(np.corrcoef(d[:-1], d[1:])[0, 1])


def main() -> None:
    print("健全区間の残差（移動平均 500）の形。α≈1 はウォーク、α≈0 は定常、α≈2 は傾向\n")
    print(f"{'素子':>8} {'α':>7} {'ρ₁':>8} {'残差×動作点':>13} {'残差×動作点²':>14}")
    print("-" * 56)
    rows, als, rhos = [], [], []
    for dev in mos.DEVICES:
        y, op, rid, _s, n1 = series(dev)
        fp = np.arange(len(y)) < n1 // 2
        a, b, g = line(y[fp], op[fp])
        if g <= 0:
            continue
        h = rid <= 4
        r = (y[h] - (a * op[h] + b)) / g
        o = op[h]
        rs = smooth(r)
        al, _ = alpha(rs)
        rr = rho1(rs)
        c1 = float(np.corrcoef(r, o)[0, 1])
        c2 = float(np.corrcoef(r, o ** 2)[0, 1])
        print(f"{dev:>8} {al:>7.2f} {rr:>8.3f} {c1:>13.3f} {c2:>14.3f}")
        als.append(al); rhos.append(rr)
        rows.append(("real", dev, al, rr, c1, c2))

    print(f"\n  実素子 中央値: α = {np.median(als):.2f}、ρ₁ = {np.median(rhos):.3f}")

    # the simulation, on the same ruler
    aa, gg, drift = measured_constants()
    rng = np.random.default_rng(SEED)
    d, base, degrading, _o = make_units(rng, drift, 9.6)
    sa, sr = [], []
    for i in np.where(~degrading)[0][:20]:
        x = smooth(d[i, :ENROL])
        al, _ = alpha(x)
        sa.append(al); sr.append(rho1(x))
        rows.append(("sim", int(i), al, sr[-1], float("nan"), float("nan")))
    print(f"  仮想モジュール 中央値: α = {np.median(sa):.2f}、ρ₁ = {np.median(sr):.3f}")

    ar, arho = float(np.median(als)), float(np.median(rhos))
    print(f"\n=== 事前に固定した読み方 ===")
    if 0.8 <= ar <= 1.2:
        print(f"  α = {ar:.2f} は 0.8〜1.2。**ウォークの模型は妥当。違いは別のところにある**")
    elif ar > 1.2:
        print(f"  α = {ar:.2f} は 1.2 超。**健全区間にも傾向がある。"
              f"「漂流」と呼んでいたものは緩やかな傾向である**")
    else:
        print(f"  α = {ar:.2f} は 0.8 未満。**定常に近い。ウォークは実物より暴れている**")
    if arho < -0.05:
        print(f"  ρ₁ = {arho:.3f} は負。**戻る漂流。採り直しが効きにくい理由になりうる**")
    else:
        print(f"  ρ₁ = {arho:.3f}。**独立増分に近い**")
    c1m = float(np.median([r[4] for r in rows if r[0] == "real"]))
    c2m = float(np.median([r[5] for r in rows if r[0] == "real"]))
    print(f"  残差×動作点 {c1m:+.3f}、残差×動作点² {c2m:+.3f}"
          + ("  → **温度で説明できる分が残っている**"
             if max(abs(c1m), abs(c2m)) > 0.2 else "  → 直線で引き切れている"))

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("kind\tunit\talpha\trho1\tcorr_op\tcorr_op2\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
