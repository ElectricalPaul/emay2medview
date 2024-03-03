#!/usr/bin/env python
# coding: utf-8
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Paul Fagerburg
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Read data files in CVS format produces by EMAY brand pulse oximeters.


This class implements an iterator that returns tuples of a timestamp,
an SpO2 reading, and a Pulse Rate reading.

Usage example:
```
with open("sample.csv", newline="") as csvfile:
    emay = EmayFileReader.EmayFileReader(csvfile)

    for val in emay:
        print(str(val[0]), val[1], val[2])

2024-02-26 21:10:35 93 83
2024-02-26 21:10:36 93 83
etc.
```

The software provided with EMAY pulse oximiters creates a CSV file
containing all of the data.

The first row is a header:
    Date,Time,SpO2(%),PR(bpm)

Each row after that contains a date (in USA month/day/year order), a time
in 12-hour format, an integer for the SpO2%, and an integer for the pulse
rate:
    2/26/2024,9:10:35 PM,93,83

Based on code by user "joeblough", used by permission. Original post at
https://www.apneaboard.com/forums/Thread-python-file-converter-for-EMAY-sleep-pulse-oximeter
"""

import csv
import datetime
import logging
import sys


class EmayFileReader:
    def __init__(self, csvfile):
        self.reader = csv.DictReader(csvfile)

        if self.reader.fieldnames != ["Date", "Time", "SpO2(%)", "PR(bpm)"]:
            logging.error(f"CSV file does not appear to be a valid EMAY CSV file")
            self.reader = None

    def __iter__(self):
        return self

    def __next__(self):
        try:
            row = next(self.reader)
        except TypeError:
            raise StopIteration

        try:
            date_and_time = row["Date"] + " " + row["Time"]
            timestamp = datetime.datetime.strptime(
                date_and_time, "%m/%d/%Y %I:%M:%S %p"
            )
        except (ValueError, AttributeError):
            logging.error(
                f"Invalid date/time '{date_and_time}' on line {self.reader.line_num}"
            )
            raise StopIteration

        try:
            o2 = int(row["SpO2(%)"])
        except ValueError:
            # If the field is empty, `row["SpO2(%)"]` is `''`
            # `int('')` raises ValueError
            logging.warning(f"Empty/invalid SpO2(%) value line {self.reader.line_num}")
            o2 = None
        except TypeError:
            # If the field is missing, `row["SpO2(%)"]` is `None`
            # `int(None)` raises TypeError
            logging.error(f"Missing SpO2(%) value line {self.reader.line_num}")
            raise StopIteration

        try:
            bpm = int(row["PR(bpm)"])
        except ValueError:
            logging.warning(f"Empty/invalid PR(bpm) value line {self.reader.line_num}")
            bpm = None
        except TypeError:
            logging.error(f"Missing PR(bpm) value line {self.reader.line_num}")
            raise StopIteration

        return (timestamp, o2, bpm)
