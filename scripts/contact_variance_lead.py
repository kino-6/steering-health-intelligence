#!/usr/bin/env python3
"""Does resistance variance lead resistance level? (docs/173 -> docs/174)

Executes the protocol pre-registered in docs/173 against SOReDD, the
Stuttgart Open Relay Degradation Dataset (CC BY 4.0), which records contact
resistance through each relay's life to a terminal event.

Per unit, fixed in docs/173 before any value was read:

    selection  metadata.lastEvent present, and >= 1000 valid resistance
               samples after dropping NaN
    windows    the life split into 10 equal windows by sample order
    level      L_k = median resistance in window k
    variance   V_k = IQR / median in window k
    baseline   window 1 of that same unit -- never a population reference

    k_v  first window where V_k / V_1 > 1.50
    k_l  first window where L_k / L_1 > 1.10

The thresholds are set against the hypothesis on purpose: variance has to
move 50% while level only has to move 10%.

Criteria: C1 the majority of units have k_v < k_l; C2 the median lead
k_l - k_v; C3 where k_l falls in life, to compare with the knee-shaped
trajectory the literature describes (docs/172).
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / ".soredd"
OUT_TSV = REPO_ROOT / "data" / "contact_variance_lead.tsv"

N_WIN = 10
MIN_SAMPLES = 1000
V_RISE, L_RISE = 1.50, 1.10


# Three of the published files carry trailing commas before a closing brace
# or bracket, which is not valid JSON, and one is not clean UTF-8. Both are
# defects in the distributed files, not in the download -- sizes match the
# manifest exactly. Repaired on read rather than skipped.
TRAILING = re.compile(r",\s*([}\]])")

# "started" is recorded in lastEvent for a unit that never reached a terminal
# event, so it does not satisfy the selection rule of docs/173, which asks for
# units that reached one.
TERMINAL = {"stuck open", "stuck closed"}

UNPARSEABLE: list[str] = []


def load(path: Path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        try:
            d = json.loads(TRAILING.sub(r"\1", raw))
        except json.JSONDecodeError:
            # one published file is truncated at end of stream; its size matches
            # the manifest, so the distributed copy itself is incomplete
            UNPARSEABLE.append(path.name)
            return None
    m = d.get("metadata", {})
    if m.get("lastEvent") not in TERMINAL:
        return None
    vals = d.get("contactResistance", {}).get("values", [])
    r = []
    for t, x in vals:
        if isinstance(x, (int, float)) and not (isinstance(x, float) and math.isnan(x)):
            r.append(float(x))
    if len(r) < MIN_SAMPLES:
        return None
    return m, np.array(r)


def windows(r):
    """Level and relative variance per window, in sample order."""
    edges = np.linspace(0, len(r), N_WIN + 1).astype(int)
    L, V = [], []
    for i in range(N_WIN):
        seg = r[edges[i]:edges[i + 1]]
        med = float(np.median(seg))
        q1, q3 = np.percentile(seg, [25, 75])
        L.append(med)
        V.append((q3 - q1) / med if med else float("nan"))
    return np.array(L), np.array(V)


def first_over(x, ratio):
    """1-based index of the first window exceeding ratio x baseline; None if never."""
    base = x[0]
    if not base or base != base:
        return None
    for i in range(1, len(x)):
        if x[i] / base > ratio:
            return i + 1
    return None


def main() -> None:
    rows = []
    # relay types are A through E; globbing "A*.json" would silently analyse
    # 18 of the 100 units. The protocol does not restrict to one type.
    for p in sorted(CACHE.glob("*.json")):
        if p.name == "filelist.tsv":
            continue
        got = load(p)
        if not got:
            continue
        m, r = got
        L, V = windows(r)
        rows.append({
            "unit": p.stem, "cycles": m.get("cycles"), "event": m.get("lastEvent"),
            "load": m.get("resistiveLoad"), "voltage": m.get("voltage"), "n": len(r),
            "k_v": first_over(V, V_RISE), "k_l": first_over(L, L_RISE),
            "L": L, "V": V,
        })

    if UNPARSEABLE:
        print(f"読み取り不能だった配布ファイル: {len(UNPARSEABLE)} 件 {UNPARSEABLE}")
    print(f"選別後の個体数: {len(rows)}  (終端事象に到達 かつ {MIN_SAMPLES}点以上)")
    if not rows:
        print("該当なし"); return

    print(f"\n{'unit':>7} {'cycles':>9} {'event':>14} {'n':>7} {'k_v':>5} {'k_l':>5} {'先行':>6}")
    print("-" * 60)
    lead, both = [], 0
    c1 = 0
    for r in rows:
        kv, kl = r["k_v"], r["k_l"]
        mark = ""
        if kv and kl:
            both += 1
            lead.append(kl - kv)
            if kv < kl:
                c1 += 1
                mark = f"{kl - kv:+d}窓"
            else:
                mark = "なし"
        elif kv and not kl:
            mark = "変動のみ"
        elif kl and not kv:
            mark = "水準のみ"
        else:
            mark = "どちらも"
        print(f"{r['unit']:>7} {str(r['cycles']):>9} {str(r['event'])[:14]:>14} {r['n']:>7} "
              f"{str(kv):>5} {str(kl):>5} {mark:>6}")

    print(f"\n=== C1 先行性: 変動が水準より早い個体の割合 ===")
    print(f"  両方が発火した個体 {both} 件中 {c1} 件で k_v < k_l  "
          f"({c1/both:.0%} )  {'PASS' if both and c1 > both/2 else 'FAIL'} (基準: 過半)")
    only_v = sum(1 for r in rows if r["k_v"] and not r["k_l"])
    only_l = sum(1 for r in rows if r["k_l"] and not r["k_v"])
    print(f"  変動のみ発火 {only_v} 件 / 水準のみ発火 {only_l} 件")

    print(f"\n=== C2 先行幅 ===")
    if lead:
        print(f"  k_l − k_v の中央値: {np.median(lead):+.1f} 窓 (= 寿命の {np.median(lead)/N_WIN:+.0%})")
    else:
        print("  算出不能")

    print(f"\n=== C3 水準が立ち上がる位置(膝の確認) ===")
    kls = [r["k_l"] for r in rows if r["k_l"]]
    if kls:
        print(f"  k_l の中央値: {np.median(kls):.1f} / {N_WIN} 窓 "
              f"(= 寿命の {np.median(kls)/N_WIN:.0%} 時点)")
        print(f"  範囲: {min(kls)} 〜 {max(kls)}")

    with OUT_TSV.open("w") as fh:
        fh.write("unit\tcycles\tlast_event\tload\tvoltage\tn_samples\tk_variance\tk_level\t"
                 + "\t".join(f"L{i+1}" for i in range(N_WIN)) + "\t"
                 + "\t".join(f"V{i+1}" for i in range(N_WIN)) + "\n")
        for r in rows:
            fh.write(f"{r['unit']}\t{r['cycles']}\t{r['event']}\t{r['load']}\t{r['voltage']}\t"
                     f"{r['n']}\t{r['k_v']}\t{r['k_l']}\t"
                     + "\t".join(f"{v:.4f}" for v in r["L"]) + "\t"
                     + "\t".join(f"{v:.4f}" for v in r["V"]) + "\n")
    print(f"\nwrote {OUT_TSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
