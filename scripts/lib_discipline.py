#!/usr/bin/env python3
"""Guards against mistakes this repository has actually made.

Each function here exists because a specific error happened and cost a
conclusion. Import these instead of hand-rolling the same comparison again.

See CHECKS.md for the full list and the incident behind each one.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import numpy as np


# --------------------------------------------------------------------------
# 1. Threshold comparison on small-sample rank statistics
#
# Incident (docs/205): the pre-registered bar was Spearman rho >= 0.8. On four
# points one adjacent inversion gives EXACTLY 4/5, which passes -- but scipy
# returns 0.7999999999999999 and a bare `>= 0.8` rejected it. That flipped a
# verdict from fail to pass once the error was noticed, which is exactly the
# kind of thing that looks like tuning after the fact.
# --------------------------------------------------------------------------
def spearman_exact(x, y) -> Fraction:
    """Spearman rho as an exact Fraction when there are no ties.

    Falls back to the float value wrapped in a Fraction if ranks tie, which
    is the case the closed form does not cover.
    """
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    n = len(x)
    rx, ry = _rank(x), _rank(y)
    if len(set(rx)) != n or len(set(ry)) != n:
        from scipy import stats
        return Fraction(float(stats.spearmanr(x, y).statistic)).limit_denominator(10**6)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return Fraction(1) - Fraction(6 * int(d2), n * (n * n - 1))


def _rank(a):
    order = np.argsort(a, kind="stable")
    r = np.empty(len(a), dtype=int)
    r[order] = np.arange(1, len(a) + 1)
    return list(r)


def passes(value, threshold, direction: str = ">=", tol: float = 1e-9) -> bool:
    """Compare against a pre-registered threshold without float noise.

    Use this for every pre-registered criterion. The tolerance repairs
    representation error only; it is far below any threshold this repository
    has ever set, and it never moves a bar.
    """
    v, t = float(value), float(threshold)
    if direction == ">=":
        return v >= t - tol
    if direction == "<=":
        return v <= t + tol
    if direction == ">":
        return v > t + tol
    if direction == "<":
        return v < t - tol
    raise ValueError(direction)


# --------------------------------------------------------------------------
# 2. Measurement-session grouping
#
# Incident, three times (docs/162, docs/201, docs/203): the KAIST recordings
# split into measurement campaigns months apart, and the step between
# campaigns is larger than the fault effect. Twice this was found by accident
# through a sensor-polarity quirk, which does not generalise; the recording
# timestamp sits in the file metadata and does.
#
# A per-unit baseline is not enough. The baseline must come from the SAME
# measurement session as the record being judged.
# --------------------------------------------------------------------------
def session_key_tdms(path: Path) -> str:
    """Recording date from TDMS metadata -- the campaign identifier."""
    from nptdms import TdmsFile
    meta = TdmsFile.read_metadata(path)
    for g in meta.groups():
        for c in g.channels():
            t = c.properties.get("wf_start_time")
            if t is not None:
                return str(t)[:10]
    return "unknown"


def require_same_session(keys: dict, baseline_key) -> list:
    """Keep only the records sharing the baseline's session, and say so.

    Returns the kept keys. Raises if fewer than three remain, because a
    monotonicity claim on two points is not a claim.
    """
    day0 = keys[baseline_key]
    kept = [k for k, v in keys.items() if v == day0]
    dropped = [k for k in keys if k not in kept]
    if dropped:
        print(f"   session {day0}: kept {sorted(kept)}, dropped {sorted(dropped)}")
    if len(kept) < 3:
        raise ValueError(
            f"only {len(kept)} record(s) share the baseline's session {day0} -- "
            "this cell is not evaluable")
    return kept


# --------------------------------------------------------------------------
# 3. Knowing what the observable actually is
#
# Incident (docs/199): thirty-four documents rested on Vds/Id from the NASA
# steadyState block, called it on-resistance, and built a capability model on
# conduction loss. The device was in its active region the whole time,
# dropping 4.9 V of a 5.61 V supply -- never switching. The check below would
# have caught it on day one.
# --------------------------------------------------------------------------
def switching_or_linear(v_device, v_supply, tol: float = 0.25) -> str:
    """Is the device switching, or sitting in its active region?

    A switch drops a small fraction of the supply while conducting. A device
    dropping most of the supply is a controlled dissipator, and I-squared-R
    reasoning does not apply to it.
    """
    frac = float(np.median(np.asarray(v_device) / np.asarray(v_supply)))
    kind = "linear/active region" if frac > tol else "switching"
    print(f"   device drops {frac:.1%} of the supply -> {kind}")
    return kind
