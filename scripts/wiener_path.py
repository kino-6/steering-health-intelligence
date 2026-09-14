#!/usr/bin/env python3
"""Random-drift Wiener path model (Lu & Meeker 1993; docs/372).

    X_i(t) = mu_i t + sigma_B B(t),   mu_i ~ lognormal,   failure at X = D

No curvature to identify: a slope per unit, the slope's spread across units,
a diffusion for the healthy wander, and an inverse-Gaussian time to failure.
Two groups, never pooled: A, the six stepped devices on the deviation series
over conducting hours; B, the five continuous tests on transient dR/R0 over
aging time.
"""

from __future__ import annotations

import csv
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line
from lifetime_simulation import read_epoch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "wiener_path.tsv"
POP = ROOT / "data" / "population.tsv"
CONT = ROOT / "data" / "continuous_tests_v2.tsv"
WIN_PER_H, ENROL, TARGET = 720, 720, 2.7
NOISE_W = (1.0 / 3.0) / np.sqrt(50)
N_UNITS, MAX_H, SEED = 1000, 200.0, 372


def conducting_hours(dev):
    hrs, rid = read_epoch(dev)
    dt = np.diff(hrs, prepend=hrs[0]); dt[dt < 0] = 0; dt[dt > 1 / 60] = 0
    return np.cumsum(dt)


def group_a():
    rows = []
    for dev in mos.DEVICES:
        y, op, rid, _s, n1 = series(dev)
        t = conducting_hours(dev)
        if len(t) != len(y):
            continue
        fit = np.arange(len(y)) < n1 // 2
        a, b, g = line(y[fit], op[fit])
        t_ref = float(np.median(op[fit])); S = (a * t_ref + b) / g
        x = (y - (a * op + b)) / g                      # deviation, 3-sigma units
        D = S * 0.25                                    # C = 0.894
        late = rid >= 5
        # slope over the degrading stretch, diffusion from the healthy stretch
        mu = float(np.polyfit(t[late], x[late], 1)[0])
        h = rid <= 4
        xh, th = x[h], t[h]
        w = 50
        m = np.convolve(xh, np.ones(w) / w, mode="valid"); tm = th[w - 1:]
        dm, dt = np.diff(m), np.diff(tm); ok = dt > 0
        sig_b = float(np.sqrt(np.var(dm[ok]) / np.mean(dt[ok]))) if ok.any() else float("nan")
        over = np.flatnonzero(np.convolve(x, np.ones(w) / w, mode="same") >= D)
        t_fail = float(t[over[0]]) if len(over) else float("nan")
        healthy_h = float(t[h].max())
        rows.append(dict(dev=f"Test_{dev}", mu=mu, sig_b=sig_b, D=D, t_fail=t_fail, healthy_h=healthy_h, S=S, t0=float(t[late].min())))
    return rows


def group_b():
    """Slope of dR/R0 over the second half before death, from the v2 series
    recomputed here (same definition as docs/370)."""
    import scipy.io as sio
    rows = []
    z = zipfile.ZipFile(mos.ZIP)
    for test in (35, 36, 37, 38, 41):
        name = [n for n in z.namelist() if re.search(rf"Test_{test}_run_1\.mat$", n)][0]
        p = mos.CACHE / name
        if not p.exists():
            z.extract(name, mos.CACHE)
        m = sio.loadmat(p, squeeze_me=True, struct_as_record=False)["measurement"]
        tr = np.ravel(m.transient); t = np.array([float(x.timeEpoch) for x in tr]); t = (t - t.min()) * 24
        R, I = [], []
        for x in tr:
            i = np.asarray(x.timeDomain.drainCurrent, float); v = np.asarray(x.timeDomain.drainSourceVoltage, float)
            g = np.asarray(x.timeDomain.gateSourceVoltage, float); on = g > 15.0
            if on.sum() < 20 or not np.isfinite(i[on]).any():
                R.append(np.nan); I.append(np.nan); continue
            R.append(float(np.nanmedian(v[on] / i[on]))); I.append(float(np.nanmedian(i[on])))
        R, I = np.array(R), np.array(I); ok = np.isfinite(R) & np.isfinite(I); R, I, t = R[ok], I[ok], t[ok]
        h = max(50, len(R) // 10); R0, I0 = float(np.median(R[:h])), float(np.median(I[:h]))
        dead = np.flatnonzero(I < 0.2 * I0); end = int(dead[0]) if len(dead) else len(R)
        x = R[:end] / R0 - 1.0; tt = t[:end]
        late = np.arange(end) >= end // 2
        mu = float(np.polyfit(tt[late], x[late], 1)[0])
        m = np.convolve(x[:h], np.ones(50) / 50, mode="valid"); tm = tt[49:h]
        dm, dt = np.diff(m), np.diff(tm); okd = dt > 0
        sig_b = float(np.sqrt(np.var(dm[okd]) / np.mean(dt[okd]))) if okd.any() else float("nan")
        over = np.flatnonzero(np.convolve(x, np.ones(50) / 50, mode="same") >= 0.08)
        rows.append(dict(dev=f"Test_{test}", mu=mu, sig_b=sig_b, D=0.08, t_fail=float(tt[over[0]]) if len(over) else float("nan"),
                         healthy_h=float(tt[h]), S=float("nan"), t0=float(tt[end // 2]), death=float(tt[-1])))
    return rows


def ig_band(mu, sig_b, D, t0):
    """10-90 percent band of the inverse-Gaussian first-passage time, shifted by t0."""
    if not (mu > 0 and sig_b > 0):
        return float("nan"), float("nan")
    lam = D ** 2 / sig_b ** 2; mean = D / mu
    dist = stats.invgauss(mean / lam, scale=lam)
    return t0 + dist.ppf(0.1), t0 + dist.ppf(0.9)


def main() -> None:
    A, B = group_a(), group_b()
    out = []
    for label, rows in (("A: 7 run の 6 素子（逸脱、通電時間）", A), ("B: 連続試験 5 本（ΔR/R0、aging time）", B)):
        print(f"\n{label}")
        print(f"{'個体':<9}{'μ [/h]':>10}{'σ_B [/√h]':>11}{'D':>8}{'故障 [h]':>9}{'IG 10%':>8}{'IG 90%':>8}{'含む':>5}")
        for r in rows:
            lo, hi = ig_band(r["mu"], r["sig_b"], r["D"], r["t0"])
            inside = (lo <= r["t_fail"] <= hi) if np.isfinite(r["t_fail"]) and np.isfinite(lo) else False
            r["ig_lo"], r["ig_hi"], r["inside"] = lo, hi, inside
            print(f"{r['dev']:<9}{r['mu']:>10.4f}{r['sig_b']:>11.4f}{r['D']:>8.3f}{r['t_fail']:>9.2f}{lo:>8.2f}{hi:>8.2f}{'○' if inside else '×':>5}")
            out.append((label[0], r["dev"], r["mu"], r["sig_b"], r["D"], r["t_fail"], lo, hi, int(inside)))
        mus = np.array([r["mu"] for r in rows if r["mu"] > 0])
        if len(mus) >= 2:
            s = float(np.log(mus).std(ddof=1))
            print(f"  μ > 0 の個体 {len(mus)}/{len(rows)}、log μ の標準偏差 s = {s:.2f}、最大/最小 = {mus.max() / mus.min():.1f}")

    print("\n=== 事前登録した予想 ===")
    for label, rows in (("A", A), ("B", B)):
        mus = np.array([r["mu"] for r in rows if r["mu"] > 0])
        s = float(np.log(mus).std(ddof=1)) if len(mus) >= 2 else float("nan")
        print(f"  W1 組 {label}: log μ の s <= 0.8         : {s:.2f} -> {'PASS' if s <= 0.8 else 'FAIL'}")
    n_in = sum(1 for r in A if r["inside"])
    print(f"  W2 組 A: 逆ガウスの 10〜90% が故障時刻を含む >= 4/6 : {n_in}/6 -> {'PASS' if n_in >= 4 else 'FAIL'}")

    # ---- population from group A
    rng = np.random.default_rng(SEED)
    pop = []
    with POP.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            pop.append((float(r["sigma"]), float(r["S"])))
    mus = np.array([r["mu"] for r in A if r["mu"] > 0]); lm, ls = np.log(mus).mean(), np.log(mus).std(ddof=1)
    sig_b = float(np.nanmedian([r["sig_b"] for r in A]))
    healthy_h = float(np.median([r["healthy_h"] for r in A]))
    q = min(TARGET / WIN_PER_H, 1.0 - 1.0 / ENROL)
    det, fa = [], []
    for i in range(N_UNITS):
        sigma, S = pop[rng.integers(len(pop))]
        degrading = i % 2 == 1
        mu = float(np.exp(rng.normal(lm, ls)))
        D = S * 0.25
        if degrading:
            t0 = float(rng.uniform(0.5, healthy_h)); t_fail = t0 + D / mu; run_h = min(t_fail + 1.0, MAX_H)
        else:
            t0, t_fail, run_h = float("nan"), float("nan"), healthy_h
        n_run = int(run_h * WIN_PER_H); n = ENROL + n_run
        dt_w = 1.0 / WIN_PER_H
        w = np.cumsum(rng.normal(0, sig_b * np.sqrt(dt_w), n)) + rng.normal(0, NOISE_W, n)
        t_h = (np.arange(n) - ENROL) / WIN_PER_H
        if degrading:
            w = w + mu * np.clip(t_h - t0, 0, None)
        thr = float(np.quantile(np.abs(w[:ENROL]), 1 - q))
        fired = np.abs(w[ENROL:]) > thr
        if degrading:
            idx = np.flatnonzero(fired); t_alarm = idx[0] / WIN_PER_H if len(idx) else float("inf")
            det.append(t_alarm < t_fail <= MAX_H)
        else:
            fa.append(fired.sum() / run_h)
    det, fa = np.array(det), np.array(fa)
    print(f"\n組 A の母数で 1,000 個体（σ_B = {sig_b:.4f}、健全期 {healthy_h:.1f} h、log μ: m = {lm:.2f}, s = {ls:.2f}）")
    print(f"  W3 故障前に警報 >= 90%           : {det.mean():.1%} -> {'PASS' if det.mean() >= 0.9 else 'FAIL'}")
    print(f"  W4 健全の誤検知 中央値 <= 5.4/h   : {np.median(fa):.2f} -> {'PASS' if np.median(fa) <= 2 * TARGET else 'FAIL'}"
          f"   (10% {np.percentile(fa, 10):.2f}, 90% {np.percentile(fa, 90):.2f})")
    print("\n何もしない基準: 指数は同定できず（docs/366, 368, 371）。直線を置いた仮想（docs/344）は検知 95〜100%、誤検知 12〜39 件/時")
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["group", "unit", "mu", "sigma_b", "D", "t_fail", "ig_lo", "ig_hi", "inside"])
        for r in out:
            w.writerow(r)
        w.writerow(["pop", "summary", lm, ls, sig_b, det.mean(), np.median(fa), healthy_h, ""])
    print(f"\n{OUT.relative_to(ROOT)} に書いた")


if __name__ == "__main__":
    main()
