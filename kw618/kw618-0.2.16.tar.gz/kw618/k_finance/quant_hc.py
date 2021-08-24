import json
import pandas as pd


# 导入常用的固定路径(多平台通用)
from kw618._file_path import *
# 本脚本依赖很多 utils_requests的函数和模块, 直接用*  (注意要避免循环导入问题)
from kw618.k_requests.utils_requests import *
from kw618.k_requests.ocr import *
from kw618.k_python.utils_python import *
from kw618.k_pandas.utils_pandas import *
from kw618.k_finance.utils_quant import *
from kw618.k_finance.quant_strategy import *

from kw618.k_finance.const import A_Zqmc_lst, ETF_Zqmc_lst


# 1. A
Zqdm_A_lst = [
    # "600900", "600031", "601318",
    "000651",
    "002415", "002230", "002168", "002142", "002505",
]

# 2. ETF
Zqdm_ETF_lst = [
    # "515030", "512600", "512330", "512810", "512610", "510300",
    # "515070", "512690", "510500", "512290", "515000", "510050",
    "159995", "159913", "159905", "159916", "159915",
]


class HC():
    """
        function: 专门用于"批量回测"的类 (便于筛选出最优质的'策略'/'策略参数'/日期/天数)
    """


    def __init__(self, Zqmc_lst=[]):
        """
            function: 初始化一些基础的通用参数 (即: 每个策略都需要去测试的参数)
        """

        # 1. 筛选需要回测的 'Zqdm代码'
        if len(Zqmc_lst) == 0:
            # 默认回测所有'自选股' (来自于'const.py')
            A_Zqdm_lst = Q.Zqmc_to_Zqdm(Zqmc_lst=A_Zqmc_lst)
            ETF_Zqdm_lst = Q.Zqmc_to_Zqdm(Zqmc_lst=ETF_Zqmc_lst)
            self.Zqdm_lst = A_Zqdm_lst + ETF_Zqdm_lst
        elif len(Zqmc_lst) >= 0:
            self.Zqdm_lst = Q.Zqmc_to_Zqdm(Zqmc_lst=Zqmc_lst)

        # 2. 选择 "回测天数"
        # self.selected_days_lst = [100, 200]
        self.selected_days_lst = [100, 200, 300, 500]

        # 3. 选择 回测开始日期
        # self.start_date_lst = ["2015-06-01", "2015-06-16", "2015-06-25"] # 15年高点的'前/中/后'
        # self.start_date_lst = ["2016-06-01", "2016-06-16", "2016-06-25"] # 换个16年份看下结果
        # self.start_date_lst = ["2018-06-01", "2018-06-16", "2018-06-25"] # 换个18年份看下结果
        self.start_date_lst = ["2017-01-01", "2018-01-01", "2019-01-01", "2020-01-01"] # 各个年份的作为初始基准节点的区别
        # self.start_date_lst = ["2019-12-01", "2020-02-01", "2020-04-01", "2020-05-15"] # 疫情前/发展期/爆发中/稳定期

        # 4. 初始化一些账户信息
        self.init_cash_balance = 100000

        # 5. [策略列表]: 策略相关的详细信息 (组合投资)
        self.strategy_lst = [
            {
                "strategy" : DoubleMovingAverage, "capital_percentage" : 0.3, "args_dic":{
                    "selected_avg" : ["5v10", "5v20", "5v30", "10v30"],
                }
            },
            {
                "strategy" : StopLoss, "capital_percentage" : 0.7, "args_dic":{
                    "first_percentage" : [0.03, 0.05, 0.1],
                    "stoploss_rate" : [0.03, 0.05, 0.08, 0.1],
                    # "first_percentage" : [0.05],
                    # "stoploss_rate" : [0.05],
                }
            },
        ]


    @staticmethod
    def _get_kwargs_lst(d):
        "递归方式, 获取到所有'策略参数-键值对'"
        k, lst = d.popitem()
        _ = []
        for i in lst:
            target_d = {k:i}
            if len(d)>0:
                d_lst = HC._get_kwargs_lst(deepcopy(d))
                for dic in d_lst:
                    target_d.update(dic)
                    _.append(deepcopy(target_d))
            else:
                _.append(target_d)
        return _






    def score_df(self, extended_dim_lst=[]):
        """
            function: 通过对各个'参数维度'的透视, 得到更优质的'策略超参数' (是对ROA_df更进一步的汇总)


            分析结果洞察:
                A. 双均线:
                    1. "5v20"/ "200 days"/ "2018-10-08" 是最佳参数
                    2. ETF 需要波动性较大的板块, 才更适合高频交易
                    3. 目前来看: 深价值(159913), 信息技术ETF(512330)  适合'等待低位捕获'

                    最佳参数:
                        selected_avg: 10v30 > 5v30 > 5v20 > 5v10
                        selected_days: 200 > 300 > 100
                        start_date: 18年10月 > 17年01月 > 17年10月

                    收益最佳证券:
                        深50ETF:
                        主要消费ETF
                        消费ETF
                        深红利
                        深价值
                        100ETF
                B. 止损:
                    1. 开始日期:
                        2017 > 2019 > 2020 > 2018  (2018为0.97, 即:亏钱)
                        (很多时候, 策略能不能赚钱并不取决于你的策略写的多牛逼, 而是这个市场在赏你饭吃....)
                    2. 策略选择:
                        双均线 > 止损  # (不管是A股还是ETF, 双均线的策略的整体收益都大于止损) (但止损策略的核心卖点是:虽然赚的不多,基本不会亏钱!)
                    3. 持仓天数:
                        200 > 100 (持仓时间越久, 翻盘机会就越大!!)
                    4. 策略参数:
                        i. stoploss_rate:
                            0.03 > 0.05 > 0.1 > 0.08


        """

        # '与指数ROA差距'的透视表
        self.index_pivot_df = self.ROA_df.pivot_table(index="Zqmc", aggfunc={"vs_001":"mean", "vs_300":"mean", "vs_500":"mean"})

        # 汇总/分析'回测结果', 得到'最佳策略&参数'
        # dim_lst = ["策略", "选择天数", "start_date"]
        dim_lst = ["策略", "选择天数", "start_date", "selected_avg", "first_percentage", "stoploss_rate"]
        dim_lst.extend(extended_dim_lst)

        best_arg_dict = {} # 专门用于存放'最佳参数'
        pivot_df_lst = []
        print("\n\n\n")
        for dim in dim_lst:
            pivot_df = self.ROA_df[["Zqmc", "ROA", dim]].pivot_table(
                index="Zqmc", aggfunc={"ROA":"mean"},
                columns=dim, margins=True,
            )
            pivot_df = pivot_df.sort_values(('ROA', 'All'), ascending=False)
            # 当被回测的Zqdm数量大于50时, 需要再底部再添加一行'All' (便于观察)
            if len(pivot_df) > 50:
                pivot_df = pivot_df.append(pivot_df.query("Zqmc=='All'"))
            pivot_df = pd.merge(pivot_df, self.index_pivot_df, how="left", on="Zqmc")
            print(pivot_df, "\n")
            pivot_df_lst.append(pivot_df)
            best_arg = pivot_df.T.sort_values("All", ascending=False).iloc[0].name[1]
            best_arg_dict.update({dim : best_arg})

        kprint(best_arg_dict=best_arg_dict)
        return pivot_df_lst




    def run(self, strategy_lst=[]):
        """
            主运行程序
        """
        if len(strategy_lst) > 0:
            self.strategy_lst = strategy_lst

        # 存放每次回测模型跑完的账户资产结果
        all_asset_dict_lst = []

        # I.循环各个'策略超参数' (寻找最优质的参数)
        # 1. 从'策略列表'中得到每个策略的详细信息
        for strategy_info in self.strategy_lst:
            # 每个策略的投入资金占比
            capital_percentage = strategy_info.get("capital_percentage")
            # 策略类型
            STRATEGY = strategy_info.get("strategy")
            # 具体策略的'详细策略参数字典' (针对不同的策略设置不同的参数)
            args_dic = strategy_info.get("args_dic")
            print("\n\n---------", args_dic)
            # [递归方法]: 获得所有排列组合情况的'策略参数-键值对'
            kwargs_lst = HC._get_kwargs_lst(args_dic)
            # 2. 取出每一个Zqdm
            for Zqdm in self.Zqdm_lst:
                # 策略实例对象 (实例化操作前置, run操作后置: 可以节省频繁实例化的资源开销)
                strategy_inst = STRATEGY(Zqdm=Zqdm, init_cash_balance=self.init_cash_balance*capital_percentage)
                # 3. 循环不同的"回测天数"
                for days in self.selected_days_lst:
                    # 4. 循环不同的"回测开始日期"
                    for start_date in self.start_date_lst:
                        # 5. 循环不同的"策略参数的排列组合"
                        for kwargs in kwargs_lst:
                            asset_dict = strategy_inst.run(selected_days=days, start_date=start_date, **kwargs, pt=False)
                            all_asset_dict_lst.append(asset_dict)

        # II.构造成df后, 排序 (呈现形式更加美观!)
        df = pd.DataFrame(all_asset_dict_lst)
        df = df.query("net_capital_value == net_capital_value") # 剔除 net_capital_value 为空的数据
        ordered_field_lst = [
            "Zqmc", "strategy_name", "net_capital_value", "ROA", "vs_001", "vs_300", "vs_500",
            "selected_days", "launch_date", "start_date", "end_date",
            "sell_times", "cash_balance", "today_market_value",
            "selected_avg",
            "first_percentage", "stoploss_rate"
        ]
        df = sort_df(df=df, ordered_field_lst=ordered_field_lst)
        self.ROA_df = df.sort_values("ROA", ascending=False)
        rename_dict = {
            "strategy_name":"策略", "net_capital_value":"净资本",
            "selected_days":"选择天数", "launch_date":"上市日期", "cash_balance":"现金余额",
            "today_market_value":"最新市值"
        }
        self.ROA_df.rename(columns=rename_dict, inplace=True)
        print(self.ROA_df)

        # III. 评分(得出"最优参数")
        self.score_df()

        return self.ROA_df












def main():

    # 回测实例1
    # ===============================
    # hc = HC()
    # ROA_df = hc.run()
    # pivot_df_lst = hc.score_df()
    # print(pivot_df_lst)



    # 回测实例2
    # ===============================
    Zqmc_lst = [
        "宁波银行",
    ]
    hc = HC(Zqmc_lst=Zqmc_lst)
    ROA_df = hc.run()







if __name__ == '__main__':
    print("Start test!\n\n")
    main()
    print("\n\n\nIt's over!")
