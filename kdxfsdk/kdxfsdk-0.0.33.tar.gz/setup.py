#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
#  File Name: setup.py
#  Author: xialingming
#  Mail: xialingming@gmail.com
#  #############################################


from setuptools import setup, find_packages

setup(
    name="kdxfsdk",
    version="0.0.33",
    keywords=("kdxf", "sdk", "xialingming"),
    description="kdxf sdk",
    long_description="xf sdk for python",
    license="MIT Licence",

    url="http://xialingming",
    author="lmxia",
    author_email="xialingming@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["pyaudio", "pyyaml>=4.2b1", "requests==2.21.0", "websocket-client==0.56.0",
                      "python-dateutil==2.7.5", "jieba", "pypinyin", "websocket==0.2.1", "semver==2.8.1",
                      "markdown==3.0.1", "tornado==5.1.1", "fire==0.1.3", "pytz==2018.9", "watchdog==0.9.0",
                      "pydub==0.23.1", "baidu-aip==2.0.0.1"]
)