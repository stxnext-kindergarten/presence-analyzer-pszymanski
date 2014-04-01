# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
import time
import urllib
import logging
import threading
from json import dumps
from lxml import etree
from functools import wraps
from flask import Response
from datetime import datetime
from presence_analyzer.main import app


log = logging.getLogger(__name__)  # pylint: disable-msg=C0103

CACHE = {}
TIMESTAMPS = {}
LOCKER = threading.Lock()


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        Response function
        """
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


def locker_function(function):
    """
    Creates locking function decorator.
    """
    @wraps(function)
    def inner_locker(*args, **kwargs):
        """
        Lock selected function.
        """
        with LOCKER:
            return function(*args, **kwargs)
    return inner_locker


def memorize_data(key, cache_time):
    """
    Caching decorator to global variable.
    """
    def wraps_function(function):
        """
        Fix name and doc function for better debugging.
        """
        @wraps(function)
        def inner_function(*args, **kwargs):
            """
            Inner function, cache function data and set cache timer.
            """
            timestamp = TIMESTAMPS.get(key, 0)
            if cache_time + timestamp > time.time():
                return CACHE[key]
            result = function(*args, **kwargs)
            CACHE[key] = result
            TIMESTAMPS[key] = time.time()
            return result
        return inner_function
    return wraps_function


@locker_function
@memorize_data('user_data', 3600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def parse_user_data_xml():
    """
    Parse and format data from users.xml
    """
    with open('runtime/data/users.xml', 'r') as xmlfile:
        tree = etree.parse(xmlfile)
        server = tree.find('./server')
        protocol = server.find('./protocol').text
        host = server.find('./host').text
        additional = '://'
        url = protocol + additional + host
        return {
            user.attrib['id']: {
                'name': user.find('./name').text,
                'avatar': url + user.find('./avatar').text}
            for user in tree.findall('./users/user')}


def import_user_xml_form_url():
    """
    Import and save users.xml form URL
    """
    with open(app.config['USERS_DATA_XML'], 'wb') as local_file:
        url = app.config['USERS_DATA_XML_URL']
        web_file = urllib.urlopen("url")
        local_file.write(web_file.read())


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def mean_group_by_weekday_seconds(items):
    """
    Groups presence entries by weekday with seconds.
    """
    result = {i: {'start': [], 'end': []} for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()]['start'].append(seconds_since_midnight(start))
        result[date.weekday()]['end'].append(seconds_since_midnight(end))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
