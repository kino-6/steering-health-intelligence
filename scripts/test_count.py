"""How few channels can carry the detection (docs/322 -> docs/323)?

docs/321 left one lever on the end-of-line time: line hours are tests divided
by the target alarm rate, so with the target fixed only the test count moves.
docs/286's eight of eight used all eight channels, and this measures what
survives cutting down to N.

The channels are ranked by cv_shift -- how far a held-out healthy interval
missed the fingerprint -- because that is decided from healthy data alone.
Ranking them by which ones detected would be choosing on the answer, and a
production line has no faults to choose with.

Data: Bacha et al., inverter-driven PMSM fault dataset, CC BY 4.0.
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
OUT = ROOT / "data" / "test_count.tsv"
NS = [1, 2, 3, 4, 6, 8]


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
    order = sorted(full.admitted, key=lambda n: full.channels[n].cv_shift)
    print("健全データだけで付けた順位（cv_shift 昇順。故障を一切見ていない）")
    for i, n in enumerate(order, 1):
        print(f"  {i}. {n:<5} cv_shift = {full.channels[n].cv_shift:.3f} 床")

    print(f"\n{'残す':>4} {'チャネル':>26} {'検定':>5} {'ライン':>8} "
          f"{'検出':>6} {'保留正常の誤報':>14} {'較正できた率':>14}")
    print("-" * 88)
    rows = []
    for N in NS:
        keep = order[:N]
        sel = lambda d: {k: d[k] for k in keep}
        sib = {k: [s for s in SIBLINGS.get(k, []) if s in keep] for k in keep}
        fp = ehr.enrol(sel(v_en), sel(o_en), siblings=sib, alarm_per_hour=1.0)
        ach = max(max(c.alarm_per_hour_fast, c.alarm_per_hour_slow)
                  for c in fp.channels.values())
        fa = sum(1 for r in ehr.Recorder(fp).run_session(
            sel(v_ho), sel(o_ho), siblings=sib, alarm_per_hour=ach)
            if r.validity and r.flags)
        det = 0
        for arr in faults.values():
            v, o = as_dicts(arr)
            rs = ehr.Recorder(fp).run_session(sel(v), sel(o), siblings=sib,
                                              alarm_per_hour=ach)
            det += any(r.validity and r.flags for r in rs)
        print(f"{N:>4} {','.join(keep):>26} {2*N:>5} {2*N:>6} 時間 "
              f"{f'{det}/8':>6} {fa:>14} {ach:>11.1f} 件/時")
        rows.append((N, ",".join(keep), 2 * N, det, fa, ach))

    print()
    best = [r for r in rows if r[3] == 8]
    if best:
        m = min(best, key=lambda r: r[0])
        print(f"G1 (N=1 で 8/8): {'PASS' if rows[0][3] == 8 else 'FAIL'}")
        print(f"G2 8/8 を保つ最小: {m[0]} 本 → 検定 {m[2]} → ライン {m[2]} 時間")
    else:
        print("G1 FAIL / G2 該当なし — どの本数でも 8/8 は残らない。"
              "健全データだけの順位では、検出に効くチャネルを選べていない")
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("n_channels\tchannels\tn_tests\tdetected_of_8\t"
                 "false_alarms\tachieved_per_hour\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
