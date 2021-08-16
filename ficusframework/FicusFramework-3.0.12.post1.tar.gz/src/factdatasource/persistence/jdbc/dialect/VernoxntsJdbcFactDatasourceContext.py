#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: tangjy
# Created on 2021/02/02
from factdatasource.execptions import NotSupportedFDException
from factdatasource.persistence.jdbc import SqlWrap
from factdatasource.persistence.jdbc.dialect.MysqlJdbcFactDatasourceContext import MysqlJdbcFactDatasourceContext


class VernoxntsJdbcFactDatasourceContext(MysqlJdbcFactDatasourceContext):

    def _delete_all_sql(self):
        raise NotSupportedFDException('VernoxNTS不支持该操作')

    def _delete_sql(self, query: str):
        raise NotSupportedFDException('VernoxNTS不支持该操作')

    def _generate_update_sql(self, table, result: dict) -> SqlWrap:
        raise NotSupportedFDException('VernoxNTS不支持该操作')