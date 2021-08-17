#  The MIT License (MIT)
#
#  Copyright (c) 2021. Scott Lau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import logging

from flask_restful import Resource

from sc_gz_dashboard.db.common_db_module import CommonDBModule
from sc_gz_dashboard.db.common_sql import *


class IndicatorHistoryItem(Resource):
    """
    单个指标历史记录操作
    """

    def __init__(self):
        self._db_module = CommonDBModule()

    def delete(self, id):
        """
        新增指标历史数据
        :return:
        """
        try:
            id = int(id)
        except ValueError:
            result_info = {'status': '00001', 'reason': u'id值非法', 'data': {}}
            return result_info
        except TypeError:
            result_info = {'status': '00001', 'reason': u'id值非法', 'data': {}}
            return result_info
        logging.getLogger(__name__).info("尝试删除指标历史记录：{0}".format(id))
        cursor, conn = self._db_module.execute(
            sql=DELETE_INDICATOR_HISTORY_RECORD,
            param=(id,),
        )
        rowcount = cursor.rowcount
        logging.getLogger(__name__).info('删除%s条记录', rowcount)
        if rowcount == 0:
            result_info = {'status': '00002', 'reason': u'记录不存在', 'data': {}}
            return result_info
        result_info = {'status': '00000', 'reason': '成功', 'data': {}}
        return result_info
