"""
Use setup.cfg to configure packaging
"""
from setuptools import setup

setup(use_scm_version=True)

#
# #!/usr/bin/env python
# # Licensed under a 3-clause BSD style license - see LICENSE.rst
#
# import glob
# import os
# import sys
#
# from setuptools import setup, find_packages
#
# # Get some values from the setup.cfg
# try:
#     from ConfigParser import ConfigParser
# except ImportError:
#     from configparser import ConfigParser
#
# conf = ConfigParser()
# conf.read(['setup.cfg'])
# metadata = dict(conf.items('metadata'))
#
# PACKAGENAME = metadata.get('package_name', 'dkist-processing-pac')
# DESCRIPTION = metadata.get('description', 'PA&C Pipeline')
# AUTHOR = metadata.get('author', 'Arthur Eigenbrot')
# AUTHOR_EMAIL = metadata.get('author_email', '')
# LICENSE = metadata.get('license', 'unknown')
# URL = metadata.get('url', 'http://dkist.nso.edu')
#
# # order of priority for long_description:
# #   (1) set in setup.cfg,
# #   (2) load LONG_DESCRIPTION.rst,
# #   (3) load README.rst,
# #   (4) package docstring
# readme_glob = 'README*'
# _cfg_long_description = metadata.get('long_description', '')
# if _cfg_long_description:
#     LONG_DESCRIPTION = _cfg_long_description
#
# elif os.path.exists('LONG_DESCRIPTION.rst'):
#     with open('LONG_DESCRIPTION.rst') as f:
#         LONG_DESCRIPTION = f.read()
#
# elif len(glob.glob(readme_glob)) > 0:
#     with open(glob.glob(readme_glob)[0]) as f:
#         LONG_DESCRIPTION = f.read()
#
# else:
#     # Get the long description from the package's docstring
#     __import__(PACKAGENAME)
#     package = sys.modules[PACKAGENAME]
#     LONG_DESCRIPTION = package.__doc__
#
# version_file = "dkist_processing_pac/_version.py"
# with open(version_file, 'r') as f:
#     lines = f.readlines()
#     VERSION = lines[0].split(' = ')[-1].replace('"', '')
#
# # Treat everything in scripts except README* as a script to be installed
# scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
#            if not os.path.basename(fname).startswith('README')]
#
#
# # Get configuration information from all of the various subpackages.
# package_info = {'packages': find_packages(),
#                 'package_data': {}}
#
# # Add the project-global data
# package_info['package_data'].setdefault(PACKAGENAME, [])
# package_info['package_data'][PACKAGENAME].append('data/*')
#
# # Define entry points for command-line scripts
# entry_points = {'console_scripts': []}
#
# entry_point_list = conf.items('entry_points')
# for entry_point in entry_point_list:
#     entry_points['console_scripts'].append('{0} = {1}'.format(entry_point[0],
#                                                               entry_point[1]))
# setup(name=PACKAGENAME,
#       version=VERSION,
#       description=DESCRIPTION,
#       scripts=scripts,
#       install_requires=metadata.get('install_requires', 'astropy').strip().split(),
#       author=AUTHOR,
#       author_email=AUTHOR_EMAIL,
#       license=LICENSE,
#       url=URL,
#       long_description=LONG_DESCRIPTION,
#       zip_safe=False,
#       use_2to3=False,
#       entry_points=entry_points,
#       include_package_data=True,
#       **package_info
# )
