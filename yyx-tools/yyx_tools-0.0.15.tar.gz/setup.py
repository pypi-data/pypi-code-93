# -*- coding: utf-8 -*-
'''
@Time    : /
@Author  : Yanyuxiang
@Email   : yanyuxiangtoday@163.com
@FileName: /
@Software: PyCharm
'''

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yyx_tools",
    version="0.0.15",
    author="yanyuxiangtoday",
    author_email="yanyuxiangtoday@163.com",
    description="tools for algorithm engineer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yanyuxiangToday/yyx_tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)