"""
execute thread command
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import tags
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import TagConsts

@tags(TagConsts.THREAD_SECURITY)
def start_new_thread():
    """
    start new thread
    """
    pass