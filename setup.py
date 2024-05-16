#!/usr/bin/env python3

from setuptools import setup


setup(
    name="emay2medview",
    version="0.0.0",
    py_modules=[
        "emay2medview",
        "EmayFileReader",
        "O2InsightProReader",
        "MedViewFileWriter",
        "FuzzyDateTimeParser",
    ],
    install_requires=[
        "Click",
        "click-option-group",
    ],
    entry_points={
        "console_scripts": [
            "emay2medview=emay2medview:main",
            "o2insight2medview=emay2medview:o2insight2medview",
        ]
    },
)
