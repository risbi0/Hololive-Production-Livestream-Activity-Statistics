import streamlit as st

def init_page_config():
    st.set_page_config(
        page_title='Hololive Production Livestream Activity Statistics',
        initial_sidebar_state='collapsed',
        layout='wide',
        menu_items={
            'About': '''
                ##### Hololive Production Livestream Activity Statistics

                *(better user experience in desktop)*

                Lifetime statistics of HoloPro talents' YouTube channels.

                Based on YouTube livestreams up to **August 8, 2024**, queried using [Holodex API](https://docs.holodex.net/). This doesn't update live; I update this manually twice a month, but I wait a few weeks longer for new generations to have streams in each day.

                Data only includes **videos where Holodex has a record of its duration**, since some unarchived streams have its durations unrecorded. This is apparent when looking at the Archive Health of non-JP members who often do unarchived streams (it shows less than actual).

                Data may also contain "noise" as neither Holodex nor YouTube's API has a way to distinguish between livestreams and premieres. I had to put some arbitrary condition to filter most non-livestreams, which is that the duration should be more than 360 seconds. This is why the main Hololive channel is updated separately.
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
                margin-top: 40px;
            }
        </style>
        ''',
        unsafe_allow_html=True
    )
