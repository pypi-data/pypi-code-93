#  Trifacta Inc. Confidential
#
#  Copyright 2020 Trifacta Inc.
#  All Rights Reserved.
#
#  Any use of this material is subject to the Trifacta Inc., Source License located
#  in the file 'SOURCE_LICENSE.txt' which is part of this package.  All rights to
#  this material and any derivative works thereof are reserved by Trifacta Inc.

import re
from collections import defaultdict


class AliasNamingUtil(object):
    """
    Utility class for manipulating dataframe alias
    """
    DEFAULT_ALIAS_PREFIX = "dataframe"

    def __init__(self, verbose=True):
        self.alias_count = defaultdict(int)

    def get_valid_alias_name(self, alias_name=None):
        """
        Public method used to generate valid alias name
        @param alias_name: alias name
        @type alias_name: str
        @return: generated valid alias name
        """
        # Handling None and empty string
        if alias_name is None or alias_name == '':
            alias_name = self.DEFAULT_ALIAS_PREFIX
        self.validate_alias_name(alias_name)
        new_alias_name = alias_name
        while new_alias_name in self.alias_count:
            new_alias_name = f'{alias_name}_{self.alias_count[alias_name]}'
            self.alias_count[alias_name] += 1
        self.alias_count[new_alias_name] += 1
        return new_alias_name

    @staticmethod
    def validate_alias_name(alias_name):
        # Remove invalid characters
        valid_alias = alias_name
        valid_alias = re.sub('[^0-9a-zA-Z_]', '', valid_alias)

        # Remove leading characters until we find a letter or underscore
        valid_alias = re.sub('^[^a-zA-Z_]+', '', valid_alias)
        if valid_alias != alias_name:
            raise Exception('Invalid alias name')
        return valid_alias

    def init_alias_names(self, *alias_names):
        """Public method to initialise the col_name_count map
        @param alias_names: list of alias names"""
        self.alias_count = defaultdict(int)
        for alias in alias_names:
            self.alias_count[alias] += 1
