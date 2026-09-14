#!/usr/bin/env python3
"""The sibling difference on the calibrated Wiener population (docs/374).

Three same-kind channels per unit. Each carries a shared wander (variance
share s) plus its own; degradation enters one channel only (or all three,
for X4). The recorder judges each channel minus the median of the other two,
thresholds from one hour of enrolment at the 32 KB line. Parameters from
docs/373 (mu lognormal, sigma_B) and docs/363 (noise, S); shared fractions
measured in docs/352.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "sibling_wiener.tsv"
POP = ROOT / "data" / "population.tsv"

LM, LS, SIG_B = -1.65, 0.25, 0.555          # docs/373
WIN_PER_H, ENROL, TARGET = 720, 720, 2.7
NOISE_W = (1.0 / 3.0) / np.sqrt(50)
HEALTHY_H, MAX_H, N_UNITS, SEED = 2.3, 60.0, 1000, 374
SHARES = [0.0, 0.318, 0.926, 1.0]


def run(s: float, all_degrade: bool, rng) -> tuple[float, float, float]:
    pop = []
    with POP.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            pop.append(float(r["S"]))
    q = min(TARGET / WIN_PER_H, 1.0 - 1.0 / ENROL)
    dt = 1.0 / WIN_PER_H
    det, leads, fa = [], [], []
    for i in range(N_UNITS):
        S = pop[rng.integers(len(pop))]
        degrading = i % 2 == 1
        mu = float(np.exp(rng.normal(LM, LS))); D = S * 0.25
        if degrading:
            t0 = float(rng.uniform(0.5, HEALTHY_H)); t_fail = t0 + D / mu; run_h = min(t_fail + 1.0, MAX_H)
        else:
            t0, t_fail, run_h = float("nan"), float("nan"), HEALTHY_H
        n = ENROL + int(run_h * WIN_PER_H)
        shared = np.cumsum(rng.normal(0, SIG_B * np.sqrt(dt), n))
        ch = np.empty((3, n))
        for k in range(3):
            own = np.cumsum(rng.normal(0, SIG_B * np.sqrt(dt), n))
            ch[k] = np.sqrt(s) * shared + np.sqrt(1 - s) * own + rng.normal(0, NOISE_W, n)
        t_h = (np.arange(n) - ENROL) / WIN_PER_H
        if degrading:
            ramp = mu * np.clip(t_h - t0, 0, None)
            if all_degrade:
                ch += ramp
            else:
                ch[0] += ramp
        # each channel minus the median of the other two
        resid = np.empty_like(ch)
        for k in range(3):
            others = np.delete(ch, k, axis=0)
            resid[k] = ch[k] - np.median(others, axis=0)
        fired_any = np.zeros(n - ENROL, bool)
        for k in range(3):
            thr = float(np.quantile(np.abs(resid[k, :ENROL]), 1 - q))
            fired_any |= np.abs(resid[k, ENROL:]) > thr
        if degrading:
            idx = np.flatnonzero(fired_any); t_alarm = idx[0] / WIN_PER_H if len(idx) else float("inf")
            hit = t_alarm < t_fail <= MAX_H
            det.append(hit)
            if hit:
                leads.append(t_fail - t_alarm)
        else:
            fa.append(fired_any.sum() / run_h)
    det, leads, fa = np.array(det), np.array(leads), np.array(fa)
    return float(det.mean()), float(np.median(leads)) if len(leads) else float("nan"), float(np.median(fa))


def main() -> None:
    rng = np.random.default_rng(SEED)
    rows = []
    print(f"3 チャネルの組、劣化は 1 本だけ。線 {TARGET} 件/時、健全期 {HEALTHY_H} h、σ_B {SIG_B}\n")
    print(f"{'共有率 s':>9}{'故障前に警報':>13}{'猶予 中央値 [h]':>16}{'健全の誤検知 中央値 [件/時]':>26}")
    res = {}
    for s in SHARES:
        d, lead, f = run(s, False, rng)
        res[s] = (d, lead, f); rows.append(("one", s, d, lead, f))
        print(f"{s:>9.3f}{d:>13.1%}{lead:>16.2f}{f:>26.2f}")
    d_all, lead_all, f_all = run(0.926, True, rng)
    rows.append(("all", 0.926, d_all, lead_all, f_all))
    print(f"\n3 本すべてが同じ速さで劣化、s = 0.926: 故障前に警報 {d_all:.1%}、誤検知 {f_all:.2f} 件/時")

    print("\n=== 事前登録した予想 ===")
    d, lead, f = res[0.926]
    print(f"  X1 s=0.926 誤検知の中央値 <= 5.4 件/時        : {f:.2f} -> {'PASS' if f <= 2 * TARGET else 'FAIL'}")
    print(f"  X2 s=0.926 故障前 >= 90% かつ 猶予 >= 2 h      : {d:.1%}, {lead:.2f} h -> {'PASS' if d >= 0.9 and lead >= 2 else 'FAIL'}")
    f3 = res[0.318][2]
    print(f"  X3 s=0.318 誤検知の中央値 > 5.4 件/時          : {f3:.2f} -> {'PASS' if f3 > 2 * TARGET else 'FAIL'}")
    print(f"  X4 全チャネル劣化で故障前 < 50%                : {d_all:.1%} -> {'PASS' if d_all < 0.5 else 'FAIL'}")
    print(f"\n何もしない基準（差分なし、docs/373）: 健全の誤検知 231 件/時。ここでの s = 0 は {res[0.0][2]:.1f} 件/時")
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["degrading", "share", "detect_before_fail", "lead_median_h", "fa_median_per_h"])
        for r in rows:
            w.writerow(r)
    print(f"\n{OUT.relative_to(ROOT)} に書いた")


if __name__ == "__main__":
    main()
