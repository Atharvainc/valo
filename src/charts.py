import plotly.graph_objects as go

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
        **LAYOUT_BASE, # type: ignore
        title='KDA trend',
        xaxis=dict(title='Match',tickmode='linear',dtick=5,gridcolor='rgba(0,0,0,0.05)',),
        yaxis=dict(title='kda',gridcolor='rgba(0,0,0,0.05)',rangemode='tozero'),
        hovermode='x unified',
    )
    return fig

def agent_breakdown(df)->go.Figure:
    fig=go.Figure()
    colors=df['agent_role'].map(ROLE_COLORS).tolist()
    fig.add_trace(go.Bar(x=df['avg_kda'],y=df['agent_name'],orientation='h',marker_color=colors,
                        customdata=df[['avg_kills','avg_deaths','avg_assists','avg_hs_pct','winrate']].values,
                        hovertemplate=('<b>%{y}</b><br>'
                                        'avg kda: %{x}<br>'
                                        'avg kills: %{customdata[0]}<br>'
                                        'avg deaths: %{customdata[1]}<br>'
                                        'avg assists: %{customdata[2]}<br>'
                                        'avg headshot%: %{customdata[3]}<br>'
                                        'winrate: %{customdata[4]}<extra></extra>'),
                        text=df['tot_matches'].apply(lambda n:f'n={n}'),
                        textposition='outside',
                        textfont=dict(size=10, color='#888780'),
                        ))
    fig.update_layout(
        **LAYOUT_BASE, # type: ignore
        title='Agent performance',
        xaxis=dict(title='Avg KDA',gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(title='',autorange='reversed')
    )
    return fig

def role_distribution(df)->go.Figure:
    fig=go.Figure()
    role_count=df.groupby('agent_role')['tot_matches'].sum().reset_index()
    fig.add_trace(go.Pie(labels=role_count['agent_role'],
                         values=role_count['tot_matches'],
                         hole=0.6,
                         marker=dict(colors=role_count['agent_role'].map(ROLE_COLORS)),
                         textinfo='label+percent',
                         hovertemplate='%{label}<br>%{value} matches (%{percent})<extra></extra>',
                         ))
    layout={**LAYOUT_BASE,'showlegend':True}
    fig.update_layout(
        **layout, #type: ignore
        title='Role distrtibution'
    )
    return fig

def map_winrate(df)->go.Figure:
    fig=go.Figure()
    fig.add_trace(go.Bar(x=df['map_name'],y=df['winrate'],orientation='v',
                         customdata=df[['tot_matches','avg_kda']].values,
                         hovertemplate=('<b>%{x}</b><br>'
                                        'winrate: %{y}%<br>'
                                        'avg KDA: %{customdata[1]}<br>'
                                        'matches played: %{customdata[0]}<extra></extra>'),))
    fig.update_layout(
        **LAYOUT_BASE, # type: ignore
        title='map winrate',
        xaxis=dict(title='',gridcolor='rgba(0,0,0,0)'),
        yaxis=dict(title='winrate',gridcolor='rgba(0,0,0,0.05)')
    )
    return fig

def shot_accuracy(df)->go.Figure:
    fig=go.Figure()
    fig.add_trace(go.Bar(name='head',x=df['agent_name'],y=df['avg_hs_pct'],marker_color='#EF4444',hovertemplate='%{x}<br>Head: %{y}%<extra></extra>',))
    fig.add_trace(go.Bar(name='body',x=df['agent_name'],y=df['avg_bs_pct'],marker_color='#F59E0B',hovertemplate='%{x}<br>Body: %{y}%<extra></extra>',))
    fig.add_trace(go.Bar(name='leg',x=df['agent_name'],y=df['avg_ls_pct'],marker_color='#5F5E5A',hovertemplate='%{x}<br>Leg: %{y}%<extra></extra>',))
    layout={**LAYOUT_BASE, "showlegend": True}
    fig.update_layout(
        **layout, #type: ignore
        barmode='stack',
        title='Shot accuracy',
        xaxis=dict(title=''),
        yaxis=dict(title='% of shots',gridcolor='rgba(0,0,0,0.05)')
    )
    return fig

def winrate_donut(stats: dict) -> go.Figure:
    wins = round(stats['win_rate'] / 100 * stats['total_matches'])
    losses = stats['total_matches'] - wins

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=['Wins', 'Losses'],
        values=[wins, losses],
        hole=0.7,
        marker=dict(colors=[WIN_COLOR, LOSS_COLOR]),
        textinfo='none',
        hoverinfo='label+value',
        sort=False,
    ))

    layout = {
        **LAYOUT_BASE,
        "margin": dict(l=0, r=0, t=0, b=0),   # overwrites LAYOUT_BASE's margin key
        "height": 140,
        "width": 140,
    }

    fig.update_layout(
        **layout,
        annotations=[dict(
            text=f"{stats['win_rate']}%<br><span style='font-size:11px;color:#888780'>{stats['total_matches']} games</span>",
            x=0.5, y=0.5,
            font=dict(size=20, color="#2C2C2A"),
            showarrow=False,
        )],
    )
    return fig