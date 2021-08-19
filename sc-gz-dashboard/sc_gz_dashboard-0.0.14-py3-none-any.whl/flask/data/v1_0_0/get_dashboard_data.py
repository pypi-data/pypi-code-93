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

from .dashboard_data_view import DashBoardDataView
from sc_gz_dashboard.utils import DecimalEncoder
import json


class GetDashboardData(Resource):

    def get(self, year: int):
        """
        获取看板数据
        :return:
        """
        try:
            year = int(year)
        except ValueError:
            result_info = {'status': '00001', 'reason': u'失败', 'data': "[]"}
            return result_info
        logging.getLogger(__name__).info("获取%s年看板数据...", year)
        view = DashBoardDataView()
        all_data = view.get_all_dashboard_data(year=year)
        result_info = {'status': '00000', 'reason': u'成功', 'data': json.dumps(all_data, cls=DecimalEncoder)}
        return result_info
