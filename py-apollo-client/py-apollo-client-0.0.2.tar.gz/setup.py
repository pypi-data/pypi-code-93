# -*- coding: utf-8 -*-
# Author: Ztj
# Email: ztj1993@gmail.com

import os.path

from setuptools import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf8')
readme = f.read()
f.close()

setup(
    name='py-apollo-client',
    version='0.0.2',
    description='python apollo client',
    long_description=readme,
    long_description_content_type='text/markdown',
    py_modules=['ApolloClient'],
    url='https://github.com/ztj1993/py-apollo-client',
    author='ZhangTianJie',
    author_email='ztj1993@gmail.com',
    keywords='apollo client',
    install_requires=[
        'requests',
    ],
    license='MIT License',
)
