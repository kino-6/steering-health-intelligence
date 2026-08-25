#!/usr/bin/env python3
"""Capability rule on a second mechanism (docs/194 protocol -> docs/195).

Executes the protocol pre-registered in docs/194 without modification.

docs/193 established the capability index on power-stage on-resistance. One
mechanism makes an instrument, not a rule, so the same FORM is applied here
to stator inter-turn shorts, where the mechanism, the binding constraint and
the shape of the data all differ.

    capability = deliverable output under the binding constraint, divided by
                 the unit's own baseline

For an inter-turn short the thermal limit binds on the hottest phase, and
torque follows the mean phase current, so

    H     = mean(|I_phase|) / max(|I_phase|)      headroom given up to imbalance
    C(s)  = H(s) / H(0)

The phase-current limit cancels in the ratio, exactly as Rth did in docs/192.

Only session S2 is used. A per-unit baseline rule requires a healthy record
of the same unit and session, and S1 has none; that is a precondition, not a
choice made from results. S1 is reported separately against its own lowest
severity, clearly marked as not testing the rule. The session split itself
was found post hoc in docs/162 and is declared in docs/194.

Data: KAIST three-phase PMSM stator fault dataset, CC BY 4.0,
Mendeley 10.17632/rgn5brrgrn.5.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
from scipy import stats

import pmsm_measured_signature as sig

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "capability_second_mechanism.tsv"
SUB_N = 10                # 20 s window split into ten sub-windows, docs/194
S2 = {0.00, 3.35, 6.48, 21.69}


def headroom(phases, f0: float) -> float:
    ph = np.array([sig.fundamental(p, f0) for p in phases])
    ph, _, _ = sig.fix_polarity(ph, phases)
    amp = np.abs(ph)
    return float(amp.mean() / amp.max())


def main() -> None:
    z = zipfile.ZipFile(sig.ZIP)
    names = sorted(n for n in z.namelist()
                   if "current" in n and "interturn" in n.replace("_", ""))

    rec = {}
    for name in names:
        p = sig.CACHE / name
        if not p.exists():
            z.extract(name, sig.CACHE)
        sev = sig.severity_from_name(Path(name).name)
        phases = sig.load_phases(p)
        f0 = sig.find_f0(phases)
        H = headroom(phases, f0)
        # sub-window spread -> declared granularity
        n = len(phases[0]) // SUB_N
        subs = [headroom([ph[i * n:(i + 1) * n] for ph in phases], f0) for i in range(SUB_N)]
        rec[sev] = dict(H=H, f0=f0, subs=np.array(subs))

    def report(sevs, base_sev, label, is_rule):
        base = rec[base_sev]
        Hb = base["H"]
        print(f"\n=== {label} (baseline severity {base_sev:.2f}%) ===")
        print(f"{'severity%':>10}{'f0[Hz]':>9}{'H':>10}{'C':>10}{'1-C':>10}{'g':>10}")
        cs, out = [], []
        for s in sevs:
            H = rec[s]["H"]
            C = H / Hb
            # granularity propagated through the same ratio
            csub = rec[s]["subs"] / np.mean(base["subs"])
            g = 3.0 * float(np.std(csub, ddof=1))
            cs.append(C)
            out.append((label, s, rec[s]["f0"], H, C, g))
            print(f"{s:>10.2f}{rec[s]['f0']:>9.2f}{H:>10.5f}{C:>10.5f}{1-C:>+10.2%}{g:>10.4%}")
        rho = stats.spearmanr(sevs, cs).statistic
        gmax = out[-1][5]
        print(f"\n  Spearman rho(severity, C) = {rho:+.3f}")
        if is_rule:
            print(f"  R1 monotone decrease  rho <= -0.8      : "
                  f"{'PASS' if rho <= -0.8 else 'FAIL'}")
            print(f"  R2 C({sevs[-1]:.2f}%) = {cs[-1]:.5f} < 1-g = {1-gmax:.5f} : "
                  f"{'PASS' if cs[-1] < 1 - gmax else 'FAIL'}")
            steps = [(sevs[i], sevs[i - 1], cs[i - 1] - cs[i], out[i][5])
                     for i in range(1, len(sevs))]
            res = [f"{lo:.2f}->{hi:.2f}%: dC={d:+.4%} vs g={g:.4%} "
                   f"{'resolved' if d > g else 'below granularity'}"
                   for hi, lo, d, g in steps]
            print("  R3 severity steps:")
            for r in res:
                print("     " + r)
        return out

    rows = report(sorted(S2), 0.00, "S2  rule test", True)
    s1 = sorted(set(rec) - S2)
    rows += report(s1, s1[0], "S1  reference only (no healthy record)", False)

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("session\tseverity_pct\tf0_hz\theadroom\tcapability\tgranularity\n")
        for lab, s, f0, H, C, g in rows:
            out.write(f"{lab.split()[0]}\t{s}\t{f0:.4f}\t{H:.6f}\t{C:.6f}\t{g:.6f}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
