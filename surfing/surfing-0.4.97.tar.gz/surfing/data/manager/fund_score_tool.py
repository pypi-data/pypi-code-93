import matplotlib as mpl
import pylab as pl
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from ...fund.engine.tuner import ScoreTuner
from ...fund.engine.backtest import *
from ...resource.data_store import DataStore
from .score import ScoreFunc
from ...util.calculator import Calculator
from .manager_fund import FundDataManager
from ..struct import AssetTrade, FundTrade, FundScoreParam, TAAParam, TaaTunerParam, AssetTradeParam, AssetWeight, AssetTimeSpan

class FundScoreTool:

    '''
    收益能力因子:  alpha ret_over_period treynor m_square annual_ret time_ret alpha_w jensen_alpha_m treynor_ratio_m
    均衡能力因子:  info_ratio sharpe calmar_ratio_m information_ratio_m sharpe_ratio_m
    风险能力因子:  beta down_risk mdd var annual_vol beta_w beta_m
    跟踪能力因子:  track_err track_err_w
    费用能力因子:  fee_rate
    '''

    INDICATOR_SIGN={
        'alpha':1,
        'beta':-1,
        'fee_rate':-1,
        'track_err':-1,
        'down_risk':-1,
        'info_ratio':1,
        'ret_over_period':1,
        'treynor':1,
        'mdd':-1,
        'm_square':1,
        'var':-1,
        'r_square':0, #解释 beta alpha 有效性
        'sharpe':1,
        'annual_ret':1,
        'annual_vol':-1,
        'time_ret':1,
        'alpha_w':1,
        'beta_w':-1,
        'track_err_w':-1,
        'beta_m':-1,
        'calmar_ratio_m':1,
        'information_ratio_m':1,
        'jensen_alpha_m':1,
        'sharpe_ratio_m':1,
        'treynor_ratio_m':1,
    }

    def __init__(self):
        self.index_list = list(AssetTimeSpan().__dict__.keys())

    def init(self):
        self.dm = DataStore.load_dm()
        self.desc_dic = self.dm.dts.fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']
        self.calculate_std()

    def recent_day(self, dt, duration):
        dts = self.dm.dts.trading_days.datetime
        dts = dts[dts > dt].values
        return dts[0], dts[duration]

    def calculate_std(self):
        dts = self.dm.dts.trading_days.datetime
        dts = dts[dts > datetime.date(2019,1,1)] #todo
        res = []
        for index_id in self.index_list:
            fund_indicator_index = self.dm.dts.fund_indicator[self.dm.dts.fund_indicator.index_id == index_id]
            for dt in dts:
                std_dic = fund_indicator_index[fund_indicator_index.datetime == dt].std(ddof=1).to_dict()
                std_dic['datetime'] = dt
                std_dic['index_id'] = index_id
                res.append(std_dic)
        
        self.indicator_daily_std = pd.DataFrame(res)
        self.indicator_std_mean = self.indicator_daily_std.groupby('index_id').mean()
        self.indicator_list = [i for i in self.indicator_daily_std.columns.tolist() if i not in ['year_lenght','index_id','fund_id']]


    def make_score_equation(self, index_id:str='hs300', score_weight:ScoreFunc=ScoreFunc()):
        score_dict = {}
        for indicator, w in score_weight.__dict__.items():
            if w != 0:
                if indicator in ['beta', 'beta_w', 'beta_m']:
                    score_w = self.INDICATOR_SIGN[indicator] * w
                else:
                    score_w = self.INDICATOR_SIGN[indicator] * w / getattr(self.indicator_std_mean.loc[index_id], indicator)
                score_i = {indicator: score_w}
                score_dict.update(score_i)
        return ScoreFunc(**score_dict)

    def fund_score_tool(self, begin_date:datetime.date=datetime.date(2015,1,1),
                              duration:int=242,
                              fund_num_list:list=[1,2,5,10],
                              score_func:ScoreFunc=ScoreFunc(alpha=0.9,beta=-0.1),
                              is_divide_by_std:bool=True,
                              index_id:str='hs300'):

        begin_date, end_date = self.recent_day(begin_date, duration)
        if is_divide_by_std:
            score_func = self.make_score_equation(index_id, score_func)
        index_price = self.dm.dts.index_price.loc[begin_date:end_date,[index_id]].copy()
        normalized_indicator = self.dm.dts.index_fund_indicator_pack.loc[index_id].loc[begin_date]
        if index_id == 'national_debt':
            time_span = AssetTimeSpan().__dict__[index_id]
            normalized_indicator = normalized_indicator[normalized_indicator.year_length > time_span]    
        score_raw = normalized_indicator.apply(lambda x: score_func.get(x), axis=1)
        top_fund_list = pd.DataFrame(score_raw).sort_values(0,ascending=False).index.tolist()
        indicators = [indicator for indicator, w in score_func.__dict__.items() if w != 0]
        fund_res = []
        for select_num in fund_num_list:
            select_funds = top_fund_list[:select_num] if select_num < len(top_fund_list) else top_fund_list
            col = f'top_{select_num}'
            fund_nav_i = self.dm.dts.fund_nav[select_funds].loc[begin_date:end_date].copy()
            fund_nav_i = fund_nav_i/fund_nav_i.iloc[0]
            fund_nav_i.loc[:,col] = fund_nav_i.mean(axis=1)
            fund_res.append(fund_nav_i[[col]].copy())
        fund_df = pd.concat(fund_res,axis=1,sort=False)
        index_price = index_price / index_price.iloc[0]
        fund_df = fund_df.join(index_price).fillna(method='ffill')
        fund_df.plot.line(figsize=(16,8))
        plt.title('top fund compare', fontsize=20)
        plt.legend(loc='upper right',fontsize=18)
        plt.grid()
        plt.show()
        result_df = normalized_indicator[indicators].loc[top_fund_list[:max(fund_num_list)]]
        result_df.loc[:,'desc_name'] = result_df.index.map(lambda x : self.desc_dic[x])
        result_df.loc[:,'score'] = result_df.index.map(lambda x: score_raw[x])
        result_df = result_df.reset_index()
        result_df.loc[:,'rank'] = result_df.index + 1
        annual_ret = []
        annual_vol = []
        sharpe = []
        mdd = []
        for fund_id in result_df.fund_id:
            res = Calculator.get_stat_result_from_df(df=fund_nav_i[[fund_id]].reset_index(), date_column='datetime', value_column=fund_id)
            annual_ret.append(res.annualized_ret)
            annual_vol.append(res.annualized_vol)
            mdd.append(res.mdd)
            sharpe.append(res.sharpe)
        result_df['mdd'] = mdd
        result_df['annual_ret'] = annual_ret
        result_df['annual_vol'] = annual_vol
        result_df['sharpe'] = sharpe
        res = []
        for group_id in fund_df:
            _res = Calculator.get_stat_result_from_df(df=fund_df[[group_id]].reset_index(), date_column='datetime', value_column=group_id)
            dic = {
                'group':group_id,
                'annual_ret':_res.annualized_ret,
                'annual_vol':_res.annualized_vol,
                'sharpe':_res.sharpe,
                'mdd':_res.mdd,
            }
            res.append(dic)
        col = ['fund_id','desc_name'] + indicators + ['score','annual_ret','mdd','annual_vol','sharpe']
        result_df = result_df.set_index('rank')[col]
        group_result = pd.DataFrame(res)[['group','annual_ret','annual_vol','mdd','sharpe']]
        return group_result, result_df

class SingleIndexFundScore:

    def __init__(self):
        pass

    def backtest(self, m, index_id, max_fund_number, fund_trade_selection, begin_date, score_func):
        saa = AssetWeight(**{index_id:1})
        t = FundTrader(AssetTradeParam(), FundTradeParam(JudgeIndexDiff=1,JudgeFundSelection=fund_trade_selection))
        fa_param = FAParam(MaxFundNumUnderAsset=max_fund_number)
        funcs = {index_id:score_func }
        begin_date = begin_date

        self.bk = FundBacktestEngine(data_manager=m, trader=t, fa_params=fa_param, fund_score_funcs=funcs)
        self.bk.init()
        self.bk.run(saa=saa, start_date=begin_date)
        self.bk_result = self.bk.get_fund_result()

    def get_result(self):
        return pd.DataFrame([self.bk_result])[['annual_ret','annual_vol','sharpe','mdd','mdd_d1','mdd_d2','turnover_rate_yearly_avg','rebalance_times']]

    def plot(self):
        self.bk._report_helper.singel_index_plot()

    def get_rebalance_detail(self):
        return self.bk._report_helper.get_rebalance_detail()

    def get_trade_history(self):
        return self.bk._report_helper.get_fund_trade()



    