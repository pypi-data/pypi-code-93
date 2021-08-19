
import datetime
import traceback
import pandas as pd
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.query import BatchQuery

from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...view.cas.fund_estimated_nav import FundEstimatedNav


class FundEstimatedNavProcessor(object):

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

            self.fund_stock = self.load_fund_stock()
            self.fund_nav_last_trading_day = self.load_fund_nav(last_trading_day)
            self.stock_price_last_trading_day = self.load_stock_price(last_trading_day)
            self.stock_list = self.get_stock_list(self.stock_price_last_trading_day)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def get_stock_list(self, stock_price):
        stock_set = set()
        for stock_id in stock_price.keys():
            stock_set.add(stock_id)
        return list(stock_set)

    def load_fund_stock(self):
        fund_stock_df = BasicDataApi().get_fund_hold_stock()
        # print(f'fund_stock_df\n {fund_stock_df}')
        fund_stock_info_list = [
            (
                fund_stock_df.columns.get_loc(f'rank{i}_stock_code'), 
                fund_stock_df.columns.get_loc(f'rank{i}_stockweight')
            ) for i in range(1,11,1)
        ]
        datetime_idx = fund_stock_df.columns.get_loc('datetime')
        fund_stock = {}
        fund_datetime = {}
        for row in fund_stock_df.itertuples(index=False):
            stock_info = []
            for fund_stock_info in fund_stock_info_list:
                if not row[fund_stock_info[0]]:
                    break
                stock_info.append([row[fund_stock_info[0]], row[fund_stock_info[1]]])
            if not stock_info:
                continue
            dt = row[datetime_idx]
            if row.fund_id not in fund_datetime or fund_datetime[row.fund_id] < dt:
                fund_datetime[row.fund_id] = dt
                fund_stock[row.fund_id] = stock_info
        return fund_stock

    def load_fund_nav(self, dt):
        fund_nav_df = BasicDataApi().get_fund_nav(dt=dt)
        # print(f'fund_nav_df\n {fund_nav_df}')
        fund_nav = {}
        for row in fund_nav_df.itertuples(index=False):
            fund_nav[row.fund_id] = [row.unit_net_value, row.acc_net_value, row.adjusted_net_value]
        return fund_nav

    def load_stock_price(self, dt):
        em_stock_price_df = RawDataApi().get_em_stock_price(dt, dt, columns=['close'])
        # print(f'em_stock_price_df\n {em_stock_price_df}')
        stock_price = {}
        for row in em_stock_price_df.itertuples(index=False):
            stock_price[row.stock_id] = row.close
        return stock_price

    def rq_stock_code_to_em(self, rq_stock_code):
        if not rq_stock_code:
            return None
        em_stock_code = rq_stock_code.replace("XSHG", "SH")
        em_stock_code = rq_stock_code.replace("XSHE", "SZ")
        return em_stock_code

    def load_stock_minute(self, stock_minute_df, use_sina_data):
        if stock_minute_df is None or stock_minute_df.empty:
            return None

        stock_minute = {}
        for row in stock_minute_df.itertuples(index=False):
            if use_sina_data:
                em_stock_code = row.stock_id
            else:
                em_stock_code = self.rq_stock_code_to_em(row.order_book_id)
                
            if not em_stock_code:
                continue
            stock_minute[em_stock_code] = row.close
        return stock_minute

    def delta_estimated(self, stock_weight, stock_price_last_trading_day, stock_price_now):
        return stock_weight / 100.0 * (stock_price_now / stock_price_last_trading_day - 1)

    def calc_fund_estimated_nav(self, stock_minute_df, curr_datetime, use_sina_data):
        try:
            stock_minute_parse_result = self.load_stock_minute(stock_minute_df, use_sina_data)
            if not stock_minute_parse_result:
                return False
            stock_minute = stock_minute_parse_result

            results = []
            for fund_id, stock_list in self.fund_stock.items():
                if fund_id not in self.fund_nav_last_trading_day:
                    continue

                ratio = 1.0
                for stock in stock_list:
                    if stock[0] not in self.stock_price_last_trading_day or stock[0] not in stock_minute:
                        continue
                    curr_stock_price_last_trading_day = self.stock_price_last_trading_day[stock[0]]
                    curr_stock_price_now = stock_minute[stock[0]]

                    # TODO: this stock component weight is not evaluated at last_trading_day!!!
                    # TODO: re-calc stock component weight for last_trading_day to get a more accurate estimation!
                    ratio += self.delta_estimated(
                        stock[1], curr_stock_price_last_trading_day, curr_stock_price_now)

                unit_net_value_estimated = self.fund_nav_last_trading_day[fund_id][0] * ratio
                acc_net_value_estimated = self.fund_nav_last_trading_day[fund_id][1] * ratio
                adjusted_net_value_estimated = self.fund_nav_last_trading_day[fund_id][2] * ratio
                
                results.append([fund_id, unit_net_value_estimated, acc_net_value_estimated, adjusted_net_value_estimated, curr_datetime])

                if len(results) >= 200:
                    # Write Cassandra DB
                    with BatchQuery() as batch:
                        for res in results:
                            FundEstimatedNav.objects(fund_id=res[0]).batch(batch).update(
                                unit_net_values__append = [res[1]],
                                acc_net_values__append = [res[2]],
                                adjusted_net_values__append = [res[3]],
                                timestamps__append = [res[4]],
                            )
                    results = []
            
            if results:
                # Write Cassandra DB
                with BatchQuery() as batch:
                    for res in results:
                        FundEstimatedNav.objects(fund_id=res[0]).batch(batch).update(
                            unit_net_values__append = [res[1]],
                            acc_net_values__append = [res[2]],
                            adjusted_net_values__append = [res[3]],
                            timestamps__append = [res[4]],
                        )
            # result_df = pd.DataFrame(results, columns = ['fund_id', 'unit_net_value', 'acc_net_value', 'adjusted_net_value', 'datetime']) 
            # print(result_df)
            # self._data_helper._upload_basic(result_df, FundEstimatedNav.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False


if __name__ == '__main__':
    fp = FundEstimatedNavProcessor()
    if fp.init():
        fp.run()
