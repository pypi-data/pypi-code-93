import pandas as pd
import datetime
from pandas.tseries.offsets import DateOffset
from ...util.singleton import Singleton
from ..wrapper.mysql import ViewDatabaseConnector
from ..view.view_models import *


class ViewDataApi(metaclass=Singleton):
    @staticmethod
    def get_fund_daily_collection():
        with ViewDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(FundDailyCollection)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns=FundDailyCollection.trans_columns())
                df['fund_type'] = df['基金大类类型']
                return df
            except Exception as e:
                print(e)
                return False

    @staticmethod
    def get_daily_index_collection():
        with ViewDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(IndexDailyCollection)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns=IndexDailyCollection.trans_columns())
                return df
            except Exception as e:
                print(e)
                return False

    @staticmethod
    def get_daily_fund_automatic_investment():
        with ViewDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(AutomaticInvestmentCollection)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns=AutomaticInvestmentCollection.trans_columns())
                return df
            except Exception as e:
                print(e)
                return False

    @staticmethod
    def get_daily_fund_daily_result(fund_id_list = []):
        with ViewDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    FundDailyCollection.fund_id,
                    FundDailyCollection.return_score,
                    FundDailyCollection.robust_score,
                    FundDailyCollection.risk_score,
                    FundDailyCollection.timing_score,
                    FundDailyCollection.selection_score,
                    FundDailyCollection.team_score,
                    FundDailyCollection.total_score,
                ).filter(
                    FundDailyCollection.fund_id.in_(fund_id_list)
                )
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns=FundDailyCollection.trans_columns())
                return df
            except Exception as e:
                print(e)
                return False

    @staticmethod
    def get_recent_stock_ipo():
        def _get_relate_date_df(df, dt):
            _df = df[df.上市日期 > dt]
            _df_normal = _df[_df.交易板块.isin(['深交所中小板','上交所主板'])]
            _df_gem = _df[_df.交易板块 == '深交所创业板']
            _df_star = _df[_df.交易板块 == '上交所科创板']
            res = {
                'data':_df,
                '普通新股只数':_df_normal.shape[0],
                '普通新股平均连板天数':_df_normal.连续涨停.mean(),
                '普通新股平均每签获利':_df_normal.每签获利.mean(),
                '创业板新股只数':_df_gem.shape[0],
                '创业板新股首日破发数':_df_gem[_df_gem.首日涨幅 < 0].shape[0],
                '创业板平均首日涨幅':_df_gem.首日涨幅.mean(),
                '科创新股只数':_df_star.shape[0],
                '科创新股首日破发数':_df_star[_df_star.首日涨幅 < 0].shape[0],
                '科创新股平均每日涨幅':_df_star.首日涨幅.mean(),
            }
            return res

        with ViewDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(StockIpoCollection)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns=StockIpoCollection.trans_columns()).drop(columns='_update_time')
                today = datetime.datetime.now().date()
                date_3m_ago = (today - DateOffset(months=3)).date()
                date_6m_ago = (today - DateOffset(months=6)).date()
                date_1y_ago = (today - DateOffset(years=1)).date()
                result = {
                    '近三月':_get_relate_date_df(df, date_3m_ago),
                    '近六月':_get_relate_date_df(df, date_6m_ago),
                    '近一年':_get_relate_date_df(df, date_1y_ago),
                }
                return result
            except Exception as e:
                print(e)
                return False

    @staticmethod
    def get_recent_conv_bond_ipo():
        def _get_relate_date_df(df, dt):
            _df = df[df.上市日期 > dt]
            res = {
                'data':_df,
                '上市数量':_df.shape[0],
                '首日破发数':_df[_df.首日涨幅 < 0].shape[0],
                '首日破发率':_df[_df.首日涨幅 < 0].shape[0] / _df.shape[0],
                '每签最大收益':_df.每签获利.max(),
                '每签最大亏损':abs(min(_df.每签获利.min(), 0)),
                '单账户累计收益':_df.单账户收益.sum(),
            }
            return res
        
        with ViewDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(ConvBondIpoCollection)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns=ConvBondIpoCollection.trans_columns()).drop(columns='_update_time')
                today = datetime.datetime.now().date()
                date_3m_ago = (today - DateOffset(months=3)).date()
                date_6m_ago = (today - DateOffset(months=6)).date()
                date_1y_ago = (today - DateOffset(years=1)).date()
                result = {
                    '近三月':_get_relate_date_df(df, date_3m_ago),
                    '近六月':_get_relate_date_df(df, date_6m_ago),
                    '近一年':_get_relate_date_df(df, date_1y_ago),
                }
                return result
            except Exception as e:
                print(e)
                return False