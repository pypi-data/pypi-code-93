
from typing import Tuple, List, Dict
from functools import partial
import math
import datetime
from dataclasses import dataclass, field
import numpy as np
import pandas as pd

from ...api.raw import RawDataApi
# from ...view.view_models import TianData
# from ...wrapper.mysql import ViewDatabaseConnector


@dataclass
class TianCollectionProcessor():
    # 一些常量
    YI: float = field(init=False, default=math.pow(10, 8))
    FIN_DATE_LIST: Tuple[str] = field(init=False, default=('2017-12-31', '2018-12-31', '2019-12-31'))

    # 内部使用，非参数
    _industry_rank: Dict[str, pd.DataFrame] = field(init=False, default_factory=dict)
    _mb_industry_rank: Dict[str, pd.DataFrame] = field(init=False, default_factory=dict)

    def _scored_by_valuation(self, industry_df: pd.DataFrame, value_df: pd.Series) -> int:
        # 权重
        w = [0.6, 0.3, 0.1]
        weight: float = self._industry_rank[value_df.bl_em_ind_code].loc[value_df.name, ['pe_ttm_deducted', 'pb_lyr_n', 'ps_ttm']].mul(w).sum()

        industry_value = industry_df.loc[value_df.bl_em_ind_code, :]
        gt_pe = value_df.pe_ttm_deducted > industry_value.pe_ttm_deducted
        gt_pb = value_df.pb_lyr_n > industry_value.pb_lyr_n
        gt_ps = value_df.ps_ttm > industry_value.ps_ttm
        value_sum = gt_pe + gt_pb + gt_ps
        if value_sum == 3:
            return round(1 + 2 * weight)
        elif value_sum == 2:
            return round(4 + weight)
        elif value_sum == 1:
            return round(6 + weight)
        else:
            return round(8 + 2 * weight)

    def _scored_by_pledge_ratio(self, value_df: pd.Series) -> int:
        value = value_df.hold_frozen_amt_accum_ratio
        if np.isnan(value):
            return 10
        elif value >= 70:
            return 4
        elif value >= 60:
            return 5
        elif value >= 50:
            return 6
        elif value >= 40:
            return 7
        elif value >= 30:
            return 8
        else:
            return 10

    def _scored_by_price(self, price_df: pd.DataFrame, value_df: pd.DataFrame) -> int:
        score = 5
        if value_df.close >= price_df[price_df.loc[:, 'stock_id'] == value_df.name].loc[:, 'close'].quantile(q=0.8):
            score -= 1
        return score

    def _scored_by_industry(self, value_df: pd.DataFrame) -> float:
        # 权重
        w = [0.4, 0.4, 0.1, 0.05, 0.05]
        try:
            weight: float = self._mb_industry_rank[value_df.mb].loc[value_df.name, ['mv', 'total_asset', 'balance_statement_141_2019-12-31', 'income_statement_9_2019-12-31', 'income_statement_61_2019-12-31']].mul(w).sum()
        except KeyError:
            weight: float = self._industry_rank[value_df.bl_em_ind_code].loc[value_df.name, ['mv', 'total_asset', 'balance_statement_141_2019-12-31', 'income_statement_9_2019-12-31', 'income_statement_61_2019-12-31']].mul(w).sum()
        return round(weight * 10, 2)

    def _get_mb(self, value_df: pd.Series) -> str:
        mb_sales_cons = value_df['mb_sales_cons_2019-12-31'] or value_df['mb_sales_cons_2018-12-31'] or value_df['mb_sales_cons_2017-12-31']
        if pd.isnull(mb_sales_cons):
            return ''
        # 简单取主营收入构成中的第一项的名称
        first_mb = mb_sales_cons.split(',')[0]
        return first_mb.split(':')[0]

    # rzw TODO: 日期参数化
    # rzw TODO: 不要在列后边加日期，使用组合索引(日期也作为索引之一)
    def compute_collection(self, end_date: str):
        raw_data_api = RawDataApi()
        # 取18个月的股价
        price_df = raw_data_api.get_em_stock_price('2018-09-01', end_date)
        # 股票基本信息
        info_df = raw_data_api.get_em_stock_info().set_index('stock_id')
        # 股票每日更新数据，基本只取最新一天的就可以
        daily_df = raw_data_api.get_em_daily_info(start_date=end_date, end_date=end_date).set_index('stock_id')
        # 股票财务数据（季报，年报数据）
        fin_df = raw_data_api.get_em_stock_fin_fac(date_list=self.FIN_DATE_LIST)
        if any((price_df is None, info_df is None, daily_df is None, fin_df is None)):
            print('get base em stock info failed when computing tian collection')
            return
        temp_df_list: List[pd.DataFrame] = []
        # 遍历每个datetime
        for name, group in fin_df.groupby(by='datetime'):
            # 每个group内drop掉datetime列后将其余列都加上日期后缀（包括季报和年报的时间）
            temp_df_list.append(group.set_index('stock_id').drop(columns='datetime').rename(columns=lambda x: x+'_'+name.isoformat()))
        # 将所有这些列粘到一起
        fin_df = pd.concat(temp_df_list, axis=1)

        # 在这里列出来各个table需要用到的一些字段
        info_data_list: List[str] = ['name', 'bl_em_ind_code']
        price_data_list: List[str] = ['close']
        daily_data_list: List[str] = ['total_share', 'hold_frozen_amt_accum_ratio',
                                      'pe_ttm_deducted', 'pb_lyr_n', 'ps_ttm', 'a_holder']
        fin_data_list: List[str] = ['np_ttmrp', 'performance_express_parent_ni', 'mb_sales_cons', 'mb_sales_cons_p', 'gp_margin', 'np_margin',
                                    'inv_turn_ratio', 'ar_turn_ratio', 'expense_toor', 'roe_avg', 'roe_wa', 'eps_basic', 'eps_diluted', 'bps',
                                    'balance_statement_25', 'balance_statement_46', 'balance_statement_93', 'balance_statement_103',
                                    'balance_statement_141', 'balance_statement_140', 'income_statement_9', 'income_statement_48', 'income_statement_60',
                                    'income_statement_61', 'income_statement_85', 'income_statement_127', 'income_statement_14', 'cashflow_statement_39',
                                    'cashflow_statement_59', 'cashflow_statement_77', 'cashflow_statement_82', 'cashflow_statement_86']
        # 手工拼一下带日期的列
        real_fin_data_list: List[str] = []
        for date in self.FIN_DATE_LIST:
            for fin in fin_data_list:
                real_fin_data_list.append(fin+'_'+date)
        # 取到所有需要的数据，price_df只取end_date的close
        df = pd.concat([info_df.loc[:, info_data_list], price_df[price_df.loc[:, 'datetime'] == datetime.date.fromisoformat(end_date)].loc[:, price_data_list+['stock_id']].set_index('stock_id'),
                        daily_df.loc[:, daily_data_list], fin_df.loc[:, real_fin_data_list]], axis=1)
        # 干掉没有东财分类的行
        df = df[~df['bl_em_ind_code'].isnull()]
        # 计算总市值和总资产
        df['mv'] = df['close'] * df['total_share']
        df['total_asset'] = df['balance_statement_25_2019-12-31'] + df['balance_statement_46_2019-12-31']

        # 计算主营业务
        df['mb'] = df.apply(self._get_mb, axis='columns')
        print(df.shape)
        # 计算行业数据（按东财行业分类以及按主营业务分类）
        industry_df = pd.DataFrame(columns=['bl_em_ind_code', 'pe_ttm_deducted', 'pb_lyr_n', 'ps_ttm'])
        mb_industry_df = pd.DataFrame(columns=['mb', 'pe_ttm_deducted', 'pb_lyr_n', 'ps_ttm'])
        for _, row in df.iterrows():
            # 按东财行业分类
            if row.bl_em_ind_code not in industry_df.loc[:, 'bl_em_ind_code'].to_list():
                industry_temp_df = df[row.bl_em_ind_code == df['bl_em_ind_code']].loc[:, ['pe_ttm_deducted', 'pb_lyr_n', 'ps_ttm',
                    'mv', 'total_asset', 'balance_statement_141_2019-12-31', 'income_statement_9_2019-12-31', 'income_statement_61_2019-12-31']]
                # 保存下来几个指标的行业中位数
                industry_df = industry_df.append({
                    'bl_em_ind_code': row.bl_em_ind_code,
                    'pe_ttm_deducted': industry_temp_df.loc[:, 'pe_ttm_deducted'].median(),
                    'pb_lyr_n': industry_temp_df.loc[:, 'pb_lyr_n'].median(),
                    'ps_ttm': industry_temp_df.loc[:, 'ps_ttm'].median(),
                }, ignore_index=True)
                # 保存下来每只股票中几个指标的行业排名分位数
                self._industry_rank[row.bl_em_ind_code] = pd.concat([
                    industry_temp_df.loc[:, 'pe_ttm_deducted'].rank(ascending=False, pct=True),
                    industry_temp_df.loc[:, 'pb_lyr_n'].rank(ascending=False, pct=True),
                    industry_temp_df.loc[:, 'ps_ttm'].rank(ascending=False, pct=True),
                    industry_temp_df.loc[:, 'mv'].rank(pct=True),
                    industry_temp_df.loc[:, 'total_asset'].rank(pct=True),
                    industry_temp_df.loc[:, 'balance_statement_141_2019-12-31'].rank(pct=True),
                    industry_temp_df.loc[:, 'income_statement_9_2019-12-31'].rank(pct=True),
                    industry_temp_df.loc[:, 'income_statement_61_2019-12-31'].rank(pct=True),
                ], axis='columns')
            # 按主营业务分类
            mb = self._get_mb(row)
            if mb and mb not in mb_industry_df.loc[:, 'mb'].to_list():
                mb_industry_temp_df = df[mb == df['mb']].loc[:, ['pe_ttm_deducted', 'pb_lyr_n', 'ps_ttm', 'mv', 'total_asset', 'balance_statement_141_2019-12-31', 'income_statement_9_2019-12-31', 'income_statement_61_2019-12-31']]
                mb_industry_df = mb_industry_df.append({
                    'mb': mb,
                    'pe_ttm_deducted': mb_industry_temp_df.loc[:, 'pe_ttm_deducted'].median(),
                    'pb_lyr_n': mb_industry_temp_df.loc[:, 'pb_lyr_n'].median(),
                    'ps_ttm': mb_industry_temp_df.loc[:, 'ps_ttm'].median(),
                }, ignore_index=True)
                self._mb_industry_rank[mb] = pd.concat([
                    mb_industry_temp_df.loc[:, 'pe_ttm_deducted'].rank(ascending=False, pct=True),
                    mb_industry_temp_df.loc[:, 'pb_lyr_n'].rank(ascending=False, pct=True),
                    mb_industry_temp_df.loc[:, 'ps_ttm'].rank(ascending=False, pct=True),
                    mb_industry_temp_df.loc[:, 'mv'].rank(pct=True),
                    mb_industry_temp_df.loc[:, 'total_asset'].rank(pct=True),
                    mb_industry_temp_df.loc[:, 'balance_statement_141_2019-12-31'].rank(pct=True),
                    mb_industry_temp_df.loc[:, 'income_statement_9_2019-12-31'].rank(pct=True),
                    mb_industry_temp_df.loc[:, 'income_statement_61_2019-12-31'].rank(pct=True),
                ], axis='columns')
        industry_df.set_index('bl_em_ind_code', inplace=True)

        # filter 1 读取wind四级行业分类中所有入选的股票
        stocks_in_industry = pd.read_excel('./config_tian/stocks_in_industry_2.xlsx', sheet_name='industry_lv4')
        stocks: List[str] = []
        for _, value in stocks_in_industry.loc[:, 'stocks'].items():
            for stock in value.split(';'):
                one = stock.split(',')[0]
                if one in df.index:
                    stocks.append(one)

        df = df.loc[stocks, :]
        print(f'num in stock pool: {len(df)}')
        # filter 2 按总市值过滤
        df = df[(df['mv'] >= 30*self.YI) & (df['mv'] <= 500*self.YI)]
        print(f'num after filtered by mv: {len(df)}')
        # filter 3 按控股股东质押率过滤
        df = df[df['hold_frozen_amt_accum_ratio'].isnull() | df['hold_frozen_amt_accum_ratio'] < 80]
        print(f'num after filtered by hold_frozen_amt_accum_ratio: {len(df)}')
        '''
        # filter 4 按最近三年净利润过滤
        df = df[((df['np_ttmrp_2019-12-31'].isnull()) & (df['performance_express_parent_ni_2019-12-31'] > 0) & (df['np_ttmrp_2018-12-31'] > 0) & (df['np_ttmrp_2017-12-31'] > 0)) |
                ((df['np_ttmrp_2019-12-31'] > 0) & (df['np_ttmrp_2018-12-31'] > 0) & (df['np_ttmrp_2017-12-31'] > 0))]
        print(f'num after filtered by np_ttmrp: {len(df)}')
        '''

        # scoring
        scored_df = pd.DataFrame()
        scored_df['name'] = df.loc[:, 'name']
        # 估值维度打分
        scored_df['scored_by_valuation'] = df.loc[:, ['bl_em_ind_code', 'pe_ttm_deducted', 'pb_lyr_n', 'ps_ttm']].apply(partial(self._scored_by_valuation, industry_df), axis='columns')
        # 控股股东质押率维度打分
        scored_df['scored_by_pledge_ratio'] = df.loc[:, ['hold_frozen_amt_accum_ratio']].apply(self._scored_by_pledge_ratio, axis='columns')
        # 股价维度打分
        scored_df['scored_by_price'] = df.loc[:, ['close']].apply(partial(self._scored_by_price, price_df), axis='columns')
        # 行业地位维度打分
        scored_df['scored_by_industry'] = df.loc[:, ['bl_em_ind_code', 'mb']].apply(self._scored_by_industry, axis='columns')
        # 总分扩展到百分制
        scored_df['score'] = scored_df.loc[:, ['scored_by_valuation', 'scored_by_pledge_ratio', 'scored_by_price', 'scored_by_industry']].apply(lambda x: x.sum()*100/35, axis='columns')
        scored_df['score(partial)'] = scored_df.loc[:, ['scored_by_valuation', 'scored_by_pledge_ratio', 'scored_by_price', 'scored_by_industry']].apply(lambda x: x.sum(), axis='columns')

        # 读取benchmark
        benchmark_df = pd.read_excel('./config_tian/tf_stock_pool_2th.xlsx', sheet_name='评分表', index_col=1)
        scored_df = scored_df[scored_df['name'].isin(benchmark_df['股票简称'])]
        for row in benchmark_df[['股票简称', '行业地位', '估值', '实控人', '历史股价', '总得分']].itertuples():
            scored_df.at[scored_df['name'] == row.股票简称, 'benchmark_score_by_industry'] = row.行业地位
            scored_df.at[scored_df['name'] == row.股票简称, 'benchmark_score_by_valuation'] = row.估值
            scored_df.at[scored_df['name'] == row.股票简称, 'benchmark_score_by_pledge_ratio'] = row.实控人
            scored_df.at[scored_df['name'] == row.股票简称, 'benchmark_score_by_price'] = row.历史股价
            scored_df.at[scored_df['name'] == row.股票简称, 'benchmark_score(partial)'] = row.行业地位 + row.估值 + row.实控人 + row.历史股价
            scored_df.at[scored_df['name'] == row.股票简称, 'benchmark_score'] = row.总得分
        '''
        for c in ['benchmark_score_by_industry', 'benchmark_score_by_valuation', 'benchmark_score_by_pledge_ratio', 'benchmark_score_by_price', 'benchmark_score']:
            scored_df[c] = scored_df[c].astype('int32')
        '''

        scored_df['score(with tf)'] = scored_df['score(partial)'] + scored_df['benchmark_score'] - scored_df['benchmark_score(partial)']

        # 计算总分的几个绝对误差
        scored_df['score_ae'] = scored_df['score'].sub(scored_df['benchmark_score']).abs()
        scored_df['score(with tf)_ae'] = scored_df['score(with tf)'].sub(scored_df['benchmark_score']).abs()
        scored_df['score(partial)_ae'] = scored_df['score(partial)'].sub(scored_df['benchmark_score(partial)']).abs()

        # 按几个决定误差由高到低排序
        scored_df.sort_values(by=['score(with tf)_ae', 'score(partial)_ae', 'score_ae'], ascending=False, inplace=True)
        output_list = ['name', 'scored_by_industry', 'benchmark_score_by_industry', 'scored_by_valuation', 'benchmark_score_by_valuation',
                       'scored_by_pledge_ratio', 'benchmark_score_by_pledge_ratio', 'scored_by_price', 'benchmark_score_by_price',
                       'score', 'score(with tf)', 'benchmark_score', 'score_ae', 'score(with tf)_ae', 'score(partial)', 'benchmark_score(partial)', 'score(partial)_ae']
        print(scored_df[output_list])
        scored_df[output_list].to_csv('./score.csv', float_format='%.2f')
        # df.to_sql(TianData.__tablename__, ViewDatabaseConnector().get_engine(), index=False, if_exists='append')


if __name__ == '__main__':
    TianCollectionProcessor().compute_collection('2020-02-28')
