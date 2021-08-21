# -*- coding: utf-8 -*-

# @package zhiming
# @copyright Copyright (c) 2021, Ming-Fan Li.
# @license APL v2.0


from __future__ import with_statement

import sys
if sys.version_info < (3, 6):
    sys.exit('Python 3.6 or greater is required.')

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
import setuptools

import zhiming


with open('README.md') as fp:
    readme = fp.read()

with open('LICENSE') as fp:
    license = fp.read()

setup(name = 'zhiming',
      version = zhiming.__version__,
      description = 'A package for information and data analysis.',
      url='https://github.com/Li-Ming-Fan/zhiming',
      #
      long_description = readme,
      long_description_content_type="text/markdown",
      author = 'Ming-Fan Li',
      author_email = 'li_m_f@163.com',
      maintainer='Ming-Fan Li',
      maintainer_email='li_m_f@163.com',      
      packages=setuptools.find_packages(),
      #license=license,
      platforms=['any'],
      classifiers=[]
      )
