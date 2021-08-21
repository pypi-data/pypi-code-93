# -*- coding: utf-8 -*-
# Intro: mysql 实例模块安装文件
# Author: Ztj
# Email: ztj1993@gmail.com

import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
readme = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='py-ztj-mysql',
    version='2.0.0',
    description='python mysql instance package',
    long_description=readme,
    long_description_content_type='text/markdown',
    py_modules=['ZtjMySQL'],
    url='https://github.com/ztj1993/py-mysql',
    author='ZhangTianJie',
    author_email='ztj1993@gmail.com',
    keywords='mysql',
    install_requires=[
        'pymysql',
        'DBUtils',
    ],
    license='MIT License',
)
