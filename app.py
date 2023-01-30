from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np
import math, calendar

st.set_page_config(
    page_title='Hololive Production Livestream Activity Statistics',
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
        f"{round(df.loc[name, 'total_hrs']):,} ({hrs_dd_hh_mm[0]} days, {hrs_dd_hh_mm[1].lstrip('0')} hour{plural(hrs_dd_hh_mm[1])}, {hrs_dd_hh_mm[2].lstrip('0')} minute{plural(hrs_dd_hh_mm[2])})",
        f"{avg_mins_hh_mm[0]} hour{plural(avg_mins_hh_mm[0])}, {avg_mins_hh_mm[1].lstrip('0')} minute{plural(avg_mins_hh_mm[1])}"
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
        height=445,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.markdown('<p id="heatmap-title">Livestream Timeseries Heatmap</p>', unsafe_allow_html=True)
    st.plotly_chart(heatmap, use_container_width=True)
    st.caption('''
        Lightest and darkest tint represent the least and most frequent streamed times of the day respectively. 
        Opposite/complementary color of the darkest tint represent 0 streaming times.
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
    ah_col.caption('Does not represent the entirety of unarchived videos as the Holodex API does not record the duration on some of it, so it wasn\'t counted.')
    topic_col.plotly_chart(topics_bar, use_container_width=True)

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

@st.cache
def load_data():
    return pd.read_csv('data/data.csv',   index_col=[0]), \
           pd.read_csv('data/colors.csv', index_col=[0])

@st.cache
def load_topics(name):
    return pd.read_csv(f'data/{name}/topics.csv', header=None, index_col=[0])

df, colors = load_data()
days = list(calendar.day_name)
days = days[-1:] + days[:-1] # shift Sunday to 1st position, being the 1st day of the week
time_offsets = [
    -1260, -1200, -1140, -1050, -1080, -1020, -960, -900, -840, -780,
    -690, -720,  -660, -600, -540, -480, -420, -360, -330, -300,
    -270, -240, -210, -195, -180, -150, -120, -60, -15, 0,
    30, 60, 90, 120, 180, 225, 240, 300
]

col1, col2 = st.columns([1, 1])
select = col1.selectbox('Hololive Production Member:', df['ch_name'].tolist())
time_offset = col2.selectbox('Heatmap Timezone:', time_offsets, index=29, format_func=to_timezone) # default to JP timzone

name = df.index[df['ch_name'] == select][0]
main_color = f"#{colors.loc[name, 'most']}"
sub_color = f"#{colors.loc[name, 'least']}"
opp_color = f"#{colors.loc[name, 'zero']}"
topics = load_topics(name)

st.markdown(f"<h2 style='text-align: center;'>{df.full_name[df['ch_name'] == select][0]}</h3>", unsafe_allow_html=True)
display_individual_stats()
display_heatmap()
display_hour_and_day_charts()
display_archive_and_topics_charts()