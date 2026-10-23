# -*- coding: utf-8 -*-
"""diagram_kit v2 — primitives for single-figure explanation diagrams.

Design contract
---------------
* The axes spans the whole figure, so **drawing coordinates are inches**:
  a canvas of (W, H) has x in [0, W] and y in [0, H]. Nudging a label by 0.2 is
  therefore an obvious, predictable move.
* Every primitive takes absolute coordinates and never guesses a layout.
* Overlap is the author's job, but `Canvas.qa()` now measures it: it reports
  intersecting text pairs, texts outside the canvas, and glyphs the CJK face
  cannot render. `save()` runs `qa()` automatically.
* Keep CJK and monospace text in separate calls — `text(mono=True)` refuses CJK
  and warns instead of silently dropping glyphs.

Quick start
-----------
    from diagram_kit import Canvas, PALETTE
    c = Canvas()
    c.title("组张量：nx.Graph → BatchedGraph（COO）", "graco/data/batch.py")
    c.box(0.2, 4.7, 4.0, 3.5, "① 输入：两张 nx.Graph")
    c.node_graph(1.15, 5.05, [(0.6, 2.3), (2.0, 2.3)], [(0, 1)], ["0", "1"], PALETTE["blue"])
    c.save("out.png")          # prints a QA report
"""
import re
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont, FontProperties
from matplotlib.ft2font import FT2Font
from matplotlib.patches import Circle, FancyBboxPatch

PALETTE = {
    "blue": "#3B6EA5",
    "orange": "#C4712B",
    "green": "#3F7A5E",
    "purple": "#6A5A96",
    "grey": "#6E7B87",
    "red": "#B23B3B",
    "ink": "#1F2A36",
    "ink2": "#2C3E50",
    "soft": "#3A4A5A",
    "box": "#F4F6F9",
    "edge": "#B9C2CC",
    "grid_blue": "#EAF1F8",
    "grid_orange": "#FBEEE2",
    "grid_green": "#E8F1EC",
    "grid_blue_edge": "#BBD0E4",
    "grid_orange_edge": "#E6C9AA",
    "grid_green_edge": "#B9D3C5",
    "wire": "#9AA7B4",
    "hair": "#DDE3E9",
}

#: colour → (fill, border) for grids / chips
TINTS = {
    "blue": ("#EAF1F8", "#BBD0E4"),
    "orange": ("#FBEEE2", "#E6C9AA"),
    "green": ("#E8F1EC", "#B9D3C5"),
    "purple": ("#EDEBF4", "#C6BFDC"),
    "grey": ("#F1F3F5", "#D6DBE0"),
}

CJK_FONTS = ["Microsoft YaHei", "SimHei"]
#: glyphs that CJK faces routinely lack; replaced with ASCII by the author
SUSPECT_GLYPHS = "₁₂₃ₖₙ₍₎⚠Σ∑→≥≤≠×·∘̂≈∼"

_CJK = re.compile(r"[\u2e80-\u9fff\uff00-\uffef\u3000-\u303f]")


def setup_fonts():
    plt.rcParams["font.sans-serif"] = CJK_FONTS
    plt.rcParams["axes.unicode_minus"] = False


def _font_glyphs():
    """Char → glyph index map for the resolved CJK face (cached)."""
    if not hasattr(_font_glyphs, "cache"):
        path = findfont(FontProperties(family=CJK_FONTS))
        _font_glyphs.cache = FT2Font(path)
    return _font_glyphs.cache


def has_glyph(ch):
    try:
        return _font_glyphs().get_char_index(ord(ch)) != 0
    except Exception:
        return True


def check_glyphs(texts):
    """Return {char: sample_text} for characters the CJK face cannot render."""
    bad = {}
    for s in texts:
        for ch in str(s):
            if ch.strip() == "" or ch in "\n":
                continue
            if not has_glyph(ch):
                bad.setdefault(ch, s[:40])
    return bad


class Canvas:
    """One figure, one axes, inch coordinates, with built-in layout QA."""

    def __init__(self, w=15.2, h=9.2, dpi=160, facecolor="white"):
        setup_fonts()
        self.w, self.h = w, h
        self.dpi = dpi
        self.fig = plt.figure(figsize=(w, h), dpi=dpi)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, w)
        self.ax.set_ylim(0, h)
        self.ax.axis("off")
        self.fig.patch.set_facecolor(facecolor)
        self._texts = []          # (artist, kind) for QA
        self._boxes = []          # (x, y, w, h, title) for QA

    # ---------------------------------------------------------------- text --
    def text(self, x, y, s, size=9.6, color=None, mono=False, track=True, **kw):
        """Draw text. Never pass CJK through `mono=True` (the mono face lacks CJK)."""
        kw.setdefault("va", "top")
        kw.setdefault("ha", "left")
        if mono:
            if _CJK.search(str(s)):
                raise ValueError(
                    "mono=True with CJK text will drop glyphs: %r\n"
                    "Split it into a CJK call and a monospace call." % (s,)
                )
            kw["family"] = "monospace"
        art = self.ax.text(x, y, s, fontsize=size, color=color or PALETTE["soft"], **kw)
        if track:
            self._texts.append(art)
        return art

    def title(self, main, sub=None, x=0.35):
        self.ax.text(x, self.h - 0.40, main, fontsize=17, weight="bold",
                     color="#14202E", va="center")
        if sub:
            self.text(x, self.h - 0.74, sub, size=10.5, color=PALETTE["grey"], va="center")

    # ---------------------------------------------------------------- boxes --
    def box(self, x, y, w, h, title=None, fc=None, ec=None, tsize=12.5, lw=1.2,
            tint=None, dashed=False):
        if tint and tint in TINTS:
            fc = fc or TINTS[tint][0]
            ec = ec or TINTS[tint][1]
        self.ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",
            fc=fc or PALETTE["box"], ec=ec or PALETTE["edge"], lw=lw,
            linestyle="--" if dashed else "-"))
        if title:
            self.text(x + 0.16, y + h - 0.26, title, size=tsize, va="top",
                      color=PALETTE["ink"], weight="bold")
        self._boxes.append((x, y, w, h, title))
        return (x, y, w, h)

    def lane(self, x, y, w, h, label, tint="grey", tsize=9.6):
        """Swimlane: a tinted band with a rotated-less label at top-left."""
        self.ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.10",
            fc=TINTS[tint][0], ec=TINTS[tint][1], lw=1.0))
        self.text(x + 0.10, y + h - 0.16, label, size=tsize, va="top",
                  color=PALETTE["soft"], weight="bold")
        self._boxes.append((x, y, w, h, label))

    def chip(self, x, y, text, tint="blue", fs=9.0, pad=0.12, color=None, mono=False):
        """Small rounded label chip; width estimated from text length."""
        w = pad * 2 + len(text) * fs / 160.0 + 0.10 * len(text) * 0.4
        self.ax.add_patch(FancyBboxPatch(
            (x, y), w, 0.30, boxstyle="round,pad=0.02,rounding_size=0.08",
            fc=TINTS[tint][0], ec=TINTS[tint][1], lw=1.0))
        self.text(x + pad, y + 0.15, text, size=fs, va="center",
                  color=color or PALETTE[tint], mono=mono)
        return w

    # ------------------------------------------------------------ arrows ----
    def arrow(self, x1, y1, x2, y2, color=None, lw=1.8, ms=14, style="-|>", ls="-"):
        self.ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                         arrowprops=dict(arrowstyle=style, color=color or "#5A6B7B",
                                         lw=lw, mutation_scale=ms, linestyle=ls))

    def elbow(self, pts, color=None, lw=1.6, head=True):
        """Orthogonal routed connector through a list of points."""
        (x0, y0), rest = pts[0], pts[1:]
        for i, (x1, y1) in enumerate(rest):
            last = i == len(rest) - 1
            self.ax.plot([x0, x1], [y0, y1], color=color or "#5A6B7B", lw=lw,
                         solid_capstyle="round", zorder=2)
            x0, y0 = x1, y1
        if head:
            self.arrow(pts[-2][0], pts[-2][1], pts[-1][0], pts[-1][1],
                       color=color, lw=lw)

    # ------------------------------------------------------------ primitives --
    def node_graph(self, ox, oy, pos, edges, labels, color, r=0.19, lsize=9.5, lw=1.6,
                   directed=False):
        """Tiny node-link drawing. `pos` are offsets from (ox, oy), in inches."""
        for u, v in edges:
            p, q = (ox + pos[u][0], oy + pos[u][1]), (ox + pos[v][0], oy + pos[v][1])
            if directed:
                self.arrow(p[0], p[1], q[0], q[1], color=PALETTE["wire"], lw=lw, ms=11)
            else:
                self.ax.plot([p[0], q[0]], [p[1], q[1]], color=PALETTE["wire"],
                             lw=lw, zorder=1)
        for i, (x, y) in enumerate(pos):
            self.ax.add_patch(Circle((ox + x, oy + y), r, fc=color, ec="white",
                                     lw=1.2, zorder=3))
            self.ax.text(ox + x, oy + y, labels[i], color="white", fontsize=lsize,
                         ha="center", va="center", zorder=4, weight="bold")

    def tensor_grid(self, x0, y0, rows, row_labels=None, group_sizes=None,
                    group_colors=None, cw=0.80, ch=0.50, fs=9.8, label_fs=10,
                    drop=0.07, header=None, tints=None):
        """Numeric grid (COO rows, matrices, tables). One cell per value.

        `tints` overrides the per-cell tint list (list of "blue"/"orange"/...).
        Returns (width, height) consumed so callers can place brackets.
        """
        ncol = len(rows[0])
        groups = group_sizes or [ncol]
        names = list(tints) if tints else []
        if not names:
            palette_names = ["blue", "orange", "green", "purple"]
            for gi, g in enumerate(groups):
                names += [palette_names[gi % len(palette_names)]] * g
        if header:
            for ci, h in enumerate(header):
                self.text(x0 + ci * cw + (cw - drop) / 2, y0 + 0.34, str(h), size=fs,
                          color=PALETTE["grey"], ha="center", va="center", mono=True)
        for ri, row in enumerate(rows):
            y = y0 - ri * ch
            yl = (row_labels or [None] * len(rows))[ri]
            if yl:
                self.ax.text(x0 - 0.95, y + (ch - drop) / 2, yl, fontsize=label_fs,
                             color=PALETTE["grey"], va="center")
            for ci, val in enumerate(row):
                key = names[ci] if ci < len(names) else "blue"
                if key in ("blue", "orange", "green", "purple", "grey"):
                    tint = key
                    col = PALETTE[tint] if tint != "grey" else PALETTE["soft"]
                else:                                   # explicit hex
                    tint, col = "blue", key
                fc = TINTS[tint][0] if tint in TINTS else PALETTE["grid_blue"]
                ec = TINTS[tint][1] if tint in TINTS else PALETTE["grid_blue_edge"]
                self.ax.add_patch(FancyBboxPatch(
                    (x0 + ci * cw, y), cw - drop, ch - drop,
                    boxstyle="round,pad=0.02,rounding_size=0.04", fc=fc, ec=ec, lw=1.0))
                self.ax.text(x0 + ci * cw + (cw - drop) / 2, y + (ch - drop) / 2,
                             str(val), fontsize=fs, family="monospace",
                             color=col, ha="center", va="center")
        return ncol * cw, len(rows) * ch

    def timeline(self, x0, y, items, span=None, color=None, fs=9.4, r=0.11):
        """Horizontal timeline. `items` = [(label, detail or None), ...]."""
        n = len(items)
        span = span or (self.w - 1.2)
        step = span / max(n - 1, 1)
        self.ax.plot([x0, x0 + span], [y, y], color=PALETTE["edge"], lw=2.2, zorder=1)
        for i, it in enumerate(items):
            label, detail = it if isinstance(it, (tuple, list)) else (it, None)
            x = x0 + i * step
            self.ax.add_patch(Circle((x, y), r, fc=color or PALETTE["blue"],
                                     ec="white", lw=1.2, zorder=3))
            self.text(x, y + 0.26, label, size=fs, ha="center", va="bottom",
                      color=PALETTE["ink2"], weight="bold")
            if detail:
                self.text(x, y - 0.30, detail, size=fs - 0.6, ha="center", va="top",
                          color=PALETTE["grey"])

    def tree(self, x, y, root, children, color=None, gap=0.34, fs=9.4, arm=0.5):
        """Two-level hierarchy: root chip on top, children in a row underneath."""
        col = color or PALETTE["blue"]
        self.ax.add_patch(FancyBboxPatch((x - 0.9, y), 1.8, 0.34,
                                         boxstyle="round,pad=0.02,rounding_size=0.08",
                                         fc=TINTS["blue"][0], ec=TINTS["blue"][1], lw=1.0))
        self.text(x, y + 0.17, root, size=fs + 0.4, ha="center", va="center",
                  color=PALETTE["ink"], weight="bold")
        n = len(children)
        xs = [x + (i - (n - 1) / 2) * 1.5 for i in range(n)]
        ych = y - 0.95
        self.ax.plot([x, x], [y, y - arm + 0.02], color=PALETTE["wire"], lw=1.4)
        if n > 1:
            self.ax.plot([xs[0], xs[-1]], [y - arm + 0.02, y - arm + 0.02],
                         color=PALETTE["wire"], lw=1.4)
        for cx, ch in zip(xs, children):
            self.ax.plot([cx, cx], [y - arm + 0.02, ych + 0.32], color=PALETTE["wire"], lw=1.4)
            self.ax.add_patch(FancyBboxPatch((cx - 0.66, ych), 1.32, 0.32,
                                             boxstyle="round,pad=0.02,rounding_size=0.06",
                                             fc="white", ec=col, lw=1.0))
            self.text(cx, ych + 0.16, ch, size=fs - 0.4, ha="center", va="center",
                      color=PALETTE["ink2"])

    def bracket(self, x1, x2, y, label, color, fs=9.4, tick=0.22):
        """Horizontal |-| bracket with a centred label underneath."""
        self.ax.annotate("", xy=(x1, y), xytext=(x2, y),
                         arrowprops=dict(arrowstyle="|-|", color=color, lw=1.4))
        self.ax.text((x1 + x2) / 2, y - tick, label, fontsize=fs, color=color,
                     ha="center", va="top")

    def callout(self, x, y, w, h, text, color=None, fs=9.4, tint="orange"):
        """Dashed attention box (pitfall / caveat)."""
        col = color or PALETTE["red"]
        self.ax.add_patch(FancyBboxPatch((x, y), w, h,
                                         boxstyle="round,pad=0.04,rounding_size=0.08",
                                         fc="white", ec=col, lw=1.3, linestyle="--"))
        self.text(x + 0.14, y + h - 0.18, text, size=fs, va="top", color=col)
        self._boxes.append((x, y, w, h, text))

    def legend(self, x, y, items, fs=9.2, dx=0.42, dy=0.30):
        """items = [(tint_name, label), ...]"""
        for i, (tint, label) in enumerate(items):
            yy = y - i * dy
            self.ax.add_patch(FancyBboxPatch((x, yy - 0.10), 0.26, 0.20,
                                             boxstyle="round,pad=0.01,rounding_size=0.04",
                                             fc=TINTS.get(tint, TINTS["blue"])[0],
                                             ec=TINTS.get(tint, TINTS["blue"])[1], lw=1.0))
            self.text(x + dx, yy, label, size=fs, va="center", color=PALETTE["soft"])

    def kv_lines(self, x, y, lines, fs=9.8, mono=True, color=None, dy=0.30):
        """Key/value block; one line per entry. Returns y after the block."""
        for i, s in enumerate(lines):
            use_mono = mono and not _CJK.search(str(s))
            self.text(x, y - i * dy, s, size=fs, color=color or PALETTE["ink2"],
                      va="center", mono=use_mono)
        return y - len(lines) * dy

    def footnote(self, x, y, lines, fs=9.6, dy=0.34, color=None):
        for i, s in enumerate(lines):
            self.ax.text(x, y - i * dy, s, fontsize=fs, color=color or PALETTE["soft"],
                         va="top")

    def why(self, x, y, text, fs=10.2, color=None, width=None):
        """The single most valuable line: why this step exists."""
        self.ax.text(x, y, text, fontsize=fs, color=color or PALETTE["ink2"],
                     va="top", ha="left", weight="bold")

    # ------------------------------------------------------------------ QA --
    def _draw_quiet(self):
        """Draw once while capturing matplotlib's glyph warnings (no stderr spam)."""
        found = {}
        pat = re.compile(r"Glyph (\d+)")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self.fig.canvas.draw()
        for w in caught:
            m = pat.search(str(w.message))
            if m:
                try:
                    found[chr(int(m.group(1)))] = "renderer fallback"
                except ValueError:
                    pass
        self._glyphs_from_draw = found
        return found

    def qa(self, pad_shrink=0.90, min_area=4.0):
        """Measure layout problems. Returns dict(overlaps, outside, glyphs)."""
        self._draw_quiet()
        rend = self.fig.canvas.get_renderer()
        W, H = self.fig.canvas.get_width_height()

        boxes = []
        for t in self._texts:
            try:
                bb = t.get_window_extent(renderer=rend)
            except Exception:
                continue
            if bb.width < 1 or bb.height < 1:
                continue
            boxes.append((t.get_text().replace("\n", " ")[:38], bb))

        overlaps = []
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i][1], boxes[j][1]
                # shrink both slightly: touching labels are fine, stacked ones are not
                ax0 = a.x0 + a.width * (1 - pad_shrink) / 2
                ax1 = a.x1 - a.width * (1 - pad_shrink) / 2
                ay0 = a.y0 + a.height * (1 - pad_shrink) / 2
                ay1 = a.y1 - a.height * (1 - pad_shrink) / 2
                bx0 = b.x0 + b.width * (1 - pad_shrink) / 2
                bx1 = b.x1 - b.width * (1 - pad_shrink) / 2
                by0 = b.y0 + b.height * (1 - pad_shrink) / 2
                by1 = b.y1 - b.height * (1 - pad_shrink) / 2
                w = min(ax1, bx1) - max(ax0, bx0)
                h = min(ay1, by1) - max(ay0, by0)
                if w > 0 and h > 0 and w * h > min_area:
                    overlaps.append((boxes[i][0], boxes[j][0], round(w * h, 1)))

        outside = [name for name, bb in boxes
                   if bb.x0 < -2 or bb.y0 < -2 or bb.x1 > W + 2 or bb.y1 > H + 2]
        outside = [n for n in outside if n.strip()]
        glyphs = check_glyphs([b[0] for b in boxes])
        glyphs.update(getattr(self, "_glyphs_from_draw", {}))
        glyphs.update(getattr(self, "_glyphs_from_save", {}))
        return {"overlaps": overlaps, "outside": outside, "glyphs": glyphs}

    def report(self, qa_result=None):
        r = qa_result or self.qa()
        ok = not r["overlaps"] and not r["outside"] and not r["glyphs"]
        print("QA:", "PASS" if ok else "NEEDS FIX")
        if r["overlaps"]:
            print("  overlapping text pairs (%d):" % len(r["overlaps"]))
            for a, b, area in r["overlaps"][:12]:
                print("   - %r  ×  %r   (%.0f px^2)" % (a, b, area))
        if r["outside"]:
            print("  text outside canvas:", r["outside"][:6])
        if r["glyphs"]:
            esc = ["U+%04X %s" % (ord(k), v.encode("unicode_escape").decode("ascii", "replace"))
                   for k, v in list(r["glyphs"].items())[:8]]
            print("  missing glyphs (CJK face cannot render):")
            for e in esc:
                print("   -", e)
        return ok

    # ---------------------------------------------------------------- output --
    def save(self, path, pad=0.18, qa=True):
        found = {}
        pat = re.compile(r"Glyph (\d+)")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self.fig.savefig(path, facecolor=self.fig.get_facecolor(),
                             bbox_inches="tight", pad_inches=pad)
        for w in caught:
            m = pat.search(str(w.message))
            if m:
                try:
                    found[chr(int(m.group(1)))] = "savefig fallback"
                except ValueError:
                    pass
        self._glyphs_from_save = found
        print("saved:", path)
        if qa:
            self.report()
        return path
