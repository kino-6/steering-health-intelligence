#!/usr/bin/env python3
"""Window length and recurrence sensitivity (docs/155).

docs/144 measured the detection limits of the log-sign pipeline at a single
operating point: one 60 s window, z>=4, clean FPR 6.7%. It noted that
"lengthening the window / counting recurrence should raise sensitivity"
but left that UNVERIFIED. This script verifies it.

Two designs are compared at MATCHED total observation time (60 s):

  A. single window  : one 60 s window, flag if max|z| >= 4
  B. k-of-N recurrence: split the same 60 s into N sub-windows,
                        flag if >= k sub-windows have max|z| >= 4

Design B is what docs/144's own conclusion demands: a steady bias is
detected 100% of the time even at the smallest injected magnitude, which
means road camber and payload also fire it. A single shot is therefore
unusable; recurrence is the actual design. The honest question is not
"does sensitivity rise" but "at a MATCHED false-positive rate, does the
detection limit improve".

All designs are evaluated on a COMMON COHORT: segments whose every
sub-window, at every window length, clears the excitation gate. Without
this the comparison is confounded -- requiring excitation in all 4 of the
15 s sub-windows silently selects a small, unusually well-excited
subpopulation (137 of 910 segments), and its numbers are not comparable
with the 60 s single-window figures measured on 621 segments.

Sub-windows come from splitting ONE segment, so they are guaranteed to be
the same vehicle and the same drive. Concatenating consecutive segments to
build windows LONGER than 60 s is not done: each commaSteeringControl
segment resets t to 0 and contiguity between segments is not established.

Data: commaSteeringControl (comma.ai, MIT). Healthy vehicles only -- this
bounds pipeline sensitivity, it is not a claim about real failures.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
PLATFORM = sys.argv[1] if len(sys.argv) > 1 else "FORD_MAVERICK_1ST_GEN"
_SUFFIX = "" if PLATFORM == "FORD_MAVERICK_1ST_GEN" else "_" + PLATFORM.lower().replace("-", "_")
DATA_DIR = REPO_ROOT / ".public_log_cache" / PLATFORM
OUT_TSV = REPO_ROOT / "data" / f"steering_window_recurrence{_SUFFIX}.tsv"

MIN_SPEED, ANGLE_SPLIT = 5.0, 2.0
ANGLE_DOMAIN, DOMAIN_FRACTION, JUMP_MAX, EXCITATION_MIN = 45.0, 0.10, 2.0, 0.15
Z_FLAG, DT = 4.0, 0.1
FULL_SEC, MIN_VALID_FULL = 60.0, 300
FEATURES = ["bias", "drift", "asymmetry", "lag", "gain_dev", "hf_noise"]

WINDOWS = [15.0, 30.0, 60.0]          # sub-window length in seconds
INJECTIONS = {
    "lag_s": [0.1, 0.2, 0.3, 0.4, 0.5],
    "gain": [0.02, 0.05, 0.10, 0.15, 0.20],
    "bias_ms2": [0.05, 0.10, 0.20, 0.30],
    "asym_ms2": [0.05, 0.10, 0.20, 0.30],
}


def load_segment(csv: Path):
    """Gate a raw segment exactly as docs/144 does, then return its arrays."""
    df = pd.read_csv(csv, usecols=["vEgo", "steeringAngleDeg", "t",
                                   "latAccelSteeringAngle", "latAccelLocalizer"])
    m = (df["vEgo"] > MIN_SPEED) & df["latAccelLocalizer"].notna() & df["latAccelSteeringAngle"].notna()
    d = df[m]
    if len(d) < MIN_VALID_FULL:
        return None
    angle = d["steeringAngleDeg"].to_numpy()
    if float(np.mean(np.abs(angle) > ANGLE_DOMAIN)) > DOMAIN_FRACTION:
        return None
    d = d[np.abs(angle) <= ANGLE_DOMAIN]
    if len(d) < MIN_VALID_FULL:
        return None
    implied = d["latAccelSteeringAngle"].to_numpy()
    actual = d["latAccelLocalizer"].to_numpy()
    if np.max(np.abs(np.diff(actual - implied))) > JUMP_MAX:
        return None
    return {"t": d["t"].to_numpy(), "angle": d["steeringAngleDeg"].to_numpy(),
            "implied": implied, "actual": actual}


def split(seg, win_sec: float):
    """Split one gated segment into consecutive sub-windows of win_sec."""
    t = seg["t"]
    t0 = t[0]
    n_sub = int(round(FULL_SEC / win_sec))
    min_valid = int(MIN_VALID_FULL * win_sec / FULL_SEC)
    out = []
    for i in range(n_sub):
        m = (t >= t0 + i * win_sec) & (t < t0 + (i + 1) * win_sec)
        if int(m.sum()) < min_valid:
            out.append(None)
            continue
        out.append({k: seg[k][m] for k in ("t", "angle", "implied", "actual")})
    return out


def features(seg):
    implied, actual, angle, t = seg["implied"], seg["actual"], seg["angle"], seg["t"]
    r = actual - implied
    excitation = float(np.std(implied))
    bias = float(np.mean(r))
    drift = float(np.polyfit(t, r, 1)[0]) if len(np.unique(t)) > 2 else 0.0
    left, right = r[angle > ANGLE_SPLIT], r[angle < -ANGLE_SPLIT]
    asym = (float(np.mean(left) - np.mean(right))
            if (len(left) >= 20 and len(right) >= 20 and excitation >= EXCITATION_MIN) else np.nan)
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
    return {"bias": bias, "drift": drift, "asymmetry": asym, "lag": lag,
            "gain_dev": gain_dev, "hf_noise": float(np.std(np.diff(r))), "excitation": excitation}


def inject(seg, kind: str, mag: float):
    implied, actual, angle = seg["implied"], seg["actual"], seg["angle"]
    r = actual - implied
    if kind == "lag_s":
        k = int(round(mag / DT))
        shifted = np.concatenate([np.repeat(implied[0], k), implied[:-k]]) if k > 0 else implied
        actual2 = r + shifted
    elif kind == "gain":
        actual2 = r + (1 + mag) * implied
    elif kind == "bias_ms2":
        actual2 = actual + mag
    elif kind == "asym_ms2":
        off = np.where(angle > ANGLE_SPLIT, mag / 2, np.where(angle < -ANGLE_SPLIT, -mag / 2, 0.0))
        actual2 = actual + off
    else:
        raise ValueError(kind)
    return {**seg, "actual": actual2}


def robust_stats(vals):
    v = np.array(vals, dtype=float)
    med = np.nanmedian(v)
    mad = np.nanmedian(np.abs(v - med))
    scale = 1.4826 * mad if mad > 1e-12 else np.nanstd(v)
    return med, (scale if scale > 1e-12 else 1.0)


def max_z(f, stats):
    zs = []
    for name in FEATURES:
        v = f[name]
        if v is None or (isinstance(v, float) and math.isnan(v)):
            continue
        med, sc = stats[name]
        zs.append(abs((v - med) / sc))
    return max(zs) if zs else 0.0


def main() -> None:
    segs = []
    for csv in sorted(DATA_DIR.glob("*.csv")):
        s = load_segment(csv)
        if s:
            segs.append((csv.stem, s))
    print(f"platform={PLATFORM}  gated 60s segments: {len(segs)}")

    # split once per window length, and compute features once
    subs = {win: {name: split(s, win) for name, s in segs} for win in WINDOWS}
    feats = {win: {name: [features(w) if w else None for w in ws] for name, ws in subs[win].items()}
             for win in WINDOWS}

    # COMMON COHORT: every sub-window valid AND excited, at every window length.
    # The excitation gate is what lag/gain need; requiring it only in the finest
    # split would still leave the coarser designs on a different population.
    cohort = []
    for name, _ in segs:
        ok = True
        for win in WINDOWS:
            fws = feats[win][name]
            if any(fw is None or fw["excitation"] < EXCITATION_MIN for fw in fws):
                ok = False
                break
        if ok:
            cohort.append(name)
    print(f"common cohort (all sub-windows valid and excited at every window length): {len(cohort)}")

    rows = []
    for win in WINDOWS:
        n_sub = int(round(FULL_SEC / win))
        # population stats are recomputed per window length: features change with
        # duration. They are fitted on the cohort so every design shares a reference.
        stats = {f: robust_stats([feats[win][n][i][f] for n in cohort for i in range(n_sub)])
                 for f in FEATURES}
        clean_z = {n: [max_z(feats[win][n][i], stats) for i in range(n_sub)] for n in cohort}
        print(f"\n--- window {win:.0f}s  (N={n_sub} per 60s)  cohort {len(cohort)}")

        for k in range(1, n_sub + 1):
            fpr = float(np.mean([sum(z >= Z_FLAG for z in clean_z[n]) >= k for n in cohort]))
            healthy = [n for n in cohort if sum(z >= Z_FLAG for z in clean_z[n]) < k]
            print(f"  k={k}/{n_sub}: clean FPR {fpr:.1%}  healthy for injection: {len(healthy)}")
            for kind, mags in INJECTIONS.items():
                for mag in mags:
                    det = usable = 0
                    for n in healthy:
                        fz = [max_z(features(inject(w, kind, mag)), stats) for w in subs[win][n]]
                        usable += 1
                        if sum(z >= Z_FLAG for z in fz) >= k:
                            det += 1
                    rate = det / usable if usable else float("nan")
                    rows.append({"window_s": win, "n_sub": n_sub, "k": k, "clean_fpr": fpr,
                                 "kind": kind, "mag": mag, "detected": det,
                                 "usable": usable, "rate": rate})

    with OUT_TSV.open("w") as out:
        out.write("window_s\tn_sub\tk_of_n\tclean_fpr\tkind\tmagnitude\tdetected\tusable\tdetection_rate\n")
        for r in rows:
            out.write(f"{r['window_s']:.0f}\t{r['n_sub']}\t{r['k']}\t{r['clean_fpr']:.4f}\t"
                      f"{r['kind']}\t{r['mag']}\t{r['detected']}\t{r['usable']}\t{r['rate']:.4f}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
