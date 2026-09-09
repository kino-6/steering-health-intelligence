"""A simulated power module, so detection has a ground truth (docs/343).

Six real devices cannot give a detection limit: the onset time and the rate are
unknown, and the held-out healthy interval is 0.07 hours. "2 to 5 of 6" is a
tally, not a limit. A simulated module knows when degradation starts, how fast
it goes, and has as much healthy time as needed.

Only three quantities come from the real devices -- the temperature
coefficient, the noise floor, and the size of the healthy drift. The rest is
chosen, and docs/343 lists it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from boundary_vs_refresh import series, line

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "virtual_module.tsv"

N_UNITS = 200
# docs/321: a threshold is a quantile of k windows and cannot be finer than
# 1/k. One alarm per hour at 720 windows per hour needs 720 enrolment windows,
# which is one hour. The first version used ten minutes and could not get below
# 6 alarms per hour, so Z1 failed on false alarms rather than on detection.
ENROL = 36000             # 1 hour of end-of-line sweep
N_SAMP = ENROL + 72000    # plus 2 hours of running
FAST = 50
# accumulated degradation over the running period, in units of the accumulated
# healthy drift over the same period. docs/315 measured the real ratio this
# way (0.2 floors of drift against 0.7 of onset), so the two are comparable.
RATES = [0.25, 0.5, 1, 2, 4, 8, 16]
SEED = 343
HOUR = 36000.0


def measured_constants():
    """Temperature coefficient, noise floor and healthy drift, from the data."""
    slopes, floors, drifts = [], [], []
    for dev in mos.DEVICES:
        y, op, rid, _s, n1 = series(dev)
        fp = np.arange(len(y)) < n1 // 2
        a, b, g = line(y[fp], op[fp])
        if g <= 0:
            continue
        slopes.append(a); floors.append(g)
        # healthy drift: how far the residual's running mean wanders in runs 1-4,
        # in floors, per sample
        h = (rid <= 4)
        r = (y[h] - (a * op[h] + b)) / g
        w = 500
        m = np.convolve(r, np.ones(w) / w, mode="valid")
        # accumulated wander over the healthy period, in floors
        drifts.append(float(m.max() - m.min()))
    return (float(np.median(slopes)), float(np.median(floors)),
            float(np.median(drifts)))


def make_units(rng, drift, rate, n=N_UNITS):
    """Half healthy, half degrading from a random onset. Truth is returned."""
    t = np.arange(N_SAMP)
    # operating point: driving and parked, a cycle of about 20 minutes
    base = 90 + 45 * np.sin(2 * np.pi * t / 12000) ** 2
    d = np.empty((n, N_SAMP))
    degrading = np.zeros(n, bool)
    onset = np.full(n, -1)
    run_len = N_SAMP - ENROL
    step = drift / np.sqrt(run_len)          # walk accumulating `drift` floors
    for i in range(n):
        walk = np.cumsum(rng.normal(0, step, N_SAMP))        # healthy drift
        noise = rng.normal(0, 1.0, N_SAMP)                   # one floor of noise
        dev = walk + noise
        if i % 2 == 1:
            degrading[i] = True
            o = int(rng.uniform(ENROL + 6000, N_SAMP - 18000))
            onset[i] = o
            ramp = np.zeros(N_SAMP)
            # accumulate rate*drift floors from onset to the end
            ramp[o:] = np.linspace(0, drift * rate, N_SAMP - o)
            dev = dev + ramp
        d[i] = dev
    return d, base, degrading, onset


def evaluate(d, degrading, target_per_hour=1.0):
    """Enrol on the first block, then run. Returns detection and false alarms."""
    n = d.shape[0]
    hit = np.zeros(n, bool)
    fa = np.zeros(n)
    for i in range(n):
        cal = d[i, :ENROL]
        k = ENROL // FAST
        w = np.abs(cal[: k * FAST].reshape(k, FAST).mean(axis=1))
        q = max(target_per_hour / (HOUR / FAST), 1.0 / k)
        thr = float(np.quantile(w, 1 - q))
        run = d[i, ENROL:]
        m = len(run) // FAST
        ww = np.abs(run[: m * FAST].reshape(m, FAST).mean(axis=1))
        fired = ww > thr
        hit[i] = bool(fired.any())
        fa[i] = fired.sum() / (m * FAST / HOUR)
    det = float(hit[degrading].mean())
    false = float(np.median(fa[~degrading]))
    return det, false


def main() -> None:
    a, g, drift = measured_constants()
    print(f"実測から取った 3 つ: 温度係数 {a:+.5f} / ノイズ床 {g:.3f} / "
          f"健全期に漂う量 {drift:.3f} 床\n")
    rng = np.random.default_rng(SEED)
    print(f"{'劣化速度 D':>12} {'検出率':>9} {'健全群の誤検知':>15} {'Z1 条件':>10}")
    print("-" * 52)
    rows, z1 = [], None
    for rate in RATES:
        d, base, degrading, onset = make_units(rng, drift, rate)
        det, false = evaluate(d, degrading)
        ok = det >= 0.90 and false <= 1.0
        if ok and z1 is None:
            z1 = rate
        print(f"{rate:>12g} {det:>8.1%} {false:>13.1f}/h "
              f"{'満たす' if ok else '':>10}")
        rows.append((rate, det, false, int(ok)))

    print()
    if z1 is None:
        bad = "誤検知" if any(r[1] >= 0.90 for r in rows) else "検出率"
        print(f"  Z1 該当なし。**{bad}の側で条件を満たせない**")
    else:
        print(f"  Z1 検出限界: **劣化速度が健全期の漂流の {z1} 倍以上**なら、"
              f"誤検知 1 件/時 以下で 90% 検出できる")

    # Z3: where do the real devices sit on this scale?
    print(f"\nZ3 実素子 6 個を同じ物差しで測る")
    print(f"{'素子':>8} {'劣化の累積':>12} {'健全期の累積':>13} {'比 D':>8}")
    reals = []
    for dev in mos.DEVICES:
        y, op, rid, _s, n1 = series(dev)
        fp = np.arange(len(y)) < n1 // 2
        aa, bb, gg = line(y[fp], op[fp])
        if gg <= 0:
            continue
        r = (y - (aa * op + bb)) / gg
        w = 500
        m = np.convolve(r, np.ones(w) / w, mode="valid")
        rr = rid[w - 1:]
        early = m[rr <= 4]
        late = m[rr >= 5]
        dh = float(early.max() - early.min())     # accumulated healthy drift
        dg = float(abs(late[-1] - late[0]))       # accumulated degradation
        reals.append(dg / dh if dh > 0 else float("nan"))
        print(f"{dev:>8} {dg:>12.2e} {dh:>13.2e} {reals[-1]:>8.2f}")
    med = float(np.median(reals))
    print(f"  中央値 D = {med:.2f}")
    if z1 is not None:
        print(f"  → 限界 {z1} の{'下' if med < z1 else '上'}にある。"
              + ("**実素子の劣化は、検出できる速度に達していない**"
                 if med < z1 else "**速度は足りている。別の問題がある**"))

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("rate\tdetection\tfalse_per_hour\tmeets_z1\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
