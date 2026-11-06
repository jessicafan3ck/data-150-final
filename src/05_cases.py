"""05_cases.py: unexplained premium and case studies (brief §6.6).

Fits M1 (performance-only fee model, outcome B) leave-one-out: each transfer is predicted by a model that never
saw it. Residual = log fee - predicted log fee ("unexplained premium"). Then asks whether the premium lines up
with excess attention (Wikipedia pageviews not explained by performance and controls).
Writes outputs/tables/cases_premium_ranking.csv, cases_cards.csv and docs/results_cases.md.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
CLEAN, TABLES, DOCS = ROOT / "data/clean", ROOT / "outputs/tables", ROOT / "docs"
M0 = "age + I(age**2) + attacker + year + log_buyer_rev"
M1 = f"log_fee ~ {M0} + P"
CASES = [("Kylian Mbappé", 2017), ("Neymar", 2017), ("Ousmane Dembele", 2017), ("Joao Felix", 2019),
         ("Jude Bellingham", 2023), ("Désiré Doué", 2026)]

tr = pd.read_csv(CLEAN / "transfers.csv")
tr["age"] = tr.age_at_transfer
ENGLISH = {"England", "Scotland", "Wales", "Northern Ireland", "Republic of Ireland", "United States", "Canada",
           "Australia"}
nat = tr.groupby("player").nationality.transform(lambda s: s.dropna().iloc[0] if s.notna().any() else None)
tr["english_home"] = nat.isin(ENGLISH).astype(int)
d = tr.dropna(subset=["log_fee", "P", "log_buyer_rev"]).reset_index(drop=True)

# leave-one-out predictions with 95% prediction intervals
pred, lo, hi, pctl = [], [], [], []
for i in range(len(d)):
    m = smf.ols(M1, d.drop(index=i)).fit()
    sf = m.get_prediction(d.iloc[[i]]).summary_frame(alpha=0.05)
    pred.append(sf["mean"].iloc[0]); lo.append(sf["obs_ci_lower"].iloc[0]); hi.append(sf["obs_ci_upper"].iloc[0])
    se_obs = (sf["obs_ci_upper"].iloc[0] - sf["mean"].iloc[0]) / stats.t.ppf(0.975, m.df_resid)
    pctl.append(stats.t.cdf((d.log_fee.iloc[i] - sf["mean"].iloc[0]) / se_obs, m.df_resid))
d["pred_log_fee"], d["pi_lo"], d["pi_hi"], d["premium_pctl"] = pred, lo, hi, pctl
d["resid_premium"] = d.log_fee - d.pred_log_fee
d["pred_fee_eur_m"] = np.exp(d.pred_log_fee)
d["pred_fee_lo"], d["pred_fee_hi"] = np.exp(d.pi_lo), np.exp(d.pi_hi)

# excess attention among transfers that have C
c = d.dropna(subset=["log_wiki12"]).copy()
c["excess_C"] = smf.ols(f"log_wiki12 ~ P + english_home + {M0}", c).fit().resid
d = d.merge(c[["transfer_id", "excess_C"]], on="transfer_id", how="left")
d["wiki12_pctl"] = d.log_wiki12.rank(pct=True)
d["excess_pctl"] = d.excess_C.rank(pct=True)
rank = d.sort_values("resid_premium", ascending=False)[
    ["player", "year", "from_club", "to_club", "fee_eur_m", "pred_fee_eur_m", "pred_fee_lo", "pred_fee_hi",
     "resid_premium", "premium_pctl", "wiki12", "wiki12_pctl", "excess_C", "excess_pctl", "P"]]
rank.to_csv(TABLES / "cases_premium_ranking.csv", index=False)

cc = d.dropna(subset=["excess_C"])
reg = smf.ols("resid_premium ~ excess_C", cc).fit(cov_type="HC1")
rho, rho_p = stats.spearmanr(cc.resid_premium, cc.excess_C)
rho_raw, rho_raw_p = stats.spearmanr(cc.resid_premium, cc.log_wiki12)

cards = []
for name, yr in CASES:
    r = d[(d.player == name) & (d.year == yr)]
    if r.empty:
        why = tr[(tr.player == name) & (tr.year == yr)]
        reason = ("not in record_transfers" if why.empty else
                  "no performance data (seller outside top-5 leagues)" if why.P.isna().all() else
                  "buyer not in club_financials" if why.log_buyer_rev.isna().all() else "missing")
        cards.append(dict(player=name, year=yr, status=f"not estimable: {reason}"))
        continue
    r = r.iloc[0]
    above = r.log_fee > r.pi_hi
    high_c = (r.wiki12_pctl >= 0.75) if pd.notna(r.wiki12_pctl) else None
    verdict = ("consistent with allegation" if above and high_c else
               "fee above performance-only range, attention not high" if above else
               "fee within performance-only range")
    cards.append(dict(player=name, year=yr, status="estimated", fee_eur_m=r.fee_eur_m,
                      pred_fee_eur_m=r.pred_fee_eur_m, pi_lo=r.pred_fee_lo, pi_hi=r.pred_fee_hi,
                      resid_premium=r.resid_premium, premium_pctl=r.premium_pctl,
                      wiki12=r.wiki12, wiki12_pctl=r.wiki12_pctl, excess_pctl=r.excess_pctl, verdict=verdict))
cards = pd.DataFrame(cards)
cards.to_csv(TABLES / "cases_cards.csv", index=False)

f = lambda x, n=1: "" if pd.isna(x) else f"{x:.{n}f}"
md = ["# Premium and case studies (src/05_cases.py)\n",
      f"Performance-only fee model M1 (`{M1}`), fit leave-one-out on {len(d)} paid permanent transfers with performance "
      "and buyer-revenue data. Residual = unexplained premium in log points (+0.69 ≈ fee double the prediction).\n",
      "## Does the premium track excess attention?\n",
      f"- {len(cc)} transfers also have 12-month Wikipedia pageviews.",
      f"- OLS residual premium on excess attention: slope {reg.params['excess_C']:.3f} "
      f"[{reg.conf_int().loc['excess_C', 0]:.3f}, {reg.conf_int().loc['excess_C', 1]:.3f}], p = {reg.pvalues['excess_C']:.3f}, R² = {reg.rsquared:.3f}.",
      f"- Spearman ρ(premium, excess attention) = {rho:.2f} (p = {rho_p:.3f}); ρ(premium, raw attention) = {rho_raw:.2f} (p = {rho_raw_p:.3f}).\n",
      "## Ranking (largest unexplained premium first)\n",
      "| Transfer | Fee €m | M1 predicted €m [95% PI] | Premium (log) | Attention pctl | Excess attention pctl |",
      "|---|---|---|---|---|---|"]
for r in rank.itertuples():
    md.append(f"| {r.player} {r.year} ({r.from_club} → {r.to_club}) | {r.fee_eur_m:g} | {f(r.pred_fee_eur_m)} "
              f"[{f(r.pred_fee_lo)}, {f(r.pred_fee_hi)}] | {r.resid_premium:+.2f} | {f(100 * r.wiki12_pctl, 0)} | {f(100 * r.excess_pctl, 0)} |")
md += ["\n## Case cards\n",
       "Rule (brief §6.6): consistent with the allegation only if the fee is above the 95% prediction interval "
       "**and** attention is in the top quartile of these transfers.\n",
       "| Case | Fee €m | Predicted €m [95% PI] | Premium | Attention pctl | Verdict |", "|---|---|---|---|---|---|"]
for r in cards.itertuples():
    if r.status != "estimated":
        md.append(f"| {r.player} {r.year} | | | | | {r.status} |")
    else:
        md.append(f"| {r.player} {r.year} | {r.fee_eur_m:g} | {f(r.pred_fee_eur_m)} [{f(r.pi_lo)}, {f(r.pi_hi)}] | "
                  f"{r.resid_premium:+.2f} | {f(100 * r.wiki12_pctl, 0)} | {r.verdict} |")
md.append("\nJobe Bellingham is not in any supplied file; his case needs hand-collected fee, performance and attention data.")
(DOCS / "results_cases.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
