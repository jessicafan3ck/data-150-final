"""Shared matplotlib style: reference palette (light mode), recessive axes, 200 dpi PNGs."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "font.family": "sans-serif", "legend.frameon": False, "legend.fontsize": 9, "lines.linewidth": 2,
    "savefig.dpi": 200, "savefig.bbox": "tight",
})


def note(fig, text):
    """Source / method footnote in muted ink under the plot."""
    fig.text(0.01, -0.02, text, fontsize=7.5, color=MUTED, ha="left", va="top", wrap=True)
