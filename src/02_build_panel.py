"""02_build_panel.py: build the player-year panel and the transfer-event table (brief §6.2).

Inputs
  data/raw/*                         supplied files (read-only)
  /Users/jessicafan/data/*stats/     FootyStats season exports, top-5 leagues 2009/10-2024/25 (performance P)
  data/external/wiki_pageviews.csv   from 00_fetch_wikipedia.py (commercial proxy C)
Outputs
  data/clean/perf_seasons.csv  player-season performance with z-scores and composite P
  data/clean/panel.csv         outcome A: player-year (mv, P, C)
  data/clean/transfers.csv     outcomes B, C: paid permanent transfers (fee, mv_t-1, P, C, buyer revenue)
  docs/name_crosswalk_perf.csv target player -> FootyStats full_name (birth-year checked)
  docs/panel_build.md          drop counts at each filter step

Timing conventions (also in docs/decisions.md)
  Valuation in year t is treated as a mid-year (June) valuation.
  Panel: P = season ending in t; C12 = mean monthly views Jul(t-1)..Jun(t); C6 = Jan(t)..Jun(t).
  Transfer on date d: P = last season ending before d (season ending year(d) if month >= 6, else year(d)-1);
  C12 / C6 = mean monthly views in the 12 / 6 calendar months before the month of d.
"""
import glob
import re
import unicodedata
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
np.random.seed(150)
ROOT = Path(__file__).resolve().parents[1]
RAW, EXT, CLEAN, DOCS = ROOT / "data/raw", ROOT / "data/external", ROOT / "data/clean", ROOT / "docs"
CLEAN.mkdir(parents=True, exist_ok=True)
PERF_GLOB = "/Users/jessicafan/data/*stats/*-players-*-stats.csv"
MIN_RATE_MINUTES = 450      # below this, per-90 rates are too noisy to use
MIN_REF_MINUTES = 900       # reference population for z-scores
GAMES = {"Bundesliga": 34}  # others 38

log = []


def step(msg):
    log.append(f"- {msg}")
    print(msg)


def norm(name):
    s = str(name)
    for a, b in {"ø": "o", "Ø": "o", "æ": "ae", "ß": "ss", "đ": "d", "ł": "l", "ı": "i"}.items():
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"\b(extension|loan)\b", "", s.lower())
    return re.sub(r"[^a-z ]", "", s).strip()


# FootyStats uses full or alternative names for some players.
PERF_ALIAS = {
    "vinicius jr": ["vinicius jose paixao de oliveira junior", "vinicius junior"],
    "andy robertson": ["andrew robertson"],
    "antony": ["antony matheus dos santos"],
    "rodri": ["rodrigo hernandez cascante"],
    "gavi": ["pablo martin paez gavira"],
    "ederson": ["ederson santana de moraes"],
    "dean huijsen": ["dean donny huijsen"],
    "estevao willian": ["estevao willian almeida de oliveira goncalves", "estevao"],
    "franco mastantuono": [],
}

# ---------------------------------------------------------------- performance
cols = ["full_name", "birthday", "league", "season", "position", "Current Club", "nationality",
        "minutes_played_overall", "appearances_overall", "goals_overall", "assists_overall",
        "penalty_goals", "clean_sheets_overall", "conceded_overall"]
perf = pd.concat([pd.read_csv(f, usecols=lambda c: c in cols) for f in sorted(glob.glob(PERF_GLOB))], ignore_index=True)
perf = perf[perf.position != "Coach"].rename(columns={
    "minutes_played_overall": "minutes", "appearances_overall": "apps", "goals_overall": "goals",
    "assists_overall": "assists", "clean_sheets_overall": "clean_sheets", "conceded_overall": "conceded",
    "Current Club": "club"})
perf["season_end"] = perf.season.str[-4:].astype(int)
perf["birth_year"] = pd.to_datetime(perf.birthday, unit="s", errors="coerce").dt.year
perf["key"] = perf.full_name.map(norm)
perf["team_minutes"] = perf.league.map(GAMES).fillna(38) * 90
num = ["minutes", "apps", "goals", "assists", "penalty_goals", "clean_sheets", "conceded"]
perf[num] = perf[num].fillna(0)
step(f"Performance rows loaded: {len(perf):,} (5 leagues, seasons {perf.season_end.min() - 1}/{perf.season_end.min()}"
     f"–{perf.season_end.max() - 1}/{perf.season_end.max()})")

# a player who moved mid-season has one row per league: sum counts, keep the league/club with most minutes
perf = perf.sort_values("minutes", ascending=False)
agg = perf.groupby(["key", "birth_year", "season_end"], dropna=False).agg(
    full_name=("full_name", "first"), position=("position", "first"), league=("league", "first"),
    club=("club", "first"), nationality=("nationality", "first"), team_minutes=("team_minutes", "first"),
    **{c: (c, "sum") for c in num}).reset_index()
step(f"Player-seasons after merging mid-season moves: {len(agg):,}")

agg["npga90"] = np.where(agg.minutes >= MIN_RATE_MINUTES,
                         (agg.goals - agg.penalty_goals + agg.assists) / agg.minutes * 90, np.nan)
agg["cs90"] = np.where(agg.minutes >= MIN_RATE_MINUTES, agg.clean_sheets / agg.minutes * 90, np.nan)
agg["conc90"] = np.where(agg.minutes >= MIN_RATE_MINUTES, agg.conceded / agg.minutes * 90, np.nan)
agg["min_share"] = (agg.minutes / agg.team_minutes).clip(upper=1)

# z-scores within season x position group, against all top-5-league players with >= 900 minutes
ref = agg[agg.minutes >= MIN_REF_MINUTES]
for c in ["npga90", "cs90", "conc90", "min_share"]:
    mu = ref.groupby(["season_end", "position"])[c].mean().rename("mu")
    sd = ref.groupby(["season_end", "position"])[c].std().rename("sd")
    agg = agg.merge(pd.concat([mu, sd], axis=1).reset_index(), on=["season_end", "position"], how="left")
    agg[f"z_{c}"] = (agg[c] - agg.mu) / agg.sd
    agg = agg.drop(columns=["mu", "sd"])
# fixed-weight composite per position group (components kept for robustness)
z = agg
P = {
    "Forward": (2 * z.z_npga90 + z.z_min_share) / 3,
    "Midfielder": (z.z_npga90 + z.z_min_share) / 2,
    "Defender": (z.z_min_share + z.z_cs90 - z.z_conc90 + 0.5 * z.z_npga90) / 3.5,
    "Goalkeeper": (z.z_min_share + z.z_cs90 - z.z_conc90) / 3,
}
agg["P"] = np.select([agg.position == k for k in P], [P[k] for k in P], np.nan)
# a season with too few minutes for rates still carries information through minutes share
agg["P"] = agg.P.fillna(agg.z_min_share)
agg.to_csv(CLEAN / "perf_seasons.csv", index=False)

# ---------------------------------------------------------------- targets and crosswalk
mv = pd.read_csv(RAW / "player_market_values.csv")
rt = pd.read_csv(RAW / "record_transfers.csv")
step(f"Market-value rows: {len(mv):,} ({mv.player_name.nunique()} players)")
nd = mv.duplicated(["player_name", "year"]).sum()
mv = mv.groupby(["player_name", "year"], as_index=False).agg(
    age=("age", "first"), position=("position", "first"),
    market_value_eur_m=("market_value_eur_m", "mean"), is_peak_year=("is_peak_year", "max"))
step(f"Averaged {nd} duplicated player-years (Bukayo Saka's two series) → {len(mv):,} rows")

rt["player_clean"] = rt.player_name.str.replace(r" (extension|loan)$", "", regex=True)
rt["date"] = pd.to_datetime(rt.date)
targets = pd.concat([
    mv.assign(by=mv.year - mv.age).groupby("player_name").by.median().round().rename("birth_year"),
    rt.assign(by=rt.year - rt.age_at_transfer).groupby("player_clean").by.median().round().rename("birth_year"),
]).groupby(level=0).first().reset_index().rename(columns={"index": "player_name"})

cw = []
for r in targets.itertuples():
    keys = [norm(r.player_name)] + PERF_ALIAS.get(norm(r.player_name), [])
    c = agg[agg.key.isin(keys) & (agg.birth_year - r.birth_year).abs().le(1)]
    if c.empty:
        cw.append((r.player_name, r.birth_year, None, None, 0))
        continue
    best = c.groupby(["key", "birth_year"]).minutes.sum().idxmax()
    cw.append((r.player_name, r.birth_year, best[0], best[1], c.full_name.nunique()))
cw = pd.DataFrame(cw, columns=["player_name", "birth_year_src", "perf_key", "perf_birth_year", "n_names"])
cw.to_csv(DOCS / "name_crosswalk_perf.csv", index=False)
step(f"Targets: {len(cw)} players; matched to performance data (name + birth year ±1): "
     f"{cw.perf_key.notna().sum()}. Unmatched: {', '.join(cw.loc[cw.perf_key.isna(), 'player_name'])}")
perf_m = agg.merge(cw.dropna(subset=["perf_key"]), left_on=["key", "birth_year"],
                   right_on=["perf_key", "perf_birth_year"])[
    ["player_name", "season_end", "full_name", "position", "league", "club", "nationality", "minutes",
     "npga90", "cs90", "conc90", "min_share", "z_npga90", "z_cs90", "z_conc90", "z_min_share", "P"]]
perf_m = perf_m.rename(columns={"position": "pos_group"})

# ---------------------------------------------------------------- commercial proxy: Wikipedia pageviews
wv = pd.read_csv(EXT / "wiki_pageviews.csv", dtype={"month": str})
wv["m"] = pd.PeriodIndex(pd.to_datetime(wv.month, format="%Y%m"), freq="M")
wv = wv.set_index(["player_name", "m"]).views.sort_index()
WIKI_START = pd.Period("2015-07", "M")


def window_mean(player, end_excl, months):
    """Mean monthly views over the `months` months strictly before period end_excl; NaN if window predates data."""
    start = end_excl - months
    if start < WIKI_START or player not in wv.index.get_level_values(0):
        return np.nan
    # months with no record = article did not exist yet (zero views); the API reports every month since creation
    s = wv.loc[player].reindex(pd.period_range(start, end_excl - 1, freq="M"), fill_value=0)
    return s.mean()


# social platforms linked (static, file dated Apr 2022); NaN if the player is not in the file
sm = pd.read_excel(RAW / "football_players_social_media.xlsx")
links = sm[["Twitter", "Instagram", "Facebook"]].astype(str).apply(lambda c: c.str.lower())
sm["n_platforms"] = sum(links.apply(lambda c: c.str.contains(d)).any(axis=1).astype(int)
                        for d in ["twitter", "instagram", "facebook"])
sm["has_instagram"] = links.apply(lambda c: c.str.contains("instagram")).any(axis=1).astype(int)
sm_keys = pd.concat([sm.assign(k=sm.PlayerName.map(norm)), sm.assign(k=sm.PlayerFullName.map(norm))])
sm_keys = sm_keys.groupby("k")[["n_platforms", "has_instagram"]].max()

# ---------------------------------------------------------------- panel (outcome A)
pan = mv.copy()
pan["log_mv"] = np.log(pan.market_value_eur_m.clip(lower=0.1))
pan = pan.merge(perf_m.rename(columns={"season_end": "year"}), on=["player_name", "year"], how="left")
step(f"Panel rows: {len(pan):,}; with performance in season ending t: {pan.P.notna().sum():,}")
jun = lambda y: pd.Period(f"{y}-07", "M")  # exclusive end = July -> window ends June
pan["wiki12"] = [window_mean(p, jun(y), 12) for p, y in zip(pan.player_name, pan.year)]
pan["wiki6"] = [window_mean(p, jun(y), 6) for p, y in zip(pan.player_name, pan.year)]
pan["wiki12_prev"] = [window_mean(p, jun(y) - 12, 12) for p, y in zip(pan.player_name, pan.year)]
for c in ["wiki12", "wiki6", "wiki12_prev"]:
    pan[f"log_{c}"] = np.log1p(pan[c])
pan["wiki_growth"] = pan.log_wiki12 - pan.log_wiki12_prev
step(f"Panel rows with Wikipedia C12 (years ≥ 2016): {pan.wiki12.notna().sum():,}; with both P and C: "
     f"{(pan.P.notna() & pan.wiki12.notna()).sum():,} ({pan.loc[pan.P.notna() & pan.wiki12.notna(), 'player_name'].nunique()} players)")
pan = pan.join(sm_keys, on=pan.player_name.map(norm))
pan["attacker"] = pan.position.isin(["FW", "LW", "RW", "AM", "ST", "CF"]).astype(int)
pan["young"] = (pan.age <= 21).astype(int)
pan["post2017"] = (pan.year >= 2018).astype(int)
pan.to_csv(CLEAN / "panel.csv", index=False)

# ---------------------------------------------------------------- transfers (outcomes B, C)
step(f"record_transfers rows: {len(rt)}")
for flag in ["is_extension", "is_loan", "is_free_transfer"]:
    n0 = len(rt)
    rt = rt[rt[flag] == 0]
    step(f"  drop {flag}: −{n0 - len(rt)} → {len(rt)}")
tr = rt.rename(columns={"player_clean": "player"}).drop(columns=["player_name"])
tr["log_fee"] = np.log(tr.fee_eur_m)
mvk = mv.set_index(["player_name", "year"]).market_value_eur_m
tr["mv_tm1"] = [mvk.get((p, y - 1), np.nan) for p, y in zip(tr.player, tr.year)]
tr["mv_t"] = [mvk.get((p, y), np.nan) for p, y in zip(tr.player, tr.year)]
tr["premium"] = tr.log_fee - np.log(tr.mv_tm1)
tr["premium_t"] = tr.log_fee - np.log(tr.mv_t)
tr["perf_season"] = np.where(tr.date.dt.month >= 6, tr.year, tr.year - 1)
tr = tr.merge(perf_m.rename(columns={"player_name": "player", "season_end": "perf_season"}),
              on=["player", "perf_season"], how="left")
mo = tr.date.dt.to_period("M")
tr["wiki12"] = [window_mean(p, m, 12) for p, m in zip(tr.player, mo)]
tr["wiki6"] = [window_mean(p, m, 6) for p, m in zip(tr.player, mo)]
tr["wiki12_prev"] = [window_mean(p, m - 12, 12) for p, m in zip(tr.player, mo)]
for c in ["wiki12", "wiki6", "wiki12_prev"]:
    tr[f"log_{c}"] = np.log1p(tr[c])
tr["wiki_growth"] = tr.log_wiki12 - tr.log_wiki12_prev
cf = pd.read_csv(RAW / "club_financials.csv")
rev = cf.set_index(["club_name", "year"]).revenue_eur_m
tr["buyer_rev_tm1"] = [rev.get((c, y - 1), np.nan) for c, y in zip(tr.to_club, tr.year)]
tr["log_buyer_rev"] = np.log(tr.buyer_rev_tm1)
tr = tr.join(sm_keys, on=tr.player.map(norm))
tr["attacker"] = tr.position.isin(["FW", "LW", "RW", "AM", "ST", "CF"]).astype(int)
tr["young"] = (tr.age_at_transfer <= 21).astype(int)
tr["post2017"] = (tr.year >= 2017).astype(int)
tr.to_csv(CLEAN / "transfers.csv", index=False)
step(f"Paid permanent transfers: {len(tr)}; with P: {tr.P.notna().sum()}; with wiki C12: {tr.wiki12.notna().sum()}; "
     f"with buyer revenue: {tr.buyer_rev_tm1.notna().sum()}; with mv(t−1): {tr.mv_tm1.notna().sum()}")
both = tr.P.notna() & tr.wiki12.notna()
step(f"  P and C12: {both.sum()}; + buyer revenue: {(both & tr.buyer_rev_tm1.notna()).sum()}; "
     f"+ mv(t−1) (premium): {(both & tr.mv_tm1.notna()).sum()}")
step(f"  missing P (seller outside top-5 leagues or unmatched): "
     f"{', '.join(tr.loc[tr.P.isna(), 'player'] + ' ' + tr.loc[tr.P.isna(), 'year'].astype(str))}")

(DOCS / "panel_build.md").write_text("# Panel build log (src/02_build_panel.py)\n\n" + "\n".join(log) + "\n")
