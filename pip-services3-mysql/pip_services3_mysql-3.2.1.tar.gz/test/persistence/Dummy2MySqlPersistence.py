# -*- coding: utf-8 -*-
from typing import Optional

from pip_services3_commons.data import FilterParams, PagingParams, DataPage

from pip_services3_mysql.persistence.IdentifiableMySqlPersistence import IdentifiableMySqlPersistence
from test.fixtures.IDummy2Persistence import IDummy2Persistence


class Dummy2MySqlPersistence(IdentifiableMySqlPersistence, IDummy2Persistence):
    def __init__(self):
        super().__init__('dummies2')
        self._auto_generate_id = False

    def _define_schema(self):
        self._clear_schema()
        self._ensure_schema(
            'CREATE TABLE `' + self._table_name + '` (id INTEGER PRIMARY KEY, `key` VARCHAR(50), `content` TEXT)')
        self._ensure_index(self._table_name + '_key', {'key': 1}, {'unique': True})

    def get_page_by_filter(self, correlation_id: Optional[str], filter: FilterParams, paging: PagingParams, sort=None,
                           select=None) -> DataPage:
        filter = filter or FilterParams()
        key = filter.get_as_nullable_string('key')

        filter_condition = ''
        if key is not None:
            filter_condition += "`key`='" + key + "'"

        return super().get_page_by_filter(correlation_id, filter_condition, paging, None, None)

    def get_count_by_filter(self, correlation_id: Optional[str], filter) -> int:
        filter = filter or FilterParams()
        key = filter.get_as_nullable_string('key')

        filter_condition = ''
        if key is not None:
            filter_condition += "`key`='" + key + "'"

        return super().get_count_by_filter(correlation_id, filter_condition)
