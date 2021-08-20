# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

from setuptools import setup

setup(
    name = "map-address",
    packages = ["map_address"],
    entry_points = {
        "console_scripts": ['map_address = map_address.map_it:main']
        },
    version = "0.1.0",
    description = "An application to open a map address in a web browser from commandline or clipboard",
    long_description = "",
    author = "Cyril Mukabwa",
    author_email = "mukabwacyril@gmail.com",
    url = "https://github.com/muckswon-1/muckswon-1"
    )
