# coding=UTF-8
import sys
import os
import re
import io
from .verify import verifyToken
from .runner import Runner, Result,EMTResult,PowerFlowResult
from .project import Project, ProjectRevision, ProjectTopology

from .utils import MatlabDataEncoder, DateTimeEncode
# from .function import * as function
__all__ = ['setToken', 'Project', 'ProjectRevision', 'ProjectTopology',
           'Runner', 'Result','PowerFlowResult','EMTResult','MatlabDataEncoder', 'DateTimeEncode']


def setToken(token):
    """
        设置 用户申请的 sdk token 

        :params: token token 
    """
    result = verifyToken(token)
    os.environ['CLOUDPSS_TOKEN'] = token
    os.environ['ENV_TYPE'] = result['type']
    os.environ['USER_NAME'] = result['username']
