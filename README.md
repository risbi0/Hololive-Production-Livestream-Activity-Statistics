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

### Adding New Members

Think of a one-word name that will identify each member, which in this doc will be called `name`.

Add a row in `data/details.csv` most of the values are self-explanatory, but here are the explanations for those that are not:

- `most`, `least`, `zero` - The HEX colors for the heatmap that represent the amount of livestreams in a day of the week. Get the main color of the member from https://hololive.hololivepro.com/en/talents based on the darker color in their background, that will be the `most` color. Go to https://www.color-hex.com/ and enter the color. The 3rd from the right in the Tints section will be the `least` color. The complementary color will be the `zero` color. Not all heatmaps will have good contrast based on their main color so exercise discretion.

- `active` - 0 for not active member (graduated/terminated). 1 for active.

```
<name>,full_name,ch_name,ch_id,debut_date,most,least,zero,active,branch,gen_name
```

Add a row in `data/data.csv`:
```
<name>,,,,,,,,,,,,,,
```

Add in `json/livestream_details.json`:
```
"<name>":{"missing":0,"missing_length":0,"topics":{},"details":[]},
```

Add a row in `data/generation_colors_name.csv`. EN and ID have the same color as a branch. For new JP gens, pick the main color from any of the members in the gen that's not too similar to the current colors.

Put these templates after the latest gen of their branch so they look organized.
