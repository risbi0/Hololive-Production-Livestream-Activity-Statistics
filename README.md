# Hololive Production Livestream Activity Statistics

Made with [Plotly](https://plotly.com/) and deployed in [Streamlit](https://streamlit.io/).

Data was initialized using separate scripts published in another repo, [HPLAS-Initialize](https://github.com/risbi0/HPLAS-Initialize).

### Setup

Install libraries:
```
pip install -r requirements.txt
```
Run app in localhost:
```
streamlit run Main.py
```

### Update Process

Update is done manually by running `scripts/update.py`, preferrably every 2 weeks, max being 3 weeks. This is because the Holodex API only queries up to the latest 50 videos of a channel, including non-livestreams.

The script doesn't include the Hololive channel as it is incompatible to apply the 360 second duration filter (which mostly works on the talents) since it publishes videos that are longer than that duration and aren't livestreams.

To update the channel, go to `scripts/update_holo_ch.py` and read the documentation at the top of the file before running the script.

The frequency of updating the Hololive channel doesn't follow the 2-3 week frequency since the channel seldom livestreams, so it is updated less frequently.
