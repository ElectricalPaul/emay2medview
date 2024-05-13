#!/usr/bin/env python
# coding: utf-8

from FuzzyDateTimeParser import FuzzyDateTimeParser as fdtp
import datetime
import unittest

class FuzzyDateParserTests(unittest.TestCase):
    def test_is_day_first(self):
        # Test cases where the day comes first
        self.assertTrue(fdtp.is_day_first("%d/%m/%Ey"))
        self.assertTrue(fdtp.is_day_first("%d/%m/%Y"))
        self.assertTrue(fdtp.is_day_first("%d/%m/%y"))
        self.assertTrue(fdtp.is_day_first("%e/%m/%Y"))

        # Month comes first
        self.assertFalse(fdtp.is_day_first("%m/%d/%Y"))
        self.assertFalse(fdtp.is_day_first("%m/%e/%y"))

        # Year-month-day
        self.assertFalse(fdtp.is_day_first("%Y-%m-%d"))

    def test_simplify_date_string(self):
        self.assertEqual(fdtp.simplify_date_string("2024. 05. 11"), "2024 05 11")
        self.assertEqual(fdtp.simplify_date_string("5/11/24"), "5 11 24")
        self.assertEqual(fdtp.simplify_date_string("11.5.2024 г."), "11 5 2024")
        self.assertEqual(fdtp.simplify_date_string("2024年05月11日"), "2024 05 11")

    def test_parse_with_d_fmt(self):
        # Test parsing if D_FMT was specified
        # Instead of messing with os.environ, just set the value in the class
        fdtp.d_fmt = "%m/%d/%Y"
        self.assertEqual(fdtp.parse_date("05/11/2024"), datetime.datetime(year=2024, month=5, day=11))
        fdtp.d_fmt = "%d.%m.%Y г."
        self.assertEqual(fdtp.parse_date("11.5.2024 г."), datetime.datetime(year=2024, month=5, day=11))

    def test_parse_without_d_fmt(self):
        fdtp.d_fmt = None
        self.assertEqual(fdtp.parse_date("01/01/2024"), datetime.datetime(year=2024, month=1, day=1))
        self.assertEqual(fdtp.parse_date("1/1/24"), datetime.datetime(year=2024, month=1, day=1))
        self.assertEqual(fdtp.parse_date("1.1.2024 г."), datetime.datetime(year=2024, month=1, day=1))
        self.assertEqual(fdtp.parse_date("2024年01月01日"), datetime.datetime(year=2024, month=1, day=1))

        # A nonsensical month-year-day format fails
        self.assertRaises(ValueError, fdtp.parse_date, "05-2024-11")

    def test_simplify_time_string(self):
        self.assertEqual(fdtp.simplify_time_string("12:34:56"), "12 34 56")
        self.assertEqual(fdtp.simplify_time_string("12:34:56 PM"), "12 34 56 PM")
        self.assertEqual(fdtp.simplify_time_string("am 12-34-56"), "am 12 34 56")
        self.assertEqual(fdtp.simplify_time_string("%23時59分00秒"), "23 59 00")

    def test_parse_with_t_fmt(self):
        # Test parsing if T_FMT was specified
        # Instead of messing with os.environ, just set the value in the class
        fdtp.t_fmt = "%H:%M:%S"
        self.assertEqual(fdtp.parse_time("12:34:56"), datetime.time(hour=12, minute=34, second=56))
        fdtp.t_fmt = "%I:%M:%s %p"
        self.assertEqual(fdtp.parse_time("12:34:56 pm"), datetime.time(hour=12, minute=34, second=56))

    def test_parse_without_t_fmt(self):
        fdtp.t_fmt = None
        self.assertEqual(fdtp.parse_time("23-59-00"), datetime.time(hour=23, minute=59, second=00))
        self.assertEqual(fdtp.parse_time("11:59:00 PM"), datetime.time(hour=23, minute=59, second=00))
        self.assertEqual(fdtp.parse_time("%23時59分00秒"), datetime.time(hour=23, minute=59, second=00))
        self.assertEqual(fdtp.parse_time("AM 12:34:56"), datetime.time(hour=0, minute=34, second=56))

    def test_date_format_promotion(self):
        # Verify that the logic works to move a successful format to the front
        fdtp.d_fmt = None
        # Get the last value, and then format a date according to it
        last_fmt = fdtp.date_formats[-1]
        christmas = datetime.datetime(year=2000, month=12, day=25)
        date_str = christmas.strftime(last_fmt)
        # Now parse that date, and it should move `last_fmt` to the front
        self.assertEqual(fdtp.parse_date(date_str), christmas)
        self.assertEqual(fdtp.date_formats[0], last_fmt)

    def test_time_format_promotion(self):
        # Verify that the logic works to move a successful format to the front
        fdtp.t_fmt = None
        # Get the second-to-last value, and then format a time according to it
        last_fmt = fdtp.time_formats[-2]
        high_noon = datetime.time(hour=12, minute=0, second=0)
        time_str = high_noon.strftime(last_fmt)
        # Now parse that time, and it should move `old_back` to the front
        self.assertEqual(fdtp.parse_time(time_str), high_noon)
        self.assertEqual(fdtp.time_formats[0], last_fmt)

if __name__ == "__main__":
    unittest.main()
