#!/usr/bin/env python
# coding: utf-8
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Paul Fagerburg
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unit tests for O2InsightProReader"""

import datetime
import io
import unittest
import O2InsightProReader


class O2InsightProReaderTests(unittest.TestCase):
    header = "Time,SpO2(%),Pulse Rate(bpm),Motion,SpO2 Reminder,PR Reminder,"

    def test_bad_header(self):
        # We don't decode the Motion, SpO2 Reminder, or PR Reminder fields but
        # they need to be there so we're confident this is the correct format
        csv = io.StringIO(
            """Time,SpO2(%),Pulse Rate(bpm),,,,
09:24:47AM May 22, 2024",96,50,0,0,0,
"""
        )
        reader = O2InsightProReader.O2InsightProReader(csv)
        self.assertRaises(StopIteration, next, reader)

    def test_missing_fields(self):
        # We must have both SpO2 and BPM.
        csv = io.StringIO(
            """Time,SpO2(%),Pulse Rate(bpm),Motion,SpO2 Reminder,PR Reminder,
"09:26:07AM May 22, 2024",96
"""
        )
        reader = O2InsightProReader.O2InsightProReader(csv)
        self.assertRaises(StopIteration, next, reader)

        csv = io.StringIO(
            """Time,SpO2(%),Pulse Rate(bpm),Motion,SpO2 Reminder,PR Reminder,
"09:26:07AM May 22, 2024"
"""
        )
        reader = O2InsightProReader.O2InsightProReader(csv)
        self.assertRaises(StopIteration, next, reader)

    def test_empty_fields(self):
        # If SpO2 or BPM are empty, the value is `None`
        #
        # The difference between missing and empty is whether there is a comma;
        # "a,b,c" has 3 fields
        # "a,," also has 3 fields, but the last two fields are empty
        # "a" only has 1 field
        csv = io.StringIO(
            """Time,SpO2(%),Pulse Rate(bpm),Motion,SpO2 Reminder,PR Reminder,
"09:26:35AM May 22, 2024",95,,0,0,0,
"""
        )
        reader = O2InsightProReader.O2InsightProReader(csv)
        row = next(reader)
        self.assertEqual(row[1], 95)
        self.assertIsNone(row[2], "PR(bpm) should be None")

        csv = io.StringIO(
            """Time,SpO2(%),Pulse Rate(bpm),Motion,SpO2 Reminder,PR Reminder,
"09:27:23AM May 22, 2024",,,0,0,0,
"""
        )
        reader = O2InsightProReader.O2InsightProReader(csv)
        row = next(reader)
        self.assertIsNone(row[1], "SpO2(%) should be None")
        self.assertIsNone(row[2], "PR(bpm) should be None")

        csv = io.StringIO(
            """Time,SpO2(%),Pulse Rate(bpm),Motion,SpO2 Reminder,PR Reminder,
"09:28:03AM May 22, 2024",,50,18,0,0,
"""
        )
        reader = O2InsightProReader.O2InsightProReader(csv)
        row = next(reader)
        self.assertIsNone(row[1], "SpO2(%) should be None")
        self.assertEqual(row[2], 50)

    def test_happy_path(self):
        csv = io.StringIO(
            """Time,SpO2(%),Pulse Rate(bpm),Motion,SpO2 Reminder,PR Reminder,
"09:24:47AM May 22, 2024",95,50,0,0,0,
"09:24:51AM May 22, 2024",96,53,1,0,0,
"09:24:55AM May 22, 2024",96,55,0,0,0,
"""
        )
        reader = O2InsightProReader.O2InsightProReader(csv)
        row = next(reader)
        self.assertEqual(row[0], datetime.datetime(2024, 5, 22, 9, 24, 47))
        self.assertEqual(row[1], 95)
        self.assertEqual(row[2], 50)

        row = next(reader)
        self.assertEqual(row[0], datetime.datetime(2024, 5, 22, 9, 24, 51))
        self.assertEqual(row[1], 96)
        self.assertEqual(row[2], 53)

        row = next(reader)
        self.assertEqual(row[0], datetime.datetime(2024, 5, 22, 9, 24, 55))
        self.assertEqual(row[1], 96)
        self.assertEqual(row[2], 55)

        self.assertRaises(StopIteration, next, reader)

def test_sensor_off(self):
        # When the device is unable to get a reading, like when the sensor
        # is off your finger, it records SpO2=255 and PR=65535
        csv = io.StringIO(
            """Time,SpO2(%),Pulse Rate(bpm),Motion,SpO2 Reminder,PR Reminder,
"09:25:19AM May 22, 2024",96,54,20,0,0,
"09:25:23AM May 22, 2024",255,65535,1,0,0,
"09:25:27AM May 22, 2024",255,65535,0,0,0,
"09:25:31AM May 22, 2024",255,65535,14,0,0,
"09:25:35AM May 22, 2024",97,57,0,0,0,
"""
        )
        reader = O2InsightProReader.O2InsightProReader(csv)
        row = next(reader)
        self.assertEqual(row[0], datetime.datetime(2024, 5, 22, 9, 25, 19))
        self.assertEqual(row[1], 96)
        self.assertEqual(row[2], 54)

        # Current behavior is to transparently skip rows with "sensor off" values
        row = next(reader)
        self.assertEqual(row[0], datetime.datetime(2024, 5, 22, 9, 25, 35))
        self.assertEqual(row[1], 97)
        self.assertEqual(row[2], 57)

if __name__ == "__main__":
    unittest.main()
