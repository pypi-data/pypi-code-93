# -*- coding: utf-8 -*-
"""
    pip_services3_data.IQuerableReader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for querable data readers.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from typing import List, Optional, TypeVar

from pip_services3_commons.data import SortParams

T = TypeVar('T')  # Declare type variable


class IQuerableReader(ABC):
    """
    Interface for data processing components that can query a list of data items.
    """

    def get_list_by_query(self, correlation_id: Optional[str], query: Optional[str],
                          sort: Optional[SortParams] = None) -> List[T]:
        """
        Gets a list of data items using a query string.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param query: (optional) a query string

        :param sort: (optional) sort parameters

        :return: list of items
        """
        raise NotImplementedError('Method from interface definition')
