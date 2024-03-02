#!/usr/bin/env python
# coding: utf-8
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Paul Fagerburg
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
Run all unit tests
"""

import sys
import unittest

tests = ("EmayFileReader_test", "MedViewFileWriter_test")

if __name__ == "__main__":
    for test in tests:
        print(f"Running {test}")
        result = unittest.main(test, exit=False).result
        if result.failures or result.errors:
            sys.exit(-1)
