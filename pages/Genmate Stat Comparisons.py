from plotly.subplots import make_subplots
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def generation_names(gen):
    generations_full_name = [
        'Hololive JP 0th Generation', 'Hololive JP 1sh Generation', 'Hololive JP 2nd Generation',
        'GAMERS', 'Hololive JP 3rd Generation | hololive Fantasy', 'Hololive JP 4th Generation | holoForce',
        'Hololive JP 5th Generation | NePoLaBo', 'Hololive JP 6th Generation | holoX',
        'ID 1st Generation | AREA 15', 'ID 2nd Generation | holoro', 'ID 3rd Generation | holo3ro',
        'Hololive EN 1st Generation | holoMyth', 'Hololive EN 2nd Generation | holoCouncil + Project: HOPE',
        'Holostars JP 1st Generation', 'Holostars JP 2nd Generation | SunTempo', 'Holostars JP 3rd Generation | TriNero',
        'UPROAR!!', 'Holostars EN 1st Generation | TEMPUS HQ', 'Holostars EN 2nd Generation | TEMPUS Vanguard'
    ]
    return generations_full_name[generations.index(gen)]

def load_data():
    return pd.read_csv('data/data.csv',   index_col=[0]), \
           pd.read_csv('data/colors.csv', index_col=[0])

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
    </style>
    ''',
    unsafe_allow_html=True
)

df, colors = load_data()
df['count'] = df['count'].astype(int)
df['total_hrs'] = df['total_hrs'].astype(int)
df['avg_mins'] = df['avg_mins'].astype(int)

generation_members = {
    'live_jp_0': ['sora', 'roboco', 'miko', 'suisei', 'azki'],
    'live_jp_1': ['mel', 'fubuki', 'matsuri', 'haachama', 'aki'],
    'live_jp_2': ['aqua', 'shion', 'ayame', 'choco', 'subaru'],
    'gamers': ['mio', 'okayu', 'korone'],
    'live_jp_3': ['pekora', 'rushia', 'flare', 'noel', 'marine'],
    'live_jp_4': ['kanata', 'coco', 'watame', 'towa', 'luna'],
    'live_jp_5': ['lamy', 'nene', 'botan', 'polka'],
    'live_jp_6': ['laplus', 'lui', 'koyori', 'chloe', 'iroha'],
    'id_1': ['risu', 'moona', 'iofi'],
    'id_2': ['ollie', 'anya', 'reine'],
    'id_3': ['zeta', 'kaela', 'kobo'],
    'live_en_1': ['calli', 'kiara', 'ina', 'gura', 'ame'],
    'councilrys': ['irys', 'fauna', 'sana', 'kronii', 'mumei', 'bae'],
    'stars_jp_1': ['miyabi', 'kira', 'izuru', 'aruran', 'rikka'],
    'stars_jp_2': ['astel', 'temma', 'roberu'],
    'stars_jp_3': ['kaoru', 'shien', 'oga'],
    'uproar': ['fuma', 'uyu', 'gamma', 'rio'],
    'stars_en_1': ['altare', 'magni', 'axel', 'vesper'],
    'stars_en_2': ['bettel', 'flayon', 'hakka', 'shinri']
}
generations = [
    'live_jp_0', 'live_jp_1', 'live_jp_2',
    'gamers', 'live_jp_3', 'live_jp_4',
    'live_jp_5', 'live_jp_6',
    'id_1', 'id_2', 'id_3',
    'live_en_1', 'councilrys',
    'stars_jp_1', 'stars_jp_2', 'stars_jp_3',
    'uproar', 'stars_en_1', 'stars_en_2'
]

gen = st.selectbox('Generation:', generations, format_func=generation_names)
gen = generation_members[gen]
names = df.loc[gen, 'full_name'].to_list()
# arrange values to 2x2 grid
values = [[df.loc[gen, col_name].to_list() for col_name in ['count', 'total_hrs']],
          [df.loc[gen, col_name].to_list() for col_name in ['avg_mins', 'hrs_p_wk']]]
gen_colors = [f'#{hex}' for hex in colors.loc[gen, 'most'].to_list()]

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
    go.Layout(
        legend=dict(orientation='h'),
        margin=dict(l=50, r=0, t=50, b=0)
    ),
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