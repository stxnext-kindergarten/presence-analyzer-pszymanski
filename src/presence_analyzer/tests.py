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
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

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

    def test_group_by_weekday(self):
        """
        Testing groups presence entries by weekday
        """
        import_data = utils.get_data()
        user_10 = utils.group_by_weekday(import_data[10])
        self.assertEqual(user_10.keys(), range(7))
        self.assertEqual(user_10[0], [])
        self.assertEqual(user_10[1], [30047])
        self.assertEqual(user_10[2], [24465])
        self.assertEqual(user_10[3], [23705])
        self.assertEqual(user_10[4], [])
        self.assertEqual(user_10[5], [])
        self.assertEqual(user_10[6], [])

        user_11 = utils.group_by_weekday(import_data[11])
        self.assertEqual(user_11.keys(), range(7))
        self.assertEqual(user_11[0], [24123])
        self.assertEqual(user_11[1], [16564])
        self.assertEqual(user_11[2], [25321])
        self.assertEqual(user_11[3], [22969, 22999])
        self.assertEqual(user_11[4], [6426])
        self.assertEqual(user_11[5], [])
        self.assertEqual(user_11[6], [])

    def test_seconds_since_midnight(self):
        """
        Test Calculations amount of seconds since midnight.
        """
        data = utils.seconds_since_midnight
        self.assertEqual(data(
            datetime.time(0, 1, 0)), 60)
        self.assertEqual(data(
            datetime.time(0, 10, 0)), 600)
        self.assertEqual(data(
            datetime.time(0, 30, 30)), 1830)
        self.assertEqual(data(
            datetime.time(1, 30, 30)), 5430)
        self.assertEqual(data(
            datetime.time(3, 0, 0,)), 10800)
        self.assertEqual(data(
            datetime.time(5, 30, 0)), 19800)
        self.assertEqual(data(
            datetime.time(10, 0, 0)), 36000)
        self.assertEqual(data(
            datetime.time(23, 0, 0)), 82800)

    def test_interval(self):
        """
        Test calculations inverval in seconds between two
        datetime.time objects.
        """
        data = utils.interval
        self.assertEqual(data(
            datetime.time(02, 00, 00),
            datetime.time(02, 00, 50)), 50)
        self.assertEqual(data(
            datetime.time(02, 00, 00),
            datetime.time(01, 58, 43)), -77)
        self.assertEqual(data(
            datetime.time(10, 30, 00),
            datetime.time(11, 00, 00)), 1800)
        self.assertEqual(data(
            datetime.time(15, 00, 00),
            datetime.time(14, 30, 00)), -1800)
        self.assertEqual(data(
            datetime.time(10, 00, 00),
            datetime.time(11, 00, 00)), 3600)
        self.assertEqual(data(
            datetime.time(18, 00, 00),
            datetime.time(17, 00, 00)), -3600)
        self.assertEqual(data(
            datetime.time(00, 00, 00),
            datetime.time(10, 00, 00)), 36000)
        self.assertEqual(data(
            datetime.time(12, 00, 00),
            datetime.time(05, 00, 00)), -25200)

    def test_mean(self):
        """
        Test calculations of arithmetic mean. Returns zero for empty lists.
        float(sum(items)) / len(items) if len(items) > 0 else 0
        """
        dane = utils.mean
        self.assertEqual(dane([0, 0, 0]), 0)
        self.assertEqual(dane([0, 10]), 5)
        self.assertEqual(dane([10, 10]), 10)
        self.assertEqual(dane([10, 20, 80, 100]), 52.5)
        self.assertEqual(dane([26000, 36000, 1000]), 21000)
        self.assertEqual(dane([25200, 3600, 1800, 100]), 7675)


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
