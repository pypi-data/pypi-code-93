# -*- coding: utf-8 -*-
# pebble - Passman client
# Copyright (C) 2018,2019,2020,2021 Damien Goutte-Gattat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from incenp.pebble import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='incenp.pebble',
    version=__version__,
    description='Command-line Passman client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Damien Goutte-Gattat',
    author_email='dgouttegattat@incenp.org',
    url='https://git.incenp.org/damien/pebble',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
        ],

    install_requires=[
        'requests',
        'sjcl',
        'click',
        'click-shell'
        ],

    extras_require={
        'Keyring': ['keyring']
        },

    packages=[
        'incenp',
        'incenp.pebble'
        ],

    entry_points={
        'console_scripts': [
            'pbl = incenp.pebble.__main__:pebble'
            ]
        },

    command_options={
        'build_sphinx': {
            'project': ('setup.py', 'Pebble'),
            'version': ('setup.py', __version__),
            'release': ('setup.py', __version__)
            }
        }
    )
