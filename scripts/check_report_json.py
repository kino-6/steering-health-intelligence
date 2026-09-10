#!/usr/bin/env python3
"""Gate a report JSON before it is rendered and published.

    python3 scripts/check_report_json.py reports/<name>.json

Every rule here is one the user had to state out loud, in this order:

  2026-09-07  「レポートの記述が気持ち悪すぎる。平易な日本語使ってほしい」   R3
  2026-09-07  「社内用語はありません。これは個人研究です」                  R0
  2026-09-08  「無駄に横幅が制限されており不要な改行が生成されている」       R4
  2026-09-08  「全体の流れとデータ構造以外は見る価値を感じない(ポエムのよう)」 R8
  2026-09-08  「数字だけ出されてもグラフでわかりやすくして」                R9
  2026-09-08  「指紋って一般的?」                                        R1
  2026-09-08  「レポートは折り畳みをしっかり使って」                        R7
  2026-09-09  「劣化具合出せてないじゃん」(成立を書いていない)               R2
  常時        「仮定した格子は根拠ではない」(数字の出所を先に言う)            R11

A rule that is only written down gets broken. AGENTS.md says so, and it was
broken four times before the checks existed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_plain_ja as pj

PROSE = {"p", "lead", "small", "note"}
BANNED = [
    (re.compile(r"自社|当社|弊社|社内"), "帰属先の会社は存在しない(AGENTS.md ルール0)"),
    (re.compile(r"指紋"), "この研究だけの造語。「出荷時基準値」と書く"),
    (re.compile(r"顧客|RFQ|売り込|見せる相手"), "外部の宛先は存在しない(AGENTS.md ルール0)"),
]
# pre-registration labels, sheet ids, file and tool names
SYMBOL = re.compile(r"(?<![A-Za-z])[TRDPNSMKALVX]\d{1,3}(?![A-Za-z0-9%])|EOOC\d+")
PLUMBING = re.compile(r"docs/\d+|[\w_]+\.py|[\w_]+\.tsv|check_repo|TROUBLES\.md|"
                      r"コミット|pre-commit|フック")
MAX_OPEN_ROWS = 8          # a longer table is folded
MAX_PROSE_SHARE = 0.55     # prose chars over prose+data chars
NEEDS_LEAD = {"table", "chart", "bytes", "eq", "svg"}


def strip(s: str) -> str:
    return re.sub(r"<[^>]+>", "", str(s))


def walk(blocks, path="", out=None):
    """Flatten nested fold blocks, keeping the source order and a depth flag."""
    out = [] if out is None else out
    for i, b in enumerate(blocks):
        out.append((f"{path}[{i}]", b, path != ""))
        if b["type"] == "fold":
            walk(b["blocks"], f"{path}[{i}].fold", out)
    return out


COUNTED = re.compile(r"\d[\d,]*(?:\.\d+)?\s*(?:行|点|本|台|回|素子|個体|条件|水準|節|章|"
                     r"件中|フィールド|ビット|バイト|文字)")


def numbers(s: str, claims_only=False) -> list[str]:
    """Numbers in a string. claims_only drops the ones that count the report's
    own parts (42 行, 3,796 点), which are not claims about the subject."""
    x = strip(s)
    if claims_only:
        x = COUNTED.sub(" ", x)
    return [n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", x)]


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_report_json.py <report.json>")
        return 2
    d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    bad: list[str] = []
    warn: list[str] = []

    # ---- R2  both halves, positives first (AGENTS.md 3.0 / TROUBLES T42)
    a = d.get("answer", {})
    if not a.get("holds"):
        bad.append("R2 answer.holds が空。成立する結果を必ず書く(AGENTS.md 3.0, T42)")
    if not a.get("fails"):
        bad.append("R2 answer.fails が空。限界を書かない報告は信用できない")

    # ---- collect every string and every number the report shows
    prose_chars = data_chars = 0
    pool: set[str] = set()
    raw_blocks: set[str] = set()          # blocks that quote data verbatim
    strings: list[tuple[str, str]] = []          # (where, text)

    def add_num(v):
        nonlocal data_chars
        if isinstance(v, (int, float)):
            data_chars += len(str(v))
            for s in (f"{v}", f"{v:.1f}", f"{v:.2f}", f"{v:.3f}", f"{int(v)}" if v == int(v) else "",
                      f"{v * 100:.1f}", f"{v * 100:.0f}"):
                if s:
                    pool.add(s.rstrip("0").rstrip(".") if "." in s else s)
                    pool.add(s)
        else:
            for n in numbers(v):
                pool.add(n)
                pool.add(n.rstrip("0").rstrip(".") if "." in n else n)

    for si, s in enumerate(d["sections"]):
        for where, b, nested in walk(s["blocks"], f"{s['h']}"):
            t = b["type"]
            if t in PROSE:
                if b.get("raw"):
                    raw_blocks.add(where)
                strings.append((where, b["text"]))
                prose_chars += len(strip(b["text"]))
            elif t == "table":
                for c in b["cols"]:
                    add_num(c["t"] if isinstance(c, dict) else c)
                for row in b["rows"]:
                    for c in (row["cells"] if isinstance(row, dict) else row):
                        v = c.get("v", "") if isinstance(c, dict) else c
                        add_num(v)
                        data_chars += len(strip(v))
                if b.get("note"):
                    strings.append((where + ".note", b["note"]))
                    prose_chars += len(strip(b["note"]))
            elif t == "chart":
                strings.append((where + ".caption", b["caption"]))
                prose_chars += len(strip(b["caption"]))
                for v in json_numbers(b):
                    add_num(v)
            elif t == "kpi":
                for i in b["items"]:
                    add_num(i["v"])
                    data_chars += len(strip(i["v"]))
            elif t in ("svg", "eq", "bytes"):
                if b.get("caption"):
                    strings.append((where + ".caption", b["caption"]))
                    prose_chars += len(strip(b["caption"]))
    for x in a.get("holds", []) + a.get("fails", []):
        strings.append(("答え", x))
        prose_chars += len(strip(x))
    strings.append(("lede", d["lede"]))
    for k in d.get("scope", []):
        strings.append((f"成立範囲/{k['k']}", k["v"]))
        add_num(k["v"])

    # ---- R0/R1  banned words, anywhere
    for where, s in strings:
        for rx, why in BANNED:
            m = rx.search(strip(s))
            if m:
                bad.append(f"R0 {where} 「{m.group()}」 — {why}")

    # ---- R3  plain Japanese. A raw block quotes data verbatim (a byte dump,
    # a serial number); the sentence rules do not apply to a quotation.
    for where, s in strings:
        if where in raw_blocks:
            continue
        h, w = pj.check_text(where, s)
        bad += [f"R3 {x}" for x in h]
        warn += [f"R3 {x}" for x in w]

    # ---- R4  no hard-wrapped prose
    for where, s in strings:
        if "\n" in s:
            bad.append(f"R4 {where} に改行が入っている。折り返しは表示側の仕事である")

    # ---- R10  internal symbols and tool names stay out of the prose.
    # A report may declare the domain names that look like labels (channel
    # names such as T1) in "terms". Declaring them is the point: it is visible
    # in the JSON, so a pre-registration label cannot slip through as one.
    allow = sorted(d.get("terms", []), key=len, reverse=True)
    for where, s in strings:
        p = strip(s)
        for w in allow:
            p = p.replace(w, "_")
        for rx, why in ((SYMBOL, "事前登録の記号。読者には意味がない"),
                        (PLUMBING, "ファイル名や道具の名前は本文に出さない")):
            m = rx.search(p)
            if m:
                bad.append(f"R10 {where} 「{m.group()}」 — {why}")

    # ---- R5/R6/R7/R11  per block
    for s in d["sections"]:
        flat = walk(s["blocks"], s["h"])
        for i, (where, b, nested) in enumerate(flat):
            t = b["type"]
            if t in NEEDS_LEAD:
                prev = flat[i - 1][1]["type"] if i else None
                if prev not in ("lead", "small", "p", "h3", "note", "fold"):
                    bad.append(f"R5 {where} ({t}) の直前に説明の1文が無い。"
                               f"表と図の前には、それが何を言っているかを1文置く")
            if t == "chart":
                if not b.get("alt"):
                    bad.append(f"R6 {where} に alt が無い")
                if not b.get("caption"):
                    bad.append(f"R6 {where} に caption が無い")
                if b.get("source") not in ("measured", "simulated", "assumed", "derived"):
                    bad.append(f"R11 {where} に source が無い。"
                               f"measured / simulated / assumed / derived のどれか")
            if t == "table":
                n = len(b["rows"])
                if n > MAX_OPEN_ROWS and not b.get("fold"):
                    bad.append(f"R7 {where} は {n} 行ある。{MAX_OPEN_ROWS} 行を超える表は "
                               f"fold を付けて畳む")

    # ---- R8  prose budget
    total = prose_chars + data_chars
    share = prose_chars / total if total else 1.0
    if share > MAX_PROSE_SHARE:
        bad.append(f"R8 文章が全体の {share:.0%}（上限 {MAX_PROSE_SHARE:.0%}）。"
                   f"文章 {prose_chars} 字 / データ {data_chars} 字。"
                   f"説明を削るか、数字を足す")

    # ---- R9  a number in the prose must exist in the data
    for where, s in strings:
        if where.startswith(("答え", "成立範囲")) or where in raw_blocks:
            continue
        for n in numbers(s, claims_only=True):
            v = float(n)
            if v < 10 and "." not in n:
                continue                     # small counts read as words
            key = n.rstrip("0").rstrip(".") if "." in n else n
            if n not in pool and key not in pool:
                warn.append(f"R9 {where} の「{n}」が表にも図にも無い。"
                            f"本文の数字は、必ずデータとして載っているものにする")

    for b in bad:
        print(f"  NG  {b}")
    for w in warn[:14]:
        print(f"  warn {w}")
    if len(warn) > 14:
        print(f"  warn ... ほか {len(warn) - 14} 件")
    if not bad:
        print(f"  ok  {Path(sys.argv[1]).name}  "
              f"文章 {share:.0%} / 節 {len(d['sections'])} / warn {len(warn)}")
    return 1 if bad else 0


def json_numbers(o):
    if isinstance(o, (int, float)) and not isinstance(o, bool):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            if k not in ("caption", "alt", "axis", "title", "ylabel"):
                yield from json_numbers(v)
    elif isinstance(o, list):
        for v in o:
            yield from json_numbers(v)


if __name__ == "__main__":
    raise SystemExit(main())
