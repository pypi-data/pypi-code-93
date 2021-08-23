'''
create http connection
'''

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import tags
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import TagConsts

@tags(TagConsts.HTTP_CONNECTION)
class HTTPConnection:
    '''
    create http connection
    '''
    pass