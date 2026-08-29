#!/usr/bin/env python3
"""How much does averaging buy on a real vehicle? (docs/222 -> docs/223)

Executes the protocol pre-registered in docs/222 without modification.

docs/221 measured a per-sample floor and asserted, without measuring, that a
window would lower it. docs/144 and docs/155 claim a 0.10 m/s^2 offset is
detectable, and that claim fills the EooC sheet's granularity row, so the
window length actually needed on a road is the number that connects them.

    g(N) = 3 * 1.4826 * MAD( means of non-overlapping N-sample blocks )
    r(N) = g(N) / ( g(1) / sqrt(N) )        1 if the residual is white

Correlated disturbance does not average down as one over root N, and r(N)
measures how far off that assumption is.

Also: the Audi Q3 is the only model carrying two EPS firmware versions, so it
is the only place to ask whether firmware moves the floor -- which would mean
a per-unit baseline has to be retaken after an update. It cannot isolate
firmware from the cars and the driving that came with it.

Data: commaSteeringControl, comma.ai, MIT License. 10 Hz, 60 s per log.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / ".public_log_cache"
OUT_TSV = REPO_ROOT / "data" / "window_and_firmware.tsv"

NS = [1, 2, 5, 10, 20, 50, 100]      # docs/222; 100 samples = 10 s, capped there
TARGET = 0.10                        # m/s^2, the offset docs/144 claims to detect
MIN_SAMPLES = 100
ROBUST = 3.0 * 1.4826


def mad_g(x: np.ndarray) -> float:
    return float(ROBUST * np.median(np.abs(x - np.median(x))))


def read_log(path: Path):
    d, l, act, pressed, fw = [], [], [], [], ""
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                act.append(row["latActive"] == "True")
                pressed.append(row["steeringPressed"] == "True")
                d.append(float(row["latAccelDesired"]))
                l.append(float(row["latAccelLocalizer"]))
                fw = row.get("epsFwVersion", "")
            except (ValueError, KeyError):
                return None
    keep = np.array(act) & ~np.array(pressed)
    if keep.sum() < MIN_SAMPLES:
        return None
    return (np.array(l)[keep] - np.array(d)[keep]), fw


def block_g(e: np.ndarray, n: int):
    k = len(e) // n
    if k < 5:                       # fewer than five blocks is not a spread
        return None
    return mad_g(e[:k * n].reshape(k, n).mean(axis=1))


def main() -> None:
    per_model = defaultdict(lambda: defaultdict(list))
    fw_groups = defaultdict(list)
    for model in sorted(p.name for p in CACHE.iterdir() if p.is_dir()):
        for f in sorted((CACHE / model).glob("*.csv")):
            r = read_log(f)
            if r is None:
                continue
            e, fw = r
            for n in NS:
                g = block_g(e, n)
                if g and g > 0:
                    per_model[model][n].append(g)
            g1 = block_g(e, 1)
            if g1:
                fw_groups[(model, fw)].append(g1)

    print(f"{'model':<24}" + "".join(f"{'N='+str(n):>10}" for n in NS))
    rows = []
    for model, byn in per_model.items():
        med = {n: float(np.median(byn[n])) for n in NS if byn[n]}
        print(f"{model:<24}" + "".join(f"{med.get(n, float('nan')):>10.4f}" for n in NS))
        r = {n: med[n] / (med[1] / np.sqrt(n)) for n in NS if n in med and 1 in med}
        print(f"{'  r(N) vs white noise':<24}"
              + "".join(f"{r.get(n, float('nan')):>10.2f}" for n in NS))
        reach = next((n for n in NS if med.get(n, 9e9) < TARGET), None)
        print(f"{'  reaches 0.10 m/s^2 at':<24}"
              + (f" N={reach} ({reach/10:.1f} s)" if reach
                 else f" not within N={NS[-1]} ({NS[-1]/10:.0f} s)"))
        rows.append((model, *[med.get(n, float("nan")) for n in NS],
                     r.get(NS[-1], float("nan")), reach or -1))
        print()

    r100 = [row[-2] for row in rows]
    w1 = sum(1 for x in r100 if x >= 1.5)
    print("=" * 76)
    print(f"W1 r(100) >= 1.5 (averaging buys less than white noise): "
          f"{w1}/{len(rows)} -> {'PASS' if w1 == len(rows) else 'FAIL'} (needs all)")
    if w1 != len(rows):
        print("   -> the residual is closer to white than feared; averaging works as")
        print("      assumed, which STRENGTHENS docs/144 (docs/222 anticipated this).")
    print("W2 window needed for 0.10 m/s^2: "
          + ", ".join(f"{row[0].split('_')[0]}="
                      + (f"{row[-1]/10:.1f}s" if row[-1] > 0 else ">10s") for row in rows))

    print("\nW3 firmware, Audi Q3 only (the only model with two versions)")
    q3 = {k: v for k, v in fw_groups.items()
          if k[0] == "AUDI_Q3_2ND_GEN" and len(v) >= 30}
    if len(q3) < 2:
        print("   fewer than two qualifying groups -- untestable")
    else:
        meds = []
        for (model, fw), v in sorted(q3.items(), key=lambda kv: -len(kv[1])):
            m = float(np.median(v))
            meds.append(m)
            print(f"   n={len(v):>4}  g(1) median {m:.4f}   fw {fw[:44]}")
        ratio = max(meds) / min(meds)
        print(f"   ratio {ratio:.2f} -> "
              f"{'firmware moves the floor' if ratio >= 1.2 else 'no difference at the 1.2 bar'}")
        print("   (cannot isolate firmware from the cars and driving that came with it)")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("model\t" + "\t".join(f"g_N{n}" for n in NS) + "\tr_N100\treach_N\n")
        for r_ in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r_) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
