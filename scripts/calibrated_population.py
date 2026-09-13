#!/usr/bin/env python3
"""Fit NASA's degradation model to the six devices and grow a virtual
population from the fitted spread (docs/365).

The earlier virtual module made degradation up as a straight ramp. The
authors of the NASA set report that dR_DS(on) grows exponentially from a
device-specific onset (Celaya et al., RAMS 2012), so that is the form fitted
here, on conducting hours read from the data's own timestamps:

    dR/R0 = a * (exp(b (t - t0)) - 1)   for t >= t0, else 0

Failure: NASA's dR = 0.05 ohm over the IRF520N's 0.20 ohm is +25 percent,
i.e. capability C = 1/sqrt(1.25) = 0.894. Healthy noise and signal-to-noise
are drawn from the 40-unit distribution (docs/363). Still a model.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from lifetime_simulation import read_epoch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "calibrated_population.tsv"
CAP = ROOT / "data" / "assist_capability.tsv"
POP = ROOT / "data" / "population.tsv"

C_FAIL = 1.0 / np.sqrt(1.25)          # dR/R0 = +25 percent
WIN_PER_H = 720                       # 5 s windows
ENROL = 720                           # 1 h end-of-line sweep
TARGET = 2.7                          # alarms per hour, the 32 KB line
NOISE_W = (1.0 / 3.0) / np.sqrt(50)   # window mean of noise, in 3-sigma units
DRIFT = 0.351                         # healthy drift over a run, 3-sigma units
N_UNITS = 1000
HEALTHY_H = 20.0
MAX_H = 200.0
SEED = 365


def conducting_hours_per_run(dev):
    hrs, rid = read_epoch(dev)
    dt = np.diff(hrs, prepend=hrs[0]); dt[dt < 0] = 0; dt[dt > 1 / 60] = 0
    cum = np.cumsum(dt)
    return {r: float(np.mean(cum[rid == r])) for r in sorted(set(rid.tolist()))}


def model(p, t):
    a, b, t0 = p
    return np.where(t >= t0, a * (np.exp(b * np.clip(t - t0, 0, None)) - 1.0), 0.0)


def fit_device(t, y):
    best = None
    for t0 in np.linspace(0, t.max() * 0.9, 40):
        r = least_squares(lambda p: model((p[0], p[1], t0), t) - y, x0=[0.02, 0.1],
                          bounds=([1e-6, 1e-4], [10.0, 5.0]))
        if best is None or r.cost < best[0]:
            best = (r.cost, r.x[0], r.x[1], t0)
    cost, a, b, t0 = best
    yhat = model((a, b, t0), t)
    ss = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(np.sum((y - yhat) ** 2)) / ss if ss > 0 else float("nan")
    return a, b, t0, r2


def main() -> None:
    # ---- part 1: fit
    caps = {}
    with CAP.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            caps[int(r["device"])] = [float(r[f"C_run{k}"]) for k in range(1, 8)]
    fits = []
    print("NASA の指数モデルを 6 素子に当てる（通電時間はタイムスタンプから）\n")
    print(f"{'素子':<9}{'a':>9}{'b [1/h]':>10}{'t0 [h]':>9}{'R²':>7}{'寿命 [h]':>10}{'故障までの時定数':>10}")
    for dev in mos.DEVICES:
        hrs = conducting_hours_per_run(dev)
        t = np.array([hrs[k] for k in range(1, 8)])
        y = np.array([1.0 / c ** 2 - 1.0 for c in caps[dev]])
        a, b, t0, r2 = fit_device(t, y)
        t_fail = t0 + np.log(0.25 / a + 1.0) / b
        fits.append((dev, a, b, t0, r2, t_fail))
        print(f"Test_{dev:<4}{a:>9.4f}{b:>10.4f}{t0:>9.2f}{r2:>7.3f}{t_fail:>10.1f}{(t_fail - t0) * b:>10.2f}")
    bs = np.array([f[2] for f in fits]); as_ = np.array([f[1] for f in fits])
    m1 = bs.max() / bs.min()
    print(f"\nb の最大/最小 = {m1:.2f}   a の最大/最小 = {as_.max() / as_.min():.2f}")

    # ---- part 2: population
    rng = np.random.default_rng(SEED)
    pop = []
    with POP.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            pop.append((float(r["sigma"]), float(r["S"])))
    la_mu, la_sd = np.log(as_).mean(), np.log(as_).std(ddof=1)
    lb_mu, lb_sd = np.log(bs).mean(), np.log(bs).std(ddof=1)
    q = min(TARGET / WIN_PER_H, 1.0 - 1.0 / ENROL)

    det, lead_over_tc, fa_rates = [], [], []
    rows = []
    for i in range(N_UNITS):
        sigma, S = pop[rng.integers(len(pop))]
        degrading = i % 2 == 1
        a = float(np.exp(rng.normal(la_mu, la_sd))); b = float(np.exp(rng.normal(lb_mu, lb_sd)))
        if degrading:
            t0 = float(rng.uniform(1.0, 0.5 * MAX_H))
            t_fail = t0 + np.log(0.25 / a + 1.0) / b
            run_h = min(t_fail + 1.0, MAX_H)
        else:
            t0, t_fail, run_h = float("nan"), float("nan"), HEALTHY_H
        n_run = int(run_h * WIN_PER_H)
        n = ENROL + n_run
        step = DRIFT / np.sqrt(n_run)
        w = np.cumsum(rng.normal(0, step, n)) + rng.normal(0, NOISE_W, n)
        t_h = (np.arange(n) - ENROL) / WIN_PER_H              # hours since enrolment
        if degrading:
            w = w + S * model((a, b, t0), np.clip(t_h, 0, None))
        cal = np.abs(w[:ENROL])
        thr = float(np.quantile(cal, 1 - q))
        fired = np.abs(w[ENROL:]) > thr
        if degrading:
            idx = np.flatnonzero(fired)
            t_alarm = idx[0] / WIN_PER_H if len(idx) else float("inf")
            hit = t_alarm < t_fail and t_fail <= MAX_H
            det.append(hit)
            if hit:
                lead_over_tc.append((t_fail - t_alarm) * b)
            rows.append((i, 1, sigma, S, a, b, t0, t_fail, t_alarm, int(hit), float("nan")))
        else:
            rate = fired.sum() / run_h
            fa_rates.append(rate)
            rows.append((i, 0, sigma, S, a, b, t0, t_fail, float("nan"), 0, rate))

    det = np.array(det); lead = np.array(lead_over_tc); fa = np.array(fa_rates)
    print(f"\n仮想個体 {N_UNITS}（劣化 {det.size}、健全 {fa.size}）、線 {TARGET} 件/時、故障 C = {C_FAIL:.3f}")
    print(f"  故障前に警報      : {det.mean():.1%}")
    print(f"  猶予 / 時定数 中央値: {np.median(lead):.2f}  (10% {np.percentile(lead, 10):.2f})")
    print(f"  健全の誤検知 中央値 : {np.median(fa):.2f} 件/時、線の 2 倍超 {np.mean(fa > 2 * TARGET):.1%}")

    print("\n=== 事前登録した予想 ===")
    print(f"  M1 b の最大/最小 <= 5             : {m1:.2f} -> {'PASS' if m1 <= 5 else 'FAIL'}")
    print(f"  M2 故障前に警報 >= 90%            : {det.mean():.1%} -> {'PASS' if det.mean() >= 0.9 else 'FAIL'}")
    print(f"  M3 猶予の中央値 >= 0.5 時定数     : {np.median(lead):.2f} -> {'PASS' if np.median(lead) >= 0.5 else 'FAIL'}")
    print(f"  M4 線の 2 倍超の健全個体 <= 10%   : {np.mean(fa > 2 * TARGET):.1%} -> {'PASS' if np.mean(fa > 2 * TARGET) <= 0.1 else 'FAIL'}")
    print("\n何もしない基準（直線の劣化、docs/344）: 検知 95〜100%、誤検知 12〜39 件/時")

    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["kind", "id", "a", "b", "t0", "r2_or_tfail", "extra"])
        for dev, a, b, t0, r2, tf in fits:
            w.writerow(["fit", dev, a, b, t0, r2, tf])
        w.writerow(["unit", "id", "sigma", "S", "a", "b", "t0", "t_fail", "t_alarm", "hit", "fa_rate"])
        for r in rows:
            w.writerow(["unit"] + list(r))
    print(f"\n{OUT.relative_to(ROOT)} に書いた")


if __name__ == "__main__":
    main()
