#!/usr/bin/env python

import sys
import setuptools
from distutils.core import setup

dependencies = ['dendropy==4.4.0', 'scipy', 'numpy']

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(name = "fishlifetraits",
      version = '0.4.4',
      maintainer = 'Ulises Rosas',
      maintainer_email = 'ulisesfrosasp@gmail.com',
      long_description = readme,
      long_description_content_type = 'text/markdown',
      packages = ['fishlifetraits'],
      install_requires = dependencies,
      zip_safe = False,
      classifiers = [
          'Programming Language :: Python :: 3'
      ]
)
