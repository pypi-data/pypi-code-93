import pandas as pd
import traceback
from ...wrapper.mysql import DerivedDatabaseConnector, ViewDatabaseConnector, BasicDatabaseConnector
from ...view.view_models import AutomaticInvestmentCollection
from ...view.derived_models import FundAIC
from ...view.basic_models import FundInfo
class AICDailyCollectionProcessor(object):

    def get_fund_df(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    FundInfo.fund_id,
                    FundInfo.structure_type
                )
                funds = pd.read_sql(query.statement, query.session.bind)
                return funds
            except Exception as e:
                print('Failed fill get data <err_msg> {}'.format(e))

    def get_fund_aic(self):
        # 只选择非分级基金和分级基金母基金
        fund_info = self.get_fund_df()
        fund_list = fund_info[fund_info.structure_type <= 1].fund_id.tolist()
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                latest_time = mn_session.query(FundAIC).order_by(FundAIC.datetime.desc()).limit(1).one_or_none()
                latest_time = latest_time.datetime
                print(latest_time)
                query = mn_session.query(
                    FundAIC.fund_id,
                    FundAIC.datetime,
                    FundAIC.y1_ret,
                    FundAIC.y3_ret,
                    FundAIC.y5_ret,
                    FundAIC.intel_y1_ret,
                    FundAIC.intel_y3_ret,
                    FundAIC.intel_y5_ret,
                ).filter(FundAIC.datetime==latest_time,
                        FundAIC.fund_id.in_(fund_list))
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns={
                    'datetime': 'price_time',
                })
                return df
            except Exception as e:
                print('Failed get_index_volatility <err_msg> {}'.format(e))

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

    def collection_daily_aic(self):
        try:
            print('1、 load data...')
            df = self.get_fund_aic()

            self.append_data(AutomaticInvestmentCollection.__tablename__, df)
            print(df)
            print('AIC success')
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def process(self):
        failed_tasks = []
        if not self.collection_daily_aic():
            failed_tasks.append('collection_daily_aic')
        return failed_tasks


if __name__ == '__main__':
    AICDailyCollectionProcessor().collection_daily_aic()
