"""House style for the report's figures (ACM two-column).

    from rh.plotstyle import setup, BLUE, ORANGE, AQUA, GRAY, INK, INK2, panel_letter, save
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE = "#2a78d6"      # convex / archetypes
ORANGE = "#eb6834"    # linear / directions
AQUA = "#1baf7a"      # third series
GRAY = "#898781"      # baselines and nulls
INK = "#0b0b0b"
INK2 = "#52514e"
LIGHT_BLUE = "#9cc3ef"
SINGLE, FULL = 3.33, 7.0  # figure widths in inches

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PDF_DIR = os.path.join(ROOT, "report", "figures")
PNG_DIR = "/tmp/claude-0/-home-user-MVA-courses/0bf8c9d0-cffb-55d5-b9e4-5992de5f6b3a/scratchpad/toy_preview"


def setup():
    """Set matplotlib rcParams for the report."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "legend.fontsize": 7, "legend.frameon": False,
        "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.format": "pdf", "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "axes.linewidth": 0.6, "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK, "ytick.color": INK, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "grid.color": "#e3e2de", "grid.linewidth": 0.4, "grid.linestyle": "-",
        "lines.linewidth": 1.2, "lines.markersize": 3,
        "axes.prop_cycle": matplotlib.cycler(color=[BLUE, ORANGE, AQUA, GRAY]),
        "figure.dpi": 100,
    })


def panel_letter(ax, letter, x=-0.02, y=1.02):
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontweight="bold", ha="right", va="bottom", color=INK)


def save(fig, name):
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)
    fig.savefig(os.path.join(PDF_DIR, name + ".pdf"))
    fig.savefig(os.path.join(PNG_DIR, name + ".png"), dpi=200, format="png")
    print("saved", os.path.join(PDF_DIR, name + ".pdf"))
