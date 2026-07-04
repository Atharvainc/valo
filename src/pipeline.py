from db_setup import init_db
import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time
load_dotenv()

ROLE_MAP = {
    "Jett": "Duelist",   "Reyna": "Duelist",  "Neon": "Duelist",   "Raze": "Duelist",
    "Phoenix": "Duelist","Iso": "Duelist",     "Yoru": "Duelist",   "Waylay": "Duelist",
    "Omen": "Controller","Clove": "Controller","Brimstone": "Controller","Viper": "Controller",
    "Astra": "Controller","Harbor": "Controller","Miks": "Controller",
    "Cypher": "Sentinel","Killjoy": "Sentinel","Sage": "Sentinel",  "Deadlock": "Sentinel",
    "Vyse": "Sentinel",  "Chamber": "Sentinel","Veto": "Sentinel",
    "Sova": "Initiator", "Fade": "Initiator",  "Gekko": "Initiator","Skye": "Initiator",
    "Breach": "Initiator","KAY/O": "Initiator","Tejo": "Initiator",
}

# ── FIX 2: two separate fetchers, one per queue ───────────────────────────────
# The stored-matches endpoint accepts an optional `mode` query param so we can
# ask for exactly competitive or non-competitive matches and get up to 30 each.
# This replaces the old single fetch + client-side split.

def fetch_raw_data(name, tag, mode: str|None = None, size: int = 30):
    """
    Fetch stored matches from HenrikDev.
    mode  – optional API filter: 'competitive', 'unrated', 'swiftplay', etc.
            Pass None to get the 30 most recent matches of any type.
    size  – max records (API cap is 30 per request; see note below about pagination).
    """
    api_key = os.getenv("VALO_API_KEY")

    # Requesting up to 30 records from the lifetime tracking endpoint
    url = f"https://api.henrikdev.xyz/valorant/v1/stored-matches/ap/{name}/{tag}?size={size}"
    if mode:
        url += f"&mode={mode}"

    headers = {'Authorization': api_key}
    mode_label = mode or "all modes"
    print(f"Requesting stored matches for {name}#{tag} [{mode_label}]...")

    response = requests.get(url, headers=headers) # type: ignore
    if response.status_code != 200:
        print(f"Bad request: status={response.status_code} | {response.text[:120]}")
        return []
    return response.json().get('data', [])


# ── ETL ───────────────────────────────────────────────────────────────────────
def _derive_won(match: dict) -> bool | None:
    """
    Determine win/loss from the match object.
    stats.team  → "Red" or "Blue"
    teams       → {"red": <rounds_won>, "blue": <rounds_won>}
    Returns True (win), False (loss), or None (data missing / couldn't decide).
    """
    try:
        player_team = match['stats']['team'].lower()        # "red" or "blue"
        red_rounds = match['teams']['red']
        blue_rounds = match['teams']['blue']
        if red_rounds == blue_rounds:                       # draw (rare)
            return None
        winning_team = "red" if red_rounds > blue_rounds else "blue"
        return player_team == winning_team
    except (KeyError, TypeError):
        return None


def process_and_load_etl(raw_matches: list, player_name: str, player_tag: str):
    engine = init_db(drop_existing=False)
    metadata_rows = []
    stats_rows = []

    for match in raw_matches:
        meta = match.get('meta', {})
        match_id = meta.get('id')
        if not match_id:
            continue

        queue_label = meta.get('mode', 'unknown').lower()
        player_stats = match.get('stats')
        if not player_stats:
            continue
        character = player_stats.get('character')
        if not character:
            continue

        agent = character.get('name', 'Unknown')
        role = ROLE_MAP.get(agent, 'Unknown')
        shots = player_stats.get('shots', {})
        won = _derive_won(match)

        metadata_rows.append({
            "match_id": match_id,
            "player_name": player_name,
            "player_tag": player_tag,
            "map_name": meta.get('map', {}).get('name', 'Unknown'),
            "queue_type": queue_label,
        })
        stats_rows.append({
            "match_id": match_id,
            "agent_name": agent,
            "agent_role": role,
            "kills": player_stats.get('kills', 0),
            "deaths": player_stats.get('deaths', 0),
            "assists": player_stats.get('assists', 0),
            "headshots": shots.get('head', 0),
            "bodyshots": shots.get('body', 0),
            "legshots": shots.get('leg', 0),
            "won": won,
        })

    if not stats_rows:
        print("No processable matches found in payload.")
        return

    df_matches = pd.DataFrame(metadata_rows).drop_duplicates(subset=['match_id'])
    df_stats = pd.DataFrame(stats_rows)

    try:
        existing = pd.read_sql("SELECT match_id FROM valorant_matches", con=engine)['match_id'].tolist()
        df_matches = df_matches[~df_matches['match_id'].isin(existing)]
        df_stats = df_stats[~df_stats['match_id'].isin(existing)]
    except Exception:
        pass

    if not df_matches.empty:
        print("Ingesting new matches:", df_matches['queue_type'].value_counts().to_dict())
        df_matches.to_sql('valorant_matches', con=engine, if_exists='append', index=False)

    if not df_stats.empty:
        print(f"Ingesting {len(df_stats)} player stat rows...")
        df_stats.to_sql('player_match_stats', con=engine, if_exists='append', index=False)
    else:
        print("No new data — DB already up to date.")

def load_all_history(name: str, tag: str, size_per_mode: int = 50):
    """
    Fetch each mode separately (guarantees sample size per mode,
    so competitive doesn't get crowded out by casual spam),
    then run everything through ONE generic ETL call.
    """
    print("\n--- Running Full History Pipeline ---")

    modes = ['competitive', 'unrated', 'swiftplay', 'deathmatch']
    all_matches = []

    for mode in modes:
        raw = fetch_raw_data(name, tag, mode=mode, size=size_per_mode)
        if raw:
            print(f"  Got {len(raw)} {mode} matches")
            all_matches.extend(raw)
        time.sleep(0.3)

    if all_matches:
        process_and_load_etl(all_matches,player_name=name,player_tag=tag)
    else:
        print("No matches found across any mode.")

