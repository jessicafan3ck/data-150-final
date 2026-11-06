# Data sources

| Source | File(s) | Obtained from | Access date | Licence / terms | Notes |
|---|---|---|---|---|---|
| Course-supplied archive | `player_market_values.csv`, `record_transfers.csv`, `transfers_history.csv`, `club_financials.csv`, `league_metrics.csv` | `~/Downloads/archive/` | 2026-10-24 | Unknown | See `data_audit.md`. |
| Social-media handles | `football_players_social_media.xlsx` | `~/Downloads/` (dated 2022-04-19) | 2026-10-24 | Unknown | Links only, no follower counts. |
| Player performance | FootyStats season exports, 80 CSVs | `/Users/jessicafan/data/{epl,la liga,serie a,bundesliga,ligue 1} stats/` | 2026-10-25 | FootyStats terms (group's existing download) | Top-5 leagues, 2009/10–2024/25. |
| Wikipedia pageviews | `data/external/wiki_*.csv` | Wikimedia REST API `metrics/pageviews/per-article`, en.wikipedia, agent=user; titles via REST `page/summary`, redirects and move log via the action API | 2026-10-25 | Pageview data CC0; API used within rate limits | Fetched by `src/00_fetch_wikipedia.py`. |
| UEFA club finance aggregates | `outputs/tables/context_uefa_aggregates.csv` (typed in `src/08_club_context.py`) | UEFA news: "Record revenue highlighted in new-look UEFA Club Finance and Investment Landscape Report" (2024 revenue €28.6bn); "The key trends at the heart of European club football" (summer-2026 player sales €10.3bn, spending > €10bn, projected transfer profit €6.8bn); Football Benchmark summary of the UEFA report (wages ≈ €13.5bn) | 2026-11-06 | Published figures, cited | uefa.com/news-media; footballbenchmark.com. Summer-2026 transfer figures are UEFA's provisional estimates. |
| Club valuation multiples | constants in `src/09_club_impact.py` | Forbes, "The World's Most Valuable Soccer Teams 2026" (Forbes Australia, 2 Jun 2026): most clubs valued below 4× revenue, European top-30 average 5.6×; enterprise value = equity + net debt; player trading excluded from revenue | 2026-11-06 | Published figures, cited | forbes.com.au |
