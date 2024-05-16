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
import EmayFileReader
import O2InsightProReader
import MedViewFileWriter
import click
from tqdm import tqdm


@click.command()
@click.argument("csv", type=click.Path(exists=True))
@click.option(
    "--output-file",
    "-o",
    default=None,
    help="Uses location and naming convention of the CSV file if not specified",
)
@click.option(
    "--input-format",
    "-f",
    envvar="CSV_FORMAT",
    type=click.Choice(["emay", "o2insight"]),
    default="emay",
    help="CSV file data format",
)
@click.option(
    "--time-offset",
    type=click.INT,
    default=0,
    help="Adjust times in the output data by this many seconds (positive or negative)",
)
def main(**params):
    input_filename = params["csv"]
    input_format = params["input_format"]
    timeOffset = params["time_offset"]

    if params["output_file"] is None:
        basename, _ = os.path.splitext(input_filename)
        output_filename = basename + ".dat"
        print(f"Converting {input_filename} into {output_filename} ...")
    else:
        output_filename = params["output_file"]

    with open(input_filename, newline="") as csvfile:
        if input_format == "o2insight":
            csv = O2InsightProReader.O2InsightProReader(csvfile)
        else:
            csv = EmayFileReader.EmayFileReader(csvfile)

        with open(output_filename, "wb") as datfile:
            with MedViewFileWriter.MedViewFileWriter(
                datfile, timeOffset
            ) as medview, progress(description="Processing records") as bar:
                for rec in csv:
                    if not rec[1] or not rec[2]:
                        logging.info(f"Missing data for time {rec[0]}, skip")
                        bar.update()
                        continue

                    medview.write_record(rec[0], rec[1], rec[2])
                    bar.update()


def progress(description=None, max=0, unit=None, color=None, position=None, leave=True):
    if unit is None:
        unit = " records"
    else:
        unit = " {unit}".format(unit=unit)

    bar = tqdm(unit=unit, total=max, colour=color, position=position, leave=leave)

    if description is not None:
        bar.set_description(description)

    return bar


def o2insight2medview():
    os.environ["CSV_FORMAT"] = "o2insight"
    main()


if __name__ == "__main__":
    main()
