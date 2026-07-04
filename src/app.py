from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine
import dash
from db_setup import DATABASE_URL, init_db
from pipeline import fetch_raw_data, process_and_load_etl, load_all_history
from queries import get_overview_stats, get_kda_trend, get_agent_breakdown, get_map_stats
from charts import kda_trend, agent_breakdown, role_distribution, map_winrate, shot_accuracy,winrate_donut

engine = create_engine(DATABASE_URL)
init_db(drop_existing=False) 

QUEUE_MAP = {
    "competitive": {
        "kpi":["competitive"],
        "charts":["competitive"],
    },
    "unranked": {
        "kpi":["unrated", "swiftplay", "deathmatch"],   
        "charts":["unrated", "swiftplay"],                 
    },
}

form_row = dbc.Row([
    dbc.Col(
        dcc.Input(id="player-name", placeholder="username", type="text", className="form-control"),
        width=3
    ),
    dbc.Col(
        dcc.Input(id="player-tag", placeholder="tag", type="text", className="form-control"),
        width=2
    ),
    dbc.Col(
        dcc.Dropdown(id="queue-select",options=["Competitive", "Unranked"],value="Competitive"),
        width=3
    ),
    dbc.Col(
        html.Button("Analyze", id="submit-btn", className="btn btn-primary"),
        width=2
    ),
], className="mb-4", align="center")

kpi_row = dbc.Row([
    dbc.Col(
        dbc.Card(dbc.CardBody([
            html.P("Avg KDA", className="text-muted mb-1", style={"fontSize": "12px"}),
            html.H3(id="kpi-kda", className="mb-0"),
        ])), 
        width=4
    ),
    dbc.Col(
        dbc.Card(dbc.CardBody([
            html.P("Headshot %", className="text-muted mb-1", style={"fontSize": "12px"}),
            html.H3(id="kpi-hs", className="mb-0"),
        ])), 
        width=4
    ),
    dbc.Col(
        dbc.Card(dbc.CardBody([
            html.P("Win rate", className="text-muted mb-1", style={"fontSize": "12px"}),
            dcc.Graph(id="kpi-winrate-donut", config={"displayModeBar": False}),
        ], className="d-flex flex-column align-items-center")), 
        width=4
    ),
], className="mb-4")

main_row = dbc.Row([
    dbc.Col(
        dbc.Card(dbc.CardBody([
            dcc.Graph(id="chart-kda-trend", config={"displayModeBar": False}),
        ])), 
        width=8
    ),
    dbc.Col(
        dbc.Card(dbc.CardBody([
            dcc.Graph(id="chart-role-donut", config={"displayModeBar": False}),
        ])), 
        width=4
    ),
], className="mb-4")

bottom_row = dbc.Row([
    dbc.Col(
        dbc.Card(dbc.CardBody([
            dcc.Graph(id="chart-agent-breakdown", config={"displayModeBar": False}),
        ])),
        width=4
    ),
    dbc.Col(
        dbc.Card(dbc.CardBody([
            dcc.Graph(id="chart-map-winrate", config={"displayModeBar": False}),
        ])),
        width=4
    ),
    dbc.Col(
        dbc.Card(dbc.CardBody([
            dcc.Graph(id="chart-shot-accuracy", config={"displayModeBar": False}),
        ])),
        width=4
    ),
], className="mb-4")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    form_row,
    kpi_row,
    main_row,
    bottom_row,
], fluid=True)

@callback(
    Output("kpi-kda", "children"),
    Output("kpi-hs", "children"),
    Output("kpi-winrate-donut", "figure"),
    Output("chart-kda-trend", "figure"),
    Output("chart-role-donut", "figure"),
    Output("chart-agent-breakdown", "figure"),
    Output("chart-map-winrate", "figure"),
    Output("chart-shot-accuracy", "figure"),
    Input("submit-btn", "n_clicks"),
    State("player-name", "value"),
    State("player-tag", "value"),
    State("queue-select", "value"),
    prevent_initial_call=True,
)
def update_dashboard(n_clicks, name, tag, queue):
    if not name or not tag:
        raise dash.exceptions.PreventUpdate

    load_all_history(name, tag)

    queue_key = (queue or "Competitive").lower()
    q = QUEUE_MAP.get(queue_key, QUEUE_MAP["competitive"])

    stats     = get_overview_stats(engine, name, tag, q["kpi"])
    df_trend  = get_kda_trend(engine, name, tag, q["charts"])
    df_agents = get_agent_breakdown(engine, name, tag, q["charts"])
    df_maps   = get_map_stats(engine, name, tag, q["charts"])
    df_shots  = get_agent_breakdown(engine, name, tag, q["kpi"])

    trend_fig = kda_trend(df_trend)
    role_fig  = role_distribution(df_agents)
    agent_fig = agent_breakdown(df_agents)
    map_fig   = map_winrate(df_maps)
    shot_fig  = shot_accuracy(df_shots)
    donut_fig = winrate_donut(stats)

    return f"{stats['avg_kda']}", f"{stats['avg_hs_pct']}%", donut_fig, trend_fig, role_fig, agent_fig, map_fig, shot_fig