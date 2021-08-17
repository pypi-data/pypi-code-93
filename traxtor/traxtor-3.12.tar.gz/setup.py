#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behazdi <dani.behzi@ubuntu.com>, 2020-2021

"""
tractor setup file
"""

import setuptools


with open("README.md", "r") as readme:
    long_description = readme.read()


setuptools.setup(
    name='traxtor',
    version='3.12',
    author='Danial Behzadi',
    author_email='dani.behzi@ubuntu.com',
    description='Setup an onion routing proxy',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/tractor-team/tractor",
    packages=setuptools.find_packages(),
    package_data={'tractor': [
        'SampleBridges',
        'tractor.gschema.xml',
        'man/tractor.1']},
    project_urls={
        "Bug Tracker":
        "https://gitlab.com/tractor-team/tractor/-/issues",
        "Documentation":
        "https://gitlab.com/tractor-team/tractor/-/blob/master/man/tractor.1",
        "Source Code":
        "https://gitlab.com/tractor-team/tractor",
    },
    install_requires=[
        'PyGObject',
        'fire',
        'psutil',
        'pysocks',
        'requests',
        'stem',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: "
        "GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "tractor = tractor.tractor:main",
        ],
    }
)
