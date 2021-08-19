
from datetime import datetime
import traceback

import pandas as pd

from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...view.basic_models import StyleAnalysisStockFactor
from .basic_data_helper import BasicDataHelper, add_column_to_style_analysis_factor


class StockFactor:

    _SHORT_TERM_DAYS = 20
    _LONG_TERM_DAYS = 242
    _HIGH_LOW_DAYS = 20

    def __init__(self, _data_helper):
        self.data_helper: BasicDataHelper = _data_helper
        # 记录因子值
        self._factors: pd.DataFrame = None

    @property
    def SHORT_TERM_DAYS(self):
        return self._SHORT_TERM_DAYS

    @property
    def LONG_TERM_DAYS(self):
        return self._LONG_TERM_DAYS

    @property
    def HIGH_LOW_DAYS(self):
        return self._HIGH_LOW_DAYS

    def init(self, start_date: str, end_date: str):
        # 由于有rolling, 所以需要从start_date往前多取一些数据
        trading_day = BasicDataApi().get_trading_day_list().set_index('datetime')
        start_date_loc = trading_day.index.get_loc(datetime.strptime(start_date, '%Y-%m-%d').date(), method='ffill')
        assert isinstance(start_date_loc, int), 'start date is not a valid trading day'

        extra_days = max((self.SHORT_TERM_DAYS, self.LONG_TERM_DAYS, self.HIGH_LOW_DAYS))
        assert start_date_loc >= extra_days, 'there is no enough extra days before start date'

        start_date_with_extra_days = trading_day.index.array[start_date_loc-extra_days]
        print(f'start date with extra days: {start_date_with_extra_days}')

        raw_api = RawDataApi()
        # 获取未复权收盘价
        self._stock_price = raw_api.get_em_stock_price(start_date_with_extra_days, end_date, columns=['close', 'trade_status']).set_index(['stock_id', 'datetime'])
        # 干掉当天没有进行交易的股票, 但这样的话往前取的数据可能不够rolling窗口使用了
        # self._stock_price[~self._stock_price['trade_status'].isin(('停牌一天', '暂停上市', '连续停牌'))]
        print('load stock price done')

        # 使用未复权股价的索引
        self._factors = pd.DataFrame(index=self._stock_price.index)

        # 获取后复权收盘价及前收
        self._stock_post_price = raw_api.get_em_stock_post_price(start_date_with_extra_days, end_date, columns=['close', 'pre_close', 'trade_status']).set_index(['stock_id', 'datetime'])
        # 干掉当天没有进行交易的股票, 但这样的话往前取的数据可能不够rolling窗口使用了
        # self._stock_post_price[~self._stock_post_price['trade_status'].isin(('停牌一天', '暂停上市', '连续停牌'))]
        # 按道理索引应该与未复权df完全一致，但可能值是一样的但顺序不同，这里reindex一下
        self._stock_post_price = self._stock_post_price.reindex(index=self._stock_price.index)
        print('load stock post price done')
        pd.testing.assert_index_equal(self._stock_post_price.index, self._stock_price.index)
        # reindex可能掩盖了不一致，这里看一下是否有某一行除了索引之外全为null
        assert not self._stock_post_price.isnull().all(axis=1).any(), 'stock post price df should not have any NaN!!'

        # 获取每日更新的总股本
        self._stock_daily_info = raw_api.get_em_daily_info(start_date_with_extra_days, end_date, columns=['total_share']).set_index(['stock_id', 'datetime'])
        # 与未复权股价的索引对齐(空值保持为nan)
        self._stock_daily_info = self._stock_daily_info.reindex(index=self._stock_price.index)
        # 对齐后将每只个股时间序列上总股本为nan的值ffill, TODO 再bfill
        self._stock_daily_info['total_share'] = self._stock_daily_info.reset_index().pivot_table(index='stock_id', columns='datetime', values='total_share', dropna=False).fillna(method='ffill', axis=1).fillna(method='bfill', axis=1).stack()
        print('load stock daily info done')
        assert not self._stock_daily_info.isnull().to_numpy().any(), 'stock daily info df should not have any NaN!!'

        # 获取归属于母公司股东权益合计以及其他权益工具(计算PB)
        # 注意这里不传日期参数, 获取全表的数据; 这是必要的, 因为下边的ffill需要一直向上来找到有效的值
        self._stock_fin_fac = raw_api.get_em_stock_fin_fac().set_index(['stock_id', 'datetime']).loc[:, ['balance_statement_140', 'balance_statement_195']]
        # 先做一个fillna让所有财报日期上都有值, 因为后续reindex会让很多日期所对应的行消失
        self._stock_fin_fac['balance_statement_140'] = self._stock_fin_fac.reset_index().pivot_table(index='stock_id', columns='datetime', values='balance_statement_140', dropna=False).fillna(method='ffill', axis=1).stack()
        # 与未复权股价的索引对齐(空值保持为nan)
        self._stock_fin_fac = self._stock_fin_fac.reindex(index=self._stock_price.index)
        # 其他权益工具的nan均置为0
        self._stock_fin_fac['balance_statement_195'] = self._stock_fin_fac['balance_statement_195'].fillna(0)
        # 对齐后将每只个股时间序列上归属于母公司股东权益合计为nan的值ffill, 因此这里start_date_with_extra_days应该是一个财报日期（最好为年报）
        # TODO: 先再做个bfill
        self._stock_fin_fac['balance_statement_140'] = self._stock_fin_fac.reset_index().pivot_table(index='stock_id', columns='datetime', values='balance_statement_140', dropna=False).fillna(method='ffill', axis=1).fillna(method='bfill', axis=1).stack()
        print('load stock fin fac done')

    def _lambda_1(self, x) -> pd.Series:
        window = x.rolling(window=self.HIGH_LOW_DAYS)
        return (window.max() - window.min()) / (window.max() + window.min())

    def calculate_factors(self):
        # 收益率 = 每日收盘价 / 每日前收盘价 - 1, 后复权
        self._factors['rate_of_return'] = self._stock_post_price.loc[:, 'close'] / self._stock_post_price.loc[:, 'pre_close'] - 1
        print('calculate rate_of_return done')

        # 规模 = 每日总股本 * 每日收盘价, 未复权
        self._factors['latest_size'] = self._stock_daily_info.loc[:, 'total_share'] * self._stock_price.loc[:, 'close']
        print('calculate latest_size done')

        # 价值 = 1 / PB = (归属于母公司股东权益合计 - 其他权益工具) / 规模, 未复权
        self._factors['bp'] = (self._stock_fin_fac.loc[:, 'balance_statement_140'] - self._stock_fin_fac.loc[:, 'balance_statement_195']) / self._factors.loc[:, 'latest_size']
        print('calculate bp done')

        # 短期动量, group by stock_id, 在每一只股票上按时间做rolling, 取窗口内日收益率的和
        self._factors['short_term_momentum'] = self._factors.loc[:, ['rate_of_return']].groupby(level='stock_id').apply(lambda x: x.rolling(window=self.SHORT_TERM_DAYS).sum())
        print('calculate short_term_momentum done')

        # 长期动量, group by stock_id, 在每一只股票上按时间做rolling, 取窗口内日收益率的和
        self._factors['long_term_momentum'] = self._factors.loc[:, ['rate_of_return']].groupby(level='stock_id').apply(lambda x: x.rolling(window=self.LONG_TERM_DAYS).sum())
        print('calculate long_term_momentum done')

        # 波动率, group by stock_id, 在每一只股票上按时间做rolling, 取窗口内收盘价(最大值-最小值)/(最大值+最小值)
        self._factors['high_low'] = self._stock_post_price.loc[:, ['close']].groupby(level='stock_id').apply(self._lambda_1)
        print('calculate high_low done')

    def process_all(self, start_date: str, end_date: str):
        start_date = datetime.strptime(start_date, '%Y%m%d').date().isoformat()
        end_date = datetime.strptime(end_date, '%Y%m%d').date().isoformat()
        failed_tasks = []
        try:
            self.init(start_date, end_date)
            self.calculate_factors()
            self.data_helper._upload_basic(self._factors.reset_index().set_index('datetime').loc[start_date:end_date].reset_index(), StyleAnalysisStockFactor.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(StyleAnalysisStockFactor.__table__.name)
        return failed_tasks

    # 注意该函数应该一次性执行后将一些逻辑加到process_all函数中, 以实现新因子值的每日更新
    def add_factor(self):
        # 先获取DB中整张数据表的日期范围, 以此来作为新因子计算时所需数据的日期范围
        time_range_df = BasicDataApi().get_style_analysis_time_range()
        assert time_range_df.shape[0] == 1, 'invalid time range df'

        start_date, end_date = time_range_df.iloc[0, :].loc[['start_date', 'end_date']].to_list()
        print(f'time range for adding factor: {start_date} to {end_date}')

        # 通过api获取计算新因子所需的数据

        # 计算新因子每一天的值

        # 将新因子插入到DB中新的一列
        pivot_df = pd.DataFrame()
        new_column_name = ''
        add_column_to_style_analysis_factor(pivot_df, new_column_name)


if __name__ == "__main__":
    StockFactor(BasicDataHelper()).process_all('20031231', '20141231')
