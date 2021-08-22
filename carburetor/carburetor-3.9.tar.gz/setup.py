#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behzadi <dani.behzi@ubuntu.com>, 2020-2021

"""
carburetor setup file
"""

import setuptools


with open("README.md", "r") as readme:
    long_description = readme.read()


setuptools.setup(
    name='carburetor',
    version='3.9',
    author='Danial Behzadi',
    author_email='dani.behzi@ubuntu.com',
    description='GTK frontend for Tractor',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://framagit.org/tractor/carburetor",
    packages=setuptools.find_packages(),
    include_package_data=True,
    project_urls={
        "Bug Tracker":
        "https://framagit.org/tractor/carburetor/-/issues",
        "Documentation":
        "https://framagit.org/tractor/carburetor/-/blob/master/man/tractor.1",
        "Source Code":
        "https://framagit.org/tractor/carburetor",
    },
    install_requires=[
        'traxtor',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: "
        "GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "gui_scripts": [
            "carburetor = carburetor.carburetor:main",
        ],
    }
)
