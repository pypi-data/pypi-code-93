#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: xl

@file: setup.py 
@time: 2021/05/06
@contact: 
@site:  
@software: PyCharm 
"""
from setuptools import setup, find_packages

python_requires = '>=3.7'
# or
# from distutils.core import setup
install_requires = []
print(find_packages(where='.', exclude=('tests', 'tests.*', 'test', 'test/*', 'backend'),
                    include=("rosetta_service_monitor", "rosetta_service_monitor.client")))

with open('requirements.txt', 'r') as f:
    for line in f.readlines():
        line = line.strip()
        if line and not line.startswith("#"): install_requires.append(line)

setup(
    name='rosetta_service_monitor',  # 包名字
    version='0.1.4',  # 包版本
    description='service monitor data collect client',  # 简单描述
    author='xialei',  # 作者
    author_email='xialei@joyy.sg',  # 作者邮箱
    url='',  # 包的主页
    packages=find_packages(where='.', exclude=('tests', 'tests.*', 'test', 'test/*', 'backend'),
                           include=("rosetta_service_monitor", "rosetta_service_monitor.client",
                                    "rosetta_service_monitor.client.*",
                                    "rosetta_service_monitor.tasks",
                                    "rosetta_service_monitor.tasks.*"
                                    )),
    # 包
    # scripts=['entrypoint.sh'],
    # entry_points={"console_scripts": ["crawler-cli=backend.manager:cli"]},
    python_requires=python_requires,
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
