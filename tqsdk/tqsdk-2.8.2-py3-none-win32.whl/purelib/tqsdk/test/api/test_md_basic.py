#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import random
import unittest

from tqsdk import TqApi, utils
from tqsdk.test.base_testcase import TQBaseTestcase


class TestMdBasic(TQBaseTestcase):
    """
    测试TqApi行情相关函数基本功能, 以及TqApi与行情服务器交互是否符合设计预期

    注：
    1. 在本地运行测试用例前需设置运行环境变量(Environment variables), 保证api中dict及set等类型的数据序列在每次运行时元素顺序一致: PYTHONHASHSEED=32
    2. 若测试用例中调用了会使用uuid的功能函数时（如insert_order()会使用uuid生成order_id）,
        则：在生成script文件时及测试用例中都需设置 utils.RD = random.Random(x), 以保证两次生成的uuid一致, x取值范围为0-2^32
    3. 对盘中的测试用例（即非回测）：因为TqSim模拟交易 Order 的 insert_date_time 和 Trade 的 trade_date_time 不是固定值，所以改为判断范围。
        盘中时：self.assertAlmostEqual(1575292560005832000 / 1e9, order1.insert_date_time / 1e9, places=1)
        回测时：self.assertEqual(1575291600000000000, order1.insert_date_time)
    """

    def setUp(self):
        super(TestMdBasic, self).setUp()

    def tearDown(self):
        super(TestMdBasic, self).tearDown()

    # 获取行情测试
    def test_get_quote_normal(self):
        """
        获取行情报价
        """
        # 预设服务器端响应
        utils.RD = random.Random(4)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_md_basic_get_quote_normal.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        # 获取行情
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        q = api.get_quote("SHFE.cu2106")
        self.assertEqual(q.datetime, "2021-04-20 11:23:24.500000")
        self.assertEqual(q.ask_price1, 69440.0)
        self.assertEqual(q.ask_volume1, 1)
        self.assertEqual(q.bid_price1, 69430.0)
        self.assertEqual(q.bid_volume1, 11)
        self.assertEqual(q.last_price, 69440.0)
        self.assertEqual(q.highest, 69710.0)
        self.assertEqual(q.lowest, 69000.0)
        self.assertEqual(q.open, 69660.0)
        self.assertNotEqual(q.close, q.close)  # q.close is nan
        self.assertEqual(q.average, 69292.949065)
        self.assertEqual(q.volume, 109099)
        self.assertEqual(q.amount, 37798957250.0)
        self.assertEqual(q.open_interest, 182870)
        self.assertNotEqual(q.settlement, q.settlement)
        self.assertEqual(q.upper_limit, 73530.0)
        self.assertEqual(q.lower_limit, 63900)
        self.assertEqual(q.pre_open_interest, 182656)
        self.assertEqual(q.pre_settlement, 68720.0)
        self.assertEqual(q.pre_close, 69660.0)
        self.assertEqual(q.price_tick, 10)
        self.assertEqual(q.price_decs, 0)
        self.assertEqual(q.volume_multiple, 5)
        self.assertEqual(q.max_limit_order_volume, 500)
        self.assertEqual(q.max_market_order_volume, 0)
        self.assertEqual(q.min_limit_order_volume, 0)
        self.assertEqual(q.min_market_order_volume, 0)
        self.assertEqual(q.underlying_symbol, "")
        self.assertTrue(q.strike_price != q.strike_price)  # 判定nan
        self.assertEqual(q.expired, False)
        self.assertEqual(q.ins_class, "FUTURE")
        # 这两个字段不是对用户承诺的字段，api 中调用 _symbols_to_quotes 只有 objs.quote 里说明的字段
        # self.assertEqual(q.margin, 18249.0)
        # self.assertEqual(q.commission, 13.035)
        self.assertEqual(repr(q.trading_time.day),
                         "[['09:00:00', '10:15:00'], ['10:30:00', '11:30:00'], ['13:30:00', '15:00:00']]")
        self.assertEqual(repr(q.trading_time.night), "[['21:00:00', '25:00:00']]")
        self.assertEqual(q.expire_datetime, 1623740400.0)
        self.assertEqual(q.delivery_month, 6)
        self.assertEqual(q.delivery_year, 2021)
        self.assertEqual(q.instrument_id, "SHFE.cu2106")
        self.assertEqual(q.ask_price2, 69450.0)
        self.assertEqual(q.ask_volume2, 15)
        self.assertEqual(q.ask_price3, 69460.0)
        self.assertEqual(q.ask_volume3, 29)
        self.assertEqual(q.ask_price4, 69470.0)
        self.assertEqual(q.ask_volume4, 25)
        self.assertEqual(q.ask_price5, 69480)
        self.assertEqual(q.ask_volume5, 40)
        self.assertEqual(q.bid_price2, 69420.0)
        self.assertEqual(q.bid_volume2, 45)
        self.assertEqual(q.bid_price3, 69410.0)
        self.assertEqual(q.bid_volume3, 12)
        self.assertEqual(q.bid_price4, 69400.0)
        self.assertEqual(q.bid_volume4, 15)
        self.assertEqual(q.bid_price5, 69390)
        self.assertEqual(q.bid_volume5, 8)
        # 其他取值方式
        self.assertEqual(q["pre_close"], 69660.0)
        self.assertEqual(q.get("pre_settlement"), 68720.0)
        self.assertEqual(q.get("highest"), 69710.0)
        self.assertEqual(q.get("lowest"), 69000.0)
        self.assertEqual(q["open"], 69660.0)
        self.assertNotEqual(q["close"], q["close"])
        # 报错测试
        self.assertRaises(Exception, api.get_quote, "SHFE.au2199")
        self.assertRaises(KeyError, q.__getitem__, "ask_price6")
        api.close()

    def test_get_kline_serial(self):
        """
        获取K线数据
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_md_basic_get_kline_serial.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        # 测试: 获取K线数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        klines = api.get_kline_serial("SHFE.cu2106", 10)
        self.assertEqual(klines.iloc[-1].close, 69470.0)
        self.assertEqual(klines.iloc[-1].id, 564172)
        self.assertEqual(klines.iloc[-2].id, 564171)
        self.assertEqual(klines.iloc[-1].datetime, 1618889010000000000)
        self.assertEqual(klines.iloc[-1].open, 69450)
        self.assertEqual(klines.iloc[-1].volume, 96)
        self.assertEqual(klines.iloc[-1].open_oi, 182885)
        self.assertEqual(klines.iloc[-1].duration, 10)
        # 其他取值方式
        self.assertEqual(klines.duration.iloc[-1], 10)
        self.assertEqual(klines.iloc[-1]["duration"], 10)
        self.assertEqual(klines["duration"].iloc[-1], 10)
        # 报错测试
        self.assertRaises(Exception, api.get_kline_serial, "SHFE.au1999", 10)
        self.assertRaises(AttributeError, klines.iloc[-1].__getattribute__, "dur")
        self.assertRaises(KeyError, klines.iloc[-1].__getitem__, "dur")
        api.close()

    def test_get_tick_serial(self):
        """
        获取tick数据
        """
        # 预设服务器端响应
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_md_basic_get_tick_serial.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        # 测试: 获取tick数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        ticks = api.get_tick_serial("SHFE.cu2106")
        self.assertEqual(ticks.iloc[-1].id, 3091028)
        self.assertEqual(ticks.iloc[-1].datetime, 1618889035000000000)
        self.assertEqual(ticks.iloc[-1].last_price, 69540.0)
        self.assertEqual(ticks.iloc[-1].average, 69294.40574)
        self.assertEqual(ticks.iloc[-1].highest, 69710.0)
        self.assertEqual(ticks.iloc[-1].lowest, 69000.0)
        self.assertEqual(ticks.iloc[-1].ask_price1, 69550.0)
        self.assertEqual(ticks.iloc[-1].ask_volume1, 15)
        self.assertEqual(ticks.iloc[-1].bid_price1, 69540.0)
        self.assertEqual(ticks.iloc[-1].bid_volume1, 47)
        self.assertEqual(ticks.iloc[-1].volume, 109843)
        self.assertEqual(ticks.iloc[-1].amount, 38057527050)
        self.assertEqual(ticks.iloc[-1].open_interest, 182899)
        self.assertEqual(ticks.iloc[-1].duration, 0)
        # 其他调用方式
        self.assertEqual(ticks.open_interest.iloc[-1], 182899)
        self.assertEqual(ticks["open_interest"].iloc[-2], 182899)
        self.assertEqual(ticks.iloc[-1]["ask_price1"], 69550)
        # 报错测试
        self.assertRaises(Exception, api.get_tick_serial, "SHFE.au1999")
        self.assertRaises(AttributeError, ticks.iloc[-1].__getattribute__, "dur")
        self.assertRaises(KeyError, ticks.iloc[-1].__getitem__, "dur")
        api.close()

    def test_get_kline_serial_adj_type(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_md_basic_get_kline_serial_adj_type.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        # 测试: 获取tick数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        klines1 = api.get_kline_serial("SSE.600853", 86400, adj_type=None)
        self.assertEqual(klines1.iloc[-100].id, 701)
        self.assertEqual(klines1.iloc[-100].datetime, 1606060800000000000)
        self.assertEqual(klines1.iloc[-100].open, 3.34)
        self.assertEqual(klines1.iloc[-100].high, 3.41)
        self.assertEqual(klines1.iloc[-100].low, 3.33)
        self.assertEqual(klines1.iloc[-100].close, 3.37)
        self.assertEqual(klines1.iloc[-100].volume, 6663620)
        self.assertEqual(klines1.iloc[-100].open_oi, 0)
        self.assertEqual(klines1.iloc[-100].duration, 86400)

        klines2 = api.get_kline_serial("SSE.600853", 86400, adj_type="FORWARD")
        self.assertEqual(klines2.iloc[-100].id, 701)
        self.assertEqual(klines2.iloc[-100].datetime, 1606060800000000000)
        self.assertAlmostEquals(klines2.iloc[-100].open, 2.767009, places=4)
        self.assertAlmostEquals(klines2.iloc[-100].high, 2.825, places=4)
        self.assertAlmostEquals(klines2.iloc[-100].low, 2.758724, places=4)
        self.assertAlmostEquals(klines2.iloc[-100].close, 2.791862, places=4)
        self.assertEqual(klines2.iloc[-100].volume, 6663620)
        self.assertEqual(klines2.iloc[-100].open_oi, 0)
        self.assertEqual(klines2.iloc[-100].duration, 86400)

        klines3 = api.get_kline_serial("SSE.600853", 86400, adj_type="BACK")
        self.assertEqual(klines3.iloc[-1].id, 800)
        self.assertEqual(klines3.iloc[-1].datetime, 1618848000000000000)
        self.assertAlmostEquals(klines3.iloc[-1].open, 3.234973, places=4)
        self.assertAlmostEquals(klines3.iloc[-1].high, 3.234973, places=4)
        self.assertAlmostEquals(klines3.iloc[-1].low, 3.198761, places=4)
        self.assertAlmostEquals(klines3.iloc[-1].close, 3.222903, places=4)
        self.assertEqual(klines3.iloc[-1].volume, 2152240)
        self.assertEqual(klines3.iloc[-1].open_oi, 0)
        self.assertEqual(klines3.iloc[-1].duration, 86400)

        klines4 = api.get_kline_serial("SSE.600853", 3600, adj_type="FORWARD")
        self.assertEqual(klines4.iloc[-100].id, 3903)
        self.assertEqual(klines4.iloc[-100].datetime, 1616389200000000000)
        self.assertAlmostEquals(klines4.iloc[-100].open, 2.66, places=4)
        self.assertAlmostEquals(klines4.iloc[-100].high, 2.67, places=4)
        self.assertAlmostEquals(klines4.iloc[-100].low, 2.65, places=4)
        self.assertAlmostEquals(klines4.iloc[-100].close, 2.66, places=4)
        self.assertEqual(klines4.iloc[-100].volume, 1275395)
        self.assertEqual(klines4.iloc[-100].open_oi, 0)
        self.assertEqual(klines4.iloc[-100].duration, 3600)
        api.close()

    def test_get_tick_serial_adj_type(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_md_basic_get_tick_serial_adj_type.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        # 测试: 获取tick数据
        utils.RD = random.Random(4)
        api = TqApi(auth="tianqin,tianqin", _md_url=md_url)
        ticks = api.get_tick_serial("SSE.600853", adj_type=None)
        self.assertEqual(ticks.iloc[-199].id, 1184833)
        self.assertEqual(ticks.iloc[-199].datetime, 1618887093649999872)
        self.assertEqual(ticks.iloc[-199].last_price, 2.66)
        self.assertEqual(ticks.iloc[-199].average, 2.66435)
        self.assertEqual(ticks.iloc[-199].highest, 2.68)
        self.assertEqual(ticks.iloc[-199].lowest, 2.65)

        self.assertEqual(ticks.iloc[-199].ask_price1, 2.67)
        self.assertEqual(ticks.iloc[-199].ask_volume1, 82120)
        self.assertEqual(ticks.iloc[-199].bid_price1, 2.66)
        self.assertEqual(ticks.iloc[-199].bid_volume1, 259044)

        self.assertEqual(ticks.iloc[-199].ask_price2, 2.68)
        self.assertEqual(ticks.iloc[-199].ask_volume2, 332288)
        self.assertEqual(ticks.iloc[-199].bid_price2, 2.65)
        self.assertEqual(ticks.iloc[-199].bid_volume2, 411880)

        self.assertEqual(ticks.iloc[-199].ask_price3, 2.69)
        self.assertEqual(ticks.iloc[-199].ask_volume3, 508768)
        self.assertEqual(ticks.iloc[-199].bid_price3, 2.64)
        self.assertEqual(ticks.iloc[-199].bid_volume3, 239700)

        self.assertEqual(ticks.iloc[-199].ask_price4, 2.7)
        self.assertEqual(ticks.iloc[-199].ask_volume4, 164136)
        self.assertEqual(ticks.iloc[-199].bid_price4, 2.63)
        self.assertEqual(ticks.iloc[-199].bid_volume4, 142200)

        self.assertEqual(ticks.iloc[-199].ask_price5, 2.71)
        self.assertEqual(ticks.iloc[-199].ask_volume5, 163020)
        self.assertEqual(ticks.iloc[-199].bid_price5, 2.62)
        self.assertEqual(ticks.iloc[-199].bid_volume5, 80500)

        self.assertEqual(ticks.iloc[-199].volume, 1994576)
        self.assertEqual(ticks.iloc[-199].amount, 5314250)
        api.close()
