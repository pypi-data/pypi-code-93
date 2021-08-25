# -*- coding: utf-8 -*-
from pip_services3_commons.data import FilterParams

from pip_services3_mysql.persistence.IdentifiableJsonMySqlPersistence import IdentifiableJsonMySqlPersistence
from test.fixtures.IDummyPersistence import IDummyPersistence


class DummyJsonMySqlPersistence(IdentifiableJsonMySqlPersistence, IDummyPersistence):

    def __init__(self):
        super(DummyJsonMySqlPersistence, self).__init__('dummies_json')

    def _define_schema(self):
        self._clear_schema()
        self._ensure_table()
        self._ensure_schema(
            'ALTER TABLE `' + self._table_name + '` ADD `data_key` VARCHAR(50) AS (JSON_UNQUOTE(`data`->"$.key"))')
        self._ensure_index(self._table_name + '_json_key', {"data_key": 1}, {'unique': True})

    def get_page_by_filter(self, correlation_id, filter, paging):
        filter = filter or FilterParams()
        key = filter.get_as_nullable_string('key')

        filter_condition = ''
        if key is not None:
            filter_condition += "data->key='" + key + "'"

        return super().get_page_by_filter(correlation_id, filter_condition, paging, None, None)

    def get_count_by_filter(self, correlation_id, filter):
        filter = filter or FilterParams()
        key = filter.get_as_nullable_string('key')

        filter_condition = ''
        if key is not None:
            filter_condition += "data->key='" + key + "'"

        return super().get_count_by_filter(correlation_id, filter_condition)
