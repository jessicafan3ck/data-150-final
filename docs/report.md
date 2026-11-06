# Does commercial value move transfer value beyond performance? What would it mean for clubs?

DATA 150 group project. All numbers come from `src/` (details in `docs/results_*.md`, tables in `outputs/tables/`).
**Fame** = English-Wikipedia page views in the 12 months before a valuation or transfer. **Performance** = position-specific
z-score composite from FootyStats. Results are associations, not proof that clubs pay for fame.

---

## 1. Context: how club money works, and the changing price of fame

**Figures:** `outputs/figures/context_1_club_revenue.png`, `context_2_money_in.png`, `context_3_attention_by_period.png`

- **Revenue is growing fast.** The 52 clubs in the supplied data went from €6.4bn of combined revenue in 2010 to €17.1bn in 2025.
  Wages take a steady ~55% of it.
- **Player sales are a second income stream, about a third the size of everything else.** UEFA reports €10.3bn of player
  sales in the summer-2026 window alone, against €28.6bn of operating revenue across Europe's top divisions in 2024. That is
  roughly **€36 of sales for every €100 of revenue**, of which about two-thirds (€6.8bn) is expected to be profit.
- **Some clubs live on sales.** Over 2010–2026, Benfica, RB Leipzig, Sporting, Lille, Porto and Ajax took in net transfer
  income worth 19–27% of their revenue.
- **The price of fame in market values has fallen.** Per doubling of attention at equal performance, market values were
  +25% higher in 2017–18 [95% CI +10, +42], +14% in 2019–20, and +3–6% from 2021 on (intervals now include zero).

## 2. Fame vs. performance vs. actual valuation

**Figures:** `outputs/figures/simple_1_performance_vs_attention.png`, `simple_2_attention_effect.png`

- Fame and performance overlap (correlation 0.51) but are far from the same: at the same performance score, Messi drew 19× the
  attention of Lautaro Martínez in 2021/22.
- At the same performance, age and position, a doubling of attention goes with:
  - **+12% market value** [+3, +23], 531 player-seasons;
  - **+25% transfer fee** [+6, +48], 34 transfers.
- Fees price fame about **twice as steeply** as market values do.
- Whether fame explains the fee paid *above* prior market value is not detectable (15 transfers: −5% [−48, +76]).
- Fame may partly stand in for ability the performance score misses; with player fixed effects the market-value estimate falls
  to +9% [−1, +19].

## 3. Case studies of the extremes

**Source:** `docs/results_cases.md`

- Fees above what performance alone predicts track fame not explained by performance (Spearman ρ = 0.43, p = 0.011).
- Largest unexplained premiums: **Neymar 2017** (€222m vs. €83m predicted), **Ronaldo 2018** (€117m vs. €48m),
  Caicedo 2023, Neymar 2023, Griezmann 2019, Kane 2023.
- No case meets the strict test (fee above the 95% prediction interval *and* top-quartile fame); the intervals are wide at this
  sample size. Neymar 2017 comes closest.

## 4. What a shift in transfer valuation would do to clubs

**Figures:** `outputs/figures/impact_1_transfers.png`, `impact_2_sensitivity.png`. **Source:** `docs/results_club_impact.md`

Each transfer is repriced by changing only the price of fame (performance, age, position and buyer fixed):

| Scenario | Total fees |
|---|---|
| S1 fees priced on performance only | −1% |
| S2 fees price fame like market values do | −1% |
| S3 fame premium grows by half | +4% |

- **A shift mostly moves money between clubs; the market barely shrinks.**
- **Clubs that sell famous players lose:** Barcelona would have received €65m less for Neymar (≈11% of its revenue that year),
  Real Madrid €63m less for Ronaldo, Tottenham €37m less for Kane.
- **Clubs that sell under-the-radar players gain:** Athletic Bilbao +€63m for Kepa (≈51% of its revenue), AC Milan +€31m for
  Tonali.
- **For a typical club** whose sales are 36% of revenue, performance-only pricing changes income by about −7% of revenue if it
  sells players twice as famous as average, and +9% if half as famous.
- **Club value** (Forbes: value ≈ 4× revenue for most clubs) moves by the same percentage if the change is permanent, and by about
  a quarter of it if it is a one-off.

## 5. Recommendation

1. **Selling clubs with famous players should treat the fame premium as fragile income.** It is a material share of revenue
   in big sales (≈10% for Barcelona's Neymar fee), and the price of fame in market values has already fallen since 2017–18.
   Budgets should not depend on it continuing.
2. **Buying clubs should price fame explicitly, not implicitly.** Fees reward fame twice as much as market values do. A buyer
   paying for fame should be able to point to the commercial return (shirt sales, sponsorship, audience) that justifies it.
   Otherwise, negotiating on performance-based valuations would save money.
3. **Clubs that sell under-the-radar talent have the most to gain from performance-based pricing**, and the most to lose from
   a growing fame premium. They should push valuation on performance data (e.g. scouting metrics) when they sell.
4. **For the market as a whole, the question is fairness, not size.** Removing the fame premium shifts money between clubs
   rather than out of football.

## Caveats

- Associations only: fame and performance feed each other, and fame may proxy for ability the score misses.
- The fee sample is small (34 transfers) and made of headline deals; intervals are wide (e.g. Neymar's −€65m ranges from
  −€101m to −€18m).
- Supplied market values and club financials are used as given.
- Player sales come from UEFA aggregates, which mix one transfer window (2026) with one year of revenue (2024).
- Forbes excludes player trading from the revenue it values, so the permanent-change club value figures are an upper bound.
- English Wikipedia over-weights English-speaking audiences; a control for English-speaking nationality leaves the estimates
  unchanged.
