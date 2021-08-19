
import datetime
from typing import List, Tuple, Optional
import pandas as pd
import traceback

from ...api.basic import BasicDataApi
from ...api.derived import DerivedDataApi
from ...view.derived_models import FundScoreExtended
from .derived_data_helper import DerivedDataHelper, normalize, score_rescale


class FundScoreGroupV1Process:

    _SPECIAL_LIST = ['国际(QDII)基金']
    _BLOCK_LIST = ('商品型基金',)

    def __init__(self, data_helper: DerivedDataHelper, data_cycle: int):
        self._data_helper = data_helper
        self._data_cycle = str(data_cycle) + 'Y'
        self._result: Optional[pd.DataFrame] = None

    def init(self, start_date: str, end_date: str):
        self._end_date = end_date
        self._fund_info: pd.DataFrame = BasicDataApi().get_fund_info().drop(columns='_update_time').set_index('fund_id')
        # 获取计算评分需要用到的indicator
        self._fund_indicator_group: pd.DataFrame = DerivedDataApi().get_fund_indicator_group(start_date, end_date, self._data_cycle).drop(columns='_update_time').set_index('fund_id')

    @staticmethod
    def _get_columns_weight_by_wind_class(wind_class: str) -> Tuple[List[str], List[float]]:
        if wind_class in ('偏股混合型基金', '普通股票型基金', '平衡混合型基金', '灵活配置型基金','股票多空'):
            columns_weight = {'annual_ret': 0.2, 'sharpe': 0.6, 'info_ratio': 0.15, 'continue_stats_v': 0.05}
        elif wind_class in ('中长期纯债型基金', '短期纯债型基金', '混合债券型一级基金', '混合债券型二级基金', '偏债混合型基金', '货币市场型基金'):
            columns_weight = {'annual_ret': 0.3, 'sharpe': 0.6, 'continue_stats_v': 0.1}
        elif wind_class in ('增强指数型基金', '增强指数型债券基金'):
            columns_weight = {'annual_ret': 0.2, 'continue_stats_v': 0.05, 'alpha': 0.75}
        elif wind_class in ('被动指数型基金', '被动指数型债券基金'):
            columns_weight = {'annual_ret': 0.2, 'continue_stats_v': 0.1, 'treynor': 0.7}
        elif wind_class in ('国际(QDII)基金', 'REITs'):
            columns_weight = {'annual_ret': 0.2, 'sharpe': 0.175, 'info_ratio': 0.175, 'continue_stats_v': 0.1, 'alpha': 0.175, 'treynor': 0.175}
        else:
            assert False, f'invalid wind class!! {wind_class}'
        return list(columns_weight.keys()), list(columns_weight.values())

    def _calc_score(self, x: pd.DataFrame, by_key: str) -> pd.DataFrame:
        fin_data: pd.DataFrame = self._fund_indicator_group.loc[x.index.intersection(self._fund_indicator_group.index), :]
        wind_class: str = x[by_key].array[0]

        if wind_class in ('偏股混合型基金', '普通股票型基金', '平衡混合型基金', '灵活配置型基金'):
            data_to_calc_ret: pd.DataFrame = fin_data[fin_data.sharpe >= -20]
        else:
            data_to_calc_ret: pd.DataFrame = fin_data[fin_data.alpha <= 20]
        if data_to_calc_ret.empty:
            return
        columns, weight = FundScoreGroupV1Process._get_columns_weight_by_wind_class(wind_class)
        result1 = pd.DataFrame(index=data_to_calc_ret.index)
        result1['return_score'] = score_rescale((weight * normalize(data_to_calc_ret[columns])).sum(axis=1, keepdims=True))

        data_to_calc_others: pd.DataFrame = fin_data[fin_data.sharpe >= -20]
        result2 = pd.DataFrame(index=data_to_calc_others.index)
        result2['robust_score'] = score_rescale(-normalize(data_to_calc_others[['annual_vol']]))

        if wind_class in ('货币市场型基金'):
            # 这里是为了配合db，实际应该是scale_score
            result2['allocation_score'] = score_rescale(normalize(data_to_calc_others[['scale']]))
        else:
            result2['timing_score'] = score_rescale(normalize(data_to_calc_others[['stock_cl_beta']]))
            result2['selection_score'] = score_rescale(normalize(data_to_calc_others[['stock_cl_alpha']]))
            # 这里是为了配合db，实际应该是risk_score
            result2['allocation_score'] = score_rescale(-normalize(data_to_calc_others[['mdd']]))

        # 合并所有的评分并计算总分
        total = result1.join(result2, how='outer')
        total['total_score'] = score_rescale(normalize(total.sum(axis=1).to_frame()))
        return total

    def calc(self):
        # 按wind class 2计算
        df1: pd.DataFrame = self._fund_info[(~self._fund_info.wind_class_1.isin(self._SPECIAL_LIST)) & (~self._fund_info.wind_class_2.isin(self._BLOCK_LIST))].groupby(by='wind_class_2', sort=False).apply(self._calc_score, by_key='wind_class_2')
        if not df1.empty:
            df1 = df1.droplevel(level=0)
            df1['wind_class_1'] = self._fund_info.loc[df1.index, 'wind_class_1']
        # 按wind class 1计算
        df2: pd.DataFrame = self._fund_info[self._fund_info.wind_class_1.isin(self._SPECIAL_LIST)].groupby(by='wind_class_1', sort=False).apply(self._calc_score, by_key='wind_class_1')
        if not df2.empty:
            df2 = df2.reset_index().set_index('fund_id')
        # 两部分连到一起
        self._result = df1.append(df2)
        if not self._result.empty:
            self._result['datetime'] = self._end_date
            self._result['data_cycle'] = self._data_cycle

    def process(self, start_date: str, end_date: str, end_date_dt: datetime.date) -> List[str]:
        print(f'fund score group update on the last day of week {end_date_dt}')
        failed_tasks = []
        try:
            self.init(start_date, end_date)
            self.calc()
            if not self._result.empty:
                self._data_helper._upload_derived(self._result.reset_index(), FundScoreExtended.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'fund_score_group_v1({self._data_cycle})')
        return failed_tasks

    @staticmethod
    def update_history(end_date: str, data_cycle: int):
        from ...wrapper.mysql import BasicDatabaseConnector
        from ...view.basic_models import TradingDayList
        with BasicDatabaseConnector().managed_session() as quant_session:
            query = quant_session.query(TradingDayList)
            trade_days = pd.read_sql(query.statement, query.session.bind)

        dts = trade_days[(trade_days.datetime >= datetime.date(2010, 1, 1)) &
                         (trade_days.datetime < pd.to_datetime(end_date, infer_datetime_format=True))].datetime.tolist()
        dts.reverse()
        dts = [dt for dt in dts if dt.weekday() == 4]
        for date in dts:
            fsg = FundScoreGroupV1Process(DerivedDataHelper(), data_cycle)
            if fsg.process(date, date, pd.to_datetime(date).date()):
                print(f'{date} failed')
                break
            print(f'{date} done')


if __name__ == '__main__':
    date = '20201009'
    fsg = FundScoreGroupV1Process(DerivedDataHelper(), 1)
    fsg.process(date, date, pd.to_datetime(date).date())
    # FundScoreGroupV1Process.update_history('20201010', 5)
