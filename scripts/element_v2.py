#!/usr/bin/env python3
"""The recorder, built to the answer rather than to the retired one (docs/264 -> docs/265).

scripts/eps_health_element.py emits a capability value. docs/199 showed the
physics behind that value does not hold on this rig and docs/203 showed its
sign does not survive a change of machine, so the claim was withdrawn -- but
the code kept computing it. This is the element as docs/225 now specifies it.

    fingerprint   one line of observable against operating point, the reference
                  operating point, the span that was swept, and the floor, all
                  per unit and taken once while the unit is known good
    runtime       residual against that line, divided by that unit's floor;
                  window mean and window maximum both; silence outside the span

It emits a deviation and how coarse that deviation is. It does not emit a
capability, a prediction, a location, or a remaining life -- docs/225 lists
seven refusals and check_forbidden() enforces them against the record's own
field names.

Criteria, fixed in docs/264 before running: M1 no forbidden field; M2 the
fingerprint packs into 36 bytes; M3 silence exactly outside the swept span;
M4 the verdict survives 8-bit input; M5 a record packs into 27 bytes.

Data: NASA PCoE MOSFET (public domain), KAIST PMSM (CC BY 4.0).
"""

from __future__ import annotations

import struct
import sys
from dataclasses import dataclass, fields
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "element_v2.tsv"

ROBUST = 3.0 * 1.4826
WIN = 50                       # docs/225: arm on a 5 s window at 10 Hz
FIRE = 10.0                    # docs/248: ten floors at one alarm per hour
BITS = 8                       # docs/261
RNG = np.random.default_rng(20260901)

# docs/225 section 5. The element must not carry any of these.
FORBIDDEN = ("capability", "remaining", "rul", "life", "predict", "location",
             "which_fault", "percent_of_new", "severity")


# --------------------------------------------------------------------------
# fingerprint: taken once, at end of line

# docs/196 costed 36 bytes as nine float32 for two mechanisms, which is one
# operating-point dimension each. docs/225 lists the operating point as speed,
# load and temperature, so the honest fingerprint carries a slope and a swept
# span per dimension. Both are measured below rather than assumed.
NDIM = 3                        # speed, load, temperature
FP_FMT = "<" + "f" * (NDIM * 3 + 3)     # slope/lo/hi per dim + intercept, floor, version
FP_FMT_1D = "<" + "f" * 6               # the single-dimension form docs/196 costed


@dataclass(frozen=True)
class Fingerprint:
    slope: float                # observable per unit of operating point
    intercept: float
    ref_op: float               # reference operating point
    op_lo: float                # span that was actually swept -- outside it,
    op_hi: float                # the element declines to declare
    floor: float                # this unit's own noise floor at shipping
    op_scale: float             # operating-point scale, for normalising
    version: float              # fingerprint format, so a refit is detectable

    def pack(self) -> bytes:
        """One dimension, as docs/196 costed it."""
        return struct.pack(FP_FMT_1D, self.slope, self.intercept,
                           self.op_lo, self.op_hi, self.floor, self.version)

    def pack_full(self) -> bytes:
        """Three dimensions, as docs/225 lists the operating point."""
        vals = [self.slope] * NDIM + [self.op_lo] * NDIM + [self.op_hi] * NDIM
        return struct.pack(FP_FMT, *vals, self.intercept, self.floor, self.version)

    @staticmethod
    def unpack(b: bytes) -> "Fingerprint":
        sl, ic, lo, hi, fl, ver = struct.unpack(FP_FMT_1D, b)
        return Fingerprint(sl, ic, (lo + hi) / 2, lo, hi, fl, hi - lo, ver)


def take_fingerprint(y: np.ndarray, op: np.ndarray) -> Fingerprint:
    """End of line: fit one line over the swept operating range."""
    a, b = np.polyfit(op, y, 1)
    resid = y - (a * op + b)
    g = float(ROBUST * np.median(np.abs(resid - np.median(resid))))
    return Fingerprint(float(a), float(b), float(np.median(op)),
                       float(op.min()), float(op.max()), g,
                       float(op.max() - op.min()), 2.0)


# --------------------------------------------------------------------------
# record: what the element emits, once per fired event

# docs/225 lists deviation, granularity, validity and operating point; the
# operating point is speed, load and temperature, so six float32 -- the 24
# bytes that document costed -- plus the two fields docs/259 added.
REC_FMT = "<ffffffHHBB"


@dataclass(frozen=True)
class Record:
    deviation: float            # how far from this unit's own baseline
    granularity: float          # how coarse that number is -- the unit's floor
    operating_point: float      # the dimension actually measured here
    op_load: float              # docs/225 lists three; the public data carries
    op_temp: float              # one, so the other two are reserved, not faked
    confidence: float
    seconds_since_key_on: int   # docs/251: the field reports minutes-in
    event_seconds: int
    flags: int                  # bit0 held to key-off, bit1 mean, bit2 max
    validity: int               # 1 declared, 0 declined

    def pack(self) -> bytes:
        return struct.pack(REC_FMT, self.deviation, self.granularity,
                           self.operating_point, self.op_load, self.op_temp,
                           self.confidence,
                           min(self.seconds_since_key_on, 65535),
                           min(self.event_seconds, 65535),
                           self.flags, self.validity)


def check_forbidden() -> list[str]:
    names = [f.name.lower() for f in fields(Record)] + \
            [f.name.lower() for f in fields(Fingerprint)]
    return [n for n in names if any(k in n for k in FORBIDDEN)]


# --------------------------------------------------------------------------
# runtime

def run(y: np.ndarray, op: np.ndarray, fp: Fingerprint, key_on_s: int = 0):
    """Walk the signal in windows, emitting one record per window."""
    out = []
    k = len(y) // WIN
    for i in range(k):
        s = slice(i * WIN, (i + 1) * WIN)
        yw, ow = y[s], op[s]
        inside = (ow >= fp.op_lo) & (ow <= fp.op_hi)
        if not inside.all():
            out.append(Record(0.0, fp.floor, float(np.median(ow)), 0.0, 0.0, 0.0,
                              key_on_s + i * WIN // 10, 0, 0, 0))
            continue
        resid = yw - (fp.slope * ow + fp.intercept)
        d = np.abs(resid) / fp.floor
        mean_hit, max_hit = float(np.abs(d.mean())), float(d.max())
        flags = (0b010 if mean_hit > FIRE else 0) | (0b100 if max_hit > FIRE else 0)
        out.append(Record(max(mean_hit, max_hit), fp.floor, float(np.median(ow)), 0.0, 0.0,
                          1.0, key_on_s + i * WIN // 10,
                          WIN // 10 if flags else 0, flags, 1))
    return out


def quantize(x: np.ndarray, bits: int = BITS) -> np.ndarray:
    fs = float(np.max(np.abs(x))) * 2.0
    q = 2 * fs / (2 ** bits)
    return np.clip(np.round(x / q) * q, -fs, fs)


# --------------------------------------------------------------------------

def nasa_units():
    import zipfile
    z = zipfile.ZipFile(mos.ZIP) if hasattr(mos, "ZIP") else None
    for dev in mos.DEVICES:
        y, t = [], []
        for r in (1, 2, 3):
            ron, tp = mos.read_run(z, dev, r)
            y.append(np.asarray(ron))
            t.append(np.asarray(tp))
        yield f"NASA Test_{dev}", np.concatenate(y), np.concatenate(t)


def main() -> None:
    print("=== M1 禁じられた出力を持たないか ===")
    bad = check_forbidden()
    print(f"  出力の欄: " + ", ".join(f.name for f in fields(Record)))
    print(f"  指紋の欄: " + ", ".join(f.name for f in fields(Fingerprint)))
    print(f"  禁じられた語を含む欄: {bad if bad else 'なし'}  "
          f"{'PASS' if not bad else 'FAIL'}")

    print("\n=== M2/M5 実際に詰めて測る ===")
    rows = []
    fps, sigs = {}, {}
    for label, y, op in nasa_units():
        half = len(y) // 2
        fp = take_fingerprint(y[:half], op[:half])     # EOL stands in as first half
        fps[label], sigs[label] = fp, (y[half:], op[half:])
    any_fp = next(iter(fps.values()))
    nb_fp, nb_rec = len(any_fp.pack()), len(Record(0, 0, 0, 0, 0, 0, 0, 0, 0, 1).pack())
    nb_fp3 = len(any_fp.pack_full())
    print(f"  指紋 1次元 {nb_fp} バイト × 2機構 = {nb_fp*2} バイト  (docs/196 の 36)  "
          f"{'PASS' if nb_fp*2 <= 36 else 'FAIL'}")
    print(f"  指紋 3次元 {nb_fp3} バイト × 2機構 = {nb_fp3*2} バイト  "
          f"{'**予算超過**' if nb_fp3*2 > 36 else ''}")
    print(f"  1事象  {nb_rec} バイト  (予算 27)  {'PASS' if nb_rec <= 27 else 'FAIL'}")
    # float32 does not reproduce a float64 bit for bit, so exact equality is
    # the wrong test. What matters is whether the rounding moves a deviation
    # by enough to change a verdict, so measure it against the floor.
    rt = Fingerprint.unpack(any_fp.pack())
    worst = 0.0
    for label, (y, op) in sigs.items():
        fp = fps[label]
        r2 = Fingerprint.unpack(fp.pack())
        d1 = np.abs(y - (fp.slope * op + fp.intercept)) / fp.floor
        d2 = np.abs(y - (r2.slope * op + r2.intercept)) / r2.floor
        worst = max(worst, float(np.max(np.abs(d1 - d2))))
    print(f"  往復の誤差(逸脱の単位で最大): {worst:.3e}  "
          f"発火閾値 {FIRE}  → {worst/FIRE:.1e} 倍  "
          f"{'PASS' if worst < FIRE * 0.01 else 'FAIL'} (基準: 閾値の1%未満)")

    print("\n=== M3 掃引範囲の外で黙り、内では黙らないか ===")
    # the first half of a run covers nearly the same range as the second, so
    # only one window fell outside and the test proved nothing. Narrow the
    # fingerprint's span deliberately, which is exactly the failure docs/227
    # measured: a fingerprint taken over too little of the operating range.
    tot_out = sil_out = tot_in = sil_in = 0
    for label, (y, op) in sigs.items():
        f0 = fps[label]
        mid, half_span = (f0.op_lo + f0.op_hi) / 2, (f0.op_hi - f0.op_lo) / 4
        fp = Fingerprint(f0.slope, f0.intercept, f0.ref_op,
                         mid - half_span, mid + half_span, f0.floor,
                         f0.op_scale, f0.version)
        recs = run(y, op, fp)
        k = len(y) // WIN
        for i, r in enumerate(recs):
            ow = op[i * WIN:(i + 1) * WIN]
            outside = not ((ow >= fp.op_lo) & (ow <= fp.op_hi)).all()
            if outside:
                tot_out += 1
                sil_out += (r.validity == 0)
            else:
                tot_in += 1
                sil_in += (r.validity == 0)
    print(f"  範囲外 {tot_out} 窓 → 沈黙 {sil_out}  "
          f"({sil_out/tot_out:.0%} 必要 100%)" if tot_out else "  範囲外の窓が無い")
    print(f"  範囲内 {tot_in} 窓 → 沈黙 {sil_in}  "
          f"({sil_in/tot_in:.0%} 必要 0%)" if tot_in else "  範囲内の窓が無い")
    m3 = (tot_out == 0 or sil_out == tot_out) and (tot_in == 0 or sil_in == 0)
    print(f"  {'PASS' if m3 else 'FAIL'}")

    print("\n=== M4 8ビットに量子化しても判定が一致するか ===")
    agree = total = 0
    for label, (y, op) in sigs.items():
        fp = fps[label]
        a = run(y, op, fp)
        b = run(quantize(y), op, fp)
        for ra, rb in zip(a, b):
            total += 1
            agree += (ra.validity == rb.validity) and (ra.flags == rb.flags)
        rows.append({"unit": label, "windows": len(a),
                     "fired": sum(1 for r in a if r.flags),
                     "silent": sum(1 for r in a if not r.validity)})
    rate = agree / total if total else 0.0
    print(f"  {agree}/{total} 窓で一致 = {rate:.2%}  "
          f"{'PASS' if rate >= 0.99 else 'FAIL'} (基準 99%)")

    OUT_TSV.parent.mkdir(exist_ok=True)
    with OUT_TSV.open("w") as fh:
        fh.write("unit\twindows\tfired\tsilent\tfingerprint_bytes\trecord_bytes\t"
                 "quantized_agreement\n")
        for r in rows:
            fh.write(f"{r['unit']}\t{r['windows']}\t{r['fired']}\t{r['silent']}\t"
                     f"{nb_fp}\t{nb_rec}\t{rate:.4f}\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
