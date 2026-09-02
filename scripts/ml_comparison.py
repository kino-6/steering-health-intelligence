#!/usr/bin/env python3
"""Does a one-class learner beat the straight line? (docs/289 -> docs/290)

Executes the protocol pre-registered in docs/289.

The element fits one line per channel and thresholds a quantile. Nothing is
learned, and nothing in this repository ever recorded a decision not to learn.
This measures the alternative on the same footing.

Supervised learning is unavailable by construction: a unit at end of line has
never failed, so there are no fault labels to train on. What can be compared is
one-class methods fitted to normal operation only, with thresholds set to the
same false-alarm rate on the same enrolment data, over the same channels with
the same common-mode rejection and the same five-second windows.

Criteria: L1 detection above eight of eight at a matched alarm rate; L2 false
alarms no worse than the line; L3 whether the fitted model fits in 48 bytes.

Data: Bacha et al., inverter-driven PMSM fault dataset, CC BY 4.0.
"""

from __future__ import annotations

import pickle
import sys
import zipfile
from pathlib import Path

import numpy as np
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eps_health_recorder as ehr
from demo_recorder import SIBLINGS, as_dicts
from inverter_recorder import ZIP, BASE, COLS, OPCOL, read

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "ml_comparison.tsv"
WIN = ehr.FAST_WINDOW
RNG = 20260902


def features(a):
    """Per window: mean and max of each common-mode-rejected channel.

    The same quantities the element's fast side computes, so the comparison is
    about the decision rule and not about the features.
    """
    vals, _ = as_dicts(a)
    cols = []
    for c in COLS:
        y = ehr.common_mode_reject(vals, c, SIBLINGS.get(c, ()))
        k = len(y) // WIN
        if not k:
            return None
        w = y[:k * WIN].reshape(k, WIN)
        cols.append(w.mean(axis=1))
        cols.append(np.abs(w).max(axis=1))
    return np.column_stack(cols)


def at_rate(scores_fit, scores_eval, rate):
    """Threshold at a given false-alarm rate on the fit set, applied to eval."""
    q = min(1 - rate, 1 - 1.0 / len(scores_fit))
    thr = float(np.quantile(scores_fit, q))
    return thr, float(np.mean(scores_eval > thr))


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    names = [n for n in z.namelist() if n.startswith(BASE) and n.endswith(".txt")]
    normal = read(z, next(n for n in names if "normal_operation" in n))
    faults = {Path(f).stem: read(z, f)
              for f in sorted(n for n in names if "fault_scenarios" in n)}

    half = len(normal) // 2
    X_fit = features(normal[:half])
    X_hold = features(normal[half:])
    X_fault = {k: features(v) for k, v in faults.items() if v is not None}
    X_fault = {k: v for k, v in X_fault.items() if v is not None}

    mu, sd = X_fit.mean(axis=0), X_fit.std(axis=0) + 1e-12
    def norm(x):
        return (x - mu) / sd

    # the rate the enrolment can actually express, docs/282
    rate = 1.0 / len(X_fit)
    print(f"窓 学習 {len(X_fit)} / 保留 {len(X_hold)}、特徴 {X_fit.shape[1]}")
    print(f"揃える誤報率: {rate:.5f} /窓 (この登録で刻める最小)\n")

    learners = {
        "Isolation Forest": IsolationForest(random_state=RNG, n_estimators=200),
        "One-Class SVM": OneClassSVM(nu=0.05, gamma="scale"),
        "Elliptic Envelope": EllipticEnvelope(random_state=RNG, support_fraction=0.9),
    }

    print(f"{'手法':>20} {'保留の誤報':>11} {'設計比':>8} {'検出':>7} "
          f"{'大きさ':>11}")
    print("-" * 64)
    rows = []

    # the line, as the element actually runs it
    rec = ehr.Recorder(ehr.enrol(*as_dicts(normal[:half]), siblings=SIBLINGS,
                                 alarm_per_hour=1.0))
    ach = max(max(c.alarm_per_hour_fast, c.alarm_per_hour_slow)
              for c in rec.fp.channels.values())
    r_norm = rec.run_session(*as_dicts(normal[half:]), siblings=SIBLINGS,
                             alarm_per_hour=ach)
    fa_line = sum(1 for r in r_norm if r.validity and r.flags) / max(1, len(r_norm))
    hit_line = sum(1 for k, v in faults.items() if v is not None and
                   ehr.fired(ehr.Recorder(rec.fp).run_session(
                       *as_dicts(v), siblings=SIBLINGS, alarm_per_hour=ach)))
    size_line = len(rec.fp.channels["T1"].pack())
    print(f"{'直線(現在の実装)':>20} {fa_line:>11.4f} {fa_line/rate:>7.1f}倍 "
          f"{hit_line:>5}/8 {size_line:>9}B")
    rows.append({"method": "線形(現在の実装)", "fa": fa_line, "hits": hit_line,
                 "bytes": size_line})

    for name, model in learners.items():
        model.fit(norm(X_fit))
        s_fit = -model.score_samples(norm(X_fit))
        s_hold = -model.score_samples(norm(X_hold))
        thr, fa = at_rate(s_fit, s_hold, rate)
        hits = 0
        for k, xf in X_fault.items():
            if float(np.max(-model.score_samples(norm(xf)))) > thr:
                hits += 1
        nbytes = len(pickle.dumps(model))
        print(f"{name:>20} {fa:>11.4f} {fa/rate:>7.1f}倍 {hits:>5}/8 "
              f"{nbytes:>9,}B")
        rows.append({"method": name, "fa": fa, "hits": hits, "bytes": nbytes})

    best = max(rows[1:], key=lambda r: (r["hits"], -r["fa"]))
    print(f"\n=== L1 検出が 8/8 を上回るか ===")
    print(f"  最良の学習手法 {best['method']}: {best['hits']}/8  "
          f"線形: {hit_line}/8  "
          f"{'PASS' if best['hits'] > hit_line else 'FAIL'}")
    print(f"\n=== L2 誤報が線形と同等以下か ===")
    print(f"  {best['method']} {best['fa']:.4f}  線形 {fa_line:.4f}  "
          f"{'PASS' if best['fa'] <= fa_line else 'FAIL'}")
    print(f"\n=== L3 48バイトに収まるか ===")
    for r in rows[1:]:
        print(f"  {r['method']:>20}: {r['bytes']:>9,} バイト  "
              f"{'PASS' if r['bytes'] <= 48 else 'FAIL'} "
              f"(線形の {r['bytes']/size_line:,.0f} 倍)")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("method\tfalse_alarm_holdout\tfaults_detected\tmodel_bytes\n")
        for r in rows:
            fh.write(f"{r['method']}\t{r['fa']:.6f}\t{r['hits']}\t{r['bytes']}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
