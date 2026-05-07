#!/usr/bin/env python3

import argparse
import datetime as dt
import gzip
import os
import re
import shutil
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

HTTP_ROOT = 'https://magmap.nso.edu/QR/zqs'
FILENAME_RE = re.compile(
    r'^mrzqs(?P<stamp>\d{6}t\d{4})c(?P<carrington>\d+)_(?P<count>\d+)\.fits\.gz$'
)


def _month_url(time_in):
    return f'{HTTP_ROOT}/{time_in:%Y%m}'


def _day_url(time_in):
    return f'{_month_url(time_in)}/mrzqs{time_in:%y%m%d}'


def _parse_filename(filename):
    match = FILENAME_RE.match(filename)
    if match is None:
        return None
    stamp = dt.datetime.strptime(match.group('stamp'), '%y%m%dt%H%M')
    return {
        'filename': filename,
        'time': stamp,
        'carrington': int(match.group('carrington')),
        'count': int(match.group('count')),
    }


def _list_matches(time_in):
    day_url = _day_url(time_in)
    try:
        with urlopen(day_url + '/') as response:
            listing = response.read().decode('utf-8', errors='replace')
    except (HTTPError, URLError):
        return day_url, []

    pattern = re.compile(r'href="(mrzqs' + time_in.strftime('%y%m%d') + r't[^"]+\.fits\.gz)"')
    try:
        filenames = pattern.findall(listing)
    except re.error:
        filenames = []

    entries = []
    for filename in filenames:
        parsed = _parse_filename(filename)
        if parsed is not None:
            entries.append(parsed)

    entries.sort(key=lambda entry: entry['time'])
    return day_url, entries


def _find_best_match(time_in, max_days_back=31):
    day_cursor = time_in
    for i_try in range(max_days_back + 1):
        day_url, entries = _list_matches(day_cursor)
        if entries:
            if i_try == 0:
                candidates = [entry for entry in entries if entry['time'] <= time_in]
            else:
                candidates = entries

            if candidates:
                return day_url, candidates[-1]

        day_cursor = (day_cursor - dt.timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=0
        )

    raise FileNotFoundError(
        'Could not find any GONG magnetogram within the prior '
        + str(max_days_back)
        + ' days under '
        + HTTP_ROOT
    )


def download_GONG_magnetogram(time_in, max_days_back=31, keep_gz=True):
    '''
    Download the latest GONG mrzqs magnetogram at or before the requested time.
    '''

    day_url, entry = _find_best_match(time_in, max_days_back=max_days_back)
    filename_gz = entry['filename']
    download_url = day_url + '/' + filename_gz

    try:
        with urlopen(download_url) as response, open(filename_gz, 'wb') as fhandle:
            shutil.copyfileobj(response, fhandle, 65536)
    except (HTTPError, URLError):
        sys.exit('Cannot download ' + download_url)

    if entry['time'] != time_in.replace(second=0, microsecond=0):
        print('Warning: exact GONG map not found for ' + time_in.strftime('%Y-%m-%dT%H:%M:%S'))
        print('         Using ' + entry['time'].strftime('%Y-%m-%dT%H:%M:%S'))

    filename_fits = filename_gz[:-3]
    with gzip.open(filename_gz, 'rb') as s_file, open(filename_fits, 'wb') as d_file:
        shutil.copyfileobj(s_file, d_file, 65536)

    if not keep_gz:
        os.remove(filename_gz)

    return [filename_fits]


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Download a GONG mrzqs magnetogram from the NSO FTP archive.'
    )
    parser.add_argument(
        '-t',
        '--time',
        help='Requested map time in yyyy-mm-ddThh:mm:ss format.',
        type=str,
    )
    parser.add_argument(
        '--max-days-back',
        help='How many previous days to search if no exact-time map is found.',
        type=int,
        default=31,
    )
    parser.add_argument(
        '--remove-gz',
        help='Remove the downloaded .fits.gz file after unzipping.',
        action='store_true',
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()

    if args.time is None:
        yyyy = int(input('Enter year: ' ))
        mm = int(input('Enter month: '))
        dd = int(input('Enter day: ' ))
        hh = int(input('Enter hour: '))
        minute = int(input('Enter minute: '))
        time_in = dt.datetime(year=yyyy, month=mm, day=dd, hour=hh, minute=minute)
    else:
        time_in = dt.datetime.strptime(args.time, '%Y-%m-%dT%H:%M:%S')

    filenames = download_GONG_magnetogram(
        time_in,
        max_days_back=args.max_days_back,
        keep_gz=not args.remove_gz,
    )
    print('Downloaded:', ', '.join(filenames))
