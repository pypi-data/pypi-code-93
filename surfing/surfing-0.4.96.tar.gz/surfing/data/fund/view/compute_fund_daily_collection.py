import pandas as pd
import traceback
import json
import math
import re
from sqlalchemy import func
from .compute_fund_recommendation_collection import FundRecommendationCollectionProcessor
from ...wrapper.mysql import (RawDatabaseConnector, BasicDatabaseConnector, DerivedDatabaseConnector, 
    ViewDatabaseConnector)
from ...view.view_models import FundDailyCollection
from ...view.basic_models import FundNav, FundInfo, FundRate, FundSize, FundRet, FundBenchmark, IndexInfo, \
    FundStatusLatest
from ...view.derived_models import FundAlpha, FundIndicator, FundScoreNew, FundManagerInfo, StyleBox
from ....constant import ExchangeStatus
from ....util.calculator import *
from ...api.derived import DerivedDataApi
from ...api.research_api import ResearchApi
from .__init__ import fund_s3_uri

class FundDailyCollectionProcessor(object):

    FUND_CLASSIFIER = {
        'QDII': ['国际(QDII)股票型基金', '国际(QDII)债券型基金', '国际(QDII)另类投资基金', '国际(QDII)混合型基金', ],
        'stock': ['普通股票型基金', '偏股混合型基金',  '被动指数型基金', '增强指数型基金', '平衡混合型基金', '灵活配置型基金', '股票多空'], 
        'bond': ['中长期纯债型基金', '短期纯债型基金', '偏债混合型基金', '增强指数型债券基金', '被动指数型债券基金','混合债券型二级基金', '混合债券型一级基金'],
        'mmf': ['货币市场型基金'],
        'index': ['被动指数型基金', '增强指数型基金', '增强指数型债券基金', '被动指数型债券基金', '商品型基金', 'REITs'],
    }

    def __init__(self):
        self.fund_type_dic = {}
        self.fund_recommend = FundRecommendationCollectionProcessor()
        for k, v in self.FUND_CLASSIFIER.items():
            for v_i in v:
                self.fund_type_dic[v_i] = k

    def get_fund_df(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    FundInfo.fund_id,
                    FundInfo.order_book_id,
                    FundInfo.wind_class_1,
                    FundInfo.wind_class_2,
                    FundInfo.start_date,
                    FundInfo.end_date,
                    #FundInfo.desc_name,
                    FundInfo.company_id,
                    FundInfo.benchmark,
                    FundInfo.desc_name,
                    FundInfo.track_index,
                    FundInfo.manage_fee,
                    FundInfo.start_date,
                    FundInfo.end_date,
                    FundInfo.risk_level,
                    FundInfo.company_id,
                    FundInfo.full_name,
                    FundInfo.currency,
                    FundInfo.manage_fee,
                    FundInfo.trustee_fee,
                    FundInfo.purchase_fee,
                    FundInfo.redeem_fee,
                    FundInfo.benchmark_1,
                    FundInfo.benchmark_2,
                    FundInfo.subscr_fee_detail,
                    FundInfo.purchase_fee_detail,
                    FundInfo.redeem_fee_detail,
                    FundInfo.service_fee,
                )
                funds = pd.read_sql(query.statement, query.session.bind)
                return funds.set_index('fund_id')
            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_fund_mng_list(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    FundInfo.fund_id,
                    FundInfo.fund_manager,
                )
                funds = pd.read_sql(query.statement, query.session.bind)
                return funds.set_index('fund_id')
            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))


    def get_fund_benchmark_df(self):
        def select_one_benchmark(x):
            if x is None:
                return None
            x = json.loads(x)
            if not x:
                return

            # 特殊常数处理
            if x.get('1'):
                return None

            select = max(x, key=x.get)
            if x[select] >= 0.8:
                return select
            return None

        def get_index_name(x, index_df):
            if not x:
                return None

            try:
                return index_df.loc[x, 'desc_name']
            except KeyError:
                return None

        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    IndexInfo
                )
                index_df = pd.read_sql(query.statement, query.session.bind)
                index_df = index_df.set_index('index_id')

                query = mn_session.query(
                    FundBenchmark.fund_id,
                    FundBenchmark.benchmark_s_raw,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                df['benchmark_s'] = df['benchmark_s_raw'].apply(select_one_benchmark)
                df.loc[df.benchmark_s == '-1','benchmark_s'] = None
                df['benchmark_name'] = df['benchmark_s'].apply(get_index_name, args=(index_df,))
                df = df.drop(columns=['benchmark_s_raw'])
                return df
            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_nav_df(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                latest_time = mn_session.query(FundNav).order_by(FundNav.datetime.desc()).limit(1).one_or_none()
                latest_time = latest_time.datetime
                subq = mn_session.query(
                    FundNav.fund_id.label('temp_id'),
                    func.max(FundNav.datetime).label('temp_date'),
                ).group_by(FundNav.fund_id).subquery()

                query = mn_session.query(
                    FundNav.fund_id,
                    FundNav.unit_net_value,
                    FundNav.acc_net_value,
                    FundNav.adjusted_net_value,
                    FundNav.datetime,
                    FundNav.change_rate,
                    FundNav.redeem_status,
                    FundNav.subscribe_status,
                ).filter(
                    FundNav.fund_id == subq.c.temp_id,
                    FundNav.datetime == subq.c.temp_date
                )

                nav = pd.read_sql(query.statement, query.session.bind)
                return nav.set_index('fund_id'), latest_time
            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_fund_nav_start_end_date(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    FundNav.fund_id,
                    FundNav.datetime,
                    FundNav.adjusted_net_value)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.pivot_table(index='datetime',values='adjusted_net_value',columns='fund_id')
                result = []
                for fund_id in df:
                    _df = df[[fund_id]].dropna()
                    dic = {
                        'fund_id':fund_id,
                        'price_begin_date':_df.index[0],
                        'price_end_date':_df.index[-1]
                    }
                    result.append(dic)
                df = pd.DataFrame(result).set_index('fund_id')
                return df
                
            except Exception as e:
                print('Failed get_fund_nav_start_end_date<err_msg> {}'.format(e))


    def get_indicator_df(self):
        with BasicDatabaseConnector().managed_session() as quant_session:
            try:
                latest_time = quant_session.query(FundRet).order_by(FundRet.datetime.desc()).limit(1).one_or_none()
                latest_time = latest_time.datetime
                query = quant_session.query(
                    FundRet.fund_id,
                    FundRet.annual_ret,
                    # FundRet.annualized_risk,
                    FundRet.vol,
                    #FundRet.avg_size,
                    FundRet.info_ratio,
                    FundRet.w1_ret,
                    FundRet.m1_ret,
                    FundRet.m3_ret,
                    FundRet.m6_ret,
                    FundRet.y1_ret,
                    FundRet.y3_ret,
                    FundRet.y5_ret,
                    FundRet.recent_y_ret,
                    FundRet.to_date_ret,
                    FundRet.sharpe_ratio,
                    FundRet.mdd,
                ).filter(FundRet.datetime==latest_time)
                indicator = pd.read_sql(query.statement, query.session.bind)
                indicator = indicator.rename(columns={
                    'annual_ret': 'annualized_returns',
                    'info_ratio': 'information_ratio',
                    'm1_ret': 'last_month_return',
                    'm6_ret': 'last_six_month_return',
                    'm3_ret': 'last_three_month_return',
                    'y1_ret': 'last_twelve_month_return',
                    'w1_ret': 'last_week_return',
                    'recent_y_ret': 'year_to_date_return',
                    'to_date_ret': 'to_date_return',
                    'sharpe_ratio': 'sharp_ratio',
                    'mdd': 'max_drop_down',
                    #'avg_size': 'average_size',
                })
                return indicator

            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_institution_rating_df(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                latest_time = mn_session.query(FundRate).order_by(FundRate.datetime.desc()).limit(1).one_or_none()
                latest_time = latest_time.datetime
                print(latest_time)
                query = mn_session.query(
                    FundRate.fund_id,
                    FundRate.mornstar_3y,
                    FundRate.mornstar_5y,
                    FundRate.sh_3y_comp,
                    FundRate.sh_5y_comp,
                    FundRate.jian_comp,
                    FundRate.merchant_3y,
                ).filter(FundRate.datetime==latest_time)
                rating = pd.read_sql(query.statement, query.session.bind)
                rating = rating.rename(columns={
                    'sh_3y_comp': 'sh3',
                    'sh_5y_comp': 'sh5',
                    'jian_comp': 'jajx',
                    'merchant_3y': 'zs',
                })
                rating['zs'] = rating['zs'].apply(lambda x: x[0] if x else None)
                return rating

            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_size_df(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    FundSize.fund_id,
                    FundSize.latest_size
                )
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.drop_duplicates(subset=['fund_id'], keep='last')
                df = df.set_index('fund_id')
                return df
            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_fund_manager_info_df(self):
        def helper(x):
            x['mng_name'] = '、'.join(x['mng_name'])
            x['mng_id'] = '、'.join(x['mng_id'])
            return x

        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    FundManagerInfo.fund_id,
                    FundManagerInfo.mng_id,
                    FundManagerInfo.mng_name,
                    FundManagerInfo.profit,
                ).filter(
                    FundManagerInfo.end_date == '2040-01-01',
                )
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.groupby(by='fund_id').apply(helper)
                df = df.drop_duplicates(subset=['fund_id'], keep='last')
                df = df.rename(columns={
                    'mng_name': 'fund_manager',
                    'mng_id': 'fund_manager_id',
                    'profit': 'manager_profit',
                })
                df = df.set_index('fund_id')
                return df
            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_fund_manager_info_raw_df(self):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    FundManagerInfo.fund_id,
                    FundManagerInfo.mng_id,
                    FundManagerInfo.mng_name,
                    FundManagerInfo.profit
                ).filter(
                    FundManagerInfo.end_date == '2040-01-01',
                )
                df = pd.read_sql(query.statement, query.session.bind)
                df = df
                return df
            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_exchange_status_df(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    FundStatusLatest.fund_id,
                    FundStatusLatest.PURCHSTATUS,
                    FundStatusLatest.REDEMSTATUS,
                    FundStatusLatest.LPLIMIT,
                    FundStatusLatest.OTCLPLIMITJG,
                    FundStatusLatest.OTCLPLIMITGR,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                print(df)
                return df
            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_alpha_df(self):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                latest_time = mn_session.query(FundAlpha).order_by(FundAlpha.datetime.desc()).limit(1).one_or_none()
                latest_time = latest_time.datetime
                print(latest_time)
                query = mn_session.query(
                    FundAlpha.fund_id,
                    FundAlpha.track_err,
                    FundAlpha.this_y_alpha,
                    FundAlpha.cumulative_alpha,
                    FundAlpha.w1_alpha,
                    FundAlpha.m1_alpha,
                    FundAlpha.m3_alpha,
                    FundAlpha.m6_alpha,
                    FundAlpha.y1_alpha,
                    FundAlpha.y3_alpha,
                    FundAlpha.y5_alpha,
                    FundAlpha.y10_alpha,
                ).filter(FundAlpha.datetime==latest_time)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.drop_duplicates(subset=['fund_id'], keep='last')
                return df

            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_style_df(self):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                latest_time = mn_session.query(StyleBox).order_by(StyleBox.datetime.desc()).limit(1).one_or_none()
                latest_time = latest_time.datetime
                query = mn_session.query(
                    StyleBox
                ).filter(StyleBox.datetime==latest_time)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df
            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_style_box_detail(self):
        def fund_style(x):
            if pd.isna(x):
                return None
            if x < 125:
                return '价值型'
            if x <= 175:
                return '平衡型'
            return '成长型'

        def fund_size(x):
            if pd.isna(x):
                return None
            if x < 100:
                return '小盘'
            if x <= 200:
                return '中盘'
            return '大盘'
        df = self.get_style_df()
        df['fund_size_type'] = df['y'].apply(fund_size)
        df['fund_style_type'] = df['x'].apply(fund_style)
        return df[['fund_size_type','fund_style_type','fund_id']].set_index('fund_id')

    def append_data(self, table_name, data_append_directly_data_df):
        if not data_append_directly_data_df.empty:
            with ViewDatabaseConnector().managed_session() as mn_session:
                try:
                    mn_session.execute(f'TRUNCATE TABLE {table_name}')
                    mn_session.commit()
                except Exception as e:
                    print(f'Failed to truncate table {table_name} <err_msg> {e}')
            data_append_directly_data_df.to_sql(table_name, ViewDatabaseConnector().get_engine(), index = False, if_exists = 'append')
            print('新数据已插入')
        else:
            print('没有需要插入的新数据')

    def get_exchange_status(self, x):
        if x['redeem_status'] == ExchangeStatus.LIMITED:
            x['redeem_status'] = ExchangeStatus.OPEN
        if x['subscribe_status'] == ExchangeStatus.LIMITED:
            x['subscribe_status'] = ExchangeStatus.OPEN
        if x['redeem_status'] == ExchangeStatus.CLOSE and x['subscribe_status'] == ExchangeStatus.CLOSE:
            return '暂停交易'
        if x['redeem_status'] == ExchangeStatus.SUSPENDED:
            return '暂停赎回'
        if x['subscribe_status'] == ExchangeStatus.SUSPENDED:
            return '暂停申购'
        if x['redeem_status'] == ExchangeStatus.OPEN and x['subscribe_status'] == ExchangeStatus.OPEN:
            return '正常开放'
        return '暂无状态'

    def get_found_to_now(self, x):
        if pd.isna(x):
            return None
        return round((pd.datetime.now().date() - x).days / 365, 2)

    def calc_ret_rank(self, df, cols):
        for col in cols:
            df[col + '_rank'] = df[col].rank(method='min', ascending=False)
        return df

    def calc_group_num(self, df):
        df['group_num'] = len(df)
        return df

    def modify_fund_manager(self, x):
        try:
            return x.split('\r\n')[-1].split('(')[0]
        except:
            return x

    def select_benchmark(self, x):
        if x['wind_class_II'] not in ('被动指数型基金', '增强指数型基金'):
            x['benchmark_s'] = None
            x['benchmark_name'] = None
        return x

    def parse_benchmark_1(self, fund_info):
        benchmark_split_chname = []
        multi_sign_list = ['*','×']
        for r in fund_info.itertuples():
            b = r.benchmark
            if b is None or b == '':
                result = None
            else:
                if multi_sign_list[0] in b and multi_sign_list[1] in b:
                    b = b.split('+')[0]
                for mul_sign in multi_sign_list:
                    if mul_sign in b:
                        result = b.split(mul_sign)[0].replace('收益率','').replace(':','')
            
            if result is not None:
                con = re.search('^\s*[0-9]+%',result)
                if con is not None:
                    for mul_sign in multi_sign_list:
                        if mul_sign in b:
                            result = b.split('+')[0].split(mul_sign)[1].replace('收益率','')
            
            if result is not None and result[0] == '(' and result[-1] == ')':
                result = result[1:-1]
            if result is not None and '(' in result and ')' not in result:
                result = result.replace('(','')
            if result == 'X':
                result = b.split('+')[0].split('*')[-1]
            benchmark_split_chname.append(result) 
        fund_info.loc[:, 'first_benchmark_name'] = benchmark_split_chname
        return fund_info

    def compute_daily_collection(self):
        try:
            funds = self.get_fund_df()
            funds = self.parse_benchmark_1(funds)
            funds = funds.reset_index()
            funds = funds.drop_duplicates(subset=['fund_id'], keep='last')
            funds = funds.set_index('fund_id')
            print('info', funds)
            print('-' * 100)

            bench = self.get_fund_benchmark_df()
            bench = bench.drop_duplicates(subset=['fund_id'], keep='last')
            bench = bench.set_index('fund_id')
            print('bench', bench)

            nav, latest_time = self.get_nav_df()
            print(latest_time)
            nav = nav.reset_index()
            nav = nav.drop_duplicates(subset=['fund_id'], keep='last')
            nav = nav.set_index('fund_id')
            print('nav', nav)
            print('-' * 100)

            alpha = self.get_alpha_df()
            alpha = alpha.set_index('fund_id')
            print(alpha)
            print('-' * 100)
            size = self.get_size_df()
            print(size)
            print('-' * 100)
            # TODO: need to remove this one
            score = pd.DataFrame()
            # score = self.get_score_df().set_index('fund_id')
            print(score)
            print('-' * 100)
            
            fund_indicator_score = pd.read_parquet(fund_s3_uri)
            
            score_name_dic = {  'ret_ability':'return_score',
                                'stable_ability':'robust_score',
                                'risk_ability':'risk_score',
                                'select_time':'timing_score',
                                'select_stock':'selection_score',
                                'mng_score':'team_score',
                                'total_score':'total_score',
                            }
            new_score = fund_indicator_score.rename(columns=score_name_dic)[list(score_name_dic.values())]      
            print(new_score)
            print('-' * 100)
            indicator_name_dic = {  'alpha~history_m':'alpha',
                                    'beta~history_m':'beta',
                                    'track_err~history_m':'tag_track_err',
                                    'info_ratio~history_m':'info_ratio',
                                    'treynor~history_m':'treynor',
                                    'mdd~history_daily':'mdd',
                                    'downside_std~history_m':'down_risk',
                                    'total_ret':'ret_over_period',
                                    'annual_ret~history_m':'annual_avg_daily_ret',
                                    'annual_vol~history_m':'annual_vol',
                                    'annual_ret~history_m':'annual_ret',
                                    'stock_cl_beta~history_w':'time_ret',
                                    'var~history_m':'var',
                                    'sharpe~history_m':'sharpe',
                                    'downside_std~history_m':'downside_std',
                                    'continue_regress_v~history_m':'continue_regress_v',
                                    'stock_cl_beta~history_w':'stock_cl_beta',
                                    'stock_cl_alpha~history_w':'stock_cl_alpha',
                                    'prn_hold':'prn_hold',
                                }
            tag_indicator = fund_indicator_score.rename(columns=indicator_name_dic)[list(indicator_name_dic.values())] 
            tag_indicator = tag_indicator.join(pd.DataFrame(funds.manage_fee + funds.trustee_fee,columns=['fee_rate']))
            tag_indicator['m_square'] = None
            tag_indicator['r_square'] = None
            print(tag_indicator)
            print('-' * 100)
            

            print('处理基金经理')
            fund_manager = self.get_fund_manager_info_df()
            print(fund_manager)
            
            print('处理推荐信息和概念')
            fund_recommend_list = ['sector_list','sector_name','index_list','index_name','mng_id','is_abs_ret_fund','is_conv_bond_fund','fund_id']
            fund_recommend_list = fund_recommend_list + ['is_ipo_fund','fund_type']
            fund_recommend_extend = self.fund_recommend.calc_whole_data()
            fund_recommend_extend = fund_recommend_extend[fund_recommend_list]

            _manager_info = self.get_fund_manager_info_raw_df()
            _col = {
                'mng_name':'top_mng_name',
                'profit':'top_manager_profit',
                'mng_id':'top_mng_id'
            }
            fund_recommend_extend = fund_recommend_extend[fund_recommend_extend.mng_id.notna()]
            fund_recommend_extend = fund_recommend_extend.set_index(['fund_id','mng_id']).join(_manager_info.set_index(['fund_id','mng_id'])).reset_index().rename(columns=_col).set_index('fund_id')
            funds = funds.drop(columns=['manage_fee','trustee_fee'])
            exchange_status = self.get_exchange_status_df().set_index('fund_id')
            print(exchange_status)
            print('-' * 100)

            print('处理机构评级')
            rating = self.get_institution_rating_df()
            rating = rating.drop_duplicates(subset=['fund_id'], keep='last')
            rating = rating.set_index('fund_id')
            print(rating)
            print('-' * 100)

            print('处理基金风格')
            style_df = self.get_style_box_detail()

            print('处理净值')
            fund_start_end_date_df = self.get_fund_nav_start_end_date()
            df = pd.concat([funds, bench, nav, alpha, size, rating, score, new_score, tag_indicator, exchange_status, fund_recommend_extend, fund_manager, style_df, fund_start_end_date_df], axis=1, sort=False)
            df.index.name = 'fund_id'
            print('_'*100)
            print(df)

            print('处理行情')
            indicator = self.get_indicator_df()
            indicator = indicator.drop_duplicates(subset=['fund_id'], keep='last')
            indicator = indicator.set_index('fund_id')
            print(indicator)
            print('-' * 100)

            df = pd.concat([df, indicator.reindex(index=df.index)], axis=1, sort=False)
            df.index.name = 'fund_id'
            df = df.reset_index()
            df = df.dropna(subset=['fund_id'])
            df['exchange_status'] = df.apply(self.get_exchange_status, axis=1)
            df['found_to_now'] = df['start_date'].apply(self.get_found_to_now)
            df = df.rename(columns={
                'wind_class_1': 'wind_class_I',
                'wind_class_2': 'wind_class_II',
                'start_date': 'found_date',
                'company_id': 'company_name',
                'desc_name': 'symbol',
            })
            df = df.groupby('wind_class_II').apply(self.calc_ret_rank, cols=[
                'last_week_return',
                'last_month_return',
                'last_three_month_return',
                'last_six_month_return',
                'last_twelve_month_return',
                'y3_ret',
                'y5_ret',
                'year_to_date_return',
                'to_date_return',
            ])
            df = df.groupby('wind_class_II').apply(self.calc_group_num)

            print(df)
            # 对于 track err 和 benchmark_name 只有一种存在的基金， 全都变成空
            con = df[['benchmark_name','tag_track_err']].isnull().sum(axis=1)
            df.loc[con[con == 1].index,'benchmark_name'] = None
            df.loc[con[con == 1].index,'benchmark_s'] = None
            df.loc[con[con == 1].index,'tag_track_err'] = None
            print(df)
            df = df.drop(['redeem_status', 'subscribe_status'], axis=1)
            df = df.sort_values(['fund_id'])
            df = df.dropna(subset=['order_book_id'])
            df.loc[:,'fund_type'] = df.wind_class_II.map(self.fund_type_dic)
            
            # 未纳入评分的基金 补头名基金经理 
            df = df.set_index('fund_id')
            _mng_df = self.get_fund_mng_list()
            for r in df.itertuples():
                fund_id = r.Index
                if isinstance(r.top_mng_name,float) and math.isnan(r.top_mng_name):
                    df.loc[fund_id,'top_mng_name'] = _mng_df.loc[fund_id,'fund_manager']
            df = df.reset_index()
            df.total_score = df.total_score.replace(0, None)
            
            # 新添加的公募数据
            fund_type_df = DerivedDataApi().get_fund_type_classification()
            fund_type_df = fund_type_df[fund_type_df['fund_type'] == '公募']
            fund_type_dic_1 = fund_type_df[['fund_class_1_ori','fund_class_1']].drop_duplicates().set_index('fund_class_1_ori')['fund_class_1'].to_dict()
            fund_type_dic_2 = fund_type_df[['fund_class_2_ori','fund_class_2']].drop_duplicates().set_index('fund_class_2_ori')['fund_class_2'].to_dict()
            research_api = ResearchApi()
            fund_info = research_api.get_fund_info()
            record_cds = fund_info.fund_id.dropna().tolist()

            col_dic = {
                'fund_id': 'fund_id',
                'start_date':'nav_start_date',
                'end_date':'nav_end_date',
                'trade_month':'nav_date',
                'nav_type':'nav_frequency',
                'fund_nav_completion':'fund_nav_completion',
                'recent_3m_annual_ret':'recent_3m_ret_annual',
                'recent_6m_annual_ret':'recent_6m_ret_annual',
                'y_last_ret_annual':'this_y_ret_annual',
                'recent_2y_annual_ret':'recent_2y_ret_annual',
                'recent_2y_ret':'recent_2y_ret',
                'y_last_mdd':'this_y_mdd',
                'recent_3m_mdd':'recent_3m_mdd',
                'recent_6m_mdd':'recent_6m_mdd',
                'recent_1y_mdd':'recent_1y_mdd',
                'recent_2y_mdd':'recent_2y_mdd',
                'calmar':'calmar',
                'sortino':'sortino',
            }
            info_dic = {
                'fund_id':'fund_id',
                'wind_class_1':'fund_type_1',
                'wind_class_2':'fund_type_2',
            }

            fund_info_part = fund_info[['fund_id','wind_class_1','wind_class_2']]
            fund_info_part = fund_info_part.rename(columns={'fund_id':'fund_id'})
            fund_info_part['fund_type_1'] = fund_info_part['wind_class_1'].map(fund_type_dic_1)
            fund_info_part['fund_type_2'] = fund_info_part['wind_class_2'].map(fund_type_dic_2)
            fund_info_part = fund_info_part[info_dic.keys()].rename(columns=info_dic)
            record_cds = fund_info_part.fund_id.dropna().tolist()

            fund_nav = pd.DataFrame()
            ints = 1000
            res = []
            for _i in range(0,len(record_cds),ints):
                df = research_api.get_fund_nav(fund_id_list = record_cds[_i:_i+ints] ,
                                                start_date = datetime.date(2000,1,1) ,
                                                end_date = datetime.datetime.now().date() )

                df = df.pivot_table(columns = "fund_id"  , values = "adjnav" , index = "datetime")
                for fund_id in df:
                    df = fund_nav[[fund_id]].dropna()
                    dic = CalculatorBase.get_stat_result(dates=df.index,values=df[fund_id].values)
                    dic['fund_id'] = fund_id
                    res.append(dic)
            result_df = pd.DataFrame(res)
            result_df = result_df[col_dic.keys()].rename(columns=col_dic)
            result = pd.merge(result_df,fund_info_part,on='fund_id')
            result = result.replace([np.inf, -np.inf], np.nan)
            data = df.set_index('fund_id').join(result.set_index('fund_id'))
            data = data.reset_index()
            self.append_data(FundDailyCollection.__tablename__, data)

            print(df)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def process(self):
        failed_tasks = []
        if not self.compute_daily_collection():
            failed_tasks.append('compute_fund_daily_collection')
        return failed_tasks


if __name__ == '__main__':
    FundDailyCollectionProcessor().compute_daily_collection()


