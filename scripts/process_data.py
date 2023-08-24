from datetime import date, datetime, timedelta
from pytz import timezone
from time import perf_counter
from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd
import os, glob, json

load_dotenv()
YT_DATA_API_KEY = os.getenv('YT_DATA_API_KEY')
youtube = build('youtube', 'v3', developerKey=YT_DATA_API_KEY)

def timings(time):
    weekday = time.weekday() + 1

    # sunday
    if weekday == 7:
        weekday = 0

    # for list usage
    return time.hour * 60 + time.minute - 1, weekday

def m_to_dhhmm(seconds, showDays):
    days = seconds // 86400
    seconds = seconds % 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60

    if showDays:
        return f'{days}:{hours:02d}:{minutes:02d}'

    return f'{hours}:{minutes:02d}'

def to_HHMM(i):
    return f'{str(i.item() // 60).zfill(2)}:{str(i.item() % 60).zfill(2)}'

def to_csv(df, folder_name, filename, has_header=True, has_index=True):
    df.to_csv(
        f'data/{folder_name}/{filename}.csv',
        header=has_header,
        index=has_index
    )

def main(name):
    # initialize variables
    heatmap_data = [[0 for _ in range(1440)] for _ in range(7)]
    weekday_data = [0 for _ in range(7)]
    hour_data = [0 for _ in range(12)]
    total_mins = 0
    max = {
        'title': None,
        'id': None,
        'date': 0,
        'length': 0
    }

    # iterate ID's of specified channel
    for detail in livestream_details[name]['details']:
        id = detail['id']
        title = detail['title']
        stream_date = detail['date']
        vid_dur = detail['duration']

        total_mins += round(vid_dur / 60)
        start_iso = datetime.strptime(stream_date, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone('UTC')).astimezone(timezone('Asia/Tokyo'))
        end_iso = start_iso + timedelta(seconds=vid_dur)
        # start time & end time in mins since midnigth in JP timezone
        # and day of the week (sun = 0, ..., sat = 6)
        start_time, start_day = timings(start_iso)
        end_time, end_day = timings(end_iso)

        # data
        # streams per day
        weekday_data[start_day] += 1

        # stream duration count (mins)
        same_day_stream = start_time <= end_time # check if stream ended on the same day
        duration = end_time - start_time if same_day_stream else 1440 - start_time + end_time
        if duration < 1: duration = 1
        if duration > 719: duration = 719
        hour_data[duration // 60] += 1

        # get longest video (only the first when there are multiple longest videos with equal length)
        if duration > data.loc[name, 'long_length'] and duration > max['length']:
            response = youtube.videos().list(part='snippet,status', id=id).execute()
            # add only publicly available videos (except for nuked channels)
            if len(response['items']) != 0 or name in ['rushia', 'kaoru']:
                # add details to dictionary
                max['title'] = title
                max['id'] = id
                max['date'] = start_iso
                max['length'] = duration

        # heatmap
        for i in range(1440):
            if (i >= start_time and i <= end_time and same_day_stream) or \
               (i >= start_time and not same_day_stream):
                heatmap_data[start_day][i] += 1
            elif i <= end_time and not same_day_stream:
                heatmap_data[end_day][i] += 1

    # delete old files
    old_files = glob.glob(f'data/{name}/*')
    for file in old_files:
        os.remove(file)

    # create folder if folder doesn't exist
    if not os.path.isdir(f'data/{name}'):
        os.mkdir(f'data/{name}')

    # save heatmap
    to_csv(pd.DataFrame(heatmap_data), name, 'heatmap', has_header=False, has_index=False)

    # save top 10 topics by streaming hrs
    topics_df = pd.DataFrame.from_dict(livestream_details[name]['topics'], orient='index')
    top_10_topics = topics_df.sort_values(1, ascending=False).drop('undefined').head(10)
    top_10_topics[1] = top_10_topics[1].apply(lambda x: round(x / 3600))

    to_csv(top_10_topics.sort_values(1), name, 'topics', has_header=False)

    # save stats to own csv, to be later combined
    livestream_count = round(len(livestream_details[name]['details']))
    total_hrs = round(total_mins / 60)
    avg_mins = round(total_mins / livestream_count)
    debut_date = [int(s) for s in details.loc[name, 'debut_date'].split('/')]
    update_date = date.today()

    # make DF to each member, to be later combined to main_df
    sub_df = pd.DataFrame()
    sub_df.loc[name, 'full_name'] = details.loc[name, 'full_name']
    sub_df.loc[name, 'ch_name'] = details.loc[name, 'ch_name']
    sub_df.loc[name, 'count'] = livestream_count
    sub_df.loc[name, 'total_hrs'] = total_hrs
    sub_df.loc[name, 'total_f'] = m_to_dhhmm(total_mins * 60, True)
    sub_df.loc[name, 'avg_mins'] = avg_mins
    sub_df.loc[name, 'avg_f'] = m_to_dhhmm(avg_mins * 60, False)
    sub_df.loc[name, 'missing'] = livestream_details[name]['missing']
    sub_df.loc[name, 'missing_hr'] = round(livestream_details[name]['missing_length'] / 3600, 2)
    if max['title'] != None: # save new longest video's details
        sub_df.loc[name, 'long_title'] = max['title']
        sub_df.loc[name, 'long_id'] = max['id']
        sub_df.loc[name, 'long_date'] = f"{max['date'].strftime('%B')} {max['date'].strftime('%d').lstrip('0')}, {max['date'].strftime('%Y')}"
        sub_df.loc[name, 'long_length'] = max['length']
    else: # save old details
        sub_df.loc[name, 'long_title'] = data.loc[name, 'long_title']
        sub_df.loc[name, 'long_id'] = data.loc[name, 'long_id']
        sub_df.loc[name, 'long_date'] = data.loc[name, 'long_date']
        sub_df.loc[name, 'long_length'] = data.loc[name, 'long_length']
    sub_df.loc[name, 'hrs_p_wk'] = round(total_hrs / ((update_date - date(debut_date[2], debut_date[0], debut_date[1])).days / 7), 2)
    sub_df.loc[name, 'hour_data'] = ','.join(str(data) for data in hour_data)
    sub_df.loc[name, 'weekday_data'] = ','.join(str(data) for data in weekday_data)

    to_csv(sub_df, name, 'data')

data = pd.read_csv('data/data.csv', index_col=[0])
details = pd.read_csv('data/details.csv', index_col=[0])
with open('json/livestream_details.json', encoding='utf8') as file:
    livestream_details = json.load(file)

def process_data():
    print('Running process_data.py')
    start = perf_counter()

    for holomem in details.index:
        # skip inactive talents
        if holomem not in ['rushia', 'coco', 'sana', 'kira', 'kaoru', 'vesper', 'magni']:
            print(f'Processing: {holomem}')
            main(holomem)

    # combine individual stats to main csv file
    main_df = pd.DataFrame(
        columns=[
            'full_name', 'ch_name',
            'count', 'total_hrs', 'total_f', 'avg_mins', 'avg_f', 'missing', 'missing_hr',
            'long_title', 'long_id', 'long_date', 'long_length',
            'hrs_p_wk', 'hour_data', 'weekday_data'
        ]
    )
    for holomem in details.index:
        sub_df = pd.read_csv(f'data/{holomem}/data.csv', index_col=[0])
        main_df = pd.concat([main_df, sub_df])

    main_df.to_csv('data/data.csv')

    print(f'Done. Time took: {round(perf_counter() - start, 2)} seconds.')
