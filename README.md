# Does commercial value move transfer value beyond performance?

DATA 150 group project. The plan is in `PROJECT_BRIEF.md`; results are in `docs/results_*.md`, `outputs/tables/` and `outputs/figures/`.

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install pandas numpy scipy openpyxl statsmodels scikit-learn matplotlib pyarrow tabulate
.venv/bin/python src/01_audit.py            # data audit            -> docs/data_audit.md
.venv/bin/python src/00_fetch_wikipedia.py  # pageviews (network; cached in data/external/, slow on first run)
.venv/bin/python src/02_build_panel.py      # panel + transfers     -> data/clean/, docs/panel_build.md
.venv/bin/python src/03_eda.py              # EDA                   -> docs/results_eda.md
.venv/bin/python src/04_models.py           # M0–M3, tests          -> docs/results_models.md
.venv/bin/python src/05_cases.py            # premium + case cards  -> docs/results_cases.md
.venv/bin/python src/06_figures.py          # figures               -> outputs/figures/
.venv/bin/python src/07_simple_figures.py   # 2 simplified figures  -> outputs/figures/simple_*.png
.venv/bin/python src/08_club_context.py     # part 1 context        -> docs/results_context.md
.venv/bin/python src/09_club_impact.py      # part 4 club impact    -> docs/results_club_impact.md
```

The full write-up in five parts is `docs/report.md`.

Performance data are read from `/Users/jessicafan/data/*stats/` (FootyStats exports); change `PERF_GLOB` in `src/02_build_panel.py` if they move. `data/raw/` holds the untouched originals (read-only). Judgement calls are in `docs/decisions.md`.
