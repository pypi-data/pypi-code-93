#!/usr/bin/env python3
# coding: utf-8

import sys

from joker.textmanip.main import registry

registry(['python -m joker.textmanip'] + sys.argv[1:])
