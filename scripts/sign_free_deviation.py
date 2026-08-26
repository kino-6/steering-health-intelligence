#!/usr/bin/env python3
"""Does a sign-free deviation indicator travel between machines? (docs/204 -> docs/205)

Executes the protocol pre-registered in docs/204 without modification.

docs/203 found the same normalised observable moving down with inter-turn
severity on one machine and up on another. The magnitude clears granularity
everywhere; only the direction refuses to agree. A capability value needs a
sign; noticing that a unit has departed from its own baseline does not. So
the capability declaration is dropped and what is tested here is the sign-free
form -- the same quantity docs/167 reported as a 20-300x margin on the NASA
parts.

    g0    = 3 * sd of F over ten 2 s sub-windows of the HEALTHY record
    D(s)  = | F(s) - F(0) | / g0        how many of its own noise widths away

Four features, five evaluable cells (3.0 kW coil-to-coil has its healthy
record alone on its recording date, so it cannot be evaluated). A feature
counts only if it is monotone in ALL five and clears 3 in ALL five.

C1 and V1 were already seen on every machine in docs/201 and docs/203; C2 and
V2 were seen only on 1.0 kW. Only the latter two are blind here, and the
output says so next to whatever passes.

Data: KAIST three-phase PMSM stator fault dataset, CC BY 4.0.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
from scipy import stats

import pmsm_measured_signature as sig
from motor_fault_types_and_vibration import FS_I, FS_V, SUB_N, current_features, vib_features
from cross_machine_replication import CACHE, NAME, load, session_of, sub_windows

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "sign_free_deviation.tsv"

MACHINES = ["1.0kW", "1.5kW", "3.0kW"]
SEEN = {"C1": "seen on all machines", "V1": "seen on all machines",
        "C2": "blind on 1.5/3.0 kW", "V2": "blind on 1.5/3.0 kW"}


def read_machine(tag: str):
    z = zipfile.ZipFile(CACHE / f"{tag}.zip")
    rec = {}
    for name in sorted(n for n in z.namelist() if n.lower().endswith(".tdms")):
        m = NAME.search(Path(name).name)
        if not m:
            continue
        sev = float(f"{m.group(2)}.{m.group(3)}")
        chan = m.group(4).lower()
        ftype = "intercoil" if m.group(5).lower() in ("intercoil", "coil") else "interturn"
        p = CACHE / name
        if not p.exists():
            z.extract(name, CACHE)
        day = session_of(p)
        if chan == "current":
            ph = load(z, name, FS_I)
            f0 = sig.find_f0(ph)
            c1, c2, _ = current_features(ph, f0)
            rec[(ftype, sev, "current")] = dict(
                C1=c1, C2=c2, f0=f0, day=day,
                C1s=sub_windows(ph, lambda a: current_features(a, f0)[0]),
                C2s=sub_windows(ph, lambda a: current_features(a, f0)[1]))
        else:
            rec[(ftype, sev, "vibration")] = dict(x=load(z, name, FS_V)[0], day=day)
    f0 = float(np.median([v["f0"] for k, v in rec.items() if k[2] == "current"]))
    for k, v in rec.items():
        if k[2] == "vibration":
            v["V1"], v["V2"] = vib_features(v["x"], f0)
            v["V1s"] = sub_windows([v["x"]], lambda a: vib_features(a[0], f0)[0])
            v["V2s"] = sub_windows([v["x"]], lambda a: vib_features(a[0], f0)[1])
            del v["x"]
    return rec


def main() -> None:
    results, rows = {}, []
    for tag in MACHINES:
        rec = read_machine(tag)
        for ftype in ("interturn", "intercoil"):
            sevs = sorted({s for (f, s, c) in rec if f == ftype and c == "current"})
            if 0.0 not in sevs:
                continue
            day0 = rec[(ftype, 0.0, "current")]["day"]
            keep = [s for s in sevs if rec[(ftype, s, "current")]["day"] == day0]
            cell = (tag, ftype)
            if len(keep) < 3:
                print(f"{tag} {ftype}: only {len(keep)} record(s) on the healthy "
                      f"record's date -- cell not evaluable (docs/204)")
                results[cell] = None
                continue
            print(f"\n{'='*76}\n{tag}  {ftype}   severities on {day0}: {keep}\n{'='*76}")
            print(f"{'sev%':>8}" + "".join(f"{k:>12}" for k in ("D(C1)", "D(C2)", "D(V1)", "D(V2)")))
            per = {}
            for feat, blk, sub in (("C1", "current", "C1s"), ("C2", "current", "C2s"),
                                   ("V1", "vibration", "V1s"), ("V2", "vibration", "V2s")):
                base = rec[(ftype, 0.0, blk)]
                g0 = 3.0 * float(np.std(base[sub], ddof=1))
                per[feat] = [abs(rec[(ftype, s, blk)][feat] - base[feat]) / g0 for s in keep]
            for i, s in enumerate(keep):
                print(f"{s:>8.2f}" + "".join(f"{per[k][i]:>12.1f}" for k in
                                             ("C1", "C2", "V1", "V2")))
                rows.append((tag, ftype, s, *(per[k][i] for k in ("C1", "C2", "V1", "V2"))))
            cellres = {}
            for k in ("C1", "C2", "V1", "V2"):
                # Spearman on four points takes exact rational values: 1, 4/5,
                # 3/5, 2/5. One adjacent inversion gives exactly 4/5 = 0.8,
                # which the pre-registered bar admits, but the float comes back
                # as 0.7999999999999999 and a bare >= 0.8 rejects it. The
                # tolerance below repairs a representation error; it does not
                # move the threshold.
                rho = float(stats.spearmanr(keep, per[k]).statistic)
                cellres[k] = dict(rho=rho, dmax=max(per[k]))
            print("   " + "  ".join(f"{k}: rho={cellres[k]['rho']:+.3f} "
                                    f"Dmax={cellres[k]['dmax']:.1f}"
                                    for k in ("C1", "C2", "V1", "V2")))
            results[cell] = cellres

    cells = [c for c, v in results.items() if v]
    print(f"\n{'='*76}\nevaluable cells: {len(cells)}  {cells}\n{'='*76}")
    print(f"{'feature':>9}{'monotone (rho>=0.8)':>22}{'Dmax>3':>10}{'verdict':>12}   note")
    winners = []
    for k in ("C1", "C2", "V1", "V2"):
        mono = sum(results[c][k]["rho"] >= 0.8 - 1e-9 for c in cells)
        det = sum(results[c][k]["dmax"] > 3 for c in cells)
        ok = mono == len(cells) and det == len(cells)
        winners.append(k) if ok else None
        print(f"{k:>9}{f'{mono}/{len(cells)}':>22}{f'{det}/{len(cells)}':>10}"
              f"{'PASS' if ok else 'fail':>12}   {SEEN[k]}")
    print()
    if winners:
        print(f"Y1+Y2 -> a machine-portable deviation indicator exists: {winners}")
        for w in winners:
            print(f"   {w}: {SEEN[w]}")
    else:
        print("Y1+Y2 -> NO feature is monotone and detectable in all cells.")
        print("         No machine-portable deviation indicator among these four.")
    print("\nper-cell detail:")
    for c in cells:
        print(f"  {c[0]:>6} {c[1]:<10} " + "  ".join(
            f"{k} rho={results[c][k]['rho']:+.2f} D={results[c][k]['dmax']:5.1f}"
            for k in ("C1", "C2", "V1", "V2")))

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("machine\tfault_type\tseverity\tD_C1\tD_C2\tD_V1\tD_V2\n")
        for r in rows:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                              for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
