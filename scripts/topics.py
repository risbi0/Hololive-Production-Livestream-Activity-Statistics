import pandas as pd
import json

HOLOLIVE = [
    'hololive',
    'sora', 'roboco', 'miko', 'suisei', 'azki',
    'mel', 'fubuki', 'matsuri', 'haachama', 'aki',
    'aqua', 'shion', 'ayame', 'choco', 'subaru',
    'mio', 'okayu', 'korone',
    'pekora', 'rushia', 'flare', 'noel', 'marine',
    'kanata', 'coco', 'watame', 'towa', 'luna',
    'lamy', 'nene', 'botan', 'polka',
    'laplus', 'lui', 'koyori', 'chloe', 'iroha',
    'ao', 'kanade', 'ririka', 'raden', 'hajime'
    'calli', 'kiara', 'ina', 'gura', 'ame',
    'irys', 'fauna', 'sana', 'kronii', 'mumei', 'bae',
    'shiori', 'bijou', 'nerissa', 'fuwamoco',
    'risu', 'moona', 'iofi',
    'ollie', 'anya', 'reine',
    'zeta', 'kaela', 'kobo'
]

HOLOSTARS = [
    'miyabi', 'kira', 'izuru', 'aruran', 'rikka',
    'astel', 'temma', 'roberu',
    'kaoru', 'shien', 'oga',
    'fuma', 'uyu', 'gamma', 'rio',
    'altare', 'magni', 'axel', 'vesper',
    'bettel', 'flayon', 'hakka', 'shinri'
]

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
