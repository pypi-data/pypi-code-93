
import datetime
from typing import List, Tuple, Union, Optional
import pandas as pd
from sqlalchemy.sql import func
from sqlalchemy import or_
from ...util.singleton import Singleton
from ..wrapper.mysql import RawDatabaseConnector
from ..view.raw_models import *
from pandas.tseries.offsets import DateOffset
import math

class RawDataApi(metaclass=Singleton):
    def get_raw_cm_index_price_df(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    CmIndexPrice
                ).filter(
                    CmIndexPrice.datetime >= start_date,
                    CmIndexPrice.datetime <= end_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {CmIndexPrice.__tablename__}')

    def get_cxindex_index_price_df(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    CxindexIndexPrice
                ).filter(
                    CxindexIndexPrice.datetime >= start_date,
                    CxindexIndexPrice.datetime <= end_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {CxindexIndexPrice.__tablename__}')

    def get_yahoo_index_price_df(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    YahooIndexPrice
                ).filter(
                    YahooIndexPrice.datetime >= start_date,
                    YahooIndexPrice.datetime <= end_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {YahooIndexPrice.__tablename__}')

    def get_rq_index_price_df(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    RqIndexPrice
                ).filter(
                    RqIndexPrice.datetime >= start_date,
                    RqIndexPrice.datetime <= end_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_wind_fund_info(self, funds: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    WindFundInfo
                )
                if funds:
                    query = query.filter(
                        WindFundInfo.wind_id.in_(funds),
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {WindFundInfo.__tablename__}')

    def get_fund_fee(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundFee
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_fund_rating(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundRating
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_stock_fin_fac(self, stock_id_list, start_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    RqStockFinFac
                ).filter(
                    RqStockFinFac.stock_id.in_(stock_id_list),
                    RqStockFinFac.datetime >= start_date,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_rq_stock_valuation(self, stock_id_list, start_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    RqStockValuation.datetime,
                    RqStockValuation.stock_id,
                    RqStockValuation.pb_ratio_lf,
                    RqStockValuation.pe_ratio_ttm,
                    RqStockValuation.peg_ratio_ttm,
                    RqStockValuation.dividend_yield_ttm,
                ).filter(
                    RqStockValuation.stock_id.in_(stock_id_list),
                    RqStockValuation.datetime >= start_date,

                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_rq_index_weight(self, index_id_list, start_date: str, end_date: str = ''):
        with RawDatabaseConnector().managed_session() as quant_session:
            try:
                query = quant_session.query(
                        RqIndexWeight.index_id,
                        RqIndexWeight.datetime,
                        RqIndexWeight.stock_list,
                        RqIndexWeight.weight_list,
                    ).filter(
                        RqIndexWeight.index_id.in_(index_id_list),
                        RqIndexWeight.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        RqIndexWeight.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_index_val_pct(self):
        with RawDatabaseConnector().managed_session() as quant_session:
            try:
                query = quant_session.query(
                        IndexValPct
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_rq_fund_indicator(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    RqFundIndicator
                ).filter(
                    RqFundIndicator.datetime >= start_date,
                    RqFundIndicator.datetime <= end_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_rq_trading_day_list(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    TradingDayList
                ).filter(
                    TradingDayList.datetime >= start_date,
                    TradingDayList.datetime <= end_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_em_tradedates(self, start_date='', end_date=''):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmTradeDates
                )
                if start_date:
                    query = query.filter(
                        EmTradeDates.TRADEDATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmTradeDates.TRADEDATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmTradeDates.__tablename__}')
                return None

    def get_stock_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    StockInfo
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_rq_fund_nav(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    RqFundNav
                ).filter(
                    RqFundNav.datetime >= start_date,
                    RqFundNav.datetime <= end_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_em_fund_nav(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        EmFundNav
                    )
                else:
                    query = db_session.query(
                        EmFundNav.CODES,
                        EmFundNav.DATES,
                    ).add_columns(*columns)
                if fund_ids:
                    query = query.filter(
                        EmFundNav.CODES.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        EmFundNav.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmFundNav.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFundNav.__tablename__}')
                return None

    def get_oversea_fund_nav(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        OSFundNav
                    )
                else:
                    query = db_session.query(
                        OSFundNav.codes,
                        OSFundNav.datetime,
                    ).add_columns(*columns)
                if fund_ids:
                    query = query.filter(
                        OSFundNav.codes.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        OSFundNav.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        OSFundNav.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundNav.__tablename__}')
                return None

    def get_oversea_fund_nav_adj(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        OSFundNavAdj
                    )
                else:
                    query = db_session.query(
                        OSFundNavAdj.codes,
                        OSFundNavAdj.datetime,
                    ).add_columns(*columns)
                if fund_ids:
                    query = query.filter(
                        OSFundNavAdj.codes.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        OSFundNavAdj.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        OSFundNavAdj.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundNavAdj.__tablename__}')
                return None

    def get_oversea_fund_ret(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        OSFundNav
                    )
                else:
                    query = db_session.query(
                        OSFundNav.codes,
                        OSFundNav.datetime,
                    ).add_columns(*columns)
                if fund_ids:
                    query = query.filter(
                        OSFundNav.codes.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        OSFundNav.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        OSFundNav.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                if df.empty:
                    return pd.DataFrame(columns=['datetime','codes','ret'])
                df = df.pivot_table(index='datetime', columns='codes', values='nav').ffill()
                df = df / df.bfill().iloc[0] - 1
                df = pd.DataFrame(df.stack()).rename(columns={0:'ret'}).reset_index()
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundNav.__tablename__}')
                return None

    def get_oversea_fund_ret_with_benchmark(self, start_date: str = '', end_date: str = '', fund_id: str='', trade_fee:float=0):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSFundNav
                ).filter(
                    OSFundNav.codes == fund_id,
                )
                if start_date:
                    query = query.filter(
                        OSFundNav.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        OSFundNav.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                benchmark_df = self.get_fund_benchmark_nav(fund_id)
                result = {}
                if df.empty:
                    df = pd.DataFrame(columns=['datetime','ret','benchmark'])
                    result['benchmark_name'] = None
                    result['benchmark_id'] = None
                    result['fund_id'] = fund_id
                    result['data'] = df
                    result['annual_ret'] = None
                    print(f'get data from {OSFundNav.__tablename__} fund_id:{fund_id} nav not existed start_date {start_date} end_date {end_date} ')
                    return result
                last_unit_nav = df.nav.values[-1] / df.nav.values[0] - trade_fee
                df = df.pivot_table(index='datetime', columns='codes', values='nav').ffill().dropna()
                annual_ret = math.pow(last_unit_nav, 365/df.shape[0]) - 1
                data_lag = 0
                if not benchmark_df.empty:
                    data_lag = (df.index.values[-1] - benchmark_df.datetime.values[-1]).days
                
                if benchmark_df.empty or data_lag > 10: # 如果指数数据考后10天，不展示指数
                    print(f'get data from {OSFundNav.__tablename__} fund_id: {fund_id} fund benchmark not exsited')
                    df.columns = ['ret']
                    df = df / df.bfill().iloc[0] - 1
                    df = df - trade_fee
                    df = df.reset_index()
                    df.loc[:,'benchmark'] = None
                    result['benchmark_name'] = None
                    result['benchmark_id'] = None
                    result['fund_id'] = fund_id
                    result['data'] = df
                    result['annual_ret'] = annual_ret
                    return result
                index_id = benchmark_df.codes.tolist()[0]
                _benchmark_df = benchmark_df.pivot_table(index='datetime', columns='codes', values='close')
                df = df.join(_benchmark_df).ffill()
                df.columns = ['ret','benchmark']
                if df.benchmark.isna().any():
                    index_list = df[df.benchmark.isnull()].index
                    df.loc[index_list, 'benchmark'] = df.loc[index_list, 'ret']
                    next_dt = df.loc[index_list[-1]:].index[1]
                    target_value = df.loc[next_dt,'benchmark']
                    df.loc[index_list, 'benchmark']  = df.loc[index_list, 'benchmark']  * target_value / df.loc[index_list[-1], 'benchmark']
                df = df / df.bfill().iloc[0] - 1
                df = df - trade_fee
                df = df.reset_index()
                query = db_session.query(
                    OSIndexInfo
                ).filter(
                    OSIndexInfo.index_id == index_id,
                )
                _df = pd.read_sql(query.statement, query.session.bind)
                if _df.empty:
                    print(f'get data from {OSFundNav.__tablename__} fund_id: {fund_id} fund benchmark name not exsited index_id: {index_id}')
                    result['benchmark_name'] = None
                    result['benchmark_id'] = index_id
                    result['fund_id'] = fund_id
                    result['data'] = df
                    result['annual_ret'] = annual_ret
                    return result
                benchmark_name = _df.index_name.values[0]
                result['fund_id'] = fund_id
                result['data'] = df
                result['annual_ret'] = annual_ret
                result['benchmark_name'] = benchmark_name
                result['benchmark_id'] = index_id
                return result

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundNav.__tablename__} fund_id: {fund_id}')
                return None


    def get_oversea_fund_nav_one_page(self, fund_id: str, page:int=1, page_size:int=10):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                _query = db_session.query(OSFundNav).filter(
                    OSFundNav.codes == fund_id,
                    ).order_by(
                        OSFundNav.datetime.desc()
                        )
                count =  _query.count()
                query = _query.limit(page_size).offset((page - 1) * page_size)
                df = pd.read_sql(query.statement, query.session.bind)
                result = {
                            'data':df,
                            'page':page,
                            'page_size':page_size,
                            'count':count,
                         }

                return result
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundNav.__tablename__}')
                result = {
                            'data':None,
                            'page':page,
                            'page_size':page_size,
                            'count':None,
                         }
                return result

    def get_oversea_fund_ret_daily(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        OSFundRet
                    )
                else:
                    query = db_session.query(
                        OSFundRet.codes,
                        OSFundRet.datetime,
                    ).add_columns(*columns)
                if fund_ids:
                    query = query.filter(
                        OSFundRet.codes.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        OSFundRet.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        OSFundRet.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundRet.__tablename__}')
                return None


    def get_oversea_fund_period_ret(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:

                query = db_session.query(QSOverseaFundPeriodRet)
                if fund_ids:
                    query = query.filter(
                        QSOverseaFundPeriodRet.codes.in_(fund_ids),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {QSOverseaFundPeriodRet.__tablename__}')
                return None

    def get_oversea_fund_cur_mdd(self, start_date: str = '', fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                df = self.get_oversea_fund_nav(start_date=start_date,fund_ids=fund_ids)
                df['nav'] = (df.nav/ df.nav.cummax()) - 1
                df = df.rename(columns={'nav':'current_mdd'})
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {QSOverseaFundCurMdd.__tablename__}')
                return None

    def get_qs_fund_style_box(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:

                query = db_session.query(QSFundStyleBox)
                if fund_ids:
                    query = query.filter(
                        QSFundStyleBox.codes.in_(fund_ids),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {QSFundStyleBox.__tablename__}')
                return None

    def get_qs_fund_radar(self, fund_ids: Tuple[str] = (), dt=None):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not dt:
                    dt = db_session.query(
                        func.max(QSOverseaFundRadarScore.datetime)
                    ).one_or_none()
                    if dt:
                        dt = dt[0]

                query = db_session.query(QSOverseaFundRadarScore)

                if fund_ids:
                    query = query.filter(
                        QSOverseaFundRadarScore.codes.in_(fund_ids),
                        QSOverseaFundRadarScore.datetime == dt
                    )
                else:
                    query = query.filter(
                        QSOverseaFundRadarScore.datetime == dt
                    )
                return pd.read_sql(query.statement, query.session.bind).drop(columns='fund_type', errors='ignore')
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {QSOverseaFundRadarScore.__tablename__}')
                return None

    def get_os_fund_bond_hold_rate(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(OSFundBondHoldRate.report_date)).filter(
                            OSFundBondHoldRate.codes.in_(fund_ids),
                ).one_or_none()
                dt = dt[0]
                query = db_session.query(OSFundBondHoldRate)
                if fund_ids:
                    query = query.filter(
                        OSFundBondHoldRate.codes.in_(fund_ids),
                        OSFundBondHoldRate.report_date == dt,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundBondHoldRate.__tablename__}')
                return None

    def get_os_fund_hold_industry(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(OSFundHoldIndustry.report_date)).filter(
                        OSFundHoldIndustry.codes.in_(fund_ids),
                ).one_or_none()
                dt = dt[0]
                query = db_session.query(OSFundHoldIndustry)
                if fund_ids:
                    query = query.filter(
                        OSFundHoldIndustry.codes.in_(fund_ids),
                        OSFundHoldIndustry.report_date == dt,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundHoldIndustry.__tablename__}')
                return None

    def get_os_fund_recent_ret(self, fund_id: str):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(QSFundRecentRet.datetime)).filter(
                        QSFundRecentRet.codes == fund_id,
                ).scalar()
                query = db_session.query(QSFundRecentRet).filter(
                    QSFundRecentRet.codes == fund_id,
                    QSFundRecentRet.datetime == dt,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {QSFundRecentRet.__tablename__}')
                return None

    def get_os_fund_hold_district(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(OSFundHoldDistrict.report_date)).filter(
                        OSFundHoldDistrict.codes.in_(fund_ids),
                ).one_or_none()
                dt = dt[0]
                query = db_session.query(OSFundHoldDistrict)
                if fund_ids:
                    query = query.filter(
                        OSFundHoldDistrict.codes.in_(fund_ids),
                        OSFundHoldDistrict.report_date == dt,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundHoldDistrict.__tablename__}')
                return None

    def get_os_fund_hold_bond_term(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(OSFundHoldBondTerm.report_date)).filter(
                        OSFundHoldBondTerm.codes.in_(fund_ids),
                ).one_or_none()
                dt = dt[0]
                query = db_session.query(OSFundHoldBondTerm)
                if fund_ids:
                    query = query.filter(
                        OSFundHoldBondTerm.codes.in_(fund_ids),
                        OSFundHoldBondTerm.report_date == dt,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundHoldBondTerm.__tablename__}')
                return None

    def get_oversea_index_price(self, start_date: str = '', end_date: str = '', index_id: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        OSIndexPrice
                    )
                else:
                    query = db_session.query(
                        OSIndexPrice.codes,
                        OSIndexPrice.datetime,
                    ).add_columns(*columns)
                if index_id:
                    query = query.filter(
                        OSIndexPrice.codes.in_(index_id),
                    )
                if start_date:
                    query = query.filter(
                        OSIndexPrice.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        OSIndexPrice.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSIndexPrice.__tablename__}')
                return None

    def get_os_fund_nav_div_factor(self, start_date: str = '', end_date: str = '', fund_id: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSFundNAVDivFactor
                )
                if start_date:
                    query = query.filter(
                        OSFundNAVDivFactor.ex_date >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        OSFundNAVDivFactor.ex_date <= end_date,
                    )
                if fund_id:
                    query = query.filter(
                        OSFundNAVDivFactor.product_id.in_(fund_id)
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundNAVDivFactor.__tablename__}')
                return

    def get_over_sea_fund_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSFundInfo
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_over_sea_fund_info_with_fund_id(self, fund_id:str):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSFundInfo
                ).filter(
                    OSFundInfo.codes == fund_id,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                if df.empty:
                    return df
                dt = db_session.query(
                    func.max(QSFundRecentRet.datetime)).filter(
                        QSFundRecentRet.codes == fund_id,
                ).scalar()
                df.loc[:,'latest_nav_date'] = dt
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_over_sea_fund_benchmark(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSFundBenchmark
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_over_sea_fund_benchmarks(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSFundBenchmarks
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_benchmark_nav(self, fund_id):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSFundBenchmarks.codes,
                    OSFundBenchmarks.benchmark_final,
                ).filter(
                    OSFundBenchmarks.codes == fund_id,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                index_id = df.benchmark_final.tolist()
                index_price = self.get_oversea_index_price(index_id=index_id).drop(columns=['_update_time'])
                return index_price
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_over_sea_em_stock_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmOverseaStockInfoUS
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_over_sea_em_hk_stock_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmOverseaStockInfoHK
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None


    def get_over_sea_em_index_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmOverseaIndexInfo
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_hold_top10_pos(self, fund_id:str=None):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(OSFundHoldTop10Pos.report_date)).filter(
                            OSFundHoldTop10Pos.codes == fund_id, 
                ).one_or_none()
                if dt:
                    dt = dt[0] 
                query = db_session.query(
                    OSFundHoldTop10Pos
                )
                if fund_id:
                    query = query.filter(
                        OSFundHoldTop10Pos.codes == fund_id,
                        OSFundHoldTop10Pos.report_date == dt,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_hold_top10_pos_with_desc_name(self, fund_id:str=None):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(OSFundHoldTop10Pos.report_date)).filter(
                            OSFundHoldTop10Pos.codes == fund_id, 
                ).one_or_none()
                if dt:
                    dt = dt[0] 
                query = db_session.query(
                    OSFundHoldTop10Pos
                )
                if fund_id:
                    query = query.filter(
                        OSFundHoldTop10Pos.codes == fund_id,
                        OSFundHoldTop10Pos.report_date == dt,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                asset_dic = {}
                pos_list = [f'pos_{i}' for i in range(1,11)]
                for i in pos_list:
                    asset_list = df[i].values.tolist()
                    for j in asset_list:
                        if j is None:
                            continue
                        _asset = j.split(' ')[-1]
                        if _asset not in asset_dic:
                            asset_dic[_asset] = [j]
                        else:
                            asset_dic[_asset].append(j)
                fund_dic = {
                    'Equity':self.get_fund_hold_equity_info,
                    'Govt':self.get_fund_hold_govt_info,
                    'Corp':self.get_fund_hold_corp_info,
                    'Comdty':self.get_fund_hold_comdty_info,
                    'Mtge':self.get_fund_hold_mtge_info,
                    'Index':self.get_fund_hold_index_info,
                    'Pfd':self.get_fund_hold_pfd_info,
                    'Muni':self.get_fund_hold_muni_info,
                }
                dic_name = {}
                for asset, asset_list in asset_dic.items():
                    if asset not in fund_dic:
                        continue
                    _func = fund_dic[asset]
                    _df = _func(asset_list)
                    _dic_name = _df.set_index('codes').to_dict()['asset_name']
                    dic_name.update(_dic_name)
                df = df.replace(dic_name)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_hold_equity_info(self, asset_ids:Tuple[str] = ()):
        def _parse(x): return dic[x] if x in dic else ''

        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSStockInfo.codes,
                    OSStockInfo.stock_name_c,
                )
                if asset_ids:
                    query = query.filter(
                        OSStockInfo.codes.in_(asset_ids),
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns={'stock_name_c':'asset_name'})
                dic = {'CH':'A股','HK':'港股','US':'美股'}
                codes = df.codes.tolist()
                c_name = df.asset_name.tolist()
                df.asset_name = [j+' '+_parse(i.split(' ')[1]) for i,j in zip(codes,c_name)]
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_hold_corp_info(self, asset_ids:Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSCorpBondInfo.codes,
                    OSCorpBondInfo.company_name_c,
                )
                if asset_ids:
                    query = query.filter(
                        OSCorpBondInfo.codes.in_(asset_ids),
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns={'company_name_c':'asset_name'})
                df.asset_name = df.asset_name.map(lambda x: x +'債券' if '債' not in x else x)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_hold_govt_info(self, asset_ids:Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSGovtBondInfo.codes,
                    OSGovtBondInfo.bond_name_c,
                )
                if asset_ids:
                    query = query.filter(
                        OSGovtBondInfo.codes.in_(asset_ids),
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns={'bond_name_c':'asset_name'})
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_hold_mtge_info(self, asset_ids:Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSMtgeBondInfo.codes,
                    OSMtgeBondInfo.bond_name_e
                )
                if asset_ids:
                    query = query.filter(
                        OSMtgeBondInfo.codes.in_(asset_ids),
                    )
                df = pd.read_sql(query.statement, query.session.bind).rename(columns={'bond_name_e':'asset_name'})
                df.asset_name = [i + ' 抵押债' for i in df.asset_name]
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_hold_muni_info(self, asset_ids:Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSMuniInfo.codes,
                    OSMuniInfo.asset_name_e
                )
                if asset_ids:
                    query = query.filter(
                        OSMuniInfo.codes.in_(asset_ids),
                    )
                df = pd.read_sql(query.statement, query.session.bind).rename(columns={'asset_name_e':'asset_name'})
                df.asset_name = [i + ' 美国市政债' for i in df.asset_name]
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_hold_pfd_info(self, asset_ids:Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSPfdInfo.codes,
                    OSPfdInfo.asset_name_e
                )
                if asset_ids:
                    query = query.filter(
                        OSPfdInfo.codes.in_(asset_ids),
                    )
                df = pd.read_sql(query.statement, query.session.bind).rename(columns={'asset_name_e':'asset_name'})
                df.asset_name = [i + ' 优先股' for i in df.asset_name]
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_hold_comdty_info(self, asset_ids:Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSComdtyInfo.codes,
                    OSComdtyInfo.asset_name_e
                )
                if asset_ids:
                    query = query.filter(
                        OSComdtyInfo.codes.in_(asset_ids),
                    )
                df = pd.read_sql(query.statement, query.session.bind).rename(columns={'asset_name_e':'asset_name'})
                df.asset_name = [i + ' 商品期货' for i in df.asset_name]
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_fund_hold_index_info(self, asset_ids:Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    OSIndexFutureInfo.codes,
                    OSIndexFutureInfo.asset_name_c
                )
                if asset_ids:
                    query = query.filter(
                        OSIndexFutureInfo.codes.in_(asset_ids),
                    )
                df = pd.read_sql(query.statement, query.session.bind).rename(columns={'asset_name_c':'asset_name'})
                df.asset_name = [i + ' 股指期货' for i in df.asset_name]
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def delete_em_fund_nav(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmFundNav
                ).filter(
                    EmFundNav.DATES >= start_date,
                    EmFundNav.DATES <= end_date
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmFundNav.__tablename__}')
                return None

    def delete_em_stock_future_diff(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockFutureDiff
                ).filter(
                    EmStockFutureDiff.DATES >= start_date,
                    EmStockFutureDiff.DATES <= end_date
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmStockFutureDiff.__tablename__}')
                return None

    def delete_em_us_stock_price(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmOverseaEmStockPriceUS
                ).filter(
                    EmOverseaEmStockPriceUS.DATES >= start_date,
                    EmOverseaEmStockPriceUS.DATES <= end_date
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmOverseaEmStockPriceUS.__tablename__}')
                return None

    def delete_em_index_val(self, index_id_list, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmIndexVal
                ).filter(
                    EmIndexVal.CODES.in_(index_id_list),
                    EmIndexVal.DATES >= start_date,
                    EmIndexVal.DATES <= end_date
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmIndexVal.__tablename__}')
                return None


    def get_rq_fund_size(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    RqFundSize
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_rq_stock_price(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    RqStockPrice
                ).filter(
                    RqStockPrice.datetime >= start_date,
                    RqStockPrice.datetime <= end_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_rq_stock_post_price(self, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    RqStockPostPrice
                ).filter(
                    RqStockPostPrice.datetime >= start_date,
                    RqStockPostPrice.datetime <= end_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_rq_stock_minute(self, dt=None):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not dt:
                    dt = db_session.query(
                        func.max(RqStockMinute.datetime)
                    ).one_or_none()
                if dt:
                    dt = dt[0]
                query = db_session.query(
                    RqStockMinute
                ).filter(
                    RqStockMinute.datetime == dt
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def get_em_index_price(self, start_date, end_date, index_id_list: Tuple = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmIndexPrice
                )
                if index_id_list:
                    query = query.filter(
                        EmIndexPrice.em_id.in_(index_id_list),
                    )
                query = query.filter(
                    EmIndexPrice.datetime >= start_date,
                    EmIndexPrice.datetime <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmIndexPrice.__tablename__}')
                return None

    def delete_em_index_price(self, index_id_list, start_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EmIndexPrice
                ).filter(
                    EmIndexPrice.em_id.in_(index_id_list),
                    EmIndexPrice.datetime >= start_date,
                    EmIndexPrice.datetime <= end_date,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmIndexPrice.__tablename__}')
                return None

    def get_em_index_val(self, start_date, end_date, index_id_list: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmIndexVal
                )
                if index_id_list:
                    query = query.filter(
                        EmIndexVal.CODES.in_(index_id_list),
                    )
                query = query.filter(
                    EmIndexVal.DATES >= start_date,
                    EmIndexVal.DATES <= end_date,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmIndexVal.__tablename__}')
                return None

    def get_em_fund_scale(self, start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmFundScale,
                )
                if start_date:
                    query = query.filter(
                        EmFundScale.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmFundScale.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get scale data <err_msg> {e} from {EmFundScale.__tablename__}')
                return

    def delete_em_fund_scale(self, date_to_delete: datetime.date, fund_list: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EmFundScale
                ).filter(
                    EmFundScale.CODES.in_(fund_list),
                    EmFundScale.DATES == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmFundScale.__tablename__}')
                return False

    def get_em_fund_status(self, end_date: str = ''):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmFundStatus
                )
                if end_date:
                    query = query.filter(
                        EmFundStatus.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFundStatus.__tablename__}')
                return None

    def get_em_stock_price(self, start_date: str = '', end_date: str = '', stock_list: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if columns:
                    query = db_session.query(
                        EmStockPrice.CODES,
                        EmStockPrice.DATES,
                    ).add_columns(*columns)
                else:
                    query = db_session.query(
                        EmStockPrice
                    )
                if start_date:
                    query = query.filter(
                        EmStockPrice.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmStockPrice.DATES <= end_date,
                    )
                if stock_list:
                    query = query.filter(
                        EmStockPrice.CODES.in_(stock_list)
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockPrice.__tablename__}')
                return None

    def get_em_us_stock_price(self, start_date: str = '', end_date: str = '', stock_list: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmOverseaEmStockPriceUS,
                )
                if start_date:
                    query = query.filter(
                        EmOverseaEmStockPriceUS.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmOverseaEmStockPriceUS.DATES <= end_date,
                    )
                if stock_list:
                    query = query.filter(
                        EmOverseaEmStockPriceUS.CODES.in_(stock_list)
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmOverseaEmStockPriceUS.__tablename__}')
                return None

    def get_em_hk_stock_price(self, start_date: str = '', end_date: str = '', stock_list: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmOverseaEmStockPriceHK,
                )
                if start_date:
                    query = query.filter(
                        EmOverseaEmStockPriceHK.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmOverseaEmStockPriceHK.DATES <= end_date,
                    )
                if stock_list:
                    query = query.filter(
                        EmOverseaEmStockPriceHK.CODES.in_(stock_list)
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmOverseaEmStockPriceHK.__tablename__}')
                return None

    def get_em_stock_post_price(self, start_date: str = '', end_date: str = '', stock_list: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if columns:
                    query = db_session.query(
                        EmStockPostPrice.CODES,
                        EmStockPostPrice.DATES,
                    ).add_columns(*columns)
                else:
                    query = db_session.query(
                        EmStockPostPrice,
                    )
                if stock_list:
                    query = query.filter(
                        EmStockPostPrice.CODES.in_(stock_list)
                    )
                if start_date:
                    query = query.filter(
                        EmStockPostPrice.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmStockPostPrice.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockPostPrice.__tablename__}')
                return None

    def get_em_stock_info(self, stock_list: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockInfo
                )
                if stock_list:
                    query = query.filter(
                        EmStockInfo.CODES.in_(stock_list)
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockInfo.__tablename__}')
                return None

    def get_em_stock_info_by_key_words(self, key_words:Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockInfo
                )
                for key_word in key_words:
                    query = query.filter(
                        EmStockInfo.NAME.like(f'%{key_word}%')
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockInfo.__tablename__}')
                return None

    def del_em_stock_info(self, stock_list: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EmStockInfo
                ).filter(
                    EmStockInfo.CODES.in_(stock_list),
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmStockInfo.__tablename__}')
                return False

    def get_em_daily_info(self, start_date: str = '', end_date: str = '', stock_list: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if columns:
                    query = db_session.query(
                        EmStockDailyInfo.CODES,
                        EmStockDailyInfo.DATES,
                    ).add_columns(*columns)
                else:
                    query = db_session.query(
                        EmStockDailyInfo
                    )
                if stock_list:
                    query = query.filter(
                        EmStockDailyInfo.CODES.in_(stock_list)
                    )
                if start_date:
                    query = query.filter(
                        EmStockDailyInfo.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmStockDailyInfo.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockDailyInfo.__tablename__}')
                return None

    def get_em_daily_info_last_date(self, stock_list: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if columns:
                    query = db_session.query(
                        EmStockDailyInfo.CODES,
                        EmStockDailyInfo.DATES,
                    ).add_columns(*columns)
                else:
                    query = db_session.query(
                        EmStockDailyInfo
                    )
                if stock_list:
                    query = query.filter(
                        EmStockDailyInfo.CODES.in_(stock_list)
                    )
                    dt = db_session.query(
                        func.max(EmStockDailyInfo.DATES)
                    ).one_or_none()[0]
                    query = query.filter(
                        EmStockDailyInfo.DATES == dt,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockDailyInfo.__tablename__}')
                return None

    def get_em_stock_fin_fac(self, *, stock_list: Tuple[str] = (), date_list: Tuple[str] = (), start_date: str = '', end_date: str = '', columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        EmStockFinFac
                    )
                else:
                    query = db_session.query(
                        EmStockFinFac.CODES,
                        EmStockFinFac.DATES,
                    ).add_columns(*columns)
                if stock_list:
                    query = query.filter(
                        EmStockFinFac.CODES.in_(stock_list)
                    )
                if date_list:
                    query = query.filter(
                        EmStockFinFac.DATES.in_(date_list)
                    )
                else:
                    if start_date:
                        query = query.filter(
                            EmStockFinFac.DATES >= start_date,
                        )
                    if end_date:
                        query = query.filter(
                            EmStockFinFac.DATES <= end_date,
                        )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockFinFac.__tablename__}')
                return None

    def delete_em_stock_fin_fac(self, date_to_delete: datetime.date, fund_list: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EmStockFinFac
                ).filter(
                    EmStockFinFac.CODES.in_(fund_list),
                    EmStockFinFac.DATES == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmStockFinFac.__tablename__}')
                return False

    def get_em_stock_estimate_fac(self, predict_year: int, start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockEstimateFac
                )
                if start_date:
                    query = query.filter(
                        EmStockEstimateFac.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmStockEstimateFac.DATES <= end_date,
                    )
                query = query.filter(
                    EmStockEstimateFac.predict_year == predict_year,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockEstimateFac.__tablename__}')
                return None

    def get_em_index_info(self, index_list: Union[Tuple[str], List[str]] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmIndexInfo
                )
                if index_list:
                    query = query.filter(
                        EmIndexInfo.CODES.in_(index_list)
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmIndexInfo.__tablename__}')
                return None

    def get_em_index_component(self, start_date: str = '', end_date: str = '', index_list: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmIndexComponent
                )
                if index_list:
                    query = query.filter(
                        EmIndexComponent.index_id.in_(index_list)
                    )
                if start_date:
                    query = query.filter(
                        EmIndexComponent.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmIndexComponent.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmIndexComponent.__tablename__}')
                return None

    def get_cs_index_component(self, index_list: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    CSIndexComponent
                )
                if index_list:
                    query = query.filter(
                        CSIndexComponent.index_id.in_(index_list)
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {CSIndexComponent.__tablename__}')
                return None

    def get_em_fund_holding_rate(self, start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmFundHoldingRate
                )
                if start_date:
                    query = query.filter(
                        EmFundHoldingRate.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmFundHoldingRate.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def delete_em_fund_hold_rate(self, date_to_delete: datetime.date, fund_list: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EmFundHoldingRate
                ).filter(
                    EmFundHoldingRate.CODES.in_(fund_list),
                    EmFundHoldingRate.DATES == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmFundHoldingRate.__tablename__}')
                return False

    def get_em_fund_list(self, date: str, limit = -1):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmFundList.datetime,
                    EmFundList.all_live_fund_list,
                    EmFundList.delisted_fund_list,
                ).filter(
                    EmFundList.datetime <= date,
                )
                if limit != -1:
                    query = query.order_by(EmFundList.datetime.desc()).limit(limit)
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFundList.__tablename__}')
                return None

    def delete_em_fund_info(self, funds: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            query = db_session.query(
                EmFundInfo
            ).filter(
                EmFundInfo.CODES.in_(funds),
            ).delete(synchronize_session=False)
            db_session.commit()

    def get_em_fund_info(self, funds: List[str] = []):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmFundInfo
                )
                if funds:
                    query = query.filter(
                        EmFundInfo.CODES.in_(funds),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFundInfo.__tablename__}')
                return None

    def delete_em_fund_fee(self, funds: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            query = db_session.query(
                EmFundFee
            ).filter(
                EmFundFee.CODES.in_(funds),
            ).delete(synchronize_session=False)
            db_session.commit()

    def get_em_fund_fee(self, funds: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmFundFee
                ).filter(
                    EmFundFee.CODES.in_(funds),
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFundFee.__tablename__}')
                return None

    def get_em_fund_benchmark(self, end_date: str = ''):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmFundBenchmark
                )
                if end_date:
                    query = query.filter(
                        EmFundBenchmark.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFundBenchmark.__tablename__}')
                return None

    def get_wind_holder_structure(self, start_date: str, wind_fund_list:list):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    WindFundHolderStructure
                ).filter(
                    WindFundHolderStructure.END_DT >= start_date,
                    WindFundHolderStructure.S_INFO_WINDCODE.in_(wind_fund_list),
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {WindFundHolderStructure.__tablename__}')
                return None

    def get_wind_fund_stock_portfolio(self, start_date: str, end_date: str, wind_fund_list: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    WindFundStockPortfolio
                ).filter(
                    WindFundStockPortfolio.F_PRT_ENDDATE >= start_date,
                    WindFundStockPortfolio.F_PRT_ENDDATE <= end_date,
                    WindFundStockPortfolio.S_INFO_WINDCODE.in_(wind_fund_list),
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {WindFundStockPortfolio.__tablename__}')
                return None

    def get_wind_fund_bond_portfolio(self, start_date: str, end_date: str, wind_fund_list: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    WindFundBondPortfolio
                ).filter(
                    WindFundBondPortfolio.F_PRT_ENDDATE >= start_date,
                    WindFundBondPortfolio.F_PRT_ENDDATE <= end_date,
                )
                if wind_fund_list:
                    query = query.filter(
                        WindFundBondPortfolio.S_INFO_WINDCODE.in_(wind_fund_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {WindFundBondPortfolio.__tablename__}')

    def get_wind_fund_nav(self, start_date: str, wind_fund_list:list):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    WindFundNav
                ).filter(
                    WindFundNav.PRICE_DATE >= start_date,
                    WindFundNav.F_INFO_WINDCODE.in_(wind_fund_list),
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {WindFundNav.__tablename__}')
                return None

    def get_wind_manager_info(self, wind_fund_list: List[str] = '', columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        WindFundManager
                    )
                else:
                    query = db_session.query(
                        WindFundManager.F_INFO_FUNDMANAGER_ID,
                        WindFundManager.F_INFO_WINDCODE,
                    ).add_columns(*columns)
                if wind_fund_list:
                    query = query.filter(
                        WindFundManager.F_INFO_WINDCODE.in_(wind_fund_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {WindFundManager.__tablename__}')
                return None

    def get_wind_indus_portfolio(self, start_date: str, wind_fund_list:list):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    WindIndPortfolio
                ).filter(
                    WindIndPortfolio.F_PRT_ENDDATE >= start_date,
                    WindIndPortfolio.S_INFO_WINDCODE.in_(wind_fund_list),
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {WindIndPortfolio.__tablename__}')
                return None

    def get_em_fund_rate(self, datetime: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(
                    EMFundRate
                )
                if datetime:
                    query = query.filter(
                        EMFundRate.DATES == datetime,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EMFundRate.__tablename__}')
                return None

    def get_em_fund_hold_asset(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EMFundHoldAsset)
                if fund_ids:
                    query = query.filter(
                        EMFundHoldAsset.CODES.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        EMFundHoldAsset.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EMFundHoldAsset.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EMFundHoldAsset.__tablename__}')
                return None

    def delete_em_fund_hold_asset(self, date_to_delete: datetime.date, fund_list: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EMFundHoldAsset
                ).filter(
                    EMFundHoldAsset.CODES.in_(fund_list),
                    EMFundHoldAsset.DATES == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EMFundHoldAsset.__tablename__}')
                return False

    def get_em_fund_hold_industry(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EMFundHoldIndustry)
                if fund_ids:
                    query = query.filter(
                        EMFundHoldIndustry.CODES.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        EMFundHoldIndustry.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EMFundHoldIndustry.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EMFundHoldIndustry.__tablename__}')
                return None

    def delete_em_fund_hold_industry(self, date_to_delete: datetime.date, fund_list: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EMFundHoldIndustry
                ).filter(
                    EMFundHoldIndustry.CODES.in_(fund_list),
                    EMFundHoldIndustry.DATES == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EMFundHoldIndustry.__tablename__}')
                return False

    def delete_em_fund_hold_industry_qdii(self, date_to_delete: datetime.date, fund_list: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EMFundHoldIndustryQDII
                ).filter(
                    EMFundHoldIndustryQDII.CODES.in_(fund_list),
                    EMFundHoldIndustryQDII.DATES == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EMFundHoldIndustryQDII.__tablename__}')
                return False

    def get_em_fund_hold_stock(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EMFundHoldStock)
                if fund_ids:
                    query = query.filter(
                        EMFundHoldStock.CODES.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        EMFundHoldStock.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EMFundHoldStock.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EMFundHoldStock.__tablename__}')
                return None

    def get_em_fund_hold_industry_qdii(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EMFundHoldIndustryQDII)
                if fund_ids:
                    query = query.filter(
                        EMFundHoldIndustryQDII.CODES.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        EMFundHoldIndustryQDII.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EMFundHoldIndustryQDII.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EMFundHoldIndustryQDII.__tablename__}')
                return None

    def get_em_fund_hold_stock_qdii(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EMFundHoldStockQDII)
                if fund_ids:
                    query = query.filter(
                        EMFundHoldStockQDII.CODES.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        EMFundHoldStockQDII.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EMFundHoldStockQDII.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EMFundHoldStockQDII.__tablename__}')
                return None

    def delete_em_fund_hold_stock(self, date_to_delete: datetime.date, fund_list: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EMFundHoldStock
                ).filter(
                    EMFundHoldStock.CODES.in_(fund_list),
                    EMFundHoldStock.DATES == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EMFundHoldStock.__tablename__}')
                return False

    def delete_em_fund_hold_stock_qdii(self, date_to_delete: datetime.date, fund_list: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EMFundHoldStockQDII
                ).filter(
                    EMFundHoldStockQDII.CODES.in_(fund_list),
                    EMFundHoldStockQDII.DATES == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EMFundHoldStockQDII.__tablename__}')
                return False

    def get_em_fund_hold_bond(self, start_date: str = '', end_date: str = '', fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EMFundHoldBond)
                if fund_ids:
                    query = query.filter(
                        EMFundHoldBond.CODES.in_(fund_ids),
                    )
                if start_date:
                    query = query.filter(
                        EMFundHoldBond.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EMFundHoldBond.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def delete_em_fund_hold_bond(self, date_to_delete: datetime.date, fund_list: List[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EMFundHoldBond
                ).filter(
                    EMFundHoldBond.CODES.in_(fund_list),
                    EMFundHoldBond.DATES == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EMFundHoldBond.__tablename__}')
                return False

    def get_em_mng_info(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EMMngInfo
                )
                if fund_ids:
                    query = query.filter(
                        EMMngInfo.code.in_(fund_ids),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_em_fund_mng_change(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EMFundMngChange
                )
                if fund_ids:
                    query = query.filter(
                        EMFundMngChange.code.in_(fund_ids),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_fund_com_mng_change(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EMFundCompMngChange
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_em_fund_com_core_mng(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EMFundCompCoreMng
                )
                if fund_ids:
                    query = query.filter(
                        EMFundCompCoreMng.code.in_(fund_ids),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))

    def get_em_stock_dividend(self, end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmStockDividend)
                if end_date:
                    query = query.filter(
                        EmStockDividend.DATES <= end_date
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockDividend.__tablename__}')

    def get_em_stock_dividend_by_id(self, stock_id: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmStockDividend)
                if stock_id:
                    query = query.filter(
                        EmStockDividend.CODES == stock_id,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_em_stock_dividend_by_id <err_msg> {e} from {EmStockDividend.__tablename__}')
                return pd.DataFrame([])

    def get_em_bond_info(self, bond_id_list: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmBondInfo)
                if bond_id_list:
                    query = query.filter(
                        EmBondInfo.CODES.in_(bond_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmBondInfo.__tablename__}')

    def get_em_bond_rating(self, end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmBondRating)
                if end_date:
                    query = query.filter(
                        EmBondRating.DATES <= end_date
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmBondRating.__tablename__}')

    def get_em_macroeconomic_monthly(self, codes: Tuple[str] = (), start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmMacroEconomicMonthly)
                if codes:
                    query = query.filter(
                        EmMacroEconomicMonthly.codes.in_(codes),
                    )
                if start_date:
                    query = query.filter(
                        EmMacroEconomicMonthly.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmMacroEconomicMonthly.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmMacroEconomicMonthly.__tablename__}')

    def delete_em_macroeconomic_monthly(self, the_date, codes: Tuple[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EmMacroEconomicMonthly
                ).filter(
                    EmMacroEconomicMonthly.datetime == the_date,
                    EmMacroEconomicMonthly.codes.in_(codes),
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmMacroEconomicMonthly.__tablename__}')

    def get_em_macroeconomic_daily(self, codes: Tuple[str] = (), start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmMacroEconomicDaily)
                if codes:
                    query = query.filter(
                        EmMacroEconomicDaily.codes.in_(codes),
                    )
                if start_date:
                    query = query.filter(
                        EmMacroEconomicDaily.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmMacroEconomicDaily.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmMacroEconomicDaily.__tablename__}')

    def delete_em_macroeconomic_daily(self, code: str, datetime_list):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    EmMacroEconomicDaily
                ).filter(
                    EmMacroEconomicDaily.codes == code,
                    EmMacroEconomicDaily.datetime.in_(datetime_list),
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmMacroEconomicDaily.__tablename__}')

    def get_em_macroeconomic_info(self, codes: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmMacroEconomicInfo)
                if codes:
                    query = query.filter(
                        EmMacroEconomicInfo.codes.in_(codes),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmMacroEconomicInfo.__tablename__}')

    def get_em_fund_open(self):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmFundOpen)
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFundOpen.__tablename__}')

    def get_em_fund_ipo_status(self):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmFundIPOStats)
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFundIPOStats.__tablename__}')

    def get_em_fund_stock_portfolio(self, start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmFundStockPortfolio)
                if start_date:
                    query = query.filter(
                        EmFundStockPortfolio.report_date >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmFundStockPortfolio.report_date <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFundStockPortfolio.__tablename__}')

    def get_em_stock_industrial_capital(self):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmStockIndustrialCapital)
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockIndustrialCapital.__tablename__}')

    def delete_em_stock_industrial_capital(self, the_date, period: str):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockIndustrialCapital
                ).filter(
                    EmStockIndustrialCapital.datetime == the_date,
                    EmStockIndustrialCapital.period == period,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmStockIndustrialCapital.__tablename__}')

    def get_em_stock_industrial_capital_trade_detail(self, start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmStockIndustrialCapitalTradeDetail)
                if start_date:
                    query = query.filter(
                        EmStockIndustrialCapitalTradeDetail.notice_date >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmStockIndustrialCapitalTradeDetail.notice_date <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockIndustrialCapitalTradeDetail.__tablename__}')

    def get_em_stock_shsz_to_hk_connect(self, start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmSHSZToHKStockConnect)
                if start_date:
                    query = query.filter(
                        EmSHSZToHKStockConnect.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmSHSZToHKStockConnect.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmSHSZToHKStockConnect.__tablename__}')

    def get_em_stock_research_info(self, start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmStockResearchInfo)
                if start_date:
                    query = query.filter(
                        EmStockResearchInfo.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmStockResearchInfo.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockResearchInfo.__tablename__}')

    def get_em_stock_refinancing(self, start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmStockRefinancing)
                if start_date:
                    query = query.filter(
                        EmStockRefinancing.APPROVENOTICEDATE >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmStockRefinancing.APPROVENOTICEDATE <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockRefinancing.__tablename__}')

    def get_em_stock_refinancing_by_plan_noticed_date(self, start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmStockRefinancing)
                if start_date:
                    query = query.filter(
                        EmStockRefinancing.PLANNOTICEDDATE >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmStockRefinancing.PLANNOTICEDDATE <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockRefinancing.__tablename__}')

    def get_em_stock_refinancing_impl(self, start_date: str = '', end_date: str = ''):
        with RawDatabaseConnector().managed_session() as raw_session:
            try:
                query = raw_session.query(EmStockRefinancingImpl)
                if start_date:
                    query = query.filter(
                        EmStockRefinancingImpl.DATE >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmStockRefinancingImpl.DATE <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockRefinancingImpl.__tablename__}')

    def get_em_stock_yearly(self, columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        EmStockYearly
                    )
                else:
                    query = db_session.query(
                        EmStockYearly.CODES,
                        EmStockYearly.year,
                    ).add_columns(*columns)
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockYearly.__tablename__}')

    def get_em_industry_info(self, ind_class_type: Integer = None):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmIndustryInfo,
                )
                if ind_class_type:
                    query = query.filter(
                        EmIndustryInfo.ind_class_type == ind_class_type,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_em_industry_info <err_msg> {e} from {EmIndustryInfo.__tablename__}')
                return pd.DataFrame([])

    def get_em_stock_balance(self, stock_id=None, columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if columns:
                    query = db_session.query(
                        EmStockFSBalanceSheet.CODES,
                        EmStockFSBalanceSheet.DATES,
                    ).add_columns(*columns)
                else:
                    query = db_session.query(
                        EmStockFSBalanceSheet,
                    )
                if stock_id:
                    query = query.filter(
                        EmStockFSBalanceSheet.CODES == stock_id,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_em_stock_balance <err_msg> {e} from {EmStockFSBalanceSheet.__tablename__}')
                return pd.DataFrame([])

    def get_em_stock_income(self, stock_id=None, columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockFSIncomeStatement,
                )
                if stock_id:
                    query = query.filter(
                        EmStockFSIncomeStatement.CODES == stock_id,
                    )
                if columns:
                    query = query.add_columns(*columns)
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_em_stock_income <err_msg> {e} from {EmStockFSIncomeStatement.__tablename__}')
                return pd.DataFrame([])

    def get_em_stock_income_quarterly(self, stock_id=None, columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockFSIncomeStatementQ,
                )
                if stock_id:
                    query = query.filter(
                        EmStockFSIncomeStatementQ.CODES == stock_id,
                    )
                if columns:
                    query = query.add_columns(*columns)
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_em_stock_income_quarterly <err_msg> {e} from {EmStockFSIncomeStatementQ.__tablename__}')
                return pd.DataFrame([])

    def get_em_stock_cash_flow(self, stock_id=None, columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockFSCashflowStatement,
                )
                if stock_id:
                    query = query.filter(
                        EmStockFSCashflowStatement.CODES == stock_id,
                    )
                if columns:
                    query = query.add_columns(*columns)
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_em_stock_cash_flow <err_msg> {e} from {EmStockFSCashflowStatement.__tablename__}')
                return pd.DataFrame([])

    def get_em_stock_cash_flow_quarterly(self, stock_id=None, columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmStockFSCashflowStatementQ,
                )
                if stock_id:
                    query = query.filter(
                        EmStockFSCashflowStatementQ.CODES == stock_id,
                    )
                if columns:
                    query = query.add_columns(*columns)
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_em_stock_cash_flow_quarterly <err_msg> {e} from {EmStockFSCashflowStatementQ.__tablename__}')
                return pd.DataFrame([])

    def get_em_conv_bond_info(self, bond_id_list: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmConvBondInfo,
                )
                if bond_id_list:
                    query = query.filter(
                        EmConvBondInfo.CODES.in_(bond_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_em_conv_bond_info <err_msg> {e} from {EmConvBondInfo.__tablename__}')
                return pd.DataFrame([])

    def get_em_stock_ipo_recent(self, dt):
        with RawDatabaseConnector().managed_session() as db_session:
            col_dic = {
                'IPOPRICE':'发行价',
                'IPOISSUEDATE':'首发发行日期',
                'IPOSHARESVOL':'首发数量',
                'IPOPE':'发行市盈率',
                'NAME':'股票简称',
                'SUCRATIOONL':'中签率',
                'PURCHACODEONL':'申购代码带市场',
                'CEILINGONL':'申购上限',
                'EMIND2016':'东财行业',
                'TRADEMARKET':'上市板块',
                'IPOPURCHDATEONL':'申购日期',
                'IPOANNCDATE':'发行公告日',
                'WSZQJGGGDATE':'中签公布',
                'LISTDATE':'上市日期',
                'CODES':'股票代码',
            }
            try:
                query = db_session.query(
                    EmStockIpoInfo,
                ).filter(
                    or_(
                            EmStockIpoInfo.IPOPURCHDATEONL >= dt,
                            EmStockIpoInfo.LISTDATE >= dt,
                            EmStockIpoInfo.WSZQJGGGDATE == dt,
                            EmStockIpoInfo.LISTDATE == None,
                    )
                )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time','ISSUEAMTONL','LOTNUM','COMPROFILE','BUSINESS']).rename(columns=col_dic)

                df.loc[:,'接口种类'] = ''
                df.loc[(df['上市日期'] > dt) | (df['上市日期'].isnull()),'接口种类']='未上市'
                df.loc[df['申购日期'] == dt,'接口种类']='今日申购'
                df.loc[df['上市日期'] == dt,'接口种类']='今日上市'
                df.loc[df['中签公布'] == dt,'接口种类']='今日公布中签'
                df.loc[df['申购日期'] > dt,'接口种类']='即将发行'
                df.loc[:,'申购代码'] = df.申购代码带市场.map(lambda x : x.split('.')[0] if x is not None else None)
                return df

            except Exception as e:
                print(f'Failed to get_em_stock_ipo_recent <err_msg> {e} from {EmStockIpoInfo.__tablename__}')
                return pd.DataFrame([])

    def get_em_conv_bond_ipo_recent(self, dt):
        with RawDatabaseConnector().managed_session() as db_session:
            col_dic = {
                'CODES':'转债代码',
                'CBCODE' : '转债代码无市场',
                'CBNAME' : '转债简称',
                'CBSTOCKCODE':'正股代码',
                'CBSTOCKNAME':'正股简称',
                'CBISSUEAMT':'发行规模',
                'IPOANNCDATE':'发行公告日',
                'CBIPOTYPE':'发行方式',
                'CBPURCODEONL':'申购代码',
                'ISSRATE':'发行时债项评级',
                'CBTERM':'发行期限',
                'CBISSUEPRICE':'发行价格',
                'ISSUEONLEDATE':'发行截止日期',
                'CBCONVPRICE':'转股价',
                'CBDATEONL':'申购日期',
                'CBLISTDATE':'上市日期',
                'CBRESULTDATE':'中签公布',
                'CBSUCRATEONL':'中签率',
                'QUANTLIMITINTRO':'申购数量限制说明',
            }
            try:
                query = db_session.query(
                    EmConvBondIpoInfo,
                ).filter(
                    or_(
                            EmConvBondIpoInfo.CBDATEONL >= dt,
                            EmConvBondIpoInfo.CBLISTDATE >= dt,
                            EmConvBondIpoInfo.CBRESULTDATE == dt,
                            EmConvBondIpoInfo.CBLISTDATE == None,
                    ),
                    EmConvBondIpoInfo.CBIPOTYPE == '公募',
                )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time','CBMATURITYDATE','CBREDEMPRICETM','CBRATIONCODE','CBSUCCESS','CBPUTBACKPRICEEXPLAIN','CBREDEMMEMO']).rename(columns=col_dic)
                df.loc[:,'接口种类'] = None
                df.loc[((df['上市日期'] > dt) | (df['上市日期'].isnull())) & (df['发行方式']=='公募'),'接口种类']='未上市'
                df.loc[df['申购日期'] == dt,'接口种类']='今日申购'
                df.loc[df['上市日期'] == dt,'接口种类']='今日上市'
                df.loc[df['中签公布'] == dt,'接口种类']='今日公布中签'
                df.loc[df['申购日期'] > dt,'接口种类']='即将发行'

                df.loc[:,'申购上限'] = df.申购数量限制说明.map(lambda x: int(x.split('网上申购数量上限：')[1].split('手')[0]) * 10)
                df.loc[:,'stock_id'] = df.正股代码 + '.' +df.转债代码.map(lambda x: x.split('.')[1])
                df.loc[:,'申购代码带市场'] = df.申购代码 + '.' +df.转债代码.map(lambda x: x.split('.')[1])
                df = df.dropna(subset=['接口种类'])
                stock_price = self.get_em_stock_price_recent(df.stock_id.tolist())
                df = pd.merge(df, stock_price[['close','stock_id']], on='stock_id').drop(columns=['stock_id']).rename(columns={'close':'正股价'})
                return df

            except Exception as e:
                print(f'Failed to get_em_conv_bond_ipo_recent <err_msg> {e} from {EmConvBondIpoInfo.__tablename__}')
                return pd.DataFrame([])

    def get_em_stock_price_recent(self, codes: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(EmStockPrice.DATES)
                ).one_or_none()
                if not columns:
                    query = db_session.query(
                        EmStockPrice.CODES,
                        EmStockPrice.DATES,
                        EmStockPrice.CLOSE,
                    )
                else:
                    query = db_session.query(
                        EmStockPrice.CODES,
                        EmStockPrice.DATES,
                        EmStockPrice.CLOSE,
                    ).add_columns(*columns)
                if codes:
                    query = query.filter(
                        EmStockPrice.CODES.in_(codes),
                        EmStockPrice.DATES == dt[0],
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_em_stock_price_recent <err_msg> {e} from {EmStockPrice.__tablename__}')
                return pd.DataFrame([])

    def get_em_conv_bond_dirty_price(self, codes: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmConvBondDirtyPrice.CODES,
                    EmConvBondDirtyPrice.DATES,
                    EmConvBondDirtyPrice.CLOSE,
                    EmConvBondDirtyPrice.OPEN,
                )
                if codes:
                    query = query.filter(
                        EmConvBondDirtyPrice.CODES.in_(codes),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get_em_conv_bond_dirty_price <err_msg> {e} from {EmConvBondDirtyPrice.__tablename__}')
                return pd.DataFrame([])

    def get_em_bond_rate_maturity(self, codes: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmBondRateMaturity
                )
                if codes:
                    query = query.filter(
                        EmBondRateMaturity.bond_id.in_(codes),
                    )
                return pd.read_sql(query.statement, query.session.bind).replace('A1','A').replace('A3','AAA')
            except Exception as e:
                print(f'Failed to get_em_conv_bond_dirty_price <err_msg> {e} from {EmBondRateMaturity.__tablename__}')
                return pd.DataFrame([])

    def get_em_stock_ipo_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            col_dic = {
                'IPOPRICE':'发行价',
                'IPOISSUEDATE':'首发发行日期',
                'IPOSHARESVOL':'发行总数',
                'IPOPE':'发行市盈率',
                'NAME':'股票简称',
                'SUCRATIOONL':'中签率',
                'PURCHACODEONL':'申购代码带市场',
                'CEILINGONL':'申购数量上限',
                'EMIND2016':'东财行业',
                'TRADEMARKET':'上市板块',
                'IPOPURCHDATEONL':'申购日期',
                'IPOANNCDATE':'发行公告日',
                'WSZQJGGGDATE':'中签公布',
                'LISTDATE':'上市日期',
                'CODES':'股票代码',
                'ISSUEAMTONL':'网上发行',
                'LOTNUM':'中签号',
                'COMPROFILE':'公司简介',
                'BUSINESS':'经营范围',
            }
            try:
                query = db_session.query(EmStockIpoInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time']).rename(columns=col_dic)
                df['股票代码不带市场'] = df.股票代码.map(lambda x : x.split('.')[0] if x is not None else None)
                df['申购代码'] = df.申购代码带市场.map(lambda x : x.split('.')[0] if x is not None else None)
                df['申购资金上限'] = df['发行价'] * df['申购数量上限']
                return df

            except Exception as e:
                print(f'Failed to get_em_stock_ipo_info <err_msg> {e} from {EmStockIpoInfo.__tablename__}')
                return pd.DataFrame([])

    def get_em_conv_bond_ipo_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            col_dic = {
                'CODES':'转债代码',
                'CBCODE' : '转债代码无市场',
                'CBNAME' : '转债简称',
                'CBSTOCKCODE':'正股代码',
                'CBSTOCKNAME':'正股简称',
                'CBISSUEAMT':'发行规模',
                'IPOANNCDATE':'发行公告日',
                'CBIPOTYPE':'发行方式',
                'CBPURCODEONL':'申购代码',
                'ISSRATE':'发行时债项评级',
                'CBTERM':'发行期限',
                'CBISSUEPRICE':'发行价格',
                'ISSUEONLEDATE':'发行截止日期',
                'CBCONVPRICE':'转股价',
                'CBDATEONL':'申购日期',
                'CBLISTDATE':'上市日期',
                'CBRESULTDATE':'中签公布',
                'CBSUCRATEONL':'中签率',
                'QUANTLIMITINTRO':'申购数量限制说明',
                'CBMATURITYDATE':'到期日',
                'CBREDEMPRICETM':'到期赎回价格',
                'CBRATIONCODE':'配售代码',
                'CBSUCCESS':'中签号',
                'CBPUTBACKPRICEEXPLAIN':'回售价格说明',
                'CBREDEMMEMO':'赎回价格说明',
            }
            try:
                query = db_session.query(
                    EmConvBondIpoInfo,
                ).filter(
                    EmConvBondIpoInfo.CBIPOTYPE == '公募',
                )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time']).rename(columns=col_dic)
                df.loc[:,'stock_id'] = df.正股代码 + '.' +df.转债代码.map(lambda x: x.split('.')[1])
                stock_price = self.get_em_stock_price_recent(df.stock_id.tolist())
                df = pd.merge(df, stock_price[['close','stock_id']], on='stock_id').drop(columns=['stock_id']).rename(columns={'close':'正股价'})
                df['溢价率'] = df.转股价 / df.正股价 - 1
                df['转股价值'] = df.发行价格 / df.转股价 * df.正股价
                df['回售价'] = None if df.回售价格说明 is None else df.发行价格
                df['赎回价'] = None if df.赎回价格说明 is None else df.发行价格
                df['申购数量上限'] = df.申购数量限制说明.map(lambda x: int(x.split('网上申购数量上限：')[1].split('手')[0])*10)
                df['申购代码带市场'] = df.申购代码 + '.' +df.转债代码.map(lambda x: x.split('.')[1] if x is not None else None)
                df = df.drop(columns=['回售价格说明','赎回价格说明'])
                return df

            except Exception as e:
                print(f'Failed to get_em_conv_bond_ipo_info <err_msg> {e} from {EmConvBondIpoInfo.__tablename__}')
                return pd.DataFrame([])

    def get_em_future_price(self, start_date: str = '', end_date: str = '', future_ids: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        EmFuturePrice
                    )
                else:
                    query = db_session.query(
                        EmFuturePrice.CODES,
                        EmFuturePrice.DATES,
                    ).add_columns(*columns)
                if future_ids:
                    query = query.filter(
                        EmFuturePrice.CODES.in_(future_ids),
                    )
                if start_date:
                    query = query.filter(
                        EmFuturePrice.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmFuturePrice.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFuturePrice.__tablename__}')
                return None

    def get_em_future_price_detail(self, start_date: str = '', end_date: str = '', future_ids: Tuple[str] = (), columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        EmFuturePriceDetail
                    )
                else:
                    query = db_session.query(
                        EmFuturePriceDetail.CODES,
                        EmFuturePriceDetail.DATES,
                    ).add_columns(*columns)
                if future_ids:
                    query = query.filter(
                        EmFuturePriceDetail.CODES.in_(future_ids),
                    )
                if start_date:
                    query = query.filter(
                        EmFuturePriceDetail.DATES >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmFuturePriceDetail.DATES <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFuturePriceDetail.__tablename__}')
                return None

    def delete_em_future_price(self, start_date, end_date, future_ids: Tuple[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EmFuturePrice
                ).filter(
                    EmFuturePrice.CODES.in_(future_ids),
                    EmFuturePrice.DATES >= start_date,
                    EmFuturePrice.DATES <= end_date
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {EmFuturePrice.__tablename__}')
                return None

    def get_os_index_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSIndexInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_em_stock_concept_info <err_msg> {e} from {OSIndexInfo.__tablename__}')
                return pd.DataFrame([])


    def get_em_stock_concept_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(EmStockConceptInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_em_stock_concept_info <err_msg> {e} from {EmStockConceptInfo.__tablename__}')
                return pd.DataFrame([])


    def get_qs_fund_indicator(self, dt=None):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not dt:
                    dt = db_session.query(
                        func.max(QSOverseaFundIndicator.datetime)
                    ).one_or_none()
                    if dt:
                        dt = dt[0]

                query = db_session.query(
                    QSOverseaFundIndicator
                    ).filter(
                        QSOverseaFundIndicator.datetime == dt
                    )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to QSOverseaFundIndicator <err_msg> {e} from {QSOverseaFundIndicator.__tablename__}')
                return pd.DataFrame([])

    def get_qs_fund_indicator_single_fund(self, fund_id):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    QSOverseaFundIndicator
                    ).filter(
                        QSOverseaFundIndicator.codes == fund_id
                    ).order_by(
                        QSOverseaFundIndicator.datetime.desc()
                    ).limit(3)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to QSOverseaFundIndicator <err_msg> {e} from {QSOverseaFundIndicator.__tablename__}')
                return pd.DataFrame([])

    def get_os_stock_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSStockInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_os_stock_info <err_msg> {e} from {OSStockInfo.__tablename__}')
                return pd.DataFrame([])

    def get_os_corp_bond_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSCorpBondInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_os_corp_bond_info <err_msg> {e} from {OSCorpBondInfo.__tablename__}')
                return pd.DataFrame([])

    def get_os_govt_bond_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSGovtBondInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_os_govt_bond_info <err_msg> {e} from {OSGovtBondInfo.__tablename__}')
                return pd.DataFrame([])

    def get_os_mtge_bond_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSMtgeBondInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_mtge_bond_info <err_msg> {e} from {OSMtgeBondInfo.__tablename__}')
                return pd.DataFrame([])

    def get_os_index_future_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSIndexFutureInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_index_future_info <err_msg> {e} from {OSIndexFutureInfo.__tablename__}')
                return pd.DataFrame([])

    def get_os_muni_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSMuniInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_muni_info <err_msg> {e} from {OSMuniInfo.__tablename__}')
                return pd.DataFrame([])

    def get_os_pfd_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSPfdInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_os_pfd_info <err_msg> {e} from {OSPfdInfo.__tablename__}')
                return pd.DataFrame([])

    def get_os_comdty_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSComdtyInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_os_comdty_info <err_msg> {e} from {OSComdtyInfo.__tablename__}')
                return pd.DataFrame([])

    def get_os_district_info(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSDistrictInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_os_district_info <err_msg> {e} from {OSDistrictInfo.__tablename__}')
                return pd.DataFrame([])

    def get_os_fund_fin_fac(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(OSDistrictInfo)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_os_district_info <err_msg> {e} from {OSDistrictInfo.__tablename__}')
                return pd.DataFrame([])


    def get_os_stock_fin_fac(self, *, stock_list: Tuple[str] = (), date_list: Tuple[str] = (), start_date: str = '', end_date: str = '', columns: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                if not columns:
                    query = db_session.query(
                        EmOverseaStockFinFac
                    )
                else:
                    query = db_session.query(
                        EmOverseaStockFinFac.stock_code,
                        EmOverseaStockFinFac.report_date,
                    ).add_columns(*columns)
                if stock_list:
                    query = query.filter(
                        EmOverseaStockFinFac.stock_code.in_(stock_list)
                    )
                if date_list:
                    query = query.filter(
                        EmOverseaStockFinFac.report_date.in_(date_list)
                    )
                else:
                    if start_date:
                        query = query.filter(
                            EmOverseaStockFinFac.report_date >= start_date,
                        )
                    if end_date:
                        query = query.filter(
                            EmOverseaStockFinFac.report_date <= end_date,
                        )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmOverseaStockFinFac.__tablename__}')
                return None

    def get_os_fund_hold_asset_weight(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(OSFundHoldAsset.report_date)).filter(
                            OSFundHoldAsset.codes.in_(fund_ids), 
                ).one_or_none()
                if dt:
                    dt = dt[0]
                query = db_session.query(OSFundHoldAsset)
                if fund_ids:
                    query = query.filter(
                        OSFundHoldAsset.codes.in_(fund_ids),
                        OSFundHoldAsset.report_date == dt,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                dic = {
                    'equity':['top_10_equity_w','top_10_pfd_w'],
                    'bond':['top_10_corp_bond_w','top_10_national_bond_w','top_10_mtge_bond_w','top_10_district_bond_w'],
                    'cash':['top_10_cash_w'],
                }
                for asset, fac_list in dic.items():
                    df.loc[:,asset] = df[fac_list].sum(axis=1, min_count=1)
                l = ['codes','report_date','desc_name','isin_code']
                df = df[l+list(dic.keys())]
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundHoldAsset.__tablename__}')
                return None

    def get_os_fund_hold_bond_type_weight(self, fund_ids: Tuple[str] = ()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dt = db_session.query(
                    func.max(OSFundHoldAsset.report_date)).filter(
                            OSFundHoldAsset.codes.in_(fund_ids), 
                ).one_or_none()
                if dt:
                    dt = dt[0]
                query = db_session.query(OSFundHoldAsset)
                if fund_ids:
                    query = query.filter(
                        OSFundHoldAsset.codes.in_(fund_ids),
                        OSFundHoldAsset.report_date == dt,
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                dic = {
                    'top_10_corp_bond_w':'corp_bond', # 公司债
                    'top_10_national_bond_w':'national_debt', # 国债
                    'top_10_mtge_bond_w':'mtge_bond', # 抵押债
                    'top_10_district_bond_w':'district_bond', # 地方债
                }
                l = ['codes','report_date','desc_name','isin_code']
                w_sum = df[list(dic.keys())].sum(axis=1)
                for col in dic:
                    df.loc[:, col] = df[col] / w_sum
                df = df.rename(columns=dic)
                df = df[l+list(dic.values())]
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {OSFundHoldAsset.__tablename__}')
                return None
    
    def get_btc(self, asset_ids,start_date:str='',end_date:str=''):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(EmBTCFromWeb).filter(
                    EmBTCFromWeb.codes.in_(asset_ids)
                )
                if start_date:
                    query = query.filter(
                        EmBTCFromWeb.date >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        EmBTCFromWeb.date <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_btc <err_msg> {e} from {EmBTCFromWeb.__tablename__}')
                return pd.DataFrame([])

    def get_hf_fund_info(self, fund_list: Tuple[str]=()):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(HFFundInfo)
                if fund_list:
                    query = query.filter(
                        HFFundInfo.fund_id.in_(fund_list)
                    )
                return pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
            except Exception as e:
                print(f'Failed to get_hf_fund_info <err_msg> {e} from {HFFundInfo.__tablename__}')
                return pd.DataFrame([])

    def delete_hf_fund_info(self, fund_id_list: Tuple[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HFFundInfo
                ).filter(
                    HFFundInfo.fund_id.in_(fund_id_list),
                ).delete(synchronize_session=False)
                db_session.commit()
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {HFFundInfo.__tablename__}')

    def get_hf_fund_nav(self, fund_ids, start_date:str='',end_date:str=''):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(HFFundNav).filter(
                    HFFundNav.fund_id.in_(fund_ids)
                )
                if start_date:
                    query = query.filter(
                        HFFundNav.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        HFFundNav.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_hf_fund_nav <err_msg> {e} from {HFFundNav.__tablename__}')
                return pd.DataFrame([])

    def get_hf_fund_nav_dt(self, start_date:str='', end_date:str=''):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(HFFundNav)
                if start_date:
                    query = query.filter(
                        HFFundNav.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        HFFundNav.datetime <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_hf_fund_nav_dt <err_msg> {e} from {HFFundNav.__tablename__}')
                return pd.DataFrame([])

    def delete_hf_fund_nav(self, fund_id_to_delete: str, datetime_list: Tuple[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HFFundNav
                ).filter(
                    HFFundNav.fund_id == fund_id_to_delete,
                    HFFundNav.datetime.in_(datetime_list),
                ).delete(synchronize_session=False)
                db_session.commit()
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {HFFundNav.__tablename__}')

    def get_hf_index_price(self, index_ids, start_date:str='',end_date:str=''):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(HFIndexPrice).filter(
                    HFIndexPrice.index_id.in_(index_ids)
                )
                if start_date:
                    query = query.filter(
                        HFIndexPrice.index_date >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        HFIndexPrice.index_date <= end_date,
                    )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get_hf_index_price <err_msg> {e} from {HFIndexPrice.__tablename__}')
                return pd.DataFrame([])

    def delete_hf_index_price(self, index_id_to_delete: str, datetime_list: Tuple[str]):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HFIndexPrice
                ).filter(
                    HFIndexPrice.index_id == index_id_to_delete,
                    HFIndexPrice.index_date.in_(datetime_list),
                ).delete(synchronize_session=False)
                db_session.commit()
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {HFIndexPrice.__tablename__}')

    def get_date_range(self, time_para, begin_date, end_date):
        try:
            if time_para is None:
                if begin_date is None and end_date is None:
                    time_para = 'ALL'
                else:
                    return begin_date, end_date
            today = datetime.datetime.today().date()
            dic = {
                    # 取到上周一
                    '1W':DateOffset(weeks=1) if today.weekday() == 0 else datetime.timedelta(days=(today.weekday() + 3)),
                    '2W':DateOffset(weeks=2),
                    '1M':DateOffset(months=1),
                    '3M':DateOffset(months=3),
                    '6M':DateOffset(months=6),
                    '1Y':DateOffset(months=12),
                    '3Y':DateOffset(years=3),
                    '5Y':DateOffset(years=5),
                    '10Y':DateOffset(years=10),
                    'ALL':DateOffset(years=30),   
            }
            if time_para in dic:
                try:
                    begin_date = (today - dic[time_para]).date()
                except:
                    begin_date = today - dic[time_para]
            elif time_para == 'YTD':
                begin_date = datetime.date(today.year,1,1)
            return begin_date, today
        
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from raw.get_date_range')
            return None, None

    def get_stock_future_diff_info(self, codes):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(EmStockFutureDiffInfo).filter(
                    EmStockFutureDiffInfo.codes.in_(codes)
                )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockFutureDiffInfo.__tablename__}')
                return pd.DataFrame([])

    def get_stock_index_future_diff_base(self, begin_date, end_date, codes):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(EmStockFutureDiff).filter(
                    EmStockFutureDiff.CODES.in_(codes),
                    EmStockFutureDiff.DATES >= begin_date,
                    EmStockFutureDiff.DATES <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                df = - df.pivot_table(index='DATES',columns='CODES',values='RESULT')
                df.index.name = 'datetime'
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockFutureDiff.__tablename__}')
                return pd.DataFrame([])


    def get_stock_index_future_diff(self, begin_date, end_date, time_para, codes=['EMM00597133','EMM00597141','EMM00597137']):
        # 这里是现期差 基差是期现差
        begin_date, end_date = self.get_date_range(time_para, begin_date, end_date)
        info = self.get_stock_future_diff_info(codes)
        info.loc[:,'show_name'] = info.name.map(lambda x : x.split('_')[-1]+'期货基差')
        info_dic = info.set_index('codes').to_dict()['show_name']
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(EmStockFutureDiff).filter(
                    EmStockFutureDiff.CODES.in_(codes),
                    EmStockFutureDiff.DATES >= begin_date,
                    EmStockFutureDiff.DATES <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                df = - df.pivot_table(index='DATES',columns='CODES',values='RESULT').rename(columns=info_dic)
                df.index.name = 'datetime'
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmStockFutureDiff.__tablename__}')
                return pd.DataFrame([])

    def get_north_cap(self, begin_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(EMNorthCapital).filter(
                    EMNorthCapital.datetime >= begin_date,
                    EMNorthCapital.datetime <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EMNorthCapital.__tablename__}')
                return pd.DataFrame([])

    def get_south_cap(self, begin_date, end_date):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(EMSouthCapital).filter(
                    EMSouthCapital.datetime >= begin_date,
                    EMSouthCapital.datetime <= end_date,
                )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EMSouthCapital.__tablename__}')
                return pd.DataFrame([])

    def get_hf_fund_nav_miss(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(HFFundNavMiss)
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {HFFundNavMiss.__tablename__}')
                return pd.DataFrame([])

    def get_exsited_nav_hf_fund_list(self):
        try:
            fund_info = RawDataApi().get_hf_fund_info()
            miss_df = RawDataApi().get_hf_fund_nav_miss()
            fund_info = fund_info[~fund_info.fund_id.isin(miss_df.fund_id)]
            fund_info = fund_info[['fund_id','desc_name']]
            return fund_info

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from {HFFundNavMiss.__tablename__}')
            return pd.DataFrame([])

    def get_em_future_info(self, tickers=None):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(EmFutureInfoDetail)
                if tickers:
                    query = query.filter(
                        EmFutureInfoDetail.EMCODE.in_(tickers)
                    )
                df = pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
                return df
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {EmFutureInfoDetail.__tablename__}')
                return pd.DataFrame([])
