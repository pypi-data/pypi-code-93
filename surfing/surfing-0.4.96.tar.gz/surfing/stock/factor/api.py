
import datetime
import traceback
from typing import Tuple, List, Optional
import os, psutil, time
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from pandas.tseries.offsets import DateOffset
from .base import Factor
from ...constant import StockFactorType
from .derived import DerivedFactor
from .basic_factors import BasicFactor, StockPostPriceFactor
from .utils import TradingDayList, StockIndustryInfoFactor, FundHoldStockFactor
from .factor_types import MixFactorBase
from ..factor import fund_basic_factor, fund_derived_factor, fund_append_update_factor, fund_derived_score


class DefaultFactors(DerivedFactor):

    _DEFAULT_FACTOR_NAMES = ['fin/mixf', 'gro/mixg', 'lev/mixl', 'liq/mixl', 'mom/mixm', 'sca/mv_flo', 'tech/mixt', 'val/mixv', 'vol/mixv']

    # 一个特殊的因子，对基金做归因分析时使用
    def __init__(self):
        super().__init__('default_facs', StockFactorType.SPEC)

        for one in self._DEFAULT_FACTOR_NAMES:
            self._deps.add(DerivedFactor._registry[one])

    def _section_regression(self, x: pd.DataFrame):
        # x是截面上(一个时间点上)universe中所有股票的信息
        df = x.stack().reset_index()
        df = df[df.notna().all(axis=1)]
        if df.shape[0] == 0:
            # 如果这一天没有universe中任何股票的信息，则直接返回(无法做回归)
            return

        # 对每种风格因子做标准化
        normalized = StandardScaler().fit_transform(df.loc[:, self._DEFAULT_FACTOR_NAMES].to_numpy())
        # 收益率对const(市场因子)+所有风格因子做横截面回归
        results = sm.OLS(df.loc[:, 'rate_of_return'].to_numpy(), sm.add_constant(normalized)).fit()
        # 将系数(因子收益率)保存下来, 然后再加上日期和universe
        return pd.Series(dict(zip(['const']+self._DEFAULT_FACTOR_NAMES, results.params.tolist())))

    def calc_ret(self, universe: str = 'default'):
        # 获取风格分析因子值
        factor_list: List[pd.DataFrame] = []
        for one in self._DEFAULT_FACTOR_NAMES:
            try:
                factor = DerivedFactor._registry[one]
            except KeyError as e:
                print(f'[calc_ret_by_reg] invalid stock factor name {one} (err_msg){e}')
                return
            f_val = factor.get(universe=universe)
            if f_val is None:
                print(f'[calc_ret_by_reg] retrieve value of {one} failed')
                return
            f_val = f_val.set_axis(pd.MultiIndex.from_product([[one], f_val.columns]), axis=1)
            factor_list.append(f_val)
            print(f'load {one} done')
        factor_values = pd.concat(factor_list, axis=1)
        print('load all stock factor data done')

        spp = StockPostPriceFactor()
        # 收益率列向上移1行, 使得其他列T-1日对应T日收益率
        rate_of_return = spp.get(universe=universe).pct_change(fill_method=None).shift(-1)
        rate_of_return = rate_of_return.set_axis(pd.MultiIndex.from_product([['rate_of_return'], rate_of_return.columns]), axis=1)
        factor_values = factor_values.join(rate_of_return)

        # 对每个时间点做横截面回归
        result = factor_values.groupby(by='datetime').apply(self._section_regression)
        # 最后再整体下移1行, 使得日期与收益率的日期对齐(均为T日, 之前为T-1日对应T日收益率)
        self._factor_ret[universe] = result.shift(1).dropna()


class StockFactorApi:

    _DECOMP_RET_DATE_OFFSET = DateOffset(years=1)
    _WINDOW_LEN = int(60 / 5)

    @staticmethod
    def get_stock_factor_ret(factor_names: Tuple[str], universe: str) -> Optional[pd.DataFrame]:
        rets: List[pd.Series] = []
        for one in factor_names:
            try:
                factor = DerivedFactor._registry[one]
            except KeyError as e:
                print(f'[stock_factor_api] invalid stock factor name {one} (err_msg){e} (universe){universe}')
                continue
            f_ret = factor.get_ret(universe=universe)
            if f_ret is not None:
                rets.append(f_ret)
            else:
                print(f'[stock_factor_api] retrieve return of {one} failed (universe){universe}')
        if rets:
            return pd.concat(rets, axis=1)

    @staticmethod
    def calc_factor_return_contribution(fund_ret: pd.Series, universe: str) -> Optional[pd.DataFrame]:

        def _lambda_rolling_reg(x, whole, fund_name):
            # x是基金每日收益率, 对相应日期的因子收益做回归(加前置的常数项)(使用前WINDOW_LEN日)
            results = sm.OLS(x[:-1], sm.add_constant(whole.drop(columns=fund_name).loc[x.index[:-1], :])).fit()
            # 回归结果中包含常数项系数，这里只取另外几个indicator的系数(即上边的因子收益)
            # T+1日各因子收益的贡献 = T+1日因子收益 * 前WINDOW_LEN日回归系数
            contribution = whole.drop(columns=fund_name).loc[x.index[-1], :] * results.params[1:]
            # T+1日特异收益率 = T+1日基金收益 - T+1日各因子收益的贡献和
            spec_ret = x.array[-1] - sum(contribution)

            # 记录T+1日各因子收益的贡献, 特异收益率, 基金收益率等信息
            fund_attribution_list.append(contribution.append(pd.Series({'spec': spec_ret, 'datetime': x.index.array[-1]})))
            return 0

        ret_rg = DefaultFactors().get_ret(universe=universe)
        if ret_rg is None:
            print(f'[calc_factor_return_contribution] retrieve return of default factors failed')
            return
        try:
            fund_ret = fund_ret.dropna()
            # 是否只使用部分数据计算因子暴露
            # cal_start_date = (fund_ret.index.array[-1] - StockFactorApi._DECOMP_RET_DATE_OFFSET).date()
            # if fund_ret.index.array[0] > cal_start_date:
            #     print(f'[stock_factor_api] not enough data of fund {fund_ret.name} (start_date){fund_ret.index.array[0]}')
            #     return
            # filtered_fund_ret = fund_ret[fund_ret.index >= cal_start_date]
            # if filtered_fund_ret.empty:
            #     print(f'[stock_factor_api] no data of fund {fund_ret.name} to decomp (start_date){fund_ret.index.array[0]} (end_date){fund_ret.index.array[-1]}')
            #     return
            # rg = filtered_fund_ret.to_frame().join(ret_rg).ffill().dropna()
            # 计算因子收益曲线(包含特异收益率)
            rg = fund_ret.to_frame().join(ret_rg).ffill()
            rg = rg.set_axis(pd.to_datetime(rg.index, infer_datetime_format=True)).resample('1W').sum(min_count=3)
            rg = rg.set_axis(rg.index.date)
            rg = rg[rg.notna().all(axis=1)]
            fund_attribution_list = []
            # 以下为手写的rolling, 但实际和直接用rolling的时间差不多
            # for i in range(rg.shape[0]):
            #     end_loc = i + StockFactorApi._WINDOW_LEN
            #     if end_loc + 1 >= rg.shape[0]:
            #         break
            #     data_in_window = rg.iloc[i:end_loc, :]
            #     # x是基金每日收益率, 对相应日期的因子收益做回归(加前置的常数项)(使用前WINDOW_LEN日)
            #     results = sm.OLS(data_in_window[fund_ret.name], sm.add_constant(data_in_window.drop(columns=fund_ret.name))).fit()
            #     # 回归结果中包含常数项系数，这里只取另外几个indicator的系数(即上边的因子收益)
            #     # T+1日各因子收益的贡献 = T+1日因子收益 * 前WINDOW_LEN日回归系数
            #     contribution = rg.iloc[end_loc, :].drop(fund_ret.name) * results.params[1:]
            #     # T+1日特异收益率 = T+1日基金收益 - T+1日各因子收益的贡献和
            #     spec_ret = rg.iloc[end_loc, :].at[fund_ret.name] - sum(contribution)

            #     # 记录T+1日各因子收益的贡献, 特异收益率, 基金收益率等信息
            #     fund_attribution_list.append(contribution.append(pd.Series({'spec': spec_ret, 'datetime': rg.index.array[end_loc]})))
            rg[fund_ret.name].rolling(window=StockFactorApi._WINDOW_LEN+1).apply(_lambda_rolling_reg, kwargs={'whole': rg, 'fund_name': fund_ret.name})
            factor_ret_decomp = pd.DataFrame(fund_attribution_list).set_index('datetime').cumsum()
            # factor_ret_decomp = (np.exp(factor_ret_decomp.drop(columns='spec_ret')) - 1).join(factor_ret_decomp.spec_ret)
            return factor_ret_decomp
        except Exception as e:
            print(f'[calc_factor_return_contribution] abnormal error when decomp return (err_msg){e}')
            traceback.print_exc()
            return

    @staticmethod
    def decomp_ret(fund_ret: pd.Series, factor_names: Tuple[str], universe: str) -> Optional[pd.Series]:
        ret_rg = StockFactorApi.get_stock_factor_ret(factor_names, universe)
        if ret_rg is None:
            print(f'[decomp_ret] retrieve return of {factor_names} failed')
            return
        try:
            fund_ret = fund_ret.dropna()
            rg = fund_ret.to_frame().join(ret_rg).ffill()
            rg = rg[rg.notna().all(axis=1)]
            # 计算基金全时长的因子暴露
            Y = rg.iloc[:, 0]
            X = sm.add_constant(rg.iloc[:, 1:])
            model1 = sm.OLS(Y, X)
            resu1 = model1.fit()
            return pd.Series(resu1.params[1:], index=ret_rg.columns, name=fund_ret.name)
        except Exception as e:
            print(f'[decomp_ret] abnormal error when decomp return (err_msg){e}')
            traceback.print_exc()
            return

    @staticmethod
    def fac_pos(fund_id: str, factor_names: Tuple[str], report_date: datetime.date) -> Optional[pd.DataFrame]:
        df = FundHoldStockFactor().get()
        if df is None:
            print(f'[fac_pos] failed to get data of fund hold stock')
            return
        df = df[(df.fund_id == fund_id) & (df.datetime == report_date)]
        df = df[df.notna().all(axis=1)]
        if df.empty:
            print(f'[fac_pos] empty df, can not calc (fund_id){fund_id} (report_date){report_date}')
            return

        s_list: List[pd.Series] = []
        try:
            for one in factor_names:
                try:
                    factor = DerivedFactor._registry[one]
                except KeyError as e:
                    print(f'[fac_pos] invalid stock factor name {one} (err_msg){e}')
                    continue
                f_val = factor.get()
                if f_val is None:
                    print(f'[fac_pos] retrieve value of {one} failed')
                    continue
                anjou = []
                weight = []
                for i in range(1, 11):
                    lis = df['rank'+str(i)+'_stock_code'].values
                    mult1 = pd.DataFrame(f_val[lis].iloc[-1])
                    mult1.columns = ['rank'+str(i)+'_fac']
                    mult2 = pd.DataFrame(df['rank'+str(i)+'_stockweight']).set_index(df['rank'+str(i)+'_stock_code'])
                    mult2.columns = ['rank'+str(i)+'_fac']
                    w = mult2.copy()
                    w.index = df.fund_id.to_list()
                    weight.append(w)
                    louis = (mult1 * mult2).replace({np.nan: 0})
                    louis.index = df.fund_id.to_list()
                    anjou.append(louis)
                res = (pd.concat(anjou, axis=1).sum(axis=1) / pd.concat(weight, axis=1).sum(axis=1)).rename(one)
                s_list.append(res)
        except Exception as e:
            print(f'[fac_pos] abnormal error when calc fac pos (err_msg){e}')
            traceback.print_exc()
            return
        res_df = pd.DataFrame(s_list)
        if res_df.empty:
            return
        return res_df[fund_id]


class StockFactorUpdater:

    @staticmethod
    def do_update_everyday(end_date: str, universe_list: Optional[Tuple[str]]) -> List[str]:
        def do_one_factor_update(obj) -> bool:
            if obj.name in factor_done:
                return True
            # 遍历每一个依赖, 先进行所依赖因子的更新, 这里递归可能很深
            ret = True
            for dep in obj._deps:
                ret &= do_one_factor_update(dep)
            if not isinstance(obj, (BasicFactor, DerivedFactor)):
                print(f'invalid factor {obj.name} (type){type(obj)}')
                nonlocal failed_f
                failed_f.append(obj.name)
                return False
            if isinstance(obj, MixFactorBase):
                if universe_list is not None:
                    for universe in universe_list:
                        obj.calc(universe)
                        ret &= obj.save(universe)
                        if ret:
                            print(f'save {obj.name} on {universe} done')
                        else:
                            print(f'save {obj.name} on {universe} failed')
            else:
                obj.calc()
                ret &= obj.save()
            if ret:
                print(f'save {obj.name} done')
            else:
                print(f'save {obj.name} failed')
            if isinstance(obj, DerivedFactor) and universe_list is not None:
                for universe in universe_list:
                    obj.calc_ret(universe)
                    ret &= obj.save_ret(universe)
                    if ret:
                        print(f'save ret of {obj.name} on {universe} done')
                    else:
                        print(f'save ret of {obj.name} on {universe} failed')
            factor_done.add(obj.name)
            return ret

        # 从derived因子驱动, 更新每一个因子
        failed_f: List[str] = []
        print('to update all factors')
        for one in (TradingDayList, StockIndustryInfoFactor, FundHoldStockFactor):
            obj = one()
            try:
                obj.calc()
                if isinstance(obj, TradingDayList):
                    # 不存trading day list, 但需要trim一下
                    obj.trim_by_date(end_date)
                elif not isinstance(obj, StockIndustryInfoFactor):
                    obj.save()
            except Exception as e:
                print(f'update util factor {obj.name} failed (err_msg){e}')
                traceback.print_exc()
                failed_f.append(obj.name)
        print('update utils done')
        factor_done = set()
        for obj in DerivedFactor._registry.values():
            try:
                result = do_one_factor_update(obj)
            except Exception as e:
                print(f'update derived factor {obj.name} failed (err_msg){e}')
                traceback.print_exc()
                failed_f.append(obj.name)
            else:
                if not result:
                    failed_f.append(obj.name)
        print('update all normal factors done')
        spec_factors = [DefaultFactors()]
        for obj in spec_factors:
            result = True
            try:
                for universe in universe_list:
                    obj.calc_ret(universe)
                    result &= obj.save_ret(universe)
                    if result:
                        print(f'save ret of {obj.name} on {universe} done')
                    else:
                        print(f'save ret of {obj.name} on {universe} failed')
            except Exception as e:
                print(f'update special factor {obj.name} failed (err_msg){e}')
                traceback.print_exc()
                failed_f.append(obj.name)
            else:
                if not result:
                    failed_f.append(obj.name)
        print('update all factors done')
        return failed_f


class FundFactorUpdater:

    @staticmethod
    def usage(txt=''):
        time.sleep(1)
        process = psutil.Process(os.getpid())
        num = process.memory_info()[0] / float(2 ** 20)
        print(f'\t{txt} memery usage {num}')
    
    @staticmethod
    def get_class_str_name(fac_class):
        return str(fac_class).split('.')[-1].split("'")[0]

    @staticmethod
    def do_update_every_week() -> List[str]:
        # 更新至现在

        def do_one_factor_update(obj) -> bool:
            ret = True
            if obj.name in factor_done:
                #Factor._factor_names_set.discard(obj.name)
                return True
            if obj._deps != set():
                for dep in obj._deps:
                    ret &= do_one_factor_update(dep)

            if type(obj) in append_update_factor_name:
                print(f'[append method] [{obj.name}] ')
                ret &= obj.append_update()
            else:
                print(f'[history method] [{obj.name}] ')
                obj.calc()
                ret &= obj.save()
            if ret:
                txt = f'[save] {obj.name} on done'
                factor_done.add(obj.name)
                obj.clear(recursive=True)
                FundFactorUpdater.usage(txt)
            else:
                print(f'[save] {obj.name} on failed')
            return ret
                
        factor_list = fund_basic_factor + fund_derived_factor + fund_derived_score
        append_update_factor_name = fund_append_update_factor
        factor_done = set()
        failed_f = set()
        for one in factor_list:
            try:
                obj_name = FundFactorUpdater.get_class_str_name(one)
                result = do_one_factor_update(one())
            except Exception as e:
                print(f'update derived factor {obj_name} failed (err_msg){e}')
                traceback.print_exc()
                failed_f.add(obj_name)
            else:
                if not result:
                    failed_f.add(obj_name)
        return failed_f