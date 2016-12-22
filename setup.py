#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

PACKAGES = find_packages(exclude=['tests', 'tests.*', 'build'])

REQUIRES = [
    # 'cec',
]

setup(
    name="pyCEC",
    version="0.3.5",
    author="Petr Vraník",
    author_email="hpa@suteren.net",
    description=(
        "Provide HDMI CEC devices as objects," +
        " especially for use with Home Assistant"),
    license="MIT",
    keywords="cec hdmi home-assistant",
    url="https://github.com/konikvranik/pycec/",
    packages=PACKAGES,
    install_requires=REQUIRES,
    long_description='README.rst',
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
