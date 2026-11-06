# Results summary: does commercial value move transfer value beyond performance?

All numbers are from `src/02`–`06` (details in `results_models.md`, `results_cases.md`; figures in `outputs/figures/`).
Results describe association, not causation: attention and performance feed each other.

**Measures.** Commercial proxy C = mean monthly English-Wikipedia pageviews in the 12 months before the valuation or
transfer (article + redirects). Performance P = position-specific composite from FootyStats season data, scored
against all top-5-league players in that season. Controls: age, age², position, year, league (panel); buyer revenue (transfers).

## Headline (M2 vs M1: does C add to a performance-only model?)

| Outcome | N | Per doubling of attention [95% CI] | ΔR² [bootstrap CI] | Permutation p | Out-of-sample RMSE M1 → M2 |
|---|---|---|---|---|---|
| A: log market value (panel) | 531 player-years, 83 players | **+12.5%** [+3.0, +22.9] | 0.020 [0.003, 0.051] | 0.002 | 0.900 → 0.876 |
| B: log fee | 34 transfers | **+25.1%** [+5.7, +48.1] | 0.113 [0.003, 0.276] | 0.016 | 0.664 → 0.585 |
| C: premium = log(fee / mv(t−1)) | 15 transfers | −4.6% [−48, +76] | 0.002 | 0.88 | 1.73 → 2.00 |

- **H0 is rejected for A and B.** Holding performance fixed, players with more attention carry higher market values and fees, and adding attention improves out-of-sample prediction for both.
- **Outcome C: not detectable.** With 15 transfers the interval spans −48% to +76%, so this is not evidence of no effect.
- **Robustness (A and B).** The result holds with a 6-month window instead of 12, with the performance components entered separately instead of the composite, with a control for English-speaking nationality, and after dropping the 5 most influential observations.
- **Within-player (A).** With player fixed effects the estimate falls to +8.6% [−0.6, +18.6], p = 0.07. First differences (does a change in attention predict a change in value?) show nothing detectable. Much of the association is therefore between players (who is famous), not changes within a player over time.
- **H2 heterogeneity is not supported.** In the panel the attention effect is *smaller* for players aged 21 or under, for attackers, and after 2017. For fees no interaction is detectable.
- **Alternative proxy.** The number of linked social platforms (static, 2022) shows no association with fees.

## Premium and case studies (leave-one-out, performance-only fee model, 37 transfers)

- Unexplained premium tracks excess attention (attention not explained by performance): Spearman ρ = 0.43 (p = 0.011, N = 34); slope 0.41 [0.11, 0.70].
- Largest premiums: Neymar 2017 (+0.98 log points, fee ≈ 2.7× prediction), Ronaldo 2018, Caicedo 2023, Neymar 2023, Griezmann 2019, Kane 2023.
- Named cases under the brief's rule (fee above the 95% prediction interval **and** attention in the top quartile): **none qualify**. Every case falls inside its interval, because the intervals are wide at this sample size. Neymar 2017 comes closest (€222m vs an upper bound of €241m; attention 85th percentile). João Félix 2019 cannot be estimated (Benfica is outside the performance data); Jobe Bellingham is not in any supplied file.

## Caveats

- The supplied market values and fees are used as given (see `data_audit.md` for their properties).
- English Wikipedia reflects English-language attention. The English-speaking-nationality control leaves the estimates unchanged.
- The transfer sample is a curated high-fee list (median fee €87m), so slopes may be attenuated.
- Performance covers top-5 leagues only, so 9 of 47 paid transfers drop out (sellers elsewhere).
