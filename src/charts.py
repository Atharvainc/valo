import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import create_engine
from db_setup import DATABASE_URL
from queries import get_kda_trend


ROLE_COLORS = {
    "Duelist":    "#7C3AED",   
    "Controller": "#0EA5E9",   
    "Sentinel":   "#F59E0B", 
    "Initiator":  "#EC4899",   
    "Unknown":    "#5F5E5A",   
}
WIN_COLOR="#1D9E75"
LOSS_COLOR="#D85A30"

LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",  
    plot_bgcolor="rgba(0,0,0,0)",   
    font=dict(family="sans-serif", size=12, color="#888780"),
    margin=dict(l=16, r=16, t=32, b=16),
    showlegend=False,
)

def kda_trend(df)->go.Figure:
    fig=go.Figure()
    for _,row in df.iterrows():
        color=WIN_COLOR if row['won']==1 else LOSS_COLOR
        fig.add_vrect(
            x0=row['match_num']-0.5,
            x1=row['match_num']+0.5,
            fillcolor=color,
            opacity=0.12,
            layer='below',
            line_width=0,
            )
    #kda trend line
    fig.add_trace(go.Scatter(
        x=df['match_num'],y=df['kda'],mode='lines+markers',name='KDA',line=dict(color="#B4B2A9", width=1.5),marker=dict(size=5),
        customdata=df[['agent_name','map_name','kills','deaths','assists']].values,
        hovertemplate=('Match %{x}<br>'
                        'KDA: %{y}<br>'
                        'Agent: %{customdata[0]}<br>'
                        'Map: %{customdata[1]}<br>'
                        'K/D/A: %{customdata[2]}/%{customdata[3]}/%{customdata[4]}'
                        '<extra></extra>'),
                    ))
    #rolling avg
    fig.add_trace(go.Scatter(
        x=df['match_num'],
        y=df['rolling_avg'],
        mode='lines',
        name='5-game avg',
        line=dict(color='#534AB7',width=2.5),
        hovertemplate=('5 game avg:%{y}<extra></extra>'),
    ))
    fig.update_layout(
    title='KDA trend',
    xaxis=dict(title='Match',tickmode='linear',dtick=5,gridcolor='rgba(0,0,0,0.05)',),
    yaxis=dict(title='kda',gridcolor='rgba(0,0,0,0.05)',rangemode='tozero'),
    hovermode='x unified',
)
    return fig

def get_agent_breakdown(df)->go.Figure:
    fig=go.Figure()
    for _,row in df.iterrows():
        color=ROLE_COLORS[row['agent_role']]
    return fig



if __name__=='__main__':
    engine=create_engine(DATABASE_URL)
    df=get_kda_trend(engine,'competitive')
    fig=kda_trend(df)
    fig.show()
