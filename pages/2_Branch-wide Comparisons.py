import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title='Hololive Production Livestream Activity Statistics',
    initial_sidebar_state='collapsed',
    layout='wide',
    menu_items={
        'About': '''
            ##### Hololive Production Livestream Activity Statistics

            Based on YouTube livestreams up to January 18, 2023, queried through Holodex API.
        '''
    }
)

st.markdown(
    '''
    <style>
        ul[aria-activedescendant] ul[role="option"]:nth-child(n+3):nth-child(-n+7),
        ul[aria-activedescendant] div:nth-child(n+1):nth-child(-n+5),
        div[data-testid="stDecoration"], iframe, footer {
            display: none !important;
        }
        .main .block-container {
            padding-top: 40px;
        }
    </style>
    ''',
    unsafe_allow_html=True
)    

def ordinal_suffix(n):
    if n % 100 in (11, 12, 13):
        return 'th'
    else:
        return { 1: 'st', 2: 'nd', 3: 'rd' }.get(n % 10, 'th')\

def make_chart(col_name, chart_title):
    sub_df = branch.sort_values(col_name)[['full_name', col_name]]
    values = sub_df[col_name].to_list()
    names = sub_df.index.to_list()
    colors_done = []
    counter = len(sub_df)

    fig = go.Figure()
    for value, name, in zip(values, names):
        gen_color = generation_colors_names.loc[name, 'color']
        full_name = sub_df.loc[name, 'full_name']
        fig.add_trace(
            go.Bar(
                y=[value],
                x=[full_name],
                text=value,
                textposition='outside',
                hovertemplate=f'{counter}{ordinal_suffix(counter)}, {value}, {full_name}',
                marker=dict(color=gen_color),
                # one legend per generation and only show at 1st chart
                showlegend=True if gen_color not in colors_done and col_name == 'count' else False,
                legendrank=generation_colors_names.loc[name, 'rank'],
                name=generation_colors_names.loc[name, 'gen_name_1']
            )
        )
        colors_done.append(gen_color)
        counter -= 1

    fig.update_layout(
        go.Layout(
            legend=dict(orientation='h', x=center_val, y=1.13),
            margin=dict(l=0, r=0, t=50, b=0)
        ),
        title=chart_title,
        height=500,
        yaxis=dict(visible=False)
    )
    fig.update_yaxes(fixedrange=True)
    st.plotly_chart(fig, use_container_width=True)

df = pd.read_csv('data/data.csv', index_col=[0])
colors = pd.read_csv('data/colors.csv', index_col=[0])
generation_colors_names = pd.read_csv('data/generation_colors_names.csv', index_col=[0])
df.drop('hololive', inplace=True)
df['count'] = df['count'].astype(int)
df['total_hrs'] = df['total_hrs'].astype(int)
df['avg_mins'] = df['avg_mins'].astype(int)

col_name_and_title = {
    'count': 'Total Streams',
    'total_hrs': 'Total Hours',
    'avg_mins': 'Average Minutes per Stream',
    'hrs_p_wk': 'Average Hours per Week'
}

branch = st.selectbox('Branch:', ['Hololive', 'Holostars'])
if branch == 'Hololive':
    branch = df.iloc[:57] 
    center_val = 0.25
else:
    branch = df.iloc[57:]
    center_val = 0.37

for col_name, chart_title in col_name_and_title.items():
    make_chart(col_name, chart_title)