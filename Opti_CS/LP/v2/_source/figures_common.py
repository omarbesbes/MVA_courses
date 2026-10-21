"""figures_common.py — shared helpers for the static SVG figures of Opti_CS/LP/v2.

Each page has its own generator, figures_PNN.py, which imports this module and writes figures/PNN/*.svg:
    python3 figures_P03.py        (then node build.mjs Partie03.html)

Every coordinate is computed here rather than estimated by hand. Colours are CSS classes of
style.css (strokes c1..c6, fills f1..f6, transparent fills a1..a5, text tx / tx-s / tx-b / tx-i),
so the figures follow the light and dark themes. Colour code of the LP pages: see GUIDE.md, section 5.
"""
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figures")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Fig:
    """A panel with data coordinates mapped into a region of an SVG canvas."""

    def __init__(self, canvas, box, xr, yr):
        self.c = canvas
        self.x0, self.y0, self.w, self.h = box  # pixel box of the plotting area
        self.xr, self.yr = xr, yr

    def X(self, x):
        return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def path(self, pts, cls, close=False, extra=""):
        d = ""
        pen = False
        for p in pts:
            if p is None or not np.isfinite(p[1]):
                pen = False
                continue
            d += ("L" if pen else "M") + f"{self.X(p[0]):.1f} {self.Y(p[1]):.1f}"
            pen = True
        if close:
            d += "Z"
        self.c.add(f'<path d="{d}" class="{cls}"{extra}/>')

    def fn(self, f, cls, x0=None, x1=None, n=300):
        x0 = self.xr[0] if x0 is None else x0
        x1 = self.xr[1] if x1 is None else x1
        xs = np.linspace(x0, x1, n + 1)
        self.path([(x, f(x)) for x in xs], cls)

    def line(self, x1, y1, x2, y2, cls, extra=""):
        self.c.add(f'<line x1="{self.X(x1):.1f}" y1="{self.Y(y1):.1f}" x2="{self.X(x2):.1f}" y2="{self.Y(y2):.1f}" class="{cls}"{extra}/>')

    def circle(self, x, y, r, cls):
        self.c.add(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" class="{cls}"/>')

    def text(self, x, y, s, cls="tx", anchor="start", dx=0, dy=0):
        self.c.add(f'<text x="{self.X(x) + dx:.1f}" y="{self.Y(y) + dy:.1f}" class="{cls}" text-anchor="{anchor}">{esc(s)}</text>')

    def lollipop(self, x, m, k, r=4.5):
        """A Dirac of mass m at x drawn as a stem (colour index k)."""
        self.line(x, 0, x, m, f"ln c{k}")
        self.circle(x, m, r, f"f{k}")

    def axes(self, xticks=(), yticks=(), xfmt=str, yfmt=str, grid=True, yaxis=True, xlabel=None, ylabel=None):
        for v in xticks:
            if grid:
                self.line(v, self.yr[0], v, self.yr[1], "gr")
            self.text(v, self.yr[0], xfmt(v), "tx-s", "middle", dy=14)
        for v in yticks:
            if grid:
                self.line(self.xr[0], v, self.xr[1], v, "gr")
            self.text(self.xr[0], v, yfmt(v), "tx-s", "end", dx=-5, dy=4)
        y0 = 0 if self.yr[0] <= 0 <= self.yr[1] else self.yr[0]
        self.line(self.xr[0], y0, self.xr[1], y0, "ax")
        if yaxis:
            x0 = 0 if self.xr[0] <= 0 <= self.xr[1] else self.xr[0]
            self.line(x0, self.yr[0], x0, self.yr[1], "ax")
        if xlabel:
            self.text(self.xr[1], self.yr[0], xlabel, "tx-s", "end", dy=28)
        if ylabel:
            self.text(self.xr[0], self.yr[1], ylabel, "tx-s", "start", dx=4, dy=-6)


class Canvas:
    def __init__(self, name, W, H, label, sub=""):
        """A figure figures/<sub>/<name>.svg; marker ids are prefixed by sub-name, so they stay unique in a page."""
        self.name, self.W, self.H, self.label, self.sub = name, W, H, label, sub
        self.items = []
        self.defs = []

    def add(self, s):
        self.items.append(s)

    def arrow_marker(self, k):
        """Arrow head with fill class f{k} (or fk / fm); returns the marker id."""
        mid = f"{self.sub}-{self.name}-arr-{k}"
        if not any(mid in d for d in self.defs):
            self.defs.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="f{k}"/></marker>')
        return mid

    def arrow(self, x1, y1, x2, y2, k, cls=None):
        mid = self.arrow_marker(k)
        cls = cls or f"ln c{k} thin"
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}" marker-end="url(#{mid})"/>')

    def text(self, x, y, s, cls="tx", anchor="start"):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{esc(s)}</text>')

    def save(self):
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        svg = (f'<svg viewBox="0 0 {self.W} {self.H}" role="img" aria-label="{esc(self.label)}" xmlns="http://www.w3.org/2000/svg">'
               + defs + "".join(self.items) + "</svg>")
        out = os.path.join(OUT, self.sub)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, self.name + ".svg"), "w") as f:
            f.write(svg + "\n")
        print("wrote", self.name, f"({len(svg)} bytes)")


def fmt1(v):
    return f"{v:g}"
