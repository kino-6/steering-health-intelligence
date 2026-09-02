#!/usr/bin/env python3
"""What a fitted unit emits, and what it misses (docs/292 -> docs/293).

Three parts, pre-registered in docs/292.

    D1  how much of the time the element can say anything at all, since it
        declines outside the range its fingerprint was swept over
    D2  the user's objection made testable: the element judges each channel on
        its own, so a fault that leaves every marginal intact and breaks only
        the relationship between channels should be invisible to it. Swapping
        two channels' values does exactly that and cannot change a marginal.
    D3  one key-on to key-off, printed as the message that goes to the
        operation-phase clause docs/267 mapped

Data: Bacha et al., inverter-driven PMSM fault dataset, CC BY 4.0.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eps_health_recorder as ehr
from demo_recorder import SIBLINGS, as_dicts
from inverter_recorder import ZIP, BASE, COLS, OPCOL, read
from ml_comparison import features

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "demo_sotif_signal.tsv"
SWAPS = [("Ia", "Ib"), ("T1", "T2")]
# Swapping siblings is not the test it looks like: differencing turns a
# relational change into a marginal one, so the element sees it. A channel with
# no sibling is the honest case -- shuffling its time order preserves its
# marginal exactly and destroys every relation it has.
SHUFFLE = ["Idc", "Vdc", "Vd"]


def widen(fp: ehr.Fingerprint, factor: float) -> ehr.Fingerprint:
    """The same fingerprint with its declared range widened, for D1."""
    out = ehr.Fingerprint(sample_hz=fp.sample_hz)
    for n, c in fp.channels.items():
        mid, half = (c.op_lo + c.op_hi) / 2, (c.op_hi - c.op_lo) / 2 * factor
        out.channels[n] = ehr.ChannelFingerprint(
            c.name, c.slope, c.intercept, c.floor, mid - half, mid + half,
            c.thr_fast_mean, c.thr_fast_max, c.thr_slow,
            c.alarm_per_hour_fast, c.alarm_per_hour_slow, c.cv_shift,
            c.admitted, c.siblings)
    return out


def swapped(a: np.ndarray, x: str, y: str) -> np.ndarray:
    """Exchange two channels. Neither marginal distribution changes."""
    b = a.copy()
    i, j = COLS.index(x), COLS.index(y)
    b[:, [i, j]] = b[:, [j, i]]
    return b


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    names = [n for n in z.namelist() if n.startswith(BASE) and n.endswith(".txt")]
    normal = read(z, next(n for n in names if "normal_operation" in n))
    faults = {Path(f).stem: read(z, f)
              for f in sorted(n for n in names if "fault_scenarios" in n)}
    half = len(normal) // 2
    fp = ehr.enrol(*as_dicts(normal[:half]), siblings=SIBLINGS, alarm_per_hour=1.0)
    ach = max(max(c.alarm_per_hour_fast, c.alarm_per_hour_slow)
              for c in fp.channels.values())
    rows = []

    # ---------------------------------------------------------------- D1
    print("=== D1 そもそも宣言できる時間の割合 ===")
    print(f"{'掃引幅':>8} {'宣言しない':>11} {'割合':>8}")
    print("-" * 32)
    hold = as_dicts(normal[half:])
    all_f = np.vstack([v for v in faults.values() if v is not None])
    every = as_dicts(all_f)
    for factor in (1.0, 2.0, 5.0):
        f2 = widen(fp, factor)
        rs = ehr.Recorder(f2).run_session(*every, siblings=SIBLINGS,
                                          alarm_per_hour=ach)
        sil = sum(1 for r in rs if not r.validity)
        frac = sil / max(1, len(rs))
        print(f"{'×' + str(factor):>8} {sil:>11} {frac:>7.1%}")
        rows.append({"part": "D1", "key": f"x{factor}", "value": f"{frac:.4f}"})
    base = rows[0]["value"]
    print(f"\n  そのままの掃引幅で宣言しない割合 {float(base):.1%}  "
          f"{'指摘のとおり(10%超)' if float(base) > 0.10 else '10%以下'}")

    # ---------------------------------------------------------------- D2
    print(f"\n=== D2 チャネル同士の関係だけを壊した故障 ===")
    X_fit = features(normal[:half])
    mu, sd = X_fit.mean(axis=0), X_fit.std(axis=0) + 1e-12
    iso = IsolationForest(random_state=20260902, n_estimators=200).fit((X_fit - mu) / sd)
    s_fit = -iso.score_samples((X_fit - mu) / sd)
    thr_iso = float(np.quantile(s_fit, 1 - 1.0 / len(s_fit)))

    print(f"{'入れ替えた組':>16} {'周辺分布':>10} {'単変量(記録器)':>16} "
          f"{'多変量(Isolation Forest)':>24}")
    print("-" * 74)
    for x, y in SWAPS:
        a = swapped(normal[half:], x, y)
        same = np.allclose(np.sort(a[:, COLS.index(x)]),
                           np.sort(normal[half:, COLS.index(y)]))
        rs = ehr.Recorder(fp).run_session(*as_dicts(a), siblings=SIBLINGS,
                                          alarm_per_hour=ach)
        uni = ehr.fired(rs)
        xf = features(a)
        multi = bool(xf is not None and
                     float(np.max(-iso.score_samples((xf - mu) / sd))) > thr_iso)
        print(f"{x + ' <-> ' + y:>16} {('変わらず' if same else '変わった'):>10} "
              f"{('検出' if uni else '**取り逃す**'):>16} "
              f"{('検出' if multi else '取り逃す'):>24}")
        rows.append({"part": "D2", "key": f"{x}<->{y}",
                     "value": f"uni={int(uni)},multi={int(multi)}"})

    print(f"\n  同種チャネルを持たない量で、時間順だけを壊す")
    print(f"  (周辺分布は厳密に不変。他のチャネルとの関係だけが消える)")
    print(f"{'壊した量':>16} {'同種':>8} {'単変量(記録器)':>16} "
          f"{'多変量(Isolation Forest)':>24}")
    print("-" * 70)
    rng = np.random.default_rng(20260902)
    for col in SHUFFLE:
        a = normal[half:].copy()
        i = COLS.index(col)
        a[:, i] = rng.permutation(a[:, i])
        rs = ehr.Recorder(fp).run_session(*as_dicts(a), siblings=SIBLINGS,
                                          alarm_per_hour=ach)
        uni = ehr.fired(rs)
        xf = features(a)
        multi = bool(xf is not None and
                     float(np.max(-iso.score_samples((xf - mu) / sd))) > thr_iso)
        sib = ",".join(SIBLINGS.get(col, ())) or "無し"
        print(f"{col:>16} {sib:>8} "
              f"{('検出' if uni else '**取り逃す**'):>16} "
              f"{('検出' if multi else '取り逃す'):>24}")
        rows.append({"part": "D2b", "key": f"shuffle_{col}",
                     "value": f"uni={int(uni)},multi={int(multi)}"})

    # ---------------------------------------------------------------- D3
    print(f"\n=== D3 搭載時に出るもの(1回のキーオンからキーオフまで) ===")
    print(f"出荷時: {len(fp.admitted)} チャネルを採用、指紋 {len(fp.pack())} バイト、"
          f"較正できた誤報 {ach:.1f} 件/時\n")
    session = np.vstack([normal[half:half + 600], faults["HB1_LOW_SIDE_SC"]])
    rs = ehr.Recorder(fp).run_session(*as_dicts(session), siblings=SIBLINGS,
                                      alarm_per_hour=ach)
    shown = 0
    for r in rs:
        if r.validity and r.flags:
            print("  " + r.describe())
            shown += 1
            if shown >= 4:
                break
    first = next((r for r in rs if r.validity and r.flags), None)
    if first:
        print(f"\n  運用フェーズへ送る1件({len(first.pack())} バイト):")
        print(f"    逸脱          : {first.deviation:.2f}(この個体の床の倍数)")
        print(f"    宣言粒度      : {first.granularity:.4g}(出荷時の床)")
        print(f"    有効性        : {'宣言する' if first.validity else '宣言しない'}")
        print(f"    動作点        : {first.operating_point:.1f}")
        print(f"    経過時間      : {first.seconds_since_key_on} 秒(キーオンから)")
        print(f"    持続          : {'キーオフまで' if first.flags & 1 else '継続中'}")
        print(f"    載せないもの  : 能力値・予測・故障箇所・余寿命"
              f"(検査が機械的に止める)")
        rows.append({"part": "D3", "key": "record_bytes",
                     "value": str(len(first.pack()))})

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("part\tkey\tvalue\n")
        for r in rows:
            fh.write(f"{r['part']}\t{r['key']}\t{r['value']}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
