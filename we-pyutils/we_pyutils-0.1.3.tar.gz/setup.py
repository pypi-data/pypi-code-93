#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : setup.py
@Time    : 2020-01-26 17:23
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2020 WingEase Technology Co.,Ltd. All Rights Reserved.
"""

from setuptools import setup, find_packages  # 这个包没有的可以pip一下

setup(
    name="we_pyutils",
    version="0.1.3",
    keywords=("pip", "pyutils"),
    description="WingEase Python Utils",
    long_description="WingEase Python Utils",
    license="GPLv3",

    url="https://github.com/WingEase/we_pyutils",  # 项目相关文件地址，一般是github
    author="ZENKR",
    author_email="zenkr@qq.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[  # 这个项目需要的第三方库
        "requests",
        "requests-toolbelt",
        "django-environ",
        "oss2",
    ]
)
