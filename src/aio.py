import os
import pandas as pd
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _build_context(stats: dict, df_agents: pd.DataFrame, df_maps: pd.DataFrame) -> str:
    lines = []
    lines.append(
        f"Overall: {stats['total_matches']} matches, {stats['avg_kda']} avg KDA, "
        f"{stats['avg_hs_pct']}% headshot rate, {stats['win_rate']}% win rate."
    )

    lines.append("\nAgent performance:")
    for _, row in df_agents.iterrows():
        lines.append(
            f"- {row['agent_name']} ({row['agent_role']}): "
            f"{row['tot_matches']} games, {row['avg_kda']} KDA, {row['winrate']}% winrate"
        )

    lines.append("\nMap performance:")
    for _, row in df_maps.iterrows():
        lines.append(
            f"- {row['map_name']}: {row['tot_matches']} games, {row['winrate']}% winrate"
        )

    return "\n".join(lines)


def generate_overview(stats: dict, df_agents: pd.DataFrame, df_maps: pd.DataFrame) -> str:
    if df_agents.empty or not stats.get('total_matches'):
        return "Not enough matches played yet for an AI overview."

    context = _build_context(stats, df_agents, df_maps)

    prompt = (
        "You are a Valorant coach reviewing a player's stats. "
        "Give a 3-4 sentence plain-English overview: their strengths, "
        "one clear weakness, and one specific actionable tip. "
        "Be direct and specific, reference actual numbers. "
        "Only use the agent names, map names, and stats given below — "
        "do not reference abilities, patch changes, or anything about the game "
        "that isn't explicitly stated in this data. "
        "No headers, no bullet points, just plain prose.\n\n"
        f"{context}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
        return response.text#type:ignore
    except Exception as e:
        print(f"AI overview failed: {e}")
        return "AI overview unavailable right now."

if __name__ == "__main__":
    from sqlalchemy import create_engine
    from db_setup import DATABASE_URL
    from queries import get_overview_stats, get_agent_breakdown, get_map_stats

    engine = create_engine(DATABASE_URL)
    stats = get_overview_stats(engine, "sohamchalulu", "69420", ["competitive"])
    df_agents = get_agent_breakdown(engine, "sohamchalulu", "69420", ["competitive"])
    df_maps = get_map_stats(engine, "sohamchalulu", "69420", ["competitive"])

    print(generate_overview(stats, df_agents, df_maps))