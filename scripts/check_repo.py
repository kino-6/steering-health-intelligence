#!/usr/bin/env python3
"""Pre-commit checks. Every one of these exists because it already went wrong.

Run by .git/hooks/pre-commit, so it does not depend on anyone remembering.
Each check names the incident it prevents; see CHECKS.md for the full account.

    python3 scripts/check_repo.py          # all checks
    python3 scripts/check_repo.py --list   # what is checked and why
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS, DATA, SCRIPTS = ROOT / "docs", ROOT / "data", ROOT / "scripts"

# Rule 0 of AGENTS.md: this is personal research. There is no employer, and
# there is no one to show the work to. Violated four times in prose before
# this check existed.
FORBIDDEN = [
    (r"自社|当社|弊社|社内", "AGENTS.md ルール0: 帰属先の会社は存在しない"),
    (r"(誰かに|相手に|人に)(見せ|当て)", "AGENTS.md ルール0: 見せる相手は存在しない"),
    (r"反応を(得|見)", "AGENTS.md ルール0: 外部の反応を次アクションにしない"),
]
ALLOW = "check-repo: allow"          # inline escape hatch, must carry a reason


def md_files():
    return sorted(list(DOCS.glob("*.md")) + list(ROOT.glob("*.md")))


def check_links() -> list[str]:
    """Broken internal links. Hand-checked after every commit until now."""
    bad = []
    for f in md_files():
        for m in re.finditer(r"\]\(([^)]+)\)", f.read_text(encoding="utf-8")):
            t = m.group(1).split("#")[0].strip()
            if not t or t.startswith(("http", "mailto")):
                continue
            if not (f.parent / t).resolve().exists():
                bad.append(f"{f.relative_to(ROOT)} -> {t}")
    return bad


def check_coverage() -> list[str]:
    """No dataset part may sit undecided.

    Incident: 34 documents written on one of three NASA blocks; the KAIST set
    used at 8 files of 32 and 1 machine of 3. Opening the rest overturned the
    conclusions (docs/199, docs/201, docs/203).
    """
    p = DATA / "dataset_coverage.tsv"
    if not p.exists():
        return ["data/dataset_coverage.tsv missing -- run scripts/dataset_coverage.py"]
    out = []
    for line in p.read_text(encoding="utf-8").splitlines()[1:]:
        f = line.split("\t")
        if len(f) >= 5 and f[4].strip() == "UNREVIEWED":
            out.append(f"UNREVIEWED: {f[0]} {f[1]} {f[3][:50]}")
        elif len(f) >= 5 and f[4].startswith("unused") and ":" not in f[4]:
            out.append(f"unused without a reason: {f[0]} {f[1]}")
    return out[:20] + ([f"... and {len(out)-20} more"] if len(out) > 20 else [])


def _staged() -> set[str]:
    r = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                       cwd=ROOT, capture_output=True, text=True)
    return {l.strip() for l in r.stdout.splitlines() if l.strip()}


def check_prospect() -> list[str]:
    """No dataset may be acquired without a written assessment first.

    Incident, three times: NASA MOSFET, the inverter set and NASA IGBT were all
    downloaded, enumerated, analysed, and only then found to be dominated by
    the rig's own operating-point schedule -- which the distribution papers
    describe (docs/199, docs/215, docs/234). Storage went to 62 GB and three
    analyses produced nothing but the discovery of a confound.

    data/dataset_prospect.tsv must carry a row for every acquired dataset,
    filled BEFORE the download, and every field must be answered. The field
    that matters most is operating_point: held or ramped decides whether the
    data can answer a degradation question at all.
    """
    p = DATA / "dataset_prospect.tsv"
    if not p.exists():
        return ["data/dataset_prospect.tsv missing -- assess before acquiring"]
    lines = p.read_text(encoding="utf-8").rstrip("\n").split("\n")
    head = lines[0].split("\t")
    out, acquired = [], set()
    for ln in lines[1:]:
        f = ln.split("\t")
        if len(f) != len(head):
            out.append(f"prospect row has {len(f)} fields, expected {len(head)}: {f[:2]}")
            continue
        if any(not x.strip() for x in f):
            out.append(f"prospect row has an empty field: {f[1]}")
        if f[6].strip() == "acquire":
            acquired.add(f[1].split()[0])
    cov = DATA / "dataset_coverage.tsv"
    if cov.exists():
        have = {l.split("\t")[0] for l in cov.read_text(encoding="utf-8").splitlines()[1:]
                if l.strip()}
        for d in sorted(have):
            if d not in acquired:
                out.append(f"{d} is on disk but has no 'acquire' row in dataset_prospect.tsv")
    return out


def check_derived_files() -> list[str]:
    """Every derived table must have a producing script and a SOURCES entry.

    Applied only to tables this commit adds or changes. Applying it to the
    whole of data/ would fail on tables that predate SOURCES.md, and a check
    that always fails is a check nobody reads.
    """
    src = (ROOT / "SOURCES.md").read_text(encoding="utf-8")
    corpus = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                       for p in SCRIPTS.glob("*.py"))
    staged = _staged()
    if "--all" in sys.argv:
        scope = sorted(DATA.glob("*.tsv"))
    else:
        scope = [DATA / Path(f).name for f in staged
                 if f.startswith("data/") and f.endswith(".tsv")]
    out = []
    for t in scope:
        if t.name == "dataset_coverage.tsv" or not t.exists():
            continue
        if t.name not in src:
            out.append(f"{t.name}: not listed in SOURCES.md")
        # A table declared hand-maintained in SOURCES.md needs no producing
        # script -- the EooC assumption sheet is transcribed from the results
        # documents, row by row, and no single script owns it.
        declared_manual = any(t.name in line and ("手動" in line or "hand-maintained" in line)
                              for line in src.splitlines())
        if t.name not in corpus and not declared_manual:
            out.append(f"{t.name}: no script produces it")
    return out


def check_wording() -> list[str]:
    out = []
    for f in md_files():
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            # A line that records the error is not the error. Corrections must
            # stay readable, so lines marked as a correction are exempt.
            if (ALLOW in line or f.name in ("AGENTS.md", "CHECKS.md")
                    or re.search(r"訂正|誤りである|置換|違反|は存在しない|成立しない", line)):
                continue
            for pat, why in FORBIDDEN:
                if re.search(pat, line):
                    out.append(f"{f.relative_to(ROOT)}:{i} {why} -- {line.strip()[:70]}")
    return out


def _first_commit(path: Path) -> str:
    r = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--", str(path)],
                       cwd=ROOT, capture_output=True, text=True)
    lines = [l for l in r.stdout.split() if l]
    return lines[-1] if lines else ""


def _commit_order(a: str, b: str) -> bool:
    """True when commit a is an ancestor of b (a came first)."""
    if not a or not b or a == b:
        return False
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b],
                          cwd=ROOT, capture_output=True).returncode == 0


def check_preregistration() -> list[str]:
    """A protocol must be committed before the results that cite it.

    The order is the whole value of pre-registration, and git is the only
    record of it that cannot be edited after the fact.
    """
    out = []
    for proto in sorted(DOCS.glob("*_protocol.md")):
        pc = _first_commit(proto)
        for res in DOCS.glob("*.md"):
            if res == proto or "_protocol" in res.name:
                continue
            if res.name == "INDEX.md":
                continue
            body = res.read_text(encoding="utf-8")
            # Only a document that says it EXECUTED this protocol is bound by
            # the ordering. An index or a passing citation is not.
            if not re.search(re.escape(proto.name) + r"[^\n]{0,40}(の事前登録を)?[^\n]{0,20}実行", body):
                continue
            rc = _first_commit(res)
            if pc and rc and not _commit_order(pc, rc):
                out.append(f"{res.name} cites {proto.name} but the protocol was not "
                           f"committed first")
    return out


def check_correction_backlinks() -> list[str]:
    """A retraction must be visible from the document being retracted."""
    out = []
    num = lambda n: int(n[:3]) if n[:3].isdigit() else -1
    for f in DOCS.glob("*.md"):
        if not f.name[:3].isdigit():
            continue
        body = f.read_text(encoding="utf-8")
        for m in re.finditer(r"(訂正|取り下げ|降格)[^\n]{0,80}?\((\d{3}_[^)]+\.md)\)", body):
            target = DOCS / m.group(2)
            if not target.exists():
                continue
            # Only the LATER document retracting an EARLIER one creates an
            # obligation: the earlier one must carry a pointer forward, so a
            # reader who lands on it sees that it was superseded. A note added
            # to the earlier document pointing at the later one is the fix, not
            # a violation, so the reverse direction is skipped.
            if num(f.name) <= num(target.name):
                continue
            if f.name not in target.read_text(encoding="utf-8"):
                out.append(f"{f.name} retracts {target.name}, but {target.name} "
                           f"carries no pointer forward")
    return sorted(set(out))


def check_sheet_currency() -> list[str]:
    """A sheet row must cite whatever corrected the document it rests on.

    Incident: five rows of the EooC assumption sheet still read "filled" long
    after the work behind them was withdrawn. EOOC027 carried a capability
    formula docs/199 had shown does not apply, EOOC028 one docs/203 had shown
    does not replicate. Correction rows were added elsewhere and the originals
    were never touched, so the deliverable claimed more than the documents did.

    The correction map is the same one check_correction_backlinks builds: a
    later document that retracts an earlier one. If a row cites the earlier
    document, it must cite a later one too.
    """
    sheet = DATA / "sotif_eooc_assumption_sheet.tsv"
    if not sheet.exists():
        return []
    num = lambda n: int(n[:3]) if n[:3].isdigit() else -1
    corrected: dict[str, set[str]] = {}
    for f in DOCS.glob("*.md"):
        if not f.name[:3].isdigit():
            continue
        for m in re.finditer(r"(訂正|取り下げ|降格)[^\n]{0,80}?\((\d{3})_[^)]+\.md\)",
                             f.read_text(encoding="utf-8")):
            tgt = m.group(2)
            if num(f.name) > int(tgt):
                corrected.setdefault(tgt, set()).add(f.name[:3])
    out = []
    for line in sheet.read_text(encoding="utf-8").splitlines()[1:]:
        f = line.split("\t")
        if len(f) < 6:
            continue
        rid, src = f[0], f[5]
        cited = set(re.findall(r"docs/(\d{3})", src))
        for c in sorted(cited):
            later = corrected.get(c, set())
            if later and not (later & cited):
                out.append(f"{rid} cites docs/{c}, which docs/"
                           f"{sorted(later)[0]} corrects, without citing the correction")
    return sorted(set(out))


def check_threshold_comparisons() -> list[str]:
    """Warn on bare float comparisons against a pre-registered bar.

    Incident (docs/205): `rho >= 0.8` rejected an exact 4/5 because the float
    was 0.7999999999999999, flipping a verdict. Use lib_discipline.passes.
    """
    out = []
    for p in SCRIPTS.glob("*.py"):
        if p.name in ("lib_discipline.py", "check_repo.py"):
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        if "lib_discipline" in body or "1e-9" in body:
            continue
        for i, line in enumerate(body.splitlines(), 1):
            if re.search(r"\brho\b[^\n]*(>=|<=)\s*0?\.\d", line) or \
               re.search(r"(>=|<=)\s*0?\.\d+\s*(#|$)", line) and "rho" in line:
                out.append(f"{p.name}:{i} bare threshold compare -- use "
                           f"lib_discipline.passes() : {line.strip()[:60]}")
    return out


CHECKS = [
    ("links", check_links, True, "壊れた内部リンク"),
    ("dataset coverage", check_coverage, True, "データセットの未棚卸し部分 (docs/199, 201, 203)"),
    ("acquisition assessment", check_prospect, True, "取得前の見どころ評価 (docs/199, 215, 234)"),
    ("derived files", check_derived_files, True, "出力表に生成スクリプトとSOURCES記載があるか"),
    ("wording", check_wording, True, "AGENTS.md ルール0 の禁止語"),
    ("pre-registration order", check_preregistration, True, "事前登録が結果より先にコミットされたか"),
    ("correction backlinks", check_correction_backlinks, True, "訂正元へのリンクが張られているか"),
    ("sheet currency", check_sheet_currency, True, "EooCシートの行が訂正を反映しているか"),
    ("threshold compares", check_threshold_comparisons, False, "浮動小数点での閾値判定 (docs/205)"),
]


def main() -> int:
    if "--list" in sys.argv:
        for name, _, hard, why in CHECKS:
            print(f"  {'[block]' if hard else '[warn] ':8} {name:24} {why}")
        return 0
    failed = 0
    for name, fn, hard, _ in CHECKS:
        problems = fn()
        if not problems:
            print(f"  ok    {name}")
            continue
        tag = "FAIL " if hard else "warn "
        print(f"  {tag} {name}: {len(problems)}")
        for p in problems[:12]:
            print(f"          {p}")
        if len(problems) > 12:
            print(f"          ... and {len(problems)-12} more")
        if hard:
            failed += 1
    if failed:
        print(f"\n{failed} blocking check(s) failed. "
              f"Commit with --no-verify only with a stated reason.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
