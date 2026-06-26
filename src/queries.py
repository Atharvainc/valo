import pandas as pd
from sqlalchemy import create_engine, text
from db_setup import DATABASE_URL

def get_overview_stats(engine,queue:str):
    query=text('''
            SELECT COUNT(*) AS total_matches,
               ROUND(AVG(CAST(kills+assists AS FLOAT)/NULLIF(deaths,0)),2) AS avg_kda,
               ROUND(AVG(CAST(headshots AS FLOAT)/NULLIF(headshots+bodyshots+legshots,0)*100),1) AS avg_hs_pct,
               ROUND(SUM(CASE WHEN won=1 THEN 1 ELSE 0 END)*100/NULLIF(COUNT(*),0),1) AS winrate
               FROM player_match_stats s
               JOIN valorant_matches m ON s.match_id=m.match_id
               WHERE m.queue_type= :queue
               ''')
    res=pd.read_sql(query,con=engine,params={'queue':queue})
    return res.iloc[0].to_dict()


if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine(DATABASE_URL)
    print(get_overview_stats(engine, queue="competitive"))

