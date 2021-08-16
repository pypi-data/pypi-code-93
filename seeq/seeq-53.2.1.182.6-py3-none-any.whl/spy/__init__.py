"""
Short for Seeq PYthon, the SPy library provides methods to interact with data that is exposed to the Seeq Server.
"""

from seeq.spy import assets
from seeq.spy import docs
from seeq.spy import workbooks
from seeq.spy import widgets
from seeq.spy import utils
from seeq.spy import jobs

from seeq.spy._login import login, logout
from seeq.spy._plot import plot
from seeq.spy._pull import pull
from seeq.spy._push import push
from seeq.spy._search import search
from seeq.spy._common import PATH_ROOT, DEFAULT_WORKBOOK_PATH, Status
from seeq.spy._config import options

client = None
user = None
server_version = None

__all__ = ['assets', 'docs', 'workbooks', 'widgets', 'login', 'logout', 'plot', 'pull', 'push', 'search',
           'PATH_ROOT', 'DEFAULT_WORKBOOK_PATH', 'Status', 'options', 'client', 'user', 'server_version', 'jobs',
           'utils']

__version__ = '%d.%d.%d.%d.%d' % (int('53'), int('2'), int('1'),
                                  int('182'), int('6'))
