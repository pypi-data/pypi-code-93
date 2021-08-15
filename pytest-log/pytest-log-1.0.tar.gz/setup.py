# @File ：setup.py
# -*- ecoding: utf-8 -*-
# @Time: 2021/8/12 21:50
# @Author: niu run peng

from setuptools import setup

setup(
    name='pytest-log',
    url='https://gitee.com/niu-runpeng/PytestWork.git',
    version='1.0',
    author='Niu RunPeng',
    author_email='1733808462@qq.com',
    description='print log',
    long_description='for pytest print log',
    classifiers=[],
    license='proprietary',
    packages=['pytest_log'],
    install_requires=['pytest>=3.8'],
    entry_points={
        'pytest11': [
            'pytest_log = pytest_log',
        ]
    }
)
