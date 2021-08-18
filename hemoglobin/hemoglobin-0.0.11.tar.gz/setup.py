#!/usr/bin/env python

from distutils.core import setup

import hemoglobin

setup(
    name="hemoglobin",
    version=hemoglobin.__version__,
    description="A CLI wrapper for the grammarbot library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Matt Copperwaite",
    author_email="matt@copperwaite.net",
    url="https://github.com/yamatt/python3-hemoglobin",
    packages=["hemoglobin"],
    scripts=["scripts/hemoglobin"],
    install_requires=open("requirements.txt", encoding="utf-8").readlines(),
    license="gplv3",
    project_urls={
        "Source": "https://github.com/yamatt/python3-hemoglobin",
        "Tracker": "https://github.com/yamatt/python3-hemoglobin/issues",
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
        "Intended Audience :: Other Audience",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
