
from typing import Dict, Any, Set, Optional, Union
from collections import defaultdict
from ..struct import FundScoreParam, ScoreFilter, ScorePenaltyParams
from .data_tables import FundDataTables
import dataclasses
import pandas as pd
import re
import datetime
import time
import math
import numpy as np
from copy import deepcopy


@dataclasses.dataclass
class ManagerFunc:
    trade_year: float = 0
    annualized_ret: float = 0
    annualized_vol: float = 0
    model_alpha: float = 0
    model_beta: float = 0
    sharpe: float = 0

    def get(self, data):
        return  self.trade_year * data.trade_year \
                + self.annualized_ret * data.annualized_ret \
                + self.annualized_vol * data.annualized_vol \
                + self.model_beta * data.model_beta \
                + self.model_alpha * data.model_alpha \
                + self.sharpe * data.sharpe

    def __str__(self):
        func_str = ''
        for fac, w in self.__dict__.items():
            if w == 0:
                continue
            flag = ''
            if w > 0:
                flag = '+'
            if fac == 'beta':
                func_str += f'{flag}{w} * abs(1-{fac})'
            else:
                func_str += f'{flag}{w} * {fac}'
        return func_str

@dataclasses.dataclass
class ScoreFunc:

    alpha: float = 0  # weight of alpha
    beta: float = 0  # weight of abs(1-beta), or beta's deviation from 1
    track_err: float = 0  # weight of track_err
    fee_rate: float = 0  # weight of fee_rate
    info_ratio: float = 0
    ipo_weight: float = 0
    fund_size: float = 0
    mng_annualized_ret: float = 0
    mng_annualized_vol: float = 0
    mng_model_alpha: float = 0
    mng_model_beta: float = 0
    mng_sharpe: float = 0
    mng_trade_year: float = 0
    mng_fund_size: float = 0
    mng_now_comp_year: float = 0
    mng_year_ret_std: float = 0
    alpha_bond: float = 0
    beta_bond: float = 0
    alpha_hs300: float = 0
    beta_hs300: float = 0
    active: float = -10
    FundMngScoreV1: float = 0
    RetAbilityFundScore: float = 0
    RiskAbilityFundScore: float = 0
    StableAbility: float = 0
    WinRateMonthlyTop50: float = 0
    WinRateMonthlyTop75: float = 0
     #默认条件不选择主动型，对主动性加分数惩罚
    # last_year_alpha: float = 0
    # last_year_beta: float = 0
    # last_two_year_alpha: float = 0
    # last_two_year_beta: float = 0
    # down_risk: float = 0
    # ret_over_period: float = 0
    # treynor: float = 0
    # mdd: float = 0
    # m_square: float = 0
    # var_: float = 0
    # sharpe: float = 0
    # annual_ret: float = 0
    # annual_vol: float = 0
    # time_ret: float = 0
    # alpha_w: float = 0
    # beta_w: float = 0
    # track_err_w: float = 0
    # beta_m: float = 0
    # calmar_ratio_m: float = 0
    # information_ratio_m: float = 0
    # jensen_alpha_m: float = 0
    # sharpe_ratio_m: float = 0
    # treynor_ratio_m: float = 0

    def get(self, data):
        return  self.alpha * data.alpha \
                + self.track_err * data.track_err \
                + self.fee_rate * data.fee_rate \
                + self.beta * abs(1-data.beta) \
                + self.info_ratio * data.info_ratio \
                + self.alpha_bond * data.alpha_bond \
                + self.beta_bond * data.beta_bond \
                + self.alpha_hs300 * data.alpha_hs300 \
                + self.beta_hs300 * data.beta_hs300 \
                + self.ipo_weight * data.ipo_weight \
                + self.fund_size * data.fund_size \
                + data.mng_annualized_ret.mul(other=self.mng_annualized_ret, fill_value=0) \
                + data.mng_annualized_vol.mul(other=self.mng_annualized_vol, fill_value=0) \
                + data.mng_model_alpha.mul(other=self.mng_model_alpha, fill_value=0) \
                + data.mng_model_beta.mul(other=self.mng_model_beta, fill_value=0) \
                + data.mng_sharpe.mul(other=self.mng_sharpe, fill_value=0) \
                + data.mng_trade_year.mul(other=self.mng_trade_year, fill_value=0) \
                + data.mng_fund_size.mul(other=self.mng_fund_size, fill_value=0) \
                + data.mng_now_comp_year.mul(other=self.mng_now_comp_year, fill_value=0) \
                + data.mng_year_ret_std.mul(other=self.mng_year_ret_std, fill_value=0) \
                + data.active * self.active \
                + data.FundMngScoreV1.mul(other=self.FundMngScoreV1, fill_value=0) \
                + data.RetAbilityFundScore.mul(other=self.RetAbilityFundScore, fill_value=0) \
                + data.RiskAbilityFundScore.mul(other=self.RiskAbilityFundScore, fill_value=0) \
                + data.StableAbility.mul(other=self.StableAbility, fill_value=0) \
                + data.WinRateMonthlyTop50.mul(other=self.WinRateMonthlyTop50, fill_value=0) \
                + data.WinRateMonthlyTop75.mul(other=self.WinRateMonthlyTop75, fill_value=0) 
                # + self.down_risk * data.down_risk \
                # + self.info_ratio * data.info_ratio \
                # + self.ret_over_period * data.ret_over_period \
                # + self.treynor * data.treynor \
                # + self.mdd * data.mdd \
                # + self.m_square * data.m_square \
                # + self.var_ * data.var_ \
                # + self.sharpe * data.sharpe \
                # + self.annual_ret * data.annual_ret \
                # + self.annual_vol * data.annual_vol \
                # + self.time_ret * data.time_ret

    def get_all(self, data):
        return  self.alpha * data.alpha \
                + self.track_err * data.track_err \
                + self.fee_rate * data.fee_rate \
                + self.down_risk * data.down_risk \
                + self.info_ratio * data.info_ratio \
                + self.ret_over_period * data.ret_over_period \
                + self.treynor * data.treynor \
                + self.mdd * data.mdd \
                + self.m_square * data.m_square \
                + self.var_ * data.var_ \
                + self.sharpe * data.sharpe \
                + self.annual_ret * data.annual_ret \
                + self.annual_vol * data.annual_vol \
                + self.time_ret * data.time_ret \
                + self.beta * abs(1-data.beta) \
                + self.alpha_w * data.alpha_w \
                + self.track_err_w * data.track_err_w \
                + self.calmar_ratio_m * data.calmar_ratio_m \
                + self.information_ratio_m * data.information_ratio_m \
                + self.jensen_alpha_m * data.jensen_alpha_m \
                + self.sharpe_ratio_m * data.sharpe_ratio_m \
                + self.treynor_ratio_m * data.treynor_ratio_m \
                + self.beta_w * abs(1-data.beta_w) \
                + self.beta_m * abs(1-data.beta_m) \
                + self.last_year_alpha * data.last_year_alpha \
                + self.last_year_beta * data.last_year_beta \
                + self.last_two_year_alpha * data.last_two_year_alpha \
                + self.last_two_year_beta * data.last_two_year_beta

    def __str__(self):
        func_str = ''
        for fac, w in self.__dict__.items():
            if w == 0:
                continue
            flag = ''
            if w > 0:
                flag = '+'
            if fac == 'beta':
                func_str += f'{flag}{w} * abs(1-{fac})'
            else:
                func_str += f'{flag}{w} * {fac}'
        return func_str


class FundScoreManager:

    def __init__(self, score_filter=ScoreFilter(), score_penalty_param=ScorePenaltyParams()):
        self.params = None
        self.dts = None
        self.funcs = {
            'hs300': {
                'default': ScoreFunc(track_err=-0.4,beta=-0.6),
                'enhanced':ScoreFunc(alpha=0.6, beta=-0.3),
                'active': ScoreFunc(mng_trade_year=0.1, mng_sharpe=0.3,alpha=0.4,mng_year_ret_std=-0.2,active=10),
                'active_2': ScoreFunc(WinRateMonthlyTop75=0.5, RiskAbilityFundScore=-0.5,active=10),
            },
            'csi500': {
                'default': ScoreFunc(info_ratio=0.2,track_err=-0.7, fee_rate=-0.1),
                'enhanced':ScoreFunc(alpha=0.7, beta=-0.3),
                'active': ScoreFunc(mng_trade_year=0.1, mng_sharpe=0.3,alpha=0.4,mng_year_ret_std=-0.2,active=10),
                'active_2': ScoreFunc(WinRateMonthlyTop75=0.5, RiskAbilityFundScore=-0.5,active=10),
            }, 
            'gem': {
                'default': ScoreFunc(info_ratio=0.2,track_err=-0.7, fee_rate=-0.1),
                'enhanced':ScoreFunc(alpha=0.3, beta=-0.50, track_err=-0.2),
                'active': ScoreFunc(mng_trade_year=0.15, mng_annualized_ret=0.15, mng_sharpe=0.15,alpha=0.1,mng_model_alpha=0.3,mng_model_beta=0.15,active=10),  
            },
            'national_debt': {
                'default':ScoreFunc(alpha=0.20, beta=-0.45, track_err=-0.35),#, fee_rate=-0.2),
            }, 
            'mmf':{
                'default':ScoreFunc(alpha=0.3, beta=-0.2, fee_rate=-0.1, track_err=-0.4),
            }, 
            'sp500rmb':{
                'default':ScoreFunc(fee_rate=-0.2, track_err=-0.8)
            },  
            'gold': {
                'default':ScoreFunc(alpha=0.15, track_err=-0.85),
            },  
            'hsi': {
                'default':ScoreFunc(alpha=0.3, fee_rate=-0.3, track_err=-0.4),# set default score equation
            },  
            'active': {
                'default':ManagerFunc(trade_year=0.15, annualized_ret=0.15, sharpe=0.15, model_alpha=0.3, model_beta=0.15)
            },
            'conv_bond':{
                'default':ScoreFunc(fee_rate=-0.1, alpha_bond=0.4, beta_bond=-0.1),# set default score equation
            }
        }
        self.score_cache = defaultdict(dict)
        self.score_raw_cache = defaultdict(dict)
        self.score_manager_cache = defaultdict(dict)
        self.score_filter = score_filter
        self.score_penalty_param = score_penalty_param
        self._size_and_com_hold_cache: Dict[Any, pd.Index] = {}

    # Caution!!增加字段应考虑相应修改该函数
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        if self.params != other.params:
            return False
        if self.funcs != other.funcs:
            return False
        if self.score_filter != other.score_filter:
            return False
        if self.score_penalty_param != other.score_penalty_param:
            return False
        return True

    # 获取字符串形式的各大类的默认score func
    def get_default_func_str(self) -> Dict[str, str]:
        return {index_id: str(score_func) for index_id, score_func in self.funcs.items()}

    def set_param(self, score_param: FundScoreParam):
        self.params = score_param

    def set_dts(self, dts: FundDataTables):
        self.dts = dts
        self.fund_id_to_name = self.dts.fund_info[['fund_id', 'desc_name']].set_index('fund_id').to_dict()['desc_name']
        self.fund_name_to_id = self.dts.fund_info[['fund_id', 'desc_name']].set_index('desc_name').to_dict()['fund_id']

    def _get_fund_score(self, dt, index_id, is_filter_c, score_func: Optional[ScoreFunc] = None) -> dict:
        assert self.params and self.dts, 'cannot provide fund_score without params or data tables'
        try:
            # pivot_table会把index以外各列都为nan的行自动干掉(感觉应该是bug，而且dropna=False的行为也不合理)
            # 因此这里如果找不到的话直接返回空
            cur_d = self.dts.index_fund_indicator_pack.loc[index_id, dt]
        except KeyError:
            return {}, {}
        return self._get_score(index_id=index_id, dt=dt, cur_d=cur_d, is_filter_c=is_filter_c, score_func=score_func)

    def get_fund_score(self, dt, index_id, is_filter_c, score_func: Optional[Union[ScoreFunc, str]] = None):
        if score_func is not None and score_func:
            # 指定了score_func，缓存里肯定没有，直接算一遍然后返回
            return self._get_fund_score(dt, index_id, is_filter_c, score_func)
        try:
            # 先尝试从缓存里取
            return self.score_cache[dt][index_id], self.score_raw_cache[dt][index_id]
        except KeyError:
            # 获取不到的话则算一遍，注意这里不存缓存
            return self._get_fund_score(dt, index_id, is_filter_c)

    def get_fund_scores(self, dt, index_list, is_filter_c=True, fund_score_funcs: Optional[Dict[str, Union[ScoreFunc, str]]] = None) -> dict:
        index_score = self.score_cache[dt]
        index_score_raw = self.score_raw_cache[dt]
        if not index_score or not index_score_raw:
            # 先用默认的fund_score_funcs对所有的index算一下
            for index_id in index_list:
                # 这里由于index_score和index_score_raw都是dict, 所以我们这样赋值可以更新到self.score_cache和self.score_raw_cache
                index_score[index_id], index_score_raw[index_id] = self._get_fund_score(dt, index_id, is_filter_c)

        # 没有指定fund_score_funcs，可以直接返回
        if fund_score_funcs is None or not fund_score_funcs:
            return index_score, index_score_raw

        # 如果指定了fund_score_funcs，需要重新算一下其中指定的index
        score = {}
        score_raw = {}
        for index_id, func in fund_score_funcs.items():
            score[index_id], score_raw[index_id] = self._get_fund_score(dt, index_id, is_filter_c, func)
        # 将指定的index的和默认的index组合到一起返回
        # python3.9可以直接用"|"运算符
        score.update({index_id: v for index_id, v in index_score.items() if index_id not in score})
        score_raw.update({index_id: v for index_id, v in index_score_raw.items() if index_id not in score_raw})
        return score, score_raw

    def get_manager_scores(self, dt, active_fund_id_list, score_select):
        index_id = 'active'
        type_i = score_select[index_id]
        fund_ids = self._filter_size_and_com_hold(dt, index_id, active_fund_id_list)
        #print(f'dt {dt} index_id {index_id} score_select {score_select} self.score_manager_cache[dt] {self.score_manager_cache[dt]}')  
        try:
            manager_score = self.score_manager_cache[dt][score_select[index_id]].to_dict()
            _manager_funds = self.dts.fund_manager_rank.loc[dt].to_dict()['fund_list']
            # 根据对规模和持有人结构筛选条件过滤基金
            manager_funds = {}
            for mng_id, mng_funds in _manager_funds.items():
                _mng_funds = [ i for i in mng_funds if i in fund_ids]
                if len(_mng_funds) > 0:
                    manager_funds[mng_id] = _mng_funds[0] 
            # 如果经理当时不存基金, 即无基金可选, 直接去掉分数
            manager_score = {mng_id : score_i for mng_id, score_i in manager_score.items() if mng_id in manager_funds}
            return {type_i:manager_score}, manager_funds
        except:
            return {type_i:{}}, {}

    def _wrapper(self, df: pd.DataFrame, is_filter_c: bool, use_weekly_monthly_indicators: bool):
        # T日大类下有很多基金，这里取一下它们的datetime和index_id，因为值都是一样的所以取array[0]就OK
        dt = df.datetime.array[0]
        index_id: str = df.index_id.array[0]
        # 这里把index换成了fund_id
        score, score_raw = self._get_score(index_id=index_id, dt=dt, cur_d=df.set_index('fund_id').drop(columns=['datetime', 'index_id']), is_filter_c=is_filter_c, use_weekly_monthly_indicators=use_weekly_monthly_indicators)
        self.score_cache[dt][index_id] = score
        self.score_raw_cache[dt][index_id] = score_raw

    def _wrapper_manager(self, df: pd.DataFrame):
        dt = df.datetime.array[0]
        manager_rank = self._get_manager_score(dt=dt, cur_d=df.set_index('manager_id').drop(columns=['datetime']))
        self.score_manager_cache[dt] = manager_rank

    def pre_calculate(self, is_filter_c=True, use_weekly_monthly_indicators=False):
        # self.dts.fund_indicator.pivot_table(index=['datetime', 'index_id'])
        # 上面这一行会耗时10秒左右，且之后遍历index(datetime-index_id pair)也会比下边groupby慢一些
        # 这里应该没必要先groupby datetime，再groupby index_id（如果真这样可能更慢吧）
        self.dts.fund_indicator.groupby(by=['datetime', 'index_id']).apply(lambda x: self._wrapper(x, is_filter_c, use_weekly_monthly_indicators))

    def pre_calculate_manager(self):
        self.dts.fund_manager_score.groupby(by=['datetime']).apply(lambda x: self._wrapper_manager(x))

    def _get_manager_score(self, dt, cur_d):
        # manager top list first
        index_id = 'active'
        cur_d = cur_d.apply(lambda x: (x - x.mean() + 1e-6)/ (x.std() + 1e-6), axis=0)
        func_dic = self.funcs.get(index_id)
        score_sum = {}
        for type_i, func in func_dic.items():
            score = func.get(cur_d)
            score_sum[type_i] = score
        return score_sum

    def _get_score(self, index_id, dt, cur_d, is_filter_c, use_weekly_monthly_indicators=False, score_func: Optional[Union[ScoreFunc, str]] = None):
        fund_ids = self._filter_size_and_com_hold(dt, index_id, cur_d.index)
        if fund_ids is not cur_d.index:
            # 这里没有dropna总计可以快24秒
            cur_d = cur_d.reindex(fund_ids)
        func_dic = self.funcs.get(index_id) if score_func is None else {'temp': score_func}
        if cur_d.shape[0] > 1:
            cur_d_sta = cur_d.apply(lambda x: (x - x.mean() + 1e-6)/ (x.std() + 1e-6), axis=0)
            cur_d_sta['beta'] = cur_d['beta']
            cur_d_sta['year_length'] = cur_d['year_length']
            cur_d_sta['active'] = cur_d['active']
            cur_d_sta['mng_fund_size'] = cur_d['mng_fund_size']
            less_mng_year = cur_d[cur_d['mng_trade_year'] < 1].index.tolist()
            cur_d = cur_d_sta
            score_raw_sum = {}
            score_sum = {}
            for type_i, func in func_dic.items():
                if isinstance(func, str):
                    try:
                        FundScoreManager.test_func(func)
                    except Exception as e:
                        # func str不合法，直接返回空
                        print(f'eval fund score func str failed for {index_id} (err_msg){e}')
                        return {}, {}
                    score_raw = cur_d.apply(FundScoreManager.get_func(func), axis=1)
                else:
                    # 默认均走这个分支
                    if use_weekly_monthly_indicators:
                        score_raw = func.get_all(cur_d)
                    else:
                        score_raw = func.get(cur_d)
                if index_id in self.score_penalty_param.FilterYearIndex:
                    punish_funds = cur_d[cur_d.year_length < self.score_penalty_param.JudgeYearLength].index.tolist()
                    for _fund_id in punish_funds:
                        score_raw[_fund_id] += self.score_penalty_param.Penalty
                    if index_id in ['hs300','csi500'] and type_i in ['active']:
                        punish_funds_1 = cur_d_sta[cur_d_sta['mng_fund_size'] < 5e8].index.tolist()
                        punish_funds_1 = cur_d_sta[cur_d_sta['mng_fund_size'] < 5e8].index.tolist()
                        # 对于管理规模不到5千万和 年限不到1年到经理，进行惩罚
                        for _fund_id in punish_funds_1:
                            score_raw[_fund_id] += self.score_penalty_param.Penalty
                        for _fund_id in less_mng_year:
                            score_raw[_fund_id] += self.score_penalty_param.Penalty
                score = (score_raw - score_raw.min()) / (score_raw.max() - score_raw.min())
                if is_filter_c:
                    score = self._filter_score(score)
                score_sum[type_i] = score.to_dict()
                score_raw_sum[type_i] = score_raw.to_dict()
        else:
            score_raw_sum = {type_i : {cur_d.index[0]: 1} for type_i in func_dic}
            score_sum = score_raw_sum
        return score_sum, score_raw_sum

    def _filter_size_and_com_hold(self, dt, index_id: str, fund_ids: pd.Index):
        if index_id not in self.score_filter.FilterIndexId:
            return fund_ids
        try:
            # retrieve from cache
            _select_funds = self._size_and_com_hold_cache[dt]
        except KeyError:
            try:
                fund_com_hold_dt = self.dts.fund_com_hold.loc[dt]
            except KeyError:
                return fund_ids

            hold_select_fund_id = fund_com_hold_dt[fund_com_hold_dt < self.score_filter.CompanyHoldLimit].index
            fund_size_dt = self.dts.fund_size.loc[dt]
            size_select_fund_id = fund_size_dt[(fund_size_dt >= self.score_filter.SizeBottom)
                                               & (fund_size_dt <= self.score_filter.SizeTop)].index
            _select_funds = hold_select_fund_id.intersection(size_select_fund_id)
            # 这里做了一个缓存：T日备选的基金列表；因为多个大类可能多次取同一日的备选基金列表
            # 这个缓存没有清理，但看起来应该没问题
            self._size_and_com_hold_cache[dt] = _select_funds
        select_funds = _select_funds.intersection(fund_ids)
        if select_funds.empty:
            return fund_ids
        else:
            return select_funds

    def _filter_score(self, score_series: pd.Series) -> pd.Series:
        # 同一天同资产 同基金A B 在 选B
        # 同一天同资产 同基金A C 在 选C
        # 这里比之前总计快6秒左右
        index_fund_name: Set[str] = {self.fund_id_to_name[_] for _ in score_series.index}
        for fund_name in index_fund_name:
            if 'B' in fund_name or 'C' in fund_name:
                prefered_fund, count = re.subn(r'[BC]$', 'A', fund_name)
                if count != 0 and prefered_fund in index_fund_name:
                    score_series[self.fund_name_to_id[prefered_fund]] = 0
        return score_series

    def _filter_score_prefer_a(self, score_series: pd.Series) -> pd.Series:
        # 同一天同资产 同基金A B 在 选A   适合长周期策略
        # 同一天同资产 同基金A C 在 选A   适合长周期策略
        index_fund_name: Set[str] = {self.fund_id_to_name[_] for _ in score_series.index}
        for fund_name in index_fund_name:
            if 'B' in fund_name or 'C' in fund_name:
                prefered_fund, count = re.subn(r'[BC]$', 'A', fund_name)
                if count != 0 and prefered_fund in index_fund_name:
                    score_series[self.fund_name_to_id[fund_name]] = 0
        return score_series

    def _white_and_black_list_filter(self, score, score_raw, disproved_set):
        score = self._white_black_func(deepcopy(score), disproved_set)
        score_raw = self._white_black_func(deepcopy(score_raw), disproved_set)
        return score, score_raw

    def _white_black_func(self, score, disproved_set):
        del_list = []
        for index_id in score:
            for type_i in score[index_id]:
                for fund_id in score[index_id][type_i]:
                        if fund_id in disproved_set:
                            # 之前是给非白名单 黑名单的基金给分数惩罚，但是基金数量不足时，会交易
                            # 现在改为强逻辑，直接删掉
                            #score[index_id][fund_id] += self.score_penalty_param.BlackListPenalty
                            del_list.append([index_id, type_i, fund_id])
        for del_i in del_list:
            del score[del_i[0]][del_i[1]][del_i[2]]
        return score

    @staticmethod
    def test_func(func_str):
        for item in ScoreFunc.__dataclass_fields__.keys():
            locals()[item] = 0
        # if we cannot calculate, it just breaks
        eval(func_str)
        return True

    @staticmethod
    def get_func(func_str):
        new_func = func_str
        for item in ScoreFunc.__dataclass_fields__.keys():
            new_func = new_func.replace(item, 'x.' + item)
        return lambda x: eval(new_func)

    @staticmethod
    def score_calc(func_str, dm, index_id, dt):
        # 选出组合展示持有1年的回测结果 
        # 同一天同资产 同基金A B 在 选A
        # 同一天同资产 同基金A C 在 选A
        cur_d = dm.dts.index_fund_indicator_pack.loc[index_id, dt]
        cur_d_sta = cur_d.apply(lambda x: (x - x.mean() + 1e-6)/ (x.std() + 1e-6), axis=0)
        cur_d_sta['beta'] = cur_d['beta']
        cur_d = cur_d_sta
        f = FundScoreManager.get_func(func_str)
        score_series = cur_d.apply(f, axis=1)
        score_series = dm._score_manager._filter_score_prefer_a(score_series)
        return score_series

class FundRankScoreManager(FundScoreManager):

    def __init__(self, score_filter=ScoreFilter(), score_penalty_param=ScorePenaltyParams()):
        super().__init__(score_filter=score_filter, score_penalty_param=score_penalty_param)
        print('#### score rank manager init')

    def _get_score(self, index_id, dt, cur_d, is_filter_c, use_weekly_monthly_indicators=False, score_func: Optional[Union[ScoreFunc, str]] = None):
        fund_ids = self._filter_size_and_com_hold(dt, index_id, cur_d.index)
        if fund_ids is not cur_d.index:
            # 这里没有dropna总计可以快24秒
            cur_d = cur_d.reindex(fund_ids)
        func_dic = self.funcs.get(index_id) if score_func is None else {'temp': score_func}
        if cur_d.shape[0] > 1:
            #修改因子预处理方式 改用rank
            #cur_d_sta = cur_d.apply(lambda x: (x - x.mean() + 1e-6)/ (x.std() + 1e-6), axis=0)
            cur_d_sta = cur_d.rank(ascending=False,pct=True)
            cur_d_sta['beta'] = cur_d['beta']
            cur_d_sta['year_length'] = cur_d['year_length']
            cur_d_sta['active'] = cur_d['active']
            cur_d_sta['mng_fund_size'] = cur_d['mng_fund_size']
            less_mng_year = cur_d[cur_d['mng_trade_year'] < 1].index.tolist()
            cur_d = cur_d_sta
            score_raw_sum = {}
            score_sum = {}
            for type_i, func in func_dic.items():
                if isinstance(func, str):
                    try:
                        FundScoreManager.test_func(func)
                    except Exception as e:
                        # func str不合法，直接返回空
                        print(f'eval fund score func str failed for {index_id} (err_msg){e}')
                        return {}, {}
                    score_raw = cur_d.apply(FundScoreManager.get_func(func), axis=1)
                else:
                    # 默认均走这个分支
                    if use_weekly_monthly_indicators:
                        score_raw = func.get_all(cur_d)
                    else:
                        score_raw = func.get(cur_d)
                if index_id in self.score_penalty_param.FilterYearIndex:
                    punish_funds = cur_d[cur_d.year_length < self.score_penalty_param.JudgeYearLength].index.tolist()
                    for _fund_id in punish_funds:
                        score_raw[_fund_id] += self.score_penalty_param.Penalty
                    if index_id in ['hs300','csi500'] and type_i in ['active']:
                        punish_funds_1 = cur_d_sta[cur_d_sta['mng_fund_size'] < 5e8].index.tolist()
                        punish_funds_1 = cur_d_sta[cur_d_sta['mng_fund_size'] < 5e8].index.tolist()
                        # 对于管理规模不到5千万和 年限不到1年到经理，进行惩罚
                        for _fund_id in punish_funds_1:
                            score_raw[_fund_id] += self.score_penalty_param.Penalty
                        for _fund_id in less_mng_year:
                            score_raw[_fund_id] += self.score_penalty_param.Penalty
                score = (score_raw - score_raw.min()) / (score_raw.max() - score_raw.min())
                if is_filter_c:
                    score = self._filter_score(score)
                score_sum[type_i] = score.to_dict()
                score_raw_sum[type_i] = score_raw.to_dict()
        else:
            score_raw_sum = {type_i : {cur_d.index[0]: 1} for type_i in func_dic}
            score_sum = score_raw_sum
        return score_sum, score_raw_sum