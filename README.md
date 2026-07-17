# helo
# prozect

A full-stack Valorant player analytics dashboard. Enter a Riot ID, pull real match history, and get a visual breakdown of performance — KDA trends, agent and map win rates, shot accuracy, and an AI-generated coaching summary.

**Live demo:** [valotrack.onrender.com](https://valotrack.onrender.com)
*(hosted on Render's free tier — the server spins down after inactivity, so the first load can take up to a minute)*

<img width="649" height="746" alt="Screenshot 2026-07-12 032859" src="https://github.com/user-attachments/assets/5b0b6aab-8e84-459e-b987-4e155de16a8a" />


---

## What it does

- Pulls a player's match history from the [HenrikDev Valorant API](https://docs.henrikdev.xyz/valorant), split across competitive, unrated, swiftplay, and deathmatch queues
- Runs an ETL pipeline that cleans, deduplicates, and loads matches into a relational SQLite database
- Computes KDA, headshot accuracy, win rate, and per-agent/per-map performance using SQL window functions and aggregates
- Renders everything as an interactive Plotly/Dash dashboard: a rolling-average KDA trend line with win/loss bands, agent and map performance bars, a role-distribution donut, and a shot-accuracy breakdown
- Generates a short, data-grounded performance summary using an LLM (Gemini) — strengths, weaknesses, and one actionable tip, computed entirely from the player's own stats

## Tech stack

| Layer | Tools |
|---|---|
| Data ingestion | Python, `requests`, HenrikDev API |
| Storage | SQLite, SQLAlchemy ORM |
| Querying | Raw SQL — CTEs, window functions, aggregates |
| Visualization | Plotly, Dash, `dash-bootstrap-components` |
| AI overview | Google Gemini API |
| Deployment | Render, Gunicorn |
| Env/deps | `uv` |

## Architecture

```
pipeline.py   → fetches + cleans match data from the API, loads into SQLite
db_setup.py   → SQLAlchemy models (MatchMetadata, PlayerMatchStats) + schema
queries.py    → parameterized SQL functions, one per chart/metric
charts.py     → Plotly figure builders, pure functions (DataFrame → Figure)
ai_overview.py→ builds a stats summary and calls Gemini for the AI overview
app.py        → Dash layout + callback wiring everything together
```

Each layer only talks to the one below it — `charts.py` never touches the database, `queries.py` never builds a figure. This kept debugging manageable as the project grew.

## Key design decisions

- **Per-mode fetching, not one combined pull.** The API caps stored matches at ~50 per player. Fetching each queue mode separately (rather than one mixed batch) guarantees a competitive-heavy player's ranked games aren't crowded out by casual matches, and vice versa.
- **Player-scoped schema with indexing.** Every match is tagged with the player's name/tag, so the same database can serve any number of players without data bleeding between them, and a composite index keeps lookups fast as usage grows.
- **Grounded AI overview.** The LLM prompt is explicitly restricted to the stats it's given — no outside game knowledge, no hallucinated meta commentary — so the summary stays accurate even for agents or maps added after the model's training cutoff.
- **Sample-size guards.** Agent and map charts only show categories with enough matches (`n ≥ 3`) to avoid a single lucky (or unlucky) game skewing the visual.

## Running locally

```bash
git clone https://github.com/Atharvainc/valo.git
cd valo
uv sync
```

Create a `.env` file in the project root:
```
VALO_API_KEY=your_henrikdev_key
GEMINI_API_KEY=your_gemini_key
```

```bash
uv run src/app.py
```

Open `http://127.0.0.1:8050`.

## What I'd improve next

- Persistent storage (Postgres) instead of SQLite, so match history survives a server restart
- Caching per-player results to avoid re-hitting the API on every search
- Async/parallel API calls across the four queue modes instead of sequential fetching, to cut load time

---

Built as a weekend project to get hands-on with SQL beyond what's taught in a standard DBMS course, and to practice shipping something end-to-end — ingestion, storage, analysis, visualization, and deployment.
