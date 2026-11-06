# Decisions log

Each judgement call, dated, with the reason.

| Date | Decision | Reason |
|---|---|---|
| 2026-10-24 | Raw files copied to `data/raw/` and set read-only. | Brief §2, §7. |
| 2026-10-24 | Name key = accent-stripped, lowercase, letters only (ø→o etc.); "extension"/"loan" suffixes removed. | Brief finding 6. |
| 2026-10-24 | Social links classified by URL domain, not header. | Instagram/Facebook headers are swapped. |
| 2026-10-25 | **Group decision: test the brief's question on the supplied files as given**; the audit (`data_audit.md`) is documentation, not a gate. | User instruction. |
| 2026-10-25 | `transfers_history.csv` not used: it cannot be linked to any player in the other files. | No shared players (1 name, wrong ages). |
| 2026-10-25 | Saka duplicate player-years averaged (10 rows). | Keeps the player; gap small relative to cross-player spread. |
| 2026-10-25 | Performance P from FootyStats season exports in `/Users/jessicafan/data/*stats/` (top-5 leagues, 2009/10–2024/25). Matched by name **and** birth year ±1. | Only source on disk covering all seasons. |
| 2026-10-25 | P uses only stats filled in every season: non-penalty goals + assists per 90, minutes share, clean sheets per 90, goals conceded per 90. xG/xA, tackles, ratings exist only from 2020/21 and are not used. | Consistent definition 2010–2025. |
| 2026-10-25 | P = fixed-weight composite of within-season, within-position z-scores (reference: all top-5-league players with ≥ 900 min). FW (2·output + minutes)/3; MF (output + minutes)/2; DF (minutes + CS − conceded + 0.5·output)/3.5; GK (minutes + CS − conceded)/3. Rates need ≥ 450 min, otherwise P = minutes z-score. League FE in the panel models are the league-strength adjustment. | Brief §3. |
| 2026-10-25 | Players outside the top-5 leagues have no P and drop from the models (e.g. João Félix 2019 from Benfica). | No data. |
| 2026-10-25 | **Commercial proxy C = English-Wikipedia monthly pageviews** (Wikimedia API, user agent, article + all redirects + pre-move base title). The social file has no follower counts. Number of linked social platforms (static, 2022) used as an alternative C. | Brief §3 lists pageviews as a time-varying commercial proxy. |
| 2026-10-25 | Months before an article existed count as 0 views; windows starting before Jul 2015 are missing. | Pageview API starts Jul 2015. |
| 2026-10-25 | Timing: valuation in year t treated as June of t. Panel: P = season ending in t; C12 = Jul(t−1)–Jun(t); C6 = Jan–Jun(t). Transfers: P = last full season before the date; C12/C6 = 12/6 months before the transfer month. Pre-transfer value = mv(t−1). | Brief finding 7. |
| 2026-10-25 | Excess attention = residual of C on P, controls and an English-speaking-nationality flag. | English Wikipedia over-weights English-speaking audiences; without the extra regressor M2b is algebraically identical to M2. |
| 2026-10-25 | Transfer models: controls age, age², attacker, year (linear), log buyer revenue (t−1). No year FE, because N ≈ 33. | Degrees of freedom. |
| 2026-10-25 | Jobe Bellingham not included. | Not in any supplied file; needs hand-collected data. |
| 2026-11-06 | **Scope extended to five parts**: context (club finances, price of attention over time), disparity models, case studies, club-level impact of a valuation shift, recommendation. | Group's revised project plan. |
| 2026-11-06 | Gross player sales taken from UEFA published aggregates, not `transfers_history.csv`. Central ratio: player sales ≈ 36% of operating revenue (€10.3bn summer-2026 sales / €28.6bn 2024 revenue), with a 10–50% sensitivity range. | `transfers_history.csv` implies the median club sells ~2× its revenue a year, which does not fit `club_financials.csv`. Group chose published reports. The two UEFA figures come from different years and the sales figure covers one window only. |
| 2026-11-06 | Club value = revenue × Forbes multiple (most clubs < 4×, top-30 average 5.6×). Permanent income changes move value by the same %; one-off changes by that % / 4. | Group chose a revenue multiple. Forbes excludes player trading from the revenue it values, so the permanent case is an upper bound. |
| 2026-11-06 | Valuation-shift scenarios reprice fees by changing only the attention coefficient, centred on the sample-mean attention: S1 β=0 (performance only), S2 β_B→β_A (fees price fame like market values), S3 β_B×1.5. | Holds performance, age, position and buyer fixed; centring makes the average-attention player's fee unchanged. |
| 2026-11-06 | Price of attention over time estimated in the market-value panel only (period × attention interaction). | The fee sample (34) is too small to split by period. |
