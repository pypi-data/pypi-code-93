
import datetime
import traceback
import pandas as pd
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.query import BatchQuery

from ...api.raw import RawDataApi
from ....constant import IndexPriceSource
from ...api.basic import BasicDataApi
from ...view.cas.realtime_index_price import RealtimeIndexPrice
from ...view.cas.realtime_index_price_snapshot import RealtimeIndexPriceSnapshot


class RealtimeIndexPriceProcessor(object):

    def init(self):
        try:
            today = datetime.datetime.today().strftime('%Y-%m-%d')
            trading_day_list = BasicDataApi().get_trading_day_list(start_date=today, end_date=today)
            if trading_day_list is None or trading_day_list.empty:
                print(f'Today {today} is not trading day!')
                return False
                
            last_trading_day = BasicDataApi().get_last_trading_day()
            print(f'last_trading_day: {last_trading_day}')
            if not last_trading_day:
                print(f'Cannot find last trading day!')
                return False

            index_info_df = BasicDataApi().get_index_info()
            if index_info_df is None:
                print('Failed to get index list')
                return False
            index_info_df = index_info_df[index_info_df.price_source == IndexPriceSource.default]
            self.index_ids = set(index_info_df.em_id.to_list())
            self.index_ids.discard(None)

            self.index_id_mapping = self.load_index_id_mapping(index_info_df)

            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def load_index_id_mapping(self, index_info_df):
        index_id_mapping = {}
        for row in index_info_df.itertuples(index=False):
            if not row.em_id:
                continue
            index_id_mapping[row.em_id] = row.index_id
        return index_id_mapping

    def load_realtime_index_price(self, realtime_index_price_df):
        if realtime_index_price_df is None or realtime_index_price_df.empty:
            return None

        realtime_index_price = {}
        for row in realtime_index_price_df.itertuples(index=False):
            realtime_index_price[row.em_id] = row.price
        return realtime_index_price

    def calc_realtime_index_price(self, realtime_index_price_df, curr_datetime):
        try:
            realtime_index_price = self.load_realtime_index_price(realtime_index_price_df)
            if not realtime_index_price:
                return False

            results = []
            results_snapshot = {}
            for em_id, price in realtime_index_price.items():
                if em_id not in self.index_id_mapping:
                    continue

                results.append([self.index_id_mapping[em_id], price, curr_datetime])
                results_snapshot[self.index_id_mapping[em_id]] = price

                if len(results) >= 200:
                    # Write Cassandra DB
                    with BatchQuery() as batch:
                        for res in results:
                            RealtimeIndexPrice.objects(index_id=res[0]).batch(batch).update(
                                prices__append = [res[1]],
                                timestamps__append = [res[2]],
                            )
                    results = []
            
            if results:
                # Write Cassandra DB
                with BatchQuery() as batch:
                    for res in results:
                        RealtimeIndexPrice.objects(index_id=res[0]).batch(batch).update(
                            prices__append = [res[1]],
                            timestamps__append = [res[2]],
                        )

            RealtimeIndexPriceSnapshot().create(
                ts = curr_datetime,
                index_prices = results_snapshot
            )

        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def dump_index_list(self):
        '''
        Utility function
        '''
        import time
        import datetime
        import pandas as pd

        from ....util.config import SurfingConfigurator
        from ...view.raw_models import EmRealtimeIndexPrice
        from ...wrapper.mysql import RawDatabaseConnector
        from ...api.basic import BasicDataApi
        from ..raw.raw_data_helper import RawDataHelper
        from ..raw.em_raw_data_downloader import EmRawDataDownloader

        with RawDatabaseConnector().managed_session() as db_session:
            query = db_session.query(
                EmRealtimeIndexPrice.em_id
            )
            df = pd.read_sql(query.statement, query.session.bind)
        print(df)
        index_ids = set(df.em_id.to_list())
        print(index_ids)

        index_info_df = BasicDataApi().get_index_info().reset_index()
        index_id_mapping = {}
        realtime = pd.DataFrame(columns=['index_id', 'desc_name', 'is_select', 'em_id'])
        count_realtime = 0
        others = pd.DataFrame(columns=['index_id', 'desc_name', 'is_select', 'em_id'])
        count_others = 0
        for row in index_info_df.itertuples(index=False):
            if row.em_id in index_ids:
                realtime.loc[count_realtime] = [row.index_id, row.desc_name, row.is_select, row.em_id]
                count_realtime += 1
            else:
                others.loc[count_others] = [row.index_id, row.desc_name, row.is_select, row.em_id]
                count_others += 1

        realtime.to_excel('./realtime_index.xlsx')
        others.to_excel('./other_index.xlsx')