'''
Latest stream ID:pnzZ7w1HR1s

For getting public YouTube livestreams ID's. Go to their YouTube channel under Live tab,
scroll to the videos to load the elements, then enter in dev console.

JSON.stringify(Array.from(document.querySelectorAll('#video-title-link')).map(e => e.href))

Remove any ID's including any upcoming streams and older streams (starting with the latest stream ID mentioned above).

Replace the empty list of 'ids' below with the final array.

After running this, run process_data.py with the specified code lines uncommented.
'''

from dotenv import load_dotenv
from update import parse_date
import json, requests, os

load_dotenv()
HOLODEX_API_KEY = os.getenv('HOLODEX_API_KEY')

ids = []

print('Updating official Hololive channel...')

with open(os.path.join(os.path.dirname(__file__), '../json/livestream_details.json'), encoding='utf8') as file:
    livestream_details = json.load(file)

for id in ids:
    print(id)
    response = requests.get(f'https://holodex.net/api/v2/videos/{id}', headers={'X-APIKEY': HOLODEX_API_KEY})
    data = json.loads(response.text)

    if not any(detail['id'] == data['id'] for detail in livestream_details['hololive']['details']):
        topic = data['topic_id'] if 'topic_id' in data else 'undefined'
        # details
        details = {}
        details['id'] = data['id']
        details['title'] = data['title']
        details['duration'] = data['duration']
        details['date'] = data['available_at']
        details['topic'] = topic
        livestream_details['hololive']['details'].append(details)
        # topics
        if topic not in livestream_details['hololive']['topics']:
            livestream_details['hololive']['topics'][topic] = [0, 0]
        livestream_details['hololive']['topics'][topic][0] += 1
        livestream_details['hololive']['topics'][topic][1] += data['duration']
        # missing
        if data['status'] == 'missing':
            livestream_details['hololive']['missing'] += 1
            livestream_details['hololive']['missing_length'] += data['duration']

# sort date from earliest to latest
livestream_details['hololive']['details'] = sorted(livestream_details['hololive']['details'], key=lambda x: parse_date(x['date']))
# sort topics alphabetically
livestream_details['hololive']['topics'] = dict(sorted(livestream_details['hololive']['topics'].items(), key=lambda l: l[0].lower()))

with open(os.path.join(os.path.dirname(__file__), '../json/livestream_details.json'), 'w', encoding='utf-8') as file:
    json.dump(livestream_details, file, ensure_ascii=False)

print('Done.')
