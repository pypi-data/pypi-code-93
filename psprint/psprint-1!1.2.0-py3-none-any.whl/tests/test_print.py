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
'''
test print
'''

import tempfile
import unittest
from pathlib import Path

from psprint import DEFAULT_PRINT, errors, init_print
from psprint.mark_types import InfoMark
from psprint.printer import PrintSpace


class TestPrintSpace(unittest.TestCase):
    """
    Test basic functions
    """
    @staticmethod
    def test_defaults_load():
        """
        print all default marks
        """
        print(DEFAULT_PRINT)

    @staticmethod
    def test_disabled():
        '''
        Disable fancy
        '''
        DEFAULT_PRINT.psprint('Disabled', disabled=True)

    @staticmethod
    def test_default_mark():
        '''
        Default print
        '''
        DEFAULT_PRINT.psprint("Info Mark", mark='info')

    @staticmethod
    def test_new_mark():
        """
        Test kwarg
        """
        configuration = '\n'.join([
            'FLAGS:',
            '  short: No',
            '  pad: Yes',
            '',
            'TEST:',
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
        with tempfile.NamedTemporaryFile('wt', delete=False) as config:
            config.write(configuration)
        my_print = init_print(Path(config.name))
        my_print.psprint("Test Text", mark='TEST')
        my_print.psprint("Info Test", mark='info')
        my_print.set_opts({}, '')
        config.close()
        my_print.remove_style(mark='TEST')
        PrintSpace({})

    def test_not_in(self):
        self.assertNotIn('badkey', DEFAULT_PRINT)

    def test_mark_in(self):
        self.assertIn(DEFAULT_PRINT.info_style['info'], DEFAULT_PRINT)
        self.assertIn('info', DEFAULT_PRINT)

    @staticmethod
    def test_on_the_fly():
        """
        Test definition on the fly
        """
        DEFAULT_PRINT.psprint("OTF text",
                              pref="OTF",
                              pref_s="o",
                              text_bgcol='lg',
                              pref_color='r',
                              short=True)

    @staticmethod
    def test_mod_mark():
        """
        Test a modified mark
        """
        DEFAULT_PRINT.psprint("MOD MARK test",
                              mark=2,
                              pref_color="lg",
                              pref=None,
                              pref_s=None)

    @staticmethod
    def test_edit():
        '''
        test edit style
        '''
        DEFAULT_PRINT.edit_style(pref="my_test", index_int=4)

    @staticmethod
    def test_int_pref():
        """
        int/float as prefix
        """
        DEFAULT_PRINT.psprint("bad prefix", pref=1234)

    @staticmethod
    def test_pop_style():
        '''
        test edit style
        '''
        DEFAULT_PRINT.remove_style(index_int=4)

    @staticmethod
    def test_allow_unknown_mark():
        '''
        allow an unknown mark (interpret as 0/cont)
        '''
        DEFAULT_PRINT.psprint("Test Unknown", mark=88)

    @staticmethod
    def test_precreated_mark():
        mark = InfoMark(pref='prepref')
        DEFAULT_PRINT.psprint("pass mark", mark=mark)

    @staticmethod
    def test_precreated_inherit():
        mark = InfoMark(parent=DEFAULT_PRINT.info_style['info'])
        DEFAULT_PRINT.psprint("pass mark", mark=mark)


class TextErrors(unittest.TestCase):
    def test_warns(self):
        """
        Check that warnings are thrown
        """
        self.assertWarns(errors.PSPrintWarning,
                         DEFAULT_PRINT.psprint,
                         "warn_text",
                         mark=5,
                         pref="SOME LONG TEXT",
                         pref_s="LONG SHORT")

    def test_bad_pref(self):
        """
        trigger a bad prefix
        """
        self.assertRaises((errors.BadPrefix, errors.BadShortPrefix),
                          DEFAULT_PRINT.psprint,
                          "bad prefix",
                          pref=["bad list prefix"])

    def test_bad_col(self):
        """
        trigger a bad color error
        """
        self.assertRaises(errors.BadColor,
                          DEFAULT_PRINT.psprint,
                          "bad color",
                          pref_color=77)
        self.assertRaises(errors.BadBGCol,
                          DEFAULT_PRINT.psprint,
                          "bad color",
                          pref_bgcol=77)
        self.assertRaises(errors.BadGloss,
                          DEFAULT_PRINT.psprint,
                          "bad gloss",
                          pref_gloss=77)

    def test_bad_rm_mark(self):
        '''
        test mark removal error
        '''
        self.assertRaises(SyntaxError, DEFAULT_PRINT.remove_style)

    def test_bad_mark(self):
        '''
        test bad mark creation
        '''
        self.assertRaises(errors.BadMark,
                          DEFAULT_PRINT.psprint,
                          "bad mark",
                          mark=[])

    def test_no_file(self):
        """
        custom-supplied file missing
        """
        self.assertRaises(FileNotFoundError, init_print, "bad_file_name")

    def test_nokey(self):
        """
        bad key not in PrintSpace
        """
        self.assertRaises(KeyError, DEFAULT_PRINT.__getitem__, list())


class TestIter(unittest.TestCase):
    @staticmethod
    def test_iter_list():
        DEFAULT_PRINT.psprint([1, [2, 20, 200], 3, 4], mark="info")

    @staticmethod
    def test_iter_gen():
        DEFAULT_PRINT.psprint(
            (k for k in (1, (t for t in (2, 20, 200)), 3, 4)), mark="info")

    @staticmethod
    def test_iter_dict():
        DEFAULT_PRINT.psprint(
            {
                "a": 1,
                "b": 2,
                3: {
                    "int": 3,
                    "bool": bin(3),
                    "hex": hex(3)
                }
            },
            mark="info")

    @staticmethod
    def test_iter_all():
        DEFAULT_PRINT.psprint((k for k in [[], {
            "a": 1,
            "b": [2, "b"],
            3: {
                "int": 3,
                "bool": bin(3),
                "hex": hex(3)
            }
        }, {1, 2, 3, 4}]),
                              mark="info")
