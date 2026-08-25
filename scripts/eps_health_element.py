#!/usr/bin/env python3
"""EPS health element -- a component-side SOTIF (EooC) element (docs/196).

This is not another analysis. It is the thing itself: the element that an EPS
would carry in order to take part in a SOTIF argument from the component side.
It declares, at run time, how much steering capability it can still deliver,
with a stated granularity, and it refuses to declare when it cannot.

There is no public EPS degradation data, so the element is exercised on the
two public datasets whose mechanisms an EPS shares:

    power stage   NASA PCoE MOSFET thermal overstress ageing (public domain)
    motor winding KAIST 1.0 kW PMSM inter-turn shorts (CC BY 4.0)

Neither is an EPS. The mechanisms are the same and the element is the same;
the hardware is not. That boundary is printed with the results, not buried.

--------------------------------------------------------------------------
Three parts, matching what a real element needs

 1. fingerprint (end of line)
    Everything per-unit that the runtime needs, taken once while the unit is
    known good. This is the whole content of the "per-unit baseline" idea of
    docs/163: without it the runtime has only a population threshold, which
    docs/193 showed fires on healthy units and cannot emit a value at all.

 2. estimate (run time)
    Observation -> operating-point normalisation -> capability. The formulas
    are those pre-registered in docs/192 and docs/194 and confirmed in
    docs/193 and docs/195:

        power stage    C = sqrt(R_hat_base / R_hat(t))
        motor winding  C = H(t) / H(0),  H = mean|I| / max|I|

    Both cancel the constraint parameter (Rth, phase-current limit) in the
    ratio, which is why they are computable from public data at all.

 3. declare
    A value is emitted only with its granularity and its validity. SOTIF is
    about a function being insufficient without anything having failed, so an
    element that emits a confident wrong number is worse than one that emits
    nothing. Refusal is a first-class output here.

--------------------------------------------------------------------------
Declared design decisions (assumptions, not results -- nothing below is
tested by this script, and each is on the EooC sheet)

 D1 composition. The two mechanisms act on different factors of the same
    expression: torque follows mean phase current, and the thermal limit caps
    the maximum phase current. So

        T_max  =  H(t) * I_limit(R_on(t))     ->     C = C_winding * C_stage

    They are multiplied. If instead they were to contend for the same limit,
    min() would be correct and more conservative; that case is declared, not
    assumed away. This composition has NOT been verified: no public unit
    carries both mechanisms, so the two streams come from different hardware.

 D2 granularity composition. Treated as independent, so relative
    granularities add in quadrature.

 D3 extrapolation. The fingerprint is fitted over the operating-point span
    seen at end of line. Beyond that span the normalisation is extrapolating,
    so granularity is inflated in proportion to the distance travelled,

        g_eff = g * (1 + d_out / span)

    and the element refuses beyond twice the span. The alternative -- refusing
    outside the fitted span entirely -- was tried first and is reported in
    docs/196, because on this data it refuses exactly the runs where the
    degradation appears.

Data: NASA PCoE (public domain); KAIST, CC BY 4.0, 10.17632/rgn5brrgrn.5.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

import mosfet_precursor as mos
import pmsm_measured_signature as sig
from capability_second_mechanism import headroom

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "eps_health_element_run.tsv"

EOL_RUNS = (1, 2, 3)          # what the unit sees at end of line, docs/166
SUB_N = 10                    # sub-windows used to measure granularity, docs/194
MAX_EXTRAP = 2.0              # D3: refuse beyond twice the fitted span


# ---------------------------------------------------------------- declaration
@dataclass
class Declaration:
    """What the element puts on the bus."""
    mechanism: str
    capability: float | None      # None means: not declared
    granularity: float | None
    valid: bool
    reason: str
    operating_point: float = float("nan")

    def line(self) -> str:
        if not self.valid:
            return f"{self.mechanism:<12} --        --        REFUSED  {self.reason}"
        return (f"{self.mechanism:<12} C={self.capability:.4f}  "
                f"+/-{self.granularity:.4f}  ok       {self.reason}")


# ---------------------------------------------------------------- fingerprint
@dataclass
class StageFingerprint:
    """Per-unit, taken once at end of line, for the power stage."""
    temp_coeff: float             # ohm/degC, this unit's own
    r_hat_base: float             # temperature-normalised on-resistance
    t_ref: float                  # reference operating point
    t_span: tuple[float, float]   # operating-point range actually fitted
    g_base: float                 # granularity measured at end of line

    @property
    def span(self) -> float:
        return self.t_span[1] - self.t_span[0]

    def bytes_needed(self) -> int:
        return 4 * 6              # six float32: coeff, base, ref, lo, hi, g


@dataclass
class WindingFingerprint:
    h_base: float                 # balance at end of line
    f0_ref: float                 # electrical frequency of the reference point
    g_base: float

    def bytes_needed(self) -> int:
        return 4 * 3


# ------------------------------------------------------------------- run time
def stage_estimate(r_on: float, t_pkg: float, fp: StageFingerprint) -> Declaration:
    """Power stage: normalise the operating point, then C = sqrt(base/now)."""
    lo, hi = fp.t_span
    d_out = max(0.0, lo - t_pkg, t_pkg - hi)
    if fp.span <= 0 or d_out > MAX_EXTRAP * fp.span:
        return Declaration("power stage", None, None, False,
                           f"operating point {t_pkg:.1f}C is {d_out:.1f}C outside the "
                           f"fingerprint span {lo:.1f}-{hi:.1f}C", t_pkg)
    r_hat = r_on - fp.temp_coeff * (t_pkg - fp.t_ref)
    if r_hat <= 0:
        return Declaration("power stage", None, None, False,
                           "normalised resistance non-positive", t_pkg)
    c = float(np.sqrt(fp.r_hat_base / r_hat))
    g = fp.g_base * (1.0 + d_out / fp.span)           # D3
    note = "in span" if d_out == 0 else f"extrapolated {d_out:.1f}C, granularity x{1+d_out/fp.span:.2f}"
    return Declaration("power stage", c, g, True, note, t_pkg)


def winding_estimate(phases, f0: float, fp: WindingFingerprint) -> Declaration:
    """Motor winding: C = H(t)/H(0), with H the balance headroom."""
    if abs(f0 - fp.f0_ref) / fp.f0_ref > 0.05:
        return Declaration("motor winding", None, None, False,
                           f"electrical frequency {f0:.1f}Hz is off the reference "
                           f"{fp.f0_ref:.1f}Hz by more than 5%", f0)
    h = headroom(phases, f0)
    n = len(phases[0]) // SUB_N
    subs = np.array([headroom([p[i * n:(i + 1) * n] for p in phases], f0)
                     for i in range(SUB_N)])
    c = h / fp.h_base
    g = 3.0 * float(np.std(subs / fp.h_base, ddof=1))
    return Declaration("motor winding", c, g, True, "in span", f0)


def compose(decls: list[Declaration]) -> Declaration:
    """D1/D2: independent factors multiply; granularities add in quadrature."""
    if any(not d.valid for d in decls):
        bad = ", ".join(d.mechanism for d in decls if not d.valid)
        return Declaration("STR capability", None, None, False,
                           f"not declared because {bad} refused")
    c = float(np.prod([d.capability for d in decls]))
    rel = np.array([d.granularity / d.capability for d in decls])
    g = float(c * np.sqrt(np.sum(rel ** 2)))
    return Declaration("STR capability", c, g, True,
                       "composed by D1 (multiplicative) -- NOT verified on one unit")


# ----------------------------------------------------------------------- main
def main() -> None:
    rows: list[tuple] = []

    # ---- power stage: fingerprint at end of line, then operate -------------
    print("=" * 78)
    print("POWER STAGE   NASA PCoE MOSFET thermal overstress ageing")
    print("=" * 78)
    z = zipfile.ZipFile(mos.ZIP)
    stage_stream: dict[int, list[Declaration]] = {}
    for dev in mos.DEVICES:
        med = {}
        for run in range(1, mos.N_RUNS + 1):
            ron, tp = mos.read_run(z, dev, run)
            med[run] = (float(np.median(ron)), float(np.median(tp)), ron, tp)

        T = np.array([med[r][1] for r in EOL_RUNS])
        R = np.array([med[r][0] for r in EOL_RUNS])
        a, _ = np.polyfit(T, R, 1)
        t_ref = med[1][1]
        rhat_eol = np.array([med[r][0] - a * (med[r][1] - t_ref) for r in EOL_RUNS])
        base = float(rhat_eol.mean())
        c_eol = np.sqrt(base / rhat_eol)
        fp = StageFingerprint(temp_coeff=float(a), r_hat_base=base, t_ref=t_ref,
                              t_span=(float(T.min()), float(T.max())),
                              g_base=3.0 * float(np.std(c_eol, ddof=1)))

        print(f"\nTest_{dev}  fingerprint: coeff {fp.temp_coeff:.5f} ohm/C, "
              f"span {fp.t_span[0]:.1f}-{fp.t_span[1]:.1f}C ({fp.span:.1f}C), "
              f"g {fp.g_base:.4%}, {fp.bytes_needed()} bytes")
        stream = []
        for run in range(1, mos.N_RUNS + 1):
            d = stage_estimate(med[run][0], med[run][1], fp)
            stream.append(d)
            print(f"   run {run}  T={med[run][1]:6.1f}C  {d.line()}")
            rows.append(("power stage", f"Test_{dev}", run, med[run][1],
                         d.capability, d.granularity, int(d.valid), d.reason))
        stage_stream[dev] = stream

    # ---- motor winding -----------------------------------------------------
    print("\n" + "=" * 78)
    print("MOTOR WINDING   KAIST 1.0 kW PMSM inter-turn shorts")
    print("=" * 78)
    zp = zipfile.ZipFile(sig.ZIP)
    names = sorted(n for n in zp.namelist()
                   if "current" in n and "interturn" in n.replace("_", ""))
    recs = {}
    for name in names:
        p = sig.CACHE / name
        if not p.exists():
            zp.extract(name, sig.CACHE)
        sev = sig.severity_from_name(Path(name).name)
        ph = sig.load_phases(p)
        recs[sev] = (ph, sig.find_f0(ph))

    ph0, f00 = recs[0.00]
    n = len(ph0[0]) // SUB_N
    subs0 = np.array([headroom([p[i * n:(i + 1) * n] for p in ph0], f00) for i in range(SUB_N)])
    h0 = headroom(ph0, f00)
    wfp = WindingFingerprint(h_base=h0, f0_ref=f00,
                             g_base=3.0 * float(np.std(subs0 / h0, ddof=1)))
    print(f"\nfingerprint: H {wfp.h_base:.5f}, f0 {wfp.f0_ref:.1f}Hz, "
          f"g {wfp.g_base:.4%}, {wfp.bytes_needed()} bytes")
    S2 = [0.00, 3.35, 6.48, 21.69]
    wind_stream = []
    for sev in S2:
        ph, f0 = recs[sev]
        d = winding_estimate(ph, f0, wfp)
        wind_stream.append(d)
        print(f"   severity {sev:5.2f}%  {d.line()}")
        rows.append(("motor winding", "KAIST 1.0kW", sev, f0,
                     d.capability, d.granularity, int(d.valid), d.reason))

    # ---- refusal actually exercised ---------------------------------------
    print("\n" + "=" * 78)
    print("REFUSAL   the element must decline when it cannot normalise")
    print("=" * 78)
    off = winding_estimate(recs[21.69][0], wfp.f0_ref * 1.5, wfp)
    print(f"   operating point moved 50% off reference -> {off.line()}")
    dev0 = mos.DEVICES[0]
    ron0, tp0 = mos.read_run(z, dev0, 1)
    T = np.array([np.median(mos.read_run(z, dev0, r)[1]) for r in EOL_RUNS])
    R = np.array([np.median(mos.read_run(z, dev0, r)[0]) for r in EOL_RUNS])
    a0, _ = np.polyfit(T, R, 1)
    fp0 = StageFingerprint(float(a0), float(np.median(ron0)), float(np.median(tp0)),
                           (float(T.min()), float(T.max())), 0.001)
    far = stage_estimate(float(np.median(ron0)), float(T.min()) - 3 * fp0.span, fp0)
    print(f"   operating point far below fingerprint span -> {far.line()}")

    # ---- composed declaration ---------------------------------------------
    print("\n" + "=" * 78)
    print("COMPOSED STR capability   (D1: multiplicative; NOT verified on one unit)")
    print("=" * 78)
    print(f"{'stage state':<22}{'winding state':<22}{'C':>10}{'granularity':>14}")
    for dev in (8, 14):
        for run in (1, mos.N_RUNS):
            for sev, wd in zip(S2, wind_stream):
                if sev not in (0.00, 21.69):
                    continue
                c = compose([stage_stream[dev][run - 1], wd])
                if c.valid:
                    print(f"{f'Test_{dev} run {run}':<22}{f'severity {sev:.2f}%':<22}"
                          f"{c.capability:>10.4f}{c.granularity:>13.4%}")
                    rows.append(("composed", f"Test_{dev} run{run} + sev{sev}", run, sev,
                                 c.capability, c.granularity, 1, c.reason))

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("mechanism\tunit\tindex\toperating_point\tcapability\t"
                  "granularity\tvalid\treason\n")
        for r in rows:
            out.write("\t".join("" if x is None else
                                (f"{x:.6g}" if isinstance(x, float) else str(x))
                                for x in r) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")
    print("\nNeither dataset is an EPS. The mechanisms are shared; the hardware is not.")


if __name__ == "__main__":
    main()
