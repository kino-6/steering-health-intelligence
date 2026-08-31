#!/usr/bin/env python3
"""Block a report that talks about the work instead of the answer.

    python3 scripts/check_report.py <draft.md>

2026-09-01, the user said the reports are unintelligible, and that this had
happened many times. .claude/skills/report/SKILL.md already existed and was
not followed, so the fix is not more prose.

The diagnosis, from this session's own reports: they narrate what happened to
the bookkeeping -- a check was added, a blank became a decision, a defect was
found and fixed -- and never state what the research question's answer is now.
A reader who is not tracking the document numbers cannot extract anything.

So the shape is fixed to four slots, and the work is allowed only in the last
one:

    ## 答え            what the question's answer is, now
    ## 前回からの変化    what moved since the last report, or that nothing did
    ## 根拠            numbers, in units that mean something outside this repo
    ## この答えが崩れる条件
    ## 作業            everything about scripts, checks, commits -- last, brief
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from question_status import status as question_status

REQUIRED = ["## 答え", "## 前回からの変化", "## 根拠", "## この答えが崩れる条件", "## 作業"]

# symbols the skill already bans: pre-registration labels and sheet ids
SYMBOL = re.compile(r"(?<![A-Za-z])[TRDPNSMKA]\d{1,3}(?![A-Za-z0-9])|EOOC\d+")
# file and tool names -- allowed only in the work section
PLUMBING = re.compile(r"docs/\d+|[\w_]+\.py|[\w_]+\.tsv|check_repo|TROUBLES\.md|"
                      r"SKILL\.md|origin/main|コミット|push|pre-commit|フック|hook")
ACTIVITY = re.compile(r"追加しました|直しました|更新しました|更新しています|作りました|"
                      r"実装しました|走らせました|引っかかりました|検査|スクリプト|登録簿")
# an internal multiple of a noise floor means nothing on its own
FLOOR = re.compile(r"床の[\d０-９]")
ABSOLUTE = re.compile(r"m/s|mA|\bA\b|°C|バイト|ビット|秒|分|時間|台|件|%|％")

# a falsification condition that only insiders could check is not one.
# 2026-09-01: a report said the answer breaks if the analog chain is noisy and
# that "this is decided by circuit design" -- rule 1 kept in letter, broken in
# spirit, and the direction was backwards besides.
UNCHECKABLE = re.compile(r"公開データでは決まらな|公開情報では(決まらな|確かめられな)|"
                         r"回路設計で決まり|内部(情報|資料|データ)|実機が無い|"
                         r"社内|測ってみない(と|限り)")

# the answer section must be about the subject, not about this repository's
# own paperwork. 2026-09-01: a report opened with "every blank in the
# specification is filled", which is bookkeeping, not an answer.
BOOKKEEPING = re.compile(r"空欄|仕様書?が|検証|事前登録|文書|判定|棚卸|登録簿|Repo")

MAX_CHARS = 1400
MAX_ANSWER_SENTENCES = 3


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_report.py <draft.md>")
        return 2
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    bad: list[str] = []

    for h in REQUIRED:
        if h not in text:
            bad.append(f"見出し「{h}」が無い")
    if bad:
        for b in bad:
            print(f"  NG  {b}")
        print(f"\n必要な型:\n" + "\n".join(f"  {h}" for h in REQUIRED))
        return 1

    work_at = next(i for i, l in enumerate(lines) if l.startswith("## 作業"))
    body = lines[:work_at]

    for i, l in enumerate(body):
        for rx, why in ((SYMBOL, "内部記号。読者には意味がない"),
                        (PLUMBING, "ファイル名・道具の話は「作業」節へ"),
                        (ACTIVITY, "自分の作業の話は「作業」節へ")):
            m = rx.search(l)
            if m:
                bad.append(f"{i+1}行目「{m.group()}」 — {why}")
        if FLOOR.search(l) and not ABSOLUTE.search(l):
            bad.append(f"{i+1}行目 床の倍数に実寸が添えられていない")

    # the answer must be short enough to be an answer
    a0 = next(i for i, l in enumerate(lines) if l.startswith("## 答え"))
    a1 = next(i for i, l in enumerate(lines) if i > a0 and l.startswith("## "))
    ans = " ".join(lines[a0 + 1:a1]).strip()
    n = len([s for s in re.split(r"[。！？]", ans) if s.strip()])
    if n > MAX_ANSWER_SENTENCES:
        bad.append(f"「答え」が{n}文ある。{MAX_ANSWER_SENTENCES}文以内にする")
    if not ans:
        bad.append("「答え」が空である")

    b0 = next((i for i, l in enumerate(lines) if l.startswith("## この答えが崩れる条件")), None)
    if b0 is not None:
        seg = "\n".join(lines[b0 + 1:work_at])
        m = UNCHECKABLE.search(seg)
        if m:
            bad.append(f"崩れる条件に「{m.group()}」 — 公開情報で確かめられない条件は "
                       f"反証条件ではなく内部情報の要求である")

    # 2026-09-01: the user said the reports answer one specific sub-case and
    # never the question that was asked, and to loop until it can be answered.
    # So a report is checked against the registered question, not against
    # whatever happened to be finished today.
    head, closed, openi = question_status()
    if head is None:
        bad.append("QUESTION.md が無い。報告の前に問いを登録する")
    elif openi:
        need = f"残り {len(openi)} 件"
        if need not in text:
            bad.append(f"問いに開いている項目が {len(openi)} 件ある。"
                       f"「{need}」と、何が残っているかを書くか、先に閉じる "
                       f"(python3 scripts/question_status.py)")
    else:
        m = BOOKKEEPING.search(ans)
        if m:
            bad.append(f"「答え」に「{m.group()}」 — これは帳簿の話であって"
                       f"問いへの答えではない。対象について書く")
        key = [w for w in ("報告", "出せ", "可能") if w in ans]
        if not key:
            bad.append("問いは全項目閉じている。「答え」は問い"
                       "(何を報告すべきか・それは可能か)に答えること。"
                       "個別の検証結果は「根拠」節へ")

    if len(text) > MAX_CHARS:
        bad.append(f"全体 {len(text)} 文字。{MAX_CHARS} 文字以内にする")

    for b in bad:
        print(f"  NG  {b}")
    if not bad:
        print(f"  ok  {path.name}  ({len(text)} 文字)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
