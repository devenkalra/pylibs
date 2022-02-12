import unittest
from test import support
from dkhelpers.timehelpers import TimeManager
import datetime
import pytz

class MyTestCase1(unittest.TestCase):

    # Only use setUp() and tearDown() if necessary

    def setUp(self):
        self.tf = TimeManager("America/Los_Angeles")


    def tearDown(self):
        pass

    def test_format_as_canonical(self):

        pdt = pytz.timezone('America/Los_Angeles')
        utctz = pytz.timezone('UTC')

        # No TZ
        d = datetime.datetime(2022, 1, 1)
        f = self.tf.format_as_canonical(d)
        self.assertEqual("Sat Jan 01 2022 12:00:00 AM", f)

        # UTC
        d = datetime.datetime(2022, 1, 1, tzinfo=utctz)
        f = self.tf.format_as_canonical(d, tz='UTC')
        self.assertEqual("Sat Jan 01 2022 12:00:00 AM UTC", f)

        # Pacific
        d = pdt.normalize(d)
        f = self.tf.format_as_canonical(d, tz='America/Los_Angeles')
        self.assertEqual('Fri Dec 31 2021 04:00:00 PM PST', f)

        d = datetime.datetime(2022, 1, 1, 10, 12, 56, 34512, tzinfo=pytz.UTC)
        f = self.tf.format_as_canonical(d, tz='GMT', msec=True)
        self.assertEqual("Sat Jan 01 2022 10:12:56.034512 AM UTC",f)

        d = pdt.normalize(d)
        f = self.tf.format_as_canonical(d, tz='America/Los_Angeles')
        self.assertEqual('Sat Jan 01 2022 02:12:56 AM PST', f)

        d = datetime.datetime(2022, 1, 1, 10, 12, 56, 34512, tzinfo=pytz.UTC)

        f = self.tf.format_as_canonical(d, tz="GMT")
        self.assertEqual('Sat Jan 01 2022 10:12:56 AM UTC', f)

        d = pdt.normalize(d)
        f = self.tf.format_as_canonical(d, tz='America/Los_Angeles')
        self.assertEqual('Sat Jan 01 2022 02:12:56 AM PST', f)

        d = self.tf.date(2022, 1, 1, timezone_name="America/Los_Angeles")
        f = self.tf.format_as_canonical(d, tz='America/Los_Angeles')
        self.assertEqual('Sat Jan 01 2022 12:00:00 AM PST', f)

        d = self.tf.datetime(2022, 1, 1, 10, 12, 56, timezone_name="America/Los_Angeles")
        f = self.tf.format_as_canonical(d, tz='America/Los_Angeles')
        self.assertEqual('Sat Jan 01 2022 10:12:56 AM PST', f)

        # Test feature one.

    def xtest_format_as_iso(self):
        d = datetime.datetime(2022, 1, 1)
        f = self.tf.format_as_iso(d)
        self.assertEqual("2022-01-01T08:00:00Z", f)
        d = datetime.datetime(2022, 1, 1, 10, 12, 56, 34512, tzinfo=pytz.UTC)
        f = self.tf.format_as_iso(d, msec=True)
        self.assertEqual("2022-01-01T10:12:56.034512Z",f)

        pdt = pytz.timezone('America/Los_Angeles')
        d = datetime.datetime(2022, 1, 1, 10, 12, 56, 34512)
        d = d.astimezone(pdt)

        f = self.tf.format_as_iso(d)
        self.assertEqual('2022-01-01T18:12:56Z', f)

        # Test feature one.


    def test_feature_two(self):
        # Test feature two.
        pass


if __name__ == '__main__':
    unittest.main()