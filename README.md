# Hololive Production Livestream Activity Statistics

Made with [Plotly](https://plotly.com/) and deployed in [Streamlit](https://streamlit.io/).

Data was initialized using separate scripts published in another repo, [HPLAS-Initialize](https://github.com/risbi0/HPLAS-Initialize).

### Requirements

- Python
- Holodex API key (`HOLODEX_API_KEY`)
- YouTube Data API key (`YT_DATA_API_KEY`)

### Setup

Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

Install libraries:
```bash
pip install -r requirements.txt
```

Run app locally:
```bash
streamlit run Main.py
```

### JSON Schema

```
{
    "<name>": {
        "missing": int,
        "missing_length": int,
        "topics": {
            "<topic_name>": [int, int]
        },
        "details": [
            {
                "id": string,
                "title": string,
                "duration": int,
                "date": string
            }
        ]
    }
}
```

- `name` - Name of the channel. The same name used as the index in the CSV files.
    - `missing` - Amount of unarchived livestreams.
    - `missing_length` - Total duration of unarchived livestreams in seconds.
    - `topics` - The topic of the livestream provided by Holodex API.
        - `topic_name` - Name of the topic. Represented by an array of two integers. The 1st integer and 2nd integer is the amount of livestreams with the same topic and the total duration (in seoncds) of said livestreams respectively.
    - `details` - An array of JSON's for details of each livestream.
        - `id` - YouTube ID of the livestream.
        - `title` - Title of the livestream.
        - `duration` - Duration of the livestream.
        - `date` - The date and time the livestream started in ISO 8601 (UTC+0).

### Update Process

Update is done manually by running `scripts/update.py`, preferrably every 2 weeks, max being 3 weeks. This is because the Holodex API only queries up to the latest 50 videos of a channel, including non-livestreams.

The script doesn't include the Hololive channel because it is incompatible to apply the 360 second duration filter (which mostly works on the members) since most of its videos are longer than that duration and aren't livestreams. When updating it, `scripts/update_holo_ch.py` is used (more documentation in the script). The channel is updated less frequently since it seldom livestreams.

### Adding New Members

Think of a one-word name that will identify each member which is represented by `name`.

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
