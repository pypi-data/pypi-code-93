"""
dom.sax unsafe functions
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import TagConsts
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import tags
from . import xmlreader


@tags(TagConsts.FILE_READ_AND_WRITE)
def parse():
    """
    Parse file or fileobject
    """
    pass