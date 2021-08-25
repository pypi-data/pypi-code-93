#!/usr/bin/env python3

from setuptools import setup
from os import path
from evs import __version__

with open(path.join(path.dirname(__file__), 'evs/README.md'), 'r') as fh:
  long_description = fh.read()

setup(
  name='castlabs-evs',
  version=__version__,
  author='Emil Pettersson',
  author_email='emil.pettersson@castlabs.com',
  description='A client for EVS, Widevine/VMP signing service',
  long_description=long_description,
  long_description_content_type='text/markdown',
  keywords='castlabs evs 3pl widevine vmp drm electron wvvmp ecs',
  url='https://github.com/castlabs/electron-releases/wiki/EVS',
  packages=[
    'castlabs_evs',
    'castlabs_evs.core',
    'castlabs_evs.cli'
  ],
  package_dir={
    'castlabs_evs': 'evs',
  },
  entry_points={
    'console_scripts': [
      'evs-account = castlabs_evs.cli.account:main',
      'evs-vmp = castlabs_evs.cli.vmp:main',
    ]
  },
  install_requires=[
    'boto3',
    'cryptography',
    'macholib',
    'requests',
  ],
  python_requires='>=3.7',
  license='APACHE 2.0',
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    "Programming Language :: Python :: 3 :: Only",
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Software Development :: Build Tools',
    'Topic :: Utilities',
  ],
)
