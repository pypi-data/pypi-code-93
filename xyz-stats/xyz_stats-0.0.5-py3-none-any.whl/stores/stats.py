# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals, print_function

from xyz_util.mongoutils import Store


class Report(Store):
    name = 'stats_report'

    def daily(self, report_id, the_date, data):
        self.upsert(dict(id=report_id, the_date=the_date), data)
