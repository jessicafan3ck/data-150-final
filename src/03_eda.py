"""03_eda.py: exploratory analysis (brief §6.3). Tables to outputs/tables/eda_*.csv, summary to docs/results_eda.md."""
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor

import viz_style as vs
from viz_style import plt

ROOT = Path(__file__).resolve().parents[1]
CLEAN, TABLES, FIGS, DOCS = ROOT / "data/clean", ROOT / "outputs/tables", ROOT / "outputs/figures", ROOT / "docs"
FIGS.mkdir(parents=True, exist_ok=True)

pan = pd.read_csv(CLEAN / "panel.csv")
tr = pd.read_csv(CLEAN / "transfers.csv")
md = ["# Exploratory analysis (src/03_eda.py)\n"]

# distributions (log scale)
desc = pd.concat({
    "mv_eur_m (panel)": pan.market_value_eur_m.describe(),
    "wiki12 monthly views (panel)": pan.wiki12.describe(),
    "fee_eur_m (transfers)": tr.fee_eur_m.describe(),
    "wiki12 monthly views (transfers)": tr.wiki12.describe(),
    "premium log(fee/mv_t-1)": tr.premium.describe(),
}, axis=1).T
desc.to_csv(TABLES / "eda_distributions.csv")
md += ["## Distributions\n", desc.round(2).to_markdown(), ""]

# correlations and VIF between P and C
cols = ["log_mv", "P", "log_wiki12", "wiki_growth", "age"]
corr = pan[cols].dropna().corr()
corr.to_csv(TABLES / "eda_corr_panel.csv")
tcols = ["log_fee", "premium", "P", "log_wiki12", "age_at_transfer", "log_buyer_rev"]
tcorr = tr[tcols].dropna().corr()
tcorr.to_csv(TABLES / "eda_corr_transfers.csv")
X = pan[["P", "log_wiki12", "age"]].dropna()
X = X.assign(const=1.0)
vif = {c: variance_inflation_factor(X.values, i) for i, c in enumerate(X.columns) if c != "const"}
md += ["## Correlations (panel, rows with P and C)\n", corr.round(2).to_markdown(), "",
       "## Correlations (transfers)\n", tcorr.round(2).to_markdown(), "",
       f"VIF (panel): " + ", ".join(f"{k} {v:.2f}" for k, v in vif.items()) + "\n"]

# age curve: how much does age alone shape mv?
age_curve = pan.groupby(["age", "position"]).log_mv.median().unstack()
age_curve.to_csv(TABLES / "eda_age_curve_by_position.csv")

# fee-to-mv ratio over time and by buyer
tr["fee_to_mv"] = tr.fee_eur_m / tr.mv_tm1
by_year = tr.groupby("year").fee_to_mv.agg(["median", "count"])
by_buyer = tr.groupby("to_club").fee_to_mv.agg(["median", "count"]).sort_values("count", ascending=False)
by_year.to_csv(TABLES / "eda_fee_to_mv_by_year.csv")
by_buyer.to_csv(TABLES / "eda_fee_to_mv_by_buyer.csv")
md += ["## Fee / mv(t−1) by buyer (transfers with mv)\n", by_buyer.dropna().round(2).to_markdown(), ""]

# figure: mv trajectory by age, median per position group
fig, ax = plt.subplots(figsize=(7, 4))
grp = pan.assign(g=np.select([pan.position.isin(["FW", "LW", "RW", "AM"]), pan.position.isin(["CM", "DM"])],
                             ["Attackers", "Midfielders"], "Defenders & GK"))
for (name, g), col in zip(grp.groupby("g"), [vs.BLUE, vs.ORANGE, vs.AQUA]):
    m = g.groupby("age").market_value_eur_m.median()
    m = m[g.groupby("age").size() >= 5]
    ax.plot(m.index, m.values, color=col, label=name)
    ax.annotate(name, (m.index[-1], m.values[-1]), xytext=(4, 0), textcoords="offset points", fontsize=8.5, color=vs.INK2,
                va="center")
ax.set_yscale("log")
ax.set_xlabel("Age")
ax.set_ylabel("Median market value (€m, log scale)")
ax.set_title("Market value by age, median per position group")
ax.legend(loc="lower center")
vs.note(fig, "Source: player_market_values.csv (85 players, 2010–2026). Ages with < 5 player-years omitted.")
fig.savefig(FIGS / "eda_age_curve.png")

(DOCS / "results_eda.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
