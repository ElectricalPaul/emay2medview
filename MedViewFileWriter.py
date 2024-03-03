#!/usr/bin/env python
# coding: utf-8
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Paul Fagerburg
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Write data files in MedView[TM] format.

MedView is the name of the software that works with ChoiceMMed[TM]
pulse oximeters.

This class writes time-stamped SpO2 and BPM values to a binary file.
Usage example:

```
with open(output_filename, "wb") as datfile:
    with MedViewFileWriter.MedViewFileWriter(datfile) as dat:
        # ...
        # [magic happens here, and now ts is a date and time,
        # and o2 and bpm have valid values]
        # ...
        dat.write_record(ts, o2, bpm)
```
When the MedViewFileWriter goes out of scope, the file will be updated
with the count of records written to it before the file object itself
is destructed and the file gets closed.

A file starts with an ID byte (which we set to 0), and the number of
records in 16-bit little-endian format. A file can have at most 65535
records.

Each record in the file is 11 bytes. The bytes are, in order:
    0 - purpose unknown
    0 - purpose unknown
    0 - purpose unknown
    Year, 2-digits only
    Month
    Day
    Hour (0-23)
    Minute
    Second
    SpO2
    BPM

ChoiceMMed and MedView are trademarks of Beijing Choice Electronic Tech Co.
I found the registration for ChoiceMMed, but couldn't find it for MedView,
but I'm assuming that's trademarked, too.

Based on code by user "joeblough", used by permission. Original post at
https://www.apneaboard.com/forums/Thread-python-file-converter-for-EMAY-sleep-pulse-oximeter
"""

import logging
import struct
import unittest


class MedViewFileWriter:
    def __init__(self, datfile):
        # Keep track of the number of records written to output file.
        self.records = 0
        # File handle for the DAT file
        self.datfile = datfile
        self.write_dat_header()

    def __del__(self):
        self.update_dat_header()
        self.datfile = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.update_dat_header()
        self.datfile = None

    def write_dat_header(self):
        """Write the header to the DAT file."""
        # Write the header.
        # When closing the file, we will seek back and overwrite these bytes.
        line = struct.pack("@BBB", 0, 0, 0)
        self.datfile.write(line)

    def update_dat_header(self):
        """Update the file with the count of records."""
        logging.debug(f"update_dat_header, records = {self.records}")
        # If nothing was written to the file, nothing to update
        if self.records == 0 or self.datfile is None:
            logging.debug("NOP")
            return

        assert (
            self.records <= 65535
        ), "Number of records in the file must be less than 64K."

        # Update the count of records at the start of the file.
        # seek(1) to skip the ID byte.
        self.datfile.seek(1)
        line = struct.pack("<H", self.records)
        self.datfile.write(line)

    def write_record(self, timestamp, o2, bpm):
        """Write a single data record to the file.

        If any of the parameters are invalid, the record will not be written.

        Params:
            timestamp - a datetime.datetime object
            o2 - SpO2 percentage, represented as an integer
            bpm - BPM
        """
        # If we hit the maximum number of records, log an error and exit
        if self.records >= 65535:
            logging.error("Maximum number of output records exceeded.")
            return

        try:
            o2 = int(o2)
        except:
            logging.error(f"Invalid SpO2 value: '{o2}'")
            return

        try:
            bpm = int(bpm)
        except:
            logging.error(f"Invalid BPM value: '{bpm}'")
            return

        try:
            line = struct.pack(
                "@xxxBBBBBBBB",
                int(timestamp.year - 2000),  # 2-digit year only
                int(timestamp.month),
                int(timestamp.day),
                int(timestamp.hour),
                int(timestamp.minute),
                int(timestamp.second),
                int(o2),
                int(bpm),
            )
        except (ValueError, TypeError, AttributeError):
            # The timestamp could be missing a field, or one of the fields
            # could be the wrong type or an invalid value.
            logging.error(f"Invalid timestamp: '{timestamp}'")
            return

        self.datfile.write(line)
        self.records += 1


if __name__ == "__main__":
    unittest.main()
