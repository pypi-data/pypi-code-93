
import traceback
from typing import List, Dict
from functools import partial
from datetime import datetime

import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...api.derived import DerivedDataApi
from ...view.basic_models import StyleAnalysisStockFactor
from ...view.derived_models import StyleAnalysisFactorReturn

from .derived_data_helper import DerivedDataHelper


class StyleAnalysisProcessor:

    # 一些预定义变量, 永远不应该修改
    _STOCK_FACTOR_RETURN_SOURCE_INDEX = 'all'
    _WINDOW_LEN = 60

    def __init__(self, data_helper, universe: str = _STOCK_FACTOR_RETURN_SOURCE_INDEX):
        self._data_helper = data_helper
        self._universe: str = universe

        # 获取除const因子(市场因子)以外, basic的表中所有因子列的名字
        self._factor_columns: List[str] = StyleAnalysisStockFactor.__table__.columns.keys()[:]
        try:
            for c in ('stock_id', 'datetime', 'rate_of_return', '_update_time'):
                self._factor_columns.remove(c)
        except ValueError as e:
            print(f"it's weird, got a error {e} while dropping some columns that is not a factor")

        # universe中股票成分列表
        self._stocks: pd.DataFrame = None
        # 因子收益
        self._factor_return: List[pd.Series] = []
        # 横截面回归的r2
        self._r2: List[float] = []
        # 横截面回归时每一天的样本容量
        self._sample_nums: List[float] = []
        # 横截面回归时每一天universe中实际的样本容量
        self._real_sample_nums: List[float] = []

        # 基金收益归因信息
        self._fund_attribution: Dict[str, pd.DataFrame] = {}
        self._fund_attribution_list: List[pd.Series] = []

        # 因子暴露(时间序列回归系数)信息
        self._exposure_estimated: Dict[str, pd.DataFrame] = {}
        self._exposure_estimated_list: List[pd.Series] = []

    @property
    def STOCK_FACTOR_RETURN_SOURCE_INDEX(self):
        return self._STOCK_FACTOR_RETURN_SOURCE_INDEX

    @property
    def FACTOR_COLUMNS(self):
        return self._factor_columns

    @property
    def WINDOW_LEN(self):
        return self._WINDOW_LEN

    def _section_regression(self, x: pd.DataFrame):
        # x是截面上(一个时间点上)universe中所有股票的信息
        df = x.dropna().reset_index(level='stock_id')
        if df.shape[0] == 0:
            # 如果这一天没有universe中任何股票的信息，则直接返回(无法做回归)
            return

        # 记一下样本容量
        self._sample_nums.append(df.shape[0])

        # 根据这一天的日期获取对应时间点上的指数成分信息
        assert df.index.nunique() == 1, 'the number of unique values of index in section regression must be 1!!'
        if self._stocks is not None:
            stock_list = self._stocks.loc[df.index.date[0], 'stock_list'].split(',')
            # 只使用成分股做回归
            df = df[df['stock_id'].isin(stock_list)]

        # 记一下根据指数成分过滤后实际的样本容量
        self._real_sample_nums.append(df.shape[0])

        # 对每种风格因子做标准化
        normalized = StandardScaler().fit_transform(df.loc[:, self.FACTOR_COLUMNS].to_numpy())
        # 收益率对const(市场因子)+所有风格因子做横截面回归
        results = sm.OLS(df.loc[:, 'rate_of_return'].to_numpy(), sm.add_constant(normalized)).fit()
        # 记录r2以及rate_of_return
        self._r2.append(results.rsquared)
        # 将系数(因子收益率)保存下来, 然后再加上日期和universe
        return pd.Series(dict(zip(['const']+self.FACTOR_COLUMNS, results.params.tolist()))).append(pd.Series({'universe_index': self._universe}))

    def calculate(self, start_date: str, end_date: str):
        start_date = datetime.strptime(start_date, '%Y%m%d').date().isoformat()
        end_date = datetime.strptime(end_date, '%Y%m%d').date().isoformat()

        # 由于需要shift, 所以需要从start_date往前多取一些数据
        trading_day = BasicDataApi().get_trading_day_list().set_index('datetime')
        start_date_loc = trading_day.index.get_loc(datetime.strptime(start_date, '%Y-%m-%d').date(), method='ffill')
        assert isinstance(start_date_loc, int), 'start date is not a valid trading day'

        extra_days = 2
        assert start_date_loc >= extra_days, 'there is no enough extra days before start date'

        start_date_with_extra_days = trading_day.index.array[start_date_loc-extra_days]
        print(f'start date with extra days: {start_date_with_extra_days}')

        # 获取指数成分信息(时间序列)
        if self._universe != self.STOCK_FACTOR_RETURN_SOURCE_INDEX:
            self._stocks = RawDataApi().get_em_index_component(start_date_with_extra_days, end_date, [self._universe]).set_index('datetime')
            print('load index component data done')
        else:
            print('calculation on whole market, no need to get index component')

        # 获取风格分析因子值
        factor_values = BasicDataApi().get_style_analysis_data(start_date_with_extra_days, end_date).drop(columns='_update_time')
        print('load style analysis data done')

        # 收益率列, 存在一些日期的股票没有值, 如未上市等, 这里不做处理后边直接dropna
        rate_of_return: pd.DataFrame = factor_values.pivot_table(index='datetime', columns='stock_id', values='rate_of_return')
        if self._stocks is not None:
            # 指数成分信息与因子值进行索引对齐(空值bfill填充, 因为没有前值)
            self._stocks = self._stocks.reindex(rate_of_return.index, method='bfill')
            assert not self._stocks.isnull().to_numpy().any(), 'index component df should not have any NaN!!'
        # 收益率列向上移1行, 使得其他列T-1日对应T日收益率
        factor_values = factor_values.set_index(['datetime', 'stock_id'])
        factor_values['rate_of_return'] = rate_of_return.shift(-1).stack()

        # 对每个时间点做横截面回归
        self._factor_return = factor_values.groupby(level='datetime').apply(self._section_regression)
        # 最后再整体下移1行, 使得日期与收益率的日期对齐(均为T日, 之前为T-1日对应T日收益率)
        self._factor_return = self._factor_return.shift(1).dropna()

    def process(self, start_date, end_date):
        failed_tasks = []
        try:
            self.calculate(start_date, end_date)
            # 将风格因子收益率的时间序列存到DB
            self._data_helper._upload_derived(self._factor_return.loc[start_date:end_date, :].reset_index(), StyleAnalysisFactorReturn.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'style_analysis_factor_return({self._universe})')
        return failed_tasks

    # def analyse_stock(self, start_date: str, end_date: str, stock_ids: List[str]):
    #     # 取一只个股的收益率时间序列
    #     stock_price = RawDataApi().get_em_stock_price(start_date, end_date, stock_ids, ['stock_id', 'datetime', 'close', 'pre_close']).set_index('datetime')
    #     df = stock_price.pivot_table(index='datetime', columns='stock_id', values='close') / stock_price.pivot_table(index='datetime', columns='stock_id', values='pre_close') - 1
    #     print(df)

    #     # style_factor_return = DerivedDataApi().get_style_factor_return(start_date, end_date, self.STOCK_FACTOR_RETURN_SOURCE_INDEX).set_index('datetime')
    #     style_factor_return = pd.DataFrame(self._factor_return)
    #     for stock in df.columns:
    #         # 个股的收益率时间序列对风格因子收益率的时间序列做回归
    #         results = sm.OLS(df.loc[:, stock].to_numpy(), style_factor_return.loc[:, self.FACTOR_COLUMNS].to_numpy()).fit()
    #         return pd.Series(dict(zip(self.FACTOR_COLUMNS, results.params.tolist()))).append(pd.Series({'universe_index': self.STOCK_FACTOR_RETURN_SOURCE_INDEX}))
    #         # print(df.loc[:, stock] - style_factor_return.loc[:, self.FACTOR_COLUMNS] * regr.coef_)

    def _lambda_2(self, x, whole):
        # x是基金每日收益率, 对相应日期的const+风格因子收益做回归(加前置的常数项)(使用前WINDOW_LEN日)
        results = sm.OLS(x[:-1].to_numpy(), sm.add_constant(whole.loc[x.index[:-1], ['const']+self.FACTOR_COLUMNS].to_numpy())).fit()
        # 回归结果中包含常数项系数，这里只取另外几个indicator的系数(即上边的const+风格因子收益)
        # T+1日各因子收益的贡献 = T+1日因子收益 * 前WINDOW_LEN日回归系数
        contribution = whole.loc[x.index[-1], ['const']+self.FACTOR_COLUMNS] * results.params[1:]
        # T+1日特异收益率 = T+1日基金收益 - T+1日各因子收益的贡献和
        spec_ret = x.array[-1] - sum(contribution)

        # 记录T+1日各因子收益的贡献, 特异收益率, 基金收益率等信息
        self._fund_attribution_list.append(contribution.append(pd.Series({'spec_ret': spec_ret, 'rate_of_return': x.array[-1], 'datetime': x.index.array[-1]})))
        # 记录对前WINDOW_LEN日回归得到的因子暴露(回归系数), r2等信息
        self._exposure_estimated_list.append(pd.Series(dict(zip(['const']+self.FACTOR_COLUMNS, results.params[1:].tolist()))).append(pd.Series({'r2': results.rsquared, 'datetime': x.index.array[-1]})))
        # 这里简单起见未使用返回值, 而是直接将信息记录在类中
        return 0

    def _lambda_1(self, style_factor_return, fund_info, x):
        # 获取基金的universe
        index_id = (fund_info[fund_info['fund_id'] == x.name].loc[:, 'index_id'].array[0])
        # 取出所有该universe下的所有风格因子收益
        style_factor_return = style_factor_return[style_factor_return['universe_index'] == index_id].set_index('datetime')
        # 将基金的复权净值列加到风格因子收益df里做成一个整体
        # 先统一index, 且基金每日收益率的nan值用0填充
        # 然后dropna, 这样后边rolling的窗口数可以保证是真实的
        whole = style_factor_return.assign(rate_of_return=x.reindex(style_factor_return.index)).dropna()
        # 对这张完整df做rolling
        whole.loc[:, 'rate_of_return'].rolling(window=self.WINDOW_LEN+1).apply(func=self._lambda_2, kwargs={'whole': whole})

        self._fund_attribution[x.name] = pd.DataFrame(self._fund_attribution_list)
        self._exposure_estimated[x.name] = pd.DataFrame(self._exposure_estimated_list)
        # print(self._fund_attribution[x.name])
        print(self._fund_attribution[x.name]['spec_ret'])

    def analyse_fund(self, start_date: str, end_date: str, fund_ids: List[str]):
        # 取基金的收益率时间序列
        fund_nav = BasicDataApi().get_fund_nav(fund_ids)
        # 复权净值的nan使用上一日的值
        df = fund_nav.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value').fillna(method='ffill')
        assert not df.isnull().to_numpy().any(), 'fund nav df should not have any NaN!!'
        # 计算每日净值增长率
        df = df / df.shift(1) - 1

        # 从fund_info中获取fund_id和fund_index
        fund_info = BasicDataApi().get_fund_info().loc[:, ['fund_id', 'index_id']]
        # 只需要我们要分析的基金的信息
        fund_info = fund_info[fund_info['fund_id'].isin(fund_ids)]
        # 这里还是先用传进来的 universe 来做 index 了
        fund_info['index_id'] = self._universe
        # 将基金信息中的index_id作为universe获取风格因子收益
        style_factor_return = DerivedDataApi().get_style_factor_return(start_date, end_date, fund_info['index_id'].to_list())
        # TODO do a reindex to stock by fund index
        # style_factor_return.reindex(fund_nav.index)

        # 对每一列(即每只基金)进行计算, apply进去的是该基金的复权净值时间序列
        df.apply(partial(self._lambda_1, style_factor_return, fund_info))


if __name__ == "__main__":
    data_helper = DerivedDataHelper()
    for universe in ('hs300', 'csi800', 'all'):
        sap = StyleAnalysisProcessor(data_helper, universe)
        sap.process('20210601', '20210601')
