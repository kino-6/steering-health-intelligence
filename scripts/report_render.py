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
                     f'font-size="10.5" fill="{fill}">{esc(it["note"])}</text>')

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
    ylo = 0.0 if min(allv) >= 0 else -nice_max(-min(allv))
    yhi = nice_max(max(allv))
    x0, x1, y0, y1 = 70, 700, 34, 230
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
        g.append(f'<text x="{x0 + 6}" y="{fy(hl["y"]) - 6:.1f}" font-size="10.5" '
                 f'fill="{col}">{esc(hl["label"])}</text>')
    for mk in c.get("marks", []):
        g.append(f'<line x1="{fx(mk["x"]):.1f}" y1="{y0}" x2="{fx(mk["x"]):.1f}" y2="{y1}" '
                 f'stroke="var(--accent)" stroke-width="1.4" stroke-dasharray="4 3"/>')
        g.append(f'<text x="{fx(mk["x"]) - 6:.1f}" y="{y0 + 12}" font-size="10.5" '
                 f'fill="var(--accent)" text-anchor="end">{esc(mk["label"])}</text>')
    g.append(f'<line class="ax" x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}"/>')

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
            g.append(f'<text class="lbl" x="{pts[-1][0] + 8:.1f}" y="{pts[-1][1] + 4:.1f}" '
                     f'fill="{col}">{esc(s["endlabel"])}</text>')

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


# ---------------------------------------------------------------- byte layout

SIZES = {"f64": 8, "f32": 4, "u32": 4, "i32": 4, "u16": 2, "i16": 2,
         "u8": 1, "i8": 1}


def field_bits(f: dict) -> int:
    if "bits" in f:
        return int(f["bits"])
    return SIZES[f["t"]] * 8


def render_bytes(b: dict) -> str:
    """A memory map drawn to scale, plus the table that names every field.

    2026-09-10, the user asked why the data structures were acceptable in this
    format. They were not: the previous block drew one equal-width box per
    field, so a 4-byte float and a 1-byte flag looked the same and the layout
    could not be read at all. Widths come from the type now, the offsets are
    drawn, and the declared total is checked against the sum.
    """
    fs = b["fields"]
    bits = [field_bits(f) for f in fs]
    tot = sum(bits)
    in_bits = any("bits" in f for f in fs)
    unit = "ビット" if in_bits else "バイト"   # what the ruler counts
    if b["total"] * 8 != tot:                 # total is always in bytes
        raise SystemExit(f"バイト割り当てが合わない: 宣言 {b['total']} バイト / "
                         f"合計 {tot / 8:g} バイト")

    x0, x1, y0, h = 8, 772, 28, 40
    per = (x1 - x0) / tot
    step = 4 if not in_bits else 8            # ruler step, in the drawn unit
    step_b = step * (1 if in_bits else 8)

    g = [f'<svg viewBox="0 0 780 {y0 + h + 46}" role="img" '
         f'aria-label="{esc(b["alt"])}">']
    off = 0
    for f, nb in zip(fs, bits):
        w = nb * per
        x = x0 + off * per
        key = f.get("key")
        fill = "var(--accent)" if key else "var(--panel2)"
        ink = "var(--bg)" if key else "var(--ink2)"
        g.append(f'<rect x="{x:.1f}" y="{y0}" width="{max(w - 1.5, 1.5):.1f}" '
                 f'height="{h}" fill="{fill}" stroke="var(--line)" stroke-width="1">'
                 f'<title>{esc(f["name"])} {esc(f.get("t", str(f.get("bits")) + " bit"))}'
                 f' @ {off // (1 if in_bits else 8)}</title></rect>')
        lab = str(f["name"])
        if _cjk_width(lab) * 0.82 < w - 8:
            g.append(f'<text x="{x + w / 2 - 0.8:.1f}" y="{y0 + h / 2 + 4:.1f}" '
                     f'text-anchor="middle" font-size="10.5" fill="{ink}">{esc(lab)}</text>')
        else:
            g.append(f'<text x="{x + w / 2 - 0.8:.1f}" y="{y0 + h / 2 + 4:.1f}" '
                     f'text-anchor="middle" font-size="10.5" fill="{ink}">'
                     f'{off // (1 if in_bits else 8)}</text>')
        off += nb

    # offset ruler
    g.append(f'<line class="ax" x1="{x0}" y1="{y0 + h + 6}" x2="{x1}" y2="{y0 + h + 6}"/>')
    o = 0
    while o <= tot:
        x = x0 + o * per
        g.append(f'<line class="ax" x1="{x:.1f}" y1="{y0 + h + 6}" x2="{x:.1f}" '
                 f'y2="{y0 + h + 11}"/>')
        g.append(f'<text x="{x:.1f}" y="{y0 + h + 26}" text-anchor="middle" '
                 f'font-size="10">{o // (1 if in_bits else 8)}</text>')
        o += step_b
    g.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{y0 + h + 42}" text-anchor="middle" '
             f'fill="var(--ink3)" font-size="11">{esc(unit)}の位置</text>')
    g.append(f'<text x="{x0}" y="{y0 - 10}" font-size="11" fill="var(--ink3)">'
             f'0</text>')
    g.append(f'<text x="{x1}" y="{y0 - 10}" font-size="11" fill="var(--ink3)" '
             f'text-anchor="end">{b["total"]} バイト</text>')
    g.append("</svg>")

    fig = (f'<figure class="viz">' + "\n".join(g)
           + f'<figcaption><b class="src">実測</b>{b["caption"]}</figcaption></figure>')

    # the table is generated from the same fields, so the two cannot disagree
    rows, off = [], 0
    for f in fs:
        nb = field_bits(f)
        pos = (f"{off // 8}" if not in_bits
               else f"{off // 8} バイト bit{off % 8}")
        size = (f'{nb // 8} B' if not in_bits else f"{nb} bit")
        rows.append([{"v": f["name"], "tone": "ok" if f.get("key") else ""},
                     f.get("t", "bit"), pos, size, f.get("why", "")])
        off += nb
    rows.append({"cells": ["合計", "", "", f'{b["total"]} B', b.get("sum_why", "")],
                 "sum": True})
    tbl = render_table({"cols": ["フィールド", "型", {"t": "位置", "n": True},
                                 {"t": "大きさ", "n": True}, "何のためにあるか"],
                        "rows": rows, "stripe": True,
                        "fold": b.get("fold", f'割り当て {len(fs)} フィールドの内訳')})
    return fig + tbl


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
            tds.append(f'<td class="{k.strip()}">{esc(v)}</td>' if k.strip()
                       else f"<td>{esc(v)}</td>")
        body.append(f"<tr{cls}>" + "".join(tds) + "</tr>")
    t = (f'<div class="wrap"><table><tr>{head}</tr>' + "".join(body) + "</table></div>")
    if b.get("note"):
        t += f'<p class="small">{esc(b["note"])}</p>'
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
:root{
  --bg:#f7f8f6; --panel:#edefea; --panel2:#e3e6e0; --ink:#12161a; --ink2:#4b544d; --ink3:#7b857c;
  --line:#d5d9d2; --rule:#bfc5bc; --accent:#a35f00; --warn:#9d3327; --ok:#2f6b45;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#c98500; --s5:#c0568a; --s6:#4a7a2c;
  --grid:#d5d9d2; --axis:#7b857c;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#141715; --panel:#1c201d; --panel2:#242924; --ink:#e9ece7; --ink2:#aab3ab; --ink3:#7c867d;
  --line:#2e342f; --rule:#3d443e; --accent:#e0a33c; --warn:#e07a68; --ok:#79bd92;
  --s1:#5f9fe8; --s2:#f0855a; --s3:#4cc79a; --s4:#dcaa3f; --s5:#dd85ac; --s6:#8fb96a;
  --grid:#2e342f; --axis:#7c867d;
}}
:root[data-theme="dark"]{
  --bg:#141715; --panel:#1c201d; --panel2:#242924; --ink:#e9ece7; --ink2:#aab3ab; --ink3:#7c867d;
  --line:#2e342f; --rule:#3d443e; --accent:#e0a33c; --warn:#e07a68; --ok:#79bd92;
  --s1:#5f9fe8; --s2:#f0855a; --s3:#4cc79a; --s4:#dcaa3f; --s5:#dd85ac; --s6:#8fb96a;
  --grid:#2e342f; --axis:#7c867d;
}
*{box-sizing:border-box}
body{background:var(--bg); color:var(--ink); margin:0;
  font-family:"Zen Kaku Gothic New",system-ui,"Hiragino Sans","Noto Sans JP",sans-serif;
  font-size:14.5px; line-height:1.75}
main{max-width:1280px; margin:0 auto; padding:44px 30px 88px}
.eyebrow{font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink3); margin:0 0 12px}
h1{font-size:clamp(24px,3.4vw,34px); font-weight:700; line-height:1.3; margin:0 0 6px;
  text-wrap:balance}
.lede{color:var(--ink2); font-size:15px; margin:0 0 28px; max-width:78ch}
h2{font-size:17px; font-weight:700; margin:52px 0 2px; padding-bottom:7px;
  border-bottom:1px solid var(--rule); overflow:hidden}
h2 .en{font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.08em;
  color:var(--ink3); font-weight:400; float:right; padding-top:5px}
h3{font-size:14px; font-weight:700; margin:28px 0 6px; color:var(--ink2)}
p{margin:12px 0; max-width:82ch}
p.lead{margin:16px 0 6px}
a{color:inherit; text-decoration-color:var(--rule); text-underline-offset:3px}
.small{font-size:12.5px; color:var(--ink2)}
.note{background:var(--panel); border-left:3px solid var(--warn); padding:12px 18px;
  margin:16px 0; font-size:13.5px}

.answer{display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:1px;
  background:var(--rule); border:1px solid var(--rule); margin:24px 0 8px}
.answer > div{background:var(--bg); padding:16px 20px}
.answer h4{margin:0 0 8px; font-size:12px; font-family:"IBM Plex Mono",monospace;
  letter-spacing:.1em; text-transform:uppercase; color:var(--ink3)}
.answer ul{margin:0; padding-left:18px} .answer li{margin:5px 0}
.answer .h h4{color:var(--ok)} .answer .f h4{color:var(--warn)}

.top{display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:1px;
  background:var(--rule); border:1px solid var(--rule); margin:22px 0 8px}
.top div{background:var(--panel); padding:13px 17px}
.top .k{font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ink3)}
.top .v{font-size:15px; font-weight:700; margin-top:3px; line-height:1.45}
.top .v.y{color:var(--ok)} .top .v.n{color:var(--warn)}

.wrap{overflow-x:auto; margin:14px 0 8px}
table{border-collapse:collapse; width:100%; font-size:12.5px}
th,td{text-align:left; padding:7px 16px 7px 0; border-bottom:1px solid var(--line);
  vertical-align:top}
th{font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink3); font-weight:500;
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
summary{cursor:pointer; padding:10px 16px; font-family:"IBM Plex Mono",monospace;
  font-size:12px; letter-spacing:.04em; color:var(--ink2); background:var(--panel);
  list-style:none; display:flex; align-items:center; gap:10px}
summary::-webkit-details-marker{display:none}
summary::before{content:"\\25B8"; font-size:10px; color:var(--ink3)}
details[open] summary::before{content:"\\25BE"}
summary:hover{color:var(--ink)}
details > .wrap, details > p, details > figure{padding:0 16px}
details > .wrap{margin-top:12px}
details > p:last-child{padding-bottom:14px}

figure{margin:20px 0 8px}
figure svg{display:block; width:100%; height:auto}
figcaption{font-size:12px; color:var(--ink3); margin-top:10px; max-width:88ch}
figcaption .src{display:inline-block; font-family:"IBM Plex Mono",monospace; font-size:10px;
  letter-spacing:.08em; border:1px solid var(--rule); padding:1px 7px; margin-right:9px;
  color:var(--ink2); font-weight:500; vertical-align:1px}
.eq{background:var(--panel); border:1px solid var(--line); padding:16px 20px; margin:14px 0;
  font-family:"IBM Plex Mono",monospace; font-size:15px; overflow-x:auto; white-space:nowrap}
.eq b{color:var(--accent); font-weight:600}
.bytes{display:flex; flex-wrap:wrap; gap:2px; margin:10px 0 4px;
  font-family:"IBM Plex Mono",monospace; font-size:11px}
.bytes span{background:var(--panel2); border:1px solid var(--line); padding:5px 9px;
  white-space:nowrap}
.bytes span.a{background:var(--accent); color:var(--bg); border-color:var(--accent)}
footer{margin-top:60px; padding-top:18px; border-top:1px solid var(--line); font-size:11.5px;
  color:var(--ink3); font-family:"IBM Plex Mono",monospace; line-height:1.9}

.viz text{font-family:"IBM Plex Mono",monospace; font-size:11px; fill:var(--ink2)}
.viz text.lbl{font-size:11.5px; font-weight:500}
.viz .gl{stroke:var(--grid); stroke-width:1}
.viz .ax{stroke:var(--axis); stroke-width:1}
.viz .ln{fill:none; stroke-width:2; stroke-linejoin:round; stroke-linecap:round}
.viz circle.pt{stroke:var(--bg); stroke-width:1.5}
.legend{display:flex; flex-wrap:wrap; gap:6px 20px; margin:8px 0 0;
  font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:var(--ink2)}
.legend span{display:inline-flex; align-items:center; gap:7px}
.legend i{width:14px; height:3px; border-radius:2px; display:inline-block}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
"""


def render(d: dict) -> str:
    o = [f'<title>{esc(d["title"])}</title>',
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500;600'
         '&display=swap">',
         f"<style>{CSS}</style>", "<main>",
         f'<p class="eyebrow">{esc(d["eyebrow"])}</p>',
         f'<h1>{esc(d["title"])}</h1>',
         f'<p class="lede">{d["lede"]}</p>']

    a = d["answer"]
    o.append('<div class="answer"><div class="h"><h4>成立していること</h4><ul>'
             + "".join(f"<li>{x}</li>" for x in a["holds"]) + "</ul></div>")
    o.append('<div class="f"><h4>成立していないこと</h4><ul>'
             + "".join(f"<li>{x}</li>" for x in a["fails"]) + "</ul></div></div>")

    for s in d["sections"]:
        en = f'<span class="en">{esc(s["en"])}</span>' if s.get("en") else ""
        o.append(f'<h2>{esc(s["h"])}{en}</h2>')
        o += [render_block(b) for b in s["blocks"]]

    o.append('<h2>成立範囲<span class="en">scope</span></h2>')
    o.append(render_table({"cols": ["項目", "内容"],
                           "rows": [[k["k"], k["v"]] for k in d["scope"]]}))
    o.append("<footer>" + "<br>\n".join(esc(x) for x in d["sources"]) + "</footer>")
    o.append("</main>")
    return "\n".join(o) + "\n"


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
