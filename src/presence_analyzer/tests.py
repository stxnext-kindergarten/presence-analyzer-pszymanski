# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_CACHE_DATA = os.path.join(
    os.path.dirname(__file__),
    '..', '..', 'runtime', 'data', 'test_cache_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect to presence_weekday.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday')

    def test_presence_weekday(self):
        """
        Test presence weekday page.
        """
        resp = self.client.get('/chart/presence_weekday')
        self.assertEqual(resp.status_code, 200)

    def test_mean_time_weekday(self):
        """
        Test presence mean time page.
        """
        resp = self.client.get('/chart/mean_time_weekday')
        self.assertEqual(resp.status_code, 200)

    def test_presence_start_end(self):
        """
        Test presence start end page.
        """
        resp = self.client.get('/chart/presence_start_end')
        self.assertEqual(resp.status_code, 200)

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_users_view_xml(self):
        """
        Test correct return new users api
        """
        resp = self.client.get('/api/v2/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        # user_10
        self.assertDictEqual(data['10'], {
            u'avatar': u'https://intranet.stxnext.pl/api/images/users/10',
            u'name': u'Maciej Z.'
            })

        # user_11
        self.assertDictEqual(data['11'], {
            u'avatar': u'https://intranet.stxnext.pl/api/images/users/11',
            u'name': u'Maciej D.'
            })

    def test_mean_time_weekday_view(self):
        """
        Test correct return of mean presence time of given user
        grouped by weekday.
        """

        # user_10
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertListEqual(data, [
            [u'Mon', 0],
            [u'Tue', 30047.0],
            [u'Wed', 24465.0],
            [u'Thu', 23705.0],
            [u'Fri', 0],
            [u'Sat', 0],
            [u'Sun', 0], ])

        # user_11
        resp = self.client.get('/api/v1/mean_time_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertListEqual(data, [
            [u'Mon', 24123.0],
            [u'Tue', 16564.0],
            [u'Wed', 25321.0],
            [u'Thu', 22984.0],
            [u'Fri', 6426.0],
            [u'Sat', 0],
            [u'Sun', 0], ])

    def test_presence_weekday_view(self):
        """
        Test correct return of total presence time of given user
        grouped by weekday.
        """

        # user_10
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertListEqual(data, [
            [u'Weekday', u'Presence (s)'],
            [u'Mon', 0],
            [u'Tue', 30047],
            [u'Wed', 24465],
            [u'Thu', 23705],
            [u'Fri', 0],
            [u'Sat', 0],
            [u'Sun', 0], ])

        # user_11
        resp = self.client.get('/api/v1/presence_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertListEqual(data, [
            [u'Weekday', u'Presence (s)'],
            [u'Mon', 24123],
            [u'Tue', 16564],
            [u'Wed', 25321],
            [u'Thu', 45968],
            [u'Fri', 6426],
            [u'Sat', 0],
            [u'Sun', 0], ])

    def test_presence_start_end_view(self):
        """
        Test correct return of average time for start and end work.
        """

        # user_10
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertListEqual(data, [
            [u'Mon', 0, 0],
            [u'Tue', 34745.0, 64792.0],
            [u'Wed', 33592.0, 58057.0],
            [u'Thu', 38926.0, 62631.0],
            [u'Fri', 0, 0],
            [u'Sat', 0, 0],
            [u'Sun', 0, 0], ])

        # user_11
        resp = self.client.get('/api/v1/presence_start_end/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertListEqual(data, [
            [u'Mon', 33134.0, 57257.0],
            [u'Tue', 33590.0, 50154.0],
            [u'Wed', 33206.0, 58527.0],
            [u'Thu', 35602.0, 58586.0],
            [u'Fri', 47816.0, 54242.0],
            [u'Sat', 0, 0],
            [u'Sun', 0, 0]])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_cache_get_data(self):
        """
        Test Caching decorator to global variable.
        """
        data = utils.get_data()
        main.app.config.update({'TEST_DATA_CSV': TEST_CACHE_DATA})
        cache_data = utils.get_data()
        self.assertEqual(data, cache_data)

    def test_group_by_weekday(self):
        """
        Testing groups presence entries by weekday
        """
        import_data = utils.get_data()
        # user_10
        user_10 = utils.group_by_weekday(import_data[10])
        self.assertEqual(user_10.keys(), range(7))
        self.assertDictEqual(user_10, {
            0: [],
            1: [30047],
            2: [24465],
            3: [23705],
            4: [],
            5: [],
            6: [],
        })

        # user_11
        user_11 = utils.group_by_weekday(import_data[11])
        self.assertEqual(user_11.keys(), range(7))
        self.assertDictEqual(user_11, {
            0: [24123],
            1: [16564],
            2: [25321],
            3: [22969, 22999],
            4: [6426],
            5: [],
            6: [],
        })

    def test_mean_group_by_weekday_seconds(self):
        """
        Testing groups presence entries by weekday with seconds
        """
        import_data = utils.get_data()
        # user_10
        user_10 = utils.mean_group_by_weekday_seconds(import_data[10])
        self.assertEqual(user_10.keys(), range(7))
        self.assertDictEqual(user_10, {
            0: {'end': [], 'start': []},
            1: {'end': [64792], 'start': [34745]},
            2: {'end': [58057], 'start': [33592]},
            3: {'end': [62631], 'start': [38926]},
            4: {'end': [], 'start': []},
            5: {'end': [], 'start': []},
            6: {'end': [], 'start': []}
            })

        # user_11
        user_11 = utils.mean_group_by_weekday_seconds(import_data[11])
        self.assertEqual(user_11.keys(), range(7))
        self.assertDictEqual(user_11, {
            0: {'end': [57257], 'start': [33134]},
            1: {'end': [50154], 'start': [33590]},
            2: {'end': [58527], 'start': [33206]},
            3: {'end': [60085, 57087], 'start': [37116, 34088]},
            4: {'end': [54242], 'start': [47816]},
            5: {'end': [], 'start': []},
            6: {'end': [], 'start': []}
            })

    def test_seconds_since_midnight(self):
        """
        Test Calculations amount of seconds since midnight.
        """
        self.assertEqual(utils.seconds_since_midnight(
            datetime.time(0, 1, 0)), 60)
        self.assertEqual(utils.seconds_since_midnight(
            datetime.time(0, 10, 0)), 600)
        self.assertEqual(utils.seconds_since_midnight(
            datetime.time(0, 30, 30)), 1830)
        self.assertEqual(utils.seconds_since_midnight(
            datetime.time(1, 30, 30)), 5430)
        self.assertEqual(utils.seconds_since_midnight(
            datetime.time(3, 0, 0,)), 10800)
        self.assertEqual(utils.seconds_since_midnight(
            datetime.time(5, 30, 0)), 19800)
        self.assertEqual(utils.seconds_since_midnight(
            datetime.time(10, 0, 0)), 36000)
        self.assertEqual(utils.seconds_since_midnight(
            datetime.time(23, 0, 0)), 82800)

    def test_interval(self):
        """
        Test calculations inverval in seconds between two
        datetime.time objects.
        """

        self.assertEqual(utils.interval(
            datetime.time(02, 00, 00),
            datetime.time(02, 00, 50)), 50)
        self.assertEqual(utils.interval(
            datetime.time(02, 00, 00),
            datetime.time(01, 58, 43)), -77)
        self.assertEqual(utils.interval(
            datetime.time(10, 30, 00),
            datetime.time(11, 00, 00)), 1800)
        self.assertEqual(utils.interval(
            datetime.time(15, 00, 00),
            datetime.time(14, 30, 00)), -1800)
        self.assertEqual(utils.interval(
            datetime.time(10, 00, 00),
            datetime.time(11, 00, 00)), 3600)
        self.assertEqual(utils.interval(
            datetime.time(18, 00, 00),
            datetime.time(17, 00, 00)), -3600)
        self.assertEqual(utils.interval(
            datetime.time(00, 00, 00),
            datetime.time(10, 00, 00)), 36000)
        self.assertEqual(utils.interval(
            datetime.time(12, 00, 00),
            datetime.time(05, 00, 00)), -25200)

    def test_mean(self):
        """
        Test calculations of arithmetic mean. Returns zero for empty lists.
        float(sum(items)) / len(items) if len(items) > 0 else 0
        """

        self.assertAlmostEqual(utils.mean([0.2, 0.4, 0.3]), 0.3)
        self.assertEqual(utils.mean([0, 0, 0]), 0)
        self.assertEqual(utils.mean([0, 10]), 5)
        self.assertEqual(utils.mean([10, 10]), 10)
        self.assertEqual(utils.mean([10, 20, 80, 100]), 52.5)
        self.assertEqual(utils.mean([26000, 36000, 1000]), 21000)
        self.assertEqual(utils.mean([25200, 3600, 1800, 100]), 7675)


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
