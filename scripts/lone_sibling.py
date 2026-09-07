"""Why does the fourth channel make false alarms jump (docs/328 -> docs/329)?

docs/323's table is not monotone: three DC channels give four false alarms,
adding T2 gives thirty-nine, and adding T1 and T3 after it brings them back to
eleven. The candidate written down before running is that T2's siblings are T1
and T3, neither of which is present at four channels, so T2 alone has no
common-mode rejection while the DC channels never needed any.

The decisive arm is the last one: keep the same four tests, but let T2 use T1
and T3 as rejection partners without admitting them. If that alone removes the
spike, the test count and the calibration are exonerated.
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
OUT = ROOT / "data" / "lone_sibling.tsv"
DC = ["Vdc", "Vd", "Idc"]
FOURTH = ["T2", "T1", "T3", "Ia", "Ib"]
L1_SPIKE, L2_SETTLED = 20, 10        # docs/328, stated there as having nothing behind them


def evaluate(tests, reject_with, v_en, o_en, v_ho, o_ho, faults):
    """tests: channels that may declare. reject_with: siblings usable for the
    common-mode subtraction, whether or not they are themselves tests."""
    need = sorted(set(tests) | set(reject_with))
    sel = lambda d: {k: d[k] for k in need}
    sib = {k: [s for s in SIBLINGS.get(k, []) if s in reject_with] for k in need}
    # enrol only the channels that may declare, but hand them the wider set so
    # common_mode_reject can reach a sibling that is not itself a test
    fp = ehr.enrol({k: ehr.common_mode_reject(sel(v_en), k, sib.get(k, ()))
                    for k in tests},
                   {k: o_en[k] for k in tests}, siblings={}, alarm_per_hour=1.0)
    ach = max(max(c.alarm_per_hour_fast, c.alarm_per_hour_slow)
              for c in fp.channels.values())
    pre = lambda v: {k: ehr.common_mode_reject(sel(v), k, sib.get(k, ()))
                     for k in tests}
    fa = sum(1 for r in ehr.Recorder(fp).run_session(
        pre(v_ho), {k: o_ho[k] for k in tests}, siblings={}, alarm_per_hour=ach)
        if r.validity and r.flags)
    det = 0
    for arr in faults.values():
        v, o = as_dicts(arr)
        rs = ehr.Recorder(fp).run_session(pre(v), {k: o[k] for k in tests},
                                          siblings={}, alarm_per_hour=ach)
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
    run = lambda t, r: evaluate(t, r, v_en, o_en, v_ho, o_ho, faults)

    base_fa, base_det = run(DC, [])
    print(f"3 本（DC 側のみ、同種チャネル無し）     誤報 {base_fa}  検出 {base_det}/8\n")

    print("4 本目を入れ替える。除去の相手は採用チャネルの中にしか居ない")
    print(f"{'4 本目':>7} {'集合内の同種':>14} {'誤報':>6} {'検出':>7}")
    rows, spikes = [], {}
    for x in FOURTH:
        tests = DC + [x]
        present = [s for s in SIBLINGS.get(x, []) if s in tests]
        fa, det = run(tests, tests)
        spikes[x] = fa
        print(f"{x:>7} {(','.join(present) or 'なし'):>14} {fa:>6} {f'{det}/8':>7}")
        rows.append(("swap", x, ",".join(present) or "-", fa, det))

    print("\n決定的な検査: 検定は 4 本のまま、T2 に T1・T3 を除去の相手としてだけ与える")
    fa_fix, det_fix = run(DC + ["T2"], DC + ["T2", "T1", "T3"])
    print(f"{'T2+相手':>7} {'T1,T3':>14} {fa_fix:>6} {f'{det_fix}/8':>7}")
    rows.append(("reject_only", "T2", "T1,T3", fa_fix, det_fix))

    temps = [spikes[x] for x in ("T2", "T1", "T3")]
    l1 = all(v >= L1_SPIKE for v in temps)
    l2 = fa_fix <= L2_SETTLED
    l3 = all(spikes[x] >= L1_SPIKE for x in ("Ia", "Ib"))
    print("\n=== 事前登録した判定 ===")
    print(f"  L1 T1・T3 を 4 本目にしても {L1_SPIKE} 件以上 : {temps} → {'PASS' if l1 else 'FAIL'}")
    print(f"  L2 除去の相手を与えると {L2_SETTLED} 件以下    : {fa_fix} → {'PASS' if l2 else 'FAIL'}")
    print(f"  L3 Ia・Ib も相方が居ないので跳ねる        : "
          f"{[spikes['Ia'], spikes['Ib']]} → {'PASS' if l3 else 'FAIL'}")
    if l1 and l2:
        print("\n  → H1。独りぼっちの同種チャネルが原因。"
              "同種を持つ量は、その同種も一緒に採用しないかぎり採用しない")
    elif not l2:
        print("\n  → H1 は落ちた。除去の相手を与えても戻らない。原因は分からない")
    else:
        print("\n  → 事前登録どおりには揃わなかった。表のまま記述する")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("arm\tfourth\tsiblings_available\tfalse_alarms\tdetected_of_8\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
