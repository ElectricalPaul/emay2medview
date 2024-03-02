#!/usr/bin/env python
# coding: utf-8
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Paul Fagerburg
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Convert an EMAY pulse oximiter CSV file into the MD300W1 DAT file format that OSCAR can import.

Based on code by user "joeblough", used by permission. Original post at
https://www.apneaboard.com/forums/Thread-python-file-converter-for-EMAY-sleep-pulse-oximeter
"""

import logging
import os
import sys
import EmayFileReader
import MedViewFileWriter


def process_emay_csv(input_filename):
    basename, _ = os.path.splitext(input_filename)
    output_filename = basename + ".dat"
    print(f"Converting {input_filename} into {output_filename} ...")

    with open(input_filename, newline="") as csvfile:
        emay = EmayFileReader.EmayFileReader(csvfile)
        with open(output_filename, "wb") as datfile:
            with MedViewFileWriter.MedViewFileWriter(datfile) as medview:
                for rec in emay:
                    medview.write_record(rec[0], rec[1], rec[2])


if __name__ == "__main__":
    for filename in sys.argv[1:]:
        process_emay_csv(filename)
