#!/usr/bin/env python3
"""Enumerate every dataset down to its fields, and force a decision on each.

Incident this exists for (docs/199, docs/201, docs/203): thirty-four documents
were written on the NASA MOSFET set using one of its three data blocks, and
the two unopened blocks turned out to hold the fact that the observable was
misidentified and that the temperature trend was the rig's own schedule. The
KAIST set was used at 8 files of 32, and at one machine of three; opening the
rest overturned the winding conclusions.

Every one of those was avoidable by listing what is in the archive before
deciding what to analyse.

This walks each dataset, lists its members, and opens ONE representative of
each member pattern to list the fields inside it. The result is merged into
data/dataset_coverage.tsv, keeping any status already recorded there. Anything
new arrives as UNREVIEWED, and scripts/check_repo.py fails while an UNREVIEWED
row exists -- so a newly downloaded archive cannot be analysed before its
contents have been looked at and each part marked.

Status values:
    used                 something in this repository reads it
    unused:<reason>      deliberately not used, reason required
    UNREVIEWED           not yet decided -- blocks the commit

Run after acquiring any dataset:  python3 scripts/dataset_coverage.py
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_TSV = REPO_ROOT / "data" / "dataset_coverage.tsv"

# The gitignored acquisition directories, from .gitignore.
DATASETS = [".nhtsa_flat", ".nhtsa_cache", ".dvsa_mot", ".jp_mlit",
            ".pmsm_fault", ".nasa_pcoe", ".soredd", ".public_log_cache"]

PATTERN = re.compile(r"\d+")


def pattern_of(name: str) -> str:
    """Collapse a filename to its family, so 32 severities list as one row."""
    return PATTERN.sub("#", Path(name).name)


def fields_of(path: Path) -> list[str]:
    """Internal structure of one file: the level the NASA miss happened at."""
    s = path.suffix.lower()
    try:
        if s == ".mat":
            import scipy.io as sio
            m = sio.loadmat(path, squeeze_me=True, struct_as_record=False)
            out = []
            for k, v in m.items():
                if k.startswith("__"):
                    continue
                names = getattr(v, "_fieldnames", None)
                if names:
                    for f in names:
                        out.append(f"{k}.{f}")
                        import numpy as np
                        arr = np.ravel(getattr(v, f))
                        inner = getattr(arr[0], "_fieldnames", None) if arr.size else None
                        for g in (inner or []):
                            sub = getattr(arr[0], g)
                            deeper = getattr(sub, "_fieldnames", None)
                            for h in (deeper or [g]):
                                out.append(f"{k}.{f}.{g}.{h}" if deeper else f"{k}.{f}.{g}")
                else:
                    out.append(k)
            return out
        if s == ".tdms":
            from nptdms import TdmsFile
            t = TdmsFile.read_metadata(path)
            out = []
            for g in t.groups():
                chans = list(g.channels())
                if not chans:
                    out.append(f"{g.name}/(no channels)")
                for c in chans:
                    out.append(f"{g.name}/{c.name}")
                    for k in sorted(c.properties):
                        out.append(f"{g.name}/{c.name}.{k}")
            return out
        if s in (".csv", ".tsv"):
            with open(path, encoding="latin-1") as fh:
                head = fh.readline().rstrip("\n")
            sep = "\t" if "\t" in head else ","
            cols = head.split(sep)
            return cols if len(cols) < 60 else cols[:60] + [f"...(+{len(cols)-60})"]
        if s == ".txt":
            # NHTSA flat files carry no header row; the columns are defined by a
            # separate layout document. Reading line 1 as field names produced
            # one row per complaint narrative, which is noise, not coverage.
            with open(path, encoding="latin-1") as fh:
                head = fh.readline().rstrip("\n")
            if "\t" in head:
                return [f"(headerless, {head.count(chr(9)) + 1} tab-separated columns; "
                        f"see the accompanying layout file)"]
            return ["(free text)"]
    except Exception as e:  # a file we cannot open is still a fact to record
        return [f"(unreadable: {type(e).__name__})"]
    return []


def walk() -> list[tuple[str, str, str, str]]:
    rows = []
    for ds in DATASETS:
        root = REPO_ROOT / ds
        if not root.exists():
            continue
        seen_pat: dict[str, Path] = {}
        for p in sorted(root.rglob("*")):
            if p.is_dir():
                continue
            rel = str(p.relative_to(root))
            if p.suffix.lower() == ".zip":
                try:
                    z = zipfile.ZipFile(p)
                except Exception:
                    rows.append((ds, rel, "(archive)", "(unreadable)"))
                    continue
                pats: dict[str, str] = {}
                for m in z.namelist():
                    if m.endswith("/"):
                        continue
                    pats.setdefault(pattern_of(m), m)
                for pat, member in sorted(pats.items()):
                    rows.append((ds, f"{rel}!{pat}", "(member)", ""))
                continue
            pat = pattern_of(rel)
            key = f"{ds}|{pat}"
            rows.append((ds, pat, "(file)", ""))
            if key not in seen_pat:
                seen_pat[key] = p
                for f in fields_of(p):
                    rows.append((ds, pat, "field", f))
    # de-duplicate, preserving order
    out, seen = [], set()
    for r in rows:
        if r[:4] in seen:
            continue
        seen.add(r[:4])
        out.append(r)
    return out


def script_corpus() -> str:
    """Everything this repository's code says, for the auto-marking below."""
    parts = []
    for p in sorted((REPO_ROOT / "scripts").glob("*.py")):
        if p.name == "dataset_coverage.py":
            continue
        parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def auto_status(row: tuple[str, str, str, str], corpus: str) -> str | None:
    """Mark a row `used` only when some script names the thing.

    Deliberately conservative: it can say used, never unused. Deciding that
    something is NOT needed is the judgement this file exists to force, and a
    tool must not make it silently -- that is precisely how thirty-four
    documents got written on one third of the NASA data.
    """
    ds, member, kind, field = row
    token = field.split(".")[-1].split("/")[-1] if field else Path(member).name
    token = token.strip()
    if len(token) < 4 or token.startswith("("):
        return None
    return "used" if token in corpus else None


def main() -> None:
    prior = {}
    if OUT_TSV.exists():
        with open(OUT_TSV, encoding="utf-8") as fh:
            next(fh, None)
            for line in fh:
                f = line.rstrip("\n").split("\t")
                if len(f) >= 5:
                    prior[tuple(f[:4])] = f[4]
    rows = walk()
    corpus = script_corpus()
    for r in rows:
        if tuple(r) not in prior:
            a = auto_status(r, corpus)
            if a:
                prior[tuple(r)] = a
    new = [r for r in rows if tuple(r) not in prior]
    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8") as out:
        out.write("dataset\tmember\tkind\tfield\tstatus\n")
        for r in rows:
            out.write("\t".join(r) + "\t" + prior.get(tuple(r), "UNREVIEWED") + "\n")
    unrev = sum(1 for r in rows if prior.get(tuple(r), "UNREVIEWED") == "UNREVIEWED")
    print(f"{len(rows)} entries across {len({r[0] for r in rows})} datasets; "
          f"{len(new)} new; {unrev} UNREVIEWED")
    if unrev:
        print(f"\nEdit {OUT_TSV.relative_to(REPO_ROOT)} and set each UNREVIEWED row to")
        print("  used            -- something here reads it")
        print("  unused:<reason> -- deliberately not used, reason required")
        print("check_repo.py fails while any UNREVIEWED remains.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
