#!/usr/bin/env python3
"""Does a model quantity cross the rig's own setpoint change? (docs/256 -> docs/257)

Executes the protocol pre-registered in docs/256 against NASA PCoE MOSFET
Thermal Overstress Aging (public domain), already inventoried.

Four analyses in this repo died the same way: the rig moved its setpoint and
that motion swamped the observable. docs/189 measured the thermal path
directly and found the sign reversed, because it divided by the device's own
13 W when external heating carries most of the flux.

A ratio removes the flux:

    index = (flange - package) / (package - ambient)

External heating raises numerator and denominator together, so lowering the
setpoint from 250 to 230 C should not move the index unless the device changed.
Ambient is not recorded, so it is assumed and swept (M3).

Runs are compared only at matched measured flange temperature, since each run
sweeps 40 -> 250 C rather than holding.

Criteria, fixed in docs/256 before any value was read: M1 the index is larger
in run 3 than run 1 for at least 5 of 6 devices, direction fixed in advance;
M2 the same comparison on the raw temperature difference, as a control; M3
whether M1 survives ambient assumed anywhere in 20-40 C.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import scipy.io as sio

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA = REPO_ROOT / ".nasa_pcoe" / "MOSFET_Thermal_Overstress_Aging_v0"
OUT_TSV = REPO_ROOT / "data" / "thermal_index.tsv"

DEVICES = ["Test_8", "Test_9", "Test_10", "Test_11", "Test_12", "Test_14"]
RUNS = [1, 3]
BANDS = [100.0, 150.0, 200.0, 220.0]     # flange temperature, docs/256
HALF = 5.0
AMBIENTS = [20.0, 25.0, 30.0, 35.0, 40.0]
AMB_BASE = 25.0
MIN_IN_BAND = 20


def load(dev: str, run: int):
    m = sio.loadmat(DATA / f"{dev}_run_{run}.mat", squeeze_me=True,
                    struct_as_record=False)["measurement"]
    tp, tf, cur = [], [], []
    for e in m.steadyState.flat:
        d = e.timeDomain
        tp.append(d.packageTemperature)
        tf.append(d.flangeTemperature)
        cur.append(d.drainCurrent)
    tp, tf, cur = np.array(tp), np.array(tf), np.array(cur)
    keep = cur > 0.01                     # the device dissipates nothing while off
    return tp[keep], tf[keep]


def band_median(tp, tf, band, amb):
    """Median index and raw difference among records whose flange sits in the band."""
    sel = np.abs(tf - band) <= HALF
    if sel.sum() < MIN_IN_BAND:
        return None, None, int(sel.sum())
    d = tf[sel] - tp[sel]
    den = tp[sel] - amb
    ok = den > 1.0
    if ok.sum() < MIN_IN_BAND:
        return None, None, int(ok.sum())
    return float(np.median(d[ok] / den[ok])), float(np.median(d)), int(ok.sum())


def main() -> None:
    cache = {(d, r): load(d, r) for d in DEVICES for r in RUNS}

    rows = []
    print(f"周囲温度 {AMB_BASE:.0f} °C を仮定した場合\n")
    print(f"{'素子':>8} {'帯':>6} {'指数 run1':>11} {'指数 run3':>11} {'向き':>6} "
          f"{'生の差 run1':>12} {'生の差 run3':>12} {'向き':>6}")
    print("-" * 82)

    idx_up = {d: 0 for d in DEVICES}
    raw_up = {d: 0 for d in DEVICES}
    idx_n = {d: 0 for d in DEVICES}

    for dev in DEVICES:
        for b in BANDS:
            vals = {}
            for r in RUNS:
                tp, tf = cache[(dev, r)]
                vals[r] = band_median(tp, tf, b, AMB_BASE)
            (i1, d1, n1), (i3, d3, n3) = vals[1], vals[3]
            if i1 is None or i3 is None:
                print(f"{dev:>8} {b:>5.0f}C   帯に十分な点が無い (n={n1}, {n3})")
                continue
            idx_n[dev] += 1
            up_i = "上" if i3 > i1 else "下"
            up_r = "上" if d3 > d1 else "下"
            if i3 > i1:
                idx_up[dev] += 1
            if d3 > d1:
                raw_up[dev] += 1
            print(f"{dev:>8} {b:>5.0f}C {i1:>11.4f} {i3:>11.4f} {up_i:>6} "
                  f"{d1:>11.2f}C {d3:>11.2f}C {up_r:>6}")
            rows.append({"device": dev, "band": b, "idx1": i1, "idx3": i3,
                         "raw1": d1, "raw3": d3, "n1": n1, "n3": n3})

    # a device counts as rising if the index rose in a majority of its bands
    def verdict(counter):
        return {d: (counter[d] > idx_n[d] / 2) for d in DEVICES if idx_n[d]}

    vi, vr = verdict(idx_up), verdict(raw_up)
    print(f"\n=== M1 指数: run3 > run1 の素子 ===")
    for d in DEVICES:
        if d in vi:
            print(f"  {d:>8}: {idx_up[d]}/{idx_n[d]} 帯で上昇 -> {'上' if vi[d] else '下'}")
    n_up = sum(vi.values())
    print(f"  **{n_up}/{len(vi)}**  {'PASS' if n_up >= 5 else 'FAIL'} (基準: 6中5以上)")

    print(f"\n=== M2 生の温度差(対照) ===")
    for d in DEVICES:
        if d in vr:
            print(f"  {d:>8}: {raw_up[d]}/{idx_n[d]} 帯で上昇 -> {'上' if vr[d] else '下'}")
    print(f"  {sum(vr.values())}/{len(vr)} 素子で上昇")

    print(f"\n=== M3 仮定した周囲温度への依存 ===")
    for amb in AMBIENTS:
        up = 0
        for dev in DEVICES:
            c = t = 0
            for b in BANDS:
                i1, _, _ = band_median(*cache[(dev, 1)], b, amb)
                i3, _, _ = band_median(*cache[(dev, 3)], b, amb)
                if i1 is None or i3 is None:
                    continue
                t += 1
                c += i3 > i1
            if t and c > t / 2:
                up += 1
        print(f"  周囲 {amb:>4.0f} °C -> {up}/6 素子で上昇  "
              f"{'PASS' if up >= 5 else 'FAIL'}")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with OUT_TSV.open("w") as fh:
        fh.write("device\tflange_band_C\tindex_run1\tindex_run3\t"
                 "raw_diff_run1_C\traw_diff_run3_C\tn_run1\tn_run3\n")
        for r in rows:
            fh.write(f"{r['device']}\t{r['band']:.0f}\t{r['idx1']:.5f}\t{r['idx3']:.5f}\t"
                     f"{r['raw1']:.3f}\t{r['raw3']:.3f}\t{r['n1']}\t{r['n3']}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
