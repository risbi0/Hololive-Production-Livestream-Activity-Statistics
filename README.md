# Hololive Production Livestream Activity Statistics

Made with [Plotly](https://plotly.com/) and deployed in [Streamlit](https://streamlit.io/).

Data was initialized using separate scripts published in another repo, [HPLAS-Initialize](https://github.com/risbi0/HPLAS-Initialize). It is updated using `scripts/execute.py`.

### Setup

Install libraries:
```
pip install -r requirements.txt
```
Run app in localhost:
```
streamlit run Main.py
```

### Notes

`scripts/update.py` doesn't include the Hololive channel as it is incompatible to apply the 360 second duration filter that mostly works on the talents, since it publishes videos that are longer than that duration and is not a livestream. So I still use [HPLAS-Initialize](https://github.com/risbi0/HPLAS-Initialize) for specifically updating the channel, and I get their livestreams from the Live tab in their YouTube page since it's easier to do that way.