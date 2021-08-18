# -*- coding: utf-8 -*-
# Author: Ztj
# Email: ztj1993@gmail.com

import os.path

from setuptools import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf8')
readme = f.read()
f.close()

setup(
    name='py-apollo-config',
    version='0.0.1',
    description='python apollo config',
    long_description=readme,
    long_description_content_type='text/markdown',
    py_modules=['ApolloConfig'],
    url='https://github.com/ztj1993/py-apollo-config',
    author='ZhangTianJie',
    author_email='ztj1993@gmail.com',
    keywords='apollo config',
    install_requires=[
        'config-registry',
        'py-apollo-client',
    ],
    license='MIT License',
)
