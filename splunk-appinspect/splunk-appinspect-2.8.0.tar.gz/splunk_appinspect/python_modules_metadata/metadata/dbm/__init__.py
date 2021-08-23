'''The dbm module provides an interface to the Unix "(n)dbm" library.'''

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import tags
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import TagConsts

from . import dumb
from . import ndbm
from . import gnu

@tags(TagConsts.DATA_PERSISTENCE)
def open():
    '''
    Open a dbm database and return a dbm object.
    '''
    pass
