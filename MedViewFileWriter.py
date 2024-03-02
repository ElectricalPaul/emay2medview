#!/usr/bin/env python
# coding: utf-8
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Paul Fagerburg
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Write data files in MedView[TM] format.

MedView is the name of the software that works with ChoiceMMed[TM]
pulse oximeters.

MedView files have the same base name, plus an underscore and a
sequence number after the first one. All files use the .DAT extension.
So a set of related files might be named:
    mydata.DAT
    mydata_1.DAT
    mydata_2.DAT
Each file can have at most 65535 records.

A file starts with an ID byte (which we set to 0), and the number of
records in 16-bit little-endian format.

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
import os
import struct
import unittest


class MedViewFileWriter:
    def __init__(self, fname):
        # Get the base filename by removing the extension, if any.
        self.basename, _ = os.path.splitext(fname)
        logging.debug(f"__init__, fname = '{fname}', basename = '{self.basename}'")
        # Keep track of the number of output files created.
        self.num_files = 0
        # Keep track of the number of records written to current output file.
        self.records = 0
        # File handle for current DAT file
        self.dat_file = None
        # List of output filenames
        self.output_file_names = []

    def __del__(self):
        logging.debug(f"__del__, basename = '{self.basename}'")
        # Close the file if anything was written to it.
        if self.records != 0:
            self.close_output_file()

    def make_output_filename(self):
        """Return an output name from the base name and how many output files exist."""
        if self.num_files == 0:
            return self.basename + ".dat"

        return self.basename + "_" + str(self.num_files) + ".dat"

    def create_output_file(self):
        """Create an output file with the "next" name and write the header."""
        output_name = self.make_output_filename()
        logging.info(f"Create output file '{output_name}'")
        self.dat_file = open(output_name, "wb")
        self.output_file_names.append(output_name)
        # Write the header.
        # When closing the file, we will seek back and overwrite these bytes.
        line = struct.pack("@BBB", 0, 0, 0)
        self.dat_file.write(line)

    def close_output_file(self):
        """Update the file with the count of records and then close it."""
        logging.debug(f"close_outut_file, records = {self.records}")
        if self.records == 0 or self.dat_file is None:
            logging.debug("NOP")
            return

        assert (
            self.records <= 65535
        ), "Number of records in the file must be less than 64K."

        # Update the count of records at the start of the file.
        # seek(1) to skip the ID byte.
        self.dat_file.seek(1)
        line = struct.pack("<H", self.records)
        self.dat_file.write(line)

        # Close the file and get ready to create the next one if needed.
        self.dat_file.close()
        self.dat_file = None
        self.records = 0
        self.num_files += 1

    def write_record(self, timestamp, o2, bpm):
        """Write a single data record to the file.

        If the output file doesn't exist, it will be created and opened first.
        If the output file gets "full" (65535 records) after this write, it will be closed.

        Params:
            timestamp - a datetime.datetime object
            o2 - SpO2 percentage, represented as an integer
            bpm - BPM
        """
        try:
            o2 = int(o2)
        except:
            raise ValueError(
                f"Invalid SpO2 value: '{o2}', at or near record number {1+self.records+65536*self.num_files}"
            )

        try:
            bpm = int(bpm)
        except:
            raise ValueError(
                f"Invalid BPM value: '{bpm}', at or near record number {1+self.records+65536*self.num_files}"
            )

        # Create the output file if needed.
        if self.records == 0:
            logging.debug("records == 0, creating output file")
            self.create_output_file()

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

        self.dat_file.write(line)
        self.records += 1

        # If we hit the maximum number of records, close the file.
        # The next time we call write_record, it will create a new output file.
        if self.records == 65535:
            self.close_output_file()


if __name__ == "__main__":
    unittest.main()
