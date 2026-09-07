"""Detect the writing habits that made the reports unreadable (AGENTS.md 3.1).

2026-09-07, the user asked how plain Japanese could be detected and corrected
at all, and noted that a gate looks hard. It is hard for the register as a
whole. It is not hard for the specific habits, and the habits are what actually
did the damage.

Three tiers, by how precisely each can be caught:

  block  a string that is always wrong here      -- em dash, rule-0 words
  block  a countable property                    -- sentence length
  warn   a pattern with real false positives     -- noun-stop, phrase density

The noun-stop rule is the interesting one. Japanese prose normally ends a
sentence on a predicate; ending on a noun is a stylistic device, and I used it
throughout. Without a morphological analyser, "the character before 。 is kanji
or katakana" approximates it, and the false-positive rate is measured by
--measure rather than assumed.

Run on a file, or with --measure to print hit rates over the repo.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAX_SENTENCE = 90

# always wrong in this repo
BLOCK = [
    (re.compile(r"——|――"), "「——」で文をつながない。文を切って接続詞を使う"),
    (re.compile(r"自社|当社|弊社|社内"), "帰属先の会社は存在しない(AGENTS.md ルール0)"),
]

# sentences ending on a noun. Excludes the endings that are legitimately
# nominal in a specification: 〜こと。 〜もの。 〜とき。 and bare figures.
NOUN_STOP = re.compile(r"[一-鿿ァ-ヺ][。]")
NOUN_OK = re.compile(r"(こと|もの|とき|ため|場合|以上|以下|以内|通り|倍|件|回|点)[。]")

# constructions I actually wrote, kept as a list that grows from real failures
# rather than from a theory of good style
NG = [
    ("のほうが", "「AのほうがBより」の比較。どちらがどうなのかを直接書く"),
    ("という読みが", "「〜という読みが出る」。誰がどう読むかを書く"),
    ("にほかならない", "強調のための言い換え。事実だけ書く"),
    ("と言ってよい", "断定を避ける飾り。断定するかしないかを決める"),
    ("ということである", "言い換えの入れ子。1文で言う"),
    ("に他ならない", "同上"),
    ("を意味する", "「〜を意味する」。何がどうなるかを直接書く"),
]


def sentences(line: str):
    for s in re.split(r"(?<=[。！？])", line):
        t = s.strip()
        if t:
            yield t


def prose_lines(text: str):
    """Only prose. Tables, headings, lists and code carry their own style."""
    in_code = False
    for i, l in enumerate(text.splitlines(), 1):
        if l.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or not l.strip():
            continue
        t = l.lstrip()
        # tables, headings and html carry their own conventions. Bullets and
        # block quotes do not -- in these reports they hold the prose, and
        # excluding them was hiding most of what this is meant to catch.
        if t.startswith(("|", "#", "<", "!")):
            continue
        t = re.sub(r"^[-*>]\s*", "", t)
        # numbered lists are catalogue entries, not prose. INDEX.md is 237
        # lines of them and triggered on every one before this line existed.
        if re.match(r"\d+[.)]\s", t):
            continue
        yield i, t


def check(path: Path, warn_too=True) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    hard, soft = [], []
    for i, l in prose_lines(text):
        for pat, why in BLOCK:
            m = pat.search(l)
            if m:
                hard.append(f"{i}行 「{m.group()}」 — {why}")
        for s in sentences(l):
            plain = re.sub(r"\[([^\]]*)\]\([^)]*\)|[*`]", r"\1", s)
            if len(plain) > MAX_SENTENCE:
                hard.append(f"{i}行 1文が {len(plain)} 文字 — {MAX_SENTENCE} 以内に切る")
            if not warn_too:
                continue
            tail = plain.strip()[-2:]
            if NOUN_STOP.search(tail) and not NOUN_OK.search(tail):
                soft.append(f"{i}行 体言止めの疑い: …{plain.strip()[-18:]}")
            for w, why in NG:
                if w in plain:
                    soft.append(f"{i}行 「{w}」 — {why}")
    return hard, soft


def measure() -> None:
    """Hit rate over the repo, so the gate is set from data not from taste."""
    files = sorted(list((ROOT / "docs").glob("*.md")) + list(ROOT.glob("*.md")))
    th = ts = tl = 0
    worst = []
    for f in files:
        h, s = check(f)
        n = sum(1 for _ in prose_lines(f.read_text(encoding="utf-8")))
        th += len(h); ts += len(s); tl += n
        if s:
            worst.append((len(s) / max(n, 1), len(s), n, f.name))
    print(f"文書 {len(files)} 件、散文行 {tl:,}")
    print(f"  ブロック該当 {th:,} 件")
    print(f"  警告該当     {ts:,} 件  (散文行の {ts/max(tl,1):.1%})")
    print("\n警告の密度が高い文書:")
    for r, s, n, name in sorted(worst, reverse=True)[:8]:
        print(f"  {r:6.1%}  {s:>4}/{n:<4}  {name}")


def main() -> int:
    if "--measure" in sys.argv:
        measure()
        return 0
    if len(sys.argv) < 2:
        print("usage: check_plain_ja.py <file> | --measure")
        return 2
    p = Path(sys.argv[1])
    hard, soft = check(p)
    for x in hard:
        print(f"  NG   {x}")
    for x in soft:
        print(f"  warn {x}")
    if not hard and not soft:
        print(f"  ok   {p.name}")
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
