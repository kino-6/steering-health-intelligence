#!/usr/bin/env python3
"""Replication on two machines never opened before (docs/202 -> docs/203).

Executes the protocol pre-registered in docs/202 without modification.

Every winding-side conclusion up to docs/201 rested on the 1.0 kW machine.
The same Mendeley release holds 1.5 kW and 3.0 kW, which docs/202 was written
and committed before downloading. So exploration and confirmation sit on
different data for the first time in this work:

  X1  does the capability rule reproduce on inter-turn shorts,
      rho <= -0.8 on BOTH new machines
  X2  docs/201 says current does not track coil-to-coil shorts. A claim of no
      effect cannot be confirmed, only refuted: |rho| >= 0.8 on both machines
      would refute it
  X3  the direction hypothesis from docs/201 -- vibration at 2*f0 falls with
      inter-turn severity and rises with coil-to-coil. Generated on 1.0 kW, so
      1.0 kW is barred from confirming it. All four machine-by-fault cells
      must agree; three of four is not a pass (docs/202)

Session stratification is pre-registered here rather than applied afterwards.
docs/201 established that polarity-flipped records sit at their own level
whatever the severity, so only the session holding the healthy record is
analysed. A new machine whose session structure differs makes the affected
question fail instead of being worked around.

Data: KAIST three-phase PMSM stator fault dataset, CC BY 4.0,
Mendeley 10.17632/rgn5brrgrn.5.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

import numpy as np
from nptdms import TdmsFile
from scipy import stats

import pmsm_measured_signature as sig
from motor_fault_types_and_vibration import (
    FS_I, FS_V, SUB_N, WINDOW_S, current_features, vib_features,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / ".pmsm_fault"
OUT_TSV = REPO_ROOT / "data" / "cross_machine_replication.tsv"

MACHINES = ["1.5kW", "3.0kW"]                 # 1.0kW is barred from confirming X3
NAME = re.compile(r"(\d+)W_(\d+)[._](\d+)_(current|vibration)_(interturn|intercoil)\.tdms",
                  re.I)


def load(z, name: str, fs: float):
    p = CACHE / name
    if not p.exists():
        z.extract(name, CACHE)
    grp = TdmsFile.read(p)["Log"]
    data = [np.asarray(c[:], dtype=np.float64) for c in grp.channels()]
    n = min(len(d) for d in data)
    w = int(WINDOW_S * fs)
    s = (n - w) // 2
    return [d[s:s + w] - d[s:s + w].mean() for d in data]


def sub_windows(arrs, fn):
    n = len(arrs[0]) // SUB_N
    return np.array([fn([a[i * n:(i + 1) * n] for a in arrs]) for i in range(SUB_N)])


def read_machine(tag: str):
    zp = CACHE / f"{tag}.zip"
    if not zp.exists():
        return None
    z = zipfile.ZipFile(zp)
    rec = {}
    for name in sorted(n for n in z.namelist() if n.lower().endswith(".tdms")):
        m = NAME.search(Path(name).name)
        if not m:
            print(f"   skipped unparsed name: {Path(name).name}")
            continue
        sev = float(f"{m.group(2)}.{m.group(3)}")
        chan, ftype = m.group(4).lower(), m.group(5).lower()
        if chan == "current":
            ph = load(z, name, FS_I)
            f0 = sig.find_f0(ph)
            h, i2, flipped = current_features(ph, f0)
            rec[(ftype, sev, "current")] = dict(
                H=h, I2=i2, f0=f0, flipped=flipped,
                Hs=sub_windows(ph, lambda a: current_features(a, f0)[0]))
        else:
            x = load(z, name, FS_V)[0]
            rec[(ftype, sev, "vibration")] = dict(x=x)
    # electrical frequency comes from the current records of this machine
    f0s = [v["f0"] for k, v in rec.items() if k[2] == "current"]
    f0 = float(np.median(f0s)) if f0s else float("nan")
    for k, v in list(rec.items()):
        if k[2] == "vibration":
            v1, v2 = vib_features(v["x"], f0)
            v["V1"], v["V2"] = v1, v2
            v["V1s"] = sub_windows([v["x"]], lambda a: vib_features(a[0], f0)[0])
            del v["x"]
    return rec, f0


def main() -> None:
    rows, verdict = [], {}
    for tag in MACHINES:
        out = read_machine(tag)
        if out is None:
            print(f"{tag}: archive not present -- cannot evaluate")
            return
        rec, f0 = out
        print("=" * 88)
        print(f"{tag}   electrical frequency {f0:.1f} Hz")
        print("=" * 88)
        for ftype in ("interturn", "intercoil"):
            sevs = sorted({s for (f, s, c) in rec if f == ftype and c == "current"})
            if not sevs or 0.0 not in sevs:
                print(f"  {ftype}: no healthy record -- question fails for this cell")
                verdict[(tag, ftype)] = None
                continue
            flips = {s: rec[(ftype, s, "current")]["flipped"] for s in sevs}
            keep = [s for s in sevs if flips[s] == flips[0.0]]
            print(f"\n  {ftype}  severities {sevs}")
            print(f"  session of the healthy record keeps {keep} "
                  f"(dropped {[s for s in sevs if s not in keep]})")
            bi = rec[(ftype, 0.0, "current")]
            bv = rec.get((ftype, 0.0, "vibration"))
            print(f"  {'sev%':>8}{'C1':>10}{'gC1':>9}{'V1':>10}{'gV1':>9}")
            c1s, v1s, ks = [], [], []
            for s in keep:
                c = rec[(ftype, s, "current")]
                C1 = c["H"] / bi["H"]
                gC1 = 3 * float(np.std(c["Hs"] / np.mean(bi["Hs"]), ddof=1))
                v = rec.get((ftype, s, "vibration"))
                if v is None or bv is None:
                    V1 = gV1 = float("nan")
                else:
                    V1 = v["V1"] / bv["V1"]
                    gV1 = 3 * float(np.std(v["V1s"] / np.mean(bv["V1s"]), ddof=1))
                c1s.append(C1); v1s.append(V1); ks.append(s)
                print(f"  {s:>8.2f}{C1:>10.4f}{gC1:>9.4f}{V1:>10.3f}{gV1:>9.3f}")
                rows.append((tag, ftype, s, C1, gC1, V1, gV1, int(flips[s])))
            rc = float(stats.spearmanr(ks, c1s).statistic) if len(ks) > 2 else float("nan")
            rv = (float(stats.spearmanr(ks, v1s).statistic)
                  if len(ks) > 2 and not np.isnan(v1s).any() else float("nan"))
            print(f"    current   rho = {rc:+.3f}")
            print(f"    vibration rho = {rv:+.3f}   "
                  f"direction {'down' if rv < 0 else 'up'}")
            verdict[(tag, ftype)] = dict(rc=rc, rv=rv, n=len(ks))

    print("\n" + "=" * 88)
    it = [verdict.get((t, "interturn")) for t in MACHINES]
    ic = [verdict.get((t, "intercoil")) for t in MACHINES]
    x1 = all(v and v["rc"] <= -0.8 for v in it)
    print(f"X1 capability rule reproduces on inter-turn (rho <= -0.80 on both): "
          f"{[None if v is None else round(v['rc'], 3) for v in it]} -> "
          f"{'PASS' if x1 else 'FAIL'}")
    x2 = all(v and abs(v["rc"]) >= 0.8 for v in ic)
    print(f"X2 docs/201 refuted? current tracks coil-to-coil on both: "
          f"{[None if v is None else round(v['rc'], 3) for v in ic]} -> "
          f"{'REFUTED' if x2 else 'not refuted'}")
    cells = [(t, f, verdict.get((t, f))) for t in MACHINES
             for f in ("interturn", "intercoil")]
    want = {"interturn": -1, "intercoil": +1}
    ok = [(t, f, v is not None and not np.isnan(v["rv"])
           and np.sign(v["rv"]) == want[f]) for t, f, v in cells]
    x3 = all(o for _, _, o in ok)
    print(f"X3 vibration direction, all 4 cells must agree:")
    for t, f, o in ok:
        v = verdict.get((t, f))
        print(f"     {t:>6} {f:<10} rho = "
              f"{'n/a' if v is None else format(v['rv'], '+.3f')}  "
              f"expected {'down' if want[f] < 0 else 'up':<4} -> {'ok' if o else 'MISMATCH'}")
    print(f"   -> {'CONFIRMED' if x3 else 'NOT CONFIRMED'}")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("machine\tfault_type\tseverity\tC1\tgC1\tV1\tgV1\tpolarity_flipped\n")
        for r in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
