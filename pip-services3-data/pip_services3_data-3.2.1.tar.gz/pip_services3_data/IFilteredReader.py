# -*- coding: utf-8 -*-
"""
    pip_services3_data.IFilteredReader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for filtered data readers.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC
from typing import List, Optional, TypeVar

from pip_services3_commons.data import SortParams, FilterParams

T = TypeVar('T')  # Declare type variable


class IFilteredReader(ABC):
    """
    Interface for data processing components that can retrieve a list of data items by filter.
    """

    def get_list_by_filter(self, correlation_id: Optional[str], filter: Optional[FilterParams],
                           sort: Optional[SortParams] = None) -> List[T]:
        """
        Gets a list of data items using filter parameters.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param filter: (optional) filter parameters

        :param sort: (optional) sort parameters

        :param paging: (optional) paging parameters

        :return: list of items
        """
        raise NotImplementedError('Method from interface definition')
