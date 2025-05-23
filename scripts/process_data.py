from datetime import date, datetime, timedelta
from pytz import timezone
from time import perf_counter
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import numpy as np
import os, glob, json

load_dotenv()
YT_DATA_API_KEY = os.getenv('YT_DATA_API_KEY')
youtube = build('youtube', 'v3', developerKey=YT_DATA_API_KEY)

current_script_dir = Path(__file__).resolve().parent
parent_dir = current_script_dir.parent

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
        os.path.join(parent_dir, f'data/{folder_name}/{filename}.csv'),
        header=has_header,
        index=has_index
    )

def hrs_per_week(name):
    data_dict = {}

    # add durations for each week
    for detail in livestream_details[name]['details']:
        stream_date = detail['date']
        vid_dur = detail['duration'] / 3600
        start_iso = datetime.strptime(stream_date, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone('UTC')).astimezone(timezone('Asia/Tokyo'))
        year = start_iso.year
        week_no = int(start_iso.strftime('%U')) # week start on Sunday

        # years with January 1 on sunday have its week no. from 1 to 53, adjusting it to be from 0 to 52
        if datetime(year, 1, 1).weekday() == 6:
            week_no -= 1

        date = f'{year}-{week_no}'

        if date not in data_dict:
            data_dict[date] = 0

        data_dict[date] += vid_dur

    # add current year-week if there's no record of it
    date_today = datetime.now(timezone('Asia/Tokyo'))
    year = date_today.year
    week_no = int(date_today.strftime('%U'))
    curr_year_week = f'{year}-{week_no}'
    if curr_year_week not in data_dict:
        data_dict[curr_year_week] = 0

    # add 0 hrs to inactive weeks
    data_list = []
    prev_year = None
    prev_week = None

    for year_week, dur in data_dict.items():
        year, week = map(int, year_week.split('-'))

        if len(data_list) == 0:
            prev_year = year
            prev_week = week
            data_list.append([year_week, dur])
            continue

        while (year > prev_year) or (year == prev_year and week > prev_week + 1):
            prev_week += 1

            if prev_week > 52:
                prev_week = 0
                prev_year += 1

            # break if next year's 1st week has a duration stored
            if year == prev_year and week == 0:
                break

            data_list.append([f"{prev_year}-{prev_week}", 0])

        data_list.append([year_week, dur])
        prev_year = year
        prev_week = week

    # turn to dictionary
    data_dict = { k: v for k, v in data_list }
    # turn to dataframe
    df = pd.DataFrame.from_dict(data_dict, orient='index', columns=['hours'])
    df['hours'] = df['hours'].round(2) # round to 2 decimals
    to_csv(df, name, 'hrs_per_week')

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
        if duration > data.loc[name, 'long_length'] and duration > max['length'] or np.isnan(data.loc[name, 'long_length']):
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
    old_files = glob.glob(os.path.join(os.path.dirname(__file__), f'..data/{name}/*'))
    for file in old_files:
        os.remove(file)

    # create folder if folder doesn't exist
    if not os.path.isdir(os.path.join(parent_dir, f'data/{name}')):
        os.mkdir(os.path.join(parent_dir, f'data/{name}'))

    # save heatmap
    to_csv(pd.DataFrame(heatmap_data), name, 'heatmap', has_header=False, has_index=False)

    # save top 10 topics by streaming hrs
    topics_df = pd.DataFrame.from_dict(livestream_details[name]['topics'], orient='index')
    # check if there are no streams with undefined topic, mostly for new members
    if 'undefined' not in topics_df.index.to_list():
        top_10_topics = topics_df.sort_values(1, ascending=False).head(10)
    else:
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
    hrs_per_week(name)

data = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/data.csv'), index_col=[0])
details = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/details.csv'), index_col=[0])
channel_names = details.loc[details['active'] != 0].index.to_list()
channel_names.remove('hololive')

def load_json():
    global livestream_details

    with open(os.path.join(os.path.dirname(__file__), '../json/livestream_details.json'), encoding='utf8') as file:
        livestream_details = json.load(file)

def process_data():
    print('Running process_data.py')
    start = perf_counter()
    load_json()

    for name in channel_names:
        print(f'Processing: {name}')
        main(name)
        # uncomment when updating holo ch, and comment the line above
        """ main('hololive')
        break """

    # combine individual stats to main csv file
    main_df = pd.DataFrame(
        columns=[
            'count', 'total_hrs', 'total_f', 'avg_mins', 'avg_f', 'missing', 'missing_hr',
            'long_title', 'long_id', 'long_date', 'long_length',
            'hrs_p_wk', 'hour_data', 'weekday_data'
        ]
    )
    for name in details.index:
        sub_df = pd.read_csv(os.path.join(os.path.dirname(__file__), f'../data/{name}/data.csv'), index_col=[0])
        main_df = pd.concat([main_df, sub_df])

    main_df.to_csv(os.path.join(parent_dir, 'data/data.csv'))

    print(f'Done. Time took: {round(perf_counter() - start, 2)} seconds.')

# uncomment when updating holo ch
#process_data()
