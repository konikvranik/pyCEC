#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

PACKAGES = find_packages(exclude=['tests', 'tests.*', 'build'])

REQUIRES = [
    #'cec',
]


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pyCEC",
    version="0.2.1",
    author="Petr Vraník",
    author_email="hpa@suteren.net",
    description=(
        "Provide HDMI CEC devices as objects, especially for use with Home Assistant"),
    license="MIT",
    keywords="cec hdmi home-assistant",
    url="https://github.com/konikvranik/pycec/",
    packages=PACKAGES,
    install_requires=REQUIRES,
    long_description=read('README.md'),
    test_suite='tests',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Topic :: Home Automation",
        "Topic :: Multimedia",
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3.4',
    ],
)
