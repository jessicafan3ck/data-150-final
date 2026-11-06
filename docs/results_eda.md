# Exploratory analysis (src/03_eda.py)

## Distributions

|                                  |   count |      mean |       std |      min |      25% |      50% |       75% |           max |
|:---------------------------------|--------:|----------:|----------:|---------:|---------:|---------:|----------:|--------------:|
| mv_eur_m (panel)                 |    1015 |     40.34 |     39.8  |     0.9  |     6.35 |    28.3  |     63.45 | 227.1         |
| wiki12 monthly views (panel)     |     785 | 111640    | 172743    |     0    | 26942.6  | 65559.4  | 134888    |   2.24757e+06 |
| fee_eur_m (transfers)            |      47 |     88.9  |     39.27 |    12    |    63.5  |    87    |    110    | 222           |
| wiki12 monthly views (transfers) |      43 | 186083    | 268721    | 14296.4  | 50135.8  | 90111    | 220780    |   1.26006e+06 |
| premium log(fee/mv_t-1)          |      18 |      0.59 |      0.89 |    -0.43 |    -0.06 |     0.41 |      0.9  |   3.05        |

## Correlations (panel, rows with P and C)

|             |   log_mv |     P |   log_wiki12 |   wiki_growth |   age |
|:------------|---------:|------:|-------------:|--------------:|------:|
| log_mv      |     1    |  0.18 |         0.1  |          0    | -0.48 |
| P           |     0.18 |  1    |         0.57 |         -0.38 |  0.38 |
| log_wiki12  |     0.1  |  0.57 |         1    |         -0.29 |  0.44 |
| wiki_growth |     0    | -0.38 |        -0.29 |          1    | -0.42 |
| age         |    -0.48 |  0.38 |         0.44 |         -0.42 |  1    |

## Correlations (transfers)

|                 |   log_fee |   premium |     P |   log_wiki12 |   age_at_transfer |   log_buyer_rev |
|:----------------|----------:|----------:|------:|-------------:|------------------:|----------------:|
| log_fee         |      1    |      0.16 | -0.08 |        -0.19 |             -0.38 |           -0.01 |
| premium         |      0.16 |      1    |  0.46 |         0.32 |              0.23 |           -0.49 |
| P               |     -0.08 |      0.46 |  1    |         0.41 |              0.26 |           -0.46 |
| log_wiki12      |     -0.19 |      0.32 |  0.41 |         1    |              0.76 |           -0.37 |
| age_at_transfer |     -0.38 |      0.23 |  0.26 |         0.76 |              1    |           -0.44 |
| log_buyer_rev   |     -0.01 |     -0.49 | -0.46 |        -0.37 |             -0.44 |            1    |

VIF (panel): P 1.56, log_wiki12 1.63, age 1.30

## Fee / mv(t−1) by buyer (transfers with mv)

| to_club             |   median |   count |
|:--------------------|---------:|--------:|
| Paris Saint-Germain |     1.67 |       3 |
| Chelsea             |     1.45 |       2 |
| FC Barcelona        |     1.09 |       2 |
| Juventus            |     3.3  |       2 |
| Real Madrid         |     1.13 |       2 |
| Al-Hilal            |     7.32 |       1 |
| Arsenal             |     1.42 |       1 |
| Bayern Munich       |     3.33 |       1 |
| Liverpool           |     1    |       1 |
| Manchester City     |     0.65 |       1 |
| Manchester United   |     2.5  |       1 |
| Tottenham           |     0.93 |       1 |

