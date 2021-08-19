
import time
import json
import datetime
from typing import Union, Tuple

import numpy as np
import statsmodels.api as sm
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from collections import defaultdict
from ...wrapper.mysql import DerivedDatabaseConnector

FUND_CLASSIFIER = {
    'stock': ['偏股混合型基金', '普通股票型基金', '增强指数型基金', '被动指数型基金'],
    'bond': ['混合债券型二级基金', '中长期纯债型基金', '增强指数型债券基金', '混合债券型一级基金', '被动指数型债券基金', '短期纯债型基金', '偏债混合型基金'],
    'QDII': ['国际(QDII)另类投资基金', '国际(QDII)混合型基金', '国际(QDII)股票型基金', '国际(QDII)债券型基金', '股票多空', '商品型基金', 'REITs'],
    'mmf': ['货币市场型基金'],
    'mix': ['平衡混合型基金', '灵活配置型基金']
}

class DateJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def normalize(a: Union[pd.DataFrame, pd.Series]) -> np.ndarray:
    if isinstance(a, pd.Series):
        a = pd.DataFrame(a)
    return StandardScaler().fit_transform(a)

def score_rescale(a: Union[pd.DataFrame, pd.Series, np.ndarray]) -> np.ndarray:
    if isinstance(a, pd.Series) or isinstance(a, np.ndarray):
        a = pd.DataFrame(a)
    a = a.rank()
    return MinMaxScaler().fit_transform(a) * 100

def cont_rescale(a: Union[pd.DataFrame, pd.Series], feature_range: Tuple[float, float] = (0, 1)) -> np.ndarray:
    if isinstance(a, pd.Series):
        a = pd.DataFrame(a)
    return MinMaxScaler(feature_range=feature_range).fit_transform(a)


class DerivedDataHelper:
    def __init__(self):
        self._updated_count = defaultdict(int)
        self._timer = time.monotonic()

    @staticmethod
    def _lambda_cl(total: np.ndarray):
        if total.shape[0] <= 1:
            return {'beta':np.nan,
                    'alpha':np.nan,
                    'alpha_t':np.nan,
                    'alpha_p':np.nan,
                    'beta_t':np.nan,
                    'beta_p':np.nan,
                    }
        X = np.array([total[:, 1], total[:, 1]]).T
        X[:, 1][X[:, 1] > 0] = 0
        if np.count_nonzero(X[:, 1]) == 0:
            return {'beta':np.nan,
                    'alpha':np.nan,
                    'alpha_t':np.nan,
                    'alpha_p':np.nan,
                    'beta_t':np.nan,
                    'beta_p':np.nan,
                    }
        X[:, 0][X[:, 0] < 0] = 0
        est2 = sm.OLS(total[:, 0], sm.add_constant(X, prepend=False)).fit()
        return {'beta':est2.params[0] - est2.params[1],
                'alpha':est2.params[-1],
                'alpha_t':est2.tvalues[-1],
                'alpha_p':est2.pvalues[-1],
                # TODO beta 2 - beta 1 , p values and t values calculation is not correct
                'beta_t':est2.tvalues[1],
                'beta_p':est2.pvalues[1]
                }

    def _upload_derived(self, df, table_name, to_truncate=False):
        print(table_name)
        # print(df)
        if to_truncate:
            with DerivedDatabaseConnector().managed_session() as mn_session:
                try:
                    mn_session.execute(f'TRUNCATE TABLE {table_name}')
                    mn_session.commit()
                except Exception as e:
                    print(f'Failed to truncate table {table_name} <err_msg> {e}')

        df = df.drop(columns='_update_time', errors='ignore')
        df.to_sql(table_name, DerivedDatabaseConnector().get_engine(), index=False, if_exists='append')

        now: float = time.monotonic()
        print(f'{table_name} costs {now - self._timer}s')
        self._timer = now
        self._updated_count[table_name] += df.shape[0]
