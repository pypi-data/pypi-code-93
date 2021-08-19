
import datetime
from typing import List, Tuple, Optional, Dict
import pandas as pd
import traceback
import numpy as np

from ...api.basic import BasicDataApi
from ...api.derived import DerivedDataApi
from ...view.derived_models import FundScoreNew
from .derived_data_helper import DerivedDataHelper, FUND_CLASSIFIER, normalize, score_rescale, cont_rescale


class FundScoreGroupProcess:

    _SPECIAL_LIST = ['国际(QDII)基金']
    _FEATURE_RANGE = (0.8, 1.2)

    def __init__(self, data_helper: DerivedDataHelper, data_cycle: int):
        self._data_helper = data_helper
        # 单位: 年
        self._data_cycle = str(data_cycle) + 'Y'
        self._result: Optional[pd.DataFrame] = None
        self._wind_class_to_type: Dict[str, str] = {}
        for k, v in FUND_CLASSIFIER.items():
            for one in v:
                self._wind_class_to_type[one] = k

    def init(self, start_date: str, end_date: str):
        self._end_date = end_date
        self._end_date_dt = pd.to_datetime(end_date).date()
        self._fund_info: pd.DataFrame = BasicDataApi().get_fund_info().drop(columns='_update_time').set_index('fund_id')
        # 获取计算评分需要用到的indicator
        self._fund_indicator_group_origin: pd.DataFrame = DerivedDataApi().get_fund_indicator_group(start_date, end_date, self._data_cycle).drop(columns='_update_time').set_index('fund_id')
        # 过滤掉scale为0的fund
        self._fund_indicator_group = self._fund_indicator_group_origin[self._fund_indicator_group_origin.scale > 0]
        # 基金经理评分以及基金经理信息
        self._fund_manager_score: pd.DataFrame = DerivedDataApi().get_fund_manager_score(start_date=start_date, end_date=end_date).drop(columns='_update_time').set_index(['manager_id', 'fund_type'])
        self._fund_manager_info: pd.dataFrame = DerivedDataApi().get_fund_manager_info().drop(columns='_update_time').set_index('fund_id')

    @staticmethod
    def _get_columns_weight_by_wind_class(wind_class: str) -> Tuple[List[str], List[float]]:
        if wind_class in ('偏股混合型基金', '普通股票型基金', '平衡混合型基金', '灵活配置型基金', '股票多空'):
            columns_weight = {'annual_ret': 0.2, 'sharpe': 0.6, 'info_ratio': 0.15, 'continue_stats_v': 0.05}
        elif wind_class in ('中长期纯债型基金', '短期纯债型基金', '混合债券型一级基金', '混合债券型二级基金', '偏债混合型基金', '货币市场型基金'):
            columns_weight = {'annual_ret': 0.3, 'sharpe': 0.6, 'continue_stats_v': 0.1}
        elif wind_class in ('增强指数型基金', '增强指数型债券基金'):
            columns_weight = {'annual_ret': 0.2, 'continue_stats_v': 0.05, 'alpha': 0.75}
        elif wind_class in ('被动指数型基金', '被动指数型债券基金'):
            columns_weight = {'annual_ret': 0.2, 'continue_stats_v': 0.1, 'treynor': 0.7}
        elif wind_class in ('国际(QDII)基金', 'REITs', '商品型基金'):
            columns_weight = {'annual_ret': 0.2, 'sharpe': 0.175, 'info_ratio': 0.175, 'continue_stats_v': 0.1, 'alpha': 0.175, 'treynor': 0.175}
        else:
            assert False, f'invalid wind class!! {wind_class}'
        return list(columns_weight.keys()), list(columns_weight.values())

    def _calc_score(self, x: pd.DataFrame, by_key: str) -> pd.DataFrame:

        fin_data: pd.DataFrame = self._fund_indicator_group.loc[x.index.intersection(self._fund_indicator_group.index), :]
        wind_class: str = x[by_key].array[0]

        if wind_class in ('偏股混合型基金', '普通股票型基金', '平衡混合型基金', '灵活配置型基金', '股票多空'):
            data_to_calc_ret: pd.DataFrame = fin_data[fin_data.sharpe >= -20]
        else:
            data_to_calc_ret: pd.DataFrame = fin_data[fin_data.alpha <= 20]
        # columns, weight = FundScoreGroupProcess._get_columns_weight_by_wind_class(wind_class)
        result1 = pd.DataFrame(index=data_to_calc_ret.index)
        if result1.shape[0] == 0:
            return

        # 第一个维度打分 综合收益能力
        if wind_class == '普通股票型基金':
            ret_temp = 0.6 * normalize(data_to_calc_ret['sharpe']) + 0.2 * normalize(data_to_calc_ret['info_ratio_hs300']) + 0.2 * normalize(data_to_calc_ret['annual_ret'])
            result1['return_score'] = score_rescale(ret_temp * cont_rescale(data_to_calc_ret['continue_stats_v'], feature_range=self._FEATURE_RANGE))
        elif wind_class in ('增强指数型基金', '增强指数型债券基金'):
            ret_temp = 0.6 * normalize(data_to_calc_ret['alpha']) + 0.2 * normalize(data_to_calc_ret['info_ratio']) + 0.2 * normalize(data_to_calc_ret['annual_ret'])
            result1['return_score'] = score_rescale(ret_temp * cont_rescale(data_to_calc_ret['continue_stats_v'], feature_range=self._FEATURE_RANGE))
        elif wind_class in ('被动指数型基金', '被动指数型债券基金'):
            track_temp = data_to_calc_ret['track_err']
            result1['return_score'] = score_rescale(-track_temp)
        elif wind_class in ('偏股混合型基金', '平衡混合型基金', '灵活配置型基金', '股票多空'):
            ret_temp = 0.6 * normalize(data_to_calc_ret['sharpe']) + 0.2 * normalize(data_to_calc_ret['info_ratio']) + 0.2 * normalize(data_to_calc_ret['annual_ret'])
            result1['return_score'] = score_rescale(ret_temp * cont_rescale(data_to_calc_ret['continue_stats_v'], feature_range=self._FEATURE_RANGE))
        elif wind_class in ('偏债混合型基金', '中长期纯债型基金', '短期纯债型基金', '混合债券型一级基金', '混合债券型二级基金'):
            ret_temp = 0.6 * normalize(data_to_calc_ret['stutzer']) + 0.2 * normalize(data_to_calc_ret['info_ratio']) + 0.2 * normalize(data_to_calc_ret['annual_ret'])
            result1['return_score'] = score_rescale(ret_temp * cont_rescale(data_to_calc_ret['continue_stats_v'], feature_range=self._FEATURE_RANGE))
        elif wind_class == '货币市场型基金':
            ret_temp = data_to_calc_ret['winning_rate']
            result1['return_score'] = score_rescale(ret_temp)
        else:
            ret_temp = normalize(data_to_calc_ret['sharpe']) + normalize(data_to_calc_ret['info_ratio']) + normalize(data_to_calc_ret['annual_ret']) + normalize(data_to_calc_ret['alpha'])
            result1['return_score'] = score_rescale(ret_temp)

        # result1['return_score'] = score_rescale((weight * normalize(data_to_calc_ret[columns])).sum(axis=1, keepdims=True))

        data_to_calc_others: pd.DataFrame = fin_data[fin_data.sharpe >= -20]
        result2 = pd.DataFrame(index=data_to_calc_others.index)
        # 第二个维度打分 稳定性能力
        result2['robust_score'] = score_rescale(-normalize(data_to_calc_others[['annual_vol']]))

        # 第三个维度打分 抗风险能力
        if wind_class in ('偏股混合型基金', '普通股票型基金', '平衡混合型基金', '灵活配置型基金', '增强指数型基金', '被动指数型基金', '股票多空'):
            risk_temp = normalize(-data_to_calc_others['mdd']) + normalize(-data_to_calc_others['mdd_len']) + normalize(data_to_calc_others['VaR']) + normalize(data_to_calc_others['CVaR'])
        elif wind_class in ('偏债混合型基金', '中长期纯债型基金', '短期纯债型基金', '混合债券型一级基金', '混合债券型二级基金', '增强指数型债券基金', '被动指数型债券基金'):
            risk_temp = normalize(-data_to_calc_others['mdd']) + normalize(data_to_calc_others['VaR']) + normalize(data_to_calc_others['CVaR']) + normalize(np.log(data_to_calc_others['scale'])) + normalize(-data_to_calc_others['ins_holds'])
        # 需要再加杠杆率和到期期限
        elif wind_class in ('货币市场型基金'):
            risk_temp = normalize(np.log(data_to_calc_others['scale'])) + normalize(-data_to_calc_others['ins_holds']) + normalize(-data_to_calc_others['leverage']) + normalize(-data_to_calc_others['ptm'])
        else:
            risk_temp = normalize(-data_to_calc_others['mdd']) + normalize(data_to_calc_others['VaR'])
        result2['risk_score'] = score_rescale(risk_temp)

        # 第四个和第五个维度计算 择时能力  选证能力
        if wind_class in ('货币市场型基金', '被动指数型基金', '被动指数型债券基金', '中长期纯债型基金'):
            data_to_calc_others['hold_num'] = data_to_calc_others['hold_num'].replace(0,1) # log 0 计算错误
            scale_temp = normalize(np.log(data_to_calc_others['scale'])) + normalize(np.log(data_to_calc_others['hold_num']))
            result2['timing_score'] = score_rescale(scale_temp)
            ins_temp = normalize(data_to_calc_others['ins_holds'])
            result2['selection_score'] = score_rescale(ins_temp)
        else:
            result2['timing_score'] = score_rescale(normalize(data_to_calc_others[['stock_cl_beta']]))
            result2['selection_score'] = score_rescale(normalize(data_to_calc_others[['stock_cl_alpha']]))

        # 第六个维度 基金经理评分
        mng_data = self._fund_info.loc[fin_data.index][['wind_class_2']]
        mng_data.loc[:,'fund_type'] = mng_data.wind_class_2.map(self._wind_class_to_type)
        managers_holds = self._fund_manager_info[( self._fund_manager_info.start_date <= self._end_date_dt)
                                & (self._fund_manager_info.end_date >= self._end_date_dt)]
        mng_data = mng_data.join(managers_holds[['mng_id']]).dropna(subset=['mng_id']).reset_index()
        manager_score = self._fund_manager_score[['score']].reset_index().rename(columns={'manager_id':'mng_id'})
        result3 = pd.merge(mng_data, manager_score, on = ['mng_id','fund_type']) 
        if not result3.empty:
            result3 = result3[['score','fund_id']].groupby(by='fund_id').max().rename(columns={'score':'team_score'})
        # 合并所有的评分并计算总分
        total = result1.join(result2, how='outer')
        if not result3.empty:
            total = total.join(result3, how='outer')
        total['total_score'] = score_rescale(normalize(total.sum(axis=1).to_frame()))
        if wind_class == '货币市场型基金':
            total = total.loc[total['risk_score'].dropna().index]
        return total

    def calc(self):
        # 按wind class 2计算
        df1: pd.DataFrame = self._fund_info[~self._fund_info.wind_class_1.isin(self._SPECIAL_LIST)].groupby(by='wind_class_2', sort=False).apply(self._calc_score, by_key='wind_class_2')
        if not df1.empty:
            df1 = df1.droplevel(level=0)
            df1['wind_class_1'] = self._fund_info.loc[df1.index, 'wind_class_1']
        # 按wind class 1计算
        df2: pd.DataFrame = self._fund_info[self._fund_info.wind_class_1.isin(self._SPECIAL_LIST)].groupby(by='wind_class_1', sort=False).apply(self._calc_score, by_key='wind_class_1')
        if not df2.empty:
            df2 = df2.reset_index().set_index('fund_id')
        # 两部分连到一起
        self._result = df1.append(df2)
        self._result['team_score'] = self._result.team_score.fillna(0)
        abnormal_df = self._fund_indicator_group_origin[~self._fund_indicator_group_origin['abnormal_reason'].isnull()]
        self._result = self._result.join(abnormal_df[['abnormal_reason']],how='outer')
        self._result['datetime'] = self._end_date_dt
        self._result['data_cycle'] = self._data_cycle

    def process(self, start_date: str, end_date: str, end_date_dt: datetime.date) -> List[str]:
        print(f'fund score group update on the last day of week {end_date_dt}')
        failed_tasks = []
        try:
            self.init(start_date, end_date)
            self.calc()
            self._data_helper._upload_derived(self._result.reset_index(), FundScoreNew.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'fund_score_group({self._data_cycle})')
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
            fsg = FundScoreGroupProcess(DerivedDataHelper(), data_cycle)
            if fsg.process(date, date, pd.to_datetime(date).date()):
                print(f'{date} failed')
                break
            print(f'{date} done')


if __name__ == '__main__':
    date = '20200930'
    fsg = FundScoreGroupProcess(DerivedDataHelper(), 5)
    fsg.process(date, date, pd.to_datetime(date).date())
    # FundScoreGroupProcess.update_history('20201010', 5)
