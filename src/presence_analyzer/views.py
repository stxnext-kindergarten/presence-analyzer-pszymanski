# -*- coding: utf-8 -*-
"""
Defines views.
"""
import calendar
from flask import redirect, url_for
from flask.ext.mako import render_template, MakoTemplates
from presence_analyzer.main import app
from presence_analyzer import utils
from presence_analyzer.utils import (
    jsonify,
    get_data,
    mean,
    group_by_weekday,
    mean_group_by_weekday_seconds
)

mako = MakoTemplates(app)


import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Redirect main page to presence_weekday.
    """
    return redirect(url_for('presence_weekday',))


@app.route('/chart/presence_weekday')
def presence_weekday():
    """
    Render presence weekday page.
    """
    return render_template('presence_weekday.html', name='presence_weekday')


@app.route('/chart/mean_time_weekday')
def mean_time_weekday():
    """
    Render presence mean time page.
    """
    return render_template('mean_time_weekday.html', name='mean_time_weekday')


@app.route('/chart/presence_start_end')
def presence_start_end():
    """
    Test presence start end page.
    """
    return render_template(
        'presence_start_end.html',
        name='presence_start_end'
        )


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [{'user_id': i, 'name': 'User {0}'.format(str(i))}
            for i in data.keys()]


@app.route('/api/v2/users', methods=['GET'])
@jsonify
def users_view_xml():
    """
    Users listing with names and avatars for dropdown.
    """
    result = utils.import_user_data_xml()
    return result


@app.route('/api/v1/mean_time_weekday/')
@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/')
@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/')
@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns average time for start and end work
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = mean_group_by_weekday_seconds(data[user_id])

    result = [(
              calendar.day_abbr[weekday],
              mean(average['start']),
              mean(average['end']))
              for weekday, average in weekdays.items()
              ]
    return result
