#  Trifacta Inc. Confidential
#
#  Copyright 2020 Trifacta Inc.
#  All Rights Reserved.
#
#  Any use of this material is subject to the Trifacta Inc., Source License located
#  in the file 'SOURCE_LICENSE.txt' which is part of this package.  All rights to
#  this material and any derivative works thereof are reserved by Trifacta Inc.


import unittest

from trifacta.util.tf_alias_naming_util import AliasNamingUtil


class AliasNamingUtilTestCase(unittest.TestCase):
    def test_conflict_resolution(self):
        alias_util = AliasNamingUtil()
        self.assertEqual(alias_util.get_valid_alias_name('alias'), 'alias')
        self.assertEqual(alias_util.get_valid_alias_name('alias'), 'alias_1')
        self.assertEqual(alias_util.get_valid_alias_name('alias'), 'alias_2')

    def test_no_alias(self):
        alias_util = AliasNamingUtil()
        self.assertEqual(alias_util.get_valid_alias_name(''), 'dataframe')
        self.assertEqual(alias_util.get_valid_alias_name(), 'dataframe_1')

    def test_valid_python_var_name(self):
        alias_util = AliasNamingUtil()
        self.assertEqual(alias_util.get_valid_alias_name('al-ias'), 'alias')
        self.assertEqual(alias_util.get_valid_alias_name('-al  -ias'), 'alias_1')
        self.assertEqual(alias_util.get_valid_alias_name('_al  -ia-s'), '_alias')

    def test_alias_sync_after_deletion(self):
        alias_util = AliasNamingUtil()
        self.assertEqual(alias_util.get_valid_alias_name('alias'), 'alias')
        self.assertEqual(alias_util.get_valid_alias_name('alias'), 'alias_1')
        alias_util.init_alias_names('alias', 'alias_1')
        self.assertEqual(alias_util.get_valid_alias_name('alias'), 'alias_2')


if __name__ == '__main__':
    unittest.main()
