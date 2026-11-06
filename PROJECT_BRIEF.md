# Project Brief: Does Commercial Value Move Transfer Value Beyond Performance?

*DATA 150 group project. Written so Claude Code can pick it up cold. Treat this file as the project's CLAUDE.md.*

---

## 1. Project description

**Core question.** Does a player's commercial valuation explain his transfer valuation *beyond what his on-pitch performance explains*? Equivalently: are the "PR allegations" (that some players are priced partly on brand, not just output) supported by the data?

**Plain-language framing.** Build the best performance-only model of transfer value. Then ask whether adding a commercial proxy (social media following before the move) improves it, by how much, and for whom. Finally, find the players whose price sits well above what performance predicts, and test whether commercial reach explains that premium.

**Hypotheses**
- **H0:** After controlling for performance, age, position, buyer and market conditions, commercial proxies have no association with transfer value.
- **H1:** Commercial proxies have a positive, statistically and economically meaningful association with transfer value after those controls.
- **H2 (heterogeneity):** The effect is larger for young players, attackers, and buyers with large commercial revenue (e.g. Real Madrid, PSG), and after about 2017.

**Honest framing of the claim.** Followers and performance feed each other (good players gain followers), so this project can show *incremental predictive association*, not clean causation. Every result must be worded that way unless an identification strategy in §6.5 supports more.

**Case-study layer.** After the general framework, test named players the "allegations" point to. Candidates already in the data: Mbappé 2017, Neymar 2017, Dembélé 2017, João Félix 2019, Jude Bellingham 2023, Doué 2026. Jobe Bellingham is **not** in any supplied file; his fee, performance and following must be sourced and added by hand.

---

## 2. Data inventory and audit findings

Files in `data/raw/` (copy the uploaded files there; never edit them, write cleaned versions to `data/clean/`).

| File | Rows | What it is | Verdict |
|---|---|---|---|
| `player_market_values.csv` | 1,025 | Yearly market value (€m), age, position, `is_peak_year` for **85 real players**, 2010–2026 | Usable, with serious caveats below |
| `record_transfers.csv` | 57 | Headline transfers: fee, clubs, age, flags for free / loan / extension | Usable; small and selected on high fees |
| `transfers_history.csv` | 14,990 | Transfers 2010–2026 across 52 clubs / 10 leagues | **Appears synthetic. Do not use at player level** (see below) |
| `club_financials.csv` | 884 | 52 clubs × 17 years: revenue, wages, net transfer spend, profit, capacity | Clean and complete; use for buyer purchasing power |
| `league_metrics.csv` | 170 | 10 leagues × 17 years: revenue, attendance, ticket, foreign % | Revenue is useful; ticket price and foreign % are essentially static per league; 2020–21 attendance is a COVID artefact |
| `football_players_social_media.xlsx` | 4,049 | Player names with Twitter/Instagram/Facebook **profile links only** | No follower counts. The "Instagram" and "Facebook" column headers are **swapped** (verified: the Instagram column holds only facebook.com links). Classify by URL domain, not header |
| Performance statistics | none | Not yet collected | **Must be sourced** |
| Instagram following over time | none | Not yet collected | **Must be sourced** |

### Findings Claude Code must re-verify first, then act on

1. **`transfers_history.csv` looks randomly generated.** There are 4,334 unique names, with generic ones repeated (e.g. "David Meyer" 13 times). Median fee is roughly flat (about €5–7m) across ages 16–32 and across positions. Only 1 of the 85 market-value players appears by name (Eduardo Camavinga, 3 rows, with ages 28/25/25 against a real-player age of 18–24). It cannot be linked to market values, performance or social data. Use it only for aggregate market context (fees by year or league), or drop it. Ask the user about its provenance before relying on it for anything.
2. **Market values look stylized.** Series follow a smooth rise-peak-collapse curve and fall to roughly €2–9m after about age 30–33 for everyone. Examples: Mbappé is €37.6m in 2025 (age 26) and €12.6m in 2026; Kane is €11.4m in 2023 (age 30), while `record_transfers` has Bayern paying €100m for him that same year. If the series is mostly an age curve, any model will find that "age explains value" and little else. Validate 20+ player-years against a public source (Transfermarkt) before modelling.
3. **Duplicate rows:** Bukayo Saka has two conflicting series (peak 2024 at €136.2m vs peak 2023 at €142.5m), 10 duplicated player-years. Decide on a rule (flag, average, or drop) and document it.
4. **Tiny linked sample.** Only **47** `record_transfers` rows are paid permanent transfers (excluding free, loan, extension rows). Only **18** have a market value in the transfer year or the year before, and 35 of the 47 match the social file by normalised name. Any fee-level model on this sample is a case study, not an estimate. This is the main reason to expand the player sample (§4).
5. **Selection on the outcome.** `record_transfers` contains headline (mostly high-fee) deals, so it truncates the dependent variable. Fee models need caution (truncation-aware methods or restrict to market value as outcome).
6. **Name matching.** Use accent-stripped lowercase keys and manually reviewed fuzzy matches (e.g. "Estevão Willian" vs "Estêvão"). Keep a `name_crosswalk.csv` with a reviewed flag.
7. **Timing convention needed.** Market values are annual with no month. Define the "pre-transfer value" as the market-value row of year *t−1* (and *t* as a sensitivity check) and say so everywhere.

---

## 3. Variable definitions

**Outcomes (run all three; they answer slightly different questions)**
- `log_mv` : log market value, player-year panel (outcome A, largest sample).
- `log_fee` : log transfer fee, paid permanent transfers only (outcome B, tiny without expansion).
- `premium` : `log(fee) − log(mv_{t−1})` (outcome C, the "price above market value" the allegations are about).

**Performance (P)**, position-specific z-scores, league-strength adjusted, trailing 12 months before the transfer or valuation date:
- Output per 90: non-penalty xG + xA, shot/chance creation, progressive carries/passes; for defenders and keepers use position-appropriate metrics (tackles+interceptions, aerial wins, PSxG−GA).
- Minutes played (reliability), international caps.
- Long-history fallback: EA FC / FIFA overall rating, which exists back to 2010 for everyone.
- Build one composite per position group (PCA or fixed weights), and keep the components for robustness.

**Commercial (C)**, measured **6 and 12 months before** the valuation or transfer date:
- `log_ig_followers` and 12-month follower growth rate.
- Alternative or complementary proxies that exist as time series for everyone: Wikipedia monthly pageviews (since 2015), Google Trends interest (relative; anchor on a reference player).
- **Excess following** = residual of `log_ig_followers` on performance, age, position and nationality-market size. This is the "popularity not explained by play" measure, and the cleanest test of the allegations.

**Controls**
- Age (spline or age + age²), position, years to end of peak.
- Buyer purchasing power: buying club's revenue, wage bill, net transfer spend (`club_financials`), lagged one year.
- Selling club and league, transfer window, year fixed effects (or an inflation index from league revenue).
- Contract length remaining (not in the data; add it if sourcing real data).

---

## 4. Data acquisition tasks (do before modelling)

1. **Real valuation and transfer data at scale.** Replace or supplement the stylized series with real Transfermarkt-derived data for roughly 300–500 players (top by value, 2015–2026), including fees, dates, contract length. A public Transfermarkt dataset exists (look for the open `transfermarkt-datasets` project on GitHub/Kaggle; confirm licence and terms). **Do not scrape a site against its terms of service; ask the user first.**
2. **Performance stats.** Collect from FBref / Understat / StatsBomb open data (check terms). If coverage is thin before 2017, use EA FC ratings as the long-history proxy.
3. **Instagram following over time.** Options in order of preference: (a) a dataset or API that gives follower history; (b) Wayback Machine snapshots of profile pages around transfer dates (patchy); (c) Social Blade-style history (check terms); (d) fallback: current followers as a *level* proxy only, clearly flagged as contaminated by post-transfer fame. Always pair with Wikipedia pageviews and Google Trends as time-varying attention proxies.
4. **Case studies.** Hand-collect Jobe Bellingham and any other player the group names: fee, date, buyer/seller, trailing performance, following at t−6 and t−12 months.
5. Log every source, access date and licence in `docs/data_sources.md`.

---

## 5. Repository layout

```
data/raw/            # untouched originals
data/clean/          # cleaned and merged outputs (parquet/csv)
docs/                # data_sources.md, data_audit.md, decisions.md, name_crosswalk.csv
src/                 # 01_audit.py, 02_build_panel.py, 03_eda.py, 04_models.py, 05_cases.py, 06_figures.py
outputs/figures/     # PNGs at 200 dpi
outputs/tables/      # CSVs of all model results
README.md            # how to reproduce
```

Use Python (pandas, statsmodels, scikit-learn, linearmodels, matplotlib). Seed everything. Every number in a figure or table must be reproducible from `src/`.

---

## 6. Analytics plan

### 6.1 Audit (`01_audit.py` → `docs/data_audit.md`)
Re-verify every finding in §2: duplicates, key overlaps across files, missingness, fee/market-value plausibility, age consistency, the swapped social headers. Report exact counts. Stop and summarise for the user if findings 1 or 2 hold, because they decide the design.

### 6.2 Build the analysis panel (`02_build_panel.py`)
- Player-year panel (`player, year, age, position, mv, P, C, club, league`).
- Transfer-event table (`player, date, fee, flags, pre-transfer mv, P_t−6/12, C_t−6/12, buyer financials`) after dropping free, loan and extension rows.
- Keep drop counts at each filter step.

### 6.3 Exploratory analysis (`03_eda.py`)
- Distributions of mv, fee, followers (log scales); correlation matrix of P, C, mv, fee; VIF between P and C.
- mv trajectories by age and position (is the age curve dominating?).
- Scatter: fee vs pre-transfer mv, labelled by player; scatter: C vs P coloured by age.
- Fee-to-mv ratio over time and by buyer.

### 6.4 Core test: incremental explanatory power of commercial value (`04_models.py`)
Run for outcomes A, B and C, with standard errors clustered by player (and bootstrap CIs given small N):

| Model | Spec |
|---|---|
| M0 | age, position, year FE, buyer wealth |
| M1 | M0 + performance P |
| M2 | M1 + commercial C (log followers, growth) |
| M2b | M1 + excess following |
| M3 | M2 + interactions: C×young (age ≤ 21), C×attacker, C×buyer revenue, C×post-2017 |

Report for each:
1. Coefficient on C with CI, in % effect on value per doubling of followers.
2. **ΔR² (M2 vs M1)** and partial R² of C; relative importance (LMG/Shapley) of P vs C.
3. Nested F or Wald test for C; permutation test (shuffle C within position-year) for the ΔR².
4. **Out-of-sample:** grouped-by-player k-fold (or leave-one-player-out) RMSE for M1 vs M2. If C helps in-sample but not out-of-sample, say so.
5. Sensitivity to the timing lag (t−6 vs t−12 months) and to the performance composite vs components.

### 6.5 Stress tests of the "independent of performance" claim
- **Player fixed effects** (panel A): identify from within-player changes in following and value; absorbs time-invariant brand or nationality.
- **Lagged / growth specification:** `C_{t−1}` and Δ followers predicting Δ value, reducing reverse causality.
- **Event windows:** follower jumps around tournaments (World Cup / Euros) for players whose performance did not change; compare with matched controls.
- **Matched comparison:** pair players with near-identical P, age, position and league but very different C; compare value or premium.
- **Optional exogenous variation:** nationality / home-market size as an instrument for following. State plainly if the exclusion restriction is weak.
- Residual check: do the results survive removing the top 5 transfers (influence/Cook's distance)?

### 6.6 Premium and case studies (`05_cases.py`)
- Fit M1 (performance-only) **leave-one-out**; compute each transfer's predicted value, residual and percentile.
- Table: every transfer ranked by unexplained premium, alongside followers and excess following.
- Regress residual premium on excess following (and report the rank correlation).
- Case-study cards for the named players: fee, model-predicted fee (with prediction interval), premium, commercial rank. A player counts as consistent with the allegation only if the premium lies outside the prediction interval **and** the commercial rank is high.

### 6.7 Visuals (`06_figures.py`)
Minimum set: (1) fee vs pre-transfer market value; (2) P vs C scatter; (3) ΔR² / coefficient forest plot across specifications; (4) residual premium by player (lollipop) with followers as colour; (5) in-sample vs out-of-sample RMSE for M1 vs M2. Two of these also satisfy the class "Create 2" visualization assignment; the first Create 2 PDF only covers social-media handle coverage and should be replaced by charts from this panel.

---

## 7. Guardrails for Claude Code
- **Check in with the user** before: scraping any site, buying data, dropping `transfers_history.csv`, or changing the outcome definition.
- Never overwrite `data/raw/`. Document each judgement call in `docs/decisions.md`.
- Report effect sizes with intervals, not just p-values. With N this small, say "not detectable" rather than "no effect".
- Word conclusions as association, never as proof that clubs pay for brand.
- End each phase with a short written summary of findings, caveats and the next decision for the group.

## 8. Suggested kickoff prompt (paste into Claude Code from the repo root)

> Read `PROJECT_BRIEF.md`. Start with §6.1: run the full data audit on the files in `data/raw/`, confirm or refute each finding in §2, and write `docs/data_audit.md` with exact counts. Then stop and summarise what you found, and propose how you'd handle the synthetic-looking `transfers_history.csv` and the stylized market values before we collect any new data.
