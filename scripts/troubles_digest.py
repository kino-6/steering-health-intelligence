#!/usr/bin/env python3
"""Print the trouble-type table so it is in context, not in a file nobody opens.

Wired to SessionStart in .claude/settings.local.json, so every session begins
with the 18 types already present. The user's instruction on 2026-09-01 was
that the human side cannot catch these; a register that has to be opened
deliberately would depend on exactly the attention that is missing.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "TROUBLES.md"
TOP = 6


def main() -> None:
    if not REG.exists():
        return
    rows = [ln for ln in REG.read_text(encoding="utf-8").splitlines()
            if ln.startswith("| **T")]
    if not rows:
        return
    print("過去トラブルの型 (TROUBLES.md / .claude/skills/troubles)。"
          "結論を書く前・報告する前に当てること。")
    for ln in rows[:TOP]:
        cells = [c.strip().strip("*") for c in ln.strip("|").split("|")]
        if len(cells) >= 3:
            print(f"  {cells[0]} — {cells[1]} (過去{cells[2]}回)")
    if len(rows) > TOP:
        print(f"  ...ほか{len(rows) - TOP}型。全文は TROUBLES.md")
    print("  最多のT14は6回とも自分では気づけずユーザ指摘で判明している。"
          "「無い」と書く前に探索の軸を変えてもう一度探すこと。")


if __name__ == "__main__":
    main()
