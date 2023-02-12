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

df = pd.read_csv('data/data.csv', index_col=[0])
generation_colors_names = pd.read_csv('data/generation_colors_names.csv', index_col=[0])

st.markdown('''<h4>Top in Topics by Hours Streamed</h4>''', unsafe_allow_html=True)
st.caption('Top 20 for Hololive. Top 10 for Holostars.')

topics = {
    'apex': 'Apex Legends',
    'membersonly': 'Members-only',
    'minecraft': 'Minecraft',
    'Superchat_Reading': 'Superchat Reading',
    'singing': 'Singing',
    'talk': 'Zatsudan'
}
branch = st.selectbox('Branch:', ['Hololive', 'Holostars'])
if branch == 'Holostars': topics.pop('Superchat_Reading')
cols = [st.columns([1, 1]) for _ in range(3)]
index = 0

for topic, chart_title in topics.items():
    topics_df = pd.read_csv(f'data/{branch.lower()}_{topic}.csv', index_col=[0], header=None)
    colors_done = []
    counter = len(topics_df)

    fig = go.Figure()
    for name, value in topics_df.iterrows():
        gen_color = generation_colors_names.loc[name, 'color']
        full_name = df.loc[name, 'full_name']
        fig.add_trace(
            go.Bar(
                x=[int(value)],
                y=[full_name],
                orientation='h',
                text=value,
                textposition='outside',
                hovertemplate=f'{counter}{ordinal_suffix(counter)}, {int(value)}, {full_name}',
                marker=dict(color=gen_color),
                # one legend per generation
                showlegend=True if gen_color not in colors_done  else False,
                legendrank=generation_colors_names.loc[name, 'rank'],
                name=generation_colors_names.loc[name, 'gen_name_1']
            )
        )
        colors_done.append(gen_color)
        counter -= 1

    fig.update_layout(
        title=dict(text=chart_title),
        legend=dict(x=1, xanchor='right', y=0),
        margin=dict(l=0, r=0, t=50, b=0),
        height=500,
        xaxis=dict(visible=False, range=[0, max(topics_df[1]) * 1.1])
    )
    fig.update_xaxes(fixedrange=True)
    
    cols[index // 2][index % 2].plotly_chart(fig, use_container_width=True)
    index += 1