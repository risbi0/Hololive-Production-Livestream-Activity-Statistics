import streamlit as st

def init_page_config():
    st.set_page_config(
        page_title='Hololive Production Livestream Activity Statistics',
        initial_sidebar_state='collapsed',
        layout='wide',
        menu_items={
            'About': '''
                ##### Hololive Production Livestream Activity Statistics

                Lifetime statistics of HoloPro talents' YouTube channels.

                Based on YouTube livestreams up to **June 10, 2024**, queried through Holodex API.

                The site is updated twice a month. Main Hololive channel is updated less frequently.

                Data only includes videos where the API has a record of its duration, since some unarchived streams have its durations unrecorded. This is apparent when looking at the Archive Health of non-JP members who often do unarchived streams.

                The data collected may also contain unnecessary data since the API doesn't have a way of fetching livestreams only. I had to put some condition to filter most non-livestreams, with it having more than 360 seconds. This is why the main Hololive channel is updated separately.
            '''
        }
    )

def init_markdown():
    st.markdown(
        '''
        <style>
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
