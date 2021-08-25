# -*- coding: utf-8 -*-
from abc import ABC
from typing import List, Union, Optional

from pip_services3_commons.data import FilterParams, PagingParams, AnyValueMap, DataPage
from pip_services3_data import IGetter, IWriter, IPartialUpdater

from test.fixtures.Dummy import Dummy


class IDummyPersistence(IGetter, IWriter, IPartialUpdater, ABC):

    def get_page_by_filter(self, correlation_id: Optional[str], filter: FilterParams,
                           paging: Union[PagingParams, None]) -> DataPage:
        raise NotImplemented()

    def get_count_by_filter(self, correlation_id: Optional[str], filter: FilterParams) -> int:
        raise NotImplemented()

    def get_list_by_ids(self, correlation_id: Optional[str], ids: List[str]) -> List[Dummy]:
        raise NotImplemented()

    def get_one_by_id(self, correlation_id: Optional[str], id: str) -> Dummy:
        raise NotImplemented()

    def create(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        raise NotImplemented()

    def update(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        raise NotImplemented()

    def set(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        raise NotImplemented()

    def update_partially(self, correlation_id: Optional[str], id: str, data: AnyValueMap) -> Dummy:
        raise NotImplemented()

    def delete_by_id(self, correlation_id: Optional[str], id: str) -> Dummy:
        raise NotImplemented()

    def delete_by_ids(self, correlation_id: Optional[str], ids: List[str]):
        raise NotImplemented()
