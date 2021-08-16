
from typing import Tuple, List

import datetime
from sqlalchemy import distinct
from sqlalchemy.sql import func
import pandas as pd
import numpy as np
from ...util.singleton import Singleton
from ...constant import FOFStrategyTypeDic
from ..wrapper.mysql import BasicDatabaseConnector
from ..view.basic_models import *
from .raw import RawDataApi


class BasicDataApi(metaclass=Singleton):
    def get_trading_day_list(self, start_date='', end_date=''):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        TradingDayList
                    )
                if start_date:
                    query = query.filter(
                        TradingDayList.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        TradingDayList.datetime <= end_date,
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {TradingDayList.__tablename__}')

    def get_last_week_last_trade_dt(self):
        today = datetime.datetime.today().date()
        start_date = today - datetime.timedelta(days=15)
        df = self.get_trading_day_list(start_date=start_date)
        df.loc[:,'weekday'] = df.datetime.map(lambda x : x.weekday())
        td = pd.to_datetime(df.datetime)
        td = [_.week for _ in td]
        df.loc[:,'week_num'] = td
        last_week_num = df.week_num.values[-1]
        last_week_dt = df[df.week_num != last_week_num].datetime.values[-1]
        return last_week_dt

    def is_today_trading_date(self):
        today = datetime.datetime.now().date()
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        TradingDayList
                    ).filter(
                        TradingDayList.datetime >= today,
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                con = today in tag_df.datetime.tolist()
                return con

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {TradingDayList.__tablename__}')

    def get_last_trading_day(self, dt=datetime.datetime.today()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query_result = db_session.query(
                    func.max(TradingDayList.datetime)
                ).filter(
                    TradingDayList.datetime < dt.date(),
                ).one_or_none()
                if query_result:
                    return query_result[0]
                else:
                    return None

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {TradingDayList.__tablename__}')

    def get_sector_info(self):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        SectorInfo
                    )
                ret_df = pd.read_sql(query.statement, query.session.bind)
                return ret_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {SectorInfo.__tablename__}')

    def get_sector_index_funds(self, index_id):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        SectorFunds
                ).filter(
                    SectorFunds.index_id == index_id,
                )
                ret_df = pd.read_sql(query.statement, query.session.bind)
                return ret_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {SectorFunds.__tablename__}')

    def get_sector_index_info(self):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        SectorFunds
                )
                ret_df = pd.read_sql(query.statement, query.session.bind)
                return ret_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {SectorFunds.__tablename__}')

    def get_sector_main_index_id(self, sector_id):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    SectorInfo.main_index_id
                ).filter(
                    SectorInfo.sector_id == sector_id
                )
                ret_df = pd.read_sql(query.statement, query.session.bind)
                return ret_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {SectorInfo.__tablename__}')

    def get_sector_indices(self, sector_id):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    distinct(SectorFunds.index_id).label("index_id")
                ).filter(
                    SectorFunds.sector_id == sector_id
                )
                ret_df = pd.read_sql(query.statement, query.session.bind)
                return ret_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {SectorFunds.__tablename__}')

    def get_fund_info(self, fund_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundInfo
                    )
                if fund_list:
                    query = query.filter(
                        FundInfo.fund_id.in_(fund_list),
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundInfo.__tablename__}')

    def delete_fund_info(self, fund_list: Tuple[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundInfo
                ).filter(FundInfo.fund_id.in_(fund_list))
                query.delete(synchronize_session=False)
                db_session.commit()
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {FundInfo.__tablename__}')

    def get_fund_info_by_key_words(self, key_words: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundInfo
                )
                for key_word in key_words:
                    query = query.filter(
                         FundInfo.desc_name.like(f'%{key_word}%')
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundInfo.__tablename__}')
                return None

    def get_fund_benchmark(self, fund_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundBenchmark
                )
                if fund_list:
                    query = query.filter(
                        FundBenchmark.em_id.in_(fund_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundBenchmark.__tablename__}')

    def delete_fund_benchmark(self, fund_list: Tuple[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundBenchmark
                ).filter(FundBenchmark.em_id.in_(fund_list))
                query.delete(synchronize_session=False)
                db_session.commit()
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {FundBenchmark.__tablename__}')

    def get_index_info(self, index_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        IndexInfo
                    )
                if index_list:
                    query = query.filter(
                        IndexInfo.index_id.in_(index_list)
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexInfo.__tablename__}')

    def get_index_info_by_key_words(self, key_words:Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        IndexInfo
                    )
                for key_word in key_words:
                    query = query.filter(
                        IndexInfo.desc_name.like(f'%{key_word}%')
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexInfo.__tablename__}')

    def get_index_info_by_em_id(self, em_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        IndexInfo
                    )
                if em_id_list:
                    query = query.filter(
                        IndexInfo.em_id.in_(em_id_list)
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexInfo.__tablename__}')

    def get_index_component(self, index_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    IndexComponent
                )
                if index_list:
                    query = query.filter(
                        IndexComponent.index_id.in_(index_list)
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexComponent.__tablename__}')
                return None

    def get_stock_info(self):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        StockInfo
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {StockInfo.__tablename__}')

    def get_fund_nav(self, fund_list=None, dt=None):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundNav
                )
                if fund_list:
                    query = query.filter(
                        FundNav.fund_id.in_(fund_list),
                    )
                if dt:
                    query = query.filter(
                        FundNav.datetime == dt,
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundNav.__tablename__}')

    def delete_fund_nav(self, start_date, end_date, fund_list: Tuple[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundNav
                ).filter(
                    FundNav.datetime >= start_date,
                    FundNav.datetime <= end_date,
                )
                if fund_list:
                    query = query.filter(FundNav.fund_id.in_(fund_list))
                query.delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {FundNav.__tablename__}')
                return None

    def get_fund_nav_with_date(self, start_date='', end_date='', fund_list: Tuple[str] = (), columns: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                if columns:
                    query = db_session.query(
                        FundNav.fund_id,
                        FundNav.datetime,
                    ).add_columns(*columns)
                else:
                    query = db_session.query(
                        FundNav,
                    )
                if fund_list:
                    query = query.filter(FundNav.fund_id.in_(fund_list))
                if start_date:
                    query = query.filter(
                        FundNav.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        FundNav.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundNav.__tablename__}')

    def get_stock_price(self, stock_list, begin_date: str = '', end_date: str = ''):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        StockPrice
                ).filter(
                    # We could query all fund_ids at one time
                    StockPrice.stock_id.in_(stock_list),
                )
                if begin_date:
                    query = query.filter(StockPrice.datetime >= begin_date)
                if end_date:
                    query = query.filter(StockPrice.datetime <= end_date)

                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {StockPrice.__tablename__}')

    def get_fund_ret(self, fund_list):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundRet
                ).filter(
                        # We could query all fund_ids at one time
                        FundRet.fund_id.in_(fund_list),
                    )

                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundRet.__tablename__}')

    def get_index_price(self, index_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        IndexPrice
                )
                if index_list:
                    query = query.filter(
                        # We could query all fund_ids at one time
                        IndexPrice.index_id.in_(index_list),
                    )

                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexPrice.__tablename__}')

    def get_index_price_dt(self, start_date: str = '', end_date: str = '', index_list: Tuple[str] = (), columns: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                if columns:
                    query = db_session.query(
                        IndexPrice.index_id,
                        IndexPrice.datetime,
                    ).add_columns(*columns)
                else:
                    query = db_session.query(
                        IndexPrice
                    )
                if index_list:
                    query = query.filter(
                        IndexPrice.index_id.in_(index_list),
                    )
                if start_date:
                    query = query.filter(
                        IndexPrice.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        IndexPrice.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {IndexPrice.__tablename__}')

    def delete_index_price(self, index_id_list, start_date, end_date):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    IndexPrice
                ).filter(
                    IndexPrice.index_id.in_(index_id_list),
                    IndexPrice.datetime >= start_date,
                    IndexPrice.datetime <= end_date,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {IndexPrice.__tablename__}')
                return None

    def get_fund_nav_with_date_range(self, fund_list, start_date, end_date):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundNav
                ).filter(
                        FundNav.fund_id.in_(fund_list),
                        FundNav.datetime >= start_date,
                        FundNav.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundNav.__tablename__}')

    def get_fund_list(self):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundInfo.fund_id
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundInfo.__tablename__}')

    def get_fund_fee(self):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundInfo.fund_id,
                        FundInfo.manage_fee,
                        FundInfo.trustee_fee,
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundInfo.__tablename__}')

    def get_fund_asset(self):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundInfo.fund_id,
                        FundInfo.asset_type,
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundInfo.__tablename__}')

    def get_fund_id_mapping(self):
        fund_id_mapping = {}
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query_results = db_session.query(
                        FundInfo.fund_id,
                        FundInfo.order_book_id,
                        FundInfo.start_date,
                        FundInfo.end_date
                    ).all()

                for fund_id, order_book_id, start_date, end_date in query_results:
                    if order_book_id not in fund_id_mapping:
                        fund_id_mapping[order_book_id] = []
                    fund_id_mapping[order_book_id].append(
                        {'fund_id': fund_id, 'start_date':start_date, 'end_date': end_date})

            except Exception as e:
                print(f'Failed to get fund id mapping <err_msg> {e} from {FundInfo.__tablename__}')
                return None

        return fund_id_mapping

    def get_fund_size(self):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundSize,
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundSize.__tablename__}')

    def get_fund_open_info(self):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundOpenInfo,
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundOpenInfo.__tablename__}')


    def get_fund_status(self):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundStatusLatest,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundStatusLatest.__tablename__}')

    def get_inside_market_funds(self):
        fund_status_latest = self.get_fund_status()
        in_market_fund_list = fund_status_latest[(~fund_status_latest['trade_status'].isnull()) & (fund_status_latest.trade_status != '终止上市')].fund_id.tolist()
        fund_info = self.get_fund_info()
        return fund_info[fund_info.fund_id.isin(in_market_fund_list)]

    def get_outside_market_funds(self):
        fund_status_latest = self.get_fund_status()
        in_market_fund_list = fund_status_latest[(~fund_status_latest['trade_status'].isnull()) & (fund_status_latest.trade_status != '终止上市')].fund_id.tolist()
        fund_info = self.get_fund_info()
        return fund_info[~fund_info.fund_id.isin(in_market_fund_list)]

    def get_fund_conv_stats(self):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundConvStats,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e}')

    @staticmethod
    def get_history_fund_size(fund_id: str = '', start_date=None, end_date=None):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    Fund_size_and_hold_rate,
                )
                if fund_id:
                    query = query.filter(
                        Fund_size_and_hold_rate.fund_id == fund_id
                    )
                if start_date is not None:
                    query = query.filter(
                        Fund_size_and_hold_rate.datetime >= start_date,
                    )
                if end_date is not None:
                    query = query.filter(
                        Fund_size_and_hold_rate.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {Fund_size_and_hold_rate.__tablename__}')
                return pd.DataFrame([])

    def delete_fund_size_hold_rate(self, date_to_delete: datetime.date, fund_list: List[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    Fund_size_and_hold_rate
                ).filter(
                    Fund_size_and_hold_rate.fund_id.in_(fund_list),
                    Fund_size_and_hold_rate.datetime == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {Fund_size_and_hold_rate.__tablename__}')
                return False

    @staticmethod
    def get_fund_size_range(start_date='', end_date='', fund_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    Fund_size_and_hold_rate.fund_id,
                    Fund_size_and_hold_rate.datetime,
                    Fund_size_and_hold_rate.size,
                )
                if fund_list:
                    query = query.filter(
                        Fund_size_and_hold_rate.fund_id.in_(fund_list),
                    )
                if start_date:
                    query = query.filter(
                        # 按报告日多选取3个月，保证初值可以fill出来
                        Fund_size_and_hold_rate.datetime >= (pd.to_datetime(start_date) - datetime.timedelta(days=100)).strftime('%Y%m%d'),
                    )
                if end_date:
                    query = query.filter(
                        Fund_size_and_hold_rate.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {Fund_size_and_hold_rate.__tablename__}')
                return pd.DataFrame([])

    @staticmethod
    def get_fund_company_hold(start_date='', end_date='', fund_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    Fund_size_and_hold_rate.fund_id,
                    Fund_size_and_hold_rate.datetime,
                    Fund_size_and_hold_rate.institution_holds,
                )
                if fund_list:
                    query = query.filter(
                        Fund_size_and_hold_rate.fund_id.in_(fund_list),
                    )
                if start_date:
                    query = query.filter(
                        # 按报告日多选取3个月，保证初值可以fill出来
                        Fund_size_and_hold_rate.datetime >= (pd.to_datetime(start_date) - datetime.timedelta(days=100)).strftime('%Y%m%d'),
                    )
                if end_date:
                    query = query.filter(
                        Fund_size_and_hold_rate.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {Fund_size_and_hold_rate.__tablename__}')
                return pd.DataFrame([])

    @staticmethod
    def get_fund_persional_hold(start_date='', end_date='', fund_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    Fund_size_and_hold_rate.fund_id,
                    Fund_size_and_hold_rate.datetime,
                    Fund_size_and_hold_rate.personal_holds,
                )
                if fund_list:
                    query = query.filter(
                        Fund_size_and_hold_rate.fund_id.in_(fund_list),
                    )
                if start_date:
                    query = query.filter(
                        # 按报告日多选取3个月，保证初值可以fill出来
                        Fund_size_and_hold_rate.datetime >= (pd.to_datetime(start_date) - datetime.timedelta(days=100)).strftime('%Y%m%d'),
                    )
                if end_date:
                    query = query.filter(
                        Fund_size_and_hold_rate.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {Fund_size_and_hold_rate.__tablename__}')
                return pd.DataFrame([])

    @staticmethod
    def get_fund_size_all_data():
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    Fund_size_and_hold_rate
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {Fund_size_and_hold_rate.__tablename__}')
                return pd.DataFrame([])

    @staticmethod
    def get_history_fund_rating(fund_id):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundRate,
                ).filter(
                    FundRate.fund_id == fund_id
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundRate.__tablename__}')
                return pd.DataFrame([])

    @staticmethod
    def get_fund_hold_asset_by_id(fund_id: str = '', start_date=None, end_date=None):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldAsset,
                )
                if fund_id:
                    query = query.filter(
                        FundHoldAsset.fund_id == fund_id,
                    )
                if start_date is not None:
                    query = query.filter(
                        FundHoldAsset.datetime >= start_date,
                    )
                if end_date is not None:
                    query = query.filter(
                        FundHoldAsset.datetime <= end_date,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundHoldAsset.__tablename__}')
                return pd.DataFrame([])


    def get_fund_hold_asset_by_id_list(self, fund_id):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldAsset,
                )
                if fund_id:
                    query = query.filter(
                        FundHoldAsset.fund_id.in_(fund_id),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundHoldAsset.__tablename__}')
                return pd.DataFrame([])


    def delete_fund_hold_asset(self, date_to_delete: datetime.date, fund_list: List[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    FundHoldAsset
                ).filter(
                    FundHoldAsset.fund_id.in_(fund_list),
                    FundHoldAsset.datetime == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {FundHoldAsset.__tablename__}')
                return False

    @staticmethod
    def get_fund_hold_industry_by_id(fund_id):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldIndustry,
                ).filter(
                    FundHoldIndustry.fund_id == fund_id,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundHoldIndustry.__tablename__}')
                return pd.DataFrame([])

    @staticmethod
    def get_fund_hold_stock_by_id(fund_id: str = ''):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldStock,
                )
                if fund_id:
                    query = query.filter(
                        FundHoldStock.fund_id == fund_id,
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundHoldStock.__tablename__}')
                return pd.DataFrame([])

    def get_fund_hold_stock_by_id_list(self, fund_id):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldStock,
                )
                if fund_id:
                    query = query.filter(
                        FundHoldStock.fund_id.in_(fund_id),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundHoldStock.__tablename__}')
                return pd.DataFrame([])


    @staticmethod
    def get_fund_hold_bond_by_id(fund_id):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldBond,
                ).filter(
                    FundHoldBond.fund_id == fund_id,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundHoldBond.__tablename__}')
                return pd.DataFrame([])

    def get_fund_hold_bond_by_id_list(self, fund_id):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldBond,
                ).filter(
                    FundHoldBond.fund_id.in_(fund_id),
                )
                df = pd.read_sql(query.statement, query.session.bind)
                return df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {FundHoldBond.__tablename__}')
                return pd.DataFrame([])


    def get_style_analysis_data(self, start_date: str, end_date: str, stock_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    StyleAnalysisStockFactor
                )
                if stock_list:
                    query = query.filter(
                        StyleAnalysisStockFactor.stock_id.in_(stock_list)
                    )
                query = query.filter(
                    StyleAnalysisStockFactor.datetime >= start_date,
                    StyleAnalysisStockFactor.datetime <= end_date,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {StyleAnalysisStockFactor.__tablename__}')
                return

    def get_style_analysis_time_range(self) -> pd.DataFrame:
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    func.max(StyleAnalysisStockFactor.datetime).label('end_date'),
                    func.min(StyleAnalysisStockFactor.datetime).label('start_date'),
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get time range data <err_msg> {e} from {StyleAnalysisStockFactor.__tablename__}')
                return

    def get_barra_cne5_risk_factor(self, start_date: str, end_date: str, stock_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    BarraCNE5RiskFactor
                )
                if stock_list:
                    query = query.filter(
                        BarraCNE5RiskFactor.stock_id.in_(stock_list)
                    )
                query = query.filter(
                    BarraCNE5RiskFactor.datetime >= start_date,
                    BarraCNE5RiskFactor.datetime <= end_date,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {BarraCNE5RiskFactor.__tablename__}')
                return

    def get_fund_hold_asset(self, dt) -> pd.DataFrame:
       with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundHoldAsset
                        ).filter(
                            FundHoldAsset.datetime == dt
                        )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get time range data <err_msg> {e} from {FundHoldAsset.__tablename__}')
                return

    def get_fund_hold_industry(self, dt) -> pd.DataFrame:
       with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        FundHoldIndustry
                        ).filter(
                            FundHoldIndustry.datetime == dt
                        )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get time range data <err_msg> {e} from {FundHoldIndustry.__tablename__}')
                return

    def delete_fund_hold_industry(self, date_to_delete: datetime.date, fund_list: List[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    FundHoldIndustry
                ).filter(
                    FundHoldIndustry.fund_id.in_(fund_list),
                    FundHoldIndustry.datetime == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {FundHoldIndustry.__tablename__}')
                return False

    def get_fund_hold_stock(self, dt=None) -> pd.DataFrame:
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldStock
                )
                if dt:
                    query = query.filter(
                        FundHoldStock.datetime == dt
                    )
                else:
                    query = query.filter(
                        FundHoldStock.datetime > datetime.datetime.now() - datetime.timedelta(days=180)
                    )

                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get time range data <err_msg> {e} from {FundHoldStock.__tablename__}')
                return

    def get_fund_hold_stock_latest(self, dt=None, fund_list =[]) -> pd.DataFrame:
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                if not dt:
                    dt = db_session.query(
                        func.max(FundHoldStock.datetime)
                    ).filter(
                    FundHoldStock.fund_id.in_(fund_list),
                ).one_or_none()
                    if dt:
                        dt = dt[0]

                query = db_session.query(
                    FundHoldStock
                ).filter(
                    FundHoldStock.datetime == dt,
                    FundHoldStock.fund_id.in_(fund_list),
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get time range data <err_msg> {e} from {FundHoldStock.__tablename__}')
                return

    def get_fund_hold_bond_latest(self, dt=None, fund_list =[]) -> pd.DataFrame:
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                if not dt:
                    dt = db_session.query(
                        func.max(FundHoldBond.datetime)
                    ).filter(
                    FundHoldBond.fund_id.in_(fund_list),
                ).one_or_none()
                    if dt:
                        dt = dt[0]
                query = db_session.query(
                    FundHoldBond
                ).filter(
                    FundHoldBond.datetime == dt,
                    FundHoldBond.fund_id.in_(fund_list),
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get time range data <err_msg> {e} from {FundHoldBond.__tablename__}')
                return

    def get_fund_hold_asset_latest(self, dt=None, fund_list = []) -> pd.DataFrame:
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                if not dt:
                    dt = db_session.query(
                        func.max(FundHoldAsset.datetime)
                    ).filter(
                    FundHoldAsset.fund_id.in_(fund_list),
                ).one_or_none()
                    if dt:
                        dt = dt[0]

                query = db_session.query(
                        FundHoldAsset
                        ).filter(
                            FundHoldAsset.datetime == dt,
                            FundHoldAsset.fund_id.in_(fund_list),
                        )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get time range data <err_msg> {e} from {FundHoldAsset.__tablename__}')
                return

    def delete_fund_hold_stock(self, date_to_delete: datetime.date, fund_list: List[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    FundHoldStock
                ).filter(
                    FundHoldStock.fund_id.in_(fund_list),
                    FundHoldStock.datetime == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {FundHoldStock.__tablename__}')
                return False

    def get_fund_hold_bond(self, dt: str = '') -> pd.DataFrame:
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundHoldBond
                )
                if dt:
                    query = query.filter(
                        FundHoldBond.datetime == dt
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get time range data <err_msg> {e} from {FundHoldBond.__tablename__}')
                return

    def get_fund_ipo_stats(self, dt: str = '') -> pd.DataFrame:
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundIPOStats
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get time range data <err_msg> {e} from {FundIPOStats.__tablename__}')
                return

    def delete_fund_hold_bond(self, date_to_delete: datetime.date, fund_list: List[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    FundHoldBond
                ).filter(
                    FundHoldBond.fund_id.in_(fund_list),
                    FundHoldBond.datetime == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {FundHoldBond.__tablename__}')
                return False

    def get_fund_stock_portfolio(self, dt: str = ''):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FundStockPortfolio
                )
                if dt:
                    query = query.filter(
                        FundStockPortfolio.datetime == dt
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get time range data <err_msg> {e} from {FundStockPortfolio.__tablename__}')
                return

    def get_fund_stock_concept(self, tag_group_id_list: List[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    StockTag
                )
                if tag_group_id_list:
                    query = query.filter(
                        StockTag.tag_group_id.in_(tag_group_id_list)
                    )
                return pd.read_sql(query.statement, query.session.bind).drop(columns=['_update_time'])
            except Exception as e:
                print(f'Failed to get_fund_stock_concept <err_msg> {e} from {StockTag.__tablename__}')
                return

    def delete_fund_rate(self, date_to_delete: datetime.date, fund_list: List[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                db_session.query(
                    FundRate
                ).filter(
                    FundRate.fund_id.in_(fund_list),
                    FundRate.datetime == date_to_delete,
                ).delete(synchronize_session=False)
                db_session.commit()
                return True
            except Exception as e:
                print(f'Failed to delete data <err_msg> {e} from {FundRate.__tablename__}')

    @staticmethod
    def get_model_data(model: Base, *params):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                        *(getattr(model, k) for k in params if hasattr(model, k))
                    )
                tag_df = pd.read_sql(query.statement, query.session.bind)
                return tag_df

            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {model.__tablename__}')

    @classmethod
    def get_fund_info_data(cls, *params):
        return cls.get_model_data(FundInfo, *params)


    def get_hedge_fund_info(self, fund_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HedgeFundInfo,
                )
                if fund_id_list:
                    query = query.filter(
                        HedgeFundInfo.fund_id.in_(fund_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_hedge_fund_info <err_msg> {e} from {HedgeFundInfo.__tablename__}')

    def get_hedge_fund_alias(self, manager_id: str, fund_id_alias: str):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HedgeFundAlias,
                ).filter(
                    HedgeFundAlias.fund_id_alias == fund_id_alias,
                    HedgeFundAlias.manager_id == manager_id,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_hedge_fund_alias <err_msg> {e} from {HedgeFundAlias.__tablename__}')

    def get_hedge_fund_nav(self, fund_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HedgeFundNAV,
                )
                if fund_id_list:
                    query = query.filter(
                        HedgeFundNAV.fund_id.in_(fund_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_hedge_fund_nav <err_msg> {e} from {HedgeFundNAV.__tablename__}')


    def delete_hedge_fund_nav(self, fund_id_to_delete: str, *, date_list: Tuple[datetime.date] = (), start_date: str = '', end_date: str = '') -> bool:
        with BasicDatabaseConnector().managed_session() as session:
            try:
                query = session.query(
                    HedgeFundNAV
                ).filter(
                    HedgeFundNAV.fund_id == fund_id_to_delete,
                )
                if date_list:
                    query = query.filter(
                        HedgeFundNAV.datetime.in_(date_list),
                    )
                if start_date:
                    query = query.filter(
                        HedgeFundNAV.datetime >= start_date,
                    )
                if end_date:
                    query = query.filter(
                        HedgeFundNAV.datetime <= end_date,
                    )
                query.delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {HedgeFundNAV.__tablename__}')
                return False


    def get_fof_info(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFInfo,
                ).filter(
                    FOFInfo.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFInfo.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_info <err_msg> {e} from {FOFInfo.__tablename__}')

    def get_fof_info_by_key_words(self, manager_id: str, key_words:Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFInfo,
                ).filter(
                    FOFInfo.manager_id == manager_id,
                )
                for key_word in key_words:
                    query = query.filter(
                        FOFInfo.fof_name.like(f'%{key_word}%')
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_info <err_msg> {e} from {FOFInfo.__tablename__}')
    
    def get_fof_info_strategy_exsit(self, manager_id:str='1', fof_id_list:Tuple[str]=(), has_nav:bool=True):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFInfo,
                ).filter(
                    FOFInfo.manager_id == manager_id,
                    FOFInfo.has_nav == has_nav,
                    FOFInfo.strategy_type.isnot(None),
                )
                if fof_id_list:
                    query = query.filter(
                        FOFInfo.fof_id.in_(fof_id_list),
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                df.strategy_type = df.strategy_type.map(lambda x:FOFStrategyTypeDic[x] )
                return df
            except Exception as e:
                print(f'failed to get_fof_info_nav_exsited <err_msg> {e} from {FOFInfo.__tablename__}')

    def get_fof_info_ignore_other_info(self, manager_id:str='1', fof_id_list:Tuple[str]=()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFInfo,
                ).filter(
                    FOFInfo.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFInfo.fof_id.in_(fof_id_list),
                    )
                df = pd.read_sql(query.statement, query.session.bind)
                df.strategy_type = df.strategy_type.map(lambda x:FOFStrategyTypeDic[x] )
                return df
            except Exception as e:
                print(f'failed to get_fof_info <err_msg> {e} from get_fof_info_ignore_other_info')

    def get_fof_asset_allocation(self, manager_id, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFAssetAllocation,
                ).filter(
                    FOFAssetAllocation.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFAssetAllocation.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_asset_allocation <err_msg> {e} from {FOFAssetAllocation.__tablename__}')


    def get_fof_scale_alteration(self, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFScaleAlteration,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFScaleAlteration.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_scale_alteration <err_msg> {e} from {FOFScaleAlteration.__tablename__}')


    def get_fof_manually(self, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFManually,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFManually.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_manually <err_msg> {e} from {FOFManually.__tablename__}')

    def get_fof_other_record(self, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFOtherRecord,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFOtherRecord.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_manually <err_msg> {e} from {FOFOtherRecord.__tablename__}')

    def get_fof_account_statement(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFAccountStatement,
                ).filter(
                    FOFAccountStatement.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFAccountStatement.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_account_statement <err_msg> {e} from {FOFAccountStatement.__tablename__}')

    def delete_fof_account_statement(self, date_to_delete: datetime.date, fof_id_list: List[str]) -> bool:
        with BasicDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFAccountStatement
                ).filter(
                    FOFAccountStatement.fof_id.in_(fof_id_list),
                    FOFAccountStatement.datetime == date_to_delete,
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFAccountStatement.__tablename__}')
                return False

    def get_fof_incidental_statement(self, manager_id, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFIncidentalStatement,
                ).filter(
                    FOFIncidentalStatement.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFIncidentalStatement.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_incidental_statement <err_msg> {e} from {FOFIncidentalStatement.__tablename__}')

    def get_fof_investor_position(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFInvestorPosition,
                ).filter(
                    FOFInvestorPosition.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFInvestorPosition.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_investor_position <err_msg> {e} from {FOFInvestorPosition.__tablename__}')

    def delete_fof_investor_position(self, manager_id: str, fof_id_to_delete: datetime.date, investor_id_list: List[str]) -> bool:
        with BasicDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFInvestorPosition
                ).filter(
                    FOFInvestorPosition.fof_id == fof_id_to_delete,
                    FOFInvestorPosition.manager_id == manager_id,
                    FOFInvestorPosition.investor_id.in_(investor_id_list),
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFInvestorPosition.__tablename__}')
                return False

    def get_fof_investor_position_summary(self, manager_id: str, investor_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFInvestorPositionSummary,
                ).filter(
                    FOFInvestorPositionSummary.manager_id == manager_id,
                )
                if investor_id_list:
                    query = query.filter(
                        FOFInvestorPositionSummary.investor_id.in_(investor_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_investor_position_summary <err_msg> {e} from {FOFInvestorPositionSummary.__tablename__}')

    def delete_fof_investor_position_summary(self, manager_id: str, investor_id: str, date_list: List[str]) -> bool:
        with BasicDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFInvestorPositionSummary
                ).filter(
                    FOFInvestorPositionSummary.manager_id == manager_id,
                    FOFInvestorPositionSummary.investor_id == investor_id,
                    FOFInvestorPositionSummary.datetime.in_(date_list),
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFInvestorPositionSummary.__tablename__}')

    def get_fof_estimate_fee(self, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFEstimateFee,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFEstimateFee.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_estimate_fee <err_msg> {e} from {FOFEstimateFee.__tablename__}')

    def delete_fof_estimate_fee(self, date_to_delete: datetime.date, fof_id_list: List[str]) -> bool:
        with BasicDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFEstimateFee
                ).filter(
                    FOFEstimateFee.fof_id.in_(fof_id_list),
                    FOFEstimateFee.date == date_to_delete,
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFEstimateFee.__tablename__}')
                return False

    def get_fof_estimate_interest(self, manager_id: str, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFEstimateInterest,
                ).filter(
                    FOFEstimateInterest.manager_id == manager_id,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFEstimateInterest.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_estimate_interest <err_msg> {e} from {FOFEstimateInterest.__tablename__}')

    def delete_fof_estimate_interest(self, date_to_delete: datetime.date, fof_id_list: List[str]) -> bool:
        with BasicDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFEstimateInterest
                ).filter(
                    FOFEstimateInterest.fof_id.in_(fof_id_list),
                    FOFEstimateInterest.date == date_to_delete,
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFEstimateInterest.__tablename__}')
                return False

    def get_fof_transit_money(self, fof_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFTransitMoney,
                )
                if fof_id_list:
                    query = query.filter(
                        FOFTransitMoney.fof_id.in_(fof_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_transit_money <err_msg> {e} from {FOFTransitMoney.__tablename__}')

    def delete_fof_transit_money(self, date_to_delete: datetime.date, fof_id_list: List[str]) -> bool:
        with BasicDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    FOFTransitMoney
                ).filter(
                    FOFTransitMoney.fof_id.in_(fof_id_list),
                    FOFTransitMoney.confirmed_datetime == date_to_delete,
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {FOFTransitMoney.__tablename__}')
                return False

    def get_fof_assert_correct(self, manager_id: str, fof_id: str):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    FOFAssertCorrect,
                ).filter(
                    FOFAssertCorrect.manager_id == manager_id,
                    FOFAssertCorrect.fof_id == fof_id,
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_assert_correct <err_msg> {e} from {FOFAssertCorrect.__tablename__}')

    def get_email_parser_code(self, p_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EMailParserCode,
                )
                if p_id_list:
                    query = query.filter(
                        EMailParserCode.id.in_(p_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_email_parser_code <err_msg> {e} from {EMailParserCode.__tablename__}')

    def get_email_parser_exec(self, manager_id: str):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    EMailParserExec,
                ).filter(
                    EMailParserExec.manager_id.in_([manager_id, None]),
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_email_parser_manager <err_msg> {e} from {EMailParserExec.__tablename__}')

    def get_hedge_fund_email_raw(self, manager_id: str, fund_id_list: List[str]):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    HedgeFundEmailRaw,
                ).filter(
                    HedgeFundEmailRaw.manager_id == manager_id,
                    HedgeFundEmailRaw.fund_id.in_(fund_id_list),
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_hedge_fund_email_raw <err_msg> {e} from {HedgeFundEmailRaw.__tablename__}')

    def get_asset_info(self, asset_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    AssetInfo,
                )
                if asset_id_list:
                    query = query.filter(
                        AssetInfo.asset_id.in_(asset_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_transit_money <err_msg> {e} from {AssetInfo.__tablename__}')

    def get_asset_info_real(self, real_id_list: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    AssetInfo,
                )
                if real_id_list:
                    query = query.filter(
                        AssetInfo.real_id.in_(real_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_transit_money <err_msg> {e} from {AssetInfo.__tablename__}')

    def get_asset_info_by_real_id_and_asset_type(self, real_id_list: Tuple[str] = (), asset_type:Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    AssetInfo,
                )
                if asset_type:
                    query = query.filter(
                        AssetInfo.asset_type.in_(asset_type),
                        AssetInfo.real_id.in_(real_id_list),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_transit_money <err_msg> {e} from {AssetInfo.__tablename__}')

    def get_asset_info_by_type(self, asset_type: Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    AssetInfo,
                )
                if asset_type:
                    query = query.filter(
                        AssetInfo.asset_type.in_(asset_type),
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_transit_money <err_msg> {e} from {AssetInfo.__tablename__}')

    def get_asset_info_by_type_by_key_words(self,asset_type: Tuple[str] = (), key_words:Tuple[str] = ()):
        with BasicDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    AssetInfo,
                )
                if asset_type:
                    query = query.filter(
                        AssetInfo.asset_type.in_(asset_type),
                    )
                for key_word in key_words:
                    query = query.filter(
                        AssetInfo.real_name.like(f'%{key_word}%')
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'failed to get_fof_transit_money <err_msg> {e} from {AssetInfo.__tablename__}')

    def get_asset_details(self):
        try:
            df = self.get_asset_info()
            asset_list = df.asset_type.unique().tolist()
            result = []
            for asset_id in asset_list:
                dic = {
                    'title':asset_id,
                    'items':[],
                }
                _df = df[df.asset_type == asset_id].drop_duplicates(subset=['asset_name'])
                for r in _df.itertuples():
                    _dic = {'id':r.asset_id,'name':r.asset_name}
                    dic['items'].append(_dic)
                result.append(dic)
            return result
        except Exception as e:
            print(f'failed to get_fof_transit_money <err_msg> {e} from {AssetInfo.__tablename__}')

    def get_product_details(self):
        try:
            '''
            df = self.get_asset_info()
            df1 = df[(df['asset_type'] == '典型产品')]
            asset_list = df1.asset_name.unique().tolist()
            result = {}
            for asset_id in asset_list:
                result[asset_id] = []
                _df = df1[df1.asset_name == asset_id]
                for r in _df.itertuples():
                    result[asset_id].append([r.real_id, r.real_name])
            '''
            fund_info = self.get_fof_info_strategy_exsit()
            # 客户专属
            special_list = ['景林资产','石锋资产','林园投资','东方港湾','万方资产']
            fund_info_1 = fund_info[~fund_info.admin.isin(special_list)]
            fund_info_2 = fund_info[fund_info.admin.isin(special_list)]
            asset_list = fund_info.strategy_type.unique().tolist()
            result = {}
            for asset_id in asset_list:
                result[asset_id] = []
                _df = fund_info_1[fund_info_1.strategy_type == asset_id]
                for r in _df.itertuples():
                    result[asset_id].append([r.fof_id, r.fof_name])
            df = self.get_asset_info()
            df2 = df[df['asset_name'].isin(['商品','大盘股','中证500','创业板指','中证800','中证1000','国债'])]
            asset_list = df2.asset_name.unique().tolist()
            dic = {'商品CFCI':'商品期货指数'}
            benchmark_tag = '*业绩基准'
            result[benchmark_tag] = []
            for r in df2.itertuples():
                result[benchmark_tag].append([r.real_id, dic.get(r.real_name,r.real_name)])
            for agency_i in special_list:
                _agency_i = f'#{agency_i}'
                result[_agency_i] = []
                _df = fund_info_2[fund_info_2.admin == agency_i]
                for r in _df.itertuples():
                    result[_agency_i].append([r.fof_id, r.fof_name])
            return result
        except Exception as e:
            print(f'failed to get_fof_transit_money <err_msg> {e} from {AssetInfo.__tablename__}')

    def get_product_benchmark(self):
        try:
            result = []
            df = self.get_asset_info()
            df = df[df['asset_name'].isin(['大盘股','中证500','创业板指','上证50'])]
            for r in df.itertuples():
                result.append([r.real_id, r.real_name])
            return result
        except Exception as e:
            print(f'failed to get_fof_transit_money <err_msg> {e} from {AssetInfo.__tablename__}')

    

    
    
    

    def get_index_and_asset_price(self, index_list, begin_date, end_date):
        try:
            index_id_list = [i for i in index_list if '-' not in i]
            asset_id_list = [i for i in index_list if '-' in i]
            index_price = pd.DataFrame()
            asset_price = pd.DataFrame()
            if len(index_id_list) > 0:
                #print(f'index_ids {index_id_list}')
                index_price = self.get_index_price_dt(index_list=index_id_list, start_date=begin_date, end_date=end_date)
                index_price = index_price.pivot_table(index='datetime',columns='index_id',values='close')
            if len(asset_id_list) > 0:
                #print(f'asset_id_list {asset_id_list}')
                asset_price = self.get_asset_price_dt_back_with_asset_id(asset_list=asset_id_list,begin_date=begin_date-datetime.timedelta(days=10),end_date=end_date)
            df = pd.concat([index_price,asset_price],join='outer', axis=1).sort_index().ffill().reindex(index_price.index)
            return df
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from basic.get_index_and_asset_price')
            return pd.DataFrame()
            
    def get_index_and_asset_name_dic(self, index_list):
        try:
            index_id_list = [i for i in index_list if '-' not in i]
            asset_id_list = [i for i in index_list if '-' in i]
            name_dic = {}
            asset_dic = {}
            if len(index_id_list) > 0:
                index_info = self.get_index_info(index_id_list)
                name_dic = index_info.set_index('index_id')['desc_name'].to_dict()
            if len(asset_id_list) > 0:
                asset_info = self.get_asset_info(asset_id_list=asset_id_list)
                asset_dic = asset_info.set_index('asset_id')['real_name'].to_dict()
                name_dic.update(asset_dic)
            return name_dic

        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from basic.get_index_and_asset_info')
            return {}

    def data_resample_monthly_nav(self, df, rule='1M'):
        df = df.set_axis(pd.to_datetime(df.index), inplace=False).resample(rule).last()
        df.index = [i.date() for i in df.index]
        df.index.name = 'datetime'
        return df
            
    def market_size_df(self,begin_date, end_date, time_para, codes=['cninfo_smallcap','cni_largec','cni_midcap']):
        try:
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            index_price = self.get_index_price_dt(start_date=begin_date,end_date=end_date,index_list=codes)
            index_info = self.get_index_info(codes)
            index_price = index_price.pivot_table(index='datetime',columns='index_id',values='close').dropna()
            dic = index_info.set_index('index_id').to_dict()['desc_name']
            index_price = index_price / index_price.iloc[0] - 1
            index_price = index_price.rename(columns=dic)
            index_price.index.name = 'datetime'
            return index_price

        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from basic.market_size_df')

    def get_main_index_future_diff_yearly(self, begin_date, end_date, time_para, codes=['EMM00597141','EMM00597142','EMM00597143']):
        try:
            
            def is_third_friday(d):
                return d.weekday() == 4 and 15 <= d.day <= 21
            # 当月连续合约换仓天数
            def this_months_ex(x):
                return exchange_dts[exchange_dts >= x][0]
            # 下月连续合约换仓天数
            def next_months_ex(x):
                return exchange_dts[exchange_dts >= datetime.date(year=x.year,month=x.month,day=28)][0]
            # 下季度连续合约换仓天数
            def this_season_ex(x):
                return exchange_dts[(exchange_dts >= x) & ([i.month in [3,6,9,12] for i in exchange_dts])][1]

            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)

            # begin_date = max(begin_date, datetime.date(2020,1,1))
            codes = ['EMM00597141','EMM00597142','EMM00597143']
            df = RawDataApi().get_stock_index_future_diff_base(begin_date,end_date,codes)
            index_price = self.get_index_price_dt(start_date=begin_date,index_list=['csi500'])
            index_price = index_price.pivot_table(columns='index_id',values='close',index='datetime')
            df = df.join(index_price)
            for code_i in codes:
                df[code_i] = df[code_i] / df.csi500

            dt1 = [i for i in df.index if is_third_friday(i)]
            dt2 = []
            for i in range(200):
                _d = df.index.values[-1] + datetime.timedelta(i)
                if is_third_friday(_d):
                    dt2.append(_d)
            exchange_dts = np.array(dt1 + dt2)
            exchange_dts = np.array([i - datetime.timedelta(days=4) for i in exchange_dts])    
                
            df.loc[:,'当月连续剩余交易日'] = df.index.map(lambda x: (this_months_ex(x) - x).days + 4)
            df.loc[:,'下月连续剩余交易日'] = df.index.map(lambda x: (next_months_ex(x) - x).days + 4)
            df.loc[:,'下季连续剩余交易日'] = df.index.map(lambda x: (this_season_ex(x) - x).days + 4)

            df['EMM00597141'] = df['EMM00597141'] * 250 / df['当月连续剩余交易日']
            df['EMM00597142'] = df['EMM00597142'] * 250 / df['下月连续剩余交易日']
            df['EMM00597143'] = df['EMM00597143'] * 250 / df['下季连续剩余交易日']

            dic = {
                        'EMM00597141':'IC当月连续年化贴水率',
                        'EMM00597142':'IC下月连续年化贴水率',
                        'EMM00597143':'IC下季连续年化贴水率',
                    }
            df = df[codes].rename(columns=dic)
            df.index.name = 'datetime'
            return df

        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from basic.get_main_index_future_diff_yearly')
    
    def get_industry_list(self):
        try:
            df = RawDataApi().get_em_industry_info(ind_class_type=1)[['em_id','ind_name']]
            em_id_list = df.em_id.to_list()
            df = self.get_index_info_by_em_id(em_id_list)
            info_list = [(r.index_id,r.desc_name.replace('(申万)','')) for r in df.itertuples()]
            return info_list
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from get_em_industry_info')
            return []

    def get_industry_price(self, begin_date, end_date, time_para, industry_list):
        try:
            begin_date, end_date = RawDataApi().get_date_range(time_para, begin_date, end_date)
            df_info = self.get_index_info(industry_list)
            info_dic = {r.index_id : r.desc_name.replace('(申万)','') for r in df_info.itertuples()}
            df = self.get_index_price_dt(start_date=begin_date,end_date=end_date,index_list=industry_list)
            df = df.pivot_table(columns='index_id',values='close',index='datetime').dropna()
            df = df / df.iloc[0]
            df = df.rename(columns=info_dic)
            return df

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from get_industry_price')
            return pd.DataFrame([])

    def industry_recent_rate(self, industry_list, year:int=None, weekly:bool=False):
        try:
            df_info = self.get_index_info(industry_list)
            desc_name_dic = {r.index_id : r.desc_name.replace('(申万)','') for r in df_info.itertuples()}
            index_price = self.get_index_price_dt(start_date='20091231',index_list=industry_list).pivot_table(index='datetime',columns='index_id',values='close')
            if year is None:
                # 年度
                index_price_y = self.data_resample_monthly_nav(index_price.bfill(),rule='12M')
                index_ret_year = index_price_y.pct_change(1).dropna()
                td = index_ret_year.index
                td = [str(i.year) for i in td]
                index_ret = index_ret_year.copy()
            else:
                index_price_m = index_price.loc[datetime.date(year-1,12,31):datetime.date(year,12,31)]
                index_price_m = self.data_resample_monthly_nav(index_price_m,rule='1M').bfill()
                index_ret_m = index_price_m.pct_change(1).dropna()
                td = index_ret_m.index
                td = [str(i.year) + str(i.month).zfill(2) for i in td ]
                index_ret = index_ret_m.copy()
            if weekly:
                index_price_w = self.data_resample_monthly_nav(index_price,rule='1W').bfill()
                index_ret = index_price_w.pct_change(1).dropna().tail(12)
                td = index_ret.index
                td = [i.strftime('%Y%m%d') for i in td]
            last_day = td[-1]
            index_ret.index = td
            index_ret = index_ret.T.sort_values(last_day, ascending=False).T
            index_ret.loc['均值',:] = index_ret.mean()
            index_ret = index_ret.round(4)*100
            index_ret = index_ret.rename(columns=desc_name_dic)
            return index_ret.T
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from basic.get_industry_recent_ret')

    def get_north_cap_data(self, begin_date, end_date, time_para, index_id):
        try:
            raw_api = RawDataApi()
            begin_date, end_date = raw_api.get_date_range(time_para, begin_date, end_date)
            index_price = self.get_index_price_dt(start_date=begin_date,end_date=end_date,index_list=[index_id])
            index_info = self.get_index_info(index_list=[index_id])
            desc_name = index_info.set_index('index_id').to_dict()['desc_name']
            desc_name['north_cap'] = '北向资金'
            north_cap = raw_api.get_north_cap(begin_date, end_date)
            index_price = index_price.pivot_table(index='datetime',values='close',columns='index_id')
            north_cap =north_cap.set_index('datetime')[['north_cap']]
            df = index_price.join(north_cap).rename(columns=desc_name)
            return df
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from basic.get_north_cap_data')

    def get_south_cap_data(self, begin_date, end_date, time_para, index_id):
        try:
            raw_api = RawDataApi()
            begin_date, end_date = raw_api.get_date_range(time_para, begin_date, end_date)
            index_price = self.get_index_price_dt(start_date=begin_date,end_date=end_date,index_list=[index_id])
            index_info = self.get_index_info(index_list=[index_id])
            desc_name = index_info.set_index('index_id').to_dict()['desc_name']
            desc_name['south_cap'] = '南向资金'
            north_cap = raw_api.get_south_cap(begin_date, end_date)
            index_price = index_price.pivot_table(index='datetime',values='close',columns='index_id')
            north_cap =north_cap.set_index('datetime')[['south_cap']]
            df = index_price.join(north_cap).rename(columns=desc_name)
            return df
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from basic.get_south_cap_data')

    def get_side_cap_index(self):
        index_list = [{'id':'sse50','name':'上证50'},{'id':'hs300','name':'沪深300'},{'id':'csi500','name':'中证500'},{'id':'csi1000','name':'中证1000'},{'id':'hsi','name':'恒生指数'}]
        return index_list

    def get_side_cap_data(self, direction, begin_date, end_date, time_para, index_id):
        try:
            if direction == '北向资金':
                return self.get_north_cap_data(begin_date, end_date, time_para, index_id).dropna()
            else:
                return self.get_south_cap_data(begin_date, end_date, time_para, index_id).dropna()
        except Exception as e:
            print(f'failed to asset price <err_msg> {e} from basic.get_side_cap_data')

    def get_ppi(self, begin_date, end_date, time_para):
        try:
            raw = RawDataApi()
            begin_date, end_date = raw.get_date_range(time_para, begin_date, end_date)
            df = raw.get_em_macroeconomic_monthly(codes=['PPI'],start_date=begin_date,end_date=end_date)
            df = df.drop(columns=['_update_time','codes']).rename(columns={'datetime':'datetime','value':'同比'})
            df.loc[:,'总增长'] = df.同比.cumsum()
            if df.shape[0] > 100:
                idxs = df.index.tolist()
                _idxs = [ i for i in idxs if i%3 == 0]
                diff = idxs[-1] - _idxs[-1]
                idxs = [i + diff for i in _idxs]
                df = df.loc[idxs]
                        
            index_price = self.get_index_price_dt(start_date=begin_date,end_date=end_date,index_list=['hs300'])
            index_price = index_price.set_index('datetime')[['close']].loc[df.datetime.values[0]:df.datetime.values[-1]]
            index_ret = round(index_price.close[-1] / index_price.close[0] - 1,3)
            text = ['反映一定时期内全部工业产品出厂价格总水平的变动趋势和变动幅度的相对数。',
                    '衡量工业企业产品出厂价格变动趋势和变动程度的指数，是反映某一时期生产领域价格变动情况的重要经济指标。',
                    '由生产成本、利润和税金三部分组成，它是工业产品进入流通领域的最初价格。',
                    '指数比预期数值高时，表明有通货膨胀的风险；指数比预期数值低时，则表明有通货紧缩的风险。']
            data = {
                'data':df,
                '沪深300总增长':index_ret,
                '介绍':text,
            }
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_ppi')
            return pd.DataFrame([])
    
    def get_pmi(self, begin_date, end_date, time_para):
        try:
            raw = RawDataApi()
            begin_date, end_date = raw.get_date_range(time_para, begin_date, end_date)
            l = ['CX_PMI','PMI','NonPMI']
            df = raw.get_em_macroeconomic_monthly(codes=l)
            info = raw.get_em_macroeconomic_info(codes=l)
            name_dic = info.set_index('codes').to_dict()['desc_name']
            name_dic['CX_PMI'] = '财新PMI'
            df = df.pivot_table(index='datetime',columns='codes',values='value').dropna().rename(columns=name_dic)
            pct_chg = lambda x: x[-1] / x[0] - 1
            df.loc[:,'财新PMI同比'] = df.财新PMI.rolling(window=13).apply(pct_chg)
            df.loc[:,'非制造业PMI同比'] = df.非制造业PMI.rolling(window=13).apply(pct_chg)
            df.loc[:,'PMI同比'] = df.PMI.rolling(window=13).apply(pct_chg)
            df = df.loc[begin_date:end_date]
            df.index.name = 'datetime'
            text = ['衡量一个国家制造业的 “体检表”，是制造业在生产、新订单、商品价格、存货、 雇员、订单交货、新出口订单和进口等八个方面状况的指数。',
                    'PMI指数50为荣枯分水线。PMI略大于50，说明经济在缓慢前进，PMI略小于50说明经济在慢慢走向衰退。']
            data = {
                'data':df,
                '介绍':text,
            }
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_pmi')
            return pd.DataFrame([])

    def get_gdp(self, begin_date, end_date, time_para):
        try:
            l = ['gdp_cum_yoy',
                'gdp_i1_c_yoy',
                'gdp_i1_s_w',
                'gdp_i2_c_yoy',
                'gdp_i2_s_w',
                'gdp_i3_c_yoy',
                'gdp_i3_s_w',
                ]
            raw = RawDataApi()
            begin_date, end_date = raw.get_date_range(time_para, begin_date, end_date)
            df = raw.get_em_macroeconomic_monthly(codes=l,start_date=begin_date,end_date=end_date)
            info = raw.get_em_macroeconomic_info(codes=l)
            desc_dic = info.set_index('codes').to_dict()['desc_name']
            df = df.pivot_table(index='datetime',columns='codes',values='value')
            df = df.rename(columns=desc_dic)
            name_dic = {
                'GDP：累计同比':'总GDP同比增速',
                'GDP第一产业累计同比':'第一产业同比增速',
                '第一产业GDP当季占比':'第一产业当季贡献',
                'GDP第二产业累计同比':'第二产业同比增速',
                '第二产业GDP当季占比':'第二产业当季贡献',
                'GDP第三产业累计同比':'第三产业同比增速',
                '第三产业GDP当季占比':'第三产业当季贡献',
            }
            df = df.rename(columns=name_dic).ffill()
            text = [
                '国内生产总值，简称GDP，是指在一定时期内（一个季度或一年），全国经济中所生产出的全部最终产品和劳务的价值。 季度更新每年4月、7月、10月、来年1月，15号左右',
                '第一产业主要指生产食材以及其它一些生物材料的产业，包括种植业、林业、畜牧业、水产养殖业等直接以自然物为生产对象的产业。',
                '第二产业主要指加工制造产业，利用自然界和第一产业提供的基本材料进行加工处理。',
                '第三产业是指第一、第二产业以外的其他行业，范围比较广泛，主要包括交通运输业、通讯产业、商业、餐饮业、金融业、教育、公共服务等非物质生产部门。',
            ]
            data = {
                'data':df,
                'text':text
            }
            return data

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_gdp')
            return pd.DataFrame([])

    def get_cpi(self, begin_date, end_date, time_para):
        try:
            l = ['CPI','CPI_mom']
            raw = RawDataApi()
            begin_date, end_date = raw.get_date_range(time_para, begin_date, end_date)
            df = raw.get_em_macroeconomic_monthly(codes=l,start_date=begin_date,end_date=end_date)
            df = df.pivot_table(columns='codes',values='value',index='datetime').dropna()
            _df = (df['CPI_mom']/100 + 1).cumprod()
            df.loc[:,'CPI估算指数'] = _df / _df.iloc[0]
            df = df.drop(columns=['CPI_mom'])
            index_price = BasicDataApi().get_index_price_dt(start_date=df.index[0],end_date=df.index[-1],index_list=['hs300'])
            index_price = index_price.pivot_table(index='datetime',values='close',columns='index_id')
            index_price = index_price.reindex(index_price.index.union(df.index).sort_values()).ffill()
            df = df.join(index_price).dropna().rename(columns={'hs300':'沪深300'}).round(2)
            text = ['消费者物价指数（consumer price index），又名居民消费价格指数，简称CPI。',
                    '反映居民家庭购买的消费品和服务项目的价格水平变动情况，通常作为观察通货膨胀水平的重要指标。',
                    '由以下8大类构成：食品烟酒、衣着、居住、生活用品及服务、交通和通信、教育文化和娱乐、医疗保健、其他用品和服务。',]
            data = {
                'data':df,
                'text':text,
            }
            
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_cpi')
            return pd.DataFrame([])

    def get_ah_prem(self, begin_date, end_date, time_para, frequency):
        try:
            raw = RawDataApi()
            index_id = 'em_ah_prem'
            begin_date, end_date = raw.get_date_range(time_para, begin_date, end_date)
            index_price = BasicDataApi().get_index_price_dt(start_date=begin_date,end_date=end_date,index_list=[index_id])
            index_price = index_price.set_index('datetime')[['open','high','low','close']]
            title = 'AH股溢价指数'
            if frequency != '1D':
                index_price = index_price.set_axis(pd.to_datetime(index_price.index), inplace=False).resample(frequency).last()
                index_price.index = [i.date() for i in index_price.index]
                index_price.index.name = 'datetime'
            
            index_price.loc[:,'MA5'] = index_price.close.rolling(window=5,min_periods=1).mean() 
            index_price.loc[:,'MA10'] = index_price.close.rolling(window=10,min_periods=1).mean() 
            index_price.loc[:,'MA30'] = index_price.close.rolling(window=30,min_periods=1).mean() 
            index_price.loc[:,'MA60'] = index_price.close.rolling(window=60,min_periods=1).mean() 
            data = {
                'data':index_price,
                'title':title
            }
            return data

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_ah_prem')
            return pd.DataFrame([])

    def get_us_bond_rate(self, begin_date, end_date, time_para):
        try:
            rate_dic = {
                'US_TB_10Y':'美国十年期国债收益率',
                'US_TB_2Y':'美国两年期国债收益率',
                'US_TB_3M':'美国三月期国债收益率',
                'US_TB_5Y':'美国五年期国债收益率',
                'TB_10Y':'中国十年国债收益率',
                'TB_1Y':'中国一年国债收益率',
                'TB_3Y':'中国三年国债收益率',
                'TB_5Y':'中国五年国债收益率',
            }
            raw = RawDataApi()
            begin_date, end_date = raw.get_date_range(time_para, begin_date, end_date)
            us_debt = raw.get_em_macroeconomic_daily(codes=rate_dic.keys(),start_date=begin_date, end_date=end_date)
            df = us_debt.pivot_table(index='datetime',values='value',columns='codes').dropna()
            df = df.rename(columns=rate_dic)
            df.index.name = 'datetime'
            data = {
                'data':df,
                'text':['选取美国和中国国债名义利率']
            }
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_us_bond_rate')
            return pd.DataFrame([])

    def get_usd_index(self, begin_date, end_date, time_para):
        try:
            raw = RawDataApi()
            begin_date, end_date = raw.get_date_range(time_para, begin_date, end_date)
            rates = RawDataApi().get_raw_cm_index_price_df(start_date=begin_date,end_date=end_date)
            rates = rates[['datetime','usd_central_parity_rate']].rename(columns={'usd_central_parity_rate':'美元人民币汇率'})
            data = {
                'data':rates,
                'text':['选取中美汇率中间价'],
            }
            return data
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_usd_index')
            return pd.DataFrame([])
    
    def get_rzrqye(self, begin_date, end_date, time_para):
        try:
            raw = RawDataApi()
            begin_date, end_date = raw.get_date_range(time_para, begin_date, end_date)
            code_list = ['rq_ye','rz_ye']
            asset_info = raw.get_em_macroeconomic_info(codes=code_list)
            df = raw.get_em_macroeconomic_daily(codes=code_list,start_date=begin_date,end_date=end_date)
            df = df.pivot_table(index='datetime',columns='codes',values='value')
            df = df.rename(columns=asset_info.set_index('em_codes').to_dict()['desc_name'])
            df = df/1e8
            index_list = ['hs300','csi500','csi1000']
            index_info = BasicDataApi().get_index_info(index_list=index_list)
            index_price = BasicDataApi().get_index_price_dt(start_date=begin_date, end_date=end_date, index_list=index_list)
            index_price = index_price.pivot_table(index='datetime',columns='index_id',values='total_turnover').ffill()
            index_price = index_price.dropna()
            index_name = index_info.set_index('index_id').to_dict()['desc_name']
            index_price = index_price.rename(columns=index_name)/1e8
            index_price = index_price.set_axis(pd.to_datetime(index_price.index), inplace=False).resample('W-FRI').sum()
            index_price.index = [i.date() for i in index_price.index]
            index_price.index.name = 'datetime'
            index_price = index_price.join(df).dropna()
            data = {
                'data':index_price,
                'text':['股指交易量是周度加和,单位亿元'],
            }
            return data

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_rzrqye')
            return pd.DataFrame([])

    def _get_asset_benchmark_info_list(self):
        try:
            index_info = self.get_index_info()
            l = ['恒生指数有限公司', '巨潮资讯', '中证指数有限公司','深圳证券信息有限公司', '深圳证券交易所', '上海证券交易所',
                '东方财富','标准普尔公司','上海申银万国证券研究所有限公司']
            index_info = index_info[index_info.maker_name.isin(l)]
            result = [[r.index_id, r.desc_name] for r in index_info[['index_id','desc_name']].itertuples()]
            return result

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_asset_benchmark_info_list')
            return []

    def get_asset_benchmark_info_list(self):
        try:
            asset_type_list = ['大类资产', '期货指数', '其他地区', '行业指数', '市场指数', '策略指数', '股票指数',
                '风格指数', '主题指数']
            asset_info = BasicDataApi().get_asset_info_by_type(asset_type=asset_type_list)
            index_info = BasicDataApi().get_index_info(index_list=asset_info.real_id.tolist())
            existed_id_info = asset_info[asset_info.real_id.isin(index_info.index_id)].copy()
            not_exsited_if_info = asset_info[~asset_info.real_id.isin(index_info.index_id)]
            index_info.loc[:,'others'] = index_info.desc_name +'(' + index_info.em_id + ')'
            index_others_dic = index_info.set_index('index_id')['others'].dropna().to_dict()
            index_desc_dic = index_info.set_index('index_id')['desc_name'].to_dict()
            existed_id_info.loc[:,'others'] = existed_id_info.real_id.map(lambda x: index_others_dic[x] if x in index_others_dic else index_desc_dic[x])
            result1 = [[r.real_id, r.others] for r in existed_id_info.itertuples()]
            result2 = [[r.asset_id, r.real_name] for r in not_exsited_if_info.itertuples()]
            result = result1+result2
            return result

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_asset_benchmark_info_list')
            return []
        
    def get_asset_benchmark_info_with_layers(self):
        try:
            asset_type_list = ['大类资产', '期货指数', '其他地区', '行业指数', '市场指数', '策略指数', '股票指数',
                '风格指数', '主题指数']
            asset_info = BasicDataApi().get_asset_info_by_type(asset_type=asset_type_list)
            index_info = BasicDataApi().get_index_info(index_list=asset_info.real_id.tolist())
            existed_id_info = asset_info[asset_info.real_id.isin(index_info.index_id)].copy()
            not_exsited_if_info = asset_info[~asset_info.real_id.isin(index_info.index_id)]
            index_info.loc[:,'others'] = index_info.desc_name +'(' + index_info.em_id + ')'
            index_others_dic = index_info.set_index('index_id')['others'].dropna().to_dict()
            index_desc_dic = index_info.set_index('index_id')['desc_name'].to_dict()
            existed_id_info.loc[:,'others'] = existed_id_info.real_id.map(lambda x: index_others_dic[x] if x in index_others_dic else index_desc_dic[x])
            existed_dic = {
                'real_id':'id',
                'others':'name',
                'asset_type':'asset_type',
            }
            existed_id_info = existed_id_info[existed_dic.keys()].rename(columns=existed_dic)
            not_existed_dic = {
                'asset_id':'id',
                'real_name':'name',
                'asset_type':'asset_type'
            }
            not_exsited_if_info = not_exsited_if_info[not_existed_dic.keys()].rename(columns=not_existed_dic)
            asset_info = pd.concat([existed_id_info,not_exsited_if_info])
            asset_types = asset_info.asset_type.unique().tolist()
            _result = []
            for i in asset_types:
                dic = {
                    'title':i
                }
                _df_i = asset_info[asset_info.asset_type == i]
                _res_details = []
                for r in _df_i.itertuples():
                    _dic = {'asset_id':r.id, 'desc_name':r.name}
                    _res_details.append(_dic)
                dic['items'] = _res_details
                _result.append(dic)
            return _result
            
        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_asset_benchmark_info_with_layers')
            return []

    def get_asset_name(self, id_list:list=[]):
        try:
            hf_fund_info = self.get_fof_info_strategy_exsit(fof_id_list=id_list)
            fund_info = self.get_fund_info(fund_list=id_list)
            index_info = self.get_index_info(index_list=id_list)
            name_dic = {}
            if not hf_fund_info.empty:
                d1 = hf_fund_info.set_index('fof_id')['fof_name'].to_dict()
                name_dic.update(d1)
            if not fund_info.empty:
                d2 = fund_info.set_index('fund_id')['desc_name'].to_dict()
                name_dic.update(d2)
            if not index_info.empty:
                d3 = index_info.set_index('index_id')['desc_name'].to_dict()
                name_dic.update(d3)
            return name_dic

        except Exception as e:
            print(f'Failed to get data <err_msg> {e} from basic.get_asset_name')
            return {}

    def delete_hedge_fund_email_raw(self, manager_id: str, fof_id: str, fund_id: str, date_list: List[datetime.date]) -> bool:
        with BasicDatabaseConnector().managed_session() as session:
            try:
                session.query(
                    HedgeFundEmailRaw
                ).filter(
                    HedgeFundEmailRaw.manager_id == manager_id,
                    HedgeFundEmailRaw.fof_id == fof_id,
                    HedgeFundEmailRaw.fund_id == fund_id,
                    HedgeFundEmailRaw.datetime.in_(date_list),
                ).delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                print(f'failed to delete data <err_msg> {e} from {HedgeFundEmailRaw.__tablename__}')
                return False
