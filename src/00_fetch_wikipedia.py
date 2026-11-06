"""00_fetch_wikipedia.py: monthly English-Wikipedia pageviews (commercial/attention proxy C).

Source: Wikimedia REST pageviews API (public, CC0 data), agent=user, all-access, Jul 2015 onward.
Players = every name in player_market_values.csv + record_transfers.csv.
Writes data/external/wiki_titles.csv (name -> article, for review) and data/external/wiki_pageviews.csv.
Cached: re-running only fetches players not already in the output.
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, EXT = ROOT / "data/raw", ROOT / "data/external"
EXT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "DATA150-commercial-value/0.1 (student research project; python urllib)"}
START, END = "2015070100", "2026093000"

# Names whose search result is ambiguous or wrong; fixed by hand.
OVERRIDES = {
    "Rodri": "Rodri (footballer, born 1996)",
    "Gavi": "Gavi (footballer)",
    "Pedri": "Pedri",
    "Ederson": "Ederson (footballer, born 1993)",
    "Endrick": "Endrick (footballer, born 2006)",
    "Antony": "Antony (footballer, born 2000)",
    "Neymar": "Neymar",
    "Vinicius Jr": "Vinícius Júnior",
    "Estevão Willian": "Estêvão (footballer, born 2007)",
    "Marquinhos": "Marquinhos",
    "Joao Neves": "João Neves",
    "Joao Felix": "João Félix",
    "Joao Cancelo": "João Cancelo",
    "Luis Suarez": "Luis Suárez (footballer, born 1987)",
    "Kepa Arrizabalaga": "Kepa Arrizabalaga",
}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(0.5)
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            # 429: Wikimedia rate limit; honour Retry-After, else back off exponentially
            time.sleep(float(e.headers.get("Retry-After") or 0) or 5 * 2 ** min(attempt, 4))
        except Exception:
            time.sleep(5 * 2 ** min(attempt, 4))
    raise RuntimeError(f"gave up on {url}")


def resolve(name, birth_year):
    """Return (title, description) for a footballer's en.wikipedia article.

    Uses the REST summary endpoint (follows redirects); the action=query search API rate-limits (429)."""
    cands = [OVERRIDES[name]] if name in OVERRIDES else []
    cands += [name, f"{name} (footballer)", f"{name} (footballer, born {birth_year})",
              f"{name} (footballer, born {birth_year - 1})", f"{name} (footballer, born {birth_year + 1})"]
    for t in cands:
        info = get("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(t.replace(" ", "_"), safe=""))
        if info and info.get("type") == "standard" and re.search(r"football|soccer", (info.get("description") or "").lower()):
            return info["title"], info.get("description", "")
    return None, None


def redirects(titles):
    """{title: [titles (namespace 0) that redirect to it]}, 50 titles per request (the action API throttles hard)."""
    out = {t: [] for t in titles}
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        q = urllib.parse.quote("|".join(chunk))
        cont = ""
        while True:
            js = get(f"https://en.wikipedia.org/w/api.php?action=query&prop=redirects&titles={q}"
                     f"&rdlimit=max&rdnamespace=0&format=json{cont}")
            back = {n["to"]: n["from"] for n in js.get("query", {}).get("normalized", [])}
            for pg in js.get("query", {}).get("pages", {}).values():
                key = back.get(pg["title"], pg["title"])
                out.setdefault(key, []).extend(r["title"] for r in pg.get("redirects", []))
            if "continue" not in js:
                break
            cont = "&" + urllib.parse.urlencode(js["continue"])
    return out


def move_date(base, targets):
    """Timestamp (YYYYMMDD) of the latest move of page `base` to one of `targets`, else None."""
    q = urllib.parse.quote(base)
    js = get(f"https://en.wikipedia.org/w/api.php?action=query&list=logevents&letype=move&letitle={q}"
             f"&lelimit=50&format=json")
    hits = [e["timestamp"] for e in (js or {}).get("query", {}).get("logevents", [])
            if e.get("params", {}).get("target_title") in targets]
    return max(hits).replace("-", "")[:8] if hits else None


def main():
    mv = pd.read_csv(RAW / "player_market_values.csv")
    rt = pd.read_csv(RAW / "record_transfers.csv")
    rt["player_name"] = rt.player_name.str.replace(r" (extension|loan)$", "", regex=True)
    by = pd.concat([(mv.year - mv.age).groupby(mv.player_name).median(),
                    (rt.year - rt.age_at_transfer).groupby(rt.player_name).median()]).groupby(level=0).first()
    names = sorted(by.index)

    # 1. resolve each player to an article
    tpath = EXT / "wiki_titles.csv"
    titles = pd.read_csv(tpath) if tpath.exists() else pd.DataFrame(columns=["player_name", "wiki_title", "description"])
    titles = titles.dropna(subset=["wiki_title"]).reset_index(drop=True)  # retry unresolved names
    for n in [n for n in names if n not in set(titles.player_name)]:
        t, d = resolve(n, int(by[n]))
        titles.loc[len(titles)] = [n, t, d]
        print(f"{n:30s} -> {t}  [{d}]", flush=True)
        titles.to_csv(tpath, index=False)

    # 2. every title whose views belong to the player: the article, its redirects (former titles become
    #    redirects after a page move), and a base title the article was moved away from (e.g. "Luis Suárez",
    #    now a disambiguation page) counted only before the move.
    spath = EXT / "wiki_title_sources.csv"
    src = pd.read_csv(spath) if spath.exists() else pd.DataFrame(columns=["player_name", "title", "until"])
    todo = titles.dropna(subset=["wiki_title"])
    todo = todo[~todo.player_name.isin(set(src.player_name))]
    redir = redirects(list(todo.wiki_title)) if len(todo) else {}
    for r in todo.itertuples():
        rows = [(r.player_name, r.wiki_title, "")] + [(r.player_name, t, "") for t in redir.get(r.wiki_title, [])]
        base = re.sub(r"\s*\(.*\)$", "", r.wiki_title)
        if base != r.wiki_title:
            moved = move_date(base, {t for _, t, _ in rows})
            if moved:
                rows.append((r.player_name, base, moved))
        src = pd.concat([src, pd.DataFrame(rows, columns=src.columns)], ignore_index=True)
        src.to_csv(spath, index=False)
        print(f"{r.player_name:30s} {len(rows)} titles", flush=True)

    # 3. monthly views per title, cached
    vpath = EXT / "wiki_pageviews_by_title.csv"
    tv = pd.read_csv(vpath, dtype={"month": str}) if vpath.exists() else pd.DataFrame(columns=["title", "month", "views"])
    done = set(tv.title)
    todo_t = [t for t in src.title.unique() if t not in done]
    for k, t in enumerate(todo_t):
        art = urllib.parse.quote(t.replace(" ", "_"), safe="")
        js = get(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/"
                 f"all-access/user/{art}/monthly/{START}/{END}")
        items = (js or {}).get("items", [])
        rows = [(t, it["timestamp"][:6], it["views"]) for it in items] or [(t, "", 0)]  # placeholder marks done
        tv = pd.concat([tv, pd.DataFrame(rows, columns=tv.columns)], ignore_index=True)
        if k % 25 == 0:
            tv.to_csv(vpath, index=False)
            print(f"  {k}/{len(todo_t)} titles", flush=True)
    tv.to_csv(vpath, index=False)

    # 4. per-player monthly sum
    m = src.merge(tv[tv.month != ""], on="title")
    m = m[(m.until.fillna("") == "") | (m.month < m.until.fillna("").str[:6])]
    views = m.groupby(["player_name", "month"], as_index=False).views.sum()
    views.to_csv(EXT / "wiki_pageviews.csv", index=False)
    print(f"{titles.wiki_title.notna().sum()}/{len(titles)} resolved; {src.title.nunique():,} titles; "
          f"{len(views):,} player-months")


if __name__ == "__main__":
    main()
