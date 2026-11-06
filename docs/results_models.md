# Model results (src/04_models.py)

C = log(1 + mean monthly English-Wikipedia pageviews over the 12 months before valuation/transfer). P = position-specific performance composite (z-scores vs all top-5-league players in that season). SEs clustered by player; bootstrap resamples players. Effects are associations, not causal.

## Headline: incremental power of C over P (M2 vs M1)

| Outcome | N (players) | % change per doubling of pageviews [95% CI] | bootstrap CI | ΔR² [boot CI] | partial R² | Wald p | perm. p | Shapley P / C |
|---|---|---|---|---|---|---|---|---|
| A | 531 (83) | 12.5% [3.0, 22.9] | [4.3, 27.8] | 0.020 [0.003, 0.051] | 0.046 | 0.011 | 0.002 | 0.043 / 0.040 |
| B | 34 (32) | 25.1% [5.7, 48.1] | [3.4, 54.8] | 0.113 [0.003, 0.276] | 0.209 | 0.009 | 0.016 | 0.064 / 0.160 |
| C | 15 (13) | -4.6% [-48.3, 76.2] | [-86.1, 1051.3] | 0.002 [0.000, 0.250] | 0.004 | 0.882 | 0.884 | 0.002 / 0.001 |

## Fit by model

| model   |     A |     B |     C |
|:--------|------:|------:|------:|
| M0      | 0.495 | 0.351 | 0.526 |
| M1      | 0.558 | 0.462 | 0.527 |
| M2      | 0.579 | 0.575 | 0.529 |
| M2b     | 0.579 | 0.551 | 0.53  |
| M3      | 0.607 | 0.592 | 0.533 |

## Out-of-sample RMSE (grouped by player)

| model   |     A |     B |     C |
|:--------|------:|------:|------:|
| M1      | 0.9   | 0.664 | 1.732 |
| M2      | 0.876 | 0.585 | 1.996 |
| M2b     | 0.871 | 0.62  | 2.011 |

## Interactions (M3)

| outcome   | term                     |   coef |   ci_lo |   ci_hi |     p |
|:----------|:-------------------------|-------:|--------:|--------:|------:|
| A         | log_wiki12:young         | -0.047 |  -0.074 |  -0.021 | 0     |
| A         | log_wiki12:attacker      | -0.215 |  -0.374 |  -0.057 | 0.008 |
| A         | log_wiki12:post2017      | -0.198 |  -0.335 |  -0.061 | 0.005 |
| B         | log_wiki12:young         | -0.029 |  -0.105 |   0.048 | 0.46  |
| B         | log_wiki12:log_buyer_rev | -0.061 |  -0.213 |   0.09  | 0.428 |
| C         | log_wiki12:young         | -0.03  |  -0.262 |   0.201 | 0.797 |
| C         | log_wiki12:log_buyer_rev |  0.083 |  -2.184 |   2.35  | 0.943 |

## Excess attention (M2b)

| outcome   |   coef |   ci_lo |   ci_hi |     p |
|:----------|-------:|--------:|--------:|------:|
| A         |  0.175 |   0.04  |   0.309 | 0.011 |
| B         |  0.301 |   0.04  |   0.561 | 0.024 |
| C         | -0.087 |  -0.991 |   0.817 | 0.851 |

## Sensitivity

| outcome   | variant                              |   n |   coef_C |   ci_lo |   ci_hi |     p |   delta_r2 |
|:----------|:-------------------------------------|----:|---------:|--------:|--------:|------:|-----------:|
| A         | C12 level only                       | 531 |    0.17  |   0.041 |   0.299 | 0.01  |      0.02  |
| A         | control English-speaking nationality | 531 |    0.175 |   0.04  |   0.31  | 0.011 |      0.021 |
| A         | C6 lag                               | 531 |    0.162 |   0.031 |   0.293 | 0.015 |      0.018 |
| A         | P components                         | 493 |    0.369 |   0.214 |   0.523 | 0     |      0.045 |
| A         | C12 + growth                         | 531 |    0.17  |   0.042 |   0.298 | 0.009 |      0.02  |
| A         | no P (C only)                        | 531 |    0.257 |   0.125 |   0.389 | 0     |      0.059 |
| A         | alt C: n social platforms            | 409 |   -0.231 |  -0.459 |  -0.003 | 0.047 |      0.011 |
| B         | C12 level only                       |  34 |    0.324 |   0.08  |   0.567 | 0.009 |      0.113 |
| B         | control English-speaking nationality |  34 |    0.301 |   0.034 |   0.567 | 0.027 |      0.088 |
| B         | C6 lag                               |  34 |    0.211 |   0.012 |   0.409 | 0.037 |      0.049 |
| B         | P components                         |  34 |    0.319 |   0.048 |   0.591 | 0.021 |      0.111 |
| B         | C12 + growth                         |  32 |    0.32  |   0.026 |   0.614 | 0.033 |      0.098 |
| B         | no P (C only)                        |  34 |    0.384 |   0.108 |   0.659 | 0.006 |      0.207 |
| B         | alt C: n social platforms            |  27 |    0.017 |  -0.345 |   0.379 | 0.926 |      0     |
| C         | C12 level only                       |  15 |   -0.067 |  -0.952 |   0.817 | 0.882 |      0.002 |
| C         | control English-speaking nationality |  15 |   -0.087 |  -1.074 |   0.901 | 0.864 |      0.003 |
| C         | C6 lag                               |  15 |    0.04  |  -0.939 |   1.019 | 0.936 |      0     |
| C         | P components                         |  15 |   -0.086 |  -1.103 |   0.932 | 0.869 |      0.002 |
| C         | C12 + growth                         |  15 |   -0.321 |  -0.761 |   0.119 | 0.153 |      0.308 |
| C         | no P (C only)                        |  15 |   -0.029 |  -0.828 |   0.769 | 0.943 |      0     |

## Stress tests

| test                                                                                                                                |   n |   coef_C |   ci_lo |   ci_hi |       p |
|:------------------------------------------------------------------------------------------------------------------------------------|----:|---------:|--------:|--------:|--------:|
| A: player fixed effects                                                                                                             | 531 |    0.119 |  -0.009 |   0.246 |   0.069 |
| A: first differences, C_lag                                                                                                         | 445 |   -0.038 |  -0.079 |   0.003 |   0.069 |
| A: first differences, d_C                                                                                                           | 445 |   -0.038 |  -0.089 |   0.012 |   0.138 |
| A: drop top-5 Cook's D (Achraf Hakimi 2018; Lamine Yamal 2023; Rodri 2025; Cole Palmer 2020; Désiré Doué 2022)                      | 526 |    0.254 |   0.149 |   0.36  |   0     |
| B: drop top-5 Cook's D (Cristiano Ronaldo 2018; Erling Haaland 2022; Paul Pogba 2016; Federico Chiesa 2024; Cristiano Ronaldo 2021) |  29 |    0.322 |   0.134 |   0.511 |   0.001 |
| A: matched pairs high vs low excess C (10 pairs; coef = mean Δlog mv)                                                               |  10 |    0.205 |  -0.7   |   0.913 | nan     |
