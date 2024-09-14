from time import perf_counter
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import json, requests, os

load_dotenv()
HOLODEX_API_KEY = os.getenv('HOLODEX_API_KEY')

df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/details.csv'), index_col=[0])
channel_ids = df.loc[df['active'] != 0, 'ch_id'].to_dict()
channel_ids.pop('hololive')

excluded_topics = ['original_song', 'music_cover', 'shorts', 'animation']

def parse_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')

def update():
    print('Running update.py')
    start = perf_counter()

    with open(os.path.join(os.path.dirname(__file__), '../json/livestream_details.json'), encoding='utf8') as file:
        livestream_details = json.load(file)

    for name, channel_id in channel_ids.items():
        print(f'Updating: {name}')
        # query API
        response = requests.get(f'https://holodex.net/api/v2/channels/{channel_id}/videos?limit=50', headers={'X-APIKEY': HOLODEX_API_KEY})
        data = json.loads(response.text)
        data.reverse()

        for i in range(len(data)):
            # check first if id wasn't already processed
            if not any(detail['id'] == data[i]['id'] for detail in livestream_details[name]['details']):
                topic = data[i]['topic_id'] if 'topic_id' in data[i] else 'undefined'
                # details
                if topic.lower() not in excluded_topics and \
                'available_at' in data[i] and \
                'rebroadcast' not in data[i]['title'].lower() and \
                're-broadcast' not in data[i]['title'].lower() and \
                'ポルカの伝説' not in data[i]['title'].lower() and \
                'fauna plays' not in data[i]['title'].lower() and \
                'mumei radio' not in data[i]['title'].lower() and \
                'kara-rewind' not in data[i]['title'].lower() and \
                'duration' in data[i] and data[i]['duration'] > 360: # filter out Shorts and very short streams
                    details = {}
                    details['id'] = data[i]['id']
                    details['title'] = data[i]['title']
                    details['duration'] = data[i]['duration']
                    details['date'] = data[i]['available_at']
                    details['topic'] = topic
                    livestream_details[name]['details'].append(details)
                    # topics
                    if topic not in livestream_details[name]['topics']:
                        livestream_details[name]['topics'][topic] = [0 for _ in range(2)]
                    livestream_details[name]['topics'][topic][0] += 1
                    livestream_details[name]['topics'][topic][1] += data[i]['duration']
                    # missing
                    if data[i]['status'] == 'missing':
                        livestream_details[name]['missing'] += 1
                        livestream_details[name]['missing_length'] += data[i]['duration']

        # sort date from earliest to latest
        livestream_details[name]['details'] = sorted(livestream_details[name]['details'], key=lambda x: parse_date(x['date']))
        # sort topics alphabetically
        livestream_details[name]['topics'] = dict(sorted(livestream_details[name]['topics'].items(), key=lambda l: l[0].lower()))

    with open(os.path.join(os.path.dirname(__file__), '../json/livestream_details.json'), 'w', encoding='utf-8') as file:
        json.dump(livestream_details, file, ensure_ascii=False)

    print(f'Done. Time took: {round(perf_counter() - start, 2)} seconds.')
