'''
Soil package.
'''
# pylint:disable=consider-using-from-import
from soil.modulify import modulify
from soil.data import data
from soil.alias import alias
from soil import finder
from soil.logger import logger
import soil.connectors as connectors
from soil.decorator import decorator
from soil.task import task, task_wait
from soil.alerts import alerts

finder.install()

__all__ = [
    'modulify',
    'data_structures',
    'modules',
    'data',
    'alias',
    'logger',
    'connectors',
    'decorator',
    'task',
    'task_wait',
    'alerts'
]
