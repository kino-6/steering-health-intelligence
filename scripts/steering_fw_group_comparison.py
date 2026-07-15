#!/usr/bin/env python3
"""Do response statistics separate REAL EPS variants? (docs/147, 検証2)

AUDI_Q3_2ND_GEN segments carry two distinct EPS part/firmware identifiers
(745 vs 255 segments). Unlike synthetic injection, this is a real, fielded
difference. If the pipeline's response features separate the two groups,
that is evidence it can surface real component-variant differences from
driving logs alone.

Honest confounder, stated up front: groups = different physical vehicles,
so usage (speed, roads, drivers) differs too. We report usage features
(speed, excitation) alongside response features; a response-feature gap
that greatly exceeds the usage gap is the interesting signal, but this is
association, not causation.

Method: per-segment features (same gates as docs/144), group comparison by
median difference in pooled-MAD units (robust effect size) + deterministic
permutation test (fixed seed).
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / ".public_log_cache" / "AUDI_Q3_2ND_GEN"
OUT_TSV = REPO_ROOT / "data" / "steering_fw_group_comparison.tsv"

MIN_SPEED, MIN_VALID, ANGLE_SPLIT = 5.0, 300, 2.0
ANGLE_DOMAIN, DOMAIN_FRACTION, JUMP_MAX, EXCITATION_MIN = 45.0, 0.10, 2.0, 0.15
DT = 0.1
RESPONSE_FEATURES = ["bias", "drift", "asymmetry", "lag", "gain_dev", "hf_noise"]
USAGE_FEATURES = ["v_mean", "excitation"]


def fw_of(csv_path: Path) -> str:
    with open(csv_path) as fh:
        r = csv.reader(fh)
        header = next(r)
        i = header.index("epsFwVersion")
        row = next(r, None)
        return row[i] if row else ""


def load_features(csv_path: Path) -> dict | None:
    df = pd.read_csv(csv_path, usecols=["vEgo", "steeringAngleDeg", "t",
                                        "latAccelSteeringAngle", "latAccelLocalizer"])
    m = (df["vEgo"] > MIN_SPEED) & df["latAccelLocalizer"].notna() & df["latAccelSteeringAngle"].notna()
    d = df[m]
    if len(d) < MIN_VALID:
        return None
    angle = d["steeringAngleDeg"].to_numpy()
    if float(np.mean(np.abs(angle) > ANGLE_DOMAIN)) > DOMAIN_FRACTION:
        return None
    d = d[np.abs(angle) <= ANGLE_DOMAIN]
    if len(d) < MIN_VALID:
        return None
    implied = d["latAccelSteeringAngle"].to_numpy()
    actual = d["latAccelLocalizer"].to_numpy()
    angle = d["steeringAngleDeg"].to_numpy()
    t = d["t"].to_numpy()
    r = actual - implied
    if len(r) > 1 and np.max(np.abs(np.diff(r))) > JUMP_MAX:
        return None
    excitation = float(np.std(implied))
    left, right = r[angle > ANGLE_SPLIT], r[angle < -ANGLE_SPLIT]
    asym = float(np.mean(left) - np.mean(right)) if (len(left) >= 20 and len(right) >= 20 and excitation >= EXCITATION_MIN) else np.nan
    if excitation >= EXCITATION_MIN:
        a = implied - implied.mean(); b = actual - actual.mean()
        best_s, best_c = 0, -np.inf
        for s in range(-5, 6):
            c = np.dot(a[: len(a) - s], b[s:]) if s >= 0 else np.dot(a[-s:], b[: len(b) + s])
            if c > best_c:
                best_c, best_s = c, s
        lag = best_s * DT
        gain_dev = float(np.dot(a, b) / np.dot(a, a)) - 1.0
    else:
        lag, gain_dev = np.nan, np.nan
    return {
        "bias": float(np.mean(r)),
        "drift": float(np.polyfit(t, r, 1)[0]) if len(np.unique(t)) > 2 else 0.0,
        "asymmetry": asym, "lag": lag, "gain_dev": gain_dev,
        "hf_noise": float(np.std(np.diff(r))),
        "v_mean": float(d["vEgo"].mean()), "excitation": excitation,
    }


def effect_and_p(a: np.ndarray, b: np.ndarray, rng) -> tuple[float, float]:
    a = a[~np.isnan(a)]; b = b[~np.isnan(b)]
    if len(a) < 30 or len(b) < 30:
        return float("nan"), float("nan")
    med_diff = float(np.median(a) - np.median(b))
    pooled = np.concatenate([a - np.median(a), b - np.median(b)])
    mad = np.median(np.abs(pooled)) * 1.4826
    eff = med_diff / mad if mad > 1e-12 else float("nan")
    obs = abs(med_diff)
    both = np.concatenate([a, b])
    n = len(a)
    hits = 0
    n_perm = 2000
    for _ in range(n_perm):
        rng.shuffle(both)
        if abs(np.median(both[:n]) - np.median(both[n:])) >= obs:
            hits += 1
    return eff, (hits + 1) / (n_perm + 1)


def main() -> None:
    groups = defaultdict(list)
    for p in sorted(DATA_DIR.glob("*.csv")):
        f = load_features(p)
        if f:
            groups[fw_of(p)].append(f)
    keys = sorted(groups, key=lambda k: -len(groups[k]))
    ga, gb = keys[0], keys[1]
    A, B = groups[ga], groups[gb]
    print(f"group A: {len(A)} segs ({ga[:40]}...)")
    print(f"group B: {len(B)} segs ({gb[:40]}...)")
    rng = np.random.default_rng(0)
    lines = ["feature\tclass\tmedian_A\tmedian_B\teffect_size_mad\tp_perm"]
    print(f"{'feature':>12} {'class':>8} {'med_A':>9} {'med_B':>9} {'effect':>7} {'p':>7}")
    for feat in RESPONSE_FEATURES + USAGE_FEATURES:
        va = np.array([x[feat] for x in A], dtype=float)
        vb = np.array([x[feat] for x in B], dtype=float)
        eff, p = effect_and_p(va, vb, rng)
        cls = "response" if feat in RESPONSE_FEATURES else "usage"
        print(f"{feat:>12} {cls:>8} {np.nanmedian(va):>9.4f} {np.nanmedian(vb):>9.4f} {eff:>7.2f} {p:>7.4f}")
        lines.append(f"{feat}\t{cls}\t{np.nanmedian(va):.5f}\t{np.nanmedian(vb):.5f}\t{eff:.4f}\t{p:.4f}")
    # usage-matched re-comparison: restrict both groups to a common usage window
    def in_window(x):
        return 15.0 <= x["v_mean"] <= 30.0 and 0.2 <= x["excitation"] <= 0.8
    A2 = [x for x in A if in_window(x)]
    B2 = [x for x in B if in_window(x)]
    print(f"\nusage-matched window (v 15-30 m/s, excitation 0.2-0.8): A={len(A2)}, B={len(B2)}")
    lines.append("")
    lines.append("matched_feature\tclass\tmedian_A\tmedian_B\teffect_size_mad\tp_perm")
    for feat in RESPONSE_FEATURES + USAGE_FEATURES:
        va = np.array([x[feat] for x in A2], dtype=float)
        vb = np.array([x[feat] for x in B2], dtype=float)
        eff, p = effect_and_p(va, vb, rng)
        cls = "response" if feat in RESPONSE_FEATURES else "usage"
        print(f"{feat:>12} {cls:>8} {np.nanmedian(va):>9.4f} {np.nanmedian(vb):>9.4f} {eff:>7.2f} {p:>7.4f}")
        lines.append(f"{feat}\t{cls}\t{np.nanmedian(va):.5f}\t{np.nanmedian(vb):.5f}\t{eff:.4f}\t{p:.4f}")
    OUT_TSV.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
