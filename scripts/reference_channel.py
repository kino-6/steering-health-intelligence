"""Does the second temperature give a single device a reference (docs/349)?

Detection works where a same-kind channel exists: docs/286 got eight of eight
with zero slow-side false alarms on the inverter. The NASA test is one device,
so it has no sibling. But its records carry a flange temperature as well as a
package temperature, and docs/302 named their difference as a candidate without
trying it. That difference tracks heat flow, so it responds to the device's own
dissipation through a path the operating point does not cover.

One term is added to the baseline and nothing else. docs/349 fixes the verdict
on the healthy alpha and the false alarms, not on fit quality, because adding a
term always improves the fit.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np
import scipy.io as sio

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from drift_shape import alpha, smooth

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "reference_channel.tsv"
ROBUST = 3.0 * 1.4826
BANK = [50, 100, 300]
HOUR = 36000.0


def read_with_flange(dev):
    """Ron, package temperature, flange temperature, run id. Conducting only."""
    z = zipfile.ZipFile(mos.ZIP)
    ron, tp, tf, rid = [], [], [], []
    for r in range(1, mos.N_RUNS + 1):
        name = f"MOSFET_Thermal_Overstress_Aging_v0/Test_{dev}_run_{r}.mat"
        p = mos.CACHE / name
        if not p.exists():
            z.extract(name, mos.CACHE)
        m = sio.loadmat(p, squeeze_me=True, struct_as_record=False)["measurement"]
        recs = np.ravel(m.steadyState)
        cur = np.array([float(x.timeDomain.drainCurrent) for x in recs])
        vds = np.array([float(x.timeDomain.drainSourceVoltage) for x in recs])
        pk = np.array([float(x.timeDomain.packageTemperature) for x in recs])
        fl = np.array([float(x.timeDomain.flangeTemperature) for x in recs])
        lo, hi = np.percentile(cur, 10), np.percentile(cur, 90)
        on = cur > (lo + hi) / 2
        if not on.any():
            continue
        ron.append(vds[on] / cur[on]); tp.append(pk[on]); tf.append(fl[on])
        rid.append(np.full(on.sum(), r))
    return (np.concatenate(ron), np.concatenate(tp),
            np.concatenate(tf), np.concatenate(rid))


def fit(y, X):
    """Least squares with an intercept. Returns residual in floors."""
    A = np.column_stack([X, np.ones(len(y))])
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ c
    g = float(ROBUST * np.median(np.abs(r - np.median(r))))
    return c, g


def run_detector(res, rid):
    """Level threshold on the slow side, as docs/315 ran it."""
    cal = rid <= 3
    k = int(cal.sum())
    design = 1.0 / HOUR / len(BANK)
    fa_hits = fa_n = 0
    fire = None
    for n in BANK:
        m = np.convolve(res, np.ones(n) / n, mode="valid")
        rr = rid[n - 1:]
        c = np.abs(m[rr <= 3])
        if len(c) < 20:
            continue
        q = min(1 - design, 1 - 1.0 / len(c))
        thr = float(np.quantile(c, q))
        r4 = rr == 4
        fa_hits += int((np.abs(m[r4]) > thr).sum()); fa_n = max(fa_n, int(r4.sum()))
        s = np.where((rr >= 5) & (np.abs(m) > thr))[0]
        if s.size:
            f = int(rr[s[0]])
            fire = f if fire is None else min(fire, f)
    fa = (fa_hits / fa_n * HOUR) if fa_n else float("nan")
    return fa, fire


def main() -> None:
    print("先に確認: フランジ温度は試験機のヒーターに従って run ごとに下がるか\n")
    print(f"{'素子':>8} " + " ".join(f"{'run'+str(r):>8}" for r in range(1, 8)))
    data = {}
    for dev in mos.DEVICES:
        ron, tp, tf, rid = read_with_flange(dev)
        data[dev] = (ron, tp, tf, rid)
        meds = [np.median(tf[rid == r]) if (rid == r).any() else np.nan
                for r in range(1, 8)]
        print(f"{dev:>8} " + " ".join(f"{v:>8.1f}" for v in meds))
    print("  run ごとに単調に下がるなら、試験機の操作を写している（T1 の危険）\n")

    print(f"{'素子':>8} {'α 現行':>8} {'α 追加後':>9} {'床 現行':>9} {'床 追加後':>10} "
          f"{'誤報 現行':>11} {'誤報 追加後':>12} {'発火 現行':>9} {'発火 追加後':>10}")
    print("-" * 96)
    rows, a0s, a1s, ok0, ok1 = [], [], [], 0, 0
    for dev in mos.DEVICES:
        ron, tp, tf, rid = data[dev]
        n1 = int((rid == 1).sum())
        fp = np.arange(len(ron)) < n1 // 2
        d = tf - tp
        c0, g0 = fit(ron[fp], tp[fp, None])
        c1, g1 = fit(ron[fp], np.column_stack([tp[fp], d[fp]]))
        r0 = (ron - (c0[0] * tp + c0[1])) / g0
        r1 = (ron - (c1[0] * tp + c1[1] * d + c1[2])) / g1
        h = rid <= 4
        a0, _ = alpha(smooth(r0[h])); a1, _ = alpha(smooth(r1[h]))
        f0, fire0 = run_detector(r0, rid)
        f1, fire1 = run_detector(r1, rid)
        base = max(f0, 1e-9)
        p0 = fire0 is not None
        p1 = fire1 is not None and f1 <= base * 3
        ok0 += p0; ok1 += p1
        a0s.append(a0); a1s.append(a1)
        print(f"{dev:>8} {a0:>8.2f} {a1:>9.2f} {g0:>9.4f} {g1:>10.4f} "
              f"{f0:>10.0f}/h {f1:>11.0f}/h {str(fire0):>9} {str(fire1):>10}")
        rows.append((dev, a0, a1, g0, g1, f0, f1, fire0, fire1))

    m0, m1 = float(np.median(a0s)), float(np.median(a1s))
    print(f"\n=== 事前登録した判定 ===")
    print(f"  R1 健全期の α が 1.2 未満: {m0:.2f} → {m1:.2f} "
          f"→ {'PASS' if m1 < 1.2 else 'FAIL'}")
    print(f"  R2 誤報 3 倍以内で 6 中 5 以上が発火: {ok1}/6 "
          f"→ {'PASS' if ok1 >= 5 else 'FAIL'}")
    print(f"  R3 いまの基準との比較: 発火 {ok0}/6 → {ok1}/6")
    print(f"  出荷時基準値: 56 → 60 バイト/チャネル（float32 が 1 つ増える）")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("device\talpha_now\talpha_new\tfloor_now\tfloor_new\t"
                 "fa_now\tfa_new\tfire_now\tfire_new\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
