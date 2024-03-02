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
emay_file = EmayFileReader("sample.csv")

for val in emay_file:
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
    def __init__(self, fname):
        self.input_filename = fname
        logging.debug(f"__init__, fname = '{fname}'")
        self.csvfile = open(self.input_filename, newline="")
        self.reader = csv.DictReader(self.csvfile)

        if self.reader.fieldnames != ["Date", "Time", "SpO2(%)", "PR(bpm)"]:
            logging.error(
                f"{self.input_filename} does not appear to be a valid EMAY CSV file"
            )
            self.reader = None

    def __iter__(self):
        return self

    def __next__(self):
        try:
            row = next(self.reader)
            date_and_time = row["Date"] + " " + row["Time"]
            timestamp = datetime.datetime.strptime(
                date_and_time, "%m/%d/%Y %I:%M:%S %p"
            )
            try:
                o2 = int(row["SpO2(%)"])
            except:
                logging.error(
                    f"Missing/empty/invalid SpO2(%) value line {self.reader.line_num}"
                )
                raise StopIteration

            try:
                bpm = int(row["PR(bpm)"])
            except:
                logging.error(
                    f"Missing/empty PR(bpm) value line {self.reader.line_num}"
                )
                raise StopIteration

            return (timestamp, o2, bpm)
        except ValueError:
            logging.error(
                f"Invalid date/time '{date_and_time}' on line {self.reader.line_num}"
            )
            raise StopIteration
        except AttributeError:
            raise StopIteration
