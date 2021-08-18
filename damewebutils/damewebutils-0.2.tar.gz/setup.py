#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2019  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with damewebutils; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

import os
import re
from setuptools import setup
from os import path


def readme():
    with open('README.org') as f:
        return f.read()


cwd = os.getcwd()


def files_one_level(directory):
    f = os.popen('find ' + directory)
    l1 = []
    for line in f:
        fields = line.strip().split()
        l1.append(fields[0])
    return l1


def files_one_level_drop_pwd(directory):
    f = os.popen('find ' + directory)
    l2 = []
    for line in f:
        fields = line.strip().split()
        if not(os.path.isdir(fields[0])) and ("__init__.py" not in fields[0]):
            l2.append(drop_pwd(fields[0]))
    return l2


def drop_pwd(s):
    cwd = os.getcwd()
    result = ""
    if re.search(cwd, s):
        result = re.sub(cwd + '/', '', s)
    return result


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='damewebutils',
      version='0.2',
      description='Web utils for Python',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.6',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='web, links',
      scripts=['dameimgs.py', 'damerss.py', 'dameurls.py'],
      url='http://github.com/davidam/damewebutils',
      author='David Arroyo Menéndez',
      author_email='davidam@gmail.com',
      license='GPLv3',
      packages=['damewebutils',
                'damewebutils.tests',
                'damewebutils.files',
                'damewebutils.app'],
      package_dir={'damewebutils': 'damewebutils',
                   'damewebutils.files': 'damewebutils/files',
                   'damewebutils.tests': 'damewebutils/tests',
                   'damewebutils.app': 'damewebutils/app'},
      package_data={'damewebutils.app': ['*'],
                    'damewebutils.tests': ['*'],
                    'damewebutils.files': ['*']},
      data_files=[('damewebutils',
                   ['README.org',
                    'testsbycommands.sh',
                    'dameimgs.py',
                    'damerss.py',
                    'dameurls.py']
                   + files_one_level_drop_pwd(cwd + "/damewebutils/tests/")
                   + files_one_level_drop_pwd(cwd + "/damewebutils/files/")
                   + files_one_level_drop_pwd(cwd + "/damewebutils/files/tests"))],

      install_requires=[
          'SPARQLWrapper',
          'rdflib',
          'markdown',
          'requests',
          'cssselect',
          'lxml',
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      # entry_points={
      #     'console_scripts': ['damewebutils=damewebutils'],
      # },
      include_package_data=True,
      zip_safe=False)
