#!/usr/bin/env python
# coding: utf-8
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Paul Fagerburg
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unit tests for EmayFileReader"""

import datetime
import io
import unittest
import EmayFileReader


class EmayFileReaderTests(unittest.TestCase):
    def test_bad_header(self):
        csv = io.StringIO(
            "Date,Time,SpO2(%),PR(bpm),Extra,Extra2\n2/26/2024,9:10:35 PM,93,83\n"
        )
        reader = EmayFileReader.EmayFileReader(csv)
        self.assertRaises(StopIteration, next, reader)

    def test_bad_date_time(self):
        csv = io.StringIO("Date,Time,SpO2(%),PR(bpm)\n2/30/2024,9:10:35 PM,93,83\n")
        reader = EmayFileReader.EmayFileReader(csv)
        self.assertRaises(StopIteration, next, reader)

    def test_missing_fields(self):
        # We must have both SpO2 and BPM
        csv = io.StringIO("Date,Time,SpO2(%),PR(bpm)\n2/26/2024,9:10:35 PM,93\n")
        reader = EmayFileReader.EmayFileReader(csv)
        self.assertRaises(StopIteration, next, reader)

        csv = io.StringIO("Date,Time,SpO2(%),PR(bpm)\n2/26/2024,9:10:35 PM\n")
        reader = EmayFileReader.EmayFileReader(csv)
        self.assertRaises(StopIteration, next, reader)

    def test_empty_fields(self):
        # If SpO2 or BPM are empty, the value is `None`
        csv = io.StringIO("Date,Time,SpO2(%),PR(bpm)\n2/26/2024,9:10:35 PM,93,\n")
        reader = EmayFileReader.EmayFileReader(csv)
        row = next(reader)
        self.assertEqual(row[1], 93)
        self.assertIsNone(row[2], "PR(bpm) should be None")

        csv = io.StringIO("Date,Time,SpO2(%),PR(bpm)\n2/26/2024,9:10:36 PM,,\n")
        reader = EmayFileReader.EmayFileReader(csv)
        row = next(reader)
        self.assertIsNone(row[1], "SpO2(%) should be None")
        self.assertIsNone(row[2], "PR(bpm) should be None")

        csv = io.StringIO("Date,Time,SpO2(%),PR(bpm)\n2/26/2024,9:10:36 PM,,83\n")
        reader = EmayFileReader.EmayFileReader(csv)
        row = next(reader)
        self.assertIsNone(row[1], "SpO2(%) should be None")
        self.assertEqual(row[2], 83)

    def test_happy_path(self):
        csv = io.StringIO(
            """Date,Time,SpO2(%),PR(bpm)
2/26/2024,9:10:35 PM,93,83
2/26/2024,9:10:39 PM,94,92
"""
        )
        reader = EmayFileReader.EmayFileReader(csv)
        row = next(reader)
        self.assertEqual(row[0], datetime.datetime(2024, 2, 26, 21, 10, 35))
        self.assertEqual(row[1], 93)
        self.assertEqual(row[2], 83)

        row = next(reader)
        self.assertEqual(row[0], datetime.datetime(2024, 2, 26, 21, 10, 39))
        self.assertEqual(row[1], 94)
        self.assertEqual(row[2], 92)

        self.assertRaises(StopIteration, next, reader)

    def test_iso8601_date_time(self):
        """Users 'ST Dog' and 'capman' reported problems with ISO 8601 dates and times"""
        csv = io.StringIO(
            """Date,Time,SpO2(%),PR(bpm)
2021/12/10,11:32:14,98,85
"""
        )
        reader = EmayFileReader.EmayFileReader(csv)
        row = next(reader)
        self.assertEqual(row[0], datetime.datetime(2021, 12, 10, 11, 32, 14))
        self.assertEqual(row[1], 98)
        self.assertEqual(row[2], 85)

        self.assertRaises(StopIteration, next, reader)

if __name__ == "__main__":
    unittest.main()
