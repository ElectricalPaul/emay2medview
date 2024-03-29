#!/usr/bin/env python
# coding: utf-8
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Paul Fagerburg
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Unit tests for MedViewFileWriter"""

import datetime
import io
import os
import unittest
import MedViewFileWriter


class fake_timestamp:
    def __init__(self):
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0


class incomplete_timestamp:
    def __init__(self):
        self.year = 0
        self.month = 0
        self.day = 0
        # No 'hour' field
        self.minute = 0
        self.second = 0


class MedViewFileWriterTests(unittest.TestCase):
    def test_empty(self):
        # Don't write any records, verify it has 0x00 0x00 0x00
        with io.BytesIO() as datfile:
            dat = MedViewFileWriter.MedViewFileWriter(datfile)
            # Force MedViewFileWriter to update the file header
            dat = None
            datfile.seek(0)
            content = datfile.read()
            self.assertEqual(content, b"\x00\x00\x00")

    def test_single_record(self):
        # Write 1 record, verify entire contents
        with io.BytesIO() as datfile:
            dat = MedViewFileWriter.MedViewFileWriter(datfile)
            dat.write_record(datetime.datetime(2024, 3, 1, 23, 25, 00), 97, 82)
            # Force MedViewFileWriter to update the file header
            dat = None
            datfile.seek(0)
            content = datfile.read(3)
            self.assertEqual(content, b"\x00\x01\x00")
            content = datfile.read(11)
            self.assertEqual(content, b"\x00\x00\x00\x18\x03\x01\x17\x19\x00\x61\x52")

    def test_multiple_records(self):
        # Write 10 records, verify header
        with io.BytesIO() as datfile:
            dat = MedViewFileWriter.MedViewFileWriter(datfile)
            for n in range(10):
                dat.write_record(datetime.datetime(2024, 3, 1, 23, 25, n), 97, 82)
            # Force MedViewFileWriter to update the file header
            dat = None
            datfile.seek(0)
            content = datfile.read(3)
            self.assertEqual(content, b"\x00\x0a\x00")

    def test_file_full(self):
        # Write 65535 records, should be 720888 bytes and header is 0x00 0xFF 0xFF
        with io.BytesIO() as datfile:
            dat = MedViewFileWriter.MedViewFileWriter(datfile)
            for n in range(65535):
                dat.write_record(
                    datetime.datetime(2024, 3, 1, n // 3600, (n // 60) % 60, n % 60),
                    97,
                    82,
                )
            # Force MedViewFileWriter to update the file header
            dat = None
            datfile.seek(0)
            content = datfile.read(3)
            self.assertEqual(content, b"\x00\xff\xff")

    def test_file_overfull(self):
        # Write 65536 records, and the last one won't write.
        # The file should be 720888 bytes and header is 0x00 0xFF 0xFF.
        # Verify that record #65535 has contents expected, and was not overwritten
        with io.BytesIO() as datfile:
            dat = MedViewFileWriter.MedViewFileWriter(datfile)
            for n in range(65536):
                dat.write_record(
                    datetime.datetime(2024, 3, 1, n // 3600, (n // 60) % 60, n % 60),
                    97,
                    82,
                )
            # Force MedViewFileWriter to update the file header
            dat = None
            datfile.seek(0)
            content = datfile.read(3)
            self.assertEqual(content, b"\x00\xff\xff")

            # Verify last record of the file - it should be 65534
            datfile.seek(-11, os.SEEK_END)
            content = datfile.read(11)
            self.assertEqual(content, b"\x00\x00\x00\x18\x03\x01\x12\x0C\x0E\x61\x52")

    def test_too_many_records_assert(self):
        # Verify the assertion for too many records
        with io.BytesIO() as datfile:
            dat = MedViewFileWriter.MedViewFileWriter(datfile)
            # Force the error condition
            dat.records = 65536
            # Manually call the method that will assert
            self.assertRaises(AssertionError, dat.update_dat_header)
            # Put it back the way we found it
            dat.records = 0
            dat = None

    def test_invalid_values(self):
        with io.BytesIO() as datfile:
            dat = MedViewFileWriter.MedViewFileWriter(datfile)
            # Save the current offset in the file
            tell = datfile.tell()

            # Write records with invalid SpO2 values
            for spo2 in [None, "", "abc"]:
                dat.write_record(datetime.datetime(2024, 3, 3, 14, 42, 0), spo2, 82)
            # Verify nothing was written
            self.assertEqual(datfile.tell(), tell)

            # Write records with invalid BPM values
            for bpm in [None, "", "127.0.0.1"]:
                dat.write_record(datetime.datetime(2024, 3, 3, 14, 42, 0), 97, bpm)

            # Verify nothing was written
            self.assertEqual(datfile.tell(), tell)

    def test_datetime_invalid_values(self):
        with io.BytesIO() as datfile:
            dat = MedViewFileWriter.MedViewFileWriter(datfile)
            # Save the current offset in the file
            tell = datfile.tell()
            # Make a timestamp with one of the values invalid
            ts = fake_timestamp()
            ts.year = None
            dat.write_record(ts, 100, 100)

            # Verify nothing was written
            self.assertEqual(datfile.tell(), tell)

    def test_datetime_missing_values(self):
        with io.BytesIO() as datfile:
            dat = MedViewFileWriter.MedViewFileWriter(datfile)
            # Save the current offset in the file
            tell = datfile.tell()
            # Make a timestamp with one of the fields missing
            ts = incomplete_timestamp()
            ts.year = None
            dat.write_record(ts, 100, 100)

            # Verify nothing was written
            self.assertEqual(datfile.tell(), tell)


if __name__ == "__main__":
    unittest.main()
