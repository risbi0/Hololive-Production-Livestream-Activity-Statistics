import pandas as pd
import json

with open('json/livestream_details.json', encoding='utf8') as file:
    livestream_details = json.load(file)

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
    'risu', 'moona', 'iofi',
    'ollie', 'anya', 'reine',
    'zeta', 'kaela', 'kobo',
    'calli', 'kiara', 'ina', 'gura', 'ame',
    'irys', 'fauna', 'sana', 'kronii', 'mumei', 'bae',
]

HOLOSTARS = [
    'miyabi', 'kira', 'izuru', 'aruran', 'rikka',
    'astel', 'temma', 'roberu',
    'kaoru', 'shien', 'oga',
    'fuma', 'uyu', 'gamma', 'rio',
    'altare', 'magni', 'axel', 'vesper',
    'bettel', 'flayon', 'hakka', 'shinri'
]

HOLOPRO = HOLOLIVE + HOLOSTARS

BRANCH = HOLOLIVE # change
topics = ['apex', 'membersonly', 'minecraft', 'Superchat_Reading', 'singing', 'talk']

if BRANCH == HOLOLIVE:
    places = 20
    branch = 'hololive'
else:
    topics.remove('Superchat_Reading')
    places = 10
    branch = 'holostars'

for topic in topics:
    dct = {}
    for member in BRANCH:
        try:
            dct[member] = round(livestream_details[member]['topics'][topic][1] / 3600)
        except KeyError:
            continue

    top = pd.DataFrame.from_dict(dct, orient='index').sort_values(0, ascending=False).head(places)
    top.sort_values(0).to_csv(f'data/{branch}_{topic}.csv', header=None)