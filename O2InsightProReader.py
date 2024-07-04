#!/usr/bin/env python
# coding: utf-8

"""
Read data files in CVS format produced by Wellue's O2 Insight Pro.

This has been tested with data from Wellue's O2Ring Oximeter.

The first row is the header:
    Time,SpO2(%),Pulse Rate(bpm),Motion,SpO2 Reminder,PR Reminder
        Time is in the format HH:MM:SS{AM|PM} Month Day, Year
        HH is 12-hour format
        This appears to be independent of any OS settings for date/time formats.

    SpO2 is an integer in percent (0-100)

    Pulse Rate is an integer in beats per minute

    Motion and the Reminder fields are not used
"""

import csv
import datetime
import logging


class O2InsightProReader:
    # only have "May" data from the app at this point
    # maybe it's the full month name or the abbreviation...
    timeFormats = ["%I:%M:%S%p %B %d, %Y", "%I:%M:%S%p %b %d, %Y"]

    def __init__(self, csvfile):
        self.reader = csv.DictReader(csvfile)

        if self.reader.fieldnames[:6] != [
            "Time",
            "SpO2(%)",
            "Pulse Rate(bpm)",
            "Motion",
            "SpO2 Reminder",
            "PR Reminder",
        ]:
            logging.error(
                f"CSV file does not appear to be a valid O2 Insight Pro CSV file"
            )
            self.reader = None

    def __iter__(self):
        return self

    def __next__(self):
        try:
            row = next(self.reader)
        except TypeError:
            raise StopIteration

        for timeFormat in self.timeFormats:
            try:
                timestamp = datetime.datetime.strptime(row["Time"], timeFormat)
                break
            except ValueError:
                pass
        else:
            logging.error(
                f"Invalid date/time \"{row['Time']}\" on line {self.reader.line_num}"
            )
            raise StopIteration

        try:
            o2 = int(row["SpO2(%)"])
            # If the sensor is off, the device records 255 for SpO2
            if o2 == 255:
                o2 = None
        except ValueError:
            logging.warning(f"Empty/invalid SpO2(%) value line {self.reader.line_num}")
            o2 = None
        except TypeError:
            logging.error(f"Missing SpO2(%) value line {self.reader.line_num}")
            raise StopIteration

        try:
            bpm = int(row["Pulse Rate(bpm)"])
            # If the sensor is off, the device records 65535 for PR
            if bpm == 65535:
                bpm = None
        except ValueError:
            logging.warning(
                f"Empty/invalid Pulse Rate(bpm) value line {self.reader.line_num}"
            )
            bpm = None
        except TypeError:
            logging.error(f"Missing Pulse Rate(bpm) value line {self.reader.line_num}")
            raise StopIteration

        return (timestamp, o2, bpm)
