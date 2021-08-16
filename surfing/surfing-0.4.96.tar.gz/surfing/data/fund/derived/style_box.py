import numpy as np
import pandas as pd
import datetime
import traceback
from ...api.basic import BasicDataApi
from ...api.raw import RawDataApi
# from ...api.derived import DerivedDataApi
from ...view.derived_models import StyleBox
from ..raw.raw_data_helper import RawDataHelper
from .derived_data_helper import DerivedDataHelper

from ....constant import SEMI_UPDATE_DATE_LIST


class StyleBoxGenerator:

    def __init__(self, _data_helper: DerivedDataHelper):
        self._raw_api = RawDataApi()
        self._basic_api = BasicDataApi()
        self._data_helper: DerivedDataHelper = _data_helper

    def rank_score(self, a):
        a_rank = a.rank()
        a_score = 100 * (a_rank - a_rank.min()) / (a_rank.max() - a_rank.min())
        return a_score

    def init(self, start_date, end_date):
        # 导入并格式化股价
        self.stock_price_raw = self._raw_api.get_em_stock_price(start_date, end_date, columns=['close']).set_index(['stock_id', 'datetime'])
        self.stock_price = self.stock_price_raw.reset_index().pivot(index='datetime', columns='stock_id', values='close')
        # 导入并格式化总股本
        self.stock_daily_info_raw = self._raw_api.get_em_daily_info(start_date, end_date, columns=['total_share']).set_index(['stock_id', 'datetime'])
        self.stock_daily_info = self.stock_daily_info_raw.reset_index().pivot(index='datetime', columns='stock_id', values='total_share')
        # 相乘计算出总市值
        self.cap = (self.stock_price * self.stock_daily_info).iloc[0]
        # 导入并格式化财务数据
        start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        start_date_2 = datetime.date(start_date_dt.year - 2, start_date_dt.month, start_date_dt.day)
        self.fin_fac = self._raw_api.get_em_stock_fin_fac(start_date=start_date_2, end_date=end_date)
        pivoted_table = self.fin_fac.pivot(index='datetime', columns='stock_id', values=['income_statement_61', 'balance_statement_74', 'income_statement_9', 'cashflow_statement_39'])
        pivoted_table = pivoted_table.ffill()
        self.earnings = pivoted_table['income_statement_61']
        self.book_values = pivoted_table['balance_statement_74']
        self.revenues = pivoted_table['income_statement_9']
        self.cash = pivoted_table['cashflow_statement_39']
        # 计算所需的数据
        self.earnings_td = self.earnings.iloc[-1].dropna()
        self.bv_td = self.book_values.iloc[-1].dropna()
        self.rev_td = self.revenues.iloc[-1].dropna()
        self.cash_td = self.cash.iloc[-1].dropna()
        # 计算OGS打分所需的次级指标
        self.erate = self.earnings.pct_change().mean().dropna()
        self.brate = self.book_values.pct_change().mean().dropna()
        self.rrate = self.revenues.pct_change().mean().dropna()
        self.crate = self.cash.pct_change().mean().dropna()
        self.ers = self.rank_score(self.erate)
        self.brs = self.rank_score(self.brate)
        self.rrs = self.rank_score(self.rrate)
        self.crs = self.rank_score(self.crate)
        # 去掉计算所得数据为NaN的股票
        self.lis = self.earnings_td.index & self.cap.index & self.bv_td.index & self.rev_td.index & self.cash_td.index & self.erate.index & self.brate.index & self.rrate.index & self.crate.index
        # 计算OVS打分所需的次级指标
        self.ep = self.earnings_td[self.lis] / self.cap[self.lis]
        self.bp = self.bv_td[self.lis] / self.cap[self.lis]
        self.rp = self.rev_td[self.lis] / self.cap[self.lis]
        self.cp = self.cash_td[self.lis] / self.cap[self.lis]
        self.eps = self.rank_score(self.ep)
        self.bps = self.rank_score(self.bp)
        self.rps = self.rank_score(self.rp)
        self.cps = self.rank_score(self.cp)
        # 加权计算OVS和OGS
        self.ovs = 0.5 * self.eps + (self.bps + self.rps + self.cps) / 6
        self.ogs = (self.ers + self.brs + self.rrs + self.crs) / 4
        # 得到Value Core Growth
        self.vcg = self.ogs - self.ovs
        # 再次取交集筛去NaN
        self.lis2 = self.cap.dropna().index & self.vcg.dropna().index
        self.cap = self.cap[self.lis2]
        self.vcg = self.vcg[self.lis2]

    def cal_stock(self):
        self.capsum = self.cap.sort_values(ascending=False).cumsum()
        self.capt = self.capsum / self.capsum[-1]
        self.big_cap = self.capt[self.capt < 0.7].index
        self.mid_cap = self.capt[np.logical_and(self.capt >= 0.7, self.capt <= 0.9)].index
        self.small_cap = self.capt[self.capt > 0.9].index
        self.big_vcg = self.vcg[self.big_cap]
        self.mid_vcg = self.vcg[self.mid_cap]
        self.small_vcg = self.vcg[self.small_cap]
        self.LMT = self.cap[self.mid_cap[0]]
        self.MST = self.cap[self.mid_cap[-1]]
        x = []
        y = []
        d = []
        for i in range(len(self.vcg)):
            idx = self.vcg.index[i]
            ytemp = 100 * (1 + (np.log(self.cap.loc[idx]) - np.log(self.MST)) / (np.log(self.LMT) - np.log(self.MST)))
            y.append(ytemp)
            if ytemp > 200:
                xtemp = 100 * (1 + (self.vcg.iloc[i] - self.big_vcg.quantile(1 / 3)) / (self.big_vcg.quantile(2 / 3) - self.big_vcg.quantile(1 / 3)))
            elif ytemp < 100:
                xtemp = 100 * (1 + (self.vcg.iloc[i] - self.small_vcg.quantile(1 / 3)) / (self.small_vcg.quantile(2 / 3) - self.small_vcg.quantile(1 / 3)))
            else:
                xtemp = 100 * (1 + (self.vcg.iloc[i] - self.mid_vcg.quantile(1 / 3)) / (self.mid_vcg.quantile(2 / 3) - self.mid_vcg.quantile(1 / 3)))
            x.append(xtemp)
            d.append(idx)
        xdf = pd.DataFrame(x, index=d)
        ydf = pd.DataFrame(y, index=d)
        self.stock_res = pd.concat([xdf, ydf], axis=1)
        self.stock_res.columns = ['x', 'y']

    # repo_date数据类型为datetime.date
    def cal_fund(self, repo_date, aux_date):
        fund_list = self._basic_api.get_fund_info()
        fund_list = fund_list[(fund_list.wind_class_1 == '股票型基金') | (fund_list.wind_class_2.isin(['普通股票型基金', '偏股混合型基金', '被动指数型基金', '增强指数型基金', '平衡混合型基金', '灵活配置型基金', '股票多空']))]
        fund_list = fund_list[fund_list.end_date > repo_date]
        self.flist = fund_list[['wind_id', 'fund_id']].set_index('wind_id').to_dict()['fund_id']
        xres = []
        yres = []
        dres = []
        # dtemp = []
        repo_str = repo_date.strftime('%Y%m%d')
        aux_str = aux_date.strftime('%Y%m%d')
        # wind的数据更新起来不太方便，我们手工从Choice下载了这部分数据，所以这里换成了Choice的，但是注意这部分数据没有历史，跑历史的话应该返回去用wind的
        # temp_list = self._raw_api.get_wind_fund_stock_portfolio(start_date=repo_str, end_date=repo_str, wind_fund_list=list(self.flist.keys()))
        # 2020年中报开始使用Choice的数据
        temp_list = self._raw_api.get_em_fund_stock_portfolio(start_date=repo_str, end_date=repo_str)
        aux_temp_list = self._raw_api.get_em_fund_stock_portfolio(start_date=aux_str, end_date=aux_str)
        aux_temp_list = aux_temp_list[~aux_temp_list.em_id.isin(set(temp_list.em_id.array))]
        temp_list = pd.concat([temp_list, aux_temp_list])
        for item, fund_id in self.flist.items():
            # print(item+ ': ' +str(c)+'/'+str(l))
            temp = temp_list[temp_list.em_id == item]
            if len(temp) == 0:
                continue
            temp_data = temp[['stock_id', 'stock_mv']]
            temp_data = temp_data.reset_index()
            temp_data['weight'] = temp_data['stock_mv'] / (temp_data['stock_mv'].sum())
            xf = 0
            yf = 0
            wf = 0
            for i in range(len(temp_data)):
                idx = temp_data.stock_id[i]
                if idx in self.stock_res.index:
                    wf += temp_data.weight[i]
                    xf += temp_data.weight[i] * self.stock_res.loc[idx].x
                    yf += temp_data.weight[i] * self.stock_res.loc[idx].y
                else:
                    # print('Error, Stock Data Missing: ' + idx)
                    continue
            if wf <= 0.5:
                # print(item + 'We do not have enough stock data')
                continue

            xf = xf / wf
            yf = yf / wf
            xres.append(xf)
            yres.append(yf)
            dres.append(fund_id)
            # dtemp.append(repo_str)
        xres_df = pd.DataFrame(xres, index=dres)
        yres_df = pd.DataFrame(yres, index=dres)
        # dtemp = pd.DataFrame(dtemp, index=dres)
        # print(xres_df, yres_df, dtemp)
        self.fund_res = pd.concat([xres_df, yres_df], axis=1)
        # self.fund_res = pd.concat([dtemp, self.fund_res], axis=1)
        self.fund_res = self.fund_res.reset_index()
        self.fund_res.columns = ['fund_id', 'x', 'y']

    def process(self, start_date, end_date):
        failed_tasks = []
        try:
            self.init(start_date, end_date)
            self.cal_stock()
            real_date, aux_date = RawDataHelper.get_prev_and_aux_target_dates(end_date, SEMI_UPDATE_DATE_LIST)
            self.cal_fund(real_date, aux_date)
            # # 获取当前的style box
            # now_df = DerivedDataApi().get_fund_style_box(datetime=real_date)
            # if now_df is not None and not now_df.empty:
            #     # 过滤出来新增基金style box以及旧基金的style box发生变化的情况
            #     self.fund_res = self.fund_res.round(12).merge(now_df.drop(columns=['_update_time']), how='left', on=['fund_id', 'datetime', 'x', 'y'], indicator=True, validate='one_to_one')
            #     self.fund_res = self.fund_res[self.fund_res._merge == 'left_only'].drop(columns=['_merge'])
            # TODO: 最好原子提交下边两步
            # DerivedDataApi().delete_fund_style_box(real_date, self.fund_res.fund_id.to_list())
            self.fund_res['datetime'] = end_date
            self._data_helper._upload_derived(self.fund_res, StyleBox.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('style_box')
        return failed_tasks


if __name__ == "__main__":
    date = '20210111'
    sbg = StyleBoxGenerator(DerivedDataHelper())
    sbg.process(date, date)
