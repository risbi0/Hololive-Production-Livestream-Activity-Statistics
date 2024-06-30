'''
Latest membership stream id: U2CJ7MU2Fc8
Latest public stream id: Qqhk1RgAhwA

For getting public YouTube livestreams id's. Go to their YouTube channel under Live tab,
scroll to the videos to load the elements, then enter in dev console.

JSON.stringify(Array.from(document.querySelectorAll('#video-title-link')).map(e => e.href))

Remove any id's including latest stream and older streams.

For membership livestreams, go to their Holodex page and manually add the links to the array made above.
Be sure to check for non-public livestreams as well (grey thumbnail with duration).

Replace the empty list of 'ids' below with the final array.

After running this, run process_data.py with the specified code lines their uncommented.
'''

from dotenv import load_dotenv
import json, requests, os

load_dotenv()
HOLODEX_API_KEY = os.getenv('HOLODEX_API_KEY')

ids = []

print('Updating official Hololive channel...')

with open('json/livestream_details.json', encoding='utf8') as file:
    livestream_details = json.load(file)

for id in ids:
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

# sort topics alphabetically
livestream_details['hololive']['topics'] = dict(sorted(livestream_details['hololive']['topics'].items(), key=lambda l: l[0].lower()))

with open('json/livestream_details.json', 'w', encoding='utf-8') as file:
    json.dump(livestream_details, file, ensure_ascii=False)

print('Done.')
