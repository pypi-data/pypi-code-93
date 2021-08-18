#coding: utf-8

import sys

VERSION = "1.5.6rc0"

if not ((sys.version_info[0] == 2 and sys.version_info[1] == 7)\
        or (sys.version_info[0] == 3 and sys.version_info[1] == 6)):
    STATEMENT = "The Python requirement is Python2.7 or Python 3.6"
    raise Exception(STATEMENT)

