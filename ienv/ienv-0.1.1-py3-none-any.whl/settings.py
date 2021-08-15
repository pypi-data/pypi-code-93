# !/usr/bin/env python3
# coding: utf-8
import os
import sys
from pathlib import Path

NAME = 'ienv'
VERSION = '0.1.1'
DESCRIPTION = 'Create virtual environment of project.'
AUTHOR = 'JiangHui'
URL = 'https://github.com/536/ienv'
PACKAGES = ['ienv']

ENTRY_POINTS = {
    'console_scripts': [
        'ienv = ienv.__main__:main'
    ]
}

DEFAULT = Path('~').expanduser() / '.ienv'
IENV = os.getenv('IENV', DEFAULT)

if sys.platform == 'win32':
    binname = 'Scripts'
else:
    binname = 'bin'
