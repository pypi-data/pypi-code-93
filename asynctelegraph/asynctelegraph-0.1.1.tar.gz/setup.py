#!/usr/bin/env python

from setuptools import find_packages, setup

setup(name='asynctelegraph',
      version='0.1.1',
      description='Asynchronous telegraph API wrapper',
      author='Artem Burenin',
      author_email='burenotti@gmail.com',
      url='https://github.com/',
      packages=find_packages(exclude=("tests",)),
      install_requires=[
          "aiohttp",
          "yarl",
      ],
      license="MIT",
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
      ],
      )
