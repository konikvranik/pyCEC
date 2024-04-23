#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

this_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(this_dir, "README.rst"), "r") as f:
    long_description = f.read()

PACKAGES = find_packages(exclude=["tests", "tests.*", "build"])

setup(
    name="pyCEC",
    version="0.6.0",
    author="Petr Vraník",
    author_email="hpa@suteren.net",
    description=(
        "Provide HDMI CEC devices as objects,"
        " especially for use with Home Assistant"
    ),
    license="MIT",
    keywords="cec hdmi home-assistant",
    url="https://github.com/konikvranik/pycec/",
    packages=PACKAGES,
    install_requires=[],
    long_description=long_description,
    test_suite="tests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Topic :: Home Automation",
        "Topic :: Multimedia",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        "console_scripts": [
            "pycec=pycec.__main__:main",
        ],
    },
)
