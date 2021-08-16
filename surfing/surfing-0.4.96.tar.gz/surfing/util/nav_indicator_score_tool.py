import pandas as pd
import numpy as np
from functools import partial
import datetime
import time
import matplotlib.pyplot as plt
from ..resource.data_store import DataStore
from ..data.manager.manager_fund import FundDataManager
from ..data.manager.score import ScoreFunc
import dataclasses

@dataclasses.dataclass
class AssetStd:
    csi500: dict=None
    gold: dict=None
    hs300: dict=None
    mmf: dict=None
    gem: dict=None
    national_debt: dict=None
    sp500rmb: dict=None    

    # std = mean of std of each day each index
    def __post_init__(self):
        self.csi500 = self.csi500 or {'alpha':0.058899, 'fee_rate':0.003143, 'track_err':0.053827}
        self.gold = self.gold or  {'alpha':0.023139, 'fee_rate':0.003098, 'track_err':0.039580}
        self.hs300 = self.hs300 or {'alpha':0.034698, 'fee_rate':0.002682, 'track_err':0.038223}
        self.mmf = self.mmf or {'alpha':0.002942, 'fee_rate':0.000839, 'track_err':0.000626}
        self.gem = self.gem or {'alpha':0.062848, 'fee_rate':0.004320, 'track_err':0.058874}
        self.national_debt = self.national_debt or {'alpha':0.061111, 'fee_rate':0.002268, 'track_err':0.044224}
        self.sp500rmb = self.sp500rmb or {'alpha':0.012287, 'fee_rate':0.002262, 'track_err':0.009384}   

class FundIndicatorProcessor():

    TRADING_DAYS_PER_YEAR = 242
    NATURAL_DAYS_PER_YEAR = 365
    SHORT_TIME_SPAN = TRADING_DAYS_PER_YEAR
    LONG_TIME_SPAN = TRADING_DAYS_PER_YEAR * 3
    LONG_TERM_INDEX = ['hs300', 'csi500', 'mmf']
    MIN_TIME_SPAN = int(TRADING_DAYS_PER_YEAR / 4)#为了延长基金回测范围，评分最低年限3个月
    RISK_FEE_RATE = 0.025
    RISK_FEE_RATE_PER_DAY = RISK_FEE_RATE / TRADING_DAYS_PER_YEAR

    def __init__(self, dm:FundDataManager=None):
        self.dm = dm
        
    def init(self,  fund_ret_days:int=1,
                    index_id:str='hs300',
                    fund_list:list=None,
                    time_span:int=None,
                    if_min_time_span:bool=True,
                    min_time_span:int=None,
                    start_date:datetime.date=datetime.date(2015,1,1),
                    end_date:datetime.date=datetime.date(2020,6,19),
                    is_filter_c:bool=True,
                    if_normalize_devide_predecide_std:bool=False,
                    fund_id:str='673100!0',
                    func:ScoreFunc=ScoreFunc(alpha=0.3, beta=-0.6, fee_rate=-0.1),
                    if_rank_plot_only:bool=False):
        # 计算基金和大类资产指数收益考虑的天数， 默认1天
        # fund_list 计算指标基金列表 默认算资产下全部基金
        # time_span 计算指标考虑天数 默认hs300 csi500 3年，其他1年
        # min_time_span 计算指标最小天数 默认3月
        # if_min_time_span 计算指标是否天数不足，设置最小时间
        self.fund_ret_days = fund_ret_days
        
        self.time_span = time_span if time_span else self.get_time_span(index_id)
        if not if_min_time_span:
            self.min_time_span = time_span
        else:
            self.min_time_span = min_time_span if min_time_span else self.MIN_TIME_SPAN
        self.start_date = start_date
        self.end_date = end_date
        self.fund_nav = self.dm.dts.fund_nav.copy()
        self.fund_info = self.dm.dts.fund_info.copy()
        self.index_price = self.dm.dts.index_price.copy()
        self.is_filter_c = is_filter_c
        self.if_normalize_devide_predecide_std = if_normalize_devide_predecide_std
        self.fund_id = fund_id
        self.func = func if func else self.dm._score_manager.funcs.get(index_id)
        self.index_id = index_id
        self.if_rank_plot_only = if_rank_plot_only
        # 指数日线价格和基金净值 时间轴对齐 ，避免join后因为日期不存在出现价格空值
        # 指数数据历史上出现非交易日有数据，join后，基金净值出现空值，长周期时间序列算指标出空值 
        # 避免对日收益fillna(0)， 造成track error 计算不符合实际
        # 计算逻辑空值填充情况： 1. 只对基金费率空值fillna(0) 
        #                    2. manager fund 里对日线价格ffill
        #                    3. 指数数据按照基金数据重做index后ffill(有基金数据对日子,没有指数数据，比如季报出在季度末，非交易日有基金净值)
        #                    4. 有对超过基金终止日净值赋空值
        end_date = min(self.fund_nav.index[-1], self.index_price.index[-1])
        self.fund_nav = self.fund_nav.loc[:end_date]
        self.index_price = self.index_price[:end_date]
        fund_nav_index = self.fund_nav.index
        self.index_price = self.index_price.reindex(fund_nav_index).fillna(method = 'ffill')
        l1 = self.fund_nav.index.to_list().sort()
        l2 = self.index_price.index.to_list().sort()
        assert l1 == l2, f'date index of index price and fund nav are not identical, l1 {l1} lens {len(l1)}, l2 {l2} lens {len(l2)}'

        fund_to_enddate_dict = self.fund_info[['fund_id', 'end_date']].set_index('fund_id').to_dict()['end_date']
        self.fund_to_index_dict = self.fund_info[['fund_id', 'index_id']].set_index('fund_id').to_dict()['index_id']
        # 超过基金终止日的基金净值赋空
        for fund_id in self.fund_nav.columns:
            fund_end_date = fund_to_enddate_dict[fund_id]
            if self.end_date > fund_end_date:
                self.fund_nav.loc[fund_end_date:,fund_id] = np.nan

        self.fund_ret = np.log(self.fund_nav / self.fund_nav.shift(self.fund_ret_days))
        self.fund_ret = self.fund_ret.stack().reset_index(level=[0,1]).rename(columns={0:'ret'})        
        self.fund_ret['index_id'] = self.fund_ret.fund_id.apply(lambda x: self.fund_to_index_dict[x])
        self.fund_ret = self.fund_ret.pivot_table(index = ['index_id','datetime'],columns='fund_id',values='ret')
        self.index_ret = np.log(self.index_price / self.index_price.shift(self.fund_ret_days))
        self.fund_to_index_dict = {fund_id:index_id for fund_id,index_id in self.fund_to_index_dict.items() if fund_id in self.fund_ret.columns}
        self.index_list = self.fund_ret.index.levels[0]
        self.index_fund = { index_id : [fund_idx for fund_idx, index_idx in self.fund_to_index_dict.items() if index_idx == index_id] for index_id in self.index_list}
        self.start_date_dic = self.fund_info[['fund_id','start_date']].set_index('fund_id').to_dict()['start_date']
        self.fund_list = fund_list if fund_list else self.index_fund[index_id]

    def get_time_span(self, index_id):
        if index_id in self.LONG_TERM_INDEX:
            return self.LONG_TIME_SPAN
        else:
            return self.SHORT_TIME_SPAN

    def _rolling_alpha_beta(self, x, res, df):
        # 回归相关的都在这里 
        df_i = df.loc[x[0]:x[-1],]
        return self.regression_ralated_indicator(res,df_i)

    def regression_ralated_indicator(self, res, df_i):
        if sum(df_i.fund_ret) == 0:
            res.append({'alpha':np.Inf,'beta':np.Inf})
            return 1
        else:
            ploy_res = np.polyfit(y=df_i.fund_ret, x=df_i.benchmark_ret, deg=1)
            p = np.poly1d(ploy_res)
            beta = ploy_res[0]
            alpha = ploy_res[1] * 242
            res.append({'alpha': alpha, 
                        'beta': beta})
            return 1

    def indicator_calculator_item(self, fund_id:str):
        index_ret = self.index_ret[[self.index_id]].loc[self.start_date: self.end_date]
        df = self.fund_ret.loc[self.index_id][[fund_id]].loc[self.start_date: self.end_date].join(index_ret).dropna()
        df = df.rename(columns={self.index_id:'benchmark_ret', fund_id:'fund_ret'}).reset_index()
        df['year_length'] = df['datetime'].map(lambda x:(x-self.start_date_dic[fund_id]).days / self.NATURAL_DAYS_PER_YEAR)
        res = []
        pd.Series(df.index).rolling(
             window=self.time_span, min_periods=self.min_time_span).apply(
            partial(self._rolling_alpha_beta, res=res, df=df), raw=True)
        df = df.set_index('datetime')
        df = df.join(pd.DataFrame(res,index=df.index[-len(res):]))    
        df['track_err'] = (df.fund_ret - df.benchmark_ret).rolling(window=self.time_span, min_periods=self.min_time_span).std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        df['fund_id'] = fund_id
        df['timespan'] = int(self.time_span / self.TRADING_DAYS_PER_YEAR)
        df['fee_rate'] = self.fund_fee[fund_id]
        return df.dropna()
        
    def indicator_calculator(self):
        # 评分无关的这里均不计算
        _tm_indicator_begin = time.time()
        self.fund_fee = self.fund_info[['fund_id','manage_fee','trustee_fee']].set_index('fund_id').fillna(0).sum(axis = 1)
        result = []
        for fund_id in self.fund_list:
            res_i = self.indicator_calculator_item(fund_id)
            result.append(res_i)
        self.fund_indicator = pd.concat(result, axis=0, sort=True).replace(np.Inf,None).replace(-np.Inf,None).dropna(subset=['beta', 'alpha','track_err']).drop(['fund_ret','benchmark_ret','timespan'], axis=1)
        _tm_indicator_end = time.time()
        print(f'calculate fund indicator with fund number {len(self.fund_list)} from {self.start_date} to {self.end_date} cost time :{round(_tm_indicator_end - _tm_indicator_begin, 2)}s')
        self.index_fund_indicator_pack = self.fund_indicator.pivot_table(index=['datetime', 'fund_id'])

    def score_calculator_item(self, dt):
        cur_d = self.index_fund_indicator_pack.loc[dt]
        fund_id_list = cur_d.index.tolist()
        fund_id_list_new = self.dm._score_manager._filter_size_and_com_hold(dt, fund_id_list, self.index_id)
        if  bool(set(fund_id_list) & set(fund_id_list_new)):
            cur_d = cur_d.reindex(fund_id_list_new).dropna()
        if cur_d.shape[0] > 1:
            if self.if_normalize_devide_predecide_std:
                for indi_i in ['alpha','fee_rate','track_err']:
                    cur_d[indi_i] = cur_d[indi_i] / AssetStd().__dict__[self.index_id][indi_i]
            nd_array = cur_d[['alpha','fee_rate','track_err']].to_numpy()
            if not self.if_normalize_devide_predecide_std:
                nd_array_calc = np.apply_along_axis(lambda x: (x - x.mean() + 1e-8)/ (x.std(ddof=1) + 1e-8), 0, nd_array)
            else:
                nd_array_calc = nd_array
            nd_array_same = cur_d[['beta']].to_numpy()
            indicator_ndarry = np.concatenate([nd_array_calc,nd_array_same], axis=1)
            normalized_indicator = pd.DataFrame(indicator_ndarry,index=cur_d.index, columns=['alpha','fee_rate','track_err','beta']).reset_index()
            normalized_indicator['datetime'] = dt
            score_list = np.apply_along_axis(lambda x: self.func.get(x), 1, indicator_ndarry)
            score_raw = pd.Series(score_list,index=cur_d.index)
            if self.index_id in self.dm._score_manager.score_penalty_param.FilterYearIndex:
                punish_funds = cur_d[cur_d.year_length < self.dm._score_manager.score_penalty_param.JudgeYearLength].index.tolist()
                for _fund_id in punish_funds:
                    score_raw[_fund_id] += self.dm._score_manager.score_penalty_param.Penalty
            score = (score_raw - score_raw.min()) / (score_raw.max() - score_raw.min())
            if self.is_filter_c:
                score = self.dm._score_manager._filter_score(score)
            score = { fund_id: s for fund_id, s in score.iteritems() }
            score_raw = { fund_id: s for fund_id, s in score_raw.iteritems() }
        else:
            score_raw = {cur_d.index[0]:1}
            score = score_raw
        return score, score_raw, normalized_indicator

    def score_calculator(self):
        _tm_score_start = time.time()
        self.score_cache = {}
        self.score_raw_cache = {}
        pad = self.fund_indicator.pivot_table(index=['datetime'])
        self.normalized_df = []
        for dt in pad.index:
            self.score_cache[dt] = {}
            self.score_raw_cache[dt] = {}
            score, score_raw, normalized_indicator = self.score_calculator_item(dt)
            self.normalized_df.append(normalized_indicator)
            self.score_cache[dt][self.index_id] = score
            self.score_raw_cache[dt][self.index_id] = score_raw
        _tm_score_end = time.time()
        self.normalized_df = pd.concat(self.normalized_df)
        print(f'calculate score cost {round(_tm_score_end - _tm_score_start, 2)}')

    def get_fund_rank(self, select_num=10):
        result = []
        score_dic = self.score_raw_cache
        fund_info = self.dm.dts.fund_info
        for d in score_dic:
            if not self.index_id in score_dic[d]:
                continue
            else:
                dic = score_dic[d][self.index_id]
                top_funds = [_[0] for _ in sorted(dic.items(),key=lambda x:x[1], reverse=True)]
                num = min(len(top_funds), select_num)
                dic = {
                    'datetime':d,
                    'rank_list': top_funds[:num]
                }            
            result.append(dic)
        df = pd.DataFrame(result).set_index('datetime')  
        rank_result = []
        for d, r in df.iterrows():
            if self.fund_id in r.rank_list:
                loc = r.rank_list.index(self.fund_id)
            else:
                loc = None
            rank_result.append({'datetime':d,'rank':loc})
        rank_df_fund = pd.DataFrame(rank_result).dropna().set_index('datetime')
        return rank_df_fund

    def get_fund_score(self):
        score_dic = self.score_raw_cache
        score_result = []
        for d in score_dic:
            if not self.index_id in score_dic[d]:
                continue
            if self.fund_id in score_dic[d][self.index_id]:
                dic = {}
                dic['datetime'] = d
                dic['score_raw'] =  score_dic[d][self.index_id][self.fund_id]
                score_result.append(dic)
        return pd.DataFrame(score_result).set_index('datetime')

    def fund_analysis(self):
        nav_df = self.dm.dts.fund_nav[[self.fund_id]].dropna()
        index_df = self.dm.dts.index_price[[self.index_id]]
        fund_indicator_fund_i = self.fund_indicator[self.fund_indicator.fund_id == self.fund_id]

        price_ratio = nav_df.join(index_df).fillna(method='ffill')
        price_ratio = price_ratio / price_ratio.iloc[0]
        price_ratio['price_ratio'] = price_ratio[self.fund_id] / price_ratio[self.index_id]
        score_df = self.get_fund_score()
        if not self.if_rank_plot_only:
            nav_df.plot.line(figsize=(12,6))       
            plt.title(f'fund nav {self.fund_id}', fontsize=17)
            plt.grid()
            price_ratio[[self.index_id]].plot.line(figsize=(12,6))
            plt.title(f'index {self.index_id} price', fontsize=17)
            plt.grid()
            price_ratio[['price_ratio']].plot.line(figsize=(12,6))
            plt.title(f'fund {self.fund_id} index {self.index_id} price ratio', fontsize=17)
            plt.grid()
            indicator_list = ['alpha','beta','track_err']
            for indicator in indicator_list:
                fund_indicator_fund_i[[indicator]].plot.line(figsize=(12,6))
                plt.title(f'fund {self.fund_id} {indicator}', fontsize=17)
                plt.grid()
            score_df.plot.line(figsize=(16,8))
            plt.title(f'fund {self.fund_id} score raw',fontsize=17)
            plt.grid()
            fund_indicator_after_normalized = self.normalized_df[self.normalized_df.fund_id == self.fund_id].copy()
            for indicator, w in self.func.__dict__.items():
                if indicator != 'beta':
                    fund_indicator_after_normalized.loc[:,f'{indicator}_component'] = abs(fund_indicator_after_normalized[indicator] * w)
                else:
                    fund_indicator_after_normalized.loc[:,f'{indicator}_component'] = abs((1 - fund_indicator_after_normalized[indicator]) * w)
            stack_df = fund_indicator_after_normalized[['alpha_component','beta_component','track_err_component','fee_rate_component']]
            stack_df = stack_df.div(stack_df.sum(axis=1).values,axis=0)
            stack_df.plot.area(figsize=(18,9),legend=False,fontsize = 17)
            plt.title('score components', fontsize=17)
            plt.legend(loc='lower left',fontsize = 14)
            plt.suptitle(str(self.func.__dict__),y=0.87,fontsize=17)
            plt.show()
        rank_df_fund = self.get_fund_rank(select_num=150)
        rank_df_fund.plot.line(figsize=(16,8))
        plt.title(f'fund {self.fund_id} rank',fontsize=17)
        plt.grid()
        plt.show()
    
    def analysis(self):
        self.indicator_calculator()
        self.score_calculator()
        self.fund_analysis()

if __name__ == "__main__":
    dm = DataStore.load_dm()
    fi = FundIndicatorProcessor(dm=dm)
    #全默认值
    fi.init(fund_ret_days=1,
            index_id='hs300',
            fund_list=None,
            time_span=None,
            if_min_time_span=True,
            min_time_span=None, 
            start_date=datetime.date(2015,1,1),
            end_date=datetime.date(2020,6,19),
            is_filter_c=True,
            if_normalize_devide_predecide_std=False,
            fund_id='673100!0',
            func=ScoreFunc(alpha=0.3, beta=-0.6, fee_rate=-0.1),
            if_rank_plot_only=False)
    fi.analysis()