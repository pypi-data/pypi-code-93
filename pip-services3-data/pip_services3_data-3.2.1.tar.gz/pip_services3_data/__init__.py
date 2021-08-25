# -*- coding: utf-8 -*-
"""
    pip_services3_data.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Contains interfaces for various design patterns that work with data.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [
    'IPartialUpdater', 'IFilteredPageReader', 'IFilteredReader',
    'IGetter', 'ILoader', 'IQuerablePageReader', 'IQuerableReader',
    'ISaver', 'ISetter', 'IWriter'
]

from .IPartialUpdater import IPartialUpdater
from .IFilteredPageReader import IFilteredPageReader
from .IFilteredReader import IFilteredReader
from .IGetter import IGetter
from .ILoader import ILoader
from .IQuerablePageReader import IQuerablePageReader
from .IQuerableReader import IQuerableReader
from .ISaver import ISaver
from .ISetter import ISetter
from .IWriter import IWriter

