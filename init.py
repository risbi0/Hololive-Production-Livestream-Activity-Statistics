import streamlit as st

def init_page_config():
    st.set_page_config(
        page_title='Hololive Production Livestream Activity Statistics',
        initial_sidebar_state='collapsed',
        layout='wide',
        menu_items={
            'About': '''
                ##### Hololive Production Livestream Activity Statistics

                Based on YouTube livestreams up to **July 8, 2023** (all channels except the main Hololive channel), queried through Holodex API.

                Only including videos where the API has a record of its duration. This is in regards to some unarchived videos having their durations unrecorded.
            '''
        }
    )

def init_markdown():
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
