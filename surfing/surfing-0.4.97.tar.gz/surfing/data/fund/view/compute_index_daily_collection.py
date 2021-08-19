import pandas as pd
import traceback
import datetime
from collections import Iterable
from sqlalchemy import distinct, func
from cassandra.cqlengine.query import BatchQuery
from ...wrapper.mysql import DerivedDatabaseConnector, BasicDatabaseConnector, ViewDatabaseConnector
from ...view.view_models import IndexDailyCollection
from ...view.basic_models import IndexInfo, IndexPrice, IndexComponent
from ...view.derived_models import IndexValuationLongTerm, IndexReturn, IndexVolatility
from ....util.calculator import Calculator as SurfingCalculator
from ...view.cas.tag_method_index_level import TagMethodIndexLevel
from ....data.api.derived import DerivedDataApi
from ....constant import SectorType

class IndexDailyCollectionProcessor(object):
    def get_index_volatility(self):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                latest_time = mn_session.query(IndexVolatility).order_by(IndexVolatility.datetime.desc()).limit(1).one_or_none()
                latest_time = latest_time.datetime
                print(latest_time)
                query = mn_session.query(
                    IndexVolatility.index_id,
                    IndexVolatility.datetime,
                    IndexVolatility.w1_vol,
                    IndexVolatility.m1_vol,
                    IndexVolatility.m3_vol,
                    IndexVolatility.m6_vol,
                    IndexVolatility.y1_vol,
                    IndexVolatility.y3_vol,
                    IndexVolatility.y5_vol,
                    IndexVolatility.y10_vol,
                    IndexVolatility.this_y_vol,
                    IndexVolatility.cumulative_vol,
                ).filter(IndexVolatility.datetime==latest_time)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns={'datetime': 'vol_datetime'})
                df = df.set_index('index_id')
                return df
            except Exception as e:
                print('Failed get_index_volatility <err_msg> {}'.format(e))

    # TODO: Use basic.index_valuation_develop table
    def get_index_valuation(self):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                latest_time = mn_session.query(IndexValuationLongTerm).order_by(IndexValuationLongTerm.datetime.desc()).limit(1).one_or_none()
                latest_time = latest_time.datetime
                print(latest_time)
                query = mn_session.query(
                    IndexValuationLongTerm.index_id,
                    IndexValuationLongTerm.pb_mrq,
                    IndexValuationLongTerm.pe_ttm,
                    IndexValuationLongTerm.peg_ttm,
                    IndexValuationLongTerm.roe,
                    IndexValuationLongTerm.dy,
                    IndexValuationLongTerm.pe_pct,
                    IndexValuationLongTerm.pb_pct,
                    IndexValuationLongTerm.ps_pct,
                    IndexValuationLongTerm.val_score,
                    IndexValuationLongTerm.datetime,
                    IndexValuationLongTerm.est_peg,
                    IndexValuationLongTerm.liqmv,
                ).filter(IndexValuationLongTerm.datetime==latest_time)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.set_index('index_id')
                return df

            except Exception as e:
                print('Failed get_index_valuation <err_msg> {}'.format(e))

    def get_index_return(self):
        with DerivedDatabaseConnector().managed_session() as mn_session:
            try:
                latest_time = mn_session.query(IndexReturn).order_by(IndexReturn.datetime.desc()).limit(1).one_or_none()
                latest_time = latest_time.datetime
                print(latest_time)
                query = mn_session.query(
                    IndexReturn.index_id,
                    IndexReturn.datetime,
                    IndexReturn.w1_ret,
                    IndexReturn.m1_ret,
                    IndexReturn.m3_ret,
                    IndexReturn.m6_ret,
                    IndexReturn.y1_ret,
                    IndexReturn.y3_ret,
                    IndexReturn.y5_ret,
                    IndexReturn.y10_ret,
                    IndexReturn.this_y_ret,
                    IndexReturn.cumulative_ret,
                ).filter(IndexReturn.datetime==latest_time)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns={'datetime': 'ret_datetime'})
                df = df.set_index('index_id')
                return df

            except Exception as e:
                print('Failed get_index_return<err_msg> {}'.format(e))

    def get_index_info(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    IndexInfo.index_id,
                    IndexInfo.em_id,
                    IndexInfo.industry_tag,
                    IndexInfo.tag_method,
                    IndexInfo.desc_name,
                    IndexInfo.is_select,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.set_index('index_id')
                return df

            except Exception as e:
                print('Failed get_index_info<err_msg> {}'.format(e))

    def get_index_component(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    IndexComponent.index_id,
                    IndexComponent.id_cat,
                )
                df = pd.read_sql(query.statement, query.session.bind)
                df['id_cat'] = df['id_cat'].transform(lambda x: SectorType(x).name)
                df = df.set_index('index_id')
                return df

            except Exception as e:
                print('Failed get_index_info<err_msg> {}'.format(e))

    def get_index_price(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                subq = mn_session.query(
                    IndexPrice.index_id.label('temp_id'),
                    func.max(IndexPrice.datetime).label('temp_date'),
                ).group_by(IndexPrice.index_id).subquery()
                query = mn_session.query(
                    IndexPrice.index_id,
                    IndexPrice.datetime,
                    IndexPrice.volume,
                    IndexPrice.low,
                    IndexPrice.close,
                    IndexPrice.high,
                    IndexPrice.open,
                    IndexPrice.ret,
                    IndexPrice.total_turnover
                ).filter(
                    IndexPrice.index_id == subq.c.temp_id,
                    IndexPrice.datetime == subq.c.temp_date
                )
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns={'datetime': 'price_datetime'})
                df = df.set_index('index_id')
                return df

            except Exception as e:
                print('Failed get_index_price<err_msg> {}'.format(e))

    def get_index_price_start_end_date(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                query = mn_session.query(
                    IndexPrice.index_id,
                    IndexPrice.datetime,
                    IndexPrice.close)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.pivot_table(index='datetime',values='close',columns='index_id')
                result = []
                for index_id in df:
                    _df = df[[index_id]].dropna()
                    dic = {
                        'index_id':index_id,
                        'price_begin_date':_df.index[0],
                        'price_end_date':_df.index[-1]
                    }
                    result.append(dic)
                df = pd.DataFrame(result).set_index('index_id')
                return df
                
            except Exception as e:
                print('Failed get_index_price_start_end_date<err_msg> {}'.format(e))

    def calc_percentile(self, df):
        def helper(x, temp_df, column):
            temp_df = temp_df[temp_df['index_id'] == x]
            ret = temp_df[column].quantile([0, .3, .7, 1])
            return ret

        start_date = datetime.datetime.now().date() - datetime.timedelta(days=3700)
        with DerivedDatabaseConnector().managed_session() as mn_session:
            query = mn_session.query(
                IndexValuationLongTerm.pe_ttm,
                IndexValuationLongTerm.pb_mrq,
                IndexValuationLongTerm.index_id
            ).filter(
                IndexValuationLongTerm.datetime >= start_date,
            )
            pe_pb_df = pd.read_sql(query.statement, query.session.bind)

        dff = df['index_id'].apply(helper, args=(pe_pb_df, 'pe_ttm',))
        df['pe_0_percentile'] = dff[0.0]
        df['pe_30_percentile'] = dff[0.3]
        df['pe_70_percentile'] = dff[0.7]
        df['pe_100_percentile'] = dff[1.0]

        dff = df['index_id'].apply(helper, args=(pe_pb_df, 'pb_mrq',))
        df['pb_0_percentile'] = dff[0.0]
        df['pb_30_percentile'] = dff[0.3]
        df['pb_70_percentile'] = dff[0.7]
        df['pb_100_percentile'] = dff[1.0]
        return df

    def get_index_yesterday_price(self):
        with BasicDatabaseConnector().managed_session() as mn_session:
            try:
                yest_time = mn_session.query(
                    distinct(IndexPrice.datetime)
                ).order_by(
                    IndexPrice.datetime.desc()
                ).offset(1).limit(1).one_or_none()
                yest_time = yest_time[0]
                print(yest_time)
                query = mn_session.query(
                    IndexPrice.index_id,
                    IndexPrice.close,
                ).filter(IndexPrice.datetime==yest_time)
                df = pd.read_sql(query.statement, query.session.bind)
                df = df.rename(columns={
                    'close': 'yest_close',
                })
                df = df.set_index('index_id')
                return df

            except Exception as e:
                print('Failed get_index_price<err_msg> {}'.format(e))

    def index_level_save_to_cas(self, items):
        groups = [i for i in range(0, len(items), 100)]
        for i in groups:
            if i != groups[-1]:
                end = i + 100
            else:
                end = len(items)
            for item in items[i: end]:
                with BatchQuery() as batch:
                    TagMethodIndexLevel.batch(batch).create(
                        index_id=item.get('index_id'),
                        data=item.get('data'),
                        update_time=datetime.datetime.now(),
                    )

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

    def replace_datetime(self, obj):
        if type(obj) == str:
            return obj

        if type(obj) == dict:
            r = {}
            for key in obj:
                r[key] = self.replace_datetime(obj[key])
            return r

        if isinstance(obj, Iterable):
            return list(map(lambda x: self.replace_datetime(x), obj))

        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')

        return obj

    def get_index_val_level(self, df):
        val_level = []
        for x in df.itertuples():
            if x.tag_method == '':
                val_level.append(None)
            else:
                val_level.append(SurfingCalculator.get_val_level(x))
        df['val_level'] = val_level
        return df

    def collection_daily_index(self):
        try:
            print('1、 load data...')
            info = self.get_index_info()
            vol = self.get_index_volatility().reindex(info.index)
            ret = self.get_index_return().reindex(info.index)
            val = self.get_index_valuation().reindex(info.index)
            price = self.get_index_price().reindex(info.index)
            yest_price = self.get_index_yesterday_price().reindex(info.index)
            component = self.get_index_component().reindex(info.index)

            print('2、 concat data...')
            df = pd.concat([info, vol, ret, val, price, yest_price, component], axis=1, sort=False)
            df.index.name = 'index_id'
            df = df.reset_index()

            print('3、 calculate tag_method index level')
            items = []
            for i in df.index:
                if not df.loc[i, 'tag_method']:
                    d = []
                else:
                    d = SurfingCalculator().get_index_level_index_by_tag_method(
                        df.loc[i, 'index_id'],
                        df.loc[i, 'tag_method'],
                    )
                items.append({
                    'index_id': df.loc[i, 'index_id'],
                    'data': self.replace_datetime(d)
                })

            self.index_level_save_to_cas(items)

            print('4、 special option...')

            df['order_book_id'] = df['em_id'].apply(lambda x: x.split('.')[0] if (x and x != 'not_available') else None)
            df = df.drop(['em_id'], axis=1)
            df['industry_tag'] = df['industry_tag'].apply(lambda x: x if x != 'not_available' else None)
            df = self.calc_percentile(df)
            df = self.get_index_val_level(df)

            self.append_data(IndexDailyCollection.__tablename__, df)

            print(df)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def process(self):
        failed_tasks = []
        if not self.collection_daily_index():
            failed_tasks.append('collection_daily_index')
        return failed_tasks


if __name__ == '__main__':
    IndexDailyCollectionProcessor().collection_daily_index()
