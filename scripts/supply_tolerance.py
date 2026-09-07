"""How much supply variation does the six-hour configuration survive (docs/326)?

docs/323 cut the end-of-line sweep to six hours by keeping three channels, and
all three are DC-side quantities -- the place a vehicle moves most, and the
place this bench moves least (its DC bus swings 4.5 percent of its median,
because it is a laboratory supply).

No public record of real vehicle supply variation is in hand, so the question
is inverted the way docs/261 and docs/263 inverted theirs: not how much a car
moves, but how much movement the element survives, in the observable's own
units.

Enrolment is left undisturbed -- a production line has a stable supply -- and
the perturbation is added at runtime only. It is common to Vdc, Vd and Idc,
because a supply that moves moves them together.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eps_health_recorder as ehr
from demo_recorder import SIBLINGS, as_dicts
from inverter_recorder import ZIP, BASE, read

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "supply_tolerance.tsv"
DC = ("Vdc", "Vd", "Idc")            # docs/323's three, ranked from healthy data alone
AMPS = [0.0, 0.01, 0.02, 0.05, 0.10, 0.20, 0.30]
S1_FACTOR = 3.0                      # docs/326, stated there as having nothing behind it


def perturb(vals: dict, amp: float) -> dict:
    """One slow sinusoid, one period over the record, common to the DC channels.

    Shape and period are chosen, not derived (docs/326 says so). The point is
    that the same disturbance reaches every DC-side channel at once, which is
    what a moving supply does and what no sibling is present to cancel.
    """
    if amp <= 0:
        return vals
    out = dict(vals)
    n = len(next(iter(vals.values())))
    w = np.sin(2 * np.pi * np.arange(n) / n)
    for c in DC:
        if c in out:
            out[c] = out[c] + amp * float(np.median(out[c])) * w
    return out


def run(keep, v_en, o_en, v_ho, o_ho, faults, amp):
    sel = lambda d: {k: d[k] for k in keep}
    sib = {k: [s for s in SIBLINGS.get(k, []) if s in keep] for k in keep}
    fp = ehr.enrol(sel(v_en), sel(o_en), siblings=sib, alarm_per_hour=1.0)
    ach = max(max(c.alarm_per_hour_fast, c.alarm_per_hour_slow)
              for c in fp.channels.values())
    # the perturbation reaches the observable and the operating point alike,
    # because on this rig Vdc's operating point is Idc and Idc's is Vdc
    ho_v, ho_o = perturb(sel(v_ho), amp), perturb(sel(o_ho), amp)
    fa = sum(1 for r in ehr.Recorder(fp).run_session(
        ho_v, ho_o, siblings=sib, alarm_per_hour=ach) if r.validity and r.flags)
    det = 0
    for arr in faults.values():
        v, o = as_dicts(arr)
        rs = ehr.Recorder(fp).run_session(perturb(sel(v), amp), perturb(sel(o), amp),
                                          siblings=sib, alarm_per_hour=ach)
        det += any(r.validity and r.flags for r in rs)
    return fa, det


def main() -> None:
    z = zipfile.ZipFile(ZIP)
    names = [n for n in z.namelist() if n.startswith(BASE) and n.endswith(".txt")]
    normal = read(z, next(n for n in names if "normal_operation" in n))
    faults = {Path(f).stem: read(z, f)
              for f in sorted(n for n in names if "fault_scenarios" in n)}
    half = len(normal) // 2
    v_en, o_en = as_dicts(normal[:half])
    v_ho, o_ho = as_dicts(normal[half:])

    full = ehr.enrol(v_en, o_en, siblings=SIBLINGS, alarm_per_hour=1.0)
    three = sorted(full.admitted, key=lambda n: full.channels[n].cv_shift)[:3]
    eight = list(full.admitted)
    assert set(three) == set(DC), three

    print(f"3 本構成: {','.join(three)}   8 本構成: {len(eight)} 本")
    print(f"この試験機の Vdc の振れは中央値の 4.5%（実測）\n")
    print(f"{'振幅':>6} {'3本 誤報':>9} {'3本 検出':>9} {'8本 誤報':>9} {'8本 検出':>9}")
    print("-" * 48)
    rows, base3, base8 = [], None, None
    for amp in AMPS:
        fa3, d3 = run(three, v_en, o_en, v_ho, o_ho, faults, amp)
        fa8, d8 = run(eight, v_en, o_en, v_ho, o_ho, faults, amp)
        if base3 is None:
            base3, base8 = fa3, fa8
        print(f"{amp:>5.0%} {fa3:>9} {f'{d3}/8':>9} {fa8:>9} {f'{d8}/8':>9}")
        rows.append((amp, fa3, d3, fa8, d8))

    ok3 = [r for r in rows
           if r[1] <= max(1, base3) * S1_FACTOR and r[2] == 8]
    ok8 = [r for r in rows
           if r[3] <= max(1, base8) * S1_FACTOR and r[4] == 8]
    s1 = max(r[0] for r in ok3) if ok3 else None
    s1_8 = max(r[0] for r in ok8) if ok8 else None

    print(f"\n=== 事前登録した判定 ===")
    print(f"  S1 3 本構成が持つ最大の電源変動 : "
          f"{'なし（0% でも条件を満たさない）' if s1 is None else f'{s1:.0%}'}")
    print(f"  S2 その振幅で検出 8/8            : "
          f"{'—' if s1 is None else 'PASS'}")
    print(f"  S3 8 本構成が持つ最大           : "
          f"{'なし' if s1_8 is None else f'{s1_8:.0%}'}"
          f"  → 3 本が先に壊れる: "
          f"{'はい' if (s1 is not None and s1_8 is not None and s1 < s1_8) else 'いいえ'}")
    if s1 is not None:
        if s1 < 0.05:
            print("\n  → 5% 未満。実験室電源の範囲でしか確かめられておらず、6 時間の主張は弱まる")
        elif s1 >= 0.20:
            print("\n  → 20% 以上。6 時間の構成は電源変動に対して丈夫であり、"
                  "docs/323 の懸念のうち電源の分は晴れる")
        else:
            print(f"\n  → 5〜20% の間（{s1:.0%}）。数字のまま記述する")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("amplitude\tfa_3ch\tdet_3ch\tfa_8ch\tdet_8ch\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
