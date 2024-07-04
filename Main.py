from init import init_page_config, init_markdown
from plotly.subplots import make_subplots
from streamlit import session_state as ss
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math, calendar

init_page_config()
init_markdown()

st.markdown(
    '''
    <style>
        h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
            display: none !important;
        }
        h2, h4, h5 {
            text-align: center;
        }
        img {
            width: 100%;
            border: 3px solid transparent;
            margin-bottom: 20px;
        }
        img:hover {
            padding: 0 !important;
            border-style: solid !important;
        }
        .main .block-container {
            padding-top: 0;
        }
        div.stSelectbox label {
            margin-top: 30px !important;
        }
        .stats {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .stats p:nth-child(1) {
            margin-bottom: -5px;
            font-size: 20px;
            font-weight: bold;
        }
        .stats p:nth-child(2) {
            font-size: 18px;
        }
        #heatmap-title {
            font-weight: bold;
            margin-bottom: -20px;
        }
        div[data-testid="column"]:nth-child(2) p {
            text-align: right;
        }
    </style>
    ''',
    unsafe_allow_html=True
)

def plural(n):
    return 's' if int(n) != 1 else ''

def display_individual_stats():
    hrs_dd_hh_mm = df.loc[name, 'total_f'].split(':')
    avg_mins_hh_mm = df.loc[name, 'avg_f'].split(':')
    stat_headers = ['Total Livestreams', 'Total Hours', 'Average Duration per Stream']
    stat_details = [
        f"{round(df.loc[name, 'count']):,}",
        f"{round(df.loc[name, 'total_hrs']):,} ({hrs_dd_hh_mm[0]} days, {hrs_dd_hh_mm[1].lstrip('0') if hrs_dd_hh_mm[1].lstrip('0') != '' else '0'} hour{plural(hrs_dd_hh_mm[1])}, {hrs_dd_hh_mm[2].lstrip('0')} minute{plural(hrs_dd_hh_mm[2])})",
        f"{avg_mins_hh_mm[0]} hour{plural(avg_mins_hh_mm[0])}, {avg_mins_hh_mm[1].lstrip('0') if avg_mins_hh_mm[1].lstrip('0') != '' else '0'} minute{plural(avg_mins_hh_mm[1])}"
    ]

    col = st.columns(3)
    for i in range(len(col)):
        col[i].markdown(f'''
            <div class='stats'>
                <p>{stat_headers[i]}</p>
                <p>{stat_details[i]}</p>
            </div>''',
            unsafe_allow_html=True
        )

def display_heatmap():
    times = [f'{str(i // 60).zfill(2)}:{str(i % 60).zfill(2)}' for i in range(0, 1440)]
    days_short = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    heatmap_df = pd.read_csv(f'data/{name}/heatmap.csv', header=None)
    # shift data according to timezone difference
    heatmap_df = pd.DataFrame(np.roll(heatmap_df.values.flatten(), time_offset).reshape(7, -1))
    heatmap = make_subplots(rows=7, cols=1, vertical_spacing=0)

    # make heatmaps for each row then combine them
    for index, row in heatmap_df.iterrows():
        # custom tooltip
        tooltip = list()
        tooltip.append(list())
        for i, time in enumerate(times):
            tooltip[-1].append(f'Time: {time}<br />Day: {days[index]}<br />Count: {row[i]}')

        row_arr = row.to_numpy()
        sub_fig = go.Heatmap(
            y=[days_short[index]],
            z=[row_arr],
            zmin=np.min(row_arr[np.nonzero(row_arr)]), # min value except 0
            zmax=np.max(row_arr),
            colorscale=[
                [0, opp_color], # only zeroes as separate color
                [0.0000000000000000001, sub_color],
                [1, main_color]
            ],
            showscale=False,
            # replace x y z tooltip with custom-named one
            hoverinfo='text',
            text=tooltip,
            # remove 'trace x' on hover tooltip
            hoverlabel=dict(namelength=0)
        )
        heatmap.append_trace(sub_fig, index + 1, 1)

    heatmap.update_xaxes(
        tickvals=list(range(30, 1440, 60)),
        ticktext=list(range(0, 24)),
        fixedrange=True
    )
    heatmap.update_yaxes(fixedrange=True)
    heatmap.update_layout(
        title=f'Livestream Timeseries Heatmap {time_offset}',
        height=445,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(heatmap, use_container_width=True)
    st.caption('''
        Cumulative frequency of streams in each of the week. Data points down to the minute.
        Lightest and darkest tint represent the least and most frequent times of the day respectively.
        Opposite color of the darkest tint represent 0 streaming times.
    ''')

def bar_chart(name, col_name, x_labels, title, x_title, y_title):
    # comma-delimited string to list
    data = [int(i) for i in df.loc[name, col_name].split(',')]
    bar_fig = go.Figure(
        go.Bar(
            x=x_labels,
            y=data,
            marker=dict(color=main_color),
            hoverinfo='x,y',
            text=data,
            textposition='outside'
        )
    )
    bar_fig.update_layout(
        title=dict(text=title),
        height=500,
        xaxis=dict(type='category', fixedrange=True),
        yaxis=dict(fixedrange=True)
    )
    bar_fig.update_xaxes(title_text=x_title)
    bar_fig.update_yaxes(title_text=y_title)

    return bar_fig

def display_hour_and_day_charts():
    hour_x_labels = [f'{i}-{i + 1}' for i in range(12)]
    hour_bar = bar_chart(
        name=name,
        col_name='hour_data',
        x_labels=hour_x_labels,
        title='Stream Duration Count',
        x_title='Duration (hours)',
        y_title='Streams'
    )
    hour_bar.update_layout(
        height=450,
        margin=dict(t=50, b=0)
    )
    weekday_bar = bar_chart(
        name=name,
        col_name='weekday_data',
        x_labels=days,
        title='Cumulative Streaming Days',
        x_title='Day of the Week',
        y_title='Streams'
    )
    weekday_bar.update_layout(
        height=450,
        margin=dict(t=50, b=0)
    )
    hour_col, weekday_col = st.columns([3, 2])
    hour_col.plotly_chart(hour_bar, use_container_width=True)
    weekday_col.plotly_chart(weekday_bar, use_container_width=True)
    weekday_col.caption('Follows JST timezone (UTC+09:00).')

def topic_bar(index, color):
    return go.Bar(
        x=topics[index].tolist(),
        y=topics.index.tolist(),
        xaxis=f'x{index}',
        offsetgroup=index,
        orientation='h',
        marker=dict(color=color),
        hoverinfo='x,y',
        text=topics[index].tolist(),
        textposition='outside'
    )

def display_archive_and_topics_charts():
    topics_legend = ['Streams', 'Duration (hours)']
    unarchived = df.loc[name, 'missing']
    archived = df.loc[name, 'count'] - unarchived
    archive_health = go.Figure(
        go.Pie(
            values=[archived, unarchived],
            labels=['Archived', 'Unarchived'],
            textposition='outside',
            sort=False
        )
    )
    archive_health.update_traces(
        hoverinfo='percent',
        textinfo='value',
        marker=dict(colors=[main_color, opp_color])
    )
    archive_health.update_layout(
        title=dict(text='Archive Health'),
        margin=dict(l=0, r=0, t=70, b=15)
    )

    # set range depending on max number
    max_streams = max(topics[1].tolist())
    max_hrs = max(topics[2].tolist())
    (ax1_limit, add_1) = (50, 25) if max_streams > 100 else (5, 1)
    (ax2_limit, add_2) = (50, 25) if max_hrs > 100 else (5, 1)

    topics_bar = go.Figure([
            topic_bar(1, main_color), # hours
            topic_bar(2, sub_color) # count
    ])
    topics_bar.update_layout(
        title=dict(text='Top 10 Topics'),
        margin=dict(l=0, r=0, t=70, b=0),
        height=500,
        xaxis1=dict(
            title='Streams',
            range=[0, math.ceil((max_streams + add_1) / ax1_limit) * ax1_limit],
            fixedrange=True
        ),
        xaxis2=dict(
            title='Duration (hours)',
            overlaying='x',
            side='top',
            range=[0, math.ceil((max_hrs + add_2) / ax2_limit) * ax2_limit],
            fixedrange=True
        ),
        yaxis=dict(fixedrange=True),
        legend=dict(
            yanchor='bottom',
            y=0,
            xanchor='right',
            x=1
        ),
        legend_traceorder='reversed'
    )
    topics_bar.update_yaxes(showgrid=True)

    for index, trace in enumerate(topics_bar.data):
        trace.update(name=topics_legend[index])

    ah_col, topic_col = st.columns([2, 3])
    ah_col.plotly_chart(archive_health, use_container_width=True)
    topic_col.plotly_chart(topics_bar, use_container_width=True)
    topic_col.caption('Topics provided by Holodex. Sorted by duration.')

def display_longest_stream():
    st.markdown(f'''
        <div class='stats'>
            <h4>Longest Stream</h4>
        </div>''',
        unsafe_allow_html=True
    )
    cols = st.columns(3)
    cols[1].markdown(f'''
        <a href="{f"https://youtube.com/watch?v={df.loc[name, 'long_id']}"}" target="_blank">
            <img
                src="{f"https://i.ytimg.com/vi/{df.loc[name, 'long_id']}/maxresdefault.jpg"}"
                style="padding: 3px; border: 3px hidden {main_color};"
            >
        </a>''',
        unsafe_allow_html=True
    )

    stream_details = [
        f"{df.loc[name, 'long_title']}",
        f"{df.loc[name, 'long_date']}",
        f'''{round(df.loc[name, 'long_length'] // 60)} hour{plural(round(df.loc[name, 'long_length'] // 60))},
            {round(df.loc[name, 'long_length'] % 60)} minute{plural(round(df.loc[name, 'long_length'] % 60))}'''
    ]
    for detail in stream_details:
        st.markdown(f'''
            <div class='stats'>
                <h5>{detail}</h5>
            </div>''',
            unsafe_allow_html=True
        )

    st.caption('<div class="stats">Earliest longest archived stream. Rounded to the nearest minute.</div>', unsafe_allow_html=True)

def display_hrs_per_week():
    year_weeks = hrs_per_week.index.to_list()
    hours = hrs_per_week['hours'].to_list()

    bar_chart = go.Figure()
    for year_week, hour in zip(year_weeks, hours):
        bar_chart.add_trace(
            go.Bar(
                x=[year_week],
                y=[hour],
                hovertemplate=f'{year_week}, {hour}<extra></extra>',
                marker=dict(color=main_color),
                showlegend=False
            )
        )
    bar_chart.update_layout(
        title='Hours per Week',
        margin=dict(l=0, r=0, t=50, b=0),
        width=1500,
        xaxis_type='category'
    )
    bar_chart.update_xaxes(title_text='Year-Week')
    bar_chart.update_yaxes(title_text='Hours')
    bar_chart.update_yaxes(fixedrange=True)
    st.plotly_chart(bar_chart, use_container_width=True)
    st.caption('A week is from Sunday to Saturday at UTC+9. (Tip: You can crop to a specific time range by click and dragging horizontally.)')

def to_timezone(mins):
    timezone_abbr = [
        'BIT / IDLW',
        'NUT / SST',
        'HST / SDT / TAHT',
        'MART',
        'AKST / HDT',
        'PST',
        'MST / PDT',
        'CST / MDT',
        'EST / CDT',
        'EDT / CLT / PYT / VET',
        'NST',
        'BRT / GFT / UYT',
        'GST',
        'AZOT / CVT',
        'WET / GMT / UTC',
        'CET / WAT / WEST / BST',
        'EET / CAT / CEST / WAST',
        'EAT / AST / EEST / IDT / MSK',
        'IRST',
        'AZT / GET / GST',
        'AFT',
        'PKT / TMT / UZT',
        'IST / SLST',
        'NPT',
        'BST / BTT / KGT',
        'MMT',
        'ICT / WIB',
        'CST / MYT / PHT / SGT / AWST',
        'AWCST',
        'JST / KST',
        'ACST',
        'AEST / PGT',
        'ACDT / LHST',
        'NCT / SBT / AEDT',
        'NZST / FJT',
        'CHAST',
        'TOT / NZDT',
        'LINT'
    ]
    sign = '+' if mins >= -540 else '-'
    return f'(UTC{sign}{str(abs(9 + mins // 60)).zfill(2)}:{str(mins % 60).zfill(2)}) {timezone_abbr[time_offsets.index(mins)]}'

df = pd.read_csv('data/data.csv', index_col=[0])
details = pd.read_csv('data/details.csv', index_col=[0])
days = list(calendar.day_name)
days = days[-1:] + days[:-1] # shift Sunday to 1st position, being the 1st day of the week
time_offsets = [
    -1260, -1200, -1140, -1050, -1080, -1020, -960, -900, -840, -780,
    -690, -720,  -660, -600, -540, -480, -420, -360, -330, -300,
    -270, -240, -210, -195, -180, -150, -120, -60, -15, 0,
    30, 60, 90, 120, 180, 225, 240, 300
]

# holomem selection (WARNING: Very non-DRY code. Still I chose this over having 1 long column of names.)
# radio buttons
with st.container(height=215):
    r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns(5)
    l_jp_0 = r1c1.radio('0th Gen (and official)', ['Hololive', 'Tokino Sora', 'Roboco', 'Sakura Miko', 'Hoshimachi Suisei', 'AZKi'], index=0)
    l_jp_1 = r1c2.radio('1st Gen', ['Yozora Mel', 'Shirakami Fubuki', 'Natsuiro Matsuri', 'Akai Haato', 'Aki Rosenthal'], index=None)
    l_jp_2 = r1c3.radio('2nd Gen', ['Minato Aqua', 'Murasaki Shion', 'Nakiri Ayame', 'Yuzuki Choco', 'Oozora Subaru'], index=None)
    l_jp_g = r1c4.radio('GAMERS', ['Ookami Mio', 'Nekomata Okayu', 'Inugami Korone'], index=None)
    l_jp_3 = r1c5.radio('hololive Fantasy', ['Usada Pekora', 'Uruha Rushia', 'Shiranui Flare', 'Shirogane Noel', 'Houshou Marine'], index=None)
    r2c1, r2c2, r2c3, r2c4, _ = st.columns(5)
    l_jp_4 = r2c1.radio('holoForce', ['Amane Kanata', 'Kiryu Coco', 'Tsunomaki Watame', 'Tokoyami Towa', 'Himemori Luna'], index=None)
    l_jp_5 = r2c2.radio('NePoLaBo', ['Yukihana Lamy', 'Momosuzu Nene', 'Shishiro Botan', 'Omaru Polka'], index=None)
    l_jp_6 = r2c3.radio('holoX', ['La+ Darknesss', 'Takane Lui', 'Hakui Koyori', 'Sakamata Chloe', 'Kazama Iroha'], index=None)
    l_jp_d = r2c4.radio('ReGLOSS', ['Hiodoshi Ao', 'Otonose Kanade', 'Ichijou Ririka', 'Juufuutei Raden', 'Todoroki Hajime'], index=None)
    r3c1, r3c2, r3c3, r3c4, _ = st.columns(5)
    l_en_1 = r3c1.radio('Myth', ['Mori Calliope', 'Takanashi Kiara', 'Ninomae Ina\'nis', 'Gawr Gura', 'Watson Amelia'], index=None)
    l_en_2 = r3c2.radio('CouncilRys', ['IRyS', 'Ceres Fauna', 'Tsukumo Sana', 'Ouro Kronii', 'Nanashi Mumei', 'Hakos Baelz'], index=None)
    l_en_3 = r3c3.radio('Advent', ['Shiori Novella', 'Koseki Bijou', 'Nerissa Ravencroft', 'Fuwamoco Abyssguard'], index=None)
    l_en_4 = r3c4.radio('Justice', ['Elizabeth Rose Bloodflame', 'Gigi Murin', 'Cecilia Immergreen', 'Raora Panthera'], index=None)
    r4c1, r4c2, r4c3, _, _ = st.columns(5)
    l_id_1 = r4c1.radio('AREA 15', ['Ayunda Risu', 'Moona Hoshinova', 'Airani Iofifteen'], index=None)
    l_id_2 = r4c2.radio('holoro', ['Kureiji Ollie', 'Anya Melfissa', 'Pavolia Reine'], index=None)
    l_id_3 = r4c3.radio('holo3ro', ['Vestia Zeta', 'Kaela Kovalskia', 'Kobo Kanaeru'], index=None)
    r5c1, r5c2, r5c3, r5c4, _ = st.columns(5)
    s_jp_1 = r5c1.radio('1st Gen', ['Hanasaki Miyabi', 'Kagami Kira', 'Kanade Izuru', 'Arurandeisu', 'Rikka'], index=None)
    s_jp_2 = r5c2.radio('SunTempo', ['Astel Leda', 'Kishido Temma', 'Yukoku Roberu'], index=None)
    s_jp_3 = r5c3.radio('TriNero', ['Tsukishita Kaoru', 'Kageyama Shien', 'Aragami Oga'], index=None)
    s_jp_u = r5c4.radio('UPROAR!!', ['Yatogami Fuma', 'Utsugi Uyu', 'Hizaki Gamma', 'Minase Rio'], index=None)
    r6c1, r6c2, r6c3, _, _ = st.columns(5)
    s_en_h = r6c1.radio('TEMPUS HQ', ['Regis Altare', 'Magni Dezmond', 'Axel Syrios', 'Noir Vesper'], index=None)
    s_en_v = r6c2.radio('TEMPUS Vanguard', ['Josuiji Shinri', 'Machina X Flayon', 'Banzoin Hakka', 'Gavis Bettel'], index=None)
    s_en_a = r6c3.radio('ARMIS', ['Jurard T Rexford', 'Goldbullet', 'Octavio', 'Crimson Ruze'], index=None)

# initialize session states
if 'current' not in ss:
    ss.current = 'Hololive'

if all(e not in ss for e in ['l_jp_0', 'l_jp_1', 'l_jp_2', 'l_jp_g', 'l_jp_3', 'l_jp_4', 'l_jp_5', 'l_jp_6', 'l_jp_d', 'l_en_1', 'l_en_2', 'l_en_3', 'l_en_4', 'l_id_1', 'l_id_2', 'l_id_3', 's_jp_1', 's_jp_2', 's_jp_3', 's_jp_u', 's_en_h', 's_en_v', 's_en_a']):
    ss.l_jp_0 = None
    ss.l_jp_1 = None
    ss.l_jp_2 = None
    ss.l_jp_g = None
    ss.l_jp_3 = None
    ss.l_jp_4 = None
    ss.l_jp_5 = None
    ss.l_jp_6 = None
    ss.l_jp_d = None
    ss.l_en_1 = None
    ss.l_en_2 = None
    ss.l_en_3 = None
    ss.l_en_4 = None
    ss.l_id_1 = None
    ss.l_id_2 = None
    ss.l_id_3 = None
    ss.s_jp_1 = None
    ss.s_jp_2 = None
    ss.s_jp_3 = None
    ss.s_jp_u = None
    ss.s_en_h = None
    ss.s_en_v = None
    ss.s_en_a = None

# session state management
if l_jp_0 != ss.l_jp_0:
    ss.current = l_jp_0
    ss.l_jp_0 = l_jp_0
if l_jp_1 != ss.l_jp_1:
    ss.current = l_jp_1
    ss.l_jp_1 = l_jp_1
if l_jp_2 != ss.l_jp_2:
    ss.current = l_jp_2
    ss.l_jp_2 = l_jp_2
if l_jp_g != ss.l_jp_g:
    ss.current = l_jp_g
    ss.l_jp_g = l_jp_g
if l_jp_3 != ss.l_jp_3:
    ss.current = l_jp_3
    ss.l_jp_3 = l_jp_3
if l_jp_4 != ss.l_jp_4:
    ss.current = l_jp_4
    ss.l_jp_4 = l_jp_4
if l_jp_5 != ss.l_jp_5:
    ss.current = l_jp_5
    ss.l_jp_5 = l_jp_5
if l_jp_6 != ss.l_jp_6:
    ss.current = l_jp_6
    ss.l_jp_6 = l_jp_6
if l_jp_d != ss.l_jp_d:
    ss.current = l_jp_d
    ss.l_jp_d = l_jp_d
if l_en_1 != ss.l_en_1:
    ss.current = l_en_1
    ss.l_en_1 = l_en_1
if l_en_2 != ss.l_en_2:
    ss.current = l_en_2
    ss.l_en_2 = l_en_2
if l_en_3 != ss.l_en_3:
    ss.current = l_en_3
    ss.l_en_3 = l_en_3
if l_en_4 != ss.l_en_4:
    ss.current = l_en_4
    ss.l_en_4 = l_en_4
if l_id_1 != ss.l_id_1:
    ss.current = l_id_1
    ss.l_id_1 = l_id_1
if l_id_2 != ss.l_id_2:
    ss.current = l_id_2
    ss.l_id_2 = l_id_2
if l_id_3 != ss.l_id_3:
    ss.current = l_id_3
    ss.l_id_3 = l_id_3
if s_jp_1 != ss.s_jp_1:
    ss.current = s_jp_1
    ss.s_jp_1 = s_jp_1
if s_jp_2 != ss.s_jp_2:
    ss.current = s_jp_2
    ss.s_jp_2 = s_jp_2
if s_jp_3 != ss.s_jp_3:
    ss.current = s_jp_3
    ss.s_jp_3 = s_jp_3
if s_jp_u != ss.s_jp_u:
    ss.current = s_jp_u
    ss.s_jp_u = s_jp_u
if s_en_h != ss.s_en_h:
    ss.current = s_en_h
    ss.s_en_h = s_en_h
if s_en_v != ss.s_en_v:
    ss.current = s_en_v
    ss.s_en_v = s_en_v
if s_en_a != ss.s_en_a:
    ss.current = s_en_a
    ss.s_en_a = s_en_a

holo_select_caption, tz_col = st.columns([4, 1])
holo_select_caption.caption('Excuse the scuffness. Streamlit\'s API is quite limited.')
time_offset = tz_col.selectbox('Heatmap Timezone:', time_offsets, index=29, format_func=to_timezone) # default to JP timzone

name = df.index[details['full_name'] == ss.current][0]
main_color = f"#{details.loc[name, 'most']}"
sub_color = f"#{details.loc[name, 'least']}"
opp_color = f"#{details.loc[name, 'zero']}"
topics = pd.read_csv(f'data/{name}/topics.csv', header=None, index_col=[0])
hrs_per_week = pd.read_csv(f'data/{name}/hrs_per_week.csv', index_col=[0])

st.markdown(f"<h2>{details[details['full_name'] == ss.current]['ch_name'].values[0]}</h2>", unsafe_allow_html=True)
display_individual_stats()
display_heatmap()
display_hour_and_day_charts()
display_archive_and_topics_charts()
display_hrs_per_week()
display_longest_stream()
