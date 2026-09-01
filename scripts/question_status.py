#!/usr/bin/env python3
"""Count what is still open on the registered question (QUESTION.md).

2026-09-01, the user said the reports answer a specific sub-case and never the
question that was actually asked, and told me to loop until the question can be
answered rather than reporting each increment.

So the question lives in a file, decomposed into items that can be closed, and
this is what the report checker consults before letting a report out.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
Q = ROOT / "QUESTION.md"


def status():
    if not Q.exists():
        return None, [], []
    lines = Q.read_text(encoding="utf-8").splitlines()
    # the standing question is the first quoted line; it is never archived.
    # 2026-09-01: sub-questions were being answered in its place, and it was
    # moved to history as "closed" while later results kept changing its answer.
    head = next((l for l in lines if l.startswith("> **")), "").strip("> *")
    closed = [l for l in lines if re.match(r"\s*- \[x\]", l)]
    openi = [l for l in lines if re.match(r"\s*- \[ \]", l)]
    return head, closed, openi


def main() -> int:
    head, closed, openi = status()
    if head is None:
        print("QUESTION.md が無い")
        return 1
    print(f"問い: {head}")
    print(f"閉じた {len(closed)} / 開いている {len(openi)}")
    for l in openi:
        print("  open " + re.sub(r"\s*- \[ \]\s*", "", l))
    if not openi:
        print("  → すべて閉じている。問いに答えられる")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
