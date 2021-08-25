from setuptools import setup

setup(
    name='henry_utils_test',
    version='1.0.2',
    author='Henry Liu',
    author_email='2224546920@qq.com',
    maintainer='Henry Liu',
    description='to automatic create spark sql file ',
    packages=['henry_utils', 'henry_utils.sqlserver'],
    requires=['pymssql'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities'
    ]
)
