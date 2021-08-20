#!/usr/bin/env python3
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: JeffreyCao
# Mail: jeffreycao1024@gmail.com
# Created Time:  2021-08-19 23:58:34
# https://packaging.python.org/guides/distributing-packages-using-setuptools/#package-data
#############################################

import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gslocalizator",
    version="0.0.3",
    keywords=["google sheet", "localization", "l10n", "i18n"],
    description="update localization texts from google doc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT Licence",

    url="https://github.com/ovotop/gslocalizator",
    author="JeffreyCao",
    author_email="jeffreycao1024@gmail.com",

    packages=setuptools.find_packages(
        exclude=[
            'bin',
            'docs',
            'tests',
            'playground',
            'quick_start.py',
            'example.py',
            'cfg.py',
        ]),
    include_package_data=False,
    platforms="any",
    install_requires=[
        "ezutils",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
