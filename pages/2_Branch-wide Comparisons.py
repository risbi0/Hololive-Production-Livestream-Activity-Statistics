from init import init_page_config, init_markdown
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

init_page_config()
init_markdown()

def ordinal_suffix(n):
    if n % 100 in (11, 12, 13):
        return 'th'
    else:
        return { 1: 'st', 2: 'nd', 3: 'rd' }.get(n % 10, 'th')

def make_chart(col_name, chart_title):
    sub_df = branch.sort_values(col_name)[['full_name', col_name]]
    values = sub_df[col_name].to_list()
    names = sub_df.index.to_list()
    colors_done = []
    counter = len(sub_df)

    fig = go.Figure()
    for name, value in zip(names, values):
        gen_color = generation_colors_names.loc[name, 'color']
        full_name = sub_df.loc[name, 'full_name']
        fig.add_trace(
            go.Bar(
                x=[full_name],
                y=[value],
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
        title=chart_title,
        legend=dict(orientation='h', x=center_val, y=1.13),
        margin=dict(l=0, r=0, t=50, b=0),
        height=500,
        yaxis=dict(visible=False)
    )
    fig.update_yaxes(fixedrange=True)
    st.plotly_chart(fig, use_container_width=True)

df = pd.read_csv('data/data.csv', index_col=[0])
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

st.markdown('''<h4>Branch-wide Comparisons</h4>''', unsafe_allow_html=True)
branch = st.selectbox('Branch:', ['Hololive', 'Holostars'])
if branch == 'Hololive':
    branch = df.iloc[:57] 
    center_val = 0.25
else:
    branch = df.iloc[57:]
    center_val = 0.37

for col_name, chart_title in col_name_and_title.items():
    make_chart(col_name, chart_title)