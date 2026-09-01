#!/usr/bin/env python3
"""The recorder on a real inverter with real switch faults (docs/277 -> docs/278)

Executes the protocol pre-registered in docs/277.

The standing answer says an EPS should report deviation in phase current, DC
bus, gate drive and temperature. This dataset carries exactly those four, from
a three-phase inverter of IRF540N MOSFETs driving a PMSM converted from a car
alternator, with open-circuit, short-circuit and over-temperature faults on
individual half-bridges. It is the only thing in hand that has never been put
through the recorder, and the closest hardware to an EPS power stage here.

docs/215 set it aside because 10 Hz cannot resolve switching. The recorder
looks at window statistics, not switching waveforms, so that does not bind.

Criteria: V1 fires on seven of eight faults; V2 stays silent on held-out normal
operation, within three times the design alarm rate; V3 which of the four
signal families carries it.

Data: Bacha et al., inverter-driven PMSM fault dataset, CC BY 4.0.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import element_v2 as el
from slow_channel import slow_deviation

ROOT = Path(__file__).resolve().parent.parent
ZIP = ROOT / ".pmsm_inverter" / "PMSM-inverter-fault-diagnosis-1.0.0.zip"
BASE = "PMSM-inverter-fault-diagnosis-1.0.0/raw_data"
OUT = ROOT / "data" / "inverter_recorder.tsv"

COLS = ["Ia", "Ib", "Vdc", "Idc", "T1", "T2", "T3", "Vd"]
FAMILY = {"Ia": "相電流", "Ib": "相電流", "Vdc": "DCバス", "Idc": "DCバス",
          "T1": "温度", "T2": "温度", "T3": "温度", "Vd": "ドライバ電圧"}
# operating point: load, per docs/277. Idc itself is normalised against Vdc.
OPCOL = {c: "Idc" for c in COLS}
OPCOL["Idc"] = "Vdc"

NS = [10, 20, 50, 100]
FA_PER_HOUR, HOUR_SAMPLES = 1.0, 36000
LINE = re.compile(r"->\s*(.*)$")


def read(z, name):
    rows = []
    for ln in z.read(name).decode("utf-8", "replace").splitlines():
        m = LINE.search(ln)
        if not m:
            continue
        parts = m.group(1).split()
        if len(parts) != len(COLS):
            continue
        try:
            rows.append([float(p) for p in parts])
        except ValueError:
            continue
    return np.array(rows) if rows else None


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    names = [n for n in z.namelist() if n.startswith(BASE) and n.endswith(".txt")]
    normal = next(n for n in names if "normal_operation" in n)
    faults = sorted(n for n in names if "fault_scenarios" in n)

    a_norm = read(z, normal)
    print(f"正常運転 {len(a_norm)} 点、故障シナリオ {len(faults)} 件")
    half = len(a_norm) // 2
    fp_part, hold_part = a_norm[:half], a_norm[half:]

    fired = {}          # fault -> set of channels that fired
    fa_hold = {}
    rows = []

    for ci, col in enumerate(COLS):
        oi = COLS.index(OPCOL[col])
        y, op = fp_part[:, ci], fp_part[:, oi]
        if np.std(op) == 0:
            continue
        fp = el.take_fingerprint(y, op)
        if fp.floor <= 0:
            continue

        # threshold from the fingerprint half itself, at one alarm per hour
        best = None
        for n in NS:
            d0 = slow_deviation(y, op, fp, n)
            if d0 is None:
                continue
            q = min(1 - FA_PER_HOUR / HOUR_SAMPLES, 1 - 1.0 / len(d0))
            thr = float(np.quantile(d0, q))
            dh = slow_deviation(hold_part[:, ci], hold_part[:, oi], fp, n)
            fa = float(np.mean(dh > thr)) if dh is not None else 1.0
            if best is None or fa < best["fa"]:
                best = {"n": n, "thr": thr, "fa": fa}
        if best is None:
            continue
        fa_hold[col] = best["fa"]

        for f in faults:
            a = read(z, f)
            if a is None or len(a) < best["n"] * 2:
                continue
            d = slow_deviation(a[:, ci], a[:, oi], fp, best["n"])
            hit = bool(d is not None and (d > best["thr"]).any())
            tag = Path(f).stem
            fired.setdefault(tag, set())
            if hit:
                fired[tag].add(col)
            rows.append({"fault": tag, "channel": col, "family": FAMILY[col],
                         "n": best["n"], "thr": best["thr"],
                         "fired": int(hit), "fa_holdout": best["fa"]})

    print(f"\n{'故障シナリオ':>22} {'発火したチャネル':>34}")
    print("-" * 60)
    for tag in sorted(fired):
        ch = sorted(fired[tag])
        print(f"{tag:>22} {(', '.join(ch) if ch else '—'):>34}")

    n_fired = sum(1 for t in fired if fired[t])
    print(f"\n=== V1 8つの故障のうち発火 ===")
    print(f"  {n_fired}/{len(fired)}  {'PASS' if n_fired >= 7 else 'FAIL'} (基準 8中7)")

    design = FA_PER_HOUR / HOUR_SAMPLES
    print(f"\n=== V2 正常の後半で黙るか ===")
    print(f"{'チャネル':>8} {'誤報/判定':>11} {'設計比':>9}")
    worst = 0.0
    for c in COLS:
        if c in fa_hold:
            r = fa_hold[c] / design if design else float("inf")
            worst = max(worst, r)
            print(f"{c:>8} {fa_hold[c]:>11.5f} {r:>8.1f}倍")
    print(f"  最悪 {worst:.1f}倍  {'PASS' if worst <= 3 else 'FAIL'} (基準 3倍以内)")

    # docs/277 fixed in advance that V1 without V2 only means firing on
    # everything, so the verdict that counts uses only channels quiet enough
    # on held-out normal data
    clean = {c for c, v in fa_hold.items() if v <= design * 3}
    fired_clean = {t: (fired[t] & clean) for t in fired}
    n_clean = sum(1 for t in fired_clean if fired_clean[t])
    print(f"\n=== V1かつV2 誤報が基準内のチャネルだけで数える ===")
    print(f"  基準内のチャネル: {', '.join(sorted(clean)) if clean else 'なし'}")
    for t in sorted(fired_clean):
        ch = sorted(fired_clean[t])
        print(f"  {t:>22} {(', '.join(ch) if ch else '—'):>22}")
    print(f"  **{n_clean}/{len(fired)}**  {'PASS' if n_clean >= 7 else 'FAIL'} (基準 8中7)")

    print(f"\n=== V3 どの観測量が効いたか ===")
    fam = {}
    for r in rows:
        if r["fired"]:
            fam.setdefault(r["family"], set()).add(r["fault"])
    for k in ("相電流", "DCバス", "温度", "ドライバ電圧"):
        print(f"  {k:>8}: {len(fam.get(k, set()))}/{len(fired)} 故障で発火")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("fault\tchannel\tfamily\tn_samples\tthreshold\tfired\t"
                 "false_alarm_holdout\n")
        for r in rows:
            fh.write(f"{r['fault']}\t{r['channel']}\t{r['family']}\t{r['n']}\t"
                     f"{r['thr']:.5f}\t{r['fired']}\t{r['fa_holdout']:.6f}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
