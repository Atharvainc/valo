import os
import requests
import pandas as pd
import pyarrow
from dotenv import load_dotenv
from db_setup import init_db

load_dotenv()

def fetch_player_matches(name,tag,api_key):
    url=f"https://api.henrikdev.xyz/valorant/v3/matches/ap/{name}/{tag}"
    headers={'Authorization':api_key}
    print(f'getting match info for {name}#{tag}')
    response=requests.get(url,headers=headers)
    if response.status_code!=200:
        print(f'api connection failed with status code{response.status_code}')
        print('check where your api key resides :(')
        return None
    return response.json()['data']
    
def run_etl():
    api_key = os.getenv("VALO_API_KEY")
    engine = init_db()
    name='john doe'
    tag='69420'
    
    raw_matches=fetch_player_matches(name=name,tag=tag,api_key=api_key)
    if not raw_matches:
        print('data extraction failed :( gand mara')
        print('exiting loop')
        return
    print('extracted data sucksexfully')
    metadata_rows=[]
    stats_rows=[]
    
    for match in raw_matches:
        metadata=match['metadata']
        match_id=metadata['matchid']

        metadata_rows.append({
            'match_id':match_id,
            'map_name':metadata['map'],
            'queue_type':metadata['mode']
        })

        for player in match['players']['all_players']:
            stats_rows.append({
                "match_id": match_id,
                "puuid": player['puuid'],
                "agent_name": player['character'],
                "kills": player['stats']['kills'],
                "deaths": player['stats']['deaths'],
                "assists": player['stats']['assists']
            })

    df_matches=pd.DataFrame(metadata_rows)
    df_stats=pd.DataFrame(stats_rows)
    print('loading datasets into database engines...')
    df_matches.to_sql('valorant_matches', con=engine, if_exists='append', index=False)
    df_stats.to_sql('player_match_stats', con=engine, if_exists='append', index=False)
        
    print("\nETL cycle completed cleanly! Open your SQLite viewer to check your rows.")
if __name__ == "__main__":
    run_etl()