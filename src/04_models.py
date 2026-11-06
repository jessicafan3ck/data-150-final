"""04_models.py: incremental explanatory power of commercial value C over performance P (brief §6.4-6.5).

Outcomes
  A  log_mv    player-year panel (data/clean/panel.csv)
  B  log_fee   paid permanent transfers (data/clean/transfers.csv)
  C  premium   log(fee) - log(mv_{t-1})
C = log(1 + mean monthly English-Wikipedia pageviews), 12 months before (C6 as sensitivity).
All nested models for an outcome are fit on the same rows. SEs clustered by player.
Writes outputs/tables/*.csv and docs/results_models.md.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.model_selection import GroupKFold

SEED = 150
rng = np.random.default_rng(SEED)
ROOT = Path(__file__).resolve().parents[1]
CLEAN, TABLES, DOCS = ROOT / "data/clean", ROOT / "outputs/tables", ROOT / "docs"
TABLES.mkdir(parents=True, exist_ok=True)
N_BOOT, N_PERM = 1000, 1000
LN2 = np.log(2)
md = []

pan = pd.read_csv(CLEAN / "panel.csv")
tr = pd.read_csv(CLEAN / "transfers.csv")
pan["pos"] = pan.position
tr["pos"] = np.where(tr.attacker == 1, "ATT", "NON")
tr["age"] = tr.age_at_transfer
# English Wikipedia over-weights English-speaking audiences: flag players from English-speaking home markets
ENGLISH = {"England", "Scotland", "Wales", "Northern Ireland", "Republic of Ireland", "United States", "Canada",
           "Australia"}
for d, g in ((pan, "player_name"), (tr, "player")):
    nat = d.groupby(g).nationality.transform(lambda s: s.dropna().iloc[0] if s.notna().any() else None)
    d["english_home"] = nat.isin(ENGLISH).astype(int)


def excess(d, base):
    """Residual of log_wiki12 on performance, controls and home-market language: attention not explained by play.

    english_home is what keeps M2b from being numerically identical to M2 (Frisch-Waugh)."""
    m = smf.ols(f"log_wiki12 ~ P + english_home + {base}", d).fit()
    return m.resid


# ---------------------------------------------------------------- specifications
SPECS = {
    "A": dict(data=pan, y="log_mv", group="player_name",
              m0="age + I(age**2) + C(pos) + C(year) + C(league)",
              perm_strata=["pos", "year"],
              need=["P", "log_wiki12", "wiki_growth", "league"]),
    "B": dict(data=tr, y="log_fee", group="player",
              m0="age + I(age**2) + attacker + year + log_buyer_rev",
              perm_strata=["pos"],
              need=["P", "log_wiki12", "log_buyer_rev"]),
    "C": dict(data=tr, y="premium", group="player",
              m0="age + I(age**2) + attacker + year + log_buyer_rev",
              perm_strata=["pos"],
              need=["P", "log_wiki12", "log_buyer_rev", "premium"]),
}
# panel uses level + growth; transfers (N ~ 20-30) use level only, growth as a sensitivity
C_TERMS = {"A": "log_wiki12 + wiki_growth", "B": "log_wiki12", "C": "log_wiki12"}


def fit(formula, d, group):
    return smf.ols(formula, d).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d[group])[0]})


def oos_rmse(formula, d, group):
    """Grouped-by-player CV RMSE: 5-fold for the panel, leave-one-player-out for transfers."""
    groups = d[group].values
    k = min(5, d[group].nunique()) if len(d) > 100 else d[group].nunique()
    err = np.empty(len(d))
    for tr_i, te_i in GroupKFold(n_splits=k).split(d, groups=groups):
        dtr, dte = d.iloc[tr_i], d.iloc[te_i]
        m = smf.ols(formula, dtr).fit()
        # unseen fixed-effect levels in the test fold: predict with the training mean of the outcome
        try:
            pred = m.predict(dte)
        except Exception:
            pred = pd.Series(np.nan, index=dte.index)
        err[te_i] = (dte[formula.split("~")[0].strip()] - pred.fillna(dtr[formula.split("~")[0].strip()].mean())).values
    return float(np.sqrt(np.mean(err ** 2)))


rows, coefs, oos, perm_rows, imp_rows = [], [], [], [], []
fitted = {}
for out, s in SPECS.items():
    d = s["data"].dropna(subset=[s["y"]] + s["need"]).copy()
    d = d.reset_index(drop=True)
    d["excess_C"] = excess(d, s["m0"])
    ct = C_TERMS[out]
    young_int = "log_wiki12:young + " if d.young.nunique() > 1 else ""
    m3_extra = (f"{young_int}log_wiki12:attacker + log_wiki12:post2017" if out == "A"
                else f"{young_int}log_wiki12:log_buyer_rev")
    forms = {
        "M0": f"{s['y']} ~ {s['m0']}",
        "M1": f"{s['y']} ~ {s['m0']} + P",
        "M2": f"{s['y']} ~ {s['m0']} + P + {ct}",
        "M2b": f"{s['y']} ~ {s['m0']} + P + excess_C",
        "M3": f"{s['y']} ~ {s['m0']} + P + {ct} + {m3_extra}",
    }
    res = {k: fit(f, d, s["group"]) for k, f in forms.items()}
    fitted[out] = (d, forms, res)
    for k, r in res.items():
        rows.append(dict(outcome=out, model=k, n=int(r.nobs), n_players=d[s["group"]].nunique(),
                         r2=r.rsquared, adj_r2=r.rsquared_adj, aic=r.aic))
        for term in r.params.index:
            if term in ("P", "log_wiki12", "wiki_growth", "excess_C") or ":" in term:
                lo, hi = r.conf_int().loc[term]
                coefs.append(dict(outcome=out, model=k, term=term, coef=r.params[term], se=r.bse[term],
                                  ci_lo=lo, ci_hi=hi, p=r.pvalues[term]))
    # nested Wald test for the C block (cluster-robust)
    cterms = [t.strip() for t in ct.split("+")]
    wald = res["M2"].wald_test(" , ".join(f"{t} = 0" for t in cterms), scalar=True)
    r1, r2 = res["M1"], res["M2"]
    partial_r2 = (r1.ssr - r2.ssr) / r1.ssr
    # cluster bootstrap: C coefficient and delta R2
    players = d[s["group"]].unique()
    idx = {p: np.flatnonzero(d[s["group"].strip()].values == p) for p in players}
    bc, bdr = [], []
    for _ in range(N_BOOT):
        take = np.concatenate([idx[p] for p in rng.choice(players, len(players), replace=True)])
        db = d.iloc[take]
        try:
            b1 = smf.ols(forms["M1"], db).fit()
            b2 = smf.ols(forms["M2"], db).fit()
            bc.append(b2.params["log_wiki12"])
            bdr.append(b2.rsquared - b1.rsquared)
        except Exception:
            pass
    # permutation: shuffle the C block within strata, refit M2
    dr_obs = r2.rsquared - r1.rsquared
    perm = []
    for _ in range(N_PERM):
        dp = d.copy()
        shuffled = dp.groupby(s["perm_strata"], group_keys=False).apply(
            lambda g: g[cterms].sample(frac=1, random_state=int(rng.integers(1e9))).set_index(g.index))
        dp[cterms] = shuffled[cterms]
        perm.append(smf.ols(forms["M2"], dp).fit().rsquared - r1.rsquared)
    perm = np.array(perm)
    # Shapley (LMG) split of R2 between P and C on top of controls
    r2c = r1.rsquared - res["M0"].rsquared                       # P alone over M0
    r2cc = fit(f"{s['y']} ~ {s['m0']} + {ct}", d, s["group"]).rsquared - res["M0"].rsquared  # C alone over M0
    r2pc = r2.rsquared - res["M0"].rsquared
    shap_P = 0.5 * (r2c + (r2pc - r2cc))
    shap_C = 0.5 * (r2cc + (r2pc - r2c))
    b = r2.params["log_wiki12"]
    lo, hi = r2.conf_int().loc["log_wiki12"]
    pct = lambda x: 100 * (np.exp(x * LN2) - 1)
    perm_rows.append(dict(
        outcome=out, n=int(r2.nobs), n_players=len(players),
        coef_C=b, pct_per_doubling=pct(b), ci_lo_pct=pct(lo), ci_hi_pct=pct(hi),
        boot_ci_lo_pct=pct(np.percentile(bc, 2.5)), boot_ci_hi_pct=pct(np.percentile(bc, 97.5)),
        delta_r2=dr_obs, boot_dr2_lo=np.percentile(bdr, 2.5), boot_dr2_hi=np.percentile(bdr, 97.5),
        partial_r2_C=partial_r2, wald_F=float(wald.statistic), wald_p=float(wald.pvalue),
        perm_p=float((np.sum(perm >= dr_obs) + 1) / (N_PERM + 1)),
        shapley_P=shap_P, shapley_C=shap_C))
    # out-of-sample
    for k in ("M1", "M2", "M2b"):
        oos.append(dict(outcome=out, model=k, in_sample_rmse=float(np.sqrt(res[k].mse_resid * res[k].df_resid / res[k].nobs)),
                        oos_rmse=oos_rmse(forms[k], d, s["group"])))

summary = pd.DataFrame(perm_rows)
pd.DataFrame(rows).to_csv(TABLES / "models_fit.csv", index=False)
pd.DataFrame(coefs).to_csv(TABLES / "models_coefs.csv", index=False)
summary.to_csv(TABLES / "models_C_summary.csv", index=False)
oos_df = pd.DataFrame(oos)
oos_df.to_csv(TABLES / "models_oos.csv", index=False)

# ---------------------------------------------------------------- sensitivity (§6.4.5)
sens = []
for out, s in SPECS.items():
    d0, forms, _ = fitted[out]
    base = f"{s['y']} ~ {s['m0']}"
    variants = {
        "C12 level only": ("P", "log_wiki12", d0),
        "control English-speaking nationality": ("P + english_home", "log_wiki12", d0),
        "C6 lag": ("P", "log_wiki6", d0.dropna(subset=["log_wiki6"])),
        "P components": ("z_npga90 + z_min_share", "log_wiki12", d0.dropna(subset=["z_npga90", "z_min_share"])),
        "C12 + growth": ("P", "log_wiki12 + wiki_growth", d0.dropna(subset=["wiki_growth"])),
        "no P (C only)": ("1", "log_wiki12", d0),
    }
    for name, (pterm, cterm, dv) in variants.items():
        r = fit(f"{base} + {pterm} + {cterm}", dv, s["group"])
        r1 = fit(f"{base} + {pterm}", dv, s["group"])
        cname = cterm.split(" + ")[0]
        lo, hi = r.conf_int().loc[cname]
        sens.append(dict(outcome=out, variant=name, n=int(r.nobs), coef_C=r.params[cname], ci_lo=lo, ci_hi=hi,
                         p=r.pvalues[cname], delta_r2=r.rsquared - r1.rsquared))
    # static alternative C: number of linked social platforms (file dated Apr 2022)
    dv = d0.dropna(subset=["n_platforms"])
    if len(dv) > 15 and dv.n_platforms.nunique() > 1:
        r = fit(f"{base} + P + n_platforms", dv, s["group"])
        r1 = fit(f"{base} + P", dv, s["group"])
        lo, hi = r.conf_int().loc["n_platforms"]
        sens.append(dict(outcome=out, variant="alt C: n social platforms", n=int(r.nobs), coef_C=r.params["n_platforms"],
                         ci_lo=lo, ci_hi=hi, p=r.pvalues["n_platforms"], delta_r2=r.rsquared - r1.rsquared))
sens = pd.DataFrame(sens)
sens.to_csv(TABLES / "models_sensitivity.csv", index=False)

# ---------------------------------------------------------------- stress tests (§6.5)
stress = []
dA, formsA, resA = fitted["A"]
# player fixed effects: within-player variation (linear age is absorbed by player FE + year FE)
fe = fit("log_mv ~ I(age**2) + P + log_wiki12 + wiki_growth + C(year) + C(player_name)", dA, "player_name")
lo, hi = fe.conf_int().loc["log_wiki12"]
stress.append(dict(test="A: player fixed effects", n=int(fe.nobs), coef_C=fe.params["log_wiki12"], ci_lo=lo, ci_hi=hi,
                   p=fe.pvalues["log_wiki12"]))
# first differences: Δlog_mv on ΔP and lagged C (C_{t-1}) and ΔC
dd = dA.sort_values(["player_name", "year"]).copy()
g = dd.groupby("player_name")
dd["d_log_mv"] = g.log_mv.diff()
dd["d_P"] = g.P.diff()
dd["C_lag"] = dd.log_wiki12_prev
dd["d_C"] = dd.log_wiki12 - dd.log_wiki12_prev
dd = dd[g.year.diff().eq(1)].dropna(subset=["d_log_mv", "d_P", "C_lag", "d_C"])
fd = fit("d_log_mv ~ d_P + C_lag + d_C + age + I(age**2) + C(year)", dd, "player_name")
for t in ("C_lag", "d_C"):
    lo, hi = fd.conf_int().loc[t]
    stress.append(dict(test=f"A: first differences, {t}", n=int(fd.nobs), coef_C=fd.params[t], ci_lo=lo, ci_hi=hi,
                       p=fd.pvalues[t]))
# drop the 5 most influential observations (Cook's distance) from M2, each outcome
for out in ("A", "B"):  # premium model (N = 14) would be left with 9 rows
    d, forms, res = fitted[out]
    ols = smf.ols(forms["M2"], d).fit()
    cooks = ols.get_influence().cooks_distance[0]
    keep = np.argsort(cooks)[:-5]
    r = fit(forms["M2"], d.iloc[keep], SPECS[out]["group"])
    lo, hi = r.conf_int().loc["log_wiki12"]
    dropped = d.iloc[np.argsort(cooks)[-5:]]
    lab = (dropped.player_name + " " + dropped.year.astype(str)) if out == "A" else (dropped.player + " " + dropped.year.astype(str))
    stress.append(dict(test=f"{out}: drop top-5 Cook's D ({'; '.join(lab)})", n=int(r.nobs), coef_C=r.params["log_wiki12"],
                       ci_lo=lo, ci_hi=hi, p=r.pvalues["log_wiki12"]))
# matched comparison (panel): high vs low excess attention, same year and position, age ±1, nearest P
hi_g = dA[dA.excess_C >= dA.excess_C.quantile(2 / 3)]
lo_g = dA[dA.excess_C <= dA.excess_C.quantile(1 / 3)]
pairs = []
for r in hi_g.itertuples():
    c = lo_g[(lo_g.year == r.year) & (lo_g.pos == r.pos) & ((lo_g.age - r.age).abs() <= 1) &
             (lo_g.player_name != r.player_name)]
    c = c[(c.P - r.P).abs() <= 0.25]
    if len(c):
        m = c.loc[(c.P - r.P).abs().idxmin()]
        pairs.append((r.log_mv - m.log_mv, r.log_wiki12 - m.log_wiki12, r.player_name, m.player_name))
pairs = pd.DataFrame(pairs, columns=["d_log_mv", "d_C", "treated", "control"])
pairs.to_csv(TABLES / "stress_matched_pairs.csv", index=False)
if len(pairs) >= 5:
    boots = [pairs.d_log_mv.sample(frac=1, replace=True, random_state=i).mean() for i in range(N_BOOT)]
    stress.append(dict(test=f"A: matched pairs high vs low excess C ({len(pairs)} pairs; coef = mean Δlog mv)",
                       n=len(pairs), coef_C=pairs.d_log_mv.mean(), ci_lo=np.percentile(boots, 2.5),
                       ci_hi=np.percentile(boots, 97.5), p=np.nan))
stress = pd.DataFrame(stress)
stress.to_csv(TABLES / "stress_tests.csv", index=False)

# ---------------------------------------------------------------- write-up
f = lambda x, n=2: "" if pd.isna(x) else f"{x:.{n}f}"
md.append("# Model results (src/04_models.py)\n")
md.append("C = log(1 + mean monthly English-Wikipedia pageviews over the 12 months before valuation/transfer). "
          "P = position-specific performance composite (z-scores vs all top-5-league players in that season). "
          "SEs clustered by player; bootstrap resamples players. Effects are associations, not causal.\n")
md.append("## Headline: incremental power of C over P (M2 vs M1)\n")
md.append("| Outcome | N (players) | % change per doubling of pageviews [95% CI] | bootstrap CI | ΔR² [boot CI] | partial R² | Wald p | perm. p | Shapley P / C |")
md.append("|---|---|---|---|---|---|---|---|---|")
for r in summary.itertuples():
    md.append(f"| {r.outcome} | {r.n} ({r.n_players}) | {f(r.pct_per_doubling, 1)}% [{f(r.ci_lo_pct, 1)}, {f(r.ci_hi_pct, 1)}] | "
              f"[{f(r.boot_ci_lo_pct, 1)}, {f(r.boot_ci_hi_pct, 1)}] | {f(r.delta_r2, 3)} [{f(r.boot_dr2_lo, 3)}, {f(r.boot_dr2_hi, 3)}] | "
              f"{f(r.partial_r2_C, 3)} | {f(r.wald_p, 3)} | {f(r.perm_p, 3)} | {f(r.shapley_P, 3)} / {f(r.shapley_C, 3)} |")
md.append("\n## Fit by model\n")
md.append(pd.DataFrame(rows).pivot(index="model", columns="outcome", values="r2").round(3).to_markdown())
md.append("\n## Out-of-sample RMSE (grouped by player)\n")
md.append(oos_df.pivot(index="model", columns="outcome", values="oos_rmse").round(3).to_markdown())
md.append("\n## Interactions (M3)\n")
cd = pd.DataFrame(coefs)
md.append(cd[(cd.model == "M3") & cd.term.str.contains(":")][["outcome", "term", "coef", "ci_lo", "ci_hi", "p"]]
          .round(3).to_markdown(index=False))
md.append("\n## Excess attention (M2b)\n")
md.append(cd[(cd.model == "M2b") & (cd.term == "excess_C")][["outcome", "coef", "ci_lo", "ci_hi", "p"]].round(3).to_markdown(index=False))
md.append("\n## Sensitivity\n")
md.append(sens.round(3).to_markdown(index=False))
md.append("\n## Stress tests\n")
md.append(stress.round(3).to_markdown(index=False))
(DOCS / "results_models.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
