"""06_figures.py: the brief §6.7 figure set, PNG at 200 dpi in outputs/figures/."""
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import viz_style as vs
from viz_style import plt

ROOT = Path(__file__).resolve().parents[1]
CLEAN, TABLES, FIGS = ROOT / "data/clean", ROOT / "outputs/tables", ROOT / "outputs/figures"
FIGS.mkdir(parents=True, exist_ok=True)
SEQ = LinearSegmentedColormap.from_list("seq_blue", vs.SEQ_BLUE)
OUT_COL = {"A": vs.BLUE, "B": vs.ORANGE, "C": vs.AQUA}
OUT_LAB = {"A": "A: log market value (panel)", "B": "B: log fee", "C": "C: premium over mv(t−1)"}
CASES = {"Kylian Mbappé", "Neymar", "Ousmane Dembele", "Joao Felix", "Jude Bellingham", "Désiré Doué"}
pct = lambda b: 100 * (np.exp(b * np.log(2)) - 1)

tr = pd.read_csv(CLEAN / "transfers.csv")
pan = pd.read_csv(CLEAN / "panel.csv")
summ = pd.read_csv(TABLES / "models_C_summary.csv")
sens = pd.read_csv(TABLES / "models_sensitivity.csv")
stress = pd.read_csv(TABLES / "stress_tests.csv")
oos = pd.read_csv(TABLES / "models_oos.csv")
rank = pd.read_csv(TABLES / "cases_premium_ranking.csv")

# 1 -------------------------------------------------------------- fee vs pre-transfer market value
d = tr.dropna(subset=["mv_tm1"])
fig, ax = plt.subplots(figsize=(7, 5.2))
lim = [4, 300]
ax.plot(lim, lim, color=vs.MUTED, lw=1, ls="--", zorder=1)
ax.annotate("fee = market value", (14, 14), xytext=(4, -10), textcoords="offset points", fontsize=8, color=vs.MUTED,
            rotation=38)
ax.scatter(d.mv_tm1, d.fee_eur_m, s=46, color=vs.BLUE, edgecolor=vs.SURFACE, linewidth=1.5, zorder=3)
NUDGE = {"Lukaku": (30, -45), "Neves": (-8, 6), "Griezmann": (6, -3), "Wirtz": (5, 5), "Rice": (-8, 6),
         "Bellingham": (6, -13)}
LEADER = {"Lukaku"}  # crowded spot: label placed away with a thin leader line
for r in d.itertuples():
    last = r.player.split()[-1]
    dx, dy = NUDGE.get(last, (5, 3))
    ax.annotate(f"{last} {str(r.year)[2:]}", (r.mv_tm1, r.fee_eur_m), xytext=(dx, dy),
                ha="right" if dx < 0 else "left",
                textcoords="offset points", fontsize=7.5, color=vs.INK2,
                fontweight="bold" if r.player in CASES else "normal",
                arrowprops=dict(arrowstyle="-", color=vs.MUTED, lw=0.7, shrinkA=0, shrinkB=4) if last in LEADER else None)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(lim); ax.set_ylim(10, 300)
for a in (ax.xaxis, ax.yaxis):
    a.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
ax.set_xticks([5, 10, 30, 100, 300]); ax.set_yticks([10, 30, 100, 300])
ax.set_xlabel("Market value in year before transfer (€m, log)")
ax.set_ylabel("Transfer fee (€m, log)")
ax.set_title(f"Fee vs pre-transfer market value ({len(d)} paid transfers with a market value)")
vs.note(fig, "Sources: record_transfers.csv, player_market_values.csv. Bold = named case studies.")
fig.savefig(FIGS / "fig1_fee_vs_mv.png"); plt.close(fig)

# 2 -------------------------------------------------------------- performance vs attention
d = pan.dropna(subset=["P", "log_wiki12"])
fig, ax = plt.subplots(figsize=(7, 5))
sc = ax.scatter(d.P, d.wiki12, c=d.age, cmap=SEQ, s=22, edgecolor=vs.SURFACE, linewidth=0.8, vmin=17, vmax=35)
ax.set_yscale("log")
cb = fig.colorbar(sc, ax=ax, pad=0.02)
cb.set_label("Age", color=vs.INK2); cb.outline.set_visible(False)
rho = d[["P", "log_wiki12"]].corr().iloc[0, 1]
ax.set_xlabel("Performance composite P (z-score vs top-5-league players, same season & position)")
ax.set_ylabel("Mean monthly Wikipedia views, prior 12 months (log)")
ax.set_title(f"Performance vs attention, player-years 2016–2025 (r = {rho:.2f})")
# the top-right is crowded: labels sit in the empty upper-left with thin leader lines
LABEL_AT = {"Lionel Messi": (0.2, 2.6e6), "Cristiano Ronaldo": (-0.6, 1.5e6), "Lamine Yamal": (-1.3, 8.5e5),
            "Erling Haaland": (3.3, 2.6e6), "Jude Bellingham": (2.6, 4.5e6)}
for p, xy in LABEL_AT.items():
    r = d[d.player_name == p].sort_values("wiki12").iloc[-1:]
    if len(r):
        ax.annotate(f"{p.split()[-1]} {r.year.iloc[0]}", (r.P.iloc[0], r.wiki12.iloc[0]), xytext=xy,
                    textcoords="data", fontsize=7.5, color=vs.INK2, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", color=vs.MUTED, lw=0.7, shrinkA=2, shrinkB=3))
ax.set_ylim(top=7e6)
ax.annotate("Few minutes played:\nyoung players and\ninjured stars", (-2.9, 1.5e3), fontsize=7.5, color=vs.MUTED,
            ha="left", va="center", xytext=(-2.2, 6e2), textcoords="data",
            arrowprops=dict(arrowstyle="-", color=vs.MUTED, lw=0.7, shrinkA=2, shrinkB=3))
vs.note(fig, f"N = {len(d)} player-years, {d.player_name.nunique()} players. P: FootyStats season data. "
             "Attention: Wikimedia pageviews (en, user agents, article + redirects).")
fig.savefig(FIGS / "fig2_P_vs_C.png"); plt.close(fig)

# 3 -------------------------------------------------------------- forest plot of C across specifications
rows = []
for r in summ.itertuples():
    rows.append((r.outcome, "Main (M2)", r.pct_per_doubling, r.ci_lo_pct, r.ci_hi_pct))
for r in sens.itertuples():
    if r.variant.startswith("alt C"):
        continue
    rows.append((r.outcome, r.variant, pct(r.coef_C), pct(r.ci_lo), pct(r.ci_hi)))
for r in stress.itertuples():
    if "matched" in r.test or "C_lag" in r.test or "d_C" in r.test:
        continue
    lab = "player fixed effects" if "fixed" in r.test else "drop top-5 influential"
    rows.append((r.test[0], lab, pct(r.coef_C), pct(r.ci_lo), pct(r.ci_hi)))
fp = pd.DataFrame(rows, columns=["outcome", "spec", "est", "lo", "hi"])
# for B and C the level-only spec is the main spec
fp = fp[(fp.spec != "no P (C only)") & ~((fp.outcome != "A") & (fp.spec == "C12 level only"))]
fig, ax = plt.subplots(figsize=(7.5, 0.32 * len(fp) + 1.6))
y, ticks, labels = 0, [], []
for out in ["A", "B", "C"]:
    g = fp[fp.outcome == out]
    for r in g.itertuples():
        ax.plot([r.lo, r.hi], [y, y], color=OUT_COL[out], lw=2, solid_capstyle="round")
        ax.scatter(r.est, y, s=48 if r.spec == "Main (M2)" else 30, color=OUT_COL[out], edgecolor=vs.SURFACE,
                   linewidth=1.5, zorder=3, marker="D" if r.spec == "Main (M2)" else "o")
        ticks.append(y); labels.append(f"{out} · {r.spec}")
        y -= 1
    y -= 0.6
ax.axvline(0, color=vs.INK2, lw=1)
ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=8.5)
ax.set_xlabel("% change in outcome per doubling of Wikipedia attention (95% CI, cluster-robust)")
ax.set_title("Association of attention with value, holding performance fixed")
ax.grid(axis="y", visible=False)
ax.set_xlim(left=min(-60, fp.lo.min() - 5), right=min(fp.hi.max() + 5, 150))
for out in OUT_COL:
    ax.scatter([], [], color=OUT_COL[out], label=OUT_LAB[out])
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.07 - 1.2 / (0.32 * len(fp) + 1.6)), ncol=3)
fig.subplots_adjust(bottom=0.12)
vs.note(fig, f"◆ = main specification. Outcome C (premium) has N = {int(summ.set_index('outcome').n['C'])}; "
             "its intervals are wide by construction. CIs truncated at +150%.")
fig.savefig(FIGS / "fig3_forest_C.png"); plt.close(fig)

# 3b ------------------------------------------------------------- delta R2 with bootstrap CI
fig, ax = plt.subplots(figsize=(6, 3))
for i, r in enumerate(summ.itertuples()):
    ax.plot([r.boot_dr2_lo, r.boot_dr2_hi], [-i, -i], color=OUT_COL[r.outcome], lw=2, solid_capstyle="round")
    ax.scatter(r.delta_r2, -i, s=48, color=OUT_COL[r.outcome], edgecolor=vs.SURFACE, linewidth=1.5, zorder=3, marker="D")
    ax.annotate(f"ΔR² = {r.delta_r2:.3f}   perm. p = {r.perm_p:.3f}   N = {r.n}", (r.boot_dr2_hi, -i), xytext=(8, 0),
                textcoords="offset points", va="center", fontsize=8, color=vs.INK2)
ax.set_yticks([0, -1, -2]); ax.set_yticklabels([OUT_LAB[o] for o in summ.outcome], fontsize=8.5)
ax.set_xlim(left=0, right=summ.boot_dr2_hi.max() * 2.1)
ax.set_xlabel("ΔR² from adding attention to the performance model (M2 − M1), 95% bootstrap CI")
ax.set_title("How much extra variance attention explains")
ax.grid(axis="y", visible=False)
fig.savefig(FIGS / "fig3b_delta_r2.png"); plt.close(fig)

# 4 -------------------------------------------------------------- lollipop of unexplained premium
d = rank.sort_values("resid_premium")
fig, ax = plt.subplots(figsize=(7.5, 0.24 * len(d) + 1.4))
yy = np.arange(len(d))
cols = [SEQ(v) if pd.notna(v) else vs.GRID for v in d.wiki12_pctl]
ax.hlines(yy, 0, d.resid_premium, color=cols, lw=2)
ax.scatter(d.resid_premium, yy, s=34, color=cols, edgecolor=[vs.MUTED if pd.isna(v) else vs.SURFACE for v in d.wiki12_pctl],
           linewidth=1.2, zorder=3)
ax.axvline(0, color=vs.INK2, lw=1)
ax.set_yticks(yy)
ax.set_yticklabels([f"{p} {y}" for p, y in zip(d.player, d.year)], fontsize=7.5)
for t, p in zip(ax.get_yticklabels(), d.player):
    if p in CASES:
        t.set_fontweight("bold"); t.set_color(vs.INK)
ax.set_xlabel("Unexplained premium: log(fee) − leave-one-out performance-only prediction")
ax.set_title("Which transfers cost more than performance predicts?")
ax.grid(axis="y", visible=False)
sm_ = plt.cm.ScalarMappable(cmap=SEQ, norm=plt.Normalize(0, 100))
cb = fig.colorbar(sm_, ax=ax, pad=0.02, fraction=0.04)
cb.set_label("Attention percentile among these transfers", color=vs.INK2); cb.outline.set_visible(False)
vs.note(fig, "Grey = no pageview data (transfer before mid-2016). Bold = named case studies. "
             "+0.69 ≈ fee twice the prediction.")
fig.savefig(FIGS / "fig4_premium_lollipop.png"); plt.close(fig)

# 5 -------------------------------------------------------------- in-sample vs out-of-sample RMSE
g = oos[oos.model.isin(["M1", "M2"])].copy()
fig, ax = plt.subplots(figsize=(7, 3.6))
y, ticks, labels = 0, [], []
for out in ["A", "B", "C"]:
    for m, lab in [("M1", "M1 performance"), ("M2", "M2 + attention")]:
        r = g[(g.outcome == out) & (g.model == m)].iloc[0]
        ax.plot([r.in_sample_rmse, r.oos_rmse], [y, y], color=vs.GRID, lw=2, zorder=1)
        ax.scatter(r.in_sample_rmse, y, s=50, color=vs.BLUE, edgecolor=vs.SURFACE, linewidth=1.5, zorder=3)
        ax.scatter(r.oos_rmse, y, s=50, color=vs.ORANGE, edgecolor=vs.SURFACE, linewidth=1.5, zorder=3)
        ax.annotate(f"{r.oos_rmse:.2f}", (r.oos_rmse, y), xytext=(7, 0), textcoords="offset points", va="center",
                    fontsize=7.5, color=vs.INK2)
        ticks.append(y); labels.append(f"{out} · {lab}")
        y -= 1
    y -= 0.5
ax.set_yticks(ticks); ax.set_yticklabels(labels, fontsize=8.5)
ax.grid(axis="y", visible=False)
ax.set_xlabel("RMSE (log points; lower is better)")
ax.set_title("Does adding attention improve prediction out of sample?")
ax.scatter([], [], color=vs.BLUE, label="in-sample")
ax.scatter([], [], color=vs.ORANGE, label="out-of-sample (folds grouped by player)")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.42), ncol=2)
ax.margins(x=0.12)
fig.savefig(FIGS / "fig5_rmse.png"); plt.close(fig)
print("figures written:", sorted(p.name for p in FIGS.glob("*.png")))
