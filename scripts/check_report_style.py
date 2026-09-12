#!/usr/bin/env python3
"""Check the rendered HTML, after it is drawn.

    python3 scripts/check_report_style.py <rendered>.html

2026-09-11. Three things the user had to point at, none of which the JSON gate
can see because they only exist once the page is drawn:

  「字が潰れている」            a label wider than the box it sits in, and two
                              labels running into each other
  「Darkmode などモードに即した  a stylesheet rule beating a fill attribute, so
    色使いに Gate を設けて」     orange boxes got grey text in dark mode
  「文字サイズも Gate を設けて。 11 px grey captions, which read as noise rather
    灰色、小文字はノイズ」        than as content

So this measures. Text width is estimated the same way the renderer estimates
it (CJK full width, mono ASCII 0.6 em), which catches a renderer that forgot
to constrain a label, and the overlap test is geometry, which catches two
labels placed independently that happen to collide.

Colour is not estimated. Every text-on-surface pair the design uses is
declared in report_render.CONTRAST_PAIRS, and each is checked against WCAG in
both themes. A fill token that appears in the output but in no declared pair
is an error, so a new combination cannot slip in unchecked.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report_render as rr

MIN_PX = 11.5          # nothing readable is smaller than this
AA, AA_LARGE = 4.5, 3.0
LARGE_PX = 18.0
# tokens allowed to carry text, checked below against the declared pairs
TEXT_TOKENS = {"ink", "ink2", "ink3", "ok", "warn", "accent", "bg",
               "s1", "s2", "s3", "s4", "s5", "s6"}


def text_width(s: str, px: float) -> float:
    """Same estimate the renderer uses, at the given font size."""
    return sum(1.0 if ord(c) > 0x2E80 else 0.6 for c in s) * px


def _texts(svg: str, default_px: float):
    """Every <text> with its content, position, anchor, size and data-maxw.

    A <g> can set font-size for its children, so the inherited value is
    tracked; without it a 10 px label inside a sized group reads as the
    default and the size check misses it.
    """
    inherit: list[tuple[int, float]] = []
    for gm in re.finditer(r'<g\b[^>]*font-size="([\d.]+)"[^>]*>', svg):
        inherit.append((gm.start(), float(gm.group(1))))
    anchors: list[tuple[int, int, str]] = []       # <g text-anchor=...> spans
    for gm in re.finditer(r'<g\b[^>]*text-anchor="(\w+)"[^>]*>', svg):
        close = svg.find("</g>", gm.end())
        anchors.append((gm.end(), close if close > 0 else len(svg), gm.group(1)))
    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.S):
        at, body = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        if not body.strip():
            continue
        def a(n, d=None):
            g = re.search(rf'{n}="([^"]*)"', at)
            return g.group(1) if g else d
        cls = a("class", "") or ""
        if a("font-size") is not None:
            px = float(a("font-size"))
        elif "lbl" in cls:
            px = 12.5
        else:
            up = [v for pos, v in inherit if pos < m.start()]
            px = up[-1] if up else default_px
        yield {
            "s": body.strip(), "x": float(a("x", 0)), "y": float(a("y", 0)),
            "px": px, "anchor": a("text-anchor") or next(
                (v for s0, s1, v in anchors if s0 <= m.start() < s1), "start"),
            "maxw": float(a("data-maxw")) if a("data-maxw") else None,
            "fill": re.search(r"var\(--(\w+)\)", (a("style", "") or "") + (a("fill", "") or "")),
            "rot": "rotate" in (a("transform", "") or ""),
        }


def box(t) -> tuple[float, float, float, float]:
    w = text_width(t["s"], t["px"])
    x, y, h = t["x"], t["y"], t["px"] * 1.05
    if t.get("rot"):                      # axis titles are turned on their side
        return x - h / 2, y - w / 2, h, w
    if t["anchor"] == "middle":
        x -= w / 2
    elif t["anchor"] == "end":
        x -= w
    return x, y - t["px"] * 0.8, w, h


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_report_style.py <rendered.html>")
        return 2
    html = Path(sys.argv[1]).read_text(encoding="utf-8")
    bad: list[str] = []

    # ---- font sizes anywhere in the stylesheet
    for m in re.finditer(r"font-size:\s*([\d.]+)px", html):
        if float(m.group(1)) < MIN_PX:
            line = html[:m.start()].count("\n") + 1
            bad.append(f"字が小さい CSS {line}行 {m.group(1)}px < {MIN_PX}px")

    # ---- per figure: size, overflow, overlap
    for fm in re.finditer(r'<svg viewBox="0 0 ([\d.]+) ([\d.]+)"(.*?)</svg>', html, re.S):
        svg = fm.group(3)
        lab = re.search(r'aria-label="([^"]{0,34})', svg)
        name = (lab.group(1) if lab else "図")
        ts = list(_texts(svg, 12.0))
        for t in ts:
            if t["px"] < MIN_PX:
                bad.append(f"字が小さい {name}: 「{t['s'][:14]}」 {t['px']}px")
            if t["maxw"] is not None:
                w = text_width(t["s"], t["px"])
                if w > t["maxw"]:
                    bad.append(f"字が潰れている {name}: 「{t['s']}」 は幅 {w:.0f}px、"
                               f"入る幅は {t['maxw']:.0f}px")
        boxes = [(box(t), t) for t in ts]
        for i in range(len(boxes)):
            (ax, ay, aw, ah), ta = boxes[i]
            for j in range(i + 1, len(boxes)):
                (bx, by, bw, bh), tb = boxes[j]
                if (ax < bx + bw - 1 and bx < ax + aw - 1
                        and ay < by + bh - 1 and by < ay + ah - 1):
                    bad.append(f"字が重なっている {name}: 「{ta['s'][:12]}」 と "
                               f"「{tb['s'][:12]}」")

    # ---- a number must not be separated from its unit. 2026-09-13.
    # (the earlier phrase-level wrapping was reverted: it made the right edge
    # ragged; ordinary Japanese wrapping is correct, only this glue is needed)
    body = re.search(r"<main>(.*)</main>", html, re.S)
    text = re.sub(r"<span class=\"(?:nb|num)\">.*?</span>", "", body.group(1) if body else "")
    text = re.sub(r"<(?:svg|style)\b.*?</(?:svg|style)>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    loose = re.findall(r"\d[\d,.]* (?:バイト|ビット|件/時|KB|MB|素子|個|本|台|時間|分|秒|倍|度|回|水準|通り|3σ|σ)", text)
    for m in loose[:5]:
        bad.append(f"数字と単位が離れている: 「{m}」")

    # ---- colour, in both themes, from the declared pairs
    declared = set()
    for nm, fg, bg, px, graphic in rr.CONTRAST_PAIRS:
        declared.add(fg)
        need = AA_LARGE if (graphic or px >= LARGE_PX) else AA
        for theme in ("light", "dark"):
            c = rr.contrast(rr.PALETTE[theme][fg], rr.PALETTE[theme][bg])
            if c < need:
                bad.append(f"コントラスト不足 {theme}: {nm} ({fg} on {bg}) "
                           f"= {c:.2f}、必要 {need}")
        if px < MIN_PX:
            bad.append(f"字が小さい 宣言: {nm} {px}px < {MIN_PX}px")

    used = set()
    for m in re.finditer(r'(?:style="fill:|fill=")var\(--(\w+)\)', html):
        used.add(m.group(1))
    for m in re.finditer(r'<text[^>]*\bclass="[^"]*"[^>]*>', html):
        pass
    for tok in sorted(used & TEXT_TOKENS):
        if tok not in declared:
            bad.append(f"未宣言の文字色 --{tok} が使われている。"
                       f"report_render.CONTRAST_PAIRS に足して検査対象にする")

    for b in bad:
        print(f"  NG  {b}")
    if not bad:
        n = len(re.findall(r"<svg ", html))
        print(f"  ok  {Path(sys.argv[1]).name}  図 {n} 枚、"
              f"色 {len(rr.CONTRAST_PAIRS)} 組を両モードで検査")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
