import plotly.graph_objects as go
import plotly.express as px

ROLE_COLORS={
    'Duelist':'#7C3AED',
    'Controller':'#0F6E56',
    'Sentinel':'#993C1D',
    'Initiators':'#0EA5E9',
    'Unknown':'#5F5E5A'
}

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",  
    plot_bgcolor="rgba(0,0,0,0)",   
    font=dict(family="sans-serif", size=12, color="#888780"),
    margin=dict(l=16, r=16, t=32, b=16),
    showlegend=False,
)

def kda_trend(df)->go.Figure:
    fig=go.Figure()
    
    return fig



