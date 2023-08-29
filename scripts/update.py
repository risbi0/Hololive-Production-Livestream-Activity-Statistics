from time import perf_counter
from dotenv import load_dotenv
import json, requests, os

load_dotenv()
HOLODEX_API_KEY = os.getenv('HOLODEX_API_KEY')

channel_ids = {
    'sora':     'UCp6993wxpyDPHUpavwDFqgg',
    'roboco':   'UCDqI2jOz0weumE8s7paEk6g',
    'miko':     'UC-hM6YJuNYVAmUWxeIr9FeA',
    'suisei':   'UC5CwaMl1eIgY8h02uZw7u8A',
    'azki':     'UC0TXe_LYZ4scaW2XMyi5_kw',
    'mel':      'UCD8HOxPs4Xvsm8H0ZxXGiBw',
    'fubuki':   'UCdn5BQ06XqgXoAxIhbqw5Rg',
    'matsuri':  'UCQ0UDLQCjY0rmuxCDE38FGg',
    'haachama': 'UC1CfXB_kRs3C-zaeTG3oGyg',
    'aki':      'UCFTLzh12_nrtzqBPsTCqenA',
    'aqua':     'UC1opHUrw8rvnsadT-iGp7Cg',
    'shion':    'UCXTpFs_3PqI41qX2d9tL2Rw',
    'ayame':    'UC7fk0CB07ly8oSl0aqKkqFg',
    'choco':    'UC1suqwovbL1kzsoaZgFZLKg',
    'subaru':   'UCvzGlP9oQwU--Y0r9id_jnA',
    'mio':      'UCp-5t9SrOQwXMU7iIjQfARg',
    'okayu':    'UCvaTdHTWBGv3MKj3KVqJVCw',
    'korone':   'UChAnqc_AY5_I3Px5dig3X1Q',
    'pekora':   'UC1DCedRgGHBdm81E1llLhOQ',
    'flare':    'UCvInZx9h3jC2JzsIzoOebWg',
    'noel':     'UCdyqAaZDKHXg4Ahi7VENThQ',
    'marine':   'UCCzUftO8KOVkV4wQG1vkUvg',
    'kanata':   'UCZlDXzGoo7d44bwdNObFacg',
    'watame':   'UCqm3BQLlJfvkTsX_hvm0UmA',
    'towa':     'UC1uv2Oq6kNxgATlCiez59hw',
    'luna':     'UCa9Y57gfeY0Zro_noHRVrnw',
    'nene':     'UCAWSyEs_Io8MtpY3m-zqILA',
    'polka':    'UCK9V2B22uJYu3N7eR_BT9QA',
    'botan':    'UCUKD-uaobj9jiqB-VXt71mA',
    'lamy':     'UCFKOVgVbGmX65RxO3EtH3iw',
    'laplus':   'UCENwRMx5Yh42zWpzURebzTw',
    'lui':      'UCs9_O1tRPMQTHQ-N_L6FU2g',
    'koyori':   'UC6eWCld0KwmyHFbAqK3V-Rw',
    'chloe':    'UCIBY1ollUsauvVi4hW4cumw',
    'iroha':    'UC_vMYWcDjmfdpH6r4TTn1MQ',
    'calli':    'UCL_qhgtOy0dy1Agp8vkySQg',
    'kiara':    'UCHsx4Hqa-1ORjQTh9TYDhww',
    'ina':      'UCMwGHR0BTZuLsmjY_NT5Pwg',
    'gura':     'UCoSrY_IQQVpmIRZ9Xf-y93g',
    'ame':      'UCyl1z3jo3XHR1riLFKG5UAg',
    'irys':     'UC8rcEBzJSleTkf_-agPM20g',
    'fauna':    'UCO_aKKYxn4tvrqPjcTzZ6EQ',
    'kronii':   'UCmbs8T6MWqUHP1tIQvSgKrg',
    'mumei':    'UC3n5uGu18FoCy23ggWWp8tA',
    'bae':      'UCgmPnx-EEeOrZSg5Tiw7ZRQ',
    'shiori':   'UCgnfPPb9JI3e9A4cXHnWbyg',
    'bijou':    'UC9p_lqQ0FEDz327Vgf5JwqA',
    'nerissa':  'UC_sFNM0z0MWm9A6WlKPuMMg',
    'fuwamoco': 'UCt9H_RpQzhxzlyBxFqrdHqA',
    'risu':     'UCOyYb1c43VlX9rc_lT6NKQw',
    'moona':    'UCP0BspO_AMEe3aQqqpo89Dg',
    'iofi':     'UCAoy6rzhSf4ydcYjJw3WoVg',
    'ollie':    'UCYz_5n-uDuChHtLo7My1HnQ',
    'anya':     'UC727SQYUvx5pDDGQpTICNWg',
    'reine':    'UChgTyjG-pdNvxxhdsXfHQ5Q',
    'zeta':     'UCTvHWSfBZgtxE4sILOaurIQ',
    'kaela':    'UCZLZ8Jjx_RN2CXloOmgTHVg',
    'kobo':     'UCjLEmnpCNeisMxy134KPwWw',
    'miyabi':   'UC6t3-_N8A6ME1JShZHHqOMw',
    'izuru':    'UCZgOv3YDEs-ZnZWDYVwJdmA',
    'aruran':   'UCKeAhJvy8zgXWbh9duVjIaQ',
    'rikka':    'UC9mf_ZVpouoILRY9NUIaK-w',
    'astel':    'UCNVEsYbiZjH5QLmGeSgTSzg',
    'temma':    'UCGNI4MENvnsymYjKiZwv9eg',
    'roberu':   'UCANDOlYTJT7N5jlRC3zfzVA',
    'shien':    'UChSvpZYRPh0FvG4SJGSga3g',
    'oga':      'UCwL7dgTxKo8Y4RFIKWaf8gA',
    'fuma':     'UCc88OV45ICgHbn3ZqLLb52w',
    'uyu':      'UCgRqGV1gBf2Esxh0Tz1vxzw',
    'gamma':    'UCkT1u65YS49ca_LsFwcTakw',
    'rio':      'UCdfMHxjcCc2HSd9qFvfJgjg',
    'altare':   'UCyxtGMdWlURZ30WSnEjDOQw',
    'axel':     'UC2hx0xVkMoHGWijwr_lA01w',
    'bettel':   'UCHP4f7G2dWD4qib7BMatGAw',
    'flayon':   'UC060r4zABV18vcahAWR1n7w',
    'hakka':    'UC7gxU6NXjKF1LrgOddPzgTw',
    'shinri':   'UCMqGG8BRAiI1lJfKOpETM_w'
}

excluded_topics = ['original_song', 'music_cover', 'shorts', 'animation']

def update():
    print('Running update.py')
    start = perf_counter()

    with open('json/livestream_details.json', encoding='utf8') as file:
        livestream_details = json.load(file)

    for name, channel_id in channel_ids.items():
        print(f'Updating: {name.capitalize()}')
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
                'ポルカの伝説' not in data[i]['title'].lower() and \
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

        # sort topics alphabetically
        livestream_details[name]['topics'] = dict(sorted(livestream_details[name]['topics'].items(), key=lambda l: l[0].lower()))

    with open('json/livestream_details.json', 'w', encoding='utf-8') as file:
        json.dump(livestream_details, file, ensure_ascii=False)

    print(f'Done. Time took: {round(perf_counter() - start, 2)} seconds.')
