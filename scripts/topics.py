import pandas as pd
import json

df = pd.read_csv('data/details.csv', index_col=[0])
HOLOLIVE = df.loc[df['branch'] == 'Hololive'].index.tolist()
HOLOSTARS = df.loc[df['branch'] == 'Holostars'].index.tolist()

topic_ids = ['apex', 'membersonly', 'minecraft', 'Superchat_Reading', 'singing', 'talk']

# show top 20 for hololive, top 10 for holostars
branches = {
    'hololive': 20,
    'holostars': 10
}

def topics():
    print('Running topics.py')

    with open('json/livestream_details.json', encoding='utf8') as file:
        livestream_details = json.load(file)

    for branch, places in branches.items():
        BRANCH = HOLOLIVE if branch == 'hololive' else HOLOSTARS
        if branch == 'holostars':
            topic_ids.remove('Superchat_Reading')

        for topic in topic_ids:
            dct = {}
            for member in BRANCH:
                try:
                    dct[member] = round(livestream_details[member]['topics'][topic][1] / 3600)
                except KeyError:
                    continue

            top = pd.DataFrame.from_dict(dct, orient='index').sort_values(0, ascending=False).head(places)
            top.sort_values(0).to_csv(f'data/{branch}_{topic}.csv', header=None)

    print('Done.')
