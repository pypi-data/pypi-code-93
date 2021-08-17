#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'limin'

import os
import random
import unittest
from datetime import datetime

from tqsdk import TqApi, TqBacktest, utils, TqChan
from tqsdk.tools import DataDownloader
from tqsdk.test.base_testcase import TQBaseTestcase


class TestAuth(TQBaseTestcase):
    '''
     测试对于获取指定类型数据，tqsdk 无权限用户应该给予报错和提示；
     其他测试用例都是使用有全部权限的用户
    '''

    def setUp(self):
        super(TestAuth, self).setUp()

    def tearDown(self):
        super(TestAuth, self).tearDown()

    def test_download(self):
        """
        下载数据报错
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_auth_download.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        # 测试
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin1,tianqin1", _md_url=md_url)
        self.assertRaises(Exception, DataDownloader, api, symbol_list="CFFEX.T1809", dur_sec=0,
                       start_dt=datetime(2018, 5, 1), end_dt=datetime(2018, 7, 1), csv_file_name="tick.csv")
        api.close()

    @unittest.skip("免费用户可以每日回测3次")
    def test_backtest(self):
        """
        回测报错
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_md_backtest_get_quote.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        # 测试
        utils.RD = random.Random(4)
        self.assertRaises(Exception, TqApi, backtest=TqBacktest(datetime(2020, 6, 2), datetime(2020, 6, 3)),
                          auth="tianqin1,tianqin1", _md_url=md_url)

    def test_sec(self):
        """
        股票数据
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_auth_sec.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        # 测试
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin1,tianqin1", _md_url=md_url)
        self.assertRaises(Exception, api.get_quote, "SSE.10002513")
        api.close()
