#!/usr/bin/env python3
"""How fine an alarm rate can each dataset actually express? (docs/284)

The user asked what "an hour of held operating point" is actually about. This
makes it concrete: a threshold is a quantile of the fingerprint interval, and a
sample of k values cannot express a rate finer than 1/k. So each dataset has a
hard floor on the alarm rate it can calibrate, whatever the algorithm does.

At 10 Hz one alarm per hour is one decision in 36,000, so a fingerprint holding
fewer than 36,000 decisions cannot calibrate that target at all -- not because
the signal is weak but because the quantile does not exist in the sample.

No new acquisition; every number comes from data already inventoried.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from real_degradation import device_series, FP_FRAC

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "calibration_budget.tsv"
HOUR = 36000            # decisions per hour at 10 Hz
TARGET_PER_HOUR = 1.0


def main() -> None:
    rows = []

    n = []
    for d in mos.DEVICES:
        y, t, r = device_series(d)
        n.append(int(int((r == 1).sum()) * FP_FRAC))
    rows.append(("NASA MOSFET (6素子)", int(np.median(n)), "docs/269"))

    try:
        from igbt_recorder import device_arrays
        a = device_arrays()
        rows.append(("NASA IGBT (4素子)",
                     int(np.median([int(len(x) / 3) for x in a.values()])), "docs/282"))
    except Exception:
        pass

    try:
        from inverter_recorder import ZIP, BASE, read
        z = zipfile.ZipFile(ZIP)
        nm = [x for x in z.namelist()
              if "normal_operation" in x and x.endswith(".txt")][0]
        rows.append(("実インバータ (正常運転)", len(read(z, nm)) // 2, "docs/278"))
    except Exception:
        pass

    rows.append(("commaSteeringControl (1ログ)", 600, "docs/229"))

    print("閾値は指紋区間の分位点である。k個の標本は 1/k より細かい率を表現できない。\n")
    print(f"{'データセット':>26} {'指紋区間':>10} {'刻める最小率':>12} "
          f"{'= 1時間あたり':>13} {'目標との差':>10}")
    print("-" * 78)
    for name, k, src in rows:
        q = 1.0 / k
        per_hour = q * HOUR
        print(f"{name:>26} {k:>10,} {q:>11.2%} {per_hour:>12.0f}件 "
              f"{per_hour / TARGET_PER_HOUR:>9.0f}倍")
    print(f"{'**要件**':>26} {HOUR:>10,} {1/HOUR:>11.4%} "
          f"{TARGET_PER_HOUR:>12.0f}件 {1:>9.0f}倍")

    best = min(rows, key=lambda r: 1.0 / r[1] * HOUR)
    print(f"\n手元で最も細かく刻めるのは {best[0]} で、"
          f"1時間あたり {1.0/best[1]*HOUR:.0f} 件。**目標の {1.0/best[1]*HOUR:.0f} 倍粗い。**")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("dataset\tfingerprint_samples\tfinest_rate\tper_hour\tsource\n")
        for name, k, src in rows:
            fh.write(f"{name}\t{k}\t{1.0/k:.8f}\t{1.0/k*HOUR:.2f}\t{src}\n")
        fh.write(f"要件\t{HOUR}\t{1/HOUR:.8f}\t{TARGET_PER_HOUR:.2f}\tdocs/282\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
