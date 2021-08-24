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
from kw618.k_finance.const import ulist_change_name_dict

req = myRequest().req
client = pymongo.MongoClient(f'mongodb://kerwin:kw618@{HOST}:27017/')
db_for_quant = client["quant"]







# 原始模型类
class OrgModel():
    """
        hc模型中, 暂时只允许每次只hc一个stock;
        跑sp的时候, 只要给每个stock一定的初始cash_balance即可

        note:
            1. <<每日数据处理>>的流程:
                i. do_every_morning
                ii. 买卖点操作
                iii. do_every_evening
                (一定要搞清楚某个活儿是归属于哪个节点操作的!! )

    """

    def __init__(self, stock_code="", Zqdm="", init_cash_balance=100000):
        """
            params:
                init_cash_balance: 初始账户余额

            notice:
                1. 初始化时, Zqdm和stock_code 二选其一, 就可以实现初始化.

        """
        # 1. 初始化'静态'数据
        self.init_cash_balance = init_cash_balance # 记录一个初始启动资金(固定)
        self.cash_balance = self.init_cash_balance # 后面动态更新的余额
        if stock_code:
            self.stock_code = stock_code
            self.Zqdm = Q._StockCode_to_Zqdm(stock_code_lst=[self.stock_code])[0]
        elif Zqdm:
            self.Zqdm = Zqdm
            self.stock_code = Q._Zqdm_to_StockCode(Zqdm_lst=[self.Zqdm])[0]
        else:
            raise Exception("代码输入错误, 初始化未成功!!\n")
        self.Zqmc = Q._Zqdm_to_Zqmc(Zqdm_lst=[self.Zqdm])[0]
        self.f1 = Q._Zqdm_to_f1(Zqdm_lst=[self.Zqdm])[0] # 2:A股; 3:ETF基金;  (后期可用于计算交易费的佣金差异)
        self.sxf_rate = 0.00018 # 手续费率按'万1.8'来计算
        self.ETF_fee_rate = 0.006/365 # 托管费率按 '一年千6' 来计算 (托管费每日计提, 无需在每笔交易中另行支付) (貌似只有在及哦啊一日才会生成)
        self.strategy_name = "原型" # "OrgModel"

        # 2. 读取mongo中的历史'日K'数据的df
            # (每个实例都需要获取新的'日K'数据) (后面跑策略依赖这里的'日K'数据!!)
        # whole_hist_df = read_mongo(db_for_quant["hist_allstock"], {"stock_code":self.stock_code})
        whole_hist_df = read_mongo(db_for_quant["hist_zxstock"], {"stock_code":self.stock_code}) # 从hist_zxstock表中获取!! (提高读取性能)

        # 3. 数据预处理 (得到双均线的差值)
        # whole_hist_df["_num"] = np.arange(1, len(whole_hist_df)+1) # 新建一个'顺序序列' (但是需要在init_data函数中操作此步骤)
        whole_hist_df["5v30"] = whole_hist_df["5d_avg"] - whole_hist_df["30d_avg"]
        whole_hist_df["5v20"] = whole_hist_df["5d_avg"] - whole_hist_df["20d_avg"]
        whole_hist_df["5v10"] = whole_hist_df["5d_avg"] - whole_hist_df["10d_avg"]
        whole_hist_df["10v30"] = whole_hist_df["10d_avg"] - whole_hist_df["30d_avg"]
        self.whole_hist_df = whole_hist_df # 所有完整的历史数据
        self.launch_date = self.whole_hist_df.iloc[0]["market_date"] # 上市日期

        # 4. 读取3个主要的指数数据 (一般回测时候也不会选取14年以前的远古数据, 所以为了提高数据获取的性能, 直读取14年后的数据)
            # i. 上证指数
        self.whole_index_001_df = read_mongo(db_for_quant["hist_index"], {"Zqdm":"000001", "market_date":{"$gte":"2014-01-01"}})
            # ii. 沪深300
        self.whole_index_300_df = read_mongo(db_for_quant["hist_index"], {"Zqdm":"000300", "market_date":{"$gte":"2014-01-01"}})
            # iii. 中证500
        self.whole_index_500_df = read_mongo(db_for_quant["hist_index"], {"Zqdm":"000905", "market_date":{"$gte":"2014-01-01"}})

        # 5. 初始化'动态'数据
        self.init_data()


    def init_data(self, selected_days=99999, start_date=None, end_date=None, pt=False):
        """
            function: 用于后面重复执行run方法时候使用的'初始化'方法 (区别于__init__)
                    步骤:
                        1. 筛选回测日期
                        2. 初始化'通用型变量'
                        3. 执行'do_every_evening'的汇总函数
                        4. 初始化'针对型变量'
            params:
                selected_days: 筛选的天数  (99999代表: 取所有日期)
        """

        # 1. 筛选回测日期 (得到query_set)
        # =============================
            # i. 若给了一个start_date和一个selected_days: 从开始日期向后取xx天
            # ii. 若给了一个end_date和一个selected_days: 从截止日期向前取xx天
        if start_date is not None:
                # 如果开始日期早于'上市日期', 则把'上市日期'作为'开始日期'
            if start_date < self.launch_date:
                start_date = self.launch_date # 覆盖它
            if end_date:
                pass
            else:
                end_date = get_later_date(start_date, f"{selected_days} days")
        elif start_date is None:
            if end_date:
                    # 如果结束日期晚于'今天最新日期', 则把'今天日期'作为'结束日期'
                if end_date > get_today_date():
                    end_date = get_today_date() # 覆盖它
                start_date = get_previous_date(end_date, f"{selected_days} days")
            else:
                end_date = get_today_date()
                start_date = get_previous_date(end_date, f"{selected_days} days")

            # 重新验证一遍:
            # 如果开始日期早于'上市日期', 则把'上市日期'作为'开始日期'
        if start_date < self.launch_date:
            start_date = self.launch_date # 覆盖它
            # 如果结束日期晚于'今天最新日期', 则把'今天日期'作为'结束日期'
        if end_date > get_today_date():
            end_date = get_today_date() # 覆盖它
        query_set = f"'{start_date}' <= market_date <= '{end_date}'"
        self.hist_df = self.whole_hist_df.query(query_set)
        self.hist_df["_num"] = np.arange(1, len(self.hist_df)+1) # 新建一个'顺序序列'
        self.selected_days = get_delta_days(start_date=start_date, end_date=end_date)
        self.start_date = start_date
        self.end_date = end_date

            # 把指数也截取到相应的日期范围
        self.index_001_df = self.whole_index_001_df.query(query_set)
        self.index_300_df = self.whole_index_300_df.query(query_set)
        self.index_500_df = self.whole_index_500_df.query(query_set)
            # 每个指数的ROA (个股策略的ROA与大盘指数相比, 才能看出策略是否成功)
        self.index_001_ROA = round(self.index_001_df["end_price"].iloc[-1] / self.index_001_df["end_price"].iloc[0], 4)
        self.index_300_ROA = round(self.index_300_df["end_price"].iloc[-1] / self.index_300_df["end_price"].iloc[0], 4)
        self.index_500_ROA = round(self.index_500_df["end_price"].iloc[-1] / self.index_500_df["end_price"].iloc[0], 4)

        # 2. 初始化'通用型变量':
        # =============================
            # 1. 现金流&开平仓数流
                # (有方向): 历次buying&selling的价格/股数
                # 负数:表示买入该stock; 正数:表示卖出该stock (因为最终统计的是现金的剩余量)
        self.cash_flow_lst = []
        self.deal_count_flag = []
            # 2. 持仓股票数
        self.chicang_stock_count = 0
            # 3. 平均成本价
        self.avg_cost_price = 0
        self.cost_market_value = 0
        self.market_value_percentage = 0 # 市值占比 = 持仓股市值/总资本
        self.market_value_percentage_lst = [] # 每天的'市值占比'记录
            # 4. 初始化余额 [临时]
        self.cash_balance = self.init_cash_balance
            # 5. 交易次数
        self.buy_times = 0
        self.sell_times = 0
        self.bucang_times = 0 # 补仓次数
        self.buy_day_lst = []
        self.sell_day_lst = []
        self.deal_day_lst = [] # 每次交易操作时, 距离上次操作的天数 (不管是买,还是卖)
            # 6. 是否打印(必要的节点信息)
        self.pt = pt
            # 7. 盈亏比例
        self.LjYkbl = np.nan
        self.DrYkbl = np.nan
            # 8. 最新价格
                # 截取到的时间段内最新一天的价格
        if len(self.hist_df) > 0:
            self.newest_date = self.hist_df.iloc[-1]["market_date"]
            self.newest_price = self.hist_df.iloc[-1]["end_price"] # i. 这个hist_df中的最新价格
            self.today_date = self.newest_date
            self.today_price = self.newest_price # ii. apply函数中循环读取的'每天价格' (初始化时, 暂时用'最新价格'代替)
            # 9. ETF的费用计算 (与A股不同, 所以需要单独初始化处理)
        self.ETF_today_fee = 0
        self.ETF_fee_lst = []
        self.ETF_total_fee = 0
            # 10. 近期的'最高值'/'最低值'
        if len(self.hist_df) > 0:
            self.min_market_price = self.hist_df.iloc[0]["end_price"] # 初始化时, 暂时用'第一天的价格'代替
            self.max_market_price = self.min_market_price # 初始化时, 暂时用'第一天的价格'代替


        # 3. 执行'do_every_evening'的汇总函数:
        # =============================
        self.do_every_evening()

        # 4. 初始化'针对型变量':
        # =============================
            # 具体策略中需要用到的初始化变量
            # 1. 双均线策略:
                # 上一天的'长短线差值'
        self.last_diff_score = np.nan

            # 2. 止损策略:
                # 累计涨幅:
                    # 用于计算每天的累计涨幅 (是市场的实盘涨幅, 与上面LjYkbl的个人涨幅无关)
                    # (每天append进'最新的累计涨幅')
                # 1. "市场"累计盈亏
        self.MarketLjYk = 0.0  # 这是指"市场上"的"累计盈亏" (区别于: "自己账户"的"LjYk")
        self.MarketLjYkbl = 0.0  # 这是指"市场上"的"累计盈亏比例" (区别于: "自己账户"的"LjYkbl")
        self.MarketLjYk_lst = []
        self.MarketLjYkbl_lst = []
        self.vs_max_market_price_bl = 0.0
        self.vs_min_market_price_bl = 0.0
                # 2. "个人"累计盈亏
        self.MyLjYk = 0.0  # 这是指"个人账户"的"累计盈亏" (区别于: "市场"的"LjYk")
        self.MyLjYkbl = 0.0  # 这是指"个人账户"的"累计盈亏比例" (区别于: "市场"的"LjYkbl")
        self.MyLjYk_lst = []
        self.MyLjYkbl_lst = []



    def do_every_morning(self, doc):
        """
            function: 每天早上记录必要的数据
                    (因为不管哪个策略都需要有这一步, 所以把它抽离出来)

            params:
                doc: apply函数中的doc  (也就是self.hist_df中的每一行)


        """

        # 1. 记录 "当天" 的 "日K" 数据
        self.today_date = doc.get("market_date") # 每天实时更新'最新价格'
        self.today_price = doc.get("end_price")
        self.today_days = doc.get("_num") # 得到今天距离'基准日期'的天数
        self.DrYkbl = round(doc.get("growth_rate"), 4) # 每天实时更新'当日盈亏比例'
        self.DrYk = round(doc.get("growth_amount"), 4) # 每天实时更新'当日盈亏'
        if np.isnan(self.DrYkbl) == True: # 如果DrYkbl是空值, 默认用0来填充
            self.DrYkbl = 0.0
        if np.isnan(self.DrYk) == True: # 如果DrYkbl是空值, 默认用0来填充
            self.DrYk = 0.0

        # 2. 记录"市场上"的累计数据
        self.MarketLjYk += self.DrYk # 每天累加
        self.MarketLjYkbl += self.DrYkbl # 每天累加
        self.MarketLjYk = round(self.MarketLjYk, 4)
        self.MarketLjYkbl = round(self.MarketLjYkbl, 4)
        self.MarketLjYk_lst.append(self.MarketLjYk)
        self.MarketLjYkbl_lst.append(self.MarketLjYkbl)

        # 3. 记录"vs近期最值"的涨跌幅度 ([逻辑正确]: 更新'最值'应该放在晚上操作; 计算'与最值的幅度'应该放在早上操作:便于盘中买卖操作)
        self.vs_max_market_price = self.today_price - self.max_market_price # "今日vs近期最高值"的差值
        self.vs_max_market_price_bl = round(self.vs_max_market_price / self.max_market_price, 4) # "今日vs近期最高值"的涨跌幅
        self.vs_min_market_price = self.today_price - self.min_market_price
        self.vs_min_market_price_bl = round(self.vs_min_market_price / self.min_market_price, 4)

        # 4. 记录"个人账户"的累计数据
        if (self.avg_cost_price != 0) and (self.chicang_stock_count != 0):
            self.MyLjYk = round(self.today_price - self.avg_cost_price, 4) # 个人账户的'累计盈亏'的计算方式: 直接用 "最新价格 - 成本均价"
            self.MyLjYkbl = round(self.MyLjYk / self.avg_cost_price, 4)
        elif (self.avg_cost_price == 0) or (self.chicang_stock_count == 0):
            self.MyLjYk = 0.0
            self.MyLjYkbl = 0.0
        self.MyLjYk_lst.append(self.MyLjYk)
        self.MyLjYkbl_lst.append(self.MyLjYkbl)

        # 4. 打印
        if self.pt == True:
            print("\n\n\n[早报]:")
            print(f"    {self.today_date}: 今天是第{self.today_days}个交易日, 股价:{self.today_price}元, 当日盈亏比例:{self.DrYkbl}, 当日盈亏:{self.DrYk}")
            print(f"    平均成本价:{round(self.avg_cost_price, 2)}")
            print(f"    市场累计盈亏:{self.MarketLjYk}, 市场累计盈亏比例:{self.MarketLjYkbl}")
            print(f"    个人账户累计盈亏:{self.MyLjYk}, 个人账户累计盈亏比例:{self.MyLjYkbl}")
            print(f"    今日vs近期最低值幅度:{self.vs_min_market_price_bl}, 今日vs近期最高值幅度:{self.vs_max_market_price_bl}")



    def do_every_evening(self):
        """
            function: 每天晚上记录必要的数据 (一般是受今日交易数据所影响的数据)
                        (相当于对今天数据的汇总)

            params:
                无: 不依赖于doc, 所以也可以放在 init_data()方法 中执行


        """

        # 1. 计算当前持仓股票的'成本市值'
            # 成本市值: 指持有的这些股票共'花了多少钱','最新市值'要大于它才算有利润!
        self.cost_market_value = self.chicang_stock_count * self.avg_cost_price
        # 2. 计算当前持仓股票的'今日市值'
            # i. A股直接相乘就是'今日市值'
        self.today_market_value = self.chicang_stock_count * self.today_price
            # ii. ETF需要在'今日市值'中计提每日的管托费
        if self.f1 == 3:
            self.ETF_today_fee = self.today_market_value * self.ETF_fee_rate
            self.ETF_fee_lst.append(self.ETF_today_fee)
            self.ETF_today_fee = sum(self.ETF_fee_lst)
            self.today_market_value -= self.ETF_total_fee

        # 3. 现金流汇总
        self.sum_cash_flow = sum(self.cash_flow_lst)
        # 4. 开平仓数流汇总
        self.sum_deal_count_flag = sum(self.deal_count_flag)
            # 持有A股, 如果要卖出的话, 需要多少手续费? (ETF直接返回0)
        self.chicang_stock_deal_fee = self.get_commission_fee(
            Mmlb="S", deal_price=self.today_price, deal_count=abs(self.sum_deal_count_flag),
        )

        # 5. 今天的"总资产"
        self.total_capital_value = self.cash_balance + self.today_market_value
        # 6. 今天的"净资产" (已扣除今天持仓的交易成本) (即:假设今天把持有的股票全卖了, 账户总资产是多少?)
        self.net_capital_value = round(self.total_capital_value - self.chicang_stock_deal_fee, 0)
        # 7. 今天的"市值占比"
        self.market_value_percentage = self.today_market_value / self.total_capital_value
        self.market_value_percentage_lst.append(self.market_value_percentage)

        # 8. 记录比较'最高/最低价格' ([逻辑正确]: 更新'最值'应该放在晚上操作)
        if self.today_price > self.max_market_price:
            self.max_market_price = self.today_price
        elif self.today_price < self.min_market_price:
            self.min_market_price = self.today_price

        # 9. 打印
        if self.pt == True:
            print("[晚报]:")
            print(f"    近期最低值:{self.min_market_price}, 近期最高值:{self.max_market_price}")



    def get_round_count(self, expected_buying_count=2235, min_count=0, max_count=999999, round_type="round"):
        """
            function: 输入'预期买入股数', 计算出整手的'可买入股数'
            params:
                # stock_price: 股票单价
                # expected_buying_amount: 期望的"买入金额"

                expected_buying_count: 期望的"买入股数"
                min_count: 最低买入股数 (默认设为0, 即:没有最低限制;    也可以设为100股(1手))
                max_count: 最大买入股数 (默认为999999, 即:没有最大限制; 也可设为1000股(10手))
                    (当min_count>max_count这种逻辑错误时, 以max_count为准)
                round_type: 近似的3种方式:
                                1. round (就近)
                                2. down  (向下取整)
                                3. up    (向上取整)
            return:
                整'手'的买入股数  (eg: 100,200,500,1000)
        """

        if round_type == "round":
            round_buying_count = min(max(round(expected_buying_count, -2), min_count), max_count)
        elif round_type == "down":
            round_buying_count = min(max(expected_buying_count//100*100, min_count), max_count)
        elif round_type == "up":
            round_buying_count = min(max(math.ceil(expected_buying_count/100)*100, min_count), max_count)
        return round_buying_count



    def get_commission_fee(self, Mmlb, deal_price, deal_count):
        """
            params:
                Mmlb: 买卖类别  # "B" / "S"
                deal_price: 交易单价 (一股的价格)
                deal_count: 交易数量
        """

        if deal_count > 0:
            # 会产生手续费
                # 1. A股的手续费
            if self.f1 == 2:
                sxf = max(self.sxf_rate*(deal_price*deal_count), 5.0)

                if Mmlb == "B":
                    total_fee = sxf
                elif Mmlb == "S":
                    yhs = 0.001*(deal_price*deal_count) # 印花税都是'千分之一'的
                    sxf = 5.0
                    total_fee = yhs + sxf

                return total_fee

                # 2. ETF的手续费
            elif self.f1 == 3:
                return 0 # ETF的托管费是'每日计提'的, 所以不再在每笔交易中另外产生
        else:
            return 0


    def buying(self, buying_price, buying_count):
        # 1. 得到真实的所有'买入成本' (包含所有手续费)
        max_available_count = self.cash_balance // buying_price * 100 # 最大可购买股数
        buying_count = self.get_round_count(expected_buying_count=buying_count, min_count=0, max_count=max_available_count, round_type="round")
        commission_fee = self.get_commission_fee(
            Mmlb="B", deal_price=buying_price, deal_count=buying_count,
        )
        all_buying_cost = buying_price*buying_count + commission_fee # 真实股票市值成本 = 股票成本市值 + 所有的交易手续费

        # 2. [极其偶然情况]: 当购买金额加上手续费后超过了剩余现金 (需要扣除一部分的'买入股数')
        if self.cash_balance < all_buying_cost:
            # 减掉一部分的'买入股数'
            buying_count -= self.get_round_count(expected_buying_count=commission_fee/buying_price, min_count=100, round_type="up")
            commission_fee = self.get_commission_fee(
                Mmlb="B", deal_price=buying_price, deal_count=buying_count,
            )
            all_buying_cost = buying_price*buying_count + commission_fee # 真实股票市值成本 = 股票成本市值 + 所有的交易手续费

        # 3. 只有当现金余额>=待购入股票金额, 才能真的执行'买的操作' (否则就是逻辑bug)
        if (self.cash_balance >= all_buying_cost) and (buying_count != 0):
            # 1. '现金余额'减少
            self.cash_balance -= all_buying_cost
            # 2. '持仓股数'增加
                # (old_cost_market_value 需要在'持仓数量'增加之前计算)
            old_cost_market_value = self.chicang_stock_count * self.avg_cost_price
            self.chicang_stock_count += buying_count
            # 3. '现金流'&'开平仓数流'记录
                # 1. 负现金流: 表示买入'xxx元'的stock
            self.cash_flow_lst.append(-1 * all_buying_cost)
                # 2. 负开平仓数流: 表示买入'xxx股'的stock
            self.deal_count_flag.append(-1 * buying_count)
            # 4. 每次"买入交易"都需要重新计算'平均成本价'  ('卖出交易'不影响平均成本, 只要减去'持仓数量', 计算出来的'成本市值'就会跟着减少了)
                # (成本市值的统计是'无意义'的, 都是动态的用 当前'平均成本价*持仓数量' 计算得到的)
            new_cost_market_value = all_buying_cost
            self.avg_cost_price = (old_cost_market_value + new_cost_market_value) / self.chicang_stock_count
            # 5. '买入次数' +1
            self.buy_times += 1
            # 6. '距离上次买入天数' 添加进 buy_day_lst 中
            self.buy_day_lst.append(self.today_days-sum(self.buy_day_lst))
            # 7. '距离上次交易天数' 添加进 deal_day_lst 中
            self.deal_day_lst.append(self.today_days-sum(self.deal_day_lst))
            # if self.pt == True:
            # 必打印 (买卖节点比较重要)
            print("="*100)
            print(f"【买卖点】=========> [{self.today_date}] ======> 买入股票:{buying_count}股, 单价{buying_price}元, 成本市值:{all_buying_cost}")
            print("="*100)



    def selling(self, selling_price, selling_count):

        # 1. 得到真实的卖出后的'到手现金' (已经扣除所有手续费)
        selling_count = self.get_round_count(expected_buying_count=selling_count, min_count=0, max_count=self.chicang_stock_count, round_type="round")
        commission_fee = self.get_commission_fee(
            Mmlb="S", deal_price=selling_price, deal_count=selling_count,
        )
        all_selling_cash = selling_price * selling_count - commission_fee # 到手现金 = 股票卖出价 - 所有的交易手续费

        # 2. 只有当自己的持仓股数大于你要卖的股数时, 才能真的执行'卖的操作' (否则就是逻辑bug)
        if (self.chicang_stock_count >= selling_count) and (selling_count != 0):
            # 1. '现金余额'增加
            self.cash_balance = round(self.cash_balance + all_selling_cash, 0)
            # 2. '持仓股数'减少
            self.chicang_stock_count -= selling_count
            # 3. '现金流'&'开平仓数流'记录
                # 1. 正现金流: 表示卖出'xxx元'的stock
            self.cash_flow_lst.append(1 * all_selling_cash)
                # 2. 正开平仓数流: 表示卖出'xxx股'的stock
            self.deal_count_flag.append(1 * selling_count)
            # 4. '卖出交易'一般不会影响到成本价 (但当全部卖出时, 逻辑上就没有成本价的概念了..)
            if self.chicang_stock_count == 0:
                self.avg_cost_price = 0
            # 5. '卖出次数' +1
            self.sell_times += 1
            # 6. '距离上次卖出天数' 添加进 sell_day_lst 中
            self.sell_day_lst.append(self.today_days-sum(self.sell_day_lst))
            # 7. '距离上次交易天数' 添加进 deal_day_lst 中
            self.deal_day_lst.append(self.today_days-sum(self.deal_day_lst))
            # if self.pt == True:
            # 必打印 (买卖节点比较重要)
            print("="*100)
            print(f"【买卖点】=========> [{self.today_date}] ======> 卖出股票:{selling_count}股, 单价{selling_price}元, 到手现金:{all_selling_cash}")
            print("="*100)


    def return_asset_dict(self):

        # 1. 打印账户整体的资金状况
        print(" ⏬ ⏬" * 15)
        # print(" ↓ ↓ ↓" * 15)
        if self.pt == True:
            sprint(cash_balance=self.cash_balance)
            sprint(today_market_value=self.today_market_value)
            sprint(net_capital_value=self.net_capital_value)
            print("=="*50)
            print("=="*50)

        # 2. '账户资产'相关信息
        self.ROA = round(self.net_capital_value / self.init_cash_balance, 4)
        asset_dict = {
            "strategy_name" : self.strategy_name,
            "net_capital_value" : self.net_capital_value,
            # "all_arg_msg" : self.all_arg_msg,
            # "stock_code" : self.stock_code,
            # "Zqdm" : self.Zqdm,
            "Zqmc" : self.Zqmc,
            "selected_days" : self.selected_days,
            "launch_date" : self.launch_date,
            "start_date" : self.start_date,
            "end_date" : self.end_date,
            # "sell_day_lst" : self.sell_day_lst,
            "sell_times" : self.sell_times,
            # "cash_flow_lst" : self.cash_flow_lst,
            # "sum_cash_flow" : self.sum_cash_flow,
            "cash_balance" : int(self.cash_balance),
            "today_market_value" : self.today_market_value,
            "成本价" : self.avg_cost_price,
            "最新价" : self.today_price,
            "ROA" : self.ROA,
            "vs_001" : round(self.ROA - self.index_001_ROA, 4),
            "vs_300" : round(self.ROA - self.index_300_ROA, 4),
            "vs_500" : round(self.ROA - self.index_500_ROA, 4),
            "selected_avg" : self.selected_avg if "selected_avg" in dir(self) else None,
            "first_percentage" : self.first_percentage if "first_percentage" in dir(self) else None,
            "stoploss_rate" : self.stoploss_rate if "stoploss_rate" in dir(self) else None,
        }
        print(asset_dict)
        print("\n\n\n")

        return asset_dict


    def strategy_cal(self, doc):
        """
            function: 策略计算的主函数 (最主要的"计算模块") [apply函数]
        """
        # 1. 每早:获取必要数据
        self.do_every_morning(doc) # 每个策略都需要更新的'每日数据'

        # 2. 策略的主要内容 (买卖点都是指: 尾盘15:00时候发生的)
        # ====================================================
        # ====================================================
        #     # 1. 金叉: (昨天<0, 今天>0): 需要 buying it
        # if today_diff_score>0 and self.last_diff_score<=0:
        #     buying_count = self.cash_balance // self.today_price # [暂时设定] (待优化)
        #     self.buying(buying_price=self.today_price, buying_count=buying_count)
        #
        #     # 2. 死叉: (昨天>0, 今天<0): 需要 selling it
        # if today_diff_score<0 and self.last_diff_score>=0:
        #     selling_count = self.chicang_stock_count # 当出现死叉时, 把所有的持仓全部抛出
        #     self.selling(selling_price=self.today_price, selling_count=selling_count)

        pass # 每天都不进行任何操作

        # ====================================================
        # ====================================================


        # 3. 每晚:更新必要数据
        self.do_every_evening() # 每个策略都需要更新的'每日数据'


    def run(self, selected_days=99999, start_date=None, end_date=None, pt=False):
        """
            function: 整个'策略类'的执行入口
            params:
                selected_avg: 选择哪两根均线作为长短线的计算差值
                selected_days:
                    1. 回测的天数 (越久远的数据可能与当前的市场差异很大, 而且也伴随通货膨胀之类的影响因素)
                    2. 日期的默认选取方式: 从今天开始, 倒退几天
                    3. 这里的天数: 是指实际天数 (不是"股市的交易天数")
                start_date/end_date: 日期的str标准格式: 2020-07-20
                pt: 是否需要打印输出

            return:
                self.asset_dict (整体的收益情况) (dict类型)

        """

        # 1. 初始化数据(清零)
            # (不清零的话, 会导致重复run方法时候出错)
        self.init_data(selected_days=selected_days, start_date=start_date, end_date=end_date, pt=pt)

        # A. 当存在'该时间段内的df'时:
        if len(self.hist_df) > 0:
            self.all_arg_msg = f"【参数】==> stock_code:{self.stock_code}; days:{self.selected_days} (start:{self.start_date} -- end:{self.end_date})"
            if self.pt == True:
                print("\n\n", self.all_arg_msg, "\n")

            # 2. 执行策略计算
            self.hist_df.apply(self.strategy_cal, axis=1) # 运用上面的"策略计算"函数 (会把所有"买卖操作"数据存入 self.cash_flow_lst)

            # 3. 查看收益情况
            self.asset_dict = self.return_asset_dict() # 返回"账户资产相关信息"

            return self.asset_dict

        # B. 当不存在'该时间段内的df'时:
        else:
            return {} # 返回空dict






# 双均线策略: 回测版本
class DoubleMovingAverage(OrgModel):
    """
        function:
            (即: '金叉死叉'策略)
            短线自下而上穿过长线: 买入
            短线自上而下穿过长线: 卖出

        note:
            1. 适合有明显上升/下降趋势的市场

        tips:
            继承基础模型类后, 只需要重写两个函数:
                1. run的主运行函数
                2. strategy_cal()函数 [最核心修改的部分!!! 每个策略的主要差异所在]
    """

    def strategy_cal(self, doc):
        """
            function: 策略计算的主函数 (最主要的"计算模块") [apply函数]
        """
        # 1. 每早:获取必要数据
        self.do_every_morning(doc) # 每个策略都需要更新的'每日数据'
        today_diff_score = doc.get(self.selected_avg) # 可以选取不同的 "长短线" (由run方法中给出)

        # 2. 策略的主要内容 (买卖点都是指: 尾盘15:00时候发生的)
        # ====================================================
        # ====================================================
            # 1. 金叉: (昨天<0, 今天>0): 需要 buying it
        if today_diff_score>0 and self.last_diff_score<=0:
            buying_count = self.cash_balance // self.today_price # [暂时设定] (待优化)
            self.buying(buying_price=self.today_price, buying_count=buying_count)

            # 2. 死叉: (昨天>0, 今天<0): 需要 selling it
        if today_diff_score<0 and self.last_diff_score>=0:
            selling_count = self.chicang_stock_count # 当出现死叉时, 把所有的持仓全部抛出
            self.selling(selling_price=self.today_price, selling_count=selling_count)

        # ====================================================
        # ====================================================


        # 3. 每晚:更新必要数据
        self.do_every_evening() # 每个策略都需要更新的'每日数据'
            # 用今日的score替换昨天的 (保证每个循环中, last_diff_score中都是昨日的数据)
        self.last_diff_score = today_diff_score






    def run(self, selected_avg="5v30", selected_days=99999, start_date=None, end_date=None, pt=False):
        """
            function: 整个'策略类'的执行入口
            params:
                selected_avg: 选择哪两根均线作为长短线的计算差值
                selected_days:
                    1. 回测的天数 (越久远的数据可能与当前的市场差异很大, 而且也伴随通货膨胀之类的影响因素)
                    2. 日期的默认选取方式: 从今天开始, 倒退几天
                    3. 这里的天数: 是指实际天数 (不是"股市的交易天数")
                start_date/end_date: 日期的str标准格式: 2020-07-20
                pt: 是否需要打印输出

            return:
                self.asset_dict (整体的收益情况) (dict类型)

        """

        # 1. 初始化数据(清零)
            # (不清零的话, 会导致重复run方法时候出错)
        self.init_data(selected_days=selected_days, start_date=start_date, end_date=end_date, pt=pt)

        # A. 当存在'该时间段内的df'时:
        if len(self.hist_df) > 0:
            self.strategy_name = "双均线"
            self.selected_avg = selected_avg # 长短线指标选择 (几日均线与几日均线的差值)
            self.all_arg_msg = f"【参数】==> stock_code:{self.stock_code}; days:{self.selected_days} (start:{self.start_date} -- end:{self.end_date})"
            # if self.pt == True:
            # 必打印
            print("\n\n", self.all_arg_msg, "\n", " ↓ ↓ ↓" * 15)


            # 2. 执行策略计算
            self.hist_df.apply(self.strategy_cal, axis=1) # 运用上面的"策略计算"函数 (会把所有"买卖操作"数据存入 self.cash_flow_lst)

            # 3. 查看收益情况
            self.asset_dict = self.return_asset_dict() # 返回"账户资产相关信息"

            return self.asset_dict

        # B. 当不存在'该时间段内的df'时:
        else:
            return {} # 返回空dict






# 补损策略
class StopLoss(OrgModel):
    """
        function:
            当下降到5%的时候, 按照原市值的2倍买入(这样平摊下来的跌幅控制在2.5%之内), 越跌越买, 直到股票的涨幅在5%以上后卖出.

        note:
            1. 适合振荡器的市场 (下跌后很快会回涨). [这招在整个市场处于上升/下降通道时不适用!! 谨记!!]

        tips:   继承基础模型类后, 只需要重写两个函数:
                    1. run的主运行函数
                    2. strategy_cal()函数 [最核心修改的部分!!! 每个策略的主要差异所在]
    """

    def get_bucang_count_dict(self, first_percentage=0.045, init_cash_balance=100000, stock_price=45, exploit=True):
        """
            function: 输入'首次买入'的金额占比, 计算出每次补仓的金额
            params:
                init_cash_balance: 起始资金
                first_percentage: 首次买入占比 = 首次买入金额 / 起始资金
                exploit: 是否需要剥削最后的'剩余现金'
            return:
                每次补仓的股数 (包含'首次买入')

            note:
                amount: 代表股票金额
                count:    代表股票数量
                price:  代表股票单价 (price=amount/count)
        """
        # 最大可购买股数
        max_available_count = self.get_round_count(expected_buying_count=init_cash_balance/stock_price, round_type="down")
        # 计算首次购买股数
        first_count = self.get_round_count(expected_buying_count=max_available_count*first_percentage, min_count=100)

        this_count = first_count # 此时购买的股数
        sum_count = this_count   # 已买入的总股数
        this_count_dict = {1 : this_count} # 每次买入股数的dict
        sum_count_dict = {1 : this_count} # 累计买入'总股数'的dict

        for i in range(2, 100):
            # 1. 递减系数: i每变大一次, 这个系数就要递减, 防止资金有限的情况下补仓次数太少.
                # x的一般取值有3档: 0.1; 0.05; 0.0 (0.05较为中庸)
                # x=0.0: 完全遵循'2倍购入量', 即:每次亏损比例降为一半, 但是'最高补仓次数'会比较少 (一般就是5-6次)
            x = 0.05 # [可控变量]: 可以随意调节, 影响'递减系数', 来得到想要的"最高补仓次数" (x越大, '最高补仓次数'越多)
            decrement_coef = 1 - x * (i-2)
            # 2. 计算此次补仓的股数
            rest_available_count = int(max_available_count - sum_count) # 剩余可买入股数
            # print(sum_count, decrement_coef)
            this_count = self.get_round_count(expected_buying_count=sum_count*decrement_coef, min_count=100, round_type="down")
            # 3. 判断: 如果'购入总股数'大于'最大可购买股数', 则退出循环
            if (sum_count + this_count > max_available_count) or (this_count == 0):
                # 6. [toggle]: 看是否需要剥削最后的现金 (把剩余的'可买入股数'全部用完)
                if exploit == True:
                    if self.pt == True:
                        print("剥削它....")
                    this_count = rest_available_count
                    sum_count += this_count
                    this_count_dict.update({i:this_count})
                    sum_count_dict.update({i:sum_count})
                if self.pt == True:
                    print(this_count_dict)
                    print(sum_count_dict)
                self.bucang_count_dict = this_count_dict
                return this_count_dict
            # 4. 更新操作要在上面的'判断'之后!! (大于'最大可购买股数': 就不能update了)
            sum_count += this_count # 累计'已买入的总股数'
            this_count_dict.update({i:round(this_count, 0)})
            sum_count_dict.update({i:round(sum_count, 0)})
            # print(this_count_dict)
            # print(sum_count_dict)





    def strategy_cal(self, doc):
        """
            function: 策略计算的主函数 (最主要的"计算模块") [apply函数]
        """
        # 1. 每早:获取必要数据
        self.do_every_morning(doc) # 每个策略都需要更新的'每日数据'

        # # 2. 策略的主要内容 (买卖点都是指: 尾盘15:00时候发生的)
        # # ====================================================
        # # ====================================================

        # 1. 买点
            # i. 当还没有买入任何股票时: (参考'市场累计盈亏比例')
        if self.bucang_times == 0:
            # if self.MarketLjYkbl <= -self.stoploss_rate: # (eg: LjYkbl<=-5%)
            #     self.bucang_times += 1 # 累加'补仓次数'
            #     buying_count = self.bucang_count_dict.get(self.bucang_times, 999999)
            #     self.buying(buying_price=self.today_price, buying_count=buying_count)
            if self.vs_max_market_price_bl <= -self.stoploss_rate: # (eg: LjYkbl<=-5%)
                self.bucang_times += 1 # 累加'补仓次数'
                buying_count = self.bucang_count_dict.get(self.bucang_times, 999999)
                self.buying(buying_price=self.today_price, buying_count=buying_count)

            # ii. 当已经持有股票时: (参考'个人账户的累计盈亏比例')
        elif self.bucang_times != 0:
            if self.MyLjYkbl <= -self.stoploss_rate: # (eg: LjYkbl<=-5%)
                self.bucang_times += 1 # 累加'补仓次数'
                buying_count = self.bucang_count_dict.get(self.bucang_times, 999999) # 当补仓次数超过'补仓字典'后, 默认使用999999('剥削'最后的股数)
                self.buying(buying_price=self.today_price, buying_count=buying_count)

        # 2. 卖点
            # [toggle]: 当收益满足 2*5%的时候再卖
            # if self.MyLjYkbl >= self.stoploss_rate: # (eg: LjYkbl>=5%)
            if self.MyLjYkbl >= self.stoploss_rate *2: # (eg: LjYkbl>=10%)
                selling_count = self.chicang_stock_count # 卖点时: 把所有的持仓全部抛出
                self.selling(selling_price=self.today_price, selling_count=selling_count)
                self.bucang_times = 0 # 补仓次数清零
                # 把'市场累计盈亏'相关数据都清零. (因为补仓次数为0后, 需要依靠"市场累计盈亏"来判断是否第一次买入)
                # self.MarketLjYk = 0.0  # 这是指"市场上"的"累计盈亏" (区别于: "自己账户"的"LjYk")
                # self.MarketLjYkbl = 0.0  # 这是指"市场上"的"累计盈亏比例" (区别于: "自己账户"的"LjYkbl")
                # self.MarketLjYk_lst = []
                # self.MarketLjYkbl_lst = []
                self.min_market_price = self.today_price # 用'今日价格'作为近期的'最高/最低价格'
                self.max_market_price = self.today_price

        # # ====================================================
        # # ====================================================


        # 3. 每晚:更新必要数据
        self.do_every_evening() # 每个策略都需要更新的'每日数据'





    def run(self, first_percentage=0.03, stoploss_rate=0.05, selected_days=100, start_date=None, end_date=None, pt=False):
        """
            function: 整个'策略类'的执行入口
            params:
                selected_days:
                    1. 回测的天数 (越久远的数据可能与当前的市场差异很大, 而且也伴随通货膨胀之类的影响因素)
                    2. 日期的默认选取方式: 从今天开始, 倒退几天
                    3. 这里的天数: 是指实际天数 (不是"股市的交易天数")
                start_date/end_date: 日期的str标准格式: 2020-07-20
                pt: 是否需要打印输出
                first_percentage: 首次购买的占比 (首次占比越大, 补仓的机会越少, 风险偏大.)
                stoploss_rate: 止损比例 (当累计盈亏比例达到 "+-5%"时, 就判断为'买卖点')
                self.bucang_count_dict: 补仓字典 (即: 每次补仓时候, 需要买入'多少整百股')

            return:
                self.asset_dict (整体的收益情况) (dict类型)

        """

        # 1. 初始化数据(清零)
            # (不清零的话, 会导致重复run方法时候出错)
        self.init_data(selected_days=selected_days, start_date=start_date, end_date=end_date, pt=pt)

        # A. 当存在'该时间段内的df'时:
        if len(self.hist_df) > 0:
            self.strategy_name = "补损"
            self.first_percentage = first_percentage
            self.stoploss_rate = stoploss_rate
            self.all_arg_msg = f"\n\n【参数】==> stock_code:{self.stock_code}; days:{self.selected_days} (start:{self.start_date} -- end:{self.end_date}) ==> stoploss_rate:{self.stoploss_rate}"
            self.all_arg_msg += f"\n【参数】==> first_percentage:{first_percentage}; stoploss_rate:{stoploss_rate}; init_cash_balance:{self.init_cash_balance}"
            # if self.pt == True:
            # 必打印
            print("\n\n", self.all_arg_msg, "\n", " ↓ ↓ ↓" * 15)
            # 获取"补仓字典" (每次补仓的对应的股数)
            self.get_bucang_count_dict(
                first_percentage=first_percentage, init_cash_balance=self.init_cash_balance,
                stock_price=self.newest_price, exploit=True
            )

            # 2. 执行策略计算
            self.hist_df.apply(self.strategy_cal, axis=1) # 运用上面的"策略计算"函数 (会把所有"买卖操作"数据存入 self.cash_flow_lst)

            # 3. 查看收益情况
            self.asset_dict = self.return_asset_dict() # 返回"账户资产相关信息"

            return self.asset_dict

        # B. 当不存在'该时间段内的df'时:
        else:
            return {} # 返回空dict




def main():
    """
        function: 这里基本都是一次性的回测. 如果想要系统的批量回测, 需要使用quant_hc脚本
                    (多个参数的排列组合, 寻找最佳参数, 反映策略是否真实可行)
    """
    # o = OrgModel(Zqdm="002505")
    # d = o.run(30)
    #
    # o = DoubleMovingAverage("0.159995", init_cash_balance=100000)
    # asset_dict = o.run(selected_days=30, selected_avg="5v10")
    # print(asset_dict)

    # get_bucang_count_dict(A=0.07, init_cash_balance=300000, stock_price=3.8, exploit=True)


    # o = StopLoss("0.159995", init_cash_balance=100000)
    # o = StopLoss("0.159915", init_cash_balance=250000)
    # o = StopLoss("0.002415", init_cash_balance=100000)
    # o = StopLoss("0.002230", init_cash_balance=100000)
    # asset_dict = o.run(start_date="2020-01-15", selected_days=300, first_percentage=0.03, stoploss_rate=0.05, pt=True)
    # asset_dict = o.run(start_date="2020-03-04", selected_days=200, first_percentage=0.03, stoploss_rate=0.05, pt=False)
    # asset_dict = o.run(start_date="2020-04-20", selected_days=200, first_percentage=0.03, stoploss_rate=0.05, pt=False)
    # asset_dict = o.run(start_date="2017-06-01", selected_days=300, first_percentage=0.03, stoploss_rate=0.05, pt=False)
    # asset_dict = o.run(start_date="2017-06-15", selected_days=300, first_percentage=0.03, stoploss_rate=0.05, pt=False)
    # asset_dict = o.run(start_date="2017-06-30", selected_days=300, first_percentage=0.03, stoploss_rate=0.05, pt=False)

    "半成品结论: 惠城科技/中船防务/大康农业 这些垃圾股, 3年下来的ROA竟然还是负的..."
    "正常基本面/业绩良好的股, 使用这种方式基本都是有25%左右的收益"
    o = StopLoss("1.600685", init_cash_balance=250000)
    asset_dict = o.run(start_date="2020-07-25", selected_days=200, first_percentage=0.05, stoploss_rate=0.03)
    print(asset_dict)

    # o = DoubleMovingAverage("0.002415", init_cash_balance=30000)
    # asset_dict = o.run(selected_days=500, selected_avg="5v20", start_date="2017-01-01")
    # print(asset_dict)


if __name__ == '__main__':
    print("Start test!\n\n")
    main()
    print("\n\n\nIt's over!")
