"""09_club_impact.py: part 4. If transfer valuation priced attention differently, what happens to club income and value?

Counterfactual fees from the fee model (outcome B, M2): fee_cf = fee * exp(delta_beta * (C_i - C_bar)), where
C = log(1 + monthly Wikipedia views) and C_bar is the mean over the transfer sample. Scenarios:
  S1 performance-only pricing         delta_beta = -beta_B        (fame no longer priced)
  S2 fees price fame like market values  delta_beta = beta_A - beta_B
  S3 fame premium grows by half       delta_beta = +0.5 * beta_B
Club impact: change in a selling club's income as % of its revenue (club_financials.csv), and a generic
sensitivity using UEFA's player-sales-to-revenue ratio. Club value = revenue x multiple (Forbes), so a permanent
income change moves value by the same %; a one-off change moves it by that % / multiple.
Writes outputs/tables/impact_*.csv, outputs/figures/impact_*.png, docs/results_club_impact.md.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

import viz_style as vs
from viz_style import plt

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN, TABLES, FIGS, DOCS = (ROOT / p for p in ("data/raw", "data/clean", "outputs/tables", "outputs/figures",
                                                      "docs"))
LN2 = np.log(2)
SALES_SHARE = 10.3 / 28.6     # UEFA: player sales per euro of operating revenue (see 08_club_context.py)
MULTIPLE = 4.0                # Forbes: most clubs valued below 4x revenue (top-30 average 5.6x)
CLUB_ALIASES = {"Monaco": "AS Monaco"}


def pct(v):
    return f"{v:+.0f}%".replace("-", "−")


# ---------------------------------------------------------------- fee model (same spec as 04_models.py, M2)
tr = pd.read_csv(CLEAN / "transfers.csv")
tr["age"] = tr.age_at_transfer
d = tr.dropna(subset=["log_fee", "P", "log_wiki12", "log_buyer_rev"]).reset_index(drop=True)
mB = smf.ols("log_fee ~ age + I(age**2) + attacker + year + log_buyer_rev + P + log_wiki12", d).fit(
    cov_type="cluster", cov_kwds={"groups": pd.factorize(d.player)[0]})
bB = mB.params["log_wiki12"]
bB_lo, bB_hi = mB.conf_int().loc["log_wiki12"]
bA = pd.read_csv(TABLES / "models_C_summary.csv").set_index("outcome").loc["A", "coef_C"]
c_bar = d.log_wiki12.mean()
d["doublings"] = (d.log_wiki12 - c_bar) / LN2   # attention vs the average transferred player, in doublings

SCEN = {"S1 performance-only pricing": -bB, "S2 fees price fame like market values": bA - bB,
        "S3 fame premium grows by half": 0.5 * bB}

# ---------------------------------------------------------------- transaction-level impact
cf = pd.read_csv(RAW / "club_financials.csv").set_index(["club_name", "year"]).revenue_eur_m
d["seller"] = d.from_club.replace(CLUB_ALIASES)
d["seller_rev"] = [cf.get((c, y), np.nan) for c, y in zip(d.seller, d.year)]
for name, db in SCEN.items():
    k = name.split()[0]
    d[f"fee_{k}"] = d.fee_eur_m * np.exp(db * (d.log_wiki12 - c_bar))
    d[f"dfee_{k}"] = d[f"fee_{k}"] - d.fee_eur_m
    d[f"dfee_pct_rev_{k}"] = d[f"dfee_{k}"] / d.seller_rev * 100
# S1 with the fee coefficient at its CI bounds
for lab, b in (("lo", bB_lo), ("hi", bB_hi)):
    d[f"dfee_S1_{lab}"] = d.fee_eur_m * (np.exp(-b * (d.log_wiki12 - c_bar)) - 1)
cols = ["player", "year", "seller", "to_club", "fee_eur_m", "doublings", "seller_rev",
        "fee_S1", "dfee_S1", "dfee_S1_lo", "dfee_S1_hi", "dfee_pct_rev_S1", "dfee_S2", "dfee_S3"]
tx = d[cols].sort_values("dfee_S1")
tx.to_csv(TABLES / "impact_transfers.csv", index=False)

market = pd.DataFrame([dict(scenario=n, total_fees_actual=d.fee_eur_m.sum(),
                            total_fees_cf=d[f"fee_{n.split()[0]}"].sum()) for n in SCEN])
market["change_pct"] = (market.total_fees_cf / market.total_fees_actual - 1) * 100
market["applied_to_uefa_summer_sales_bn"] = 10.3 * market.change_pct / 100
market.to_csv(TABLES / "impact_market.csv", index=False)

# ---------------------------------------------------------------- generic club sensitivity
grid = []
for share in (0.10, 0.20, SALES_SHARE, 0.50):
    for dbl in (-2, -1, 0, 1, 2):
        for name, db in SCEN.items():
            sales_chg = np.exp(db * dbl * LN2) - 1
            inc = share * sales_chg * 100   # % of operating revenue
            grid.append(dict(scenario=name, sales_share_of_revenue=round(share * 100), sold_players_doublings=dbl,
                             sales_change_pct=sales_chg * 100, income_change_pct_of_revenue=inc,
                             value_change_pct_permanent=inc, value_change_pct_one_off=inc / MULTIPLE))
grid = pd.DataFrame(grid)
grid.to_csv(TABLES / "impact_sensitivity.csv", index=False)

# ---------------------------------------------------------------- report
s1 = market.set_index("scenario").change_pct
g = grid[(grid.scenario.str.startswith("S1")) & (grid.sales_share_of_revenue == round(SALES_SHARE * 100))]
g1 = g.set_index("sold_players_doublings").income_change_pct_of_revenue
show = tx.dropna(subset=["dfee_pct_rev_S1"]).copy()
show = pd.concat([show.head(5), show.tail(3)])
show["fee range (S1, CI)"] = [f"{a:+.0f} to {b:+.0f}" for a, b in zip(show[["dfee_S1_lo", "dfee_S1_hi"]].min(axis=1),
                                                                    show[["dfee_S1_lo", "dfee_S1_hi"]].max(axis=1))]
md = ["# Part 4: what a shift in transfer valuation would do to club income and value", "",
      "Generated by `src/09_club_impact.py`. Counterfactuals reprice each transfer in the fee model's sample "
      f"(N = {len(d)}) by changing only the price of attention; performance, age, position and buyer stay fixed.", "",
      "## Inputs", "",
      f"- Price of attention in fees: β_B = {bB:.3f} (+{(np.exp(bB * LN2) - 1) * 100:.0f}% per doubling, "
      f"95% CI {pct((np.exp(bB_lo * LN2) - 1) * 100)} to {pct((np.exp(bB_hi * LN2) - 1) * 100)}).",
      f"- Price of attention in market values: β_A = {bA:.3f} (+{(np.exp(bA * LN2) - 1) * 100:.0f}% per doubling). "
      "Fees price fame about twice as steeply as market values.",
      f"- Player sales ≈ {SALES_SHARE:.0%} of operating revenue (UEFA: €10.3bn summer-2026 sales vs €28.6bn 2024 "
      "revenue).",
      "- Club value ≈ revenue × a multiple (Forbes: most clubs below 4×, top-30 average 5.6×). A *permanent* "
      "change in income therefore moves club value by the same percentage; a *one-off* change moves it by that "
      "percentage divided by the multiple (4× used). Forbes excludes player trading from the revenue it values, so "
      "the permanent case is an upper bound.", "",
      "## Scenarios", "",
      "| Scenario | What changes | Total fees in sample |",
      "|---|---|---|",
      f"| S1 performance-only pricing | fame stops affecting fees | {pct(s1.iloc[0])} |",
      f"| S2 fees price fame like market values | fame priced at β_A instead of β_B | {pct(s1.iloc[1])} |",
      f"| S3 fame premium grows by half | β_B × 1.5 | {pct(s1.iloc[2])} |", "",
      f"Removing the fame premium barely changes the size of the market ({pct(s1.iloc[0])} of total fees, about "
      f"€{abs(market.applied_to_uefa_summer_sales_bn.iloc[0]):.1f}bn of UEFA's €10.3bn summer-2026 sales). "
      "It mainly **moves money between clubs**: clubs selling famous players receive less, clubs selling "
      "under-the-radar players receive more.", "",
      "## Who gains and who loses (S1, selling clubs in the data)", "",
      show[["player", "year", "seller", "fee_eur_m", "doublings", "dfee_S1", "fee range (S1, CI)",
            "dfee_pct_rev_S1"]].round(1).rename(columns={
                "fee_eur_m": "fee €m", "doublings": "fame vs avg (doublings)", "dfee_S1": "Δ fee €m",
                "dfee_pct_rev_S1": "Δ as % of seller revenue"}).to_markdown(index=False), "",
      "## A typical club (S1, player sales = 36% of revenue)", "",
      "| Sold players' fame vs average | Change in sales income | Change in total income, % of revenue | "
      "Club value change: permanent / one-off |",
      "|---|---|---|---|"]
for dbl, r in g.set_index("sold_players_doublings").iterrows():
    md.append(f"| {dbl:+d} doublings | {pct(r.sales_change_pct)} | {pct(r.income_change_pct_of_revenue)} | "
              f"{pct(r.value_change_pct_permanent)} / {pct(r.value_change_pct_one_off)} |")
md += ["", "Full grid (sales shares 10/20/36/50%, all scenarios) in `outputs/tables/impact_sensitivity.csv`.", ""]
(DOCS / "results_club_impact.md").write_text("\n".join(md) + "\n")
print("\n".join(md))

# ---------------------------------------------------------------- figures
p = tx.dropna(subset=["dfee_S1"]).copy()
p = pd.concat([p.head(6), p.tail(4)]).iloc[::-1]
p["lab"] = [f"{a} → {b}" for a, b in zip(p.player, p.year.astype(int).astype(str))]
fig, ax = plt.subplots(figsize=(7.5, 4.6))
fig.subplots_adjust(top=0.84, left=0.25)
colors = [vs.ORANGE if v < 0 else vs.BLUE for v in p.dfee_S1]
ax.barh(range(len(p)), p.dfee_S1, color=colors, height=0.6)
for i, (v, s) in enumerate(zip(p.dfee_S1, p.seller)):
    ax.text(v + (2 if v >= 0 else -2), i, f"{pct(v)[:-1]}m ({s})", va="center",
            ha="left" if v >= 0 else "right", fontsize=8.5, color=vs.INK)
ax.set_yticks(range(len(p)), [f"{a}, {int(y)}" for a, y in zip(p.player, p.year)])
ax.axvline(0, color=vs.INK2, lw=1)
ax.set_xlim(p.dfee_S1.min() * 3.2, p.dfee_S1.max() * 2.2)
ax.set_xticks([])
ax.grid(False)
ax.spines[["left", "bottom"]].set_visible(False)
ax.tick_params(length=0)
fig.text(0.01, 1.0, "Change in fee if transfers were priced on performance only", fontsize=13, fontweight="bold",
         ha="left", va="bottom")
fig.text(0.01, 0.985, "€ million to the selling club (in brackets). Largest losses and gains in the sample.",
         fontsize=9.5, color=vs.INK2, ha="left", va="top")
fig.savefig(FIGS / "impact_1_transfers.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(7.5, 4))
fig.subplots_adjust(top=0.84)
for share, col in ((50, vs.SEQ_BLUE[6]), (round(SALES_SHARE * 100), vs.SEQ_BLUE[4]), (20, vs.SEQ_BLUE[2]),
                   (10, vs.SEQ_BLUE[1])):
    gg = grid[(grid.scenario.str.startswith("S1")) & (grid.sales_share_of_revenue == share)]
    ax.plot(gg.sold_players_doublings, gg.income_change_pct_of_revenue, color=col, lw=2, marker="o", ms=5)
    ax.text(2.1, gg.income_change_pct_of_revenue.iloc[-1], f"sales = {share}% of revenue", va="center",
            fontsize=8.5, color=vs.INK2)
ax.axhline(0, color=vs.INK2, lw=1)
ax.set_xticks([-2, -1, 0, 1, 2], ["4× less", "2× less", "average", "2× more", "4× more"])
ax.set_xlabel("Fame of the players a club sells (Wikipedia views vs. average transferred player)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: pct(v) if v else "0"))
ax.set_xlim(-2.2, 3.4)
ax.grid(axis="x", visible=False)
ax.spines[["left", "bottom"]].set_visible(False)
ax.tick_params(length=0)
fig.text(0.01, 1.0, "Change in club income if fame stopped being priced, % of revenue", fontsize=13,
         fontweight="bold", ha="left", va="bottom")
fig.text(0.01, 0.985, "By how famous a club's sold players are and how much it relies on player sales",
         fontsize=9.5, color=vs.INK2, ha="left", va="top")
fig.savefig(FIGS / "impact_2_sensitivity.png"); plt.close(fig)
