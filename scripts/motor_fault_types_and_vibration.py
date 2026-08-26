#!/usr/bin/env python3
"""The motor dataset's unused three quarters (docs/200 -> docs/201).

Executes the protocol pre-registered in docs/200 without modification.

docs/195 used 8 of the 32 files in the KAIST 1.0 kW set: inter-turn shorts,
current only. The other 24 hold a second fault type with its own healthy
record, and a vibration channel for both. Three questions:

  W1  does the capability rule transfer to coil-to-coil shorts
  W2  does vibration carry anything current does not -- this decides whether
      the function needs a sensor an EPS ECU does not already have
  W3  can current alone separate the two fault types, which is the difference
      between saying "degraded" and saying which winding fault it is

Features, all fixed in docs/200:
  C1  H(sev)/H(0),  H = mean|I| / max|I|   fundamental amplitudes
  C2  |I2| / |I1|                          negative- to positive-sequence
  V1  vibration amplitude at 2*f0, over healthy
  V2  vibration broadband RMS, over healthy
Granularity for every feature: three standard deviations over ten 2 s
sub-windows of the same 20 s middle window.

Data: KAIST three-phase PMSM stator fault dataset, CC BY 4.0,
Mendeley 10.17632/rgn5brrgrn.5.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

import numpy as np
from nptdms import TdmsFile
from scipy import stats

import pmsm_measured_signature as sig

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / ".pmsm_fault"
ZIP = CACHE / "1.0kW.zip"
OUT_TSV = REPO_ROOT / "data" / "motor_fault_types_and_vibration.tsv"

FS_I, FS_V = 100_000.0, 25_600.0
WINDOW_S, SUB_N = 20.0, 10
A = np.exp(2j * np.pi / 3)

NAME = re.compile(r"1000W_(\d+)[._](\d+)_(current|vibration)_(interturn|intercoil)\.tdms")


def parse(name: str):
    m = NAME.match(Path(name).name)
    return (float(f"{m.group(1)}.{m.group(2)}"), m.group(3), m.group(4)) if m else None


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


def current_features(phases, f0):
    ph = np.array([sig.fundamental(p, f0) for p in phases])
    ph, _, flipped = sig.fix_polarity(ph, phases)
    amp = np.abs(ph)
    I1 = (ph[0] + A * ph[1] + A ** 2 * ph[2]) / 3
    I2 = (ph[0] + A ** 2 * ph[1] + A * ph[2]) / 3
    dom, sub = max(abs(I1), abs(I2)), min(abs(I1), abs(I2))
    return float(amp.mean() / amp.max()), float(sub / dom), flipped


def vib_features(x, f0):
    n = len(x)
    sp = np.fft.rfft(x * np.hanning(n))
    fr = np.fft.rfftfreq(n, 1 / FS_V)
    band = (fr > 2 * f0 - 5) & (fr < 2 * f0 + 5)
    return float(np.abs(sp[band]).max() * 2 / n), float(np.sqrt(np.mean(x ** 2)))


def sub_windows(arrs, fs, fn):
    n = len(arrs[0]) // SUB_N
    return np.array([fn([a[i * n:(i + 1) * n] for a in arrs]) for i in range(SUB_N)])


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    files = [n for n in z.namelist() if n.endswith(".tdms")]
    rec: dict[tuple, dict] = {}

    for name in sorted(files):
        sev, chan, ftype = parse(name)
        if chan == "current":
            ph = load(z, name, FS_I)
            f0 = sig.find_f0(ph)
            h, i2, flipped = current_features(ph, f0)
            subs = sub_windows(ph, FS_I, lambda a: current_features(a, f0)[0])
            subs2 = sub_windows(ph, FS_I, lambda a: current_features(a, f0)[1])
            rec[(ftype, sev, "current")] = dict(H=h, I2=i2, f0=f0, flipped=flipped,
                                                Hs=subs, I2s=subs2)
        else:
            x = load(z, name, FS_V)[0]
            f0 = 200.0                      # electrical frequency, docs/162
            v1, v2 = vib_features(x, f0)
            s1 = sub_windows([x], FS_V, lambda a: vib_features(a[0], f0)[0])
            s2 = sub_windows([x], FS_V, lambda a: vib_features(a[0], f0)[1])
            rec[(ftype, sev, "vibration")] = dict(V1=v1, V2=v2, V1s=s1, V2s=s2)

    rows, summary = [], {}
    for ftype in ("interturn", "intercoil"):
        sevs = sorted({s for (f, s, c) in rec if f == ftype})
        base_i = rec[(ftype, 0.0, "current")]
        base_v = rec[(ftype, 0.0, "vibration")]
        print("=" * 92)
        print(f"{ftype}   severities {sevs}")
        print("=" * 92)
        print(f"{'sev%':>7}{'pol':>5}{'C1':>9}{'gC1':>9}{'C2':>9}{'gC2':>9}"
              f"{'V1':>9}{'gV1':>9}{'V2':>9}{'gV2':>9}")
        vals = {k: [] for k in ("C1", "C2", "V1", "V2")}
        res = {k: None for k in ("C1", "C2", "V1", "V2")}
        for s in sevs:
            c, v = rec[(ftype, s, "current")], rec[(ftype, s, "vibration")]
            C1 = c["H"] / base_i["H"]
            gC1 = 3 * float(np.std(c["Hs"] / np.mean(base_i["Hs"]), ddof=1))
            C2 = c["I2"] / base_i["I2"]
            gC2 = 3 * float(np.std(c["I2s"] / np.mean(base_i["I2s"]), ddof=1))
            V1 = v["V1"] / base_v["V1"]
            gV1 = 3 * float(np.std(v["V1s"] / np.mean(base_v["V1s"]), ddof=1))
            V2 = v["V2"] / base_v["V2"]
            gV2 = 3 * float(np.std(v["V2s"] / np.mean(base_v["V2s"]), ddof=1))
            print(f"{s:>7.2f}{'flip' if c['flipped'] else '  - ':>5}"
                  f"{C1:>9.4f}{gC1:>9.4f}{C2:>9.3f}{gC2:>9.3f}"
                  f"{V1:>9.3f}{gV1:>9.3f}{V2:>9.3f}{gV2:>9.3f}")
            for k, val, g in (("C1", C1, gC1), ("C2", C2, gC2), ("V1", V1, gV1), ("V2", V2, gV2)):
                vals[k].append(val)
                if s > 0 and res[k] is None and abs(val - 1.0) > g:
                    res[k] = s
            rows.append((ftype, s, C1, gC1, C2, gC2, V1, gV1, V2, gV2,
                         c["I2"], int(c["flipped"])))
        rho = stats.spearmanr(sevs, vals["C1"]).statistic
        print(f"\n  W1  Spearman rho(severity, C1) = {rho:+.3f}")
        print(f"  W2  lowest severity resolved above its own 3-sigma:")
        for k in ("C1", "C2", "V1", "V2"):
            print(f"        {k}: {res[k] if res[k] is not None else 'none'}")
        summary[ftype] = dict(rho=rho, res=res, sevs=sevs,
                              C1=vals["C1"], C2=vals["C2"])
        print()

    print("=" * 92)
    ok1 = summary["intercoil"]["rho"] <= -0.8
    print(f"W1 rule transfers to coil-to-coil: rho = {summary['intercoil']['rho']:+.3f} "
          f"-> {'PASS' if ok1 else 'FAIL'} (needs <= -0.80)")

    def best(d, keys):
        v = [d[k] for k in keys if d[k] is not None]
        return min(v) if v else None
    ok2 = True
    for ft in ("interturn", "intercoil"):
        r = summary[ft]["res"]
        ci, vi = best(r, ("C1", "C2")), best(r, ("V1", "V2"))
        good = ci is not None and (vi is None or ci <= vi)
        ok2 &= good
        print(f"W2 {ft:>10}: current resolves at {ci}, vibration at {vi} -> "
              f"{'current suffices' if good else 'vibration needed'}")
    print(f"W2 overall -> {'PASS' if ok2 else 'FAIL'}")

    ranges = {}
    for ft in ("interturn", "intercoil"):
        r = [(c2 - 1.0) / (1.0 - c1) for s, c1, c2 in
             zip(summary[ft]["sevs"], summary[ft]["C1"], summary[ft]["C2"])
             if s > 0 and abs(1.0 - c1) > 1e-9]
        ranges[ft] = (min(r), max(r))
        print(f"W3 {ft:>10}: (C2-1)/(1-C1) spans {min(r):+.2f} .. {max(r):+.2f}")
    a, b = ranges["interturn"], ranges["intercoil"]
    ok3 = a[1] < b[0] or b[1] < a[0]
    print(f"W3 ranges overlap? {'no -> PASS, separable' if ok3 else 'yes -> FAIL, not separable'}")

    # ---- post hoc, not part of the criteria -------------------------------
    # Every "flip" record sits at C1 ~ 0.93 and vibration ~ 0.09 regardless of
    # severity, in BOTH fault types. That is the two-session structure docs/162
    # found in the inter-turn files, now present in the coil-to-coil ones too:
    # a session step, not a fault signature. docs/195 handled it by keeping the
    # session that holds the healthy record, and the same is done here -- but
    # AFTER the pre-registered verdicts above, and labelled as post hoc. It
    # does not rescue W1.
    print("\n" + "=" * 92)
    print("POST HOC -- session that holds the healthy record only. Not part of the criteria.")
    print("=" * 92)
    for ftype in ("interturn", "intercoil"):
        keep = [s for s in summary[ftype]["sevs"]
                if not rec[(ftype, s, "current")]["flipped"]]
        base_i, base_v = rec[(ftype, 0.0, "current")], rec[(ftype, 0.0, "vibration")]
        print(f"\n{ftype}   severities kept {keep}")
        print(f"{'sev%':>7}{'C1':>9}{'gC1':>9}{'V1':>9}{'gV1':>9}")
        c1s, v1s = [], []
        for s in keep:
            c, v = rec[(ftype, s, "current")], rec[(ftype, s, "vibration")]
            C1 = c["H"] / base_i["H"]
            gC1 = 3 * float(np.std(c["Hs"] / np.mean(base_i["Hs"]), ddof=1))
            V1 = v["V1"] / base_v["V1"]
            gV1 = 3 * float(np.std(v["V1s"] / np.mean(base_v["V1s"]), ddof=1))
            c1s.append(C1); v1s.append(V1)
            print(f"{s:>7.2f}{C1:>9.4f}{gC1:>9.4f}{V1:>9.3f}{gV1:>9.3f}")
        rc = stats.spearmanr(keep, c1s).statistic
        rv = stats.spearmanr(keep, v1s).statistic
        print(f"   current  rho = {rc:+.3f}   {'monotone' if abs(rc) >= 0.8 else 'NOT monotone'}")
        print(f"   vibration rho = {rv:+.3f}   {'monotone' if abs(rv) >= 0.8 else 'NOT monotone'}")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("fault_type\tseverity\tC1\tgC1\tC2\tgC2\tV1\tgV1\tV2\tgV2\t"
                  "i2_over_i1_raw\tpolarity_flipped\n")
        for r in rows:
            out.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x)
                                for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
