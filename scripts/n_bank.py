#!/usr/bin/env python3
"""Take the averaging length N out of the choices. (docs/297)

Executes the protocol pre-registered in docs/297, under its one-time revision
(recorded below; the addendum to docs/297 is written separately).

docs/295 reached 5/6 by picking one N from an assumed grid, and docs/296 showed
that the pick does not travel: leaving one device out, the remaining five pick
N = 100, 200 or 500 depending on which device is missing, and a threshold
carried from the other five fires 1,817 times the design rate on Test_10.
Two things were fitted to the six devices -- N and the threshold -- and
neither survives a change of device.

This removes both choices. A bank of three averaging lengths {100, 200, 500}
runs at once, all the time; no N is selected. The threshold of each bank
member comes from the device's own healthy stretch, at one alarm per hour
divided by three because the three members are OR-ed (docs/294, T33).
Nothing from any other device enters the threshold. Fire is the first sample
at which any member exceeds its own threshold.

One-time revision of docs/297 (protocol defect found in execution, rule 3 of
AGENTS.md; no further revision). As written, the intervals were fractions of
the runtime: calibration = first quarter, B2 = after the quarter through run 4.
Runs 5-7 hold 5 to 7 times the conducting samples of runs 1-4, so a quarter
of the runtime ends 2,000-6,000 samples inside run 5 on every device: the
"healthy" calibration contained the onset, and the B2 region was empty on all
six. The intervals are therefore defined by RUN BOUNDARY:

    fingerprint   first half of run 1                       (unchanged)
    calibration   second half of run 1 + run 2 + run 3      (thresholds)
    B2 region     run 4 only -- docs/295 shows all six run-4 medians within
                  0.24 floors, healthy by evidence and disjoint from calibration
    detection     from the start of run 5 to the end of the record

Bank, rate (1/36000 per decision, divided by 3 per member), clamp-and-report
rule and the OR over members are unchanged.

Criteria, fixed before running: B1 five of six devices fire before the record
ends; B2 the false-alarm rate on run 4 stays within three times the design
rate on every device; B3 the run of the first fire, reported against
docs/295's run 4 to 5.

Stated deviation from a literal reading: the calibration stretch is short of
the 1/108000 quantile, so the quantile is clamped to 1 - 1/len(sample) and
the achieved rate is printed per member and for the OR of the bank.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import element_v2 as el
import mosfet_precursor as mos
from real_degradation import device_series, FP_FRAC
from slow_channel import slow_deviation, FA_PER_HOUR, HOUR_SAMPLES

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "n_bank.tsv"

BANK = [100, 200, 500]                 # docs/297, all three, always
DESIGN = FA_PER_HOUR / HOUR_SAMPLES    # one alarm per hour, one decision per sample
PER_MEMBER = DESIGN / len(BANK)        # OR of three members (docs/294 T33)
CAL_END_RUN = 3                        # revision: calibration = rest of run 1 + runs 2-3
FA_RUN = 4                             # revision: B2 region = run 4 only
DETECT_FROM_RUN = 5                    # revision: search for the fire from run 5
REF_295 = {8: 5, 9: 4, 10: 5, 11: 5, 12: 5, 14: 5}   # docs/295, first fire run


def main() -> None:
    print("=== B1/B2/B3  平均長のバンク {100,200,500}。閾値は個体自身の健全区間 ===")
    print(f"  docs/297 の 1 回限りの改訂: 区間は標本の割合ではなく run 境界で切る。"
          f"較正 = run 1 後半 + run 2〜{CAL_END_RUN}、誤報評価 = run {FA_RUN}、探索 = run {DETECT_FROM_RUN} 以降")
    print(f"  設計: 誤報 {FA_PER_HOUR:.0f} 件/時 = 1/{HOUR_SAMPLES} /判定、"
          f"3 本の OR なので 1 本あたり 1/{int(1/PER_MEMBER)} /判定")
    rows = []
    for dev in mos.DEVICES:
        y, t, run_of = device_series(dev)
        n1 = int((run_of == 1).sum())
        cut = int(n1 * FP_FRAC)
        fp = el.take_fingerprint(y[:cut], t[:cut])
        yr, tr, rr = y[cut:], t[cut:], run_of[cut:]
        n_rt = len(yr)
        cal_mask = rr <= CAL_END_RUN
        reg_mask = rr == FA_RUN
        det_mask = rr >= DETECT_FROM_RUN
        n_cal_samples = int(cal_mask.sum())
        det_start = int(np.flatnonzero(det_mask)[0])

        alarm = np.zeros(n_rt, dtype=bool)            # OR over the bank, per sample
        member, thr, achieved, n_cal, in_cal = {}, {}, {}, {}, {}
        for n in BANK:
            d = slow_deviation(yr, tr, fp, n)
            if d is None:
                print(f"  Test_{dev}: N={n} に対して標本が足りない")
                continue
            end = np.arange(len(d)) + n - 1           # sample at which each mean is available
            cal = d[cal_mask[end]]                    # means available inside the calibration runs
            q = 1 - PER_MEMBER
            if q > 1 - 1.0 / len(cal):                # never a quantile outside the sample
                q = 1 - 1.0 / len(cal)
            thr[n] = float(np.quantile(cal, q))
            achieved[n] = 1 - q                       # per decision, per member
            n_cal[n] = len(cal)
            a = np.zeros(n_rt, dtype=bool)
            a[end] = d > thr[n]
            member[n] = a
            in_cal[n] = int(a[cal_mask].sum())
            alarm |= a

        # fire: first sample from the start of run 5 at which any member exceeds
        after = np.flatnonzero(alarm & det_mask)
        fire = int(after[0]) if len(after) else None
        fired = fire is not None
        fire_run = int(rr[fire]) if fired else None
        fire_by = [n for n in BANK if n in member and member[n][fire]] if fired else []

        # B2: run 4, disjoint from calibration
        n_reg = int(reg_mask.sum())
        fa_count = int(alarm[reg_mask].sum())
        fa_rate = fa_count / n_reg if n_reg else float("nan")
        fa_ratio = fa_rate / DESIGN
        fa_member = {n: int(member[n][reg_mask].sum()) for n in member}
        ach_or = sum(achieved.values())               # OR bound over the bank

        per_run = [int((rr == k).sum()) for k in range(1, mos.N_RUNS + 1)]
        print(f"\n  Test_{dev}: 運用 {n_rt} 標本 ({n_rt/HOUR_SAMPLES:.2f} h)、run 別 {per_run}")
        print(f"    較正区間 {n_cal_samples} 標本 ({n_cal_samples/HOUR_SAMPLES:.2f} h)、"
              f"誤報評価区間 (run {FA_RUN}) {n_reg} 標本 ({n_reg/HOUR_SAMPLES:.2f} h)、"
              f"探索区間 run {DETECT_FROM_RUN}〜 {int(det_mask.sum())} 標本")
        for n in BANK:
            if n not in thr:
                continue
            print(f"    N={n:>3}: 較正標本 {n_cal[n]:>5}  閾値 {thr[n]:.3f}  "
                  f"達成率 1/{int(round(1/achieved[n]))} /判定 (= {achieved[n]*HOUR_SAMPLES:.2f} 件/時)  "
                  f"較正内の超過 {in_cal[n]}  run {FA_RUN} の超過 {fa_member[n]}")
        print(f"    OR 達成率 {ach_or*HOUR_SAMPLES:.2f} 件/時 (設計 {FA_PER_HOUR:.0f}、"
              f"{ach_or/DESIGN:.1f} 倍)")
        print(f"    初発火: {(f'標本 {fire} (run {fire_run}, run {DETECT_FROM_RUN} 開始の {fire - det_start} 標本後 = {(fire - det_start)/HOUR_SAMPLES:.2f} h, N={fire_by})' if fired else '鳴らず')}")
        print(f"    誤報 (run {FA_RUN}): {fa_count} 件 / {n_reg} 判定 = 設計比 {fa_ratio:.2f} 倍"
              f"  (達成率比 {fa_rate/ach_or if ach_or else float('nan'):.2f} 倍)")
        rows.append({"dev": dev, "fire": fire, "fire_run": fire_run, "fired": fired,
                     "fa_ratio": fa_ratio, "fa_count": fa_count, "n_reg": n_reg,
                     "thr": thr, "ach": ach_or * HOUR_SAMPLES, "fire_by": fire_by,
                     "n_cal": n_cal_samples, "fire_after": (fire - det_start) if fired else None})

    # ---- verdicts --------------------------------------------------------
    n_fired = sum(1 for r in rows if r["fired"])
    print(f"\n=== B1 故障前(記録終了前)に鳴った素子 ===")
    print(f"  {n_fired}/{len(rows)}  {'PASS' if n_fired >= 5 else 'FAIL'} (基準: 6 中 5 以上)")

    print(f"\n=== B2 健全区間 (run {FA_RUN}) の誤報、素子ごと ===")
    all_ok = True
    for r in rows:
        ok = r["fa_ratio"] <= 3
        all_ok &= ok
        print(f"  Test_{r['dev']:<3} {r['fa_count']:>4} 件 / {r['n_reg']} 判定  "
              f"設計比 {r['fa_ratio']:>6.2f} 倍  {'ok' if ok else 'NG'}")
    print(f"  {'PASS' if all_ok else 'FAIL'} (基準: 6 素子すべて 3 倍以内)")

    print(f"\n=== B3 初発火の run、docs/295 の run 4〜5 と比べる ===")
    print(f"  {'素子':>8} {'本文書':>8} {'docs/295':>9} {'鳴った N':>10} {'run5開始後':>10}")
    for r in rows:
        here = f"run {r['fire_run']}" if r["fired"] else "鳴らず"
        aft = f"+{r['fire_after']}" if r["fired"] else "—"
        print(f"  Test_{r['dev']:<3} {here:>8} {'run ' + str(REF_295[r['dev']]):>9} "
              f"{str(r['fire_by']):>10} {aft:>10}")
    same = sum(1 for r in rows if r["fired"] and r["fire_run"] == REF_295[r["dev"]])
    earlier = sum(1 for r in rows if r["fired"] and r["fire_run"] < REF_295[r["dev"]])
    later = sum(1 for r in rows if r["fired"] and r["fire_run"] > REF_295[r["dev"]])
    print(f"  同じ run {same}、早い {earlier}、遅い {later}、鳴らず {len(rows) - n_fired}")
    print(f"  (探索は run {DETECT_FROM_RUN} から始めるので、run 4 以前の発火はこの設計では出ない)")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("device\tfire_index\tfire_run\tfired\tfa_ratio\t"
                 + "\t".join(f"thr_{n}" for n in BANK)
                 + "\tachieved_rate_per_hour\tcal_samples\tfa_region_samples\n")
        for r in rows:
            fh.write(f"Test_{r['dev']}\t{'' if r['fire'] is None else r['fire']}\t"
                     f"{'' if r['fire_run'] is None else r['fire_run']}\t"
                     f"{int(r['fired'])}\t{r['fa_ratio']:.4f}\t"
                     + "\t".join(f"{r['thr'][n]:.5f}" if n in r["thr"] else "" for n in BANK)
                     + f"\t{r['ach']:.4f}\t{r['n_cal']}\t{r['n_reg']}\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
