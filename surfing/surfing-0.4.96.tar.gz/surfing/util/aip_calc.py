import datetime
from datetime import date

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import scipy.optimize

def xnpv(rate, values, dates):
    '''Equivalent of Excel's XNPV function.

    >>> from datetime import date
    >>> dates = [date(2010, 12, 29), date(2012, 1, 25), date(2012, 3, 8)]
    >>> values = [-10000, 20, 10100]
    >>> xnpv(0.1, values, dates)
    -966.4345...
    '''
    
    if rate < -0.999999 or math.isclose(rate,-1,rel_tol=1e-08):
        return float('inf')
    try:
        d0 = min(dates)
        return sum([ vi / (1.0 + rate)**((di - d0).days / 365.0) for vi, di in zip(values, dates)])
    except Exception as e:
        print(f'Failed to calc xnpv rate {rate} values {values} dates {dates} d0 {d0}')
        return float('inf')

def xirr(values, dates):
    '''Equivalent of Excel's XIRR function.

    >>> from datetime import date
    >>> dates = [date(2010, 12, 29), date(2012, 1, 25), date(2012, 3, 8)]
    >>> values = [-10000, 20, 10100]
    >>> xirr(values, dates)
    0.0100612...
    '''
    try:
        return scipy.optimize.brentq(lambda r: xnpv(r, values, dates), -0.999, 1e3)
    except Exception:    # Failed to converge?
        return scipy.optimize.bisect(lambda r: xnpv(r, values, dates), -0.999, 1e3)


class AIPCalculator(object):
    def __init__(self, arr, start_date, end_date, stop_profit=None, strategy=None,
                 amt_bench=1000, mode='1w', mode_offset=0, purchase_rate=0.001, redeem_rate=0.001):
        self.arr = arr.dropna()
        self.start_date = max(start_date, self.arr.index[0])
        self.end_date = end_date or datetime.datetime.now().date()
        self.amt_bench = amt_bench
        self.mode = mode
        self.mode_offset = mode_offset
        self.yearly_multiplier = self.get_yearly_multiplier(mode)
        self.purchase_rate = purchase_rate
        self.redeem_rate = redeem_rate
        self.stop_profit = stop_profit
        # calc
        self.last_trade_day = None
        self.moving_average = None
        if strategy:
            if strategy.startswith('ma'):
                window_size = int(strategy[2:])
                self.moving_average = self.arr.rolling(window_size).mean().fillna(0)
                self.vol_10 = self.arr.pct_change(1).rolling(10).std().fillna(0)

    def get_yearly_multiplier(self, mode):
        m = None
        if mode == '1d':
            m = 365
        elif mode == '1w':
            m = 52
        elif mode == '2w':
            m = 26
        elif mode == '1m':
            m = 12
        else:
            raise Exception(f'unexpected trade mode: {mode}')
        return m

    # 判断是否当前要进行交易
    def is_to_trade(self, dt):
        if self.mode == '1d':
            return True
        elif self.mode == '1w':
            return dt.weekday() == self.mode_offset
        elif self.mode == '2w':
            return dt.weekday() == self.mode_offset and (
            self.last_trade_day is None or (dt - self.last_trade_day).days > 7)
        elif self.mode == '1m':
            return dt.day == self.mode_offset + 1
        else:
            raise Exception('unexpected trade mode: ' + self.mode)

    def convert_irr(self, irr):
        return pow(irr + 1, self.yearly_multiplier) - 1

    def convert_ret(self, ret):
        days = (self.end_date - self.start_date).days
        return pow(ret + 1, 365 / days) - 1

    def _mv_multiplier(self, val, ma, vol_10):
        if ma == 0:
            return 1
        diff = (val - ma) / ma
        if diff > 0:
            if diff <= 0.15:
                return 0.9
            elif diff <= 0.5:
                return 0.8
            elif diff <= 1:
                return 0.7
            else:
                return 0.6
        else:
            diff = abs(diff)
            if diff <= 0.05:
                return 0.6 if vol_10 > 0.05 else 1.6
            elif diff <= 0.1:
                return 0.7 if vol_10 > 0.05 else 1.7
            elif diff <= 0.2:
                return 0.8 if vol_10 > 0.05 else 1.8
            elif diff <= 0.3:
                return 0.9 if vol_10 > 0.05 else 1.9
            elif diff <= 0.4:
                return 1.0 if vol_10 > 0.05 else 2.0
            else:
                return 1.1 if vol_10 > 0.05 else 2.1

    def get_amt(self, cur_date):
        if self.moving_average is not None:
            ma = self.moving_average[:cur_date][-1]
            vol_10 = self.vol_10[:cur_date][-1]
            val = self.arr[:cur_date][-1]
            m = self._mv_multiplier(val, ma, vol_10)
            return self.amt_bench * m
        else:
            return self.amt_bench

    def run(self):
        self.res = []

        cur_date = self.start_date
        arr_idx = 0

        self.cur_mv = [0]  # 当前基金资产市值
        self.vol = [0]  # 份额
        self.tot_inv_amt = [0]  # 总投资额
        self.trd_count = [0]  # 总投资次数
        self.redeem_amt = []
        self.redeem_date = []
        self.redeem_ret = []
        self.redeem_gain = []
        self.max_cur_inv_amt = 0
        avg_cost = 0  # 平均投资成本

        self.irr_helper = ([], [])
        amt_to_trade = 0

        last_trade_mv = 0

        while cur_date < self.end_date:
            while self.arr.index[arr_idx] < cur_date and arr_idx < len(self.arr.index) - 1:
                arr_idx += 1

            if self.is_to_trade(cur_date):
                amt_to_trade += self.get_amt(cur_date)
                self.irr_helper[0].append(amt_to_trade)
                self.irr_helper[1].append(cur_date)

            if self.arr.index[arr_idx] == cur_date:
                # 交易日
                p = self.arr[arr_idx]

                # 1. 处理正常的买入工作
                if amt_to_trade > 0:
                    self.last_trade_day = cur_date
                    # update data
                    self.trd_count[-1] += 1
                    _tot_cost = sum(self.tot_inv_amt) * avg_cost
                    self.tot_inv_amt[-1] += amt_to_trade
                    self.vol[-1] += amt_to_trade * (1 - self.purchase_rate) / p
                    avg_cost = (_tot_cost + amt_to_trade * p) / sum(self.tot_inv_amt)
                    self.cur_mv[-1] = self.vol[-1] * p
                    self.res.append({'dt': cur_date, 'amt_to_trade': amt_to_trade, 'cur_mv': self.cur_mv[-1],
                                     'tot_inv_amt': self.tot_inv_amt[-1], 'avg_cost': avg_cost, 'p': p,
                                     'cur_gain': sum(self.cur_mv) - sum(self.tot_inv_amt),
                                     'max_cur_inv_amt': max(self.max_cur_inv_amt, max(self.tot_inv_amt)),
                                     })
                    last_trade_price = p
                    amt_to_trade = 0
                    # print(f'[{cur_date}] (tot){_tot_cost} (avg){avg_cost} (tot_inv_amt){str(self.tot_inv_amt)}')

                # 更新 当前基金资产市值
                self.cur_mv[-1] = self.vol[-1] * p

                # 止盈逻辑
                if self.stop_profit:
                    rate = self.cur_mv[-1] / self.tot_inv_amt[-1] - 1 if self.tot_inv_amt[-1] > 0 else 0
                    if rate >= self.stop_profit:
                        next_idx = arr_idx + 1 if arr_idx + 1 < len(self.arr) else arr_idx
                        next_p = self.arr[next_idx]
                        redeem_amt = self.vol[-1] * next_p * (1 - self.redeem_rate)
                        self.redeem_amt.append(redeem_amt)
                        self.redeem_date.append(cur_date)
                        # self.redeem_ret.append(rate)
                        self.redeem_ret.append(redeem_amt / self.tot_inv_amt[-1])
                        self.redeem_gain.append(redeem_amt - self.tot_inv_amt[-1])
                        self.cur_mv.append(0)
                        self.vol.append(0)
                        self.tot_inv_amt.append(0)
                        self.trd_count.append(0)
                        self.irr_helper[0].append(-1 * redeem_amt)
                        self.irr_helper[1].append(cur_date)
                        # irr_helper[1].append(self.arr.index[next_idx])

            cur_date += datetime.timedelta(days=1)

        # stat
        self.irr_helper[0].append(-1 * (
        self.cur_mv[-1] + amt_to_trade))  # 如果终止定投前，到了月初投入一笔前，但是一直没到交易日，没有买入资产，这笔前进入了irr_helper，但是没有进入 资产里。终止定投取钱，会少最后一笔
        self.irr_helper[1].append(self.end_date)
        self.irr = xirr(self.irr_helper[0], self.irr_helper[1])
        self.tot_mv = self.cur_mv[-1] + sum(self.redeem_amt)
        self.tot_ret = (self.tot_mv) / sum(self.tot_inv_amt) - 1
        self.ret = self.convert_ret(self.tot_ret)
        self.tot_gain = self.tot_mv - sum(self.tot_inv_amt)
        # print(f'(irr){self.irr} (cur_mv){self.tot_mv} (tot_inv_amt){sum(self.tot_inv_amt)} (ret){self.ret} (cnt){sum(self.trd_count)} (tot_ret){self.tot_ret} (tot_gain){self.tot_gain}')
        '''
        if self.stop_profit:
            print('cur_mv', self.cur_mv)
            print('tot_inv_amt', self.tot_inv_amt)
            for i in range(0, len(self.redeem_amt)):
                print(f'{self.redeem_date[i]} (ret){self.redeem_ret[i]} (inv){self.tot_inv_amt[i]} (gain){self.redeem_gain[i]} (amt){self.redeem_amt[i]}')
        '''

    def get_irr(self):
        # self.res = []
        cur_date = self.start_date
        arr_idx = 0
        self.cur_mv = 0  # 当前基金资产市值
        self.vol = 0  # 份额
        self.tot_inv_amt = 0  # 总投资额
        self.irr_helper = ([], [])
        amt_to_trade = 0
        while cur_date < self.end_date:
            while self.arr.index[arr_idx] < cur_date and arr_idx < len(self.arr.index) - 1:
                arr_idx += 1

            if self.is_to_trade(cur_date):
                amt_to_trade += self.get_amt(cur_date)
                self.irr_helper[0].append(amt_to_trade)
                self.irr_helper[1].append(cur_date)

            if self.arr.index[arr_idx] == cur_date:
                # 交易日
                p = self.arr[arr_idx]

                # 1. 处理正常的买入工作
                if amt_to_trade > 0:
                    self.tot_inv_amt += amt_to_trade
                    self.vol += amt_to_trade * (1 - self.purchase_rate) / p
                    amt_to_trade = 0

                # 更新 当前基金资产市值
                self.cur_mv = self.vol * p

                # 止盈逻辑
                if self.stop_profit:
                    rate = self.cur_mv / self.tot_inv_amt - 1 if self.tot_inv_amt > 0 else 0
                    if rate >= self.stop_profit:
                        next_idx = arr_idx + 1 if arr_idx + 1 < len(self.arr) else arr_idx
                        next_p = self.arr[next_idx]
                        redeem_amt = self.vol * next_p * (1 - self.redeem_rate)
                        self.cur_mv = 0
                        self.vol = 0
                        self.tot_inv_amt = 0
                        self.irr_helper[0].append(-1 * redeem_amt)
                        self.irr_helper[1].append(cur_date)

            cur_date += datetime.timedelta(days=1)

        # stat
        self.irr_helper[0].append(-1 * (self.cur_mv + amt_to_trade))
        self.irr_helper[1].append(self.end_date)
        self.irr = xirr(self.irr_helper[0], self.irr_helper[1])
        return self.irr

    def get_aip_total_return(self):
        cash_flow = self.irr_helper[0]
        cash_inputs = [i for i in cash_flow if i > 0]
        cash_outputs = [i for i in cash_flow if i < 0]
        return (-sum(cash_outputs) / sum(cash_inputs)) - 1

    def get_fund_ret(self):
        _arr = self.arr[self.start_date:self.end_date]
        return _arr[-1] / _arr[0] - 1

    def get_fund_vol(self):
        _arr = self.arr[self.start_date:self.end_date]
        return _arr.pct_change(1).std(ddof=1)

    def get_cash_flow(self):
        dic = {'datetime': self.irr_helper[1], 'cash_flow': self.irr_helper[0]}
        return pd.DataFrame(dic)

    def plot(self):
        df_net_arr = pd.DataFrame(self.res).set_index('dt')[['p', 'avg_cost']]
        df_net_arr.plot.line(figsize=(12, 6))
        plt.legend(fontsize=15)
        plt.title('price vs avg_cost', fontsize=25)
        plt.show()


class MultipleAIPCalculator(object):

    def __init__(self, arr, start_date, end_date, stop_profit=None, strategy=None,
                 amt_bench=1000, mode='1w', mode_offset=0, purchase_rate=0.001, redeem_rate=0.001, weight_list=None, is_set_group_amt=False):
        # weight_list = 【30，40，30】权重
        self.arr = [arr.dropna()] if not isinstance(arr, list) else [i.dropna() for i in arr]
        self.weight_list = [1 for i in self.arr ] if weight_list is None else weight_list
        _sum = sum(self.weight_list)
        self.weight_list = [i/_sum for i in self.weight_list]
        self.start_date = max([start_date] + [i.index[0] for i in self.arr])
        self.end_date = end_date or datetime.datetime.now().date()
        self.amt_bench = amt_bench
        self.mode = mode
        self.mode_offset = mode_offset
        self.yearly_multiplier = self.get_yearly_multiplier(mode)
        self.purchase_rate = purchase_rate if isinstance(purchase_rate, list) else [purchase_rate]
        self.redeem_rate = redeem_rate if isinstance(redeem_rate, list) else [redeem_rate]
        self.stop_profit = stop_profit
        self.is_set_group_amt = is_set_group_amt
        # calc
        self.last_trade_day = None
        self.moving_average = None
        if strategy:
            if strategy.startswith('ma'):
                window_size = int(strategy[2:])
                self.moving_average = [arr_i.rolling(window_size).mean().fillna(0) for arr_i in self.arr]
                self.vol_10 = [arr_i.pct_change(1).rolling(10).std().fillna(0) for arr_i in self.arr]
                
    def get_yearly_multiplier(self, mode):
        m = None
        if mode == '1d':
            m = 365
        elif mode == '1w':
            m = 52
        elif mode == '2w':
            m = 26
        elif mode == '1m':
            m = 12
        else:
            raise Exception(f'unexpected trade mode: {mode}')
        return m

    # 判断是否当前要进行交易
    def is_to_trade(self, dt):
        if self.mode == '1d':
            return True
        elif self.mode == '1w':
            return dt.weekday() == self.mode_offset
        elif self.mode == '2w':
            return dt.weekday() == self.mode_offset and (self.last_trade_day is None or (dt - self.last_trade_day).days > 7)
        elif self.mode == '1m':
            return dt.day == self.mode_offset + 1
        else:
            raise Exception('unexpected trade mode: ' + self.mode)
    
    def convert_irr(self, irr):
        return pow(irr + 1, self.yearly_multiplier) - 1
        
    def convert_ret(self, ret):
        days = (self.end_date - self.start_date).days
        return pow(ret + 1, 365 / days) - 1

    def _mv_multiplier(self, val, ma, vol_10):
        if ma == 0:
            return 1
        diff = (val - ma) / ma
        if diff > 0:
            if diff <= 0.15:
                return 0.9
            elif diff <= 0.5:
                return 0.8
            elif diff <= 1:
                return 0.7
            else:
                return 0.6
        else:
            diff = abs(diff)
            if diff <= 0.05:
                return 0.6 if vol_10 > 0.05 else 1.6
            elif diff <= 0.1:
                return 0.7 if vol_10 > 0.05 else 1.7
            elif diff <= 0.2:
                return 0.8 if vol_10 > 0.05 else 1.8
            elif diff <= 0.3:
                return 0.9 if vol_10 > 0.05 else 1.9
            elif diff <= 0.4:
                return 1.0 if vol_10 > 0.05 else 2.0
            else:
                return 1.1 if vol_10 > 0.05 else 2.1

    def get_amt(self, cur_date, idx=0):
        if self.moving_average is not None:
            ma = self.moving_average[idx][:cur_date][-1]
            vol_10 = self.vol_10[idx][:cur_date][-1]
            val = self.arr[idx][:cur_date][-1]
            m = self._mv_multiplier(val, ma, vol_10)
            return self.amt_bench * m
        else:
            return self.amt_bench
    
    def get_irr(self):
        #self.res = []
        cur_date = self.start_date
        arr_idx = 0
        self.cur_mv = [[0] for i in self.arr] # 当前基金资产市值
        _tmp_amount = [0 for i in self.arr] # 当期各资产投资量

        self.vol = [0 for i in self.arr] # 份额
        self.inv_amt = [[0] for i in self.arr] # 总投资额
        self.max_cur_inv_amt = [0 for i in self.arr]  # 当期之前最大投入
        self.avg_cost = [0 for i in self.arr] # 平均花费
        self.trd_count = [0]  # 总投资次数

        self.redeem_amt = [[] for i in self.arr]  # 赎回金额
        self.redeem_inv_amt = [[] for i in self.arr]  # 赎回时投入
        self.redeem_date = [[] for i in self.arr]  # 赎回日期
        self.redeem_ret = [[] for i in self.arr]  # 赎回比率
        self.redeem_gain = [[] for i in self.arr]  # 赎回收益

        self.irr_helper = [([], []) for i in self.arr]
        self.res = [[] for i in self.arr]
        amt_to_trade = [0 for i in self.arr]
        dts = pd.DataFrame(self.arr).T.index
        dts = dts[(dts >= self.start_date) & (dts <= self.end_date)]
        while cur_date < self.end_date:
            while dts[arr_idx] < cur_date and arr_idx < len(dts) - 1:
                arr_idx += 1

            if self.is_to_trade(cur_date):
                for idx in range(len(self.arr)):
                    _tmp_amount[idx] = self.get_amt(cur_date, idx) * self.weight_list[idx]
                #if rebalance
                if self.is_set_group_amt:
                    _sum = sum(_tmp_amount)
                    _rate = self.amt_bench/_sum if _sum !=0 else 1
                    _tmp_amount = [i * _rate for i in _tmp_amount ]
                    
                for idx in range(len(self.arr)):
                    self.irr_helper[idx][0].append(_tmp_amount[idx])
                    amt_to_trade[idx] += _tmp_amount[idx]
                    self.irr_helper[idx][1].append(cur_date)
                
            if dts[arr_idx] == cur_date:
                # 交易日
                for idx, arr in enumerate(self.arr):
                    p = self.arr[idx][cur_date]
                    # 1. 处理正常的买入工作
                    if amt_to_trade[idx] > 0:
                        self.last_trade_day = cur_date
                        self.trd_count[-1] += 1
                        self.inv_amt[idx][-1] += amt_to_trade[idx]
                        # _tot_cost = sum(self.inv_amt[idx]) * self.avg_cost[idx]
                        self.vol[idx] += amt_to_trade[idx] * (1 - self.purchase_rate[idx]) / p
                        self.avg_cost[idx] = self.inv_amt[idx][-1] / self.vol[idx]
                        self.cur_mv[idx][-1] = self.vol[idx] * p
                        tot_cur_mv = sum(self.cur_mv[idx])
                        tot_cur_inv_mv = sum(self.inv_amt[idx])
                        self.res[idx].append({
                            'dt': cur_date,
                            'amt_to_trade': amt_to_trade,
                            'cur_mv': self.cur_mv[idx][-1],
                            'inv_amt': tot_cur_inv_mv,
                            'avg_cost': self.avg_cost[idx],
                            'cur_gain': tot_cur_mv - tot_cur_inv_mv,
                            'max_cur_inv_amt': max(self.max_cur_inv_amt[idx], max(self.inv_amt[idx])),
                            'p': p,
                        })
                        #print(f'dt{cur_date} p {p} amt {amt_to_trade[idx]} v {self.vol[idx]} ')

                        # 交易完成 将各资金池制空
                        amt_to_trade[idx] = 0

                    # 更新 当前基金资产市值
                    self.cur_mv[idx][-1] = self.vol[idx] * p
                    #print(f'dt {cur_date} mv {self.cur_mv[idx]} vol {self.vol[idx]} p {p} ')
                # 止盈逻辑
                if self.stop_profit:
                    tot_mv = sum([i[-1] for i in self.cur_mv])
                    tot_inv_amt = sum([i[-1] for i in self.inv_amt])
                    rate = tot_mv / tot_inv_amt - 1 if tot_inv_amt > 0 else 0
                    if rate >= self.stop_profit:
                        for idx in range(len(self.arr)):
                            next_idx = arr_idx + 1 if arr_idx + 1 < len(dts) else arr_idx
                            next_p = self.arr[idx][dts[next_idx]]
                            redeem_amt = self.vol[idx] * next_p * (1 - self.redeem_rate[idx])

                            self.redeem_amt[idx].append(redeem_amt)
                            self.redeem_inv_amt[idx].append(self.inv_amt[idx][-1])
                            self.redeem_date[idx].append(cur_date)
                            self.redeem_ret[idx].append(redeem_amt / self.inv_amt[idx][-1])
                            self.redeem_gain[idx].append(redeem_amt - self.inv_amt[idx][-1])

                            self.cur_mv[idx].append(0)
                            self.vol[idx]=0
                            self.inv_amt[idx].append(0)

                            # todo 这里处理了一个日期有两条数据的问题，可以看看是否有更好的处理方式
                            if self.irr_helper[idx][1][-1] == cur_date:
                                self.irr_helper[idx][0][-1] -= redeem_amt
                            else:
                                self.irr_helper[idx][0].append(-1 * redeem_amt)
                                self.irr_helper[idx][1].append(cur_date)

            cur_date += datetime.timedelta(days=1)
        # stat
        res = []
        for idx in range(len(self.arr)):
            self.irr_helper[idx][0].append(-1 * (self.cur_mv[idx][-1] + amt_to_trade[idx]))
            self.irr_helper[idx][1].append(self.end_date)
            i = self.irr_helper[idx]
            dic = {'datetime': i[1], idx: i[0]}
            df = pd.DataFrame(dic).set_index('datetime')
            res.append(df)
        self.cash_flow = pd.concat(res, axis=1, sort=True)
        self.cash_flow_sum = self.cash_flow.sum(axis=1)
        self.irr = xirr(self.cash_flow_sum.values, self.cash_flow_sum.index)

        # 非最后一天的负数是止盈赎回
        self.tot_mv = sum([self.cur_mv[idx][-1] + sum(self.redeem_amt[idx]) for idx in range(len(self.arr))])
        self.tot_inv_amt = sum( [sum(i) for i in self.inv_amt])
        self.tot_ret = (self.tot_mv) / self.tot_inv_amt - 1
        self.ret = self.convert_ret(self.tot_ret)
        self.tot_gain = self.tot_mv - self.tot_inv_amt
        return self.irr

    def get_funds_tot_inv_amt(self):
        return [sum(i) for i in self.inv_amt]

    def get_funds_tot_mv(self):
        return [self.cur_mv[idx][-1] + sum(self.redeem_amt[idx]) for idx in range(len(self.arr))]

    def get_funds_tot_gain(self):
        x = self.get_funds_tot_inv_amt()
        y = self.get_funds_tot_mv()
        return [y - x for x, y in zip(x, y )]

    def get_funds_tot_ret(self):
        x = self.get_funds_tot_inv_amt()
        y = self.get_funds_tot_mv()
        return [y / x - 1 for x, y in zip(x, y )]

    def get_funds_tot_irr(self):
        res = []
        for idx in range(len(self.arr)):
            res.append(xirr(
                self.irr_helper[idx][0],
                self.irr_helper[idx][1],
            ))
        return res

    def get_aip_total_return(self):
        res = []
        for i in self.irr_helper:
            cash_flow = i[0]
            cash_inputs = [i for i in cash_flow if i > 0]
            cash_outputs = [i for i in cash_flow if i < 0]
            res.append((-sum(cash_outputs) / sum(cash_inputs)) - 1)
        return res

    def get_fund_ret(self):
        res = []
        for i in self.arr:
            _arr = i[self.start_date:self.end_date]
            res.append(_arr[-1] / _arr[0] - 1)
        return res

    def get_fund_vol(self):
        res = []
        for i in self.arr:
            _arr = i[self.start_date:self.end_date]
            res.append(_arr.pct_change(1).std(ddof=1))
        return res

    def get_cash_flow(self):
        dic = {'datetime':self.irr_sum, 'cash_flow':self.irr_helper[0]}
        return pd.DataFrame(dic)

    def plot(self):
        df_net_arr = pd.DataFrame(self.res).set_index('dt')[['p', 'avg_cost']]
        df_net_arr.plot.line(figsize=(12,6))
        plt.legend(fontsize=15)
        plt.title('price vs avg_cost',fontsize=25)
        plt.show()

if __name__ == "__main__":
    pass
    '''
    from surfing.resource.data_store import *
    m = DataStore.load_dm()
    b_d = datetime.date(2015,1,5)
    e_d = datetime.date(2019,2,5)
    index_id_1 = 'hs300'
    index_id_2 = 'csi500'
    index_id_3 = 'gem'
    price1 = index_price[index_id_1]
    price2 = index_price[index_id_2]
    price3 = index_price[index_id_3]
    price = [price1, price2, price3]
    amt_bench = 1000
    mode = '1m'
    mode_offset = 0
    purchase_rate = [0,0,0]#index_fee_avg.AssetPurchaseRate[index_id]
    redeem_rate = [0,0,0]#index_fee_avg.AssetRedeemRate[index_id]
    weight_list = [30,40,30]
    self = AIPCalculator(price, b_d, e_d, None, None, amt_bench, mode, mode_offset, purchase_rate, redeem_rate, weight_list)
    self.get_irr()
    '''