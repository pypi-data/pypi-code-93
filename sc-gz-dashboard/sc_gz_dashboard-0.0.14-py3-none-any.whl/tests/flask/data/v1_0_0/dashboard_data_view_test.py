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

import json
import logging
import unittest

from sc_utilities.log_utils import log_init

from sc_gz_dashboard.flask.data.v1_0_0.dashboard_data_view import DashBoardDataView


class DashBoardDataViewTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        log_init()

    def test_get_all_dashboard_data(self):
        view = DashBoardDataView()
        result = view.get_all_dashboard_data(year=2021)
        self.assertTrue(len(result) > 0)
        data_json = json.dumps(result, ensure_ascii=False, indent="\t")
        self.assertIsNotNone(data_json)
        logging.getLogger(__name__).info("json %s", data_json)
        # 测试是否从缓存获取数据
        result = view.get_all_dashboard_data(year=2021)
        self.assertTrue(len(result) > 0)
        # 记录不存在
        result = view.get_all_dashboard_data(year=2022)
        self.assertTrue(len(result) > 0)

    def test_get_available_years(self):
        view = DashBoardDataView()
        result = view.get_available_years()
        logging.getLogger(__name__).info("json %s", result.keys())
        self.assertTrue(len(result) > 0)
        data_json = json.dumps(result, ensure_ascii=False, indent="\t")
        self.assertIsNotNone(data_json)
        logging.getLogger(__name__).info("json %s", data_json)


if __name__ == '__main__':
    unittest.main()
