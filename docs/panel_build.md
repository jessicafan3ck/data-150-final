# Panel build log (src/02_build_panel.py)

- Performance rows loaded: 50,549 (5 leagues, seasons 2009/2010–2024/2025)
- Player-seasons after merging mid-season moves: 49,595
- Market-value rows: 1,025 (85 players)
- Averaged 10 duplicated player-years (Bukayo Saka's two series) → 1,015 rows
- Targets: 114 players; matched to performance data (name + birth year ±1): 111. Unmatched: Antony, Estevão Willian, Franco Mastantuono
- Panel rows: 1,015; with performance in season ending t: 687
- Panel rows with Wikipedia C12 (years ≥ 2016): 785; with both P and C: 568 (83 players)
- record_transfers rows: 57
-   drop is_extension: −6 → 51
-   drop is_loan: −1 → 50
-   drop is_free_transfer: −3 → 47
- Paid permanent transfers: 47; with P: 38; with wiki C12: 43; with buyer revenue: 45; with mv(t−1): 18
-   P and C12: 35; + buyer revenue: 34; + mv(t−1) (premium): 15
-   missing P (seller outside top-5 leagues or unmatched): Cristiano Ronaldo 2009, Joao Felix 2019, Matthijs de Ligt 2019, Darwin Nunez 2022, Antony 2022, Mykhailo Mudryk 2022, Enzo Fernandez 2023, Joao Neves 2024, Viktor Gyokeres 2025
