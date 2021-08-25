# -*- coding: utf-8 -*-
from pip_services3_commons.data import FilterParams

from pip_services3_postgres.persistence.IdentifiablePostgresPersistence import IdentifiablePostgresPersistence
from test.fixtures.IDummyPersistence import IDummyPersistence


class DummyPostgresPersistence(IdentifiablePostgresPersistence, IDummyPersistence):

    def __init__(self):
        super(DummyPostgresPersistence, self).__init__('dummies')

    def _define_schema(self):
        self._clear_schema()
        self._ensure_schema('CREATE TABLE ' + self._table_name + ' (id TEXT PRIMARY KEY, key TEXT, content TEXT)')
        self._ensure_index(self._table_name + '_key', {'key': 1}, {'unique': True})

    def get_page_by_filter(self, correlation_id, filter, paging):
        filter = filter or FilterParams()
        key = filter.get_as_nullable_string('key')

        filter_condition = ''
        if key is not None:
            filter_condition += "key='" + key + "'"

        return super().get_page_by_filter(correlation_id, filter_condition, paging, None, None)

    def get_coumt_by_filter(self, correlation_id, filter):
        filter = filter or FilterParams()
        key = filter.get_as_nullable_string('key')

        filter_condition = ''
        if key is not None:
            filter_condition += "key='" + key + "'"

        return super().get_count_by_filter(correlation_id, filter_condition)
