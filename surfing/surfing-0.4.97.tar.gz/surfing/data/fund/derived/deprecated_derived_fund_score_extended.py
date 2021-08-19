
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import traceback
import math
import json
import datetime
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...view.derived_models import FundScoreExtended
from ..basic.basic_data_helper import BasicDataHelper
from .derived_data_helper import DerivedDataHelper


class FundScoreExtendedProcess:

    # 无风险收益率
    _RF = 0.011
    _TRADING_DAYS_PER_YEAR = 242
    _BRINSON_BEGIN_DATE = '20191231'
    _BRINSON_END_DATE = '20200630'
    _BRINSON_CLASS_LIST = ("混合型基金", "股票型基金")

    def __init__(self, data_helper: DerivedDataHelper):
        self._data_helper = data_helper
        self._raw_api = RawDataApi()
        self._basic_api = BasicDataApi()

    def init(self, start_date: str, end_date: str):
        start_date: str = (pd.to_datetime(start_date) - datetime.timedelta(days=365*3+1)).strftime('%Y%m%d')
        print(f'start date for calc: {start_date}')
        self._end_date: str = end_date

        # 获取区间内交易日列表
        all_trading_days: pd.Series = self._basic_api.get_trading_day_list().drop(columns='_update_time').set_index('datetime')
        self._trading_days: pd.Series = all_trading_days.loc[pd.to_datetime(start_date).date():pd.to_datetime(end_date).date()]

        # 基金净值数据、指数价格数据的index对齐到交易日列表
        fund_nav: pd.DataFrame = self._basic_api.get_fund_nav_with_date(start_date, end_date)
        self._fund_nav: pd.DataFrame = fund_nav.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value').reindex(self._trading_days.index).fillna(method='ffill')
        index_price: pd.DataFrame = self._basic_api.get_index_price().drop(columns='_update_time')
        # 有的index最近没有数据，如活期存款利率/各种定期存款利率等，需要先reindex到全部的交易日列表上ffill
        index_price = index_price.pivot_table(index='datetime', columns='index_id', values='close').reindex(all_trading_days.index).fillna(method='ffill')
        # 再reindex到参与计算的交易日列表上
        self._index_price: pd.DataFrame = index_price.reindex(self._trading_days.index)
        pd.testing.assert_index_equal(self._fund_nav.index, self._index_price.index)

        try:
            # 这个指数有一天的点数是0，特殊处理一下
            self._index_price['spi_spa'] = self._index_price['spi_spa'].where(self._index_price.spi_spa != 0).fillna(method='ffill')
        except KeyError:
            pass

        # 对数净值取差分并且去掉第一个空值，得到基金对数收益率数列
        self._fund_ret: pd.DataFrame = np.log(self._fund_nav).diff().iloc[1:, :]

        # 计算benchmark return，且index对齐到fund_ret
        benchmark_ret: pd.DataFrame = self._get_benchmark_return()
        self._benchmark_ret: pd.DataFrame = benchmark_ret.reindex(self._fund_ret.index)
        pd.testing.assert_index_equal(self._fund_ret.index, self._benchmark_ret.index)

        # 获取待计算的基金列表
        fund_list: pd.DataFrame = self._basic_api.get_fund_info().drop(columns='_update_time')
        self._fund_list: pd.DataFrame = fund_list[fund_list.structure_type <= 1]
        # 获取wind一级分类
        self._wind_class_1: np.ndarray = fund_list.wind_class_1.unique()
        print('init done, begin to calc score')

    def _get_benchmark_return(self) -> pd.DataFrame:
        benchmark_list: Dict[str, float] = {}
        fund_benchmark_df: pd.DataFrame = self._basic_api.get_fund_benchmark().drop(columns='_update_time')
        # 遍历每一只基金的benchmark进行处理
        for row in fund_benchmark_df.itertuples(index=False):
            values: List[pd.Series] = []
            cons: float = 0
            # 空的benchmark表明我们没有对应的指数或无法解析公式
            if row.benchmark_s:
                benchmark: Dict[str, float] = json.loads(row.benchmark_s)
                benchmark_raw: Dict[str, float] = eval(row.benchmark)
                for (index, weight), index_raw in zip(benchmark.items(), benchmark_raw.keys()):
                    if index == '1':
                        # 表示benchmark中该项为常数
                        cons += weight
                    elif index in ('ddir', 'nonor', 'tmd_1y', 'tmd_2y', 'tmd_3m', 'tmd_3y', 'tmd_5y', 'tmd_6m', 'tmd_7d'):
                        if weight == -1:
                            # 表示我们无法解析公式
                            # print(f'[benchmark_return] Error: Need fix {row.fund_id} {index} {index_raw}')
                            break
                        else:
                            try:
                                ra: pd.Series = self._index_price.loc[:, index].copy()
                            except KeyError:
                                # 表示我们没有该指数的价格数据
                                # print(f'[benchmark_return] Error: Data Missing: {row.fund_id} {index} {index_raw}')
                                break
                            else:
                                values.append(ra.iloc[1:] * 0.01 * weight / self._TRADING_DAYS_PER_YEAR)
                    else:
                        if weight == -1:
                            # 表示我们无法解析公式
                            # print(f'[benchmark_return] Error: Need fix {row.fund_id} {index} {index_raw}')
                            break
                        else:
                            try:
                                ra: pd.Series = self._index_price.loc[:, index].copy()
                            except KeyError:
                                # 表示我们没有该指数的价格数据
                                # print(f'Error: Data Missing: {row.fund_id} {index} {index_raw}')
                                break
                            else:
                                ra = np.log(ra).diff().iloc[1:]
                                values.append(ra * weight)
                else:
                    if values or cons:
                        the_sum: float = sum(values)
                        if cons:
                            the_sum += np.log(math.pow(1 + cons, 1 / self._TRADING_DAYS_PER_YEAR))
                        benchmark_list[row.fund_id] = the_sum

        return pd.DataFrame.from_dict(benchmark_list)

    '''
    _get_resample_ret
    输入：日频率数据
    输出：月频率数据
    备注：输入需要DatetimeIndex
    '''
    @staticmethod
    def _get_resample_ret(df: pd.DataFrame) -> pd.DataFrame:
        df = df.set_axis(pd.to_datetime(df.index), inplace=False)
        return df.resample('1M').sum(min_count=1)

    @staticmethod
    def _from_rq_id(x: str) -> Optional[str]:
        _values = x.split('.')
        if _values[1] == 'XSHG':
            return _values[0] + '.SH'
        elif _values[1] == 'XSHE':
            return _values[0] + '.SZ'

    @staticmethod
    def _to_rq_id(x: str) -> Optional[str]:
        _values = x.split('.')
        if _values[1] == 'SH':
            return _values[0] + '.XSHG'
        elif _values[1] == 'SZ':
            return _values[0] + '.XSHE'

    @staticmethod
    def _brinson_calc_index(x: pd.DataFrame) -> pd.Series:
        total_weight: float = x.weight.sum()
        total_r: float = (x.weight * x.ret).sum()
        return pd.Series({'index_w': total_weight, 'index_r': total_r / total_weight})

    @staticmethod
    def _brinson_calc_fund(x: pd.DataFrame, index_datas: pd.DataFrame) -> pd.Series:
        total_weight: float = x.F_PRT_STKVALUE.sum()
        if total_weight != 0:
            total_r: float = (x.F_PRT_STKVALUE * x.ret).sum()
            fund_r = total_r / total_weight
        else:
            data = index_datas[index_datas.bl_sws_ind_code == x.bl_sws_ind_code]
            fund_r = data.index_r
        return pd.Series({'fund_w': total_weight, 'fund_r': fund_r})

    def _brinson_calc(self, fund_df: pd.DataFrame, index_datas: pd.DataFrame) -> pd.Series:
        # 处理一下基金持仓的市值权重
        stock_value_sum: float = fund_df.F_PRT_STKVALUE.sum()
        if stock_value_sum != 0:
            fund_df['F_PRT_STKVALUE'] /= stock_value_sum
        # 依次处理基金持仓个股所属的每一个申万一级行业
        summmary_list = fund_df.groupby('bl_sws_ind_code', sort=False).apply(FundScoreExtendedProcess._brinson_calc_fund, index_datas=index_datas)
        if summmary_list.empty:
            return
        # 结果和index数据放在一起
        summmary_list = summmary_list.join(index_datas, how='outer')
        summmary_list[['fund_w', 'fund_r']] = summmary_list.apply(lambda x: pd.Series([0, x.index_r]) if pd.isnull(x.fund_w) else pd.Series([x.fund_w, x.fund_r]), axis=1)
        # 计算分数
        summmary_list['R'] = summmary_list.loc[:, 'fund_w'] * summmary_list.loc[:, 'fund_r']
        summmary_list['Rs'] = summmary_list.loc[:, 'index_w'] * summmary_list.loc[:, 'fund_r']
        summmary_list['Bs'] = summmary_list.loc[:, 'fund_w'] * summmary_list.loc[:, 'index_r']
        summmary_list['B'] = summmary_list.loc[:, 'index_w'] * summmary_list.loc[:, 'index_r']
        summmary_list['Selection_BHB'] = summmary_list.loc[:, 'Rs'] - summmary_list.loc[:, 'B']
        summmary_list['Allocation_BHB'] = summmary_list.loc[:, 'Bs'] - summmary_list.loc[:, 'B']
        summmary_list['interaction_BHB'] = summmary_list.loc[:, 'R'] + summmary_list.loc[:, 'B'] - summmary_list.loc[:, 'Rs'] - summmary_list.loc[:, 'Bs']
        rd = summmary_list.loc[:, 'B'].sum()
        summmary_list['Allocation_BF'] = (summmary_list.loc[:, 'fund_w'] - summmary_list.loc[:, 'index_w']) * (summmary_list.loc[:, 'index_r'] - rd)
        return pd.Series({dim: summmary_list[dim].sum() for dim in ('Selection_BHB', 'Allocation_BHB', 'interaction_BHB')})

    def _brinson(self, start_date: str, end_date: str, benchmark: str = 'hs300'):
        index_weight_df: pd.DataFrame = self._raw_api.get_rq_index_weight([benchmark], start_date, end_date)
        # 暂时只用区间内第一天的数据
        index_weight: pd.Series = index_weight_df.iloc[0, :]
        # 将stock_list和weight_list打开
        index_whole_data = pd.DataFrame({'index_id': index_weight.at['index_id'], 'stock': json.loads(index_weight.at['stock_list']), 'weight': json.loads(index_weight.at['weight_list'])})
        # 米筐ID转换过来
        index_whole_data['stock'] = index_whole_data.stock.map(FundScoreExtendedProcess._from_rq_id)
        # index下的股票列表
        stock_list: List[str] = index_whole_data.stock.to_list()

        # blocklist = ['160218!0']
        # blocklist = ['001274!0','001428!0','002232!0','002834!0','002839!0','004049!0','004051!0', '005950!0','006050!0','006567!0','007234!0','007350!0','007501!0','007514!0','519618!0', '960009!0','960010!0','960013!0','960014!0','960015!0','960017!0','960019!0','960023!0', '960025!0', '960026!0', '960030!0', '960031!0', '960032!0', '960041!0', 'F050004!0', 'F050026!0', 'F080012!0', 'F161616!0', 'F202003!0', 'F450004!0', 'F450005!0', ]
        # brinson分类下的基金列表
        fund_list: List[str] = []
        for cl in self._BRINSON_CLASS_LIST:
            fund_list.extend(self._fund_list[self._fund_list.wind_class_1 == cl].wind_id.array)

        # 获取所有基金的股票持仓及持仓占比
        fund_stock_df: pd.DataFrame = self._raw_api.get_wind_fund_stock_portfolio(start_date, end_date, fund_list)
        # 暂时只用第一天的数据
        first_day = pd.to_datetime(fund_stock_df.F_PRT_ENDDATE).nsmallest(1).array[0].strftime('%Y%m%d')
        fund_whole_data: pd.DataFrame = fund_stock_df[fund_stock_df.F_PRT_ENDDATE == first_day]
        fund_whole_data = fund_whole_data[['S_INFO_WINDCODE', 'S_INFO_STOCKWINDCODE', 'F_PRT_STKVALUE']]

        # 计算全部股票列表
        stock_list.extend(fund_whole_data.S_INFO_STOCKWINDCODE.unique())
        stock_list_set = set(stock_list)

        # 获取全时间区间内所有这些股票的价格数据
        stock_list_set_rq = {FundScoreExtendedProcess._to_rq_id(one) for one in stock_list_set}
        stock_list_set_rq.discard(None)
        price_df: pd.DataFrame = self._basic_api.get_stock_price(stock_list_set_rq, start_date, end_date)
        price_df = price_df.pivot_table(index='datetime', columns='stock_id', values='close')
        # 米筐ID转换过来
        price_df = price_df.set_axis([FundScoreExtendedProcess._from_rq_id(one) for one in price_df.columns], axis=1, inplace=False)
        # 计算区间收益率
        ret: pd.Series = price_df.apply(lambda x: np.log(x.array[-1]) - np.log(x.array[0]))
        ret = ret.rename('ret')
        # 加到index上
        index_whole_data = index_whole_data.set_index('stock').join(ret, on='stock')

        # 获取各股票申万一级行业指数代码列表
        sw_ind_code: pd.Series = self._raw_api.get_em_stock_info(stock_list_set)
        sw_ind_code['bl_sws_ind_code'] = sw_ind_code.bl_sws_ind_code.transform(lambda x: x.split('-')[0])
        sw_ind_code = sw_ind_code[['bl_sws_ind_code', 'stock_id']].set_index('stock_id')
        # index加一列行业指数代码
        index_whole_data = index_whole_data.join(sw_ind_code, on='stock')

        # index的相关数据只需要计算一次即可，在这里算好
        index_datas: pd.DataFrame = index_whole_data.groupby(by='bl_sws_ind_code', sort=False).apply(FundScoreExtendedProcess._brinson_calc_index)
        # 依次计算每只基金
        result: pd.DataFrame = fund_whole_data.groupby(by='S_INFO_WINDCODE', sort=False).apply(lambda x: self._brinson_calc(x.join(ret, on='S_INFO_STOCKWINDCODE').join(sw_ind_code, on='S_INFO_STOCKWINDCODE'), index_datas))
        # 加上fund_id以及wind_class_1
        bdh = BasicDataHelper()
        result['fund_id'] = result.index.map(lambda x: bdh._get_fund_id_from_order_book_id(x.split('.')[0], pd.to_datetime(start_date).date()))
        result = result[result.fund_id.notna()]
        wind_class_dict: Dict[str] = self._fund_list[['fund_id', 'wind_class_1']].set_index('fund_id').to_dict()['wind_class_1']
        result['wind_class_1'] = result.fund_id.map(wind_class_dict)
        return result.set_index('fund_id')

    @staticmethod
    def _lambda_2(x: pd.Series, fund_ret_sampled: pd.DataFrame):
        temp: float = x.var()
        if pd.isnull(temp):
            return np.nan
        elif temp == 0:
            return 0

        fund_ret: pd.Series = fund_ret_sampled[x.name]
        if fund_ret.count() <= 1:
            return np.nan
        return x.cov(fund_ret) / temp

    @staticmethod
    def _lambda_1(x: pd.Series, fund_ret_sampled: pd.DataFrame):
        total = pd.concat({'Y': fund_ret_sampled[x.name], 'x': x}, axis=1)
        total = total[total.notna().all(axis=1)]
        if total.empty:
            return np.nan
        Y: pd.Series = total['Y']
        x = total['x']
        if x.count() != Y.count():
            return np.nan
        X: pd.DataFrame = pd.concat([x, x], axis=1)
        X.columns = [0, 1]
        X[0][X[0] < 0] = 0
        X[1][X[1] > 0] = 0
        regr = LinearRegression()
        regr.fit(X, Y)
        return regr.coef_[0] - regr.coef_[1]

    def calc(self):
        # 计算月度数据
        fund_ret_sampled: pd.DataFrame = FundScoreExtendedProcess._get_resample_ret(self._fund_ret)
        benchmark_ret_sampled: pd.DataFrame = FundScoreExtendedProcess._get_resample_ret(self._benchmark_ret)
        # 对齐基金收益和benchmark收益的月度数据的columns
        avail_fund_list: pd.Index = fund_ret_sampled.columns.intersection(benchmark_ret_sampled.columns)
        fund_ret_sampled = fund_ret_sampled.loc[:, avail_fund_list]
        benchmark_ret_sampled = benchmark_ret_sampled.loc[:, avail_fund_list]
        pd.testing.assert_index_equal(fund_ret_sampled.columns, benchmark_ret_sampled.columns)
        pd.testing.assert_index_equal(fund_ret_sampled.index, benchmark_ret_sampled.index)
        print('to calc basic factors')

        # beta
        beta = benchmark_ret_sampled.apply(self._lambda_2, fund_ret_sampled=fund_ret_sampled)

        # sharpe_ratio_M
        annualized_ret = fund_ret_sampled.sum(min_count=1) * 12 / fund_ret_sampled.shape[0]
        annualized_vol_0 = fund_ret_sampled.std(ddof=0) * math.sqrt(12)
        sharpe_ratio_M = (annualized_ret - self._RF) / annualized_vol_0

        # information_ratio
        ex_ret = fund_ret_sampled - benchmark_ret_sampled
        annualized_ex_ret = ex_ret.sum(min_count=1) * 12 / fund_ret_sampled.shape[0]
        annualized_vol_1 = fund_ret_sampled.std() * math.sqrt(12)
        information_ratio = annualized_ex_ret / annualized_vol_1

        # treynor_ratio
        treynor_ratio = annualized_ex_ret / beta

        # jensen_alpha
        rm = benchmark_ret_sampled.sum(min_count=1) * 12 / benchmark_ret_sampled.shape[0]
        jensen_alpha = annualized_ret - self._RF - beta * (rm - self._RF)

        # max_drawdown
        max_drawdown = 1 - (self._fund_nav / self._fund_nav.cummax()).min()

        # chang_lewellen
        chang_lewellen = benchmark_ret_sampled.apply(FundScoreExtendedProcess._lambda_1, fund_ret_sampled=fund_ret_sampled)

        # ret and vol
        ret = np.exp(self._fund_ret.sum(min_count=1)) - 1
        vol = self._fund_ret.std(ddof=0) * math.sqrt(12)

        total_df = pd.DataFrame.from_dict({'ret': ret, 'vol': vol, 'sr': sharpe_ratio_M, 'ir': information_ratio, 'treynor_ratio': treynor_ratio, 'beta': beta, 'alpha': jensen_alpha, 'mdd': max_drawdown, 'timing': chang_lewellen})
        total_df = total_df.replace([np.Inf, -np.Inf], np.nan)

        # brinson scores
        print('basic factors done, to calc brinson scores')
        brison_score_df = self._brinson(self._BRINSON_BEGIN_DATE, self._BRINSON_END_DATE)
        print('calc brinson scores done, to generate scores')

        df_list: List[pd.DataFrame] = []
        scaler = StandardScaler()
        minmax_scaler = MinMaxScaler()
        # blocklist = ['001274!0','001428!0','002232!0','002834!0','002839!0','004049!0','004051!0', '005950!0','006050!0','006567!0','007234!0','007350!0','007501!0','007514!0','519618!0', '960009!0','960010!0','960013!0','960014!0','960015!0','960017!0','960019!0','960023!0', '960025!0', '960026!0', '960030!0', '960031!0', '960032!0', '960041!0', 'F050004!0', 'F050026!0', 'F080012!0', 'F161616!0', 'F202003!0', 'F450004!0', 'F450005!0', ]
        for cl in self._wind_class_1:
            # 与该类型下的基金列表取交集作为新的索引
            df = total_df.reindex(total_df.index.intersection(self._fund_list[self._fund_list.wind_class_1 == cl].fund_id))
            # 每列标准化后即为各列的score
            df_standardized = scaler.fit_transform(df)
            df = df.join(pd.DataFrame(df_standardized, index=df.index, columns=[one + '_score' for one in df.columns]))
            # 计算return score
            return_score = df['ret_score']
            for ind in ('sr_score', 'ir_score', 'alpha_score', 'treynor_ratio_score'):
                return_score = return_score.add(df[ind], fill_value=0)
            df['return_score'] = return_score
            # 计算robust score
            df['robust_score'] = -(df['mdd_score'].add(df['vol_score'], fill_value=0))
            total_score_columns: List[str] = []
            for dim in ('return_score', 'robust_score', 'timing_score'):
                total_score_columns.append(dim)
                df[dim] = scaler.fit_transform(df[[dim]])
                # 百分制分数
                df[dim] = minmax_scaler.fit_transform(df[[dim]]) * 100
                df[dim.replace('score', 'rank')] = df[dim].rank(method='min', ascending=False)

            if cl in self._BRINSON_CLASS_LIST:
                df = df.join(brison_score_df[brison_score_df.wind_class_1 == cl], how='outer')
                for dim in ('Selection_BHB', 'Allocation_BHB', 'interaction_BHB'):
                    column_name = dim.split('_')[0].lower() + '_score'
                    total_score_columns.append(column_name)
                    df[column_name] = scaler.fit_transform(df[[dim]])
                    df = df.drop(columns=dim)
                    # 百分制分数
                    df[column_name] = minmax_scaler.fit_transform(df[[column_name]]) * 100
                    df[column_name.replace('score', 'rank')] = df[column_name].rank(method='min', ascending=False)

            # total_score = scaler.fit_transform(pd.DataFrame(df['return_score'].add(df['robust_score'], fill_value=0).add(df['timing_score'], fill_value=0)))
            total_score = pd.Series(index=df.index)
            for dim in total_score_columns:
                total_score = total_score.add(df[dim], fill_value=0)
            df['total_score'] = minmax_scaler.fit_transform(pd.DataFrame(total_score)) * 100
            df['total_rank'] = df['total_score'].rank(method='min', ascending=False)

            df['wind_class_1'] = cl
            df['datetime'] = self._end_date
            df = df.reset_index().rename(columns={'index': 'fund_id'})
            df_list.append(df)
            # df.to_csv('./res/' + cl + '_indicator.csv', encoding="utf_8_sig")
            # print(f'calc score for funds in {cl} done')
        self._result = pd.concat(df_list)

    def process(self, start_date: str, end_date: str, end_date_dt: datetime.date) -> List[str]:
        print(f'fund score extended update on the last day of week {end_date_dt}')
        failed_tasks = []
        try:
            self.init(start_date, end_date)
            self.calc()
            self._data_helper._upload_derived(self._result, FundScoreExtended.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('fund_score_extended')
        return failed_tasks


if __name__ == '__main__':
    start_date = '20200730'
    end_date = '20200730'
    fse = FundScoreExtendedProcess(DerivedDataHelper())
    fse.process(start_date, end_date)
