# -*- coding: utf-8 -*-
# Author: Ztj
# Email: ztj1993@gmail.com

import pathlib

from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
readme = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='py-ztj-redis',
    version='1.0.0',
    description='python redis instance package',
    long_description=readme,
    long_description_content_type='text/markdown',
    py_modules=['ZtjRedis'],
    url='https://github.com/ztj-package/py-redis',
    author='ZhangTianJie',
    author_email='ztj1993@gmail.com',
    keywords='redis',
    install_requires=[
        'redis',
    ],
    license='MIT License',
)
