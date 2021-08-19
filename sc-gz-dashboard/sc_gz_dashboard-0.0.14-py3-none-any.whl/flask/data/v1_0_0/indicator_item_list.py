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

import pandas as pd
from flask_restful import Resource

from sc_gz_dashboard.db.common_db_module import CommonDBModule
from sc_gz_dashboard.db.common_sql import *


class IndicatorItemList(Resource):
    """
    查询所有指标项目记录
    """

    def __init__(self):
        self._db_module = CommonDBModule()

    def get(self):
        filter_params, page_limit_params = "1=1", ""
        sql = SELECT_ALL_INDICATOR_ITEMS % (filter_params, page_limit_params)
        logging.getLogger(__name__).info('执行SQL查询：{}'.format(sql))
        cursor, conn = self._db_module.get_conn()
        df = pd.read_sql(sql, con=conn)
        records = df.to_dict(orient="records")
        result = {
            "total": len(records),
            "records": records,
        }
        result_info = {'status': '00000', 'reason': u'成功', 'data': result}
        return result_info
