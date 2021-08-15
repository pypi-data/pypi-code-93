import sys
from os import path
from setuptools import setup, find_packages

curdir = path.abspath(path.dirname(__file__))
with open(path.join(curdir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

name = 'bapiparkinglot'
version = '1.0'
description = 'Parking Lot API dibuat untuk memenuhi syarat dalam pengerjaan soal DTO Kemenkes - Backend Engineer.'
url = 'https://github.com/bearaujus/api_parking_lot'
author = 'Bear Au Jus - ジュースとくま'
author_email = 'haryobagasasyafah6@gmail.com'

list_classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7',
    'Natural Language :: English',
    'Topic :: Utilities',
]

list_install_requirements = [
    'flask',
    'flask_restful',
    'requests',
]

list_keywords = [
    'bapiparkinglot',
    'DTO',
    'Kemenkes',
    'DTO Kemenkes',
    'Backend Engineer',
]

setup (
    name = name,
    version = version,
    description = description,
    long_description = long_description,
    long_description_content_type='text/markdown',
    url = url,
    author = author,
    author_email = author_email,
    license = 'MIT',
    classifiers = list_classifiers,
    keywords = list_keywords,
    packages = find_packages(),
    install_requires = list_install_requirements
)

