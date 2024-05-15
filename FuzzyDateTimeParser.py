#!/usr/bin/env python
# coding: utf-8
"""Parse date and time strings according to user preference, system environment, and heuristics.

TL;DR turning a string representation of a date or time into a numeric representation is hard.

Depending on where you are in the world (or where your operating system believes
you are), the year, month, or day can come first. The separators between the
numbers vary, sometimes simple punctuation, sometimes a letter or character,
depending on the language. So use a little help from the user plus some heuristics.

If the user sets D_FMT in the OS environment, use that to parse the date string.
If D_FMT is not set, or if the parsing fails, the rest of the algorithm is:

* Simplify the date string into numbers separated by single spaces
* Use a list of common formats to try to parse the simplified date string
* If the parsing is successful, move that format string to the head of the list
* If the parsing throws an exception, try the next format string
* If we get to the end of the format list, throw an exception

The list of formats is initially ordered based on whether we find the format
characters for day (d or e) or month (m) first in the locale's D_FMT string.

Parsing a time is marginally easier than parsing a date; the first number is always the
hours, then the minutes, then the seconds, but the separators, 12-hour vs. 24-hour,
placement of AM/PM, whether the hours have a leading zero, etc. can vary.

Same algorithm for the time: use T_FMT from the environment if set, otherwise
simplify the time into digits, spaces, and AM/PM, and then try to parse with
various formats.
"""

import datetime
import locale
import os
import re


class FuzzyDateTimeParser:
    # Formats to try for parsing a date and a time
    date_formats = []
    time_formats = ["%H %M %S", "%I %M %S %p", "%p %I %M %S"]

    # User can specify D_FMT and/or T_FMT, which will take first priority
    d_fmt = os.getenv("D_FMT", None)
    t_fmt = os.getenv("T_FMT", None)

    @staticmethod
    def init():
        """Initialize the array of date formats for parsing
        :was
                Use `locale.nl_langinfo(locale.D_FMT)` to see if the day is first,
                decide if "%d %m %Y" and "%d %m %y" comes first in the list, or
                "%m %d %Y" and "%m %d %y" do. Also put the year-month-day format
                in the list.
        """
        if FuzzyDateTimeParser.is_day_first(locale.nl_langinfo(locale.D_FMT)):
            FuzzyDateTimeParser.date_formats = [
                "%d %m %Y",
                "%d %m %y",
                "%m %d %Y",
                "%m %d %y",
                "%Y %m %d",
            ]
        else:
            FuzzyDateTimeParser.date_formats = [
                "%m %d %Y",
                "%m %d %y",
                "%Y %m %d",
                "%d %m %Y",
                "%d %m %y",
            ]

    @staticmethod
    def is_day_first(d_fmt):
        """Determine if the default locale puts the month or day first

        Scan a date format string for the format characters for day (d or e) or
        month (m), and return True/False as soon as we see one of those.

        Returns:
            True if the day comes before the month in the date string
        """
        for ch in d_fmt:
            if ch == "d" or ch == "e":
                return True
            if ch == "m":
                return False

        # Probably should have already found d/e or m, so IDK?
        return False

    @staticmethod
    def simplify_date_string(date_str):
        """Simplify date string by replacing all non-digits with a space.

        For example, "2024. 05. 11" becomes "2024 05 11". Similarly, any date
        strings that use extra letters/characters (such as "11.5.2024 г." or
        "2024年05月11日") have those removed and replaced with a single space.

        Params:
            date_str - string representing a date

        Returns:
            the string with any non-digits replaced by a single space, no
            leading or trailing spaces, either
        """
        return re.sub("\D+", " ", date_str).strip()

    @staticmethod
    def simplify_time_string(time_str):
        """Simplify time string by replacing all non-digits with a space, but save AM/PM

        Params:
            time_str - string representing a time

        Returns:
            the string with any non-digits replaced by a single space, with any AM/PM
            preserved, no leading or trailing spaces, either
        """
        return re.sub("[^APMapm\d]+", " ", time_str).strip()

    @staticmethod
    def parse_date(date_str):
        """Parse a date string.

        Try to parse with a user-supplied date format if available. Then simplify
        the string to just numbers and spaces and try parsing with various formats.
        If one of those formats is successful, try that one first next time.

        Note that modifying the list of formats inside the loop is okay-ish, because
        we exit the loop immediately after modifying the list.

        Params:
            date_str - string representing a date

        Returns:
            datetime representing the best guess at the date the string represents.
            Or it raises a ValueError.
        """
        # First try to parse with user-supplied date format
        try:
            if FuzzyDateTimeParser.d_fmt is not None:
                return datetime.datetime.strptime(date_str, FuzzyDateTimeParser.d_fmt)
        except ValueError:
            pass

        # Now simplify the date string and try the various formats
        simp = FuzzyDateTimeParser.simplify_date_string(date_str)
        for idx, fmt in enumerate(FuzzyDateTimeParser.date_formats):
            try:
                d = datetime.datetime.strptime(simp, fmt)
                # If we got here, parsing was successful, so move this format
                # to thefront of the list and then return the parsed value
                FuzzyDateTimeParser.date_formats.insert(
                    0, FuzzyDateTimeParser.date_formats.pop(idx)
                )
                return d
            except ValueError:
                pass
        # nothing parsed correctly
        raise ValueError(f"{date_str} ({simp}) could not be parsed as a date")

    @staticmethod
    def parse_time(time_str):
        """Parse a time string.

        Same logic as parse_date, just has fewer formats and has to preserve AM/PM.

        Params:
            time_str - string representing a time

        Returns:
            time representing the best guess at the time the string represents.
            Or it raises a ValueError.
        """
        # First try to parse with user-supplied time format
        try:
            if FuzzyDateTimeParser.t_fmt is not None:
                return datetime.datetime.strptime(
                    time_str, FuzzyDateTimeParser.t_fmt
                ).time()
        except ValueError:
            pass

        # Now simplify the time string and try the various formats
        simp = FuzzyDateTimeParser.simplify_time_string(time_str)
        for idx, fmt in enumerate(FuzzyDateTimeParser.time_formats):
            try:
                t = datetime.datetime.strptime(simp, fmt).time()
                FuzzyDateTimeParser.time_formats.insert(
                    0, FuzzyDateTimeParser.time_formats.pop(idx)
                )
                return t
            except ValueError:
                pass
        # nothing parsed correctly
        raise ValueError(f"{time_str} ({simp}) could not be parsed as a time")


FuzzyDateTimeParser.init()
