"""Can the ECU's own bytes carry the capability estimate (docs/332 -> docs/333)?

docs/331 computed capability from full-precision laboratory Ron. The ECU has
thirty bytes per event and a fifty-six byte fingerprint, and this reconstructs
capability from those alone:

    Ron(t)    = a*T + b + d*g     from the record's deviation d in floors
    Ron(base) = a*T + b           from the fingerprint itself
    C         = sqrt( Ron(base) / Ron(t) )

Nothing is added to the fingerprint -- a, b and g are already in it. The
question is only whether the formats survive: float32 in the record, and on
the bus a byte in 0.1-floor steps saturating at 25.5.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mosfet_precursor as mos
from assist_capability import capability
from boundary_vs_refresh import series, line

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "power_module_model.tsv"
M1, M2 = 0.01, 0.02              # docs/332
BUS_STEP, BUS_MAX = 0.1, 25.5    # docs/318's two-byte frame


def reconstruct(dev):
    """C per run from what the recorder would actually have stored."""
    y, op, rid, _stress, n1 = series(dev)
    fpm = np.arange(len(y)) < n1 // 2
    a, b, g = line(y[fpm], op[fpm])          # the fingerprint's three numbers
    if g <= 0:
        return None
    runs = sorted(set(rid.tolist()))
    lo = max(op[rid == r].min() for r in runs)
    hi = min(op[rid == r].max() for r in runs)
    inside = (op >= lo) & (op <= hi)
    t_ref = float(np.median(op[inside]))

    out = {}
    for r in runs:
        m = (rid == r) & inside
        if not m.any():
            continue
        d = (y[m] - (a * op[m] + b)) / g      # deviation in this unit's floors
        # what the 30-byte record holds: float32 of the deviation and the
        # operating point, nothing else
        d32 = np.frombuffer(np.asarray(d, np.float32).tobytes(), np.float32)
        # what the 2-byte frame holds: 0.1 floors, saturating at 25.5
        dbus = np.clip(np.round(np.abs(d32) / BUS_STEP) * BUS_STEP, 0, BUS_MAX)
        dbus = np.copysign(dbus, d32)
        base = a * t_ref + b
        out[r] = dict(
            rec=float(np.median(base + d32 * g)),
            bus=float(np.median(base + dbus * g)),
            base=base,
            sat=float(np.mean(np.abs(d32) > BUS_MAX)))
    # capability is relative to the healthy interval, as docs/331 fixed it
    for key in ("rec", "bus"):
        h = float(np.median([out[r][key] for r in out if r <= 4]))
        for r in out:
            out[r]["C_" + key] = float(np.sqrt(h / out[r][key]))
    return out


def main() -> None:
    print("30 バイトの記録と 56 バイトの指紋だけから C を復元する")
    print(f"{'素子':>8} {'run':>4} {'真値 C':>8} {'記録から':>9} {'差':>8} "
          f"{'バスから':>9} {'差':>8} {'飽和':>7}")
    print("-" * 72)
    rows, e_rec, e_bus, sat_any = [], [], [], []
    for dev in mos.DEVICES:
        truth, _t, _s = capability(dev)
        got = reconstruct(dev)
        if truth is None or got is None:
            print(f"{dev:>8}  復元できない")
            continue
        for r in sorted(got):
            if r not in truth:
                continue
            dr = got[r]["C_rec"] - truth[r]
            db = got[r]["C_bus"] - truth[r]
            s = got[r]["sat"]
            print(f"{dev:>8} {r:>4} {truth[r]:>8.3f} {got[r]['C_rec']:>9.3f} "
                  f"{dr:>+8.4f} {got[r]['C_bus']:>9.3f} {db:>+8.4f} {s:>6.1%}")
            e_rec.append(abs(dr)); e_bus.append(abs(db)); sat_any.append(s)
            rows.append((dev, r, truth[r], got[r]["C_rec"], dr,
                         got[r]["C_bus"], db, s))

    # docs/280's admission test, run here on the same devices: fit the
    # fingerprint on the first half of run 1, then see how far a held-out
    # healthy interval misses it. A unit that cannot describe its own healthy
    # self must never be allowed to declare -- and it must not be allowed to
    # supply a capability estimate either.
    print(f"\n出荷時の採否判定は、当てはめが壊れた素子を弾けるか"
          f"（保留した健全区間のずれ、単位は床）")
    admitted = {}
    for dev in mos.DEVICES:
        y, op, rid, _s, n1 = series(dev)
        h = n1 // 2
        a, b, g = line(y[:h], op[:h])
        if g <= 0:
            continue
        held = np.abs(np.median((y[h:n1] - (a * op[h:n1] + b)) / g))
        admitted[dev] = float(held)
        errs = [abs(x[4]) for x in rows if x[0] == dev]
        worst = max(errs) if errs else float("nan")
        # docs/325's rule applied to the fingerprint itself: Ron rises with
        # temperature, so a negative slope is not a poor fit, it is a
        # physically impossible one. The held-out shift cannot see this --
        # a wrong fingerprint can still be internally consistent.
        phys = a > 0
        print(f"  Test_{dev:<3} ずれ {held:>6.3f} 床  傾き {a:>+9.5f}  "
              f"{'採用' if held < 1.0 and phys else '**除外**'}"
              f"{'' if phys else '(傾きが負。物理に反する)':>0}"
              f"  復元の最大誤差 {worst:.4f}")
        admitted[dev] = float(held) if phys else float("inf")

    keep = [d for d in admitted if admitted[d] < 1.0]
    e_ok = [abs(x[4]) for x in rows if x[0] in keep]
    if e_ok and len(keep) < len(admitted):
        print(f"\n  採用された素子だけなら 差の中央値 {np.median(e_ok):.4f}、"
              f"最大 {max(e_ok):.4f}")

    mr, mb = float(np.median(e_rec)), float(np.median(e_bus))
    print(f"\n=== 事前登録した判定 ===")
    print(f"  M1 記録から  差の中央値 {mr:.4f} < {M1}  "
          f"→ {'PASS' if mr < M1 else 'FAIL'}   最大 {max(e_rec):.4f}")
    print(f"  M2 バスから  差の中央値 {mb:.4f} < {M2}  "
          f"→ {'PASS' if mb < M2 else 'FAIL'}   最大 {max(e_bus):.4f}")
    top = max(sat_any)
    print(f"  M3 飽和(25.5 床超え)の割合  最大 {top:.1%}  "
          f"→ {'バスからは復元できない run がある' if top > 0 else '飽和なし'}")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("device\trun\tC_truth\tC_record\terr_record\t"
                 "C_bus\terr_bus\tsaturated_frac\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
