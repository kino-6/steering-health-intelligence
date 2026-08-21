#!/usr/bin/env python3
"""Miss-structure analysis inside the TRAINING era only (docs/156).

docs/147 and docs/148 registered this as the remaining desk work; docs/151
then declared everything exhausted without running it. This closes it.

Question: within the training era (2013-2018), what structurally separates
the positive cohorts the model CAUGHT from the ones it MISSED?

docs/145 answered qualitatively: "some misses are recalls found inside the
supplier before users wrote complaints -- complaint data can only see the
failure modes a user notices and reports". That is a testable claim: misses
should be characterised by LOW complaint volume before T, not by the model
being badly tuned. This script tests it.

Scope discipline (docs/143): the test era (2019-2024) has already been
accessed twice and is NOT touched here. Nothing in this script changes the
frozen operating point or the not-viable verdict. It explains WHY the
method cannot see certain recalls; it does not try to improve recall.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recall_detection_model as rdm  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "recall_miss_structure.tsv"
CONSUMER_MAKE_MIN = rdm.CONSUMER_MAKE_MIN
LEAD = 6


def med(v):
    return float(np.median(v)) if len(v) else float("nan")


def main() -> None:
    cohorts = rdm.load_cohorts()
    earliest, eps_flag, named_any = rdm.load_labels()

    universe = {k for k, c in cohorts.items() if c.tot[-1] >= 50}
    make_tot = defaultdict(int)
    for k, c in cohorts.items():
        make_tot[c.make] += c.tot[-1]
    consumer = {m for m, t in make_tot.items() if t >= CONSUMER_MAKE_MIN}
    universe = {k for k in universe if k[0] in consumer}
    earliest = {k: d for k, d in earliest.items() if k[0] in consumer}
    pos_all = {k: d for k, d in earliest.items() if k in universe}
    negatives = sorted(k for k in universe if k not in named_any)

    train_pos = {k: d for k, d in pos_all.items() if 2013 * 12 <= d <= 2018 * 12 + 11}
    test_pos = {k: d for k, d in pos_all.items() if 2019 * 12 <= d <= 2024 * 12 + 11}
    frac_tr = len(train_pos) / (len(train_pos) + len(test_pos))
    neg_train = [k for i, k in enumerate(negatives) if (i * 9301 + 49297) % 10000 < frac_tr * 10000]
    tr_dates = sorted(train_pos.values())

    make_index = defaultdict(list)
    for k in universe:
        make_index[cohorts[k].make].append(k)

    rows, ys, meta = [], [], []
    for k, d in train_pos.items():
        f = rdm.features_for(k, cohorts, make_index, d, LEAD)
        if f:
            rows.append(f); ys.append(1); meta.append(k)
    for i, k in enumerate(neg_train):
        d = tr_dates[i % len(tr_dates)]
        f = rdm.features_for(k, cohorts, make_index, d, LEAD)
        if f:
            rows.append(f); ys.append(0); meta.append(k)

    X = np.array([[r[f] for f in rdm.FEATURES] for r in rows])
    y = np.array(ys, dtype=float)
    mu, sd = X.mean(0), X.std(0) + 1e-9
    w = rdm.logistic_fit((X - mu) / sd, y)
    s = rdm.predict(w, (X - mu) / sd)
    print(f"train rows: {len(y)}  positives: {int(y.sum())}")

    # frozen operating point, reproduced exactly as the model does:
    # highest recall subject to train precision >= 0.5
    best_thr, best_rec = None, -1.0
    for t in np.unique(s):
        pred = s >= t
        if pred.sum() == 0:
            continue
        prec = float(y[pred].sum() / pred.sum())
        rec = float(y[pred].sum() / y.sum())
        if prec >= 0.5 and rec > best_rec:
            best_thr, best_rec = float(t), rec
    print(f"frozen operating point: threshold={best_thr:.4f}  train recall={best_rec:.2f}")

    pos_idx = [i for i in range(len(y)) if y[i] == 1]
    caught = [i for i in pos_idx if s[i] >= best_thr]
    missed = [i for i in pos_idx if s[i] < best_thr]
    print(f"caught {len(caught)}  missed {len(missed)}  (miss rate {len(missed)/len(pos_idx):.0%})")

    # axes fixed before looking: complaint volume, steering share, age,
    # assist share, and whether the campaign is an EPS (ELECTRIC/ASSIST) one
    axes = [
        ("complaints_before_T", lambda i: rows[i]["_tot"]),
        ("steering_complaints_before_T", lambda i: rows[i]["_steer_n"]),
        ("steer_share", lambda i: rows[i]["steer_share"]),
        ("assist_share", lambda i: rows[i]["assist_share"]),
        ("age_at_T", lambda i: rows[i]["age_at_T"]),
        ("growth", lambda i: rows[i]["growth"]),
        ("rel_make", lambda i: rows[i]["rel_make"]),
    ]
    out = []
    print(f"\n{'axis':<30}{'caught(med)':>13}{'missed(med)':>13}{'ratio':>9}")
    print("-" * 65)
    for name, fn in axes:
        c = [fn(i) for i in caught]
        m = [fn(i) for i in missed]
        mc, mm = med(c), med(m)
        ratio = (mm / mc) if mc not in (0.0,) and mc == mc else float("nan")
        print(f"{name:<30}{mc:>13.3f}{mm:>13.3f}{ratio:>9.2f}")
        out.append((name, mc, mm, ratio))

    eps_c = sum(1 for i in caught if eps_flag.get(meta[i], False))
    eps_m = sum(1 for i in missed if eps_flag.get(meta[i], False))
    print(f"\nEPS (ELECTRIC/ASSIST) campaigns: caught {eps_c}/{len(caught)} ({eps_c/len(caught):.0%})"
          f"  missed {eps_m}/{len(missed)} ({eps_m/len(missed):.0%})")

    # the docs/145 claim, stated as a number: how many misses are "quiet"
    # cohorts -- few steering complaints on the books when the recall landed
    for q in (3, 5, 10, 20):
        qc = sum(1 for i in caught if rows[i]["_steer_n"] <= q)
        qm = sum(1 for i in missed if rows[i]["_steer_n"] <= q)
        print(f"  <= {q:>2} steering complaints before T: caught {qc/len(caught):>5.0%}   missed {qm/len(missed):>5.0%}")

    with OUT_TSV.open("w") as fh:
        fh.write("metric\tcaught_median\tmissed_median\tmissed_over_caught\n")
        for name, mc, mm, ratio in out:
            fh.write(f"{name}\t{mc:.4f}\t{mm:.4f}\t{ratio:.4f}\n")
        fh.write(f"eps_campaign_share\t{eps_c/len(caught):.4f}\t{eps_m/len(missed):.4f}\t"
                 f"{(eps_m/len(missed))/(eps_c/len(caught)) if eps_c else float('nan'):.4f}\n")
        for q in (3, 5, 10, 20):
            qc = sum(1 for i in caught if rows[i]["_steer_n"] <= q) / len(caught)
            qm = sum(1 for i in missed if rows[i]["_steer_n"] <= q) / len(missed)
            fh.write(f"share_with_le_{q}_steering_complaints\t{qc:.4f}\t{qm:.4f}\t"
                     f"{(qm/qc) if qc else float('nan'):.4f}\n")
        fh.write(f"n\t{len(caught)}\t{len(missed)}\t{len(missed)/len(pos_idx):.4f}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
