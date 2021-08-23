# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='excel_tools',
    version='1.0.01',
    author='hakaboom',
    author_email='1534225986@qq.com',
    license='Apache License 2.0',
    description='This is a tool for excel',
    url='https://github.com/hakaboom/excel_tools',
    packages=['excel_tools'],
    install_requires=["openpyxl==3.0.7", "xlrd==2.0.1"],
)