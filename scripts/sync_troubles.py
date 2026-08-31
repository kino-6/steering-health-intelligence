#!/usr/bin/env python3
"""Write new failures into TROUBLES.md automatically (2026-09-01).

The user's instruction was that the human side cannot catch these, so the
register must not depend on anyone remembering to add a row. This script
finds every document that declares a correction, a withdrawal or a failed
test, and appends the ones missing from TROUBLES.md to an "unclassified"
section, with the heading that triggered it.

    python3 scripts/sync_troubles.py          # append and report
    python3 scripts/sync_troubles.py --check   # report only, exit 1 if any

It runs from .git/hooks/pre-commit before check_repo.py, so the entry is
written and staged by the same commit that introduces the failure. Nothing is
lost. check_repo.py then blocks while the unclassified section is non-empty,
so the entry has to be moved under a type before the commit completes:
writing it down is automatic, deciding what type it is is not.
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "TROUBLES.md"
SECTION = "## 未分類(自動追記) — 型に振り分けること"

MARKERS = ("訂正", "撤回", "取り下げ", "不成立", "外れた", "誤りである", "打ち切")
# a pre-registration says in advance what it will report if the test fails.
# That is the discipline working, not a trouble.
FORWARD = ("場合", "したときに", "たら", "なければ")


def failing_docs() -> list[tuple[str, str]]:
    out = []
    for f in sorted((ROOT / "docs").glob("*.md")):
        heads = [ln for ln in f.read_text(encoding="utf-8").splitlines()
                 if ln.lstrip().startswith("#") or ln.lstrip().startswith("> **")]
        hit = [h for h in heads
               if any(m in h for m in MARKERS) and not any(w in h for w in FORWARD)]
        if hit:
            out.append((f.name, hit[0].strip().lstrip("#> *").strip()))
    return out


def unclassified_body(text: str) -> str:
    if SECTION not in text:
        return ""
    return text.split(SECTION, 1)[1]


def main() -> int:
    if not REG.exists():
        print("TROUBLES.md が無い")
        return 1
    text = REG.read_text(encoding="utf-8")
    missing = [(n, h) for n, h in failing_docs() if n not in text]

    if "--check" in sys.argv:
        body = unclassified_body(text)
        pend = [ln for ln in body.splitlines() if ln.startswith("| docs/")]
        for n, h in missing:
            print(f"未登録: {n}  — {h[:80]}")
        for ln in pend:
            print(f"未分類: {ln[:100]}")
        return 1 if (missing or pend) else 0

    if not missing:
        print("TROUBLES.md: 追記なし")
        return 0

    if SECTION not in text:
        anchor = "## この登録簿自体の限界"
        block = (f"{SECTION}\n\n"
                 "**下は `scripts/sync_troubles.py` が自動で書き込んだ。**\n"
                 "**型に振り分けて、この節を空にするまでコミットは通らない。**\n\n"
                 "| 文書 | 宣言した見出し | 検出日 |\n|---|---|---|\n\n---\n\n")
        text = text.replace(anchor, block + anchor, 1)

    head, tail = text.split(SECTION, 1)
    rows = "".join(f"| [{n}](docs/{n}) | {h[:90]} | {date.today()} |\n" for n, h in missing)
    # insert after the table header inside the section
    m = re.search(r"\|---\|---\|---\|\n", tail)
    tail = tail[:m.end()] + rows + tail[m.end():]
    REG.write_text(head + SECTION + tail, encoding="utf-8")

    for n, h in missing:
        print(f"TROUBLES.md に自動追記: {n} — {h[:70]}")
    subprocess.run(["git", "add", str(REG)], cwd=ROOT, check=False)
    print(f"{len(missing)} 件を未分類として追記し、staged した。型に振り分けること")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
