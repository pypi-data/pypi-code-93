"""

套利程序的模块总览:
    1. 币安网关模块 (用于币安交易所的api交互)
    2. 价差率模块:
        i. 数据获取
        ii. 计算价差率
    3. 下单模块 (在合适的价差快速下单)



redis数据库的结构:
    r0: [存储盘口挂单数据]
        5种类型的数据:
            1. asset的'现货'盘口数据
            2. asset的'u本位合约'盘口数据
            3. asset的'币本位合约'盘口数据
            4. asset的'u本位合约'资金费率 # 键名'fBTCUSDT'
            5. asset的'溢价指数' # 键名'pXLMUSDT'
        格式:
            "DGBUSDT_PERP" : {
                'bid_price': '1.56778',
                'bid_volume': '100',
                'ask_price': '1.56882',
                'ask_volume': '59',
                'server_timestamp': '1623684133589',
                'receiver_timestamp': '1623684262.171096'
                }
            "pXLMUSDT" : {
                'open_price': '0',
                'close_price': '0',
                'high_price': '0',
                'low_price': '0',
                'server_timestamp': '1623684260444',
                'receiver_timestamp': '1623684260.358463'
            }


    r1: [存储价差率数据]
        格式:
            'ALPHAUSDT/ALPHAUSDT_PERP': {
                'open_spread_rate': '-0.00015926102882622868',
                'close_spread_rate': '0.0014342629482071904',
                'left_server_timestamp': '1623684256.722812',
                'right_server_timestamp': '1623684251.787067',
                'deltaTime_server': '4.935745000839233',
                }

    测试案例:
        r0.hgetall("1INCHUSDT")
        r1.hgetall("ALPHAUSDT/ALPHAUSDT_PERP")










资金费率套利的一些重要结论:

    1. 同样的合约杠杆, 合约持仓市值越大, 显示的保证金率越高!
        (所以, 保证金率并不是完全等价于该账户的'爆仓涨幅')









"""
