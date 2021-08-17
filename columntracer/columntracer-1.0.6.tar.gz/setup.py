# -*- coding: utf-8 -*-

import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parents

README = (HERE[0]/"README.md").read_text()

setup(
      name='columntracer',
      version='1.0.6',
      description='first version',
 	  long_description=README,
 	  long_description_content_type="text/markdown",
      url = 'https://github.com/BYL4746/columntracer', 
      packages=['columntracer'],
      install_requires=['numpy', 'matplotlib', 'scipy'],
      include_package_data=True)