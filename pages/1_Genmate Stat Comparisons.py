from init import init_page_config, init_markdown
from plotly.subplots import make_subplots
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os

init_page_config()
init_markdown()

df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/data.csv'), index_col=[0])
details = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/details.csv'), index_col=[0])
df['count'] = df['count'].astype(int)
df['total_hrs'] = df['total_hrs'].astype(int)
df['avg_mins'] = df['avg_mins'].astype(int)

st.markdown('''<h4>Genmate Stat Comparisons</h4>''', unsafe_allow_html=True)
st.caption('Comparing livestream count, total hours, average minutes per stream, and average hours per week by generation.')
st.caption('Average hours per week is calculated from the week of the debut date up to the week of the graduation or termination date. A special case for Magni Dezmond and Noir Vesper; their end date is July 7, 2023 which is the last date both have streamed.')
gen_name = st.selectbox('Generation:', details['gen_name'].dropna().unique().tolist())
gen_members = details[details['gen_name'] == gen_name].index.tolist()
names = details.loc[gen_members, 'full_name'].to_list()
# arrange values to 2x2 grid
values = [[df.loc[gen_members, col_name].to_list() for col_name in ['count', 'total_hrs']],
          [df.loc[gen_members, col_name].to_list() for col_name in ['avg_mins', 'hrs_p_wk']]]
gen_colors = [f'#{hex}' for hex in details.loc[gen_members, 'most'].to_list()]

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Livestream Count', 'Total Hours', 'Average Minutes per Stream', 'Average Hours per Week'),
    vertical_spacing=0.1,
    horizontal_spacing=0
)

for row in range(2):
    for col in range(2):
        index = 0
        for name, value, color in zip(names, values[row][col], gen_colors):
            fig.add_trace(
                go.Bar(
                    x=[value],
                    y=[name],
                    text=values[row][col][index],
                    textposition='outside',
                    orientation='h',
                    hoverinfo='x,y',
                    name=name,
                    marker_color=color,
                    showlegend=row == 1 and col == 1
                ),
                row=row + 1,
                col=col + 1,
            )
            index += 1

fig.update_layout(
    legend=dict(orientation='h'),
    margin=dict(l=50, r=0, t=50, b=0),
    height=800,
    xaxis1=dict(visible=False, range=[0, max(values[0][0]) * 1.2]),
    yaxis1=dict(visible=False),
    xaxis2=dict(visible=False, range=[0, max(values[0][1]) * 1.2]),
    yaxis2=dict(visible=False),
    xaxis3=dict(visible=False, range=[0, max(values[1][0]) * 1.2]),
    yaxis3=dict(visible=False),
    xaxis4=dict(visible=False, range=[0, max(values[1][1]) * 1.2]),
    yaxis4=dict(visible=False)
)
fig.update_xaxes(fixedrange=True)
fig.update_yaxes(fixedrange=True)

st.plotly_chart(fig, use_container_width=True)
