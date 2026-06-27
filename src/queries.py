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


def get_kda_trend(engine,queue:str)->pd.DataFrame:
    query=text('''
    WITH base AS(
    SELECT ROW_NUMBER() OVER (ORDER BY s.id ASC)
    s.kills,s.deaths,s.assists,s.won,s.agent_name,m.map_name,
    ROUND(CAST(s.kills+s.assists AS FLOAT)/NULLIF(s.death,0),2)
    FROM player_match_stats s
    join valorant_matches m on s.match_id=m.match_id
    where m.queue_type= :queue
    )
    select match_num,kills,deaths,assists,won,agent_name,map_name,kda,
    ROUND(AVG(kda) OVER(
                    ORDER BY match_num
                    ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rolling_avg
                    ),2)
    FROM base
    ORDER BY match_num ASC
    ''')
    return pd.read_sql(query,con=engine,params={'queue':queue})


if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine(DATABASE_URL)
    print(get_overview_stats(engine, queue="competitive"))

