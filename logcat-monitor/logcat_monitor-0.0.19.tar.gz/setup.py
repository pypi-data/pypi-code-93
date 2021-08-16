#!/usr/bin/env python
# -*- coding: utf-8 -*-
# --------------------------------------------------------------
# ProjectName: logcat_monitor
# Author: gentliu
# CreateTime: 2/8/2021 2:35 PM
# File Name: setup.py
# Description:
# --------------------------------------------------------------
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logcat_monitor",
    version="0.0.19",
    author="Gent Liu",
    author_email="94026236@qq.com",
    description="A tool of logcat monitor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/gentliu/logcat_monitor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)