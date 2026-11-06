"""07_simple_figures.py: simplified, presentation versions of Fig 2 and Fig 3 (class "Create 2" assignment).

Minimal text, one takeaway per chart. Detailed versions stay in 06_figures.py.
Grey for context, blue for attention/fame in both charts.
Writes outputs/figures/simple_1_performance_vs_attention.png and simple_2_attention_effect.png.
"""
from pathlib import Path

import matplotlib.patheffects as pe
import numpy as np
import pandas as pd

import viz_style as vs
from viz_style import plt

ROOT = Path(__file__).resolve().parents[1]
CLEAN, TABLES, FIGS = ROOT / "data/clean", ROOT / "outputs/tables", ROOT / "outputs/figures"
MIN_MINUTES = 900  # drop seasons with too little playing time for a meaningful performance score
CONTEXT = "#c4c3be"  # background dots and other supporting marks
HALO = [pe.withStroke(linewidth=3, foreground=vs.SURFACE)]


def views_fmt(v, _):
    return f"{v / 1e6:.2g}M" if v >= 1e6 else f"{v / 1e3:.3g}K" if v >= 1e3 else f"{v:g}"


def pct(v):
    return f"{v:+.0f}%".replace("-", "−")


def titles(fig, title, subtitle):
    fig.text(0.01, 1.0, title, fontsize=13, fontweight="bold", color=vs.INK, ha="left", va="bottom")
    fig.text(0.01, 0.985, subtitle, fontsize=9.5, color=vs.INK2, ha="left", va="top")


def declutter(ax):
    ax.spines[["left", "bottom"]].set_visible(False)
    ax.tick_params(length=0)


# 1 -------------------------------------------------------------- performance vs attention
pan = pd.read_csv(CLEAN / "panel.csv")
d = pan.dropna(subset=["P", "wiki12"])
d = d[d.minutes >= MIN_MINUTES]

# the example: same season, same position, same performance score, very different attention
pair = d[(d.year == 2022) & d.player_name.isin(["Lionel Messi", "Lautaro Martinez"])].set_index("player_name")
hi, lo = pair.loc["Lionel Messi"], pair.loc["Lautaro Martinez"]
ratio = hi.wiki12 / lo.wiki12

fig, ax = plt.subplots(figsize=(7.5, 5.2))
fig.subplots_adjust(top=0.87)
ax.scatter(d.P, d.wiki12, s=16, color=CONTEXT, alpha=0.6, edgecolor="none")
b = np.polyfit(d.P, np.log(d.wiki12), 1)
xs = np.linspace(d.P.min(), d.P.max(), 50)
ax.plot(xs, np.exp(np.polyval(b, xs)), color=vs.MUTED, lw=1, ls="--")
ax.annotate("average", (xs[-1], np.exp(np.polyval(b, xs[-1]))), xytext=(0, -12), textcoords="offset points",
            ha="right", va="top", fontsize=8, color=vs.INK2, path_effects=HALO)

ax.plot([hi.P, lo.P], [hi.wiki12, lo.wiki12], color=vs.BLUE, lw=1.2, ls=":", zorder=3)
for p in (hi, lo):
    ax.scatter(p.P, p.wiki12, s=70, color=vs.BLUE, edgecolor=vs.SURFACE, linewidth=2, zorder=4)
ax.annotate(f"{ratio:.0f}×", ((hi.P + lo.P) / 2, np.sqrt(hi.wiki12 * lo.wiki12)), xytext=(7, 0),
            textcoords="offset points", ha="left", va="center", fontsize=13, fontweight="bold", color=vs.INK,
            path_effects=HALO, zorder=5)
ax.annotate("Messi", (hi.P, hi.wiki12), xytext=(-10, 0), textcoords="offset points", ha="right", va="center",
            fontsize=9, color=vs.INK, path_effects=HALO)
# the lower-right is empty: Lautaro's label goes there with a short leader line
ax.annotate("Lautaro Martínez", (lo.P, lo.wiki12), xytext=(2.05, 1.6e4), textcoords="data", ha="left",
            va="center", fontsize=9, color=vs.INK, path_effects=HALO,
            arrowprops=dict(arrowstyle="-", color=vs.MUTED, lw=0.7, shrinkA=0, shrinkB=5))

ax.set_yscale("log")
ax.yaxis.set_major_formatter(plt.FuncFormatter(views_fmt))
ax.yaxis.set_minor_locator(plt.NullLocator())
ax.set_ylim(bottom=1e3)  # show the 1K gridline under the lowest dots
ax.grid(axis="x", visible=False)
ax.grid(axis="y", color=vs.GRID, lw=0.6)
declutter(ax)
ax.text(0, 1.03, "Wikipedia page views per month (log scale)", transform=ax.transAxes, ha="left",
        va="bottom", fontsize=9, color=vs.INK2)
ax.set_xlabel("Performance score (0 = average)")
ax.text(0, -0.025, "← worse", transform=ax.transAxes, ha="left", va="top", fontsize=9, color=vs.INK2)
ax.text(1, -0.025, "better →", transform=ax.transAxes, ha="right", va="top", fontsize=9, color=vs.INK2)
titles(fig, "On-pitch performance vs. Wikipedia attention, top-5 league players, 2016–2025",
       "Each dot is one player's season. Highlighted: Messi and Lautaro Martínez, 2021/22.")
fig.savefig(FIGS / "simple_1_performance_vs_attention.png"); plt.close(fig)

# 2 -------------------------------------------------------------- effect of attention on value
s = pd.read_csv(TABLES / "models_C_summary.csv").set_index("outcome")
rows = [("A", "Market value"), ("B", "Transfer fee")]
fig, ax = plt.subplots(figsize=(7.5, 2.6))
fig.subplots_adjust(top=0.80, left=0.18)
for i, (k, label) in enumerate(rows):
    y = -i
    est, lo, hi = s.loc[k, ["pct_per_doubling", "ci_lo_pct", "ci_hi_pct"]]
    ax.plot([lo, hi], [y, y], color=vs.BLUE, lw=3, solid_capstyle="round")
    ax.scatter(est, y, s=90, color=vs.BLUE, edgecolor=vs.SURFACE, linewidth=2, zorder=3)
    ax.annotate(pct(est), (hi, y), xytext=(10, 2), textcoords="offset points", va="bottom", fontsize=11,
                fontweight="bold", color=vs.INK)
    ax.annotate(f"95% CI: {pct(lo)} to {pct(hi)}", (hi, y), xytext=(10, -2), textcoords="offset points",
                va="top", fontsize=8.5, color=vs.INK2)
    ax.text(-0.02, y, label, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=10,
            color=vs.INK)
ax.axvline(0, color=vs.INK2, lw=1)
ax.annotate("no effect", (0, 0.42), xytext=(-4, 0), textcoords="offset points", ha="right", fontsize=8,
            color=vs.INK2)
ax.set_yticks([])
ax.set_ylim(-1.5, 0.55)
ax.set_xlim(-12, 80)
ax.set_xticks([0, 20, 40])
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: pct(v) if v else "0"))
ax.grid(False)
declutter(ax)
titles(fig, "Change in player value per doubling of Wikipedia attention",
       "Comparing players with the same performance, age and position. Bars show 95% confidence intervals.")
fig.savefig(FIGS / "simple_2_attention_effect.png"); plt.close(fig)
print("written: simple_1_performance_vs_attention.png, simple_2_attention_effect.png")
