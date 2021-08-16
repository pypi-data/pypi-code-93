import time
import datetime
import pandas as pd
import numpy as np
from pprint import pprint 
import operator
import traceback
import concurrent.futures
import os
from .backtest import FundBacktestEngine
from .trader import AssetTrader
from ...data.manager.manager_fund import FundDataManager
from ...data.struct import AssetTrade, FundTrade, FundScoreParam, TAAParam, TaaTunerParam, AssetTradeParam, AssetWeight, AssetTimeSpan
from ...data.api.derived import DerivedDataApi
from ...data.manager.score import ScoreFunc

class TaaTuner:

    BACKTEST_NUM = 3
    INDEX_WEIGHT = 0.1
    CASH_WEIGHT = 0.9
    TAA_LOW_TYPE = 'taa_low_only'
    TAA_UP_TYPE = 'taa_up_only'

    def __init__(self, start_time:str='20050101', end_time:str='20200501'):
        self.dm = FundDataManager(start_time=start_time, end_time=end_time)
        self.start_date = datetime.datetime.strptime(start_time, '%Y%m%d').date()
        self.end_date = datetime.datetime.strptime(end_time, '%Y%m%d').date()
        self.ap = AssetTradeParam()
        self.at = AssetTrader(self.ap)

    def init(self, taa_tuner:TaaTunerParam ):
        self.dm.init(score_pre_calc=False)
        self.taa_tuner = taa_tuner
        self.saa = AssetWeight(**{'cash':self.CASH_WEIGHT, self.taa_tuner.index_id:self.INDEX_WEIGHT})
        self.taa_type = self.TAA_LOW_TYPE if self.taa_tuner.IsTaaLowOnly else self.TAA_UP_TYPE
        self.bk_each_time = None

    def grid_search(self):
        self.run_saa()
        self.test_bk_time()
        self.search_bk()
        self.first_round_analysis()
        self.search_bk_2()
        self.second_round_analysis()

    def run_saa(self):
        saa_bk = FundBacktestEngine(data_manager=self.dm, trader=self.at, taa_params=None)
        saa_bk.init()
        saa_bk.run(saa=self.saa, start_date=self.start_date, end_date=self.end_date)
        self.saa_result = saa_bk._report_helper.get_asset_stat()
        
    def search_bk(self, is_test:bool=False, bk_list=None):
        if bk_list is None:
            if is_test:
                taa_param_list = self.taa_tuner.param_list[:self.BACKTEST_NUM]
            else:
                taa_param_list = self.taa_tuner.param_list
        else:
            taa_param_list = bk_list

        self.result = []
        c = 1
        bk_num = len(taa_param_list)
        if self.bk_each_time is not None:
            cost_min = len(taa_param_list) * self.bk_each_time / 60
            print(f'totally bk {bk_num} tasks index_id: {self.taa_tuner.index_id} may cost {cost_min} mins')
        else:
            print(f'totally bk {bk_num} tasks index_id: {self.taa_tuner.index_id}')
        for taa_i in taa_param_list:
            t_0 = time.time()
            taa_bk_i = FundBacktestEngine(data_manager=self.dm, trader=self.at, taa_params=taa_i)
            taa_bk_i.init()
            taa_bk_i.run(saa=self.saa, start_date=self.start_date, end_date=self.end_date)
            taa_result = taa_bk_i._report_helper.get_asset_stat()
            dic = taa_i.__dict__
            dic['taa_ret'] = taa_result['annual_ret']
            self.result.append(dic)
            t_1 = time.time()
            print(f'finish task {c}, cost {t_1 - t_0} sec')
            c += 1
        self.result = pd.DataFrame(self.result)
        self.result['saa_annual_ret'] = self.saa_result['annual_ret']
        self.result['taa_saa_annual_ret'] = self.result['taa_ret'] - self.saa_result['annual_ret']
        self.result['taa_type'] = self.taa_type
        self.result = self.result.sort_values('taa_saa_annual_ret', ascending=False)
        print()

    def test_bk_time(self):
        print()
        print('test backtest')
        t_0 = time.time()
        self.search_bk(is_test=True)
        t_1 = time.time()
        cost_time = t_1 - t_0
        self.bk_each_time = cost_time / self.BACKTEST_NUM
        print(f'bk {self.BACKTEST_NUM} times total cost {cost_time} sec, each bk {self.bk_each_time} sec')
        t_1 = time.time()
        task_num = len(self.taa_tuner.param_list)
        print(f'first round backtest may cost {task_num * self.bk_each_time / 60} mins')
        print()

    def first_round_analysis(self): 
        self.result.to_csv(f'{self.taa_tuner.index_id}_{self.taa_type}_round1.csv')
        self.first_round_result = self.result.iloc[0]
        print('first round filter result')
        pprint(self.first_round_result)
        print()

    def search_bk_2(self):
        d = self.first_round_result 
       
        self.bk_params = []
        if d.taa_type == self.TAA_UP_TYPE:
            LowThreshold = d.LowThreshold
            LowStop = d.LowStop
            LowPlus = d.LowPlus
            for HighMinus in [_ for _ in range( int(d.HighMinus * 100) - 1,int(d.HighMinus * 100) + 2, 1)]:
                for HighStop in [_ for _ in range( int(d.HighStop * 100) - 2,int(d.HighStop * 100) + 3, 1)]:
                    for HighThreshold  in [_ for _ in range( int(d.HighThreshold * 100) - 2,int(d.HighThreshold * 100) + 3, 1)]:
                        t = TAAParam()
                        t.HighThreshold = HighThreshold / 100
                        t.HighStop = HighStop / 100
                        t.HighMinus = HighMinus / 100
                        t.LowStop = LowStop 
                        t.LowThreshold = LowThreshold 
                        t.LowPlus = LowPlus 
                        t.TuneCash = True
                        self.bk_params.append(t)
        else:
            HighThreshold = d.HighThreshold
            HighStop = d.HighStop
            HighMinus = d.HighMinus
            for LowPlus in [_ for _ in range( int(d.LowPlus * 100) - 1,int(d.LowPlus * 100) + 2, 1)]:
                for LowStop in [_ for _ in range( int(d.LowStop * 100) - 2,int(d.LowStop * 100) + 3, 1)]:
                    for LowThreshold in [_ for _ in range( int(d.LowThreshold * 100) - 2,int(d.LowThreshold * 100) + 3, 1)]:
                        t = TAAParam()
                        t.HighThreshold = HighThreshold
                        t.HighStop = HighStop
                        t.HighMinus = HighMinus
                        t.LowStop = LowStop / 100
                        t.LowThreshold = LowThreshold / 100
                        t.LowPlus = LowPlus / 100
                        t.TuneCash = True
                        self.bk_params.append(t)
        self.search_bk(is_test=False, bk_list=self.bk_params)
        
    def second_round_analysis(self):
        self.result.to_csv(f'{self.taa_tuner.index_id}_{self.taa_type}_round2.csv')
        self.second_round_result = self.result.iloc[0]
        print('second round filter result')
        pprint(self.second_round_result)


class SaaTuner:

    ASSET_LIST = ['hs300', 'csi500', 'gem', 'sp500rmb', 'national_debt', 'gold']
    ROUND1_STEP = 5
    ROUND2_STEP = 1
    ROUND1_CSV = 'saa_tuner_round_1.csv'
    ROUND2_CSV = 'saa_tuner_round_2.csv'
    FINAL_CSV = 'saa_tuner_round_final.csv'

    def __init__(self, start_time:str='20050101', end_time:str='20200520'):
        self.dm = FundDataManager(start_time=start_time, end_time=end_time)
        self.start_date = datetime.datetime.strptime(start_time, '%Y%m%d').date()
        self.end_date = datetime.datetime.strptime(end_time, '%Y%m%d').date()
        self.derived = DerivedDataApi()

    def init(self):
        self.result_round1 = []
        self.result_round2 = []
        self.result_target = []
        self.dm.init(score_pre_calc=False)
        self.get_ports_saa()
        self.test_bk_time()
        
    def tune(self):
        self.first_round()
        self.second_round()
        self.final_round()

    def formal_print(self, sentence):
        print(sentence)
        print()

    def get_ports_saa(self):
        asset_info = self.derived.get_asset_allocation_info()
        asset_info = asset_info[['allocation_id','hs300','csi500','gem','sp500rmb','national_debt','gold','cash']].set_index('allocation_id')
        self.port_saa_dic = asset_info.to_dict('index')

    def bk_unit(self, asset:str, amt_diff:float):
        saa = AssetWeight(**{asset:10/100,'cash':90/100})
        asset_param = AssetTradeParam(EnableCommission=True, PurchaseDiscount=0.15, MinActionAmtDiff=amt_diff) 
        t = AssetTrader(asset_param)
        b = FundBacktestEngine(data_manager=self.dm, trader=t, taa_params=None)
        b.init()
        b.run(saa=saa,start_date=self.start_date, end_date=self.end_date)
        res = b.get_asset_result()
        return {'mdd': res['mdd'], 
                'annual_ret': res['annual_ret'], 
                'ret_over_mdd': res['ret_over_mdd'], 
                'asset': asset, 
                'amt_diff': amt_diff, 
                'start_date': self.start_date, 
                'end_date': self.end_date}

    def bk_unit_target(self, amt_diff:float):
        saa = AssetWeight(    
            hs300=15/100,
            csi500=5/100,
            gem=3/100,
            sp500rmb=7/100,
            national_debt=60/100,
            gold=7/100,
            cash=3/100
        )  
        asset_param = AssetTradeParam(EnableCommission=True, PurchaseDiscount=0.15, MinActionAmtDiff=amt_diff) 
        t = AssetTrader(asset_param)
        b = FundBacktestEngine(data_manager=self.dm, trader=t, taa_params=None)
        b.init()
        b.run(saa=saa,start_date=self.start_date, end_date=self.end_date)
        res = b.get_asset_result()
        return {'mdd': res['mdd'], 
                'annual_ret': res['annual_ret'], 
                'ret_over_mdd': res['ret_over_mdd'], 
                'amt_diff': amt_diff, 
                'start_date': self.start_date, 
                'end_date': self.end_date}
    
    def bk_input_saa_amt_diff(self, saa_dict:dict, amt_diff:float, port_id:int=0):
        try:
            saa = saa_dict#AssetWeight(saa_dict)  
            asset_param = AssetTradeParam(EnableCommission=True, PurchaseDiscount=0.15, MinActionAmtDiff=amt_diff) 
            t = AssetTrader(asset_param)
            b = FundBacktestEngine(data_manager=self.dm, trader=t, taa_params=None)
            b.init()
            b.run(saa=saa,start_date=self.start_date, end_date=self.end_date)
            res = b.get_asset_result()
            res['MinActionAmtDiff'] = amt_diff
            res['start_date'] = self.start_date
            res['end_date'] = self.end_date
            res['port_id'] = port_id
            return res
        except Exception as e:
            print(e)
            traceback.print_exc()
            print('boom')
            print(f'port_id {port_id} amt_diff {amt_diff}')
            print(saa_dict)    
            return None
        
    def test_bk_time(self):
        self.formal_print('test backtest')
        t_0 = time.time()
        asset = self.ASSET_LIST[0]
        amt_diff = [i/1000 for i in range(30,40,2)]
        for amt_diff_i in amt_diff:
            self.bk_unit(asset, amt_diff_i)
        t_1 = time.time()
        cost_time = t_1 - t_0
        self.bk_each_time = cost_time / len(amt_diff)
        self.formal_print(f'bk {len(amt_diff)} times total cost {cost_time} sec, each bk {self.bk_each_time} sec')
        
    def first_round(self):
        loop_layer_1 = self.ASSET_LIST
        loop_layer_2 = [_/10000 for _ in range(100, 905, self.ROUND1_STEP)]
        predict_time = len(loop_layer_1) * len(loop_layer_2) * self.bk_each_time / 60
        self.formal_print(f'###first round bk may cost {predict_time} mins')
        bk_time0 = time.time()
        for asset in loop_layer_1:
            asset_t0 = time.time()
            for amt_diff_i in loop_layer_2:
                self.result_round1.append(self.bk_unit(asset, amt_diff_i))
            asset_t1 = time.time()
            cost_m = (asset_t1 - asset_t0) / 60
            self.formal_print(f' - asset {asset} bk finish cost {cost_m} mins')
        bk_time1 = time.time()
        cost_m = (bk_time1 - bk_time0) / 60
        self.formal_print(f'first round finish cost cost {cost_m} mins')
        pd.DataFrame(self.result_round1).to_csv(self.ROUND1_CSV)

    def second_round(self):
        self.round1_df = pd.read_csv(self.ROUND1_CSV, index_col=0)
        loop_layer_1 = self.ASSET_LIST
        layer_2_lens = len([ i for i in range(-self.ROUND1_STEP+1, self.ROUND1_STEP, self.ROUND2_STEP)])
        predict_time = len(loop_layer_1) * layer_2_lens * self.bk_each_time / 60
        self.formal_print(f'###second round bk may cost {predict_time} mins')
        bk_time0 = time.time()
        for asset in loop_layer_1:
            amt_diff_0 = self.round1_df[self.round1_df.asset == asset].sort_values('ret_over_mdd', ascending=False).amt_diff.values[0]
            amt_diff_int = int(amt_diff_0 * 10000)
            for amt_diff_i in range(amt_diff_int - self.ROUND1_STEP + 1, amt_diff_int + self.ROUND1_STEP, self.ROUND2_STEP):
                amt_diff_i = amt_diff_i / 10000
                self.result_round2.append(self.bk_unit(asset, amt_diff_i))
        bk_time1 = time.time()
        cost_m = (bk_time1 - bk_time0) / 60
        self.formal_print(f'second round finish cost cost {cost_m} mins')
        pd.DataFrame(self.result_round2).to_csv(self.ROUND2_CSV)

    def final_round(self):
        self.round2_df = pd.read_csv(self.ROUND2_CSV, index_col=0)
        res = []
        for asset in self.ASSET_LIST:
            res_i = self.round2_df[self.round2_df.asset == asset].sort_values('ret_over_mdd', ascending=False).reset_index(drop=True).iloc[0]
            res.append(res_i)
        self.final_df = pd.DataFrame(res)
        self.formal_print('###final result sort by ret over mdd')
        print(self.final_df)
        self.final_df.to_csv(self.FINAL_CSV)
    
    def target_backtest(self):
        loop_layer = [_/10000 for _ in range(100, 905, self.ROUND1_STEP)]
        for amt_diff_i in loop_layer:
            self.result_target.append(self.bk_unit_target(amt_diff_i))
        self.target_df = pd.DataFrame(self.result_target)
        res = self.target_df.sort_values('ret_over_mdd', ascending=False).reset_index(drop=True).head()
        print(res)

    def bk_fee_search(self, fee_con:bool, MinActionAmtDiff:float):
        saa = AssetWeight(    
            hs300=15/100,
            csi500=5/100,
            gem=3/100,
            sp500rmb=7/100,
            national_debt=60/100,
            gold=7/100,
            cash=3/100
        )  
        asset_param = AssetTradeParam(EnableCommission=fee_con, PurchaseDiscount=0.15, MinActionAmtDiff=MinActionAmtDiff) 
        t = AssetTrader(asset_param)
        b = FundBacktestEngine(data_manager=self.dm, trader=t, taa_params=None)
        b.init()
        b.run(saa=saa,start_date=self.start_date, end_date=self.end_date)
        res = b.get_asset_result()
        res['MinActionAmtDiff'] = MinActionAmtDiff
        res['fee_status'] = fee_con
        res['start_date'] = self.start_date
        res['end_date'] = self.end_date
        return res

    def search_fee(self):
        self.result_fee = []
        #for fee_con in [True, False]:
        fee_con = False
        for MinActionAmtDiff in [0.02,0.03,0.04,0.05,0.06,0.065,0.07,0.08]:
            res_i = self.bk_fee_search(fee_con, MinActionAmtDiff)
            self.result_fee.append(res_i)
        #self.result_fee_df = pd.DataFrame(self.result_fee)

    def bk_unit_double_asset(self, saa, amt_dif):
        asset_param = AssetTradeParam(EnableCommission=True, PurchaseDiscount=0.15, MinActionAmtDiff=amt_dif) 
        t = AssetTrader(asset_param)
        b = FundBacktestEngine(data_manager=self.dm, trader=t, taa_params=None)
        b.init()
        b.run(saa=saa)
        res = b.get_asset_result()
        res['amt_dif'] = amt_dif
        res['rebalance_details'] = b._trader.rebalance_details
        return res

    def bk_loop_selected_amt_diff(self, asset_1, asset_2):
        result = []
        for w in range(10,91,2):
            saa = AssetWeight(**{asset_1:w/100,asset_2:(99-w)/100, 'cash':1/100})
            amt_dif = 50 / 1000
            res_i = self.bk_unit_double_asset(saa=saa, amt_dif=amt_dif)
            result.append(res_i)
        return pd.DataFrame(result)

    def find_trigger_asset(self, dic):
        res = []
        for d, k in dic.items():
            if k:
                res.append({'date':d,'trigger_asset':max(k.items(), key=operator.itemgetter(1))[0]})
        trigger_list = pd.DataFrame(res).trigger_asset.tolist()
        trigger_dic = {i: trigger_list.count(i) for i in set(trigger_list)}
        trigger_asset = max(trigger_dic.items(), key=operator.itemgetter(1))[0]
        return trigger_asset

    def find_trigger_process(self, asset_1, asset_2):
        result = self.bk_loop_selected_amt_diff(asset_1,asset_2)
        res = []
        for idx, r in result.iterrows():
            if len(r.rebalance_date) == 2:
                res.append('unvalid bk, rebalence time <= 2')
                continue
            if idx == 0:
                res.append('None')
                continue
            trigger_asset=self.find_trigger_asset(r.rebalance_details)
            res.append(trigger_asset)
        result['trigger_asset'] = res
        result['rebalance_times'] = [len(_) for _ in result['rebalance_date']]
        return result

class ScoreTuner:

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

    def __init__(self, dm:FundDataManager, index_id:str='national_debt', folder:str='good_luck'):
        self.dm = dm
        self.index_id = index_id
        self.folder = folder
        self.search_datelist = list(sorted(set(self.dm.dts.index_fund_indicator_pack.loc[self.index_id].index.get_level_values(0).tolist())))
        self.score_list = self.make_score_list()
        self.index_indicator = self.dm.dts.index_fund_indicator_pack.loc[self.index_id]
        #time_span = AssetTimeSpan().__dict__[index_id]
        #self.index_indicator = self.index_indicator[self.index_indicator.year_length > time_span]
        self.fund_desc_dic = self.dm.dts.fund_info[['fund_id','desc_name']].set_index('fund_id').to_dict()['desc_name']
        self.calculate_std()

    def recent_day(self, dt, duration):
        dts = self.dm.dts.trading_days.datetime
        dts = dts[dts > dt].values
        return dts[0], dts[duration]


    def make_score_equation(self, score_weight:ScoreFunc=ScoreFunc()):
        score_dict = {}
        for indicator, w in score_weight.__dict__.items():
            if w != 0:
                if indicator in ['beta', 'beta_w', 'beta_m']:
                    score_w = self.INDICATOR_SIGN[indicator] * w
                else:
                    score_w = self.INDICATOR_SIGN[indicator] * w / getattr(self.indicator_std_mean, indicator)
                score_i = {indicator: score_w}
                score_dict.update(score_i)
        return ScoreFunc(**score_dict)

    def calculate_std(self):
        dts = self.dm.dts.trading_days.datetime
        dts = dts[dts > datetime.date(2012,1,1)]
        fund_indicator_index = self.dm.dts.fund_indicator[self.dm.dts.fund_indicator.index_id == self.index_id]
        res = []
        for dt in dts:
            std_i = fund_indicator_index[fund_indicator_index.datetime == dt].std(ddof=1)
            res.append(std_i)
        self.indicator_std_mean = pd.DataFrame(res).mean()

    def make_date_param_list(self, time_span:int=242, begin_date=datetime.date(2015,1,1)):
        search_datelist = [_ for _ in self.search_datelist if _ >= begin_date]
        param_list = []
        for idx,d in enumerate(search_datelist):
            end_idx = time_span + idx
            if end_idx < len(search_datelist):
                param_list.append({
                    'begin_date':d,
                    'end_date':search_datelist[end_idx]
                })
        return param_list

    def make_date_param_half_year(self, time_span:int=242, begin_date=datetime.date(2012,1,1), time_lag:int=60):
        search_datelist = [_ for _ in self.search_datelist if _ >= begin_date]
        param_list = []
        for idx,d in enumerate(search_datelist):
            if idx % time_lag != 0:
                continue
            end_idx = time_span + idx
            if end_idx < len(search_datelist):
                param_list.append({
                    'begin_date':d,
                    'end_date':search_datelist[end_idx]
                })
        return param_list

    def make_score_list(self):
        score_list = []
        for alpha in np.arange(0,0.8,0.05):
            for beta in np.arange(0,0.8,0.05):
                for fee_rate in np.arange(0,0.5,0.05):
                    track_err = 1 - alpha - beta - fee_rate
                    if track_err < 0:
                        continue
                    score_list.append(ScoreFunc(alpha=self.INDICATOR_SIGN['alpha'] * alpha, 
                                                beta=self.INDICATOR_SIGN['beta'] * beta, 
                                                fee_rate=self.INDICATOR_SIGN['fee_rate'] * fee_rate,
                                                track_err=self.INDICATOR_SIGN['track_err'] * track_err))
        return score_list

    def fund_alpha_calculator(self,top_num:int=3, 
                                start_date:datetime.date=datetime.date(2018,1,1),
                                end_date:datetime.date=datetime.date(2019,1,1),
                                score_method:ScoreFunc=ScoreFunc(alpha=0.3, beta=-0.6, fee_rate=-0.1)):
        
        index_price = self.dm.dts.index_price.loc[start_date:end_date,[self.index_id]]
        raw_indicator = self.index_indicator.loc[start_date]
        # normalized_indicator = raw_indicator.apply(lambda x: (x - x.mean() + 1e-6)/ (x.std() + 1e-6), axis=0)
        # normalized_indicator['beta'] = raw_indicator['beta']
        normalized_indicator = raw_indicator
        score_raw = normalized_indicator.apply(lambda x: score_method.get(x), axis=1)
        select_funds = pd.DataFrame(score_raw).sort_values(0,ascending=False).index[:top_num].tolist()
        select_nav = self.dm.dts.fund_nav.loc[start_date:end_date,select_funds]
        funds_mean_ret =  np.mean(select_nav.iloc[-1] / select_nav.iloc[0]) - 1
        index_ret = (index_price.iloc[-1] / index_price.iloc[0]).values[0] - 1
        return funds_mean_ret - index_ret

    def select_fund_checker(self,top_num:int=4, 
                                start_date:datetime.date=datetime.date(2018,1,1),
                                end_date:datetime.date=datetime.date(2019,1,1),
                                score_method:ScoreFunc=ScoreFunc(alpha=0.5/ 0.0444, beta=-0.4, track_err=-0.0/0.03939 ,fee_rate=-0.1/ 0.00266)):
        index_price = self.dm.dts.index_price.loc[start_date:end_date,[self.index_id]]
        raw_indicator = self.index_indicator.loc[start_date]
        normalized_indicator = raw_indicator
        score_raw = normalized_indicator.apply(lambda x: score_method.get(x), axis=1)
        select_funds = pd.DataFrame(score_raw).sort_values(0,ascending=False).index[:top_num].tolist()
        select_fund_desc = [self.fund_desc_dic[i] for i in select_funds] 
        
        select_nav = self.dm.dts.fund_nav.loc[start_date:end_date,select_funds]
        funds_mean_ret =  np.mean(select_nav.iloc[-1] / select_nav.iloc[0]) - 1
        index_ret = (index_price.iloc[-1] / index_price.iloc[0]).values[0] - 1
        alpha = funds_mean_ret - index_ret
        return select_fund_desc, alpha
    
    def select_fund_score(self, score_method:ScoreFunc=ScoreFunc(alpha=0.5/ 0.0444, beta=-0.4, track_err=-0.0/0.03939 ,fee_rate=-0.1/ 0.00266)):
        result = []
        param_list = self.make_date_param_half_year()
        for param_i in param_list:
            desc_name, alpha_i = self.select_fund_checker(
                            start_date=param_i['begin_date'], 
                            end_date=param_i['end_date'],
                            score_method=score_method,
                            )
            result.append({
                'datetime' : param_i['begin_date'],
                'alpha' : alpha_i,
                'desc_name': desc_name
            })
            
        alpha_mean = np.mean([i['alpha'] for i in result])
        select_fund = [i['desc_name'] for i in result]
        select_fund = [item for sublist in select_fund for item in sublist]
        power_num = 0
        link_num = 0
        for i in select_fund:
            if '增强' in i:
                power_num += 1
            elif '联接' in i:
                link_num += 1
        power_rate = power_num / len(select_fund)
        link_rate = link_num / len(select_fund)
        dic = {
            '增强比例':power_rate,
            '联接比例':link_rate,
            'alpha':alpha_mean,
            'score_func':score_method,
        }
        return dic
    
    def score_maker(self):
        res = []
        for alpha in range(15,100,3):
            for beta in range(15,100,3):
                fee_rate = 100 - alpha - beta
                if fee_rate < 0:
                    continue
                res.append(ScoreFunc(alpha=alpha/100/0.08291, beta=-beta/100, fee_rate=-fee_rate/100/0.0031)),#csi500
                #hs300 res.append(ScoreFunc(alpha=alpha/100/0.0444, beta=-beta/100, track_err=-0.0/0.03939 ,fee_rate=-fee_rate/100/0.00266))
        return res

    def score_factor_calculator(self, score_method:ScoreFunc=ScoreFunc(alpha=0.3, beta=-0.6, fee_rate=-0.1),
                                    param_idx:int=1):
        t1 = time.time()
        param_list = self.make_date_param_list()
        result = []
        for param_i in param_list:
            alpha_i = self.fund_alpha_calculator(top_num=3, 
                               start_date=param_i['begin_date'], 
                               end_date=param_i['end_date'],
                               score_method=score_method)
            result.append({
                'datetime':param_i['begin_date'],
                'alpha':alpha_i
            })    
        name_list = [f'{fac}_{round(wgt,2)}'for fac, wgt in score_method.__dict__.items() if wgt != 0]
        csv_name = '~'.join(name_list)
        csv_path = self.folder + '/' + str(param_idx) + '-' + csv_name + '.csv'
        pd.DataFrame(result).to_csv(csv_path)
        t2 = time.time()
        print(f'param_idx {param_idx} finish ,cost time {t2 - t1} s')
        return True
        
    def score_checker(self):
        # 日度
        score_list = []
        step = 0.10
        start = 0
        end = 0.5

        for alpha in np.arange(start,end,step):
            for beta in np.arange(start,end,step):
                for ret_over_period in np.arange(start,end,step):
                    for treynor in np.arange(start,end,step):
                        for m_square in np.arange(start,end,step):
                            for annual_ret in np.arange(start,end,step):
                                for time_ret in np.arange(start,end,step):
                                    for jensen_alpha_m in np.arange(start,end,step):
                                        treynor_ratio_m = 1-alpha-beta-ret_over_period-treynor-m_square-annual_ret-time_ret-jensen_alpha_m
                                        if treynor_ratio_m < 0 or treynor_ratio_m > 0.5:
                                            continue
                                        s = ScoreFunc(alpha=alpha,
                                                beta=beta,
                                                ret_over_period=ret_over_period,
                                                treynor=treynor,
                                                m_square=m_square,
                                                annual_ret=annual_ret,
                                                time_ret=time_ret,
                                                jensen_alpha_m=jensen_alpha_m,
                                                treynor_ratio_m=treynor_ratio_m)
                                        score_list.append(self.make_score_equation(s))
        result = []
        for score_i in score_list[:50]:
            res_i = self.select_fund_score(score_i)
            result.append(res_i)
            print(score_list.index(score_i)) 


    def multi_search(self, score_list:list=[ScoreFunc(alpha=0.3, beta=-0.6, fee_rate=-0.1), 
                                            ScoreFunc(alpha=0.3, beta=-0.5, fee_rate=-0.2),
                                            ScoreFunc(alpha=0.2, beta=-0.7, fee_rate=-0.1),
                                            ScoreFunc(alpha=0.1, beta=-0.8, fee_rate=-0.1)],
                           cpu_num:int=2):
        with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_num) as executor:
            future_to_bti = {executor.submit(self.score_factor_calculator, score_method, param_idx): param_idx for param_idx, score_method in enumerate(score_list)}
            for future in concurrent.futures.as_completed(future_to_bti):
                bt_i = future_to_bti[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print(f'{bt_i} generated an exception: {exc}')
                else:
                    pass

    def show_result(self):
        csv_list = os.listdir(self.folder)
        res = []
        for csv_i in csv_list:
            csv_path = self.folder+ csv_i
            df_i = pd.read_csv(csv_path,index_col=0)
            res.append({
                'score_method':csv_i[:-4],
                'alpha_mean':df_i.alpha.mean(),
                'alpha_std':df_i.alpha.std(),
            })
        return pd.DataFrame(res)   





if __name__ == "__main__":
    
    tt = TaaTunerParam()
    tt.IsTaaUpOnly = True
    tt.index_id = 'hs300'

    LowStop = -100
    LowThreshold = -100
    LowPlus = 0

    tt.param_list = []
    for HighThreshold in range(80, 97, 2):
        for HighStop in range(50, 71, 2):
            for HighMinus in [3 , 5, 7]:
                t = TAAParam()
                t.HighThreshold = HighThreshold / 100
                t.HighStop = HighStop / 100
                t.HighMinus = HighMinus / 100
                t.LowStop = LowStop / 100
                t.LowThreshold = LowThreshold / 100
                t.LowPlus = LowPlus / 100
                t.TuneCash = True
                tt.param_list.append(t)

    bk = TaaTuner()
    bk.init(tt)   
    bk.grid_search()

    '''
    asset_1 = 'hs300'
    asset_2 = 'csi500'
    hs300_csi500 = find_trigger_process(asset_1, asset_2)
    hs300_csi500[[asset_1,asset_2,'trigger_asset','rebalance_times']]
    '''