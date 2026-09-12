#!/usr/bin/env python3
"""Render a report JSON into the HTML an Artifact publish takes.

    python3 scripts/report_render.py reports/<name>.json -o <out>.html

Why a renderer and not hand-written HTML: every chart in the previous reports
had its SVG coordinates typed by hand, so the axis and the data could disagree
without anything noticing. Here the only input is numbers, and the geometry is
computed from them, so a tick always names a value the chart reaches and a bar
is always as long as its number says.

The output is body content only. The Artifact tool wraps it in a skeleton, so
this file emits <title>, <style> and <main> and nothing above them.

Block types are documented in .claude/skills/html-report/SKILL.md.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
from pathlib import Path

# ---------------------------------------------------------------- scales


def nice_max(v: float) -> float:
    """Smallest round number at or above v, so the top tick is reachable."""
    if v <= 0:
        return 1.0
    e = math.floor(math.log10(v))
    base = 10 ** e
    for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if v <= m * base + 1e-12:
            return m * base
    return 10 * base


def nice_range(lo: float, hi: float, zero: bool = False) -> tuple[float, float]:
    """An axis the data fills.

    2026-09-11: the capability chart ran 0 to 1.5 for data that lives between
    0.82 and 1.02, so every line sat in a flat band across the middle and the
    thing the reader came for could not be seen. Bars still start at zero,
    because a bar's length is the number; a line's height is not.
    """
    if zero:
        lo = min(0.0, lo)
    span = hi - lo
    if span <= 0:
        span = abs(hi) or 1.0
    pad = span * 0.12
    lo2, hi2 = lo - pad, hi + pad
    if zero:
        lo2 = min(0.0, lo)
    step = (hi2 - lo2) / 4
    e = math.floor(math.log10(step)) if step > 0 else 0
    base = 10 ** e
    for m in (1, 2, 2.5, 5, 10):
        if step <= m * base + 1e-12:
            step = m * base
            break
    return (math.floor(lo2 / step) * step, math.ceil(hi2 / step) * step)


def ticks(lo: float, hi: float, n: int = 4) -> list[float]:
    if hi <= lo:
        return [lo]
    step = (hi - lo) / n
    e = math.floor(math.log10(step))
    base = 10 ** e
    for m in (1, 2, 2.5, 5, 10):
        if step <= m * base + 1e-12:
            step = m * base
            break
    out, x = [], math.ceil(lo / step) * step
    while x <= hi + 1e-9:
        out.append(round(x, 10))
        x += step
    return out


def fmt(v: float, unit: str = "") -> str:
    if v == int(v):
        s = f"{int(v):,}"
    elif abs(v) < 1:
        s = f"{v:.3f}".rstrip("0").rstrip(".")
    else:
        s = f"{v:,.1f}"
    return s + unit


def esc(s) -> str:
    return html.escape(str(s), quote=False)


SERIES = ["s1", "s2", "s3", "s4", "s5", "s6"]


def _cjk_width(s: str) -> float:
    """Rough label width in px at 11.5px, counting CJK as full width."""
    return sum(12.0 if ord(c) > 0x2E80 else 6.6 for c in s)


# ---------------------------------------------------------------- charts


def chart_barh(c: dict) -> str:
    """Horizontal bars. One row per item; the scale comes from the data."""
    items = c["series"]
    unit = c.get("unit", "")
    vmax = nice_max(max(abs(i["value"]) for i in items))
    lw = min(260.0, max(_cjk_width(str(i["label"])) for i in items) + 14)
    x0 = lw + 14
    pw = 780 - x0 - 78                       # room for the value label
    row, gap = 22, 34
    h = len(items) * gap + 54
    px = lambda v: x0 + (v / vmax) * pw

    g = [f'<svg viewBox="0 0 780 {h + 26}" role="img" aria-label="{esc(c["alt"])}">']
    g.append('<g class="gl">')
    for t in ticks(0, vmax):
        if t > 0:
            g.append(f'<line x1="{px(t):.1f}" y1="16" x2="{px(t):.1f}" y2="{h - 34}"/>')
    g.append("</g>")
    g.append(f'<line class="ax" x1="{x0}" y1="{h - 34}" x2="{px(vmax):.1f}" y2="{h - 34}"/>')

    for k, it in enumerate(items):
        y = 22 + k * gap
        w = max(3.0, (abs(it["value"]) / vmax) * pw)
        col = f'var(--{it.get("color", "s1")})'
        g.append(f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="{row}" rx="4" '
                 f'fill="{col}"><title>{esc(it["label"])} {fmt(it["value"], unit)}</title></rect>')
        g.append(f'<text class="lbl" x="{x0 - 10}" y="{y + 16}" text-anchor="end">'
                 f'{esc(it["label"])}</text>')
        g.append(f'<text class="lbl" x="{x0 + w + 9:.1f}" y="{y + 16}" fill="var(--ink)">'
                 f'{fmt(it["value"], unit)}</text>')

    g.append('<g text-anchor="middle" fill="var(--ink3)">')
    for t in ticks(0, vmax):
        g.append(f'<text x="{px(t):.1f}" y="{h - 16}">{fmt(t, unit if t == 0 else "")}</text>')
    if c.get("axis"):
        g.append(f'<text x="{(x0 + px(vmax)) / 2:.1f}" y="{h + 6}">{esc(c["axis"])}</text>')
    g.append("</g></svg>")
    return "\n".join(g)


def chart_barv(c: dict) -> str:
    """Vertical bars with an optional annotation printed on each bar."""
    items = c["series"]
    unit = c.get("unit", "")
    vmax = nice_max(max(i["value"] for i in items))
    x0, y0, y1 = 62, 30, 200
    pw = 700 - x0
    step = pw / len(items)
    bw = min(74.0, step * 0.62)
    py = lambda v: y1 - (v / vmax) * (y1 - y0)

    g = ['<svg viewBox="0 0 780 268" role="img" aria-label="%s">' % esc(c["alt"])]
    g.append('<g class="gl">')
    for t in ticks(0, vmax):
        if t > 0:
            g.append(f'<line x1="{x0}" y1="{py(t):.1f}" x2="{x0 + pw}" y2="{py(t):.1f}"/>')
    g.append('</g><g text-anchor="end">')
    for t in ticks(0, vmax):
        g.append(f'<text x="{x0 - 8}" y="{py(t) + 4:.1f}">{fmt(t, "")}</text>')
    g.append("</g>")
    g.append(f'<line class="ax" x1="{x0}" y1="{y1}" x2="{x0 + pw}" y2="{y1}"/>')

    for k, it in enumerate(items):
        cx = x0 + step * (k + 0.5)
        top = py(it["value"])
        col = f'var(--{it.get("color", "s1")})'
        g.append(f'<rect x="{cx - bw / 2:.1f}" y="{top:.1f}" width="{bw:.1f}" '
                 f'height="{max(4.0, y1 - top):.1f}" rx="4" fill="{col}">'
                 f'<title>{esc(it["label"])} {fmt(it["value"], unit)}'
                 f'{" / " + esc(it["note"]) if it.get("note") else ""}</title></rect>')
        g.append(f'<text class="lbl" x="{cx:.1f}" y="{top - 8:.1f}" text-anchor="middle" '
                 f'fill="var(--ink)">{fmt(it["value"], unit)}</text>')
        g.append(f'<text x="{cx:.1f}" y="{y1 + 20}" text-anchor="middle" '
                 f'fill="var(--ink3)">{esc(it["label"])}</text>')
        if it.get("note"):
            iny = top + 20 if (y1 - top) > 34 else top - 24
            fill = "var(--bg)" if (y1 - top) > 34 else "var(--ink2)"
            g.append(f'<text x="{cx:.1f}" y="{iny:.1f}" text-anchor="middle" '
                     f'font-size="12" fill="{fill}">{esc(it["note"])}</text>')

    if c.get("ylabel"):
        g.append(f'<text x="18" y="115" text-anchor="middle" transform="rotate(-90 18 115)" '
                 f'fill="var(--ink3)">{esc(c["ylabel"])}</text>')
    if c.get("axis"):
        g.append(f'<text x="{x0 + pw / 2:.1f}" y="{y1 + 44}" text-anchor="middle" '
                 f'fill="var(--ink3)">{esc(c["axis"])}</text>')
    g.append("</svg>")
    return "\n".join(g)


def chart_line(c: dict) -> str:
    """Multi-series lines. x is numeric when x.values is given, else by index."""
    xs = c["x"]
    ser = c["series"]
    unit = c.get("unit", "")
    numeric = "values" in xs
    xv = xs["values"] if numeric else list(range(len(xs["labels"])))
    xlo, xhi = min(xv), max(xv)
    allv = [v for s in ser for v in s["values"] if v is not None]
    allv += [hl["y"] for hl in c.get("hlines", [])]
    allv += [e["y"] for e in c.get("events", [])]
    ylo, yhi = nice_range(min(allv), max(allv), c.get("zero", False))
    fill = (max(allv) - min(allv)) / (yhi - ylo) if yhi > ylo else 0
    if fill < 0.35 and not c.get("zero"):
        raise SystemExit(f"軸が広すぎる: データは軸の {fill:.0%} しか使っていない "
                         f"({c.get('alt', '')[:30]})")
    x0, x1, y0, y1 = 70, 668, 34, 230
    fx = lambda v: x0 + ((v - xlo) / (xhi - xlo or 1)) * (x1 - x0)
    fy = lambda v: y1 - ((v - ylo) / (yhi - ylo or 1)) * (y1 - y0)

    g = ['<svg viewBox="0 0 780 300" role="img" aria-label="%s">' % esc(c["alt"])]
    g.append('<g class="gl">')
    for t in ticks(ylo, yhi):
        g.append(f'<line x1="{x0}" y1="{fy(t):.1f}" x2="{x1}" y2="{fy(t):.1f}"/>')
    g.append('</g><g text-anchor="end">')
    for t in ticks(ylo, yhi):
        g.append(f'<text x="{x0 - 8}" y="{fy(t) + 4:.1f}">{fmt(t, "")}</text>')
    g.append("</g>")
    for hl in c.get("hlines", []):
        col = f'var(--{hl.get("tone", "warn")})'
        g.append(f'<line x1="{x0}" y1="{fy(hl["y"]):.1f}" x2="{x1}" y2="{fy(hl["y"]):.1f}" '
                 f'stroke="{col}" stroke-width="1.4" stroke-dasharray="5 4"/>')
        g.append(f'<text x="{x0 + 6}" y="{fy(hl["y"]) - 6:.1f}" font-size="12" '
                 f'fill="{col}">{esc(hl["label"])}</text>')
    for mk in c.get("marks", []):
        mx = fx(mk["x"])
        g.append(f'<line x1="{mx:.1f}" y1="{y0}" x2="{mx:.1f}" y2="{y1}" '
                 f'stroke="var(--accent)" stroke-width="1.4" stroke-dasharray="4 3"/>')
        # keep the name off the axis: to the left of the line when there is
        # room, otherwise to its right
        w = _cjk_width(str(mk["label"])) * (12 / 11.5)
        if mx - 8 - w > x0 + 6:
            g.append(f'<text x="{mx - 8:.1f}" y="{y0 + 13}" font-size="12" '
                     f'style="fill:var(--accent)" text-anchor="end">{esc(mk["label"])}</text>')
        else:
            g.append(f'<text x="{mx + 8:.1f}" y="{y0 + 13}" font-size="12" '
                     f'style="fill:var(--accent)" text-anchor="start">{esc(mk["label"])}</text>')
    g.append(f'<line class="ax" x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}"/>')

    ends: list = []
    for k, s in enumerate(ser):
        col = f'var(--{SERIES[k % len(SERIES)]})'
        pts = [(fx(x), fy(v)) for x, v in zip(xv, s["values"]) if v is not None]
        d = " ".join(("M" if i == 0 else "L") + f"{a:.1f},{b:.1f}" for i, (a, b) in enumerate(pts))
        g.append(f'<path class="ln" stroke="{col}" d="{d}"/>')
        for (a, b), x, v in zip(pts, xv, s["values"]):
            lab = fmt(x, xs.get("unit", "")) if numeric else esc(xs["labels"][xv.index(x)])
            g.append(f'<circle class="pt" cx="{a:.1f}" cy="{b:.1f}" r="4" fill="{col}">'
                     f'<title>{esc(s["name"])} {lab} {fmt(v, unit)}</title></circle>')
        if s.get("endlabel"):
            ends.append((pts[-1], col, s["endlabel"]))

    # spread the end labels so they cannot land on one another
    ends.sort(key=lambda e: e[0][1])
    placed: list[float] = []
    for (px_, py_), col, lab in ends:
        y = py_ + 4
        while any(abs(y - q) < 15 for q in placed):
            y += 15
        placed.append(y)
    # spreading walks downward; if the cluster reaches the axis it lands on
    # the tick labels, so lift the whole cluster back above the axis
    if placed and max(placed) > y1 - 2:
        lift = max(placed) - (y1 - 2)
        placed = [q - lift for q in placed]
    for ((px_, py_), col, lab), y in zip(ends, placed):
        g.append(f'<text class="lbl" x="{px_ + 9:.1f}" y="{y:.1f}" style="fill:{col}">'
                 f'{esc(lab)}</text>')

    for ev in c.get("events", []):
        ex, ey = fx(ev["x"]), fy(ev["y"])
        g.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="7.5" fill="none" '
                 f'stroke="var(--warn)" stroke-width="2.2"><title>{esc(ev["label"])}'
                 f'</title></circle>')

    g.append('<g text-anchor="middle" fill="var(--ink3)">')
    labs = xs["labels"] if "labels" in xs else [fmt(v, xs.get("unit", "")) for v in xv]
    for x, lab in zip(xv, labs):
        g.append(f'<text x="{fx(x):.1f}" y="{y1 + 20}">{esc(lab)}</text>')
    g.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{y1 + 42}">{esc(xs["title"])}</text></g>')
    if c.get("ylabel"):
        g.append(f'<text x="20" y="132" text-anchor="middle" transform="rotate(-90 20 132)" '
                 f'fill="var(--ink3)">{esc(c["ylabel"])}</text>')
    g.append("</svg>")
    return "\n".join(g)


def chart_dots(c: dict) -> str:
    """One row per group, every raw point plotted. No averaging."""
    rows = c["rows"]
    unit = c.get("unit", "")
    allv = [v for r in rows for v in r["values"]]
    m = nice_max(max(abs(min(allv)), abs(max(allv))))
    lw = min(190.0, max(_cjk_width(str(r["label"])) for r in rows) + 14)
    x0, x1 = lw + 22, 720
    step = 26
    h = len(rows) * step + 66
    fx = lambda v: x0 + ((v + m) / (2 * m)) * (x1 - x0)

    g = [f'<svg viewBox="0 0 780 {h}" role="img" aria-label="{esc(c["alt"])}">']
    g.append('<g class="gl">')
    for t in ticks(-m, m, 6):
        if abs(t) > 1e-12:
            g.append(f'<line x1="{fx(t):.1f}" y1="18" x2="{fx(t):.1f}" y2="{h - 48}"/>')
    g.append("</g>")
    g.append(f'<line class="ax" x1="{fx(0):.1f}" y1="12" x2="{fx(0):.1f}" y2="{h - 42}" '
             f'stroke-dasharray="3 3"/>')
    for k, r in enumerate(rows):
        y = 30 + k * step
        col = f'var(--{SERIES[k % len(SERIES)]})'
        g.append(f'<text class="lbl" x="{x0 - 16}" y="{y + 4}" text-anchor="end" '
                 f'fill="{col}">{esc(r["label"])}</text>')
        g.append(f'<g fill="{col}" opacity="0.85">')
        for j, v in enumerate(r["values"]):
            tag = r["point_labels"][j] if r.get("point_labels") else str(j + 1)
            g.append(f'<circle class="pt" cx="{fx(v):.1f}" cy="{y}" r="4">'
                     f'<title>{esc(tag)} {fmt(v, unit)}</title></circle>')
        g.append("</g>")
    g.append('<g text-anchor="middle" fill="var(--ink3)">')
    for t in ticks(-m, m, 6):
        g.append(f'<text x="{fx(t):.1f}" y="{h - 26}">{fmt(t, "")}</text>')
    g.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{h - 6}">{esc(c["axis"])}</text></g>')
    g.append("</svg>")
    return "\n".join(g)


CHARTS = {"barh": chart_barh, "barv": chart_barv, "line": chart_line, "dots": chart_dots}



# ---------------------------------------------------------------- line breaks

try:
    import budoux as _budoux
    _JP = _budoux.load_default_japanese_parser()
except ImportError:                      # pragma: no cover
    _JP = None


def _phrase_wbr(text: str) -> str:
    """<wbr> between phrases. With word-break:keep-all these are the only
    places a line may break; text-align:justify then keeps the right edge
    flush, which is what the phrase-only version lacked the first time."""
    if _JP is None or not re.search(r"[぀-ヿ一-鿿]", text):
        return text
    return "<wbr>".join(_JP.parse(text))


_UNIT = (r"(?:× 3σ|3σ|σ|%|％|KB|MB|B|Hz|kHz|V|A|Ω|°C|h|bit|trip|バイト|ビット|件|時|床|素子|個|本|台|"
         r"日|年|時間|分|秒|倍|度|回|行|点|水準|通り|条件|チャネル|フィールド|段|節|run)")
_NUM_UNIT = re.compile(r"(\d[\d,.]*)( ?)(" + _UNIT + r"(?:/(?:時|年|件|時間))?)")


def jp_wrap(fragment: str) -> str:
    """Glue a number to its unit. Nothing else.

    2026-09-13, first version: broke lines only at phrase boundaries with
    <wbr> and word-break:keep-all. That made the right edge ragged and the
    page worse -- Japanese wraps at any character by convention, and the only
    real defect on the screenshot was "2 / バイト", the space I had put between
    a digit and its unit. So this now does only that.
    """
    out = []
    for part in re.split(r"(<[^>]+>)", fragment):
        if part.startswith("<") or not part.strip():
            out.append(part)
            continue
        part = _NUM_UNIT.sub(
            lambda m: f'<span class="nb">{m.group(1)}{m.group(2)}{m.group(3)}</span>', part)
        # segment around the glue spans so a number never splits from its unit
        out.append("".join(x if x.startswith("<") else _phrase_wbr(x)
                           for x in re.split(r"(<span class=\"nb\">.*?</span>)", part)))
    return "".join(out)


# ---------------------------------------------------------------- palette

PALETTE = {
    "light": {
        "bg": "#f7f8f6", "panel": "#edefea", "panel2": "#dfe3dc",
        "ink": "#12161a", "ink2": "#3f4741", "ink3": "#5d665e",
        "line": "#c8cec5", "rule": "#aab1a7",
        "accent": "#8a4f00", "warn": "#8c2c21", "ok": "#25583a",
        "s1": "#1f63b8", "s2": "#c24a15", "s3": "#0d7d55",
        "s4": "#8a6000", "s5": "#a03668", "s6": "#3c6421",
        "grid": "#c8cec5", "axis": "#5d665e",
    },
    "dark": {
        "bg": "#141715", "panel": "#1e221f", "panel2": "#2a2f2b",
        "ink": "#eef1ec", "ink2": "#c2cbc3", "ink3": "#9aa49b",
        "line": "#3a413b", "rule": "#4c544d",
        "accent": "#f0b657", "warn": "#f09080", "ok": "#8fd0a6",
        "s1": "#7ab4f0", "s2": "#f2946a", "s3": "#5fd6a8",
        "s4": "#e8bd5c", "s5": "#eb9cbf", "s6": "#a8ce7f",
        "grid": "#333a34", "axis": "#9aa49b",
    },
}

# Every text-on-surface pair the renderer can produce, with the size it is
# drawn at. 2026-09-11: the user asked for a gate on theme colours and on text
# size, after the key fields in a byte map came out unreadable -- a stylesheet
# rule was beating the fill attribute, so orange boxes got grey text.
# check_report_style.py reads this and refuses anything under the line.
CONTRAST_PAIRS = [
    # name              fg      bg        px    graphic?
    ("本文",             "ink",  "bg",      15.5, False),
    ("小さい本文",        "ink2", "bg",      13.5, False),
    ("図の説明",          "ink2", "bg",      13.5, False),
    ("表のセル",          "ink",  "bg",      13.5, False),
    ("表のセル(縞)",      "ink",  "panel",   13.5, False),
    ("表の見出し",        "ink2", "bg",      12.0, False),
    ("小見出し",          "ink2", "bg",      14.0, False),
    ("目盛りの数字",      "ink2", "bg",      12.0, False),
    ("軸の名前",          "ink3", "bg",      12.0, False),
    ("折り畳みの見出し",   "ink2", "panel",   12.5, False),
    ("数字帯の見出し",     "ink2", "panel",   12.0, False),
    ("数字帯の値",        "ink",  "panel",   15.0, False),
    ("数字帯の値(良)",     "ok",   "panel",   15.0, False),
    ("数字帯の値(否)",     "warn", "panel",   15.0, False),
    ("表の強調(良)",       "ok",   "bg",      13.5, False),
    ("表の強調(否)",       "warn", "bg",      13.5, False),
    ("バイト図の箱",      "ink2", "panel2",  12.0, False),
    ("バイト図の係数",     "bg",   "accent",  12.0, False),
    ("しきい線の名前",     "warn", "bg",      12.0, False),
    ("実測位置の名前",     "accent", "bg",    12.0, False),
    ("式の強調",          "accent", "panel", 15.0, False),
    ("凡例",             "ink2", "bg",      12.0, False),
    ("出所タグ",          "ink2", "bg",      11.5, False),
    ("脚注",             "ink3", "bg",      12.0, False),
    ("系列の名前 1",      "s1",   "bg",      12.5, False),
    ("系列の名前 2",      "s2",   "bg",      12.5, False),
    ("系列の名前 3",      "s3",   "bg",      12.5, False),
    ("系列の名前 4",      "s4",   "bg",      12.5, False),
    ("系列の名前 5",      "s5",   "bg",      12.5, False),
    ("系列の名前 6",      "s6",   "bg",      12.5, False),
]


def _lum(hex_: str) -> float:
    c = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(fg: str, bg: str) -> float:
    a, b = _lum(fg), _lum(bg)
    lo, hi = min(a, b), max(a, b)
    return (hi + 0.05) / (lo + 0.05)


def _tokens(theme: str) -> str:
    return "; ".join(f"--{k}:{v}" for k, v in PALETTE[theme].items())


# ---------------------------------------------------------------- byte layout

SIZES = {"f64": 8, "f32": 4, "u32": 4, "i32": 4, "u16": 2, "i16": 2,
         "u8": 1, "i8": 1}


def field_bits(f: dict) -> int:
    if "bits" in f:
        return int(f["bits"])
    return SIZES[f["t"]] * 8


def _rows_for(fs, bits, nrows):
    """Pack fields into nrows rows, breaking only at field boundaries."""
    tot = sum(bits)
    target = tot / nrows
    rows, cur, cur_bits = [], [], 0
    for f, nb in zip(fs, bits):
        if cur and cur_bits + nb > target + 1e-9 and len(rows) < nrows - 1:
            rows.append((cur, cur_bits))
            cur, cur_bits = [], 0
        cur.append((f, nb))
        cur_bits += nb
    if cur:
        rows.append((cur, cur_bits))
    return rows


def render_bytes(b: dict) -> str:
    """A memory map drawn to scale, plus the table that names every field.

    2026-09-10, the user asked why the data structures were acceptable in this
    format. They were not: every field got an equal-width box, so a 4-byte
    float and a 1-byte flag looked the same.

    2026-09-11, the labels were still unreadable -- names that did not fit fell
    back to a byte offset, so one row read "slope / 4 / floor / op_lo", and two
    neighbouring names ran together. The layout wraps onto as many rows as it
    takes for every real name to fit, and refuses to draw if none does.
    """
    fs = b["fields"]
    bits = [field_bits(f) for f in fs]
    tot = sum(bits)
    in_bits = any("bits" in f for f in fs)
    unit = "ビット" if in_bits else "バイト"
    per_unit = 1 if in_bits else 8
    if b["total"] * 8 != tot:
        raise SystemExit(f"バイト割り当てが合わない: 宣言 {b['total']} バイト / "
                         f"合計 {tot / 8:g} バイト")

    x0, x1, hbox, gap = 10, 770, 44, 62
    FS = 12.0
    chosen = None
    for nrows in range(1, 7):
        rows = _rows_for(fs, bits, nrows)
        widest = max(rb for _, rb in rows)
        per = (x1 - x0) / widest
        if all(_cjk_width(str(f["name"])) * (FS / 11.5) <= nb * per - 12
               for r, _ in rows for f, nb in r):
            chosen = (rows, per)
            break
    if chosen is None:
        raise SystemExit(f"バイト図: 6 行に分けても名前が箱に入らない ({b['total']} B)")
    rows, per = chosen

    top, h = 30, len(rows) * gap + 42
    g = [f'<svg viewBox="0 0 780 {top + h}" role="img" aria-label="{esc(b["alt"])}">']
    g.append(f'<text x="{x0}" y="20" font-size="12" fill="var(--ink3)">0</text>')
    g.append(f'<text x="{x1}" y="20" font-size="12" fill="var(--ink3)" '
             f'text-anchor="end">{b["total"]} バイト</text>')
    off = 0
    for ri, (row, rb) in enumerate(rows):
        y = top + ri * gap
        rx = x0
        for f, nb in row:
            w = nb * per
            key = f.get("key")
            fill = "var(--accent)" if key else "var(--panel2)"
            ink = "var(--bg)" if key else "var(--ink2)"
            g.append(f'<rect x="{rx:.1f}" y="{y}" width="{w - 2:.1f}" height="{hbox}" '
                     f'fill="{fill}" stroke="var(--line)" stroke-width="1">'
                     f'<title>{esc(f["name"])} '
                     f'{esc(f.get("t", str(f.get("bits")) + " bit"))} @ {off // per_unit}'
                     f'</title></rect>')
            g.append(f'<text x="{rx + (w - 2) / 2:.1f}" y="{y + hbox / 2 + 4.5:.1f}" '
                     f'text-anchor="middle" font-size="{FS}" style="fill:{ink}" '
                     f'data-maxw="{w - 12:.1f}">{esc(f["name"])}</text>')
            rx += w
            off += nb
        # ruler for this row
        ry = y + hbox + 6
        g.append(f'<line class="ax" x1="{x0}" y1="{ry}" x2="{x0 + rb * per:.1f}" y2="{ry}"/>')
        start_u = sum(nb for r2, _ in rows[:ri] for _, nb in r2) // per_unit
        step = 4 if not in_bits else 4
        u = 0
        while u <= rb // per_unit:
            tx = x0 + u * per_unit * per
            g.append(f'<line class="ax" x1="{tx:.1f}" y1="{ry}" x2="{tx:.1f}" y2="{ry + 5}"/>')
            g.append(f'<text x="{tx:.1f}" y="{ry + 19}" text-anchor="middle" font-size="12">'
                     f'{start_u + u}</text>')
            u += step
    g.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{top + h - 4}" text-anchor="middle" '
             f'font-size="12" fill="var(--ink3)">{esc(unit)}の位置</text>')
    g.append("</svg>")

    fig = (f'<figure class="viz">' + "\n".join(g)
           + f'<figcaption><b class="src">実測</b>{b["caption"]}</figcaption></figure>')

    # the table is generated from the same fields, so the two cannot disagree
    trows, off = [], 0
    for f in fs:
        nb = field_bits(f)
        pos = (f"{off // 8}" if not in_bits else f"{off // 8} バイト bit{off % 8}")
        size = (f'{nb // 8} B' if not in_bits else f"{nb} bit")
        trows.append([{"v": f["name"], "tone": "ok" if f.get("key") else ""},
                      f.get("t", "bit"), pos, size, f.get("why", "")])
        off += nb
    trows.append({"cells": ["合計", "", "", f'{b["total"]} B', b.get("sum_why", "")],
                  "sum": True})
    tbl = render_table({"cols": ["フィールド", "型", {"t": "位置", "n": True},
                                 {"t": "大きさ", "n": True}, "何のためにあるか"],
                        "rows": trows, "stripe": True,
                        "fold": b.get("fold", f'割り当て {len(fs)} フィールドの内訳')})
    return fig + tbl


# ---------------------------------------------------------------- sequence

def render_sequence(b: dict) -> str:
    """Who does what, in what order -- the dynamic structure.

    2026-09-11: "経路はあるがシーケンスはない。動的構造を記述してはどうか"
    The flow diagram says which boxes are connected. It does not say what
    happens once, what happens every 100 ms, and what happens only on an
    event, and that is the part a reader needs to size the thing.

    The message text runs the full width above its arrow rather than being
    squeezed between two lifelines, because a real step description does not
    fit in one lane.
    """
    acts = b["actors"]
    steps = b["steps"]
    ids = {a["id"]: i for i, a in enumerate(acts)}
    n = len(acts)
    band, right = 132, 776
    span = (right - (band + 8)) / n
    ax = [band + 8 + span * (i + 0.5) for i in range(n)]
    top, dy = 86, 52
    h = top + len(steps) * dy + 16
    tx0 = band + 12

    g = [f'<svg viewBox="0 0 780 {h}" role="img" aria-label="{esc(b["alt"])}">',
         '<defs><marker id="sq" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" '
         'markerHeight="8" orient="auto-start-reverse">'
         '<path d="M0,0 L10,5 L0,10 z" fill="var(--ink2)"/></marker></defs>']
    for ph in b.get("phases", []):
        y = top + ph["from"] * dy - 26
        y2 = top + ph["to"] * dy + 22
        g.append(f'<rect x="4" y="{y:.0f}" width="{band - 8}" height="{y2 - y:.0f}" rx="3" '
                 f'fill="var(--panel)" stroke="var(--line)"/>')
        g.append(f'<text x="{band / 2:.0f}" y="{(y + y2) / 2 + 4:.0f}" text-anchor="middle" '
                 f'class="lbl" data-maxw="{band - 20}">{esc(ph["label"])}</text>')
    for i, a in enumerate(acts):
        g.append(f'<line x1="{ax[i]:.0f}" y1="62" x2="{ax[i]:.0f}" y2="{h - 8}" '
                 f'stroke="var(--rule)" stroke-width="1" stroke-dasharray="3 4"/>')
        g.append(f'<rect x="{ax[i] - span / 2 + 5:.0f}" y="34" width="{span - 10:.0f}" '
                 f'height="26" rx="3" fill="var(--panel2)" stroke="var(--line)"/>')
        g.append(f'<text x="{ax[i]:.0f}" y="51" text-anchor="middle" class="lbl" '
                 f'data-maxw="{span - 18:.0f}">{esc(a["name"])}</text>')
    for k, s in enumerate(steps):
        y = top + k * dy
        g.append(f'<text x="{tx0}" y="{y - 13:.0f}" font-size="12.5" '
                 f'style="fill:var(--ink)" data-maxw="{right - tx0 - 4}">'
                 f'{k + 1}. {esc(s["text"])}</text>')
        if s.get("when"):
            g.append(f'<text x="{right}" y="{y + 20:.0f}" text-anchor="end" font-size="12" '
                     f'style="fill:var(--accent)" data-maxw="{right - tx0 - 4}">'
                     f'{esc(s["when"])}</text>')
        if s.get("self"):
            x = ax[ids[s["self"]]]
            g.append(f'<path class="ln" stroke="var(--ink2)" marker-end="url(#sq)" '
                     f'd="M{x:.0f},{y - 6:.0f} l30,0 l0,12 l-30,0"/>')
        else:
            i, j = ids[s["from"]], ids[s["to"]]
            g.append(f'<line x1="{ax[i]:.0f}" y1="{y:.0f}" x2="{ax[j]:.0f}" y2="{y:.0f}" '
                     f'stroke="var(--ink2)" stroke-width="1.8" marker-end="url(#sq)"/>')
            g.append(f'<circle cx="{ax[i]:.0f}" cy="{y:.0f}" r="3.5" fill="var(--ink2)"/>')
    g.append("</svg>")
    src = {"measured": "実測", "simulated": "仮想", "assumed": "置いた値",
           "derived": "計算"}[b["source"]]
    return (f'<figure class="viz">' + "\n".join(g)
            + f'<figcaption><b class="src">{src}</b>{b["caption"]}</figcaption></figure>')


# ---------------------------------------------------------------- blocks


def cell(c) -> tuple[str, str]:
    if isinstance(c, dict):
        return str(c.get("v", "")), c.get("tone", "")
    return str(c), ""


def render_table(b: dict) -> str:
    cols = b["cols"]
    num = [i for i, c in enumerate(cols) if isinstance(c, dict) and c.get("n")]
    head = "".join(
        f'<th class="n">{esc(c["t"])}</th>' if isinstance(c, dict) and c.get("n")
        else f'<th>{esc(c["t"] if isinstance(c, dict) else c)}</th>' for c in cols)
    body = []
    for r, row in enumerate(b["rows"]):
        cls = ""
        cells = row["cells"] if isinstance(row, dict) else row
        if isinstance(row, dict) and row.get("sum"):
            cls = ' class="sum"'
        elif b.get("stripe") and r % 2:
            cls = ' class="alt"'
        tds = []
        for i, c in enumerate(cells):
            v, tone = cell(c)
            k = ("n " if i in num else "") + tone
            k = ("m " if i == 0 and not num.count(0) else "") + k
            # cells are authored HTML fragments like every prose block, and a
            # text cell gets its phrase breaks the same way. 2026-09-13: they
            # were escaped here, so <strong> and <wbr> showed up as text.
            content = v          # touches only number+unit pairs
            tds.append(f'<td class="{k.strip()}">{content}</td>' if k.strip()
                       else f"<td>{content}</td>")
        body.append(f"<tr{cls}>" + "".join(tds) + "</tr>")
    t = (f'<div class="wrap"><table><tr>{head}</tr>' + "".join(body) + "</table></div>")
    if b.get("note"):
        t += f'<p class="small">{b["note"]}</p>'
    if b.get("fold"):
        return f'<details><summary>{esc(b["fold"])}</summary>{t}</details>'
    return t


def render_chart(b: dict) -> str:
    svg = CHARTS[b["kind"]](b)
    leg = ""
    if b.get("legend"):
        leg = '<div class="legend">' + "".join(
            f'<span><i style="background:var(--{l.get("color", SERIES[i])})"></i>'
            f'{esc(l["name"] if isinstance(l, dict) else l)}</span>'
            for i, l in enumerate(b["legend"])) + "</div>"
    src = {"measured": "実測", "simulated": "仮想", "assumed": "置いた値",
           "derived": "計算"}[b["source"]]
    return (f'<figure class="viz">{svg}{leg}'
            f'<figcaption><b class="src">{src}</b>{b["caption"]}</figcaption></figure>')


def render_block(b: dict) -> str:
    t = b["type"]
    if t == "p":
        return f"<p>{b['text']}</p>"
    if t == "lead":
        return f'<p class="lead">{b["text"]}</p>'
    if t == "small":
        return f'<p class="small">{b["text"]}</p>'
    if t == "note":
        return f'<div class="note">{b["text"]}</div>'
    if t == "eq":
        return f'<div class="eq">{b["text"]}</div>'
    if t == "h3":
        return f"<h3>{esc(b['text'])}</h3>"
    if t == "table":
        return render_table(b)
    if t == "chart":
        return render_chart(b)
    if t == "bytes":
        return render_bytes(b)
    if t == "sequence":
        return render_sequence(b)
    if t == "svg":
        return (f'<figure><svg viewBox="{b["viewBox"]}" role="img" '
                f'aria-label="{esc(b["alt"])}">{b["body"]}</svg>'
                f'<figcaption>{b["caption"]}</figcaption></figure>')
    if t == "kpi":
        return '<div class="top">' + "".join(
            f'<div><div class="k">{esc(i["k"])}</div>'
            f'<div class="v {i.get("tone", "")}">{esc(i["v"])}</div></div>'
            for i in b["items"]) + "</div>"
    if t == "fold":
        return ('<details><summary>' + esc(b["summary"]) + "</summary>"
                + "".join(render_block(x) for x in b["blocks"]) + "</details>")
    raise SystemExit(f"unknown block type: {t}")


# ---------------------------------------------------------------- page

CSS = """
:root{__LIGHT__}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){__DARK__}}
:root[data-theme="dark"]{__DARK__}
*{box-sizing:border-box}
body{background:var(--bg); color:var(--ink); margin:0;
  font-family:"Zen Kaku Gothic New",system-ui,"Hiragino Sans","Noto Sans JP",sans-serif;
  font-size:15.5px; line-height:1.8}
main{max-width:1280px; margin:0 auto; padding:44px 30px 88px}
.eyebrow{font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink2); margin:0 0 12px}
h1{font-size:clamp(24px,3.4vw,34px); font-weight:700; line-height:1.3; margin:0 0 6px;
  text-wrap:balance}
.lede{color:var(--ink2); font-size:16px; margin:0 0 28px}
h2{font-size:19px; font-weight:700; margin:52px 0 2px; padding-bottom:7px;
  border-bottom:1px solid var(--rule); overflow:hidden}
h2 .en{font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.08em;
  color:var(--ink3); font-weight:400; float:right; padding-top:5px}
h3{font-size:15.5px; font-weight:700; margin:28px 0 6px; color:var(--ink2)}
p{margin:12px 0}
p, li, figcaption, .small, .lede, .note{
  line-break:strict; word-break:keep-all; overflow-wrap:anywhere;
  text-align:justify; text-justify:inter-character}
td, th, summary{line-break:strict; overflow-wrap:anywhere}
.nb{white-space:nowrap}
p.summary{font-size:17px; line-height:1.9; margin:6px 0 26px}
table.front{width:auto; margin:4px 0 22px; font-size:13px}
table.front th{text-align:left; padding-right:18px; white-space:nowrap; color:var(--ink2);
  border-bottom:1px solid var(--line); text-transform:none; letter-spacing:0; font-size:12.5px}
table.front td{border-bottom:1px solid var(--line)}
ol.refs{padding-left:26px} ol.refs li{margin:6px 0}
p.lead{margin:16px 0 6px}
a{color:inherit; text-decoration-color:var(--rule); text-underline-offset:3px}
.small{font-size:13.5px; color:var(--ink2)}
.note{background:var(--panel); border-left:3px solid var(--warn); padding:14px 18px;
  margin:16px 0; font-size:14.5px}

.answer{display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:1px;
  background:var(--rule); border:1px solid var(--rule); margin:24px 0 8px}
.answer > div{background:var(--bg); padding:16px 20px}
.answer h4{margin:0 0 8px; font-size:12.5px; font-family:"IBM Plex Mono",monospace;
  letter-spacing:.1em; text-transform:uppercase; color:var(--ink3)}
.answer ul{margin:0; padding-left:18px} .answer li{margin:9px 0; line-height:1.85}
.answer .h h4{color:var(--ok)} .answer .f h4{color:var(--warn)}

.top{display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:1px;
  background:var(--rule); border:1px solid var(--rule); margin:22px 0 8px}
.top div{background:var(--panel); padding:13px 17px}
.top .k{font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink2)}
.top .v{font-size:16px; font-weight:700; margin-top:3px; line-height:1.45}
.top .v.y{color:var(--ok)} .top .v.n{color:var(--warn)}

.wrap{overflow-x:auto; margin:14px 0 8px}
table{border-collapse:collapse; width:100%; font-size:13.5px}
th,td{text-align:left; padding:7px 16px 7px 0; border-bottom:1px solid var(--line);
  vertical-align:top}
th{font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink2); font-weight:600;
  border-bottom:1px solid var(--rule); white-space:nowrap}
td.m{font-family:"IBM Plex Mono",monospace; white-space:nowrap}
td.n,th.n{font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums;
  white-space:nowrap; text-align:right; padding-right:22px}
th.n{text-align:right}
.ok{color:var(--ok); font-weight:500} .no{color:var(--warn); font-weight:500}
tr.sum td{border-top:1px solid var(--rule); font-weight:700}
tr.alt td{background:var(--panel)}

details{border:1px solid var(--line); border-radius:2px; margin:14px 0; background:var(--bg)}
details[open]{background:transparent}
summary{cursor:pointer; padding:11px 16px; font-family:"IBM Plex Mono",monospace;
  font-size:13px; letter-spacing:.04em; color:var(--ink2); background:var(--panel);
  list-style:none; display:flex; align-items:center; gap:10px}
summary::-webkit-details-marker{display:none}
summary::before{content:"\\25B8"; font-size:12px; color:var(--ink3)}
details[open] summary::before{content:"\\25BE"}
summary:hover{color:var(--ink)}
details > .wrap, details > p, details > figure{padding:0 16px}
details > .wrap{margin-top:12px}
details > p:last-child{padding-bottom:14px}

figure{margin:20px 0 8px}
figure svg{display:block; width:100%; height:auto}
figcaption{font-size:13.5px; color:var(--ink2); margin-top:12px}
figcaption .src{display:inline-block; font-family:"IBM Plex Mono",monospace; font-size:11.5px;
  letter-spacing:.08em; border:1px solid var(--rule); padding:1px 7px; margin-right:9px;
  color:var(--ink2); font-weight:500; vertical-align:1px}
.eq{background:var(--panel); border:1px solid var(--line); padding:18px 22px; margin:14px 0;
  font-family:"IBM Plex Mono",monospace; font-size:15.5px; line-height:1.9; overflow-x:auto; white-space:nowrap}
.eq b{color:var(--accent); font-weight:600}



footer{margin-top:60px; padding-top:18px; border-top:1px solid var(--line); font-size:12.5px;
  color:var(--ink3); font-family:"IBM Plex Mono",monospace; line-height:1.9}

.viz text{font-family:"IBM Plex Mono",monospace; font-size:12px; fill:var(--ink2)}
.viz text.lbl{font-size:12.5px; font-weight:600}
.viz .gl{stroke:var(--grid); stroke-width:1}
.viz .ax{stroke:var(--axis); stroke-width:1}
.viz .ln{fill:none; stroke-width:2; stroke-linejoin:round; stroke-linecap:round}
.viz circle.pt{stroke:var(--bg); stroke-width:1.5}
.legend{display:flex; flex-wrap:wrap; gap:6px 20px; margin:10px 0 0;
  font-family:"IBM Plex Mono",monospace; font-size:12.5px; color:var(--ink2)}
.legend span{display:inline-flex; align-items:center; gap:7px}
.legend i{width:14px; height:3px; border-radius:2px; display:inline-block}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
"""


def css() -> str:
    """The stylesheet, with both themes filled in from PALETTE."""
    return (CSS.replace("__LIGHT__", _tokens("light"))
               .replace("__DARK__", _tokens("dark")))


def render(d: dict) -> str:
    o = [f'<title>{esc(d["title"])}</title>',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500;600'
         '&display=swap">',
         f"<style>{css()}</style>", "<main>",
         f'<p class="eyebrow">{esc(d["eyebrow"])}</p>',
         f'<h1>{esc(d["title"])}</h1>']
    # front matter, ISO/IEC/IEEE 29119-3 5.2: identifier, issuer, status, history
    fm = d.get("front", {})
    if fm:
        o.append('<table class="front">' + "".join(
            f"<tr><th>{esc(k)}</th><td>{v}</td></tr>" for k, v in fm.items()) + "</table>")
    o.append(f'<p class="lede">{d["lede"]}</p>')

    # numbered headings: consecutive sections of one role share a number
    n = 0
    i = 0
    secs = d["sections"]
    numbered = {"序論", "用語", "方法", "結果", "考察", "結論"}
    while i < len(secs):
        role = secs[i].get("role")
        j = i
        while j < len(secs) and secs[j].get("role") == role:
            j += 1
        group = secs[i:j]
        if role in numbered:
            n += 1
        for k, s in enumerate(group):
            if role in numbered:
                num = f"{n}." if len(group) == 1 else f"{n}.{k + 1}"
                label = f'<span class="num">{num}</span> {esc(s["h"])}'
            elif role == "付録":
                label = f'<span class="num">付録 {chr(ord("A") + k)}</span>　{esc(s["h"])}'
            else:
                label = esc(s["h"])
            en = f'<span class="en">{esc(s["en"])}</span>' if s.get("en") else ""
            o.append(f'<h2>{label}{en}</h2>')
            if role == "結論" and k == 0 and d.get("answer"):
                a = d["answer"]
                o.append('<div class="answer"><div class="h"><h4>成立していること</h4><ul>'
                         + "".join(f"<li>{x}</li>" for x in a["holds"]) + "</ul></div>")
                o.append('<div class="f"><h4>成立していないこと</h4><ul>'
                         + "".join(f"<li>{x}</li>" for x in a["fails"]) + "</ul></div></div>")
            if role == "参考文献":
                o.append("<ol class=\"refs\">" + "".join(
                    f"<li>{r}</li>" for r in d.get("references", [])) + "</ol>")
            o += [render_block(b) for b in s["blocks"]]
        i = j

    o.append("</main>")
    page = "\n".join(o) + "\n"
    # one pass for the number-unit glue, over every text node outside SVG and
    # CSS. Doing it per block missed legends, headers and KPI keys in turn.
    parts = re.split(r"(<(?:svg|style)\b.*?</(?:svg|style)>)", page, flags=re.S)
    return "".join(x if x.startswith(("<svg", "<style")) else jp_wrap(x) for x in parts)


def check_bounds(html_text: str) -> list[str]:
    """Every drawn coordinate must sit inside its own viewBox.

    The old reports had their SVG coordinates typed by hand, so a label could
    sit outside the drawing and nothing said so. Here the geometry is computed,
    and this asserts the computation stayed inside the frame.
    """
    import re
    bad = []
    for m in re.finditer(r'<svg viewBox="0 0 ([\d.]+) ([\d.]+)"(.*?)</svg>', html_text, re.S):
        w, h, body = float(m.group(1)), float(m.group(2)), m.group(3)
        lab = re.search(r'aria-label="([^"]{0,36})', body)
        name = lab.group(1) if lab else "?"
        for attrs, lim in ((("x", "x1", "x2", "cx"), w), (("y", "y1", "y2", "cy"), h)):
            for a in attrs:
                for v in re.findall(rf'\b{a}="(-?[\d.]+)"', body):
                    if not -2 <= float(v) <= lim + 2:
                        bad.append(f"{name}: {a}={v} が viewBox {lim} の外")
        for x, ww in re.findall(r'<rect x="([\d.]+)" y="[\d.]+" width="([\d.]+)"', body):
            if float(x) + float(ww) > w + 2:
                bad.append(f"{name}: 棒の右端 {float(x) + float(ww):.0f} が viewBox {w} の外")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    d = json.loads(Path(a.json).read_text(encoding="utf-8"))
    out = render(d)
    for b in check_bounds(out):
        print(f"  NG  はみ出し {b}")
        return 1
    Path(a.out).write_text(out, encoding="utf-8")
    n = sum(len(s["blocks"]) for s in d["sections"])
    print(f"  ok  {a.out}  ({len(d['sections'])} 節 / {n} ブロック)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
