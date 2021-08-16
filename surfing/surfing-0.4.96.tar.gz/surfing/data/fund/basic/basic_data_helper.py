
from collections import defaultdict
import time
import datetime
import pandas as pd

from sqlalchemy.orm import sessionmaker
from ...view.basic_models import IndexInfo, StyleAnalysisStockFactor
from ...wrapper.mysql import BasicDatabaseConnector
from ...api.basic import BasicDataApi


def update_index_info_column():
    '''更新index_info中em_id列的值'''

    def modify_func(order_book_id: str) -> str:
        e = order_book_id.split('.')
        if len(e) < 2:
            return e

        if e[1] == 'XSHG':
            return e[0]+'.'+'SH'
        elif e[1] == 'XSHE':
            return e[0]+'.'+'SZ'
        else:
            return e

    Session = sessionmaker(BasicDatabaseConnector().get_engine())
    db_session = Session()
    for row in db_session.query(IndexInfo).filter(IndexInfo.tag_method.in_(['PE百分位', 'PB百分位', 'PS百分位'])).all():
        row.em_id = modify_func(row.order_book_id)
    db_session.commit()
    db_session.close()


# the param df must be a pivot table with a datetime index, columns of stock_id and values to be added
def add_column_to_style_analysis_factor(df: pd.DataFrame, new_column_name: str):
    assert new_column_name not in StyleAnalysisStockFactor.__table__.columns.keys(), f'{StyleAnalysisStockFactor.__table__.name} already have column {new_column_name}!!'

    Session = sessionmaker(BasicDatabaseConnector().get_engine())
    db_session = Session()
    for row in db_session.query(StyleAnalysisStockFactor).all():
        row['new_column_name'] = df.loc[row.datetime, row.stock_id]
    db_session.commit()
    db_session.close()


class BasicDataHelper:
    def __init__(self):
        self._updated_count = defaultdict(int)

        # Get the mapping between order_book_id and fund_id (which is defined in this system)
        self._fund_id_mapping = BasicDataApi().get_fund_id_mapping()
        self._timer: float = time.monotonic()

    def _get_fund_id_from_order_book_id(self, order_book_id: str, date: datetime.date) -> str:
        if order_book_id in self._fund_id_mapping:
            for fund_info in self._fund_id_mapping[order_book_id]:
                if (date >= fund_info['start_date'] and
                        (fund_info['end_date'] == '00000000' or date <= fund_info['end_date'])):
                    return fund_info['fund_id']
        return None

    def _upload_basic(self, df: pd.DataFrame, table_name: str, to_truncate=False):
        print(table_name)
        # print(df)
        if to_truncate:
            with BasicDatabaseConnector().managed_session() as mn_session:
                try:
                    mn_session.execute(f'TRUNCATE TABLE {table_name}')
                    mn_session.commit()
                except Exception as e:
                    print(f'Failed to truncate table {table_name} <err_msg> {e}')

        df = df.drop(columns='_update_time', errors='ignore')
        df.to_sql(table_name, BasicDatabaseConnector().get_engine(), index=False, if_exists='append')

        now: float = time.monotonic()
        print(f'{table_name} costs {now - self._timer}s')
        self._timer = now
        self._updated_count[table_name] += df.shape[0]

    def _qdii_fund_hold_r(self, r, pos_type):
        r = r[1]
        target_dic = {'CODES':r['CODES'],'DATES':r['DATES']}
        idx = 1
        for i in range(1,21):
            if pos_type == r[f'rank{i}_type']:
                target_dic[f'rank{idx}_stock'] = r[f'rank{i}_stock']
                target_dic[f'rank{idx}_stock_code'] = r[f'rank{i}_stock_code']
                target_dic[f'rank{idx}_stockval'] = r[f'rank{i}_stockval']
                target_dic[f'rank{idx}_stockweight'] = r[f'rank{i}_stockweight']
                idx += 1
                if idx == 11:
                    return target_dic
        return target_dic