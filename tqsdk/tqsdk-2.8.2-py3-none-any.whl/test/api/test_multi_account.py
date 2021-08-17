#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import random
import unittest

import pytest

from tqsdk import TqApi, TqAccount, TqSim, TqKq, utils, TqChan
from tqsdk import TqMultiAccount, TargetPosTask
from tqsdk.test.base_testcase import TQBaseTestcase
from tqsdk.test.helper import MockWebsocketsServer


@pytest.mark.skip(reason="temporarily remove Mock 多个网络连接，导致发包顺序不确定，需要重构测试代码")
class TestMultiAccount(TQBaseTestcase):
    """
    simnow 不可用，使用 TqKq 和 TqSim 测试多账户，下次录脚本可以换回 simnow 代替实盘账户
    """
    def setUp(self):
        super(TestMultiAccount, self).setUp()
        self.td_mock1 = None
        self.td_mock2 = None
        self.td_mock3 = None

    def tearDown(self):
        super(TestMultiAccount, self).tearDown()
        if self.td_mock1:
            self.td_mock1.close()
        if self.td_mock2:
            self.td_mock2.close()
        if self.td_mock3:
            self.td_mock3.close()

    """
    多账户测试场景一: 同时登陆3个实盘账户(TqAccount × 3)
    分别进行登录、下单和撤单操作, 预期持仓、资金、委托和成交数据符合预期
    """
    def test_multi_account_insert_order(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.td_mock1 = MockWebsocketsServer(url="wss://otg-sim.shinnytech.com/trade", account_id="147716")
        self.td_mock2 = MockWebsocketsServer(url="wss://otg-sim.shinnytech.com/trade", account_id="172289")
        self.td_mock3 = MockWebsocketsServer(url="wss://otg-sim.shinnytech.com/trade", account_id="103988")

        self.md_mock.run(os.path.join(dir_path, "log_file", "test_multi_account_insert_order.script.lzma"))
        self.td_mock1.run(os.path.join(dir_path, "log_file", "test_multi_account_insert_order.script.lzma"))
        self.td_mock2.run(os.path.join(dir_path, "log_file", "test_multi_account_insert_order.script.lzma"))
        self.td_mock3.run(os.path.join(dir_path, "log_file", "test_multi_account_insert_order.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        td_url1 = f"ws://127.0.0.1:{self.td_mock1.port}/"
        td_url2 = f"ws://127.0.0.1:{self.td_mock2.port}/"
        td_url3 = f"ws://127.0.0.1:{self.td_mock3.port}/"

        account1 = TqAccount("快期模拟", "147716", "123456", td_url=td_url1)
        account2 = TqAccount("快期模拟", "172289", "123456", td_url=td_url2)
        account3 = TqAccount("快期模拟", "103988", "123456", td_url=td_url3)
        account_list = TqMultiAccount([account1, account2, account3])
        utils.RD = random.Random(4)
        api = TqApi(account=account_list, auth="tianqin,tianqin", _md_url=md_url)

        # 下单
        order1 = api.insert_order(symbol="DCE.m2105", direction="BUY", offset="OPEN", volume=5, limit_price=3529,
                                  account=account1, order_id="test_multi_account_1_1")
        order2 = api.insert_order(symbol="DCE.m2105", direction="BUY", offset="OPEN", volume=10, limit_price=3540,
                                  account=account2, order_id="test_multi_account_2_1")
        order3 = api.insert_order(symbol="DCE.m2109", direction="BUY", offset="OPEN", volume=15, limit_price=3650,
                                  account=account1, order_id="test_multi_account_1_2")
        order4 = api.insert_order(symbol="DCE.m2109", direction="BUY", offset="OPEN", volume=20, limit_price=3640,
                                  account=account2, order_id="test_multi_account_2_2")
        api.cancel_order(order3, account=account1)
        api.cancel_order(order4, account=account2)
        while order1.status != "FINISHED" or order2.status != "FINISHED" or order3.status != "FINISHED" or order4.status != "FINISHED":
            api.wait_update()

        # 查询资产
        act1 = api.get_account(account1)
        act2 = api.get_account(account2)
        act3 = api.get_account(account3)
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 1000000.0, 'static_balance': 1000000.0, 'balance': 999942.5, 'available': 990930.0, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -50.0, 'position_profit': -50.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 9012.5, 'frozen_commission': 0.0, 'commission': 7.5, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.009013018248549292, 'market_value': 0.0, 'user_id': '147716'}",
            str(act1)
        )
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 0.0, 'static_balance': 1000000.0, 'balance': 999885.0, 'available': 981860.0, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -100.0, 'position_profit': -100.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 18025.0, 'frozen_commission': 0.0, 'commission': 15.0, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 1000000.0, 'withdraw': 0.0, 'risk_ratio': 0.01802707311340804, 'market_value': 0.0, 'user_id': '172289'}",
            str(act2)
        )
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 998480.0000000002, 'static_balance': 998480.0000000002, 'balance': 998480.0000000002, 'available': 998480.0000000002, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': 0.0, 'position_profit': 0.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 0.0, 'frozen_commission': 0.0, 'commission': 0.0, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0, 'market_value': 0.0, 'user_id': '103988'}",
            str(act3)
        )
        # 查询持仓
        pos1 = api.get_position("DCE.m2105", account=account1)
        pos2 = api.get_position(account=account2)["DCE.m2105"]
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2105', 'pos_long_his': 0, 'pos_long_today': 5, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 5, 'volume_long_his': 0, 'volume_long': 5, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 3521.0, 'open_price_short': nan, 'open_cost_long': 176050.0, 'open_cost_short': nan, 'position_price_long': 3521.0, 'position_price_short': nan, 'position_cost_long': 176050.0, 'position_cost_short': nan, 'float_profit_long': -50.0, 'float_profit_short': nan, 'float_profit': -50.0, 'position_profit_long': -50.0, 'position_profit_short': nan, 'position_profit': -50.0, 'margin_long': 9012.5, 'margin_short': nan, 'margin': 9012.5, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'user_id': '147716', 'volume_long_yd': 0, 'volume_short_yd': 0, 'last_price': 3520.0}",
            str(pos1)
        )
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2105', 'pos_long_his': 0, 'pos_long_today': 10, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 10, 'volume_long_his': 0, 'volume_long': 10, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 3521.0, 'open_price_short': nan, 'open_cost_long': 352100.0, 'open_cost_short': nan, 'position_price_long': 3521.0, 'position_price_short': nan, 'position_cost_long': 352100.0, 'position_cost_short': nan, 'float_profit_long': -100.0, 'float_profit_short': nan, 'float_profit': -100.0, 'position_profit_long': -100.0, 'position_profit_short': nan, 'position_profit': -100.0, 'margin_long': 18025.0, 'margin_short': nan, 'margin': 18025.0, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'user_id': '172289', 'volume_long_yd': 0, 'volume_short_yd': 0, 'last_price': 3520.0}",
            str(pos2)
        )
        # 查询委托
        ord1 = api.get_order(order_id=order1.order_id, account=account1)
        self.assertEqual(
            "{'order_id': 'test_multi_account_1_1', 'exchange_order_id': 'test_multi_account_1_1', 'exchange_id': 'DCE', 'instrument_id': 'm2105', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 5, 'volume_left': 0, 'limit_price': 3529.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1619142508746737801, 'last_msg': '', 'status': 'FINISHED', 'seqno': 5, 'user_id': '147716', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(ord1)
        )
        ord2 = api.get_order(account=account2)['test_multi_account_2_1']
        self.assertEqual(
            "{'order_id': 'test_multi_account_2_1', 'exchange_order_id': 'test_multi_account_2_1', 'exchange_id': 'DCE', 'instrument_id': 'm2105', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 10, 'volume_left': 0, 'limit_price': 3540.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1619142508746258375, 'last_msg': '', 'status': 'FINISHED', 'seqno': 5, 'user_id': '172289', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(ord2)
        )

        # 撤单结果校验
        self.assertEqual(
            "{'order_id': 'test_multi_account_1_2', 'exchange_order_id': 'test_multi_account_1_2', 'exchange_id': 'DCE', 'instrument_id': 'm2109', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 15, 'volume_left': 15, 'limit_price': 3650.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1619142508763869115, 'last_msg': '', 'status': 'FINISHED', 'seqno': 8, 'user_id': '147716', 'frozen_margin': 27037.5, 'frozen_premium': 0.0, 'frozen_commission': 22.5}",
            str(order3)
        )
        self.assertEqual(
            "{'order_id': 'test_multi_account_2_2', 'exchange_order_id': 'test_multi_account_2_2', 'exchange_id': 'DCE', 'instrument_id': 'm2109', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 20, 'volume_left': 20, 'limit_price': 3640.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1619142508763287419, 'last_msg': '', 'status': 'FINISHED', 'seqno': 8, 'user_id': '172289', 'frozen_margin': 36050.0, 'frozen_premium': 0.0, 'frozen_commission': 30.0}",
            str(order4)
        )

        # 查询成交
        trd1 = api.get_trade(account=account1)['0edba25d8f264fb9acd8fe8f034bef8d']
        self.assertEqual(
            "{'order_id': 'test_multi_account_1_1', 'trade_id': '0edba25d8f264fb9acd8fe8f034bef8d', 'exchange_trade_id': '0edba25d8f264fb9acd8fe8f034bef8d', 'exchange_id': 'DCE', 'instrument_id': 'm2105', 'direction': 'BUY', 'offset': 'OPEN', 'price': 3521.0, 'volume': 5, 'trade_date_time': 1619142508746822781, 'seqno': 1, 'user_id': '147716', 'commission': 7.5}",
            str(trd1)
        )

        trd2 = api.get_trade(account=account2)['ca59692510a84ca084ac349ee1467a16']
        self.assertEqual(
            "{'order_id': 'test_multi_account_2_1', 'trade_id': 'ca59692510a84ca084ac349ee1467a16', 'exchange_trade_id': 'ca59692510a84ca084ac349ee1467a16', 'exchange_id': 'DCE', 'instrument_id': 'm2105', 'direction': 'BUY', 'offset': 'OPEN', 'price': 3521.0, 'volume': 10, 'trade_date_time': 1619142508746373231, 'seqno': 1, 'user_id': '172289', 'commission': 15.0}",
            str(trd2)
        )
        api.close()

    """
    多账户测试场景二: 同时登录 TqAccount + TqSim + TqKq 
    分别进行登录、下单和撤单操作, 预期持仓、资金、委托和成交数据符合预期
    """
    def test_multi_account_with_diff_type_account(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.td_mock1 = MockWebsocketsServer(url="wss://otg-sim.shinnytech.com/trade", account_id="103988")
        self.td_mock3 = MockWebsocketsServer(url="wss://otg-sim.shinnytech.com/trade", account_id="0dedd51a-2826-46d0-af82-0e26ffcb5625")
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_multi_account_with_diff_type_account.script.lzma"))
        self.td_mock1.run(os.path.join(dir_path, "log_file", "test_multi_account_with_diff_type_account.script.lzma"))
        self.td_mock3.run(os.path.join(dir_path, "log_file", "test_multi_account_with_diff_type_account.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        td_url1 = f"ws://127.0.0.1:{self.td_mock1.port}/"
        td_url3 = f"ws://127.0.0.1:{self.td_mock3.port}/"

        # 测试
        account1 = TqAccount("快期模拟", "103988", "123456", td_url=td_url1)
        account2 = TqSim(account_id="sim1")
        account3 = TqKq(td_url=td_url3)
        account_list = TqMultiAccount([account1, account2, account3])
        # 测试
        utils.RD = random.Random(8)
        api = TqApi(account=account_list, _md_url=md_url, auth="tianqin,tianqin")
        # 下单
        order1 = api.insert_order(symbol="SHFE.cu2107", direction="BUY", offset="OPEN", volume=1, limit_price=71600,
                                  account=account1)
        order2 = api.insert_order(symbol="SHFE.cu2107", direction="BUY", offset="OPEN", volume=10, limit_price=71500,
                                  account=account2)
        order3 = api.insert_order(symbol="DCE.c2109", direction="BUY", offset="OPEN", volume=10,
                                  account=account3)
        order4 = api.insert_order(symbol="DCE.i2109", direction="BUY", offset="OPEN", volume=15, limit_price=1200,
                                  account=account1)
        order5 = api.insert_order(symbol="DCE.i2109", direction="BUY", offset="OPEN", volume=20, limit_price=1200,
                                  account=account2)
        api.cancel_order(order4, account=account1)
        api.cancel_order(order5, account=account2)
        while order1.status != "FINISHED" or order2.status != "FINISHED" or order3.status != "FINISHED" or order4.status != "FINISHED" or order5.status != "FINISHED":
            api.wait_update()

        # 查询委托
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_6694f229359b154881a0d5b3ffc6e35c', 'exchange_order_id': 'PYSDK_insert_6694f229359b154881a0d5b3ffc6e35c', 'exchange_id': 'SHFE', 'instrument_id': 'cu2107', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 1, 'volume_left': 0, 'limit_price': 71600.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1619445471091185153, 'last_msg': '', 'status': 'FINISHED', 'seqno': 3, 'user_id': '103988', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(order1)
        )
        self.assertAlmostEqual(1619445470540670000 / 1e9, order2['insert_date_time'] / 1e9, places=0)
        del order2['insert_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_92b850ad7eb72f8263f65da874007cb4', 'exchange_order_id': 'PYSDK_insert_92b850ad7eb72f8263f65da874007cb4', 'exchange_id': 'SHFE', 'instrument_id': 'cu2107', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 10, 'volume_left': 0, 'limit_price': 71500.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'user_id': 'sim1', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order2)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_67164890d49d0ac1e5b8063831360a40', 'exchange_order_id': 'PYSDK_insert_67164890d49d0ac1e5b8063831360a40', 'exchange_id': 'DCE', 'instrument_id': 'c2109', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 10, 'volume_left': 0, 'limit_price': 0.0, 'price_type': 'ANY', 'volume_condition': 'ANY', 'time_condition': 'IOC', 'insert_date_time': 1619445471249375387, 'last_msg': '', 'status': 'FINISHED', 'seqno': 3, 'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(order3)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_852a5fba444adf42b37f5722051e2670', 'exchange_order_id': 'PYSDK_insert_852a5fba444adf42b37f5722051e2670', 'exchange_id': 'DCE', 'instrument_id': 'i2109', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 15, 'volume_left': 0, 'limit_price': 1200.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1619445471291327675, 'last_msg': '', 'status': 'FINISHED', 'seqno': 6, 'user_id': '103988', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(order4)
        )
        self.assertAlmostEqual(1619445470677049000 / 1e9, order5['insert_date_time'] / 1e9, places=0)
        del order5['insert_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_a9b7e3ea1d1d784fb9db434b610b1631', 'exchange_order_id': 'PYSDK_insert_a9b7e3ea1d1d784fb9db434b610b1631', 'exchange_id': 'DCE', 'instrument_id': 'i2109', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 20, 'volume_left': 0, 'limit_price': 1200.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'user_id': 'sim1', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order5)
        )

        # 查询持仓
        pos1 = api.get_position("SHFE.cu2107", account=account1)
        pos2 = api.get_position("DCE.i2109", account=account1)
        self.assertEqual(
            "{'exchange_id': 'SHFE', 'instrument_id': 'cu2107', 'pos_long_his': 0, 'pos_long_today': 1, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 1, 'volume_long_his': 0, 'volume_long': 1, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 71480.0, 'open_price_short': nan, 'open_cost_long': 357400.0, 'open_cost_short': nan, 'position_price_long': 71480.0, 'position_price_short': nan, 'position_cost_long': 357400.0, 'position_cost_short': nan, 'float_profit_long': -50.0, 'float_profit_short': nan, 'float_profit': -50.0, 'position_profit_long': -50.0, 'position_profit_short': nan, 'position_profit': -50.0, 'margin_long': 31662.0, 'margin_short': nan, 'margin': 31662.0, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'user_id': '103988', 'volume_long_yd': 0, 'volume_short_yd': 0, 'last_price': 71470.0}",
            str(pos1)
        )
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'i2109', 'pos_long_his': 15, 'pos_long_today': 15, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 30, 'volume_long_his': 0, 'volume_long': 30, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 1119.0, 'open_price_short': nan, 'open_cost_long': 3357000.0, 'open_cost_short': nan, 'position_price_long': 1119.0, 'position_price_short': nan, 'position_cost_long': 3357000.0, 'position_cost_short': nan, 'float_profit_long': 85500.0, 'float_profit_short': nan, 'float_profit': 85500.0, 'position_profit_long': 85500.0, 'position_profit_short': nan, 'position_profit': 85500.0, 'margin_long': 272880.0, 'margin_short': nan, 'margin': 272880.0, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'user_id': '103988', 'volume_long_yd': 15, 'volume_short_yd': 0, 'last_price': 1147.5}",
            str(pos2)
        )

        sim_pos1 = api.get_position("SHFE.cu2107", account=account2)
        sim_pos2 = api.get_position("DCE.i2109", account=account2)
        self.assertEqual(
            "{'exchange_id': 'SHFE', 'instrument_id': 'cu2107', 'pos_long_his': 0, 'pos_long_today': 10, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 10, 'volume_long_his': 0, 'volume_long': 10, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 71500.0, 'open_price_short': nan, 'open_cost_long': 3575000.0, 'open_cost_short': 0.0, 'position_price_long': 71500.0, 'position_price_short': nan, 'position_cost_long': 3575000.0, 'position_cost_short': 0.0, 'float_profit_long': -1500.0, 'float_profit_short': 0.0, 'float_profit': -1500.0, 'position_profit_long': -1500.0, 'position_profit_short': 0.0, 'position_profit': -1500.0, 'margin_long': 246715.0, 'margin_short': 0.0, 'margin': 246715.0, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'last_price': 71470.0, 'underlying_last_price': nan, 'future_margin': 24671.5}",
            str(sim_pos1)
        )
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'i2109', 'pos_long_his': 0, 'pos_long_today': 20, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 20, 'volume_long_his': 0, 'volume_long': 20, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 1200.0, 'open_price_short': nan, 'open_cost_long': 2400000.0, 'open_cost_short': 0.0, 'position_price_long': 1200.0, 'position_price_short': nan, 'position_cost_long': 2400000.0, 'position_cost_short': 0.0, 'float_profit_long': -105000.0, 'float_profit_short': 0.0, 'float_profit': -105000.0, 'position_profit_long': -105000.0, 'position_profit_short': 0.0, 'position_profit': -105000.0, 'margin_long': 181920.0, 'margin_short': 0.0, 'margin': 181920.0, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'last_price': 1147.5, 'underlying_last_price': nan, 'future_margin': 9096.0}",
            str(sim_pos2)
        )

        pos3 = api.get_position("DCE.c2109", account=account3)
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'c2109', 'pos_long_his': 0, 'pos_long_today': 10, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 10, 'volume_long_his': 0, 'volume_long': 10, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 2768.0, 'open_price_short': nan, 'open_cost_long': 276800.0, 'open_cost_short': nan, 'position_price_long': 2768.0, 'position_price_short': nan, 'position_cost_long': 276800.0, 'position_cost_short': nan, 'float_profit_long': -100.0, 'float_profit_short': nan, 'float_profit': -100.0, 'position_profit_long': -100.0, 'position_profit_short': nan, 'position_profit': -100.0, 'margin_long': 13750.0, 'margin_short': nan, 'margin': 13750.0, 'market_value_long': nan, 'market_value_short': nan, 'market_value': nan, 'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625', 'volume_long_yd': 0, 'volume_short_yd': 0, 'last_price': 2767.0}",
            str(pos3)
        )

        # 查询成交
        trd1 = api.get_trade(account=account1)
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_6694f229359b154881a0d5b3ffc6e35c', 'trade_id': '2217b0fe97c5439b82d7fccf79181db8', 'exchange_trade_id': '2217b0fe97c5439b82d7fccf79181db8', 'exchange_id': 'SHFE', 'instrument_id': 'cu2107', 'direction': 'BUY', 'offset': 'OPEN', 'price': 71480.0, 'volume': 1, 'trade_date_time': 1619445471091296639, 'seqno': 1, 'user_id': '103988', 'commission': 17.59}",
            str(trd1['2217b0fe97c5439b82d7fccf79181db8'])
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_852a5fba444adf42b37f5722051e2670', 'trade_id': 'b3b8e28facb94cf4a6d5395576d9c5bb', 'exchange_trade_id': 'b3b8e28facb94cf4a6d5395576d9c5bb', 'exchange_id': 'DCE', 'instrument_id': 'i2109', 'direction': 'BUY', 'offset': 'OPEN', 'price': 1148.0, 'volume': 15, 'trade_date_time': 1619445471291413773, 'seqno': 2, 'user_id': '103988', 'commission': 170.54999999999998}",
            str(trd1['b3b8e28facb94cf4a6d5395576d9c5bb'])
        )

        trd2 = api.get_trade(account=account2)
        trd2_1 = trd2['PYSDK_insert_92b850ad7eb72f8263f65da874007cb4|10']
        trd2_2 = trd2['PYSDK_insert_a9b7e3ea1d1d784fb9db434b610b1631|20']
        self.assertAlmostEqual(1619445470509570000/1e9, trd2_1['trade_date_time']/1e9, places=0)
        self.assertAlmostEqual(1619445470673509000/1e9, trd2_2['trade_date_time']/1e9, places=0)
        del trd2_1['trade_date_time']
        del trd2_2['trade_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_92b850ad7eb72f8263f65da874007cb4', 'trade_id': 'PYSDK_insert_92b850ad7eb72f8263f65da874007cb4|10', 'exchange_trade_id': 'PYSDK_insert_92b850ad7eb72f8263f65da874007cb4|10', 'exchange_id': 'SHFE', 'instrument_id': 'cu2107', 'direction': 'BUY', 'offset': 'OPEN', 'price': 71500.0, 'volume': 10, 'user_id': 'sim1', 'commission': 176.225}",
            str(trd2_1)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_a9b7e3ea1d1d784fb9db434b610b1631', 'trade_id': 'PYSDK_insert_a9b7e3ea1d1d784fb9db434b610b1631|20', 'exchange_trade_id': 'PYSDK_insert_a9b7e3ea1d1d784fb9db434b610b1631|20', 'exchange_id': 'DCE', 'instrument_id': 'i2109', 'direction': 'BUY', 'offset': 'OPEN', 'price': 1200.0, 'volume': 20, 'user_id': 'sim1', 'commission': 227.39999999999998}",
            str(trd2_2)
        )

        trd3 = api.get_trade(account=account3)
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_67164890d49d0ac1e5b8063831360a40', 'trade_id': '3df9c720a80541099d140f82683ae984', 'exchange_trade_id': '3df9c720a80541099d140f82683ae984', 'exchange_id': 'DCE', 'instrument_id': 'c2109', 'direction': 'BUY', 'offset': 'OPEN', 'price': 2768.0, 'volume': 10, 'trade_date_time': 1619445471249480213, 'seqno': 1, 'user_id': '0dedd51a-2826-46d0-af82-0e26ffcb5625', 'commission': 12.0}",
            str(trd3['3df9c720a80541099d140f82683ae984'])
        )
        api.close()

    """
    多账户测试场景三: 同时登录模拟账户 TqSim × 3
    分别进行登录、下单和撤单操作, 预期持仓、资金、委托和成交数据符合预期
    """
    def test_multi_account_with_3_tqsim(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_multi_account_with_3_tqsim.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"

        account1, account2, account3 = TqSim(account_id="sim1"), TqSim(account_id="sim2"), TqSim()
        account_list = TqMultiAccount([account1, account2, account3])
        # 测试
        utils.RD = random.Random(4)
        api = TqApi(account=account_list, _md_url=md_url, auth="tianqin,tianqin")
        # 下单
        order1 = api.insert_order(symbol="DCE.m2109", direction="BUY", offset="OPEN", volume=5, limit_price=3425,
                                  account=account1)
        order2 = api.insert_order(symbol="DCE.m2109", direction="BUY", offset="OPEN", volume=10, limit_price=3430,
                                  account=account2)
        order3 = api.insert_order(symbol="DCE.m2112", direction="BUY", offset="OPEN", volume=15, limit_price=3540,
                                  account=account3)
        order4 = api.insert_order(symbol="DCE.m2112", direction="BUY", offset="OPEN", volume=20, limit_price=3540,
                                  account=account2)
        api.cancel_order(order3, account=account3)
        api.cancel_order(order4, account=account2)

        while order1.status != "FINISHED" or order2.status != "FINISHED" or order3.status != "FINISHED" or order4.status != "FINISHED":
            api.wait_update()

        # 查询资产
        act1 = api.get_account(account1)
        act2 = api.get_account(account2)
        act3 = api.get_account(account3)
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 10000000.0, 'static_balance': 10000000.0, 'balance': 9998892.5, 'available': 9990397.5, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -1100.0, 'position_profit': -1100.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 8495.0, 'frozen_commission': 0.0, 'commission': 7.5, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.0008495940925457494, 'market_value': 0.0}",
            str(act1)
        )
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 10000000.0, 'static_balance': 10000000.0, 'balance': 9974655.0, 'available': 9923455.0, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -25300.0, 'position_profit': -25300.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 51200.0, 'frozen_commission': 0.0, 'commission': 45.0, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.005133009612863803, 'market_value': 0.0}",
            str(act2)
        )
        self.assertEqual(
            "{'currency': 'CNY', 'pre_balance': 10000000.0, 'static_balance': 10000000.0, 'balance': 9983027.5, 'available': 9957370.0, 'ctp_balance': nan, 'ctp_available': nan, 'float_profit': -16950.0, 'position_profit': -16950.0, 'close_profit': 0.0, 'frozen_margin': 0.0, 'margin': 25657.5, 'frozen_commission': 0.0, 'commission': 22.5, 'frozen_premium': 0.0, 'premium': 0.0, 'deposit': 0.0, 'withdraw': 0.0, 'risk_ratio': 0.002570112122800423, 'market_value': 0.0}",
            str(act3)
        )

        # 查询持仓
        pos1 = api.get_position("DCE.m2109", account=account1)
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2109', 'pos_long_his': 0, 'pos_long_today': 5, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 5, 'volume_long_his': 0, 'volume_long': 5, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 3425.0, 'open_price_short': nan, 'open_cost_long': 171250.0, 'open_cost_short': 0.0, 'position_price_long': 3425.0, 'position_price_short': nan, 'position_cost_long': 171250.0, 'position_cost_short': 0.0, 'float_profit_long': -1100.0, 'float_profit_short': 0.0, 'float_profit': -1100.0, 'position_profit_long': -1100.0, 'position_profit_short': 0.0, 'position_profit': -1100.0, 'margin_long': 8495.0, 'margin_short': 0.0, 'margin': 8495.0, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'last_price': 3403.0, 'underlying_last_price': nan, 'future_margin': 1699.0}",
            str(pos1)
        )

        pos2_1 = api.get_position("DCE.m2109", account=account2)
        pos2_2 = api.get_position("DCE.m2112", account=account2)
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2109', 'pos_long_his': 0, 'pos_long_today': 10, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 10, 'volume_long_his': 0, 'volume_long': 10, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 3430.0, 'open_price_short': nan, 'open_cost_long': 343000.0, 'open_cost_short': 0.0, 'position_price_long': 3430.0, 'position_price_short': nan, 'position_cost_long': 343000.0, 'position_cost_short': 0.0, 'float_profit_long': -2700.0, 'float_profit_short': 0.0, 'float_profit': -2700.0, 'position_profit_long': -2700.0, 'position_profit_short': 0.0, 'position_profit': -2700.0, 'margin_long': 16990.0, 'margin_short': 0.0, 'margin': 16990.0, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'last_price': 3403.0, 'underlying_last_price': nan, 'future_margin': 1699.0}",
            str(pos2_1)
        )
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2112', 'pos_long_his': 0, 'pos_long_today': 20, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 20, 'volume_long_his': 0, 'volume_long': 20, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 3540.0, 'open_price_short': nan, 'open_cost_long': 708000.0, 'open_cost_short': 0.0, 'position_price_long': 3540.0, 'position_price_short': nan, 'position_cost_long': 708000.0, 'position_cost_short': 0.0, 'float_profit_long': -22600.0, 'float_profit_short': 0.0, 'float_profit': -22600.0, 'position_profit_long': -22600.0, 'position_profit_short': 0.0, 'position_profit': -22600.0, 'margin_long': 34210.0, 'margin_short': 0.0, 'margin': 34210.0, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'last_price': 3427.0, 'underlying_last_price': nan, 'future_margin': 1710.5}",
            str(pos2_2)
        )

        pos3 = api.get_position("DCE.m2112", account=account3)
        self.assertEqual(
            "{'exchange_id': 'DCE', 'instrument_id': 'm2112', 'pos_long_his': 0, 'pos_long_today': 15, 'pos_short_his': 0, 'pos_short_today': 0, 'volume_long_today': 15, 'volume_long_his': 0, 'volume_long': 15, 'volume_long_frozen_today': 0, 'volume_long_frozen_his': 0, 'volume_long_frozen': 0, 'volume_short_today': 0, 'volume_short_his': 0, 'volume_short': 0, 'volume_short_frozen_today': 0, 'volume_short_frozen_his': 0, 'volume_short_frozen': 0, 'open_price_long': 3540.0, 'open_price_short': nan, 'open_cost_long': 531000.0, 'open_cost_short': 0.0, 'position_price_long': 3540.0, 'position_price_short': nan, 'position_cost_long': 531000.0, 'position_cost_short': 0.0, 'float_profit_long': -16950.0, 'float_profit_short': 0.0, 'float_profit': -16950.0, 'position_profit_long': -16950.0, 'position_profit_short': 0.0, 'position_profit': -16950.0, 'margin_long': 25657.5, 'margin_short': 0.0, 'margin': 25657.5, 'market_value_long': 0.0, 'market_value_short': 0.0, 'market_value': 0.0, 'last_price': 3427.0, 'underlying_last_price': nan, 'future_margin': 1710.5}",
            str(pos3)
        )

        # 查询委托
        self.assertAlmostEquals(1624330659531909000/1e9, order1['insert_date_time']/1e9, places=0)
        self.assertAlmostEquals(1624330659528013000/1e9, order2['insert_date_time']/1e9, places=0)
        self.assertAlmostEquals(1624330659556841000/1e9, order3['insert_date_time']/1e9, places=0)
        self.assertAlmostEquals(1624330659557778000/1e9, order4['insert_date_time']/1e9, places=0)
        del order1['insert_date_time']
        del order2['insert_date_time']
        del order3['insert_date_time']
        del order4['insert_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'exchange_order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'exchange_id': 'DCE', 'instrument_id': 'm2109', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 5, 'volume_left': 0, 'limit_price': 3425.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'user_id': 'sim1', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order1)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'exchange_id': 'DCE', 'instrument_id': 'm2109', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 10, 'volume_left': 0, 'limit_price': 3430.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'user_id': 'sim2', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order2)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258', 'exchange_order_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258', 'exchange_id': 'DCE', 'instrument_id': 'm2112', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 15, 'volume_left': 0, 'limit_price': 3540.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'user_id': 'TQSIM', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order3)
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_43000de01b2ed40ed3addccb2c33be0a', 'exchange_order_id': 'PYSDK_insert_43000de01b2ed40ed3addccb2c33be0a', 'exchange_id': 'DCE', 'instrument_id': 'm2112', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 20, 'volume_left': 0, 'limit_price': 3540.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'last_msg': '全部成交', 'status': 'FINISHED', 'user_id': 'sim2', 'frozen_margin': 0.0, 'frozen_premium': 0.0}",
            str(order4)
        )

        # 查询成交
        trd1 = api.get_trade(account=account1)['PYSDK_insert_1710cf5327ac435a7a97c643656412a9|5']
        self.assertAlmostEquals(1624330659531587000/1e9, trd1['trade_date_time']/1e9, places=0)
        del trd1['trade_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9', 'trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|5', 'exchange_trade_id': 'PYSDK_insert_1710cf5327ac435a7a97c643656412a9|5', 'exchange_id': 'DCE', 'instrument_id': 'm2109', 'direction': 'BUY', 'offset': 'OPEN', 'price': 3425.0, 'volume': 5, 'user_id': 'sim1', 'commission': 7.5}",
            str(trd1)
        )

        trd2 = api.get_trade(account=account2)['PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|10']
        self.assertAlmostEquals(1624330659527693000/1e9, trd2['trade_date_time']/1e9, places=0)
        del trd2['trade_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09', 'trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|10', 'exchange_trade_id': 'PYSDK_insert_fd724452ccea71ff4a14876aeaff1a09|10', 'exchange_id': 'DCE', 'instrument_id': 'm2109', 'direction': 'BUY', 'offset': 'OPEN', 'price': 3430.0, 'volume': 10, 'user_id': 'sim2', 'commission': 15.0}",
            str(trd2)
        )

        trd3 = api.get_trade(account=account3)['PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258|15']
        self.assertAlmostEquals(1624330659555677000 / 1e9, trd3['trade_date_time'] / 1e9, places=0)
        del trd3['trade_date_time']
        self.assertEqual(
            "{'order_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258', 'trade_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258|15', 'exchange_trade_id': 'PYSDK_insert_8534f45738d048ec0f1099c6c3e1b258|15', 'exchange_id': 'DCE', 'instrument_id': 'm2112', 'direction': 'BUY', 'offset': 'OPEN', 'price': 3540.0, 'volume': 15, 'user_id': 'TQSIM', 'commission': 22.5}",
            str(trd3)
        )
        api.close()

    """
    调仓测试
    账户1 DCE.m2105 多仓 40 手, 目标仓位 30 , 需要平仓 10 手多仓
    账户2 DCE.i2101 多仓 85 手, 目标仓位 80 , 需要平仓 5 手多仓
    账户3 SHFE.rb2012 多仓 2 手, 目标仓位 5 , 需要开仓 3 手多仓
    """
    def test_multi_account_with_lib(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.td_mock1 = MockWebsocketsServer(url="wss://otg-sim.shinnytech.com/trade", account_id="147716")
        self.td_mock2 = MockWebsocketsServer(url="wss://otg-sim.shinnytech.com/trade", account_id="172289")
        self.td_mock3 = MockWebsocketsServer(url="wss://otg-sim.shinnytech.com/trade", account_id="103988")
        self.md_mock.run(os.path.join(dir_path, "log_file", "test_multi_account_with_lib.script.lzma"))
        self.td_mock1.run(os.path.join(dir_path, "log_file", "test_multi_account_with_lib.script.lzma"))
        self.td_mock2.run(os.path.join(dir_path, "log_file", "test_multi_account_with_lib.script.lzma"))
        self.td_mock3.run(os.path.join(dir_path, "log_file", "test_multi_account_with_lib.script.lzma"))
        md_url = f"ws://127.0.0.1:{self.md_mock.port}/"
        td_url1 = f"ws://127.0.0.1:{self.td_mock1.port}/"
        td_url2 = f"ws://127.0.0.1:{self.td_mock2.port}/"
        td_url3 = f"ws://127.0.0.1:{self.td_mock3.port}/"

        account1 = TqAccount("快期模拟", "147716", "123456", td_url=td_url1)
        account2 = TqAccount("快期模拟", "172289", "123456", td_url=td_url2)
        account3 = TqAccount("快期模拟", "103988", "123456", td_url=td_url3)
        account_list = TqMultiAccount([account1, account2, account3])

        utils.RD = random.Random(6)
        api = TqApi(account=account_list, auth="tianqin,tianqin", _md_url=md_url)
        symbol1 = "DCE.m2105"
        symbol2 = "DCE.i2109"
        symbol3 = "SHFE.rb2106"
        position1 = api.get_position(symbol1, account=account1)
        position2 = api.get_position(symbol2, account=account2)
        position3 = api.get_position(symbol3, account=account3)
        self.assertEqual(position1.pos, 5)
        self.assertEqual(position2.pos, 0)
        self.assertEqual(position3.pos, 0)
        api.get_quote(symbol1)
        target_pos1 = TargetPosTask(api, symbol1, account=account1)
        api.get_quote(symbol2)
        target_pos2 = TargetPosTask(api, symbol2, account=account2)
        api.get_quote(symbol3)
        target_pos3 = TargetPosTask(api, symbol3, account=account3)
        target_pos1.set_target_volume(30)
        target_pos2.set_target_volume(80)
        target_pos3.set_target_volume(5)
        while position1.volume_long != 30 or position2.volume_long != 80 or position3.volume_long != 5:
            api.wait_update()

        # 预期持仓数量
        self.assertEqual(position1.pos, 30)
        self.assertEqual(position2.pos, 80)
        self.assertEqual(position3.pos, 5)
        # 预期委托
        ord1 = api.get_order(account=account1)
        ord2 = api.get_order(account=account2)
        ord3 = api.get_order(account=account3)
        self.assertEqual(
            "{'order_id': 'PYSDK_target_181e290aae9af1698a0c510089ce5ef7', 'exchange_order_id': 'PYSDK_target_181e290aae9af1698a0c510089ce5ef7', 'exchange_id': 'DCE', 'instrument_id': 'm2105', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 25, 'volume_left': 0, 'limit_price': 3509.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1619155960790783727, 'last_msg': '', 'status': 'FINISHED', 'seqno': 11, 'user_id': '147716', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(ord1['PYSDK_target_181e290aae9af1698a0c510089ce5ef7'])
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_target_b313fc7e8db9b92c903c2ac9316774fe', 'exchange_order_id': 'PYSDK_target_b313fc7e8db9b92c903c2ac9316774fe', 'exchange_id': 'DCE', 'instrument_id': 'i2109', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 80, 'volume_left': 0, 'limit_price': 1093.5, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1619155960791377436, 'last_msg': '', 'status': 'FINISHED', 'seqno': 11, 'user_id': '172289', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(ord2['PYSDK_target_b313fc7e8db9b92c903c2ac9316774fe'])
        )
        self.assertEqual(
            "{'order_id': 'PYSDK_target_a9b3d1a243f9300cba98666ace1c9c17', 'exchange_order_id': 'PYSDK_target_a9b3d1a243f9300cba98666ace1c9c17', 'exchange_id': 'SHFE', 'instrument_id': 'rb2106', 'direction': 'BUY', 'offset': 'OPEN', 'volume_orign': 5, 'volume_left': 0, 'limit_price': 5140.0, 'price_type': 'LIMIT', 'volume_condition': 'ANY', 'time_condition': 'GFD', 'insert_date_time': 1619155960790117291, 'last_msg': '', 'status': 'FINISHED', 'seqno': 9, 'user_id': '103988', 'frozen_margin': 0.0, 'frozen_premium': 0.0, 'frozen_commission': 0.0}",
            str(ord3['PYSDK_target_a9b3d1a243f9300cba98666ace1c9c17'])
        )
        api.close()
