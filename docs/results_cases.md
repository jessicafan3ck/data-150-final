# Premium and case studies (src/05_cases.py)

Performance-only fee model M1 (`log_fee ~ age + I(age**2) + attacker + year + log_buyer_rev + P`), fit leave-one-out on 37 paid permanent transfers with performance and buyer-revenue data. Residual = unexplained premium in log points (+0.69 ≈ fee double the prediction).

## Does the premium track excess attention?

- 34 transfers also have 12-month Wikipedia pageviews.
- OLS residual premium on excess attention: slope 0.406 [0.107, 0.704], p = 0.008, R² = 0.131.
- Spearman ρ(premium, excess attention) = 0.43 (p = 0.011); ρ(premium, raw attention) = 0.42 (p = 0.013).

## Ranking (largest unexplained premium first)

| Transfer | Fee €m | M1 predicted €m [95% PI] | Premium (log) | Attention pctl | Excess attention pctl |
|---|---|---|---|---|---|
| Neymar 2017 (FC Barcelona → Paris Saint-Germain) | 222 | 83.3 [28.7, 241.3] | +0.98 | 85 | 100 |
| Cristiano Ronaldo 2018 (Real Madrid → Juventus) | 117 | 47.5 [14.8, 152.3] | +0.90 | 100 | 74 |
| Moises Caicedo 2023 (Brighton → Chelsea) | 133 | 65.9 [22.0, 197.6] | +0.70 | 47 | 79 |
| Neymar 2023 (Paris Saint-Germain → Al-Hilal) | 90 | 46.8 [12.4, 175.8] | +0.65 | 94 | 91 |
| Antoine Griezmann 2019 (Atletico Madrid → FC Barcelona) | 120 | 63.9 [21.1, 194.2] | +0.63 | 79 | 82 |
| Harry Kane 2023 (Tottenham → Bayern Munich) | 100 | 55.7 [17.6, 175.6] | +0.59 | 91 | 56 |
| Declan Rice 2023 (West Ham → Arsenal) | 116.6 | 69.2 [22.6, 211.9] | +0.52 | 50 | 47 |
| Romelu Lukaku 2021 (Inter Milan → Chelsea) | 115 | 75.0 [24.9, 226.2] | +0.43 | 74 | 65 |
| Florian Wirtz 2025 (Bayer Leverkusen → Liverpool) | 130 | 86.0 [27.1, 272.3] | +0.41 | 41 | 32 |
| Désiré Doué 2026 (Paris Saint-Germain → Real Madrid) | 90 | 59.5 [18.5, 191.0] | +0.41 | 62 | 94 |
| Kylian Mbappé 2017 (Monaco → Paris Saint-Germain) | 180 | 119.5 [32.9, 434.5] | +0.41 | 68 | 26 |
| Ousmane Dembele 2017 (Borussia Dortmund → FC Barcelona) | 135 | 90.3 [27.9, 292.2] | +0.40 | 38 | 41 |
| Harry Maguire 2019 (Leicester → Manchester United) | 87 | 64.1 [19.8, 207.4] | +0.31 | 29 | 18 |
| Philippe Coutinho 2018 (Liverpool → FC Barcelona) | 135 | 100.4 [33.2, 303.1] | +0.30 | 65 | 53 |
| Hugo Ekitike 2025 (Eintracht Frankfurt → Liverpool) | 95 | 73.9 [23.7, 230.5] | +0.25 | 59 | 62 |
| Romeo Lavia 2023 (Southampton → Chelsea) | 62 | 53.7 [15.9, 182.1] | +0.14 | 26 | 76 |
| Jude Bellingham 2023 (Borussia Dortmund → Real Madrid) | 103 | 89.9 [26.5, 305.1] | +0.14 | 82 | 88 |
| Kepa Arrizabalaga 2018 (Athletic Bilbao → Chelsea) | 80 | 71.3 [22.1, 230.1] | +0.12 | 6 | 9 |
| Dominic Solanke 2024 (Bournemouth → Tottenham) | 65 | 61.3 [19.6, 191.8] | +0.06 | 35 | 15 |
| Jadon Sancho 2021 (Borussia Dortmund → Manchester United) | 85 | 83.1 [27.1, 255.3] | +0.02 | 76 | 85 |
| Manuel Ugarte 2024 (Paris Saint-Germain → Manchester United) | 50.5 | 53.9 [16.6, 175.6] | -0.07 | 18 | 68 |
| Sandro Tonali 2023 (AC Milan → Newcastle United) | 70 | 75.5 [24.3, 234.5] | -0.08 | 12 | 24 |
| Nicolas Pepe 2019 (Lille → Arsenal) | 80 | 89.3 [29.4, 270.9] | -0.11 | 32 | 38 |
| Gonzalo Higuain 2016 (Napoli → Juventus) | 90 | 111.1 [35.7, 346.2] | -0.21 | 56 | 6 |
| Gareth Bale 2013 (Tottenham → Real Madrid) | 100 | 126.1 [38.4, 414.2] | -0.23 |  |  |
| Ruben Neves 2023 (Wolves → Al-Hilal) | 47 | 60.1 [17.0, 212.4] | -0.25 | 21 | 59 |
| Kai Havertz 2020 (Bayer Leverkusen → Chelsea) | 80 | 107.3 [35.3, 325.7] | -0.29 | 44 | 35 |
| Christopher Nkunku 2023 (RB Leipzig → Chelsea) | 60 | 92.3 [30.0, 284.1] | -0.43 | 53 | 29 |
| Paul Pogba 2016 (Juventus → Manchester United) | 105 | 165.2 [47.5, 574.7] | -0.45 | 71 | 71 |
| Mathys Tel 2025 (Bayern Munich → Tottenham) | 50 | 80.3 [24.9, 259.2] | -0.47 | 3 | 3 |
| Aymeric Laporte 2023 (Manchester City → Al-Nassr) | 27.5 | 47.5 [11.6, 194.4] | -0.55 | 24 | 50 |
| James Rodriguez 2014 (Monaco → Real Madrid) | 80 | 140.9 [45.1, 439.9] | -0.57 |  |  |
| Erling Haaland 2022 (Borussia Dortmund → Manchester City) | 60 | 115.0 [38.2, 346.3] | -0.65 | 88 | 97 |
| Riccardo Calafiori 2024 (Bologna → Arsenal) | 42 | 99.7 [32.3, 307.8] | -0.86 | 9 | 12 |
| Luis Suarez 2014 (Liverpool → FC Barcelona) | 82 | 196.6 [60.5, 638.4] | -0.87 |  |  |
| Federico Chiesa 2024 (Juventus → Liverpool) | 12 | 74.3 [26.4, 208.6] | -1.82 | 15 | 44 |
| Cristiano Ronaldo 2021 (Juventus → Manchester United) | 15 | 136.5 [25.0, 746.2] | -2.21 | 97 | 21 |

## Case cards

Rule (brief §6.6): consistent with the allegation only if the fee is above the 95% prediction interval **and** attention is in the top quartile of these transfers.

| Case | Fee €m | Predicted €m [95% PI] | Premium | Attention pctl | Verdict |
|---|---|---|---|---|---|
| Kylian Mbappé 2017 | 180 | 119.5 [32.9, 434.5] | +0.41 | 68 | fee within performance-only range |
| Neymar 2017 | 222 | 83.3 [28.7, 241.3] | +0.98 | 85 | fee within performance-only range |
| Ousmane Dembele 2017 | 135 | 90.3 [27.9, 292.2] | +0.40 | 38 | fee within performance-only range |
| Joao Felix 2019 | | | | | not estimable: no performance data (seller outside top-5 leagues) |
| Jude Bellingham 2023 | 103 | 89.9 [26.5, 305.1] | +0.14 | 82 | fee within performance-only range |
| Désiré Doué 2026 | 90 | 59.5 [18.5, 191.0] | +0.41 | 62 | fee within performance-only range |

Jobe Bellingham is not in any supplied file; his case needs hand-collected fee, performance and attention data.
