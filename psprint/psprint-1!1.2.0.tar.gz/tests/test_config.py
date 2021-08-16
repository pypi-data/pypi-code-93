#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020, 2021 Pradyumna Paranjape
# This file is part of psprint.
#
# psprint is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# psprint is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with psprint.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Test configurations
"""
import os
import tempfile
import unittest
from configparser import ConfigParser
from pathlib import Path

import toml
import yaml
from psprint import errors, init_print

CONFIG_YML = '\n'.join([
    'FLAGS:',
    '  short: No',
    '  pad: Yes',
    '',
    'test:',
    '  pref: TEST',
    '  pref_s: t',
    '  pref_color: y',
    '  pref_bgcol: blue',
    '  pref_gloss: 1',
    '  text_color: k',
    '  text_bgcol: 7',
    '  text_gloss: d',
    '',
])


class TestPrintSpace(unittest.TestCase):
    def test_yml(self):
        '''
        yml configuration marks
        '''
        with tempfile.NamedTemporaryFile('wt', delete=False) as config:
            config.write(CONFIG_YML)
        test_print = init_print(Path(config.name))
        self.assertIn('test', test_print)

    def test_toml(self):
        '''
        yml configuration marks
        '''
        with tempfile.NamedTemporaryFile('wt', delete=False) as config:
            config_toml = toml.dumps(yaml.safe_load(CONFIG_YML))
            print(config_toml)
            config.write(config_toml)
        test_print = init_print(Path(config.name))
        self.assertIn('test', test_print)

    def test_bad_mark(self):
        '''
        bad mark defined
        '''
        with tempfile.NamedTemporaryFile('wt', delete=False) as config:
            bad_yml = CONFIG_YML.replace('test:', 'test: []')
            config.write(bad_yml)
        self.assertRaises(errors.BadMark, init_print, Path(config.name))

    def tearDown(self):
        if 'PSPRINTIC' in os.environ:
            del os.environ['PSPRINTRC']

    def setUp(self):
        if 'PSPRINTIC' in os.environ:
            del os.environ['PSPRINTRC']

    def test_no_env_var(self):
        os.environ['PSPRINTRC'] = 'BAD FILE NAME'
        self.assertRaises(FileNotFoundError, init_print)
        del os.environ['PSPRINTRC']

    def test_psprintrc(self):
        os.environ['PSPRINTRC'] = '../.psprintrc'
        init_print()
