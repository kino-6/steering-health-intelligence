#!/usr/bin/env python3
"""Recall detection model — executes the pre-registered protocol (docs/140).

Inputs (built previously):
  .nhtsa_flat/cohort_monthly.tsv   complaints per cohort-month (docs/140 data)
  .nhtsa_flat/FLAT_RCL_POST_2010.txt  recall ledger for labels

Everything here follows docs/140, committed BEFORE this script ran:
cohorts MY2005-2022, activity floor >=50 lifetime complaints (both classes),
positives = steering vehicle campaigns RCDATE>=2013 (earliest per cohort),
negatives = never named in any post-2010 steering vehicle campaign,
era split train 2013-2018 / test 2019-2024 by (pseudo-)event date,
features at T = event - 6 months from complaints filed <= T,
numpy logistic regression, frozen operating point from train.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
MONTHLY = REPO_ROOT / ".nhtsa_flat" / "cohort_monthly.tsv"
RCL = REPO_ROOT / ".nhtsa_flat" / "FLAT_RCL_POST_2010.txt"
OUT_TSV = REPO_ROOT / "data" / "recall_detection_results.tsv"

FEATURES = ["steer_share", "log_steer_n", "assist_share", "growth", "rel_make", "age_at_T"]
LEADS = [6, 12, 18, 24]


def ym_to_int(ym: str) -> int:
    return int(ym[:4]) * 12 + int(ym[4:6]) - 1


def date_to_int(d: str) -> int:
    return int(d[:4]) * 12 + int(d[4:6]) - 1


class Cohort:
    __slots__ = ("months", "tot", "steer", "assist", "make", "year")

    def __init__(self, make: str, year: int):
        self.make, self.year = make, year
        self.months: list[int] = []
        self.tot: list[int] = []
        self.steer: list[int] = []
        self.assist: list[int] = []

    def finalize(self, rows):
        rows.sort()
        ct = cs = ca = 0
        for m, t, s, a in rows:
            ct += t; cs += s; ca += a
            self.months.append(m); self.tot.append(ct); self.steer.append(cs); self.assist.append(ca)

    def upto(self, m: int) -> tuple[int, int, int]:
        i = bisect_right(self.months, m)
        if i == 0:
            return 0, 0, 0
        return self.tot[i - 1], self.steer[i - 1], self.assist[i - 1]


def load_cohorts() -> dict:
    raw = defaultdict(list)
    with open(MONTHLY) as fh:
        next(fh)
        for line in fh:
            make, model, year, ym, t, s, a = line.rstrip("\n").split("\t")
            raw[(make, model, int(year))].append((ym_to_int(ym), int(t), int(s), int(a)))
    cohorts = {}
    for key, rows in raw.items():
        c = Cohort(key[0], key[2])
        c.finalize(rows)
        cohorts[key] = c
    return cohorts


def load_labels():
    earliest: dict[tuple, int] = {}
    eps_flag: dict[tuple, bool] = {}
    named_any: set = set()
    with open(RCL, encoding="latin-1") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < 22:
                continue
            make, model, year, comp, rcltype, rcdate = f[2].strip().upper(), f[3].strip().upper(), f[4], f[6].upper(), f[10], f[15]
            if rcltype != "V" or "STEERING" not in comp:
                continue
            if not (year.isdigit() and 2005 <= int(year) <= 2022):
                continue
            key = (make, model, int(year))
            named_any.add(key)
            if not (len(rcdate) == 8 and rcdate.isdigit() and int(rcdate[:4]) >= 2013):
                continue
            d = date_to_int(rcdate)
            if key not in earliest or d < earliest[key]:
                earliest[key] = d
            if "ELECTRIC" in comp or "ASSIST" in comp:
                eps_flag[key] = True
    return earliest, eps_flag, named_any


def features_for(key, cohorts, make_index, event_m: int, lead: int):
    T = event_m - lead
    c = cohorts[key]
    tot, steer, assist = c.upto(T)
    if tot < 1:
        return None
    share = steer / tot
    t2, s2, _ = c.upto(T - 24)
    recent = steer - s2
    first_m = c.months[0]
    prior_months = max((T - 24) - first_m, 1)
    prior_rate = s2 / prior_months
    growth = min(recent / (prior_rate * 24) if prior_rate > 0 else (5.0 if recent > 0 else 0.0), 5.0)
    shares = []
    for k2 in make_index.get(c.make, []):
        if k2 == key:
            continue
        t3, s3, _ = cohorts[k2].upto(T)
        if t3 >= 20:
            shares.append(s3 / t3)
    med = float(np.median(shares)) if len(shares) >= 5 else np.nan
    # v2 (docs/142): difference instead of ratio to break collinearity with steer_share
    rel = (share - med) if not math.isnan(med) else 0.0
    age = (T // 12) - c.year
    return {
        "steer_share": share, "log_steer_n": math.log1p(steer),
        "assist_share": (assist / steer) if steer else 0.0,
        "growth": growth, "rel_make": rel, "age_at_T": age,
        "_steer_n": steer, "_tot": tot, "_rel_ratio": (share / med) if (not math.isnan(med) and med > 0) else 6.0,
    }


def logistic_fit(X, y, l2=1e-3, iters=4000, lr=0.1):
    Xb = np.hstack([np.ones((len(X), 1)), X])
    w = np.zeros(Xb.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-Xb @ w))
        g = Xb.T @ (p - y) / len(y) + l2 * np.r_[0, w[1:]]
        w -= lr * g
    return w


def predict(w, X):
    Xb = np.hstack([np.ones((len(X), 1)), X])
    return 1 / (1 + np.exp(-Xb @ w))


def pr_auc(y, s):
    order = np.argsort(-s)
    y = y[order]
    tp = np.cumsum(y)
    fp = np.cumsum(1 - y)
    prec = tp / (tp + fp)
    rec = tp / y.sum()
    ap = 0.0
    prev_r = 0.0
    for p, r in zip(prec, rec):
        ap += p * (r - prev_r)
        prev_r = r
    return ap


def roc_auc(y, s):
    order = np.argsort(s)
    ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
    pos = y == 1
    n1, n0 = pos.sum(), (~pos).sum()
    return (ranks[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


V2 = True  # docs/142 revision: consumer-make scope, rel_make as difference, EPS subset
CONSUMER_MAKE_MIN = 5000


def main() -> None:
    cohorts = load_cohorts()
    earliest, eps_flag, named_any = load_labels()

    universe = {k for k, c in cohorts.items() if c.tot[-1] >= 50}
    if V2:
        make_tot = defaultdict(int)
        for k, c in cohorts.items():
            make_tot[c.make] += c.tot[-1]
        consumer = {m for m, t in make_tot.items() if t >= CONSUMER_MAKE_MIN}
        universe = {k for k in universe if k[0] in consumer}
        earliest = {k: d for k, d in earliest.items() if k[0] in consumer}
        print(f"[v2] consumer makes: {len(consumer)}; labels in scope: {len(earliest)}")
    pos_all = {k: d for k, d in earliest.items() if k in universe}
    matched_rate = len(pos_all) / len(earliest)
    negatives = sorted(k for k in universe if k not in named_any)

    train_pos = {k: d for k, d in pos_all.items() if 2013 * 12 <= d <= 2018 * 12 + 11}
    test_pos = {k: d for k, d in pos_all.items() if 2019 * 12 <= d <= 2024 * 12 + 11}
    n_tr_p, n_te_p = len(train_pos), len(test_pos)
    # deterministic negative allocation proportional to positive counts
    frac_tr = n_tr_p / (n_tr_p + n_te_p)
    neg_train = [k for i, k in enumerate(negatives) if (i * 9301 + 49297) % 10000 < frac_tr * 10000]
    neg_test = [k for k in negatives if k not in set(neg_train)]
    tr_dates = sorted(train_pos.values())
    te_dates = sorted(test_pos.values())

    def build(lead: int):
        make_index = defaultdict(list)
        for k in universe:
            make_index[cohorts[k].make].append(k)
        rows, ys, era, meta = [], [], [], []
        for split, pos, negs, dates in (("train", train_pos, neg_train, tr_dates),
                                        ("test", test_pos, neg_test, te_dates)):
            for k, d in pos.items():
                f = features_for(k, cohorts, make_index, d, lead)
                if f:
                    rows.append(f); ys.append(1); era.append(split); meta.append(k)
            for i, k in enumerate(negs):
                d = dates[i % len(dates)]
                f = features_for(k, cohorts, make_index, d, lead)
                if f:
                    rows.append(f); ys.append(0); era.append(split); meta.append(k)
        X = np.array([[r[f] for f in FEATURES] for r in rows])
        y = np.array(ys, dtype=float)
        era = np.array(era)
        return X, y, era, rows, meta

    X, y, era, rows, meta = build(6)
    tr, te = era == "train", era == "test"
    mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
    Xz = (X - mu) / sd
    w = logistic_fit(Xz[tr], y[tr])
    s_tr, s_te = predict(w, Xz[tr]), predict(w, Xz[te])

    # frozen operating point: max recall on train subject to precision >= 0.5
    ths = np.unique(s_tr)[::-1]
    best_th, best_rec = 1.01, -1
    for t in ths:
        pred = s_tr >= t
        if pred.sum() == 0:
            continue
        prec = y[tr][pred].mean()
        rec = y[tr][pred].sum() / y[tr].sum()
        if prec >= 0.5 and rec > best_rec:
            best_rec, best_th = rec, t
    pred_te = s_te >= best_th
    te_prec = y[te][pred_te].mean() if pred_te.sum() else float("nan")
    te_rec = y[te][pred_te].sum() / y[te].sum()

    # baseline hand rule (docs/136 adapted: make-median as baseline)
    def hand_rule(idx):
        out = []
        for i in np.where(idx)[0]:
            r = rows[i]
            fire = (r["_steer_n"] >= 30 and r["steer_share"] >= 0.30 and r.get("_rel_ratio", 0) >= 2.0)
            out.append(1.0 if fire else 0.0)
        return np.array(out)

    hb = hand_rule(te)
    hb_prec = y[te][hb == 1].mean() if (hb == 1).sum() else float("nan")
    hb_rec = y[te][hb == 1].sum() / y[te].sum()

    lines = []
    p = lambda s: (print(s), lines.append(str(s)))
    p(f"universe cohorts (>=50 complaints): {len(universe):,}")
    p(f"positive cohorts labeled: {len(earliest):,} -> matched in universe: {len(pos_all):,} (match rate {matched_rate:.0%})")
    p(f"train: pos {y[tr].sum():.0f} / total {tr.sum():,} (prevalence {y[tr].mean():.3%})")
    p(f"test : pos {y[te].sum():.0f} / total {te.sum():,} (prevalence {y[te].mean():.3%})")
    p("")
    p(f"TEST PR-AUC : {pr_auc(y[te], s_te):.3f}   (no-skill = prevalence {y[te].mean():.3f})")
    p(f"TEST ROC-AUC: {roc_auc(y[te], s_te):.3f}")
    p(f"frozen operating point (train prec>=0.5): threshold={best_th:.4f}, train recall={best_rec:.2f}")
    p(f"TEST precision={te_prec:.2f}, recall={te_rec:.2f}, alerts={int(pred_te.sum())}/{int(te.sum())}")
    p(f"baseline hand rule (docs/136 adapted): TEST precision={hb_prec:.2f}, recall={hb_rec:.2f}, alerts={int((hb==1).sum())}")
    p("")
    p("coefficients (standardized):")
    for name, coef in zip(["bias"] + FEATURES, w):
        p(f"  {name:>12}: {coef:+.3f}")

    # EPS subset evaluation (docs/142 change 3): test positives from ELECTRIC/ASSIST campaigns
    eps_te = te & np.array([(y[i] == 0) or (meta[i] in eps_flag) for i in range(len(y))])
    p("")
    p(f"EPS-subset TEST (positives limited to ELECTRIC/ASSIST campaigns): pos {y[eps_te].sum():.0f} / total {eps_te.sum():,}")
    if y[eps_te].sum() >= 10:
        s_eps = predict(w, Xz[eps_te])
        pred_eps = s_eps >= best_th
        eps_prec = y[eps_te][pred_eps].mean() if pred_eps.sum() else float("nan")
        eps_rec = y[eps_te][pred_eps].sum() / y[eps_te].sum()
        p(f"  PR-AUC {pr_auc(y[eps_te], s_eps):.3f} (no-skill {y[eps_te].mean():.3f}), precision {eps_prec:.2f}, recall {eps_rec:.2f}")
    else:
        p("  insufficient EPS positives in test era for stable metrics")

    # lead sweep (model refit per lead on train era only, frozen procedure)
    p("")
    p("lead sweep (train-era-fit, test-era PR-AUC / recall at frozen-style operating point):")
    for lead in LEADS:
        Xl, yl, el, rl, _ = build(lead)
        trl, tel = el == "train", el == "test"
        mul, sdl = Xl[trl].mean(0), Xl[trl].std(0) + 1e-9
        Xzl = (Xl - mul) / sdl
        wl = logistic_fit(Xzl[trl], yl[trl])
        stl, sel = predict(wl, Xzl[trl]), predict(wl, Xzl[tel])
        ths = np.unique(stl)[::-1]
        bt, br = 1.01, -1
        for t in ths:
            pr = stl >= t
            if pr.sum() and yl[trl][pr].mean() >= 0.5:
                rc = yl[trl][pr].sum() / yl[trl].sum()
                if rc > br:
                    br, bt = rc, t
        pr_te = sel >= bt
        prec_l = yl[tel][pr_te].mean() if pr_te.sum() else float("nan")
        rec_l = yl[tel][pr_te].sum() / yl[tel].sum()
        p(f"  T = event - {lead:>2}mo: PR-AUC {pr_auc(yl[tel], sel):.3f}, precision {prec_l:.2f}, recall {rec_l:.2f}")

    OUT_TSV.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
