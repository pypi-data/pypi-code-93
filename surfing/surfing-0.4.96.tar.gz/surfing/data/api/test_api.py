
from typing import Tuple, List

import datetime
from sqlalchemy import distinct
from sqlalchemy.sql import func
import pandas as pd
import numpy as np
from ...util.singleton import Singleton
from ...constant import FOFStrategyTypeDic
from ..wrapper.mysql import TestDatabaseConnector
from ..view.test_models import *

class TestDataApi(metaclass=Singleton):
    def get_stg_index_by_key_words(self, key_words:Tuple[str] = ()):
        with TestDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    PfIndexInfo
                )
                for key_word in key_words:
                    query = query.filter(
                        PfIndexInfo.desc_name.like(f'%{key_word}%')
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {PfIndexInfo.__tablename__}')
                return None

    def get_stg_index_by_index_id(self, index_list:Tuple[str] = ()):
        with TestDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    PfIndexInfo
                )
                if index_list:
                    query = query.filter(
                        PfIndexInfo.index_id.in_(index_list)
                    )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {PfIndexInfo.__tablename__}')
                return None

    def get_stg_index_price(self, index_list):
        with TestDatabaseConnector().managed_session() as db_session:
            try:
                query = db_session.query(
                    PfIndexPrice
                ).filter(
                    PfIndexPrice.index_id.in_(index_list)
                )
                return pd.read_sql(query.statement, query.session.bind)
            except Exception as e:
                print(f'Failed to get data <err_msg> {e} from {PfIndexPrice.__tablename__}')
                return None