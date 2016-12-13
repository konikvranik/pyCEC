#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

PACKAGES = find_packages(exclude=['tests', 'tests.*'])

REQUIRES = [
    'cec',
]

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyCEC",
    version = "0.0.1",
    author = "Petr Vraník",
    author_email = "hpa@suteren.net",
    description = ("Provide HDMI CEC devices as objects, especially for use with Home Assistant"),
    license = "BSD",
    keywords = "cec hdmi come-assistant",
    url = "https://github.com/konikvranik/pycec/",
    packages=['pycec', 'tests'],
    long_description=read('README.md'),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
    test_loader='pytest',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)