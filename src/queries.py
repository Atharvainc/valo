import pandas as pd
from sqlalchemy import text,bindparam
from sqlalchemy import bindparam

def get_overview_stats(engine, name, tag, queue_types: list[str]) -> dict:
    query = text("""
        SELECT
            COUNT(*) AS total_matches,
            ROUND(AVG(CAST(kills + assists AS FLOAT)/NULLIF(deaths, 0)), 2) AS avg_kda,
            ROUND(AVG(CAST(headshots AS FLOAT)/NULLIF(headshots + bodyshots + legshots, 0) * 100), 1) AS avg_hs_pct,
            ROUND(SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) * 100.0/ NULLIF(SUM(CASE WHEN won IS NOT NULL THEN 1 ELSE 0 END), 0), 1)  AS win_rate
        FROM player_match_stats s
        JOIN valorant_matches m ON s.match_id = m.match_id
        WHERE m.player_name = :player_name
        AND m.player_tag = :player_tag
        AND m.queue_type IN :queue_types
    """).bindparams(bindparam("queue_types", expanding=True))

    result = pd.read_sql(query, con=engine, params={"queue_types": queue_types,'player_name':name,'player_tag':tag})#type: ignore
    return result.iloc[0].to_dict()


def get_kda_trend(engine, name, tag, queue_types: list[str]) -> pd.DataFrame:
    query=text('''
    WITH base AS(
    SELECT ROW_NUMBER() OVER (ORDER BY s.id ASC) AS match_num,
    s.kills,s.deaths,s.assists,s.won,s.agent_name,m.map_name,
    ROUND(CAST(s.kills+s.assists AS FLOAT)/NULLIF(s.deaths,0),2) AS kda
    FROM player_match_stats s
    join valorant_matches m on s.match_id=m.match_id
    WHERE m.player_name = :player_name
        AND m.player_tag = :player_tag
        AND m.queue_type IN :queue_types
    )
    select match_num,kills,deaths,assists,won,agent_name,map_name,kda,
    ROUND(AVG(kda) OVER(
                    ORDER BY match_num
                    ROWS BETWEEN 4 PRECEDING AND CURRENT ROW),2) AS rolling_avg
    FROM base
    ORDER BY match_num ASC
    ''').bindparams(bindparam('queue_types',expanding=True))
    return pd.read_sql(query,con=engine, params={"queue_types": queue_types,'player_name':name,'player_tag':tag})#type:ignore


def get_agent_breakdown(engine, name, tag, queue_types: list[str]) -> pd.DataFrame:
    query=text('''
        SELECT COUNT(*) AS tot_matches,
        ROUND(AVG(CAST(kills AS FLOAT)),2) AS avg_kills,   
        ROUND(AVG(CAST(deaths AS FLOAT)),2) AS avg_deaths,   
        ROUND(AVG(CAST(assists AS FLOAT)),2) AS avg_assists,
        ROUND(AVG(CAST(kills+assists AS FLOAT)/NULLIF(deaths,0)),2) AS avg_kda,
        ROUND(AVG(CAST(headshots AS FLOAT)/NULLIF(headshots+bodyshots+legshots,0)*100),1) AS avg_hs_pct,
        ROUND(AVG(CAST(bodyshots AS FLOAT)/NULLIF(headshots+bodyshots+legshots,0)*100),1) AS avg_bs_pct,
        ROUND(AVG(CAST(legshots AS FLOAT)/NULLIF(headshots+bodyshots+legshots,0)*100),1) AS avg_ls_pct,
        ROUND(SUM(CASE WHEN won=1 THEN 1 ELSE 0 END)*100/NULLIF(COUNT(*),0),1) AS winrate,
        agent_name,agent_role
        FROM player_match_stats s
        JOIN valorant_matches m ON s.match_id=m.match_id
        WHERE m.player_name = :player_name
            AND m.player_tag = :player_tag
            AND m.queue_type IN :queue_types
        GROUP BY agent_name,agent_role
        HAVING COUNT(*)>=3
        ORDER BY avg_kda DESC
    ''').bindparams(bindparam('queue_types',expanding=True))
    return pd.read_sql(query, con=engine,  params={"queue_types": queue_types,'player_name':name,'player_tag':tag})#type:ignore

def get_map_stats(engine, name, tag, queue_types: list[str]) -> pd.DataFrame:
    query=text('''
    SELECT COUNT(*) AS tot_matches,
        ROUND(AVG(CAST(kills+assists AS FLOAT)/NULLIF(deaths,0)),2) AS avg_kda,
        ROUND(SUM(CASE WHEN won=1 THEN 1 ELSE 0 END)*100/NULLIF(COUNT(*),0),1) AS winrate,
        map_name
    FROM player_match_stats s
    JOIN valorant_matches m ON s.match_id=m.match_id
    WHERE m.player_name = :player_name
        AND m.player_tag = :player_tag
        AND m.queue_type IN :queue_types
    GROUP BY map_name
    HAVING COUNT(*)>=3
    ORDER BY winrate DESC
    ''').bindparams(bindparam('queue_types',expanding=True))
    return pd.read_sql(query,con=engine, params={"queue_types": queue_types,'player_name':name,'player_tag':tag})#type:ignore


