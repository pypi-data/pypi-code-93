#!/usr/bin/env python

import sys
import platform
import setuptools
from distutils.core import setup

if platform.architecture()[0] != '64bit':
    sys.stderr.write('Architecture requires 64bit')
    sys.stderr.flush()
    exit()

myos = sys.platform

if myos == 'darwin':
    bins = [
        './ext_bin/raxml/raxmlHPC-SSE3_Darwin_64bit',
        './ext_bin/consel/darwin/seqmt',
        './ext_bin/consel/darwin/makermt',
        './ext_bin/consel/darwin/consel',
        './ext_bin/consel/darwin/catpv'
            ]

elif myos == 'linux' or myos == "linux2":
    bins = [
        './ext_bin/raxml/raxmlHPC-SSE3_Linux_64bit',
        './ext_bin/consel/linux/seqmt',
        './ext_bin/consel/linux/makermt',
        './ext_bin/consel/linux/consel',
        './ext_bin/consel/linux/catpv'
            ]
else:
    sys.stderr.write('Package does not work with %s operative system'  % myos)
    sys.stderr.flush()
    exit()


dependencies = ['dendropy==4.4.0']

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(name = "ggi",
      version = '1.0.1',
      maintainer = 'Ulises Rosas',
    #   long_description = readme,
    #   long_description_content_type = 'text/markdown',
      url ='https://github.com/Ulises-Rosas/GGpy',
      packages = ['ggpy'],
      package_data = {'ggpy': ['data/*']} ,
      data_files = [ ('bin', bins) ],
      include_package_data=True,
      install_requires = dependencies,
      zip_safe = False,
      entry_points = {
        'console_scripts': [
            'ggpy   = ggpy.cli:main'
            ]
      },
      scripts=[
          './scripts/root_groups.py',
      ],
      classifiers = [
          'Programming Language :: Python :: 3'
      ]
    )
