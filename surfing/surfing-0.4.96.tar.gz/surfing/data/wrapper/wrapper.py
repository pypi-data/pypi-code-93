
from surfing.structure import Tick
import pandas as pd
import numpy as np
import os
import json
import datetime

class DataWrapper:

    def __init__(self, base_path):
        assert base_path is not None, 'data path has to be set'
        self.base_path = base_path
        self.meta_info = DataWrapper.load_meta(base_path)

    @staticmethod
    def load_meta(folder):
        file_path = folder + '/.meta_data.json'
        try:
            with open(file_path,'r') as load_f:
                meta_info = json.load(load_f)
        except:
            assert 0, 'meta info not exsited'
        return meta_info

    @staticmethod
    def save_data(df, folder, ticker, colomns=None):
        df['time'] = np.array(df.index.to_pydatetime(), dtype='datetime64[ms]')
        data_type = [(col_i, 'f4') for col_i in colomns]
        data_type.append(('time', 'datetime64[ms]'))
        df = [tuple(x) for x in df.values]
        df = np.array(df, dtype=data_type)
        np.save(os.path.join(folder, '{}.npy'.format(ticker)), df)

    @staticmethod
    def has_data(folder, ticker):
        return os.path.isfile('{}/{}.npy'.format(folder, ticker))

    @staticmethod
    def base_load_data(folder, ticker, index_column, colomns=None):
        # may learn to cache data here!
        if not DataWrapper.has_data(folder, ticker):
            return None
        value = np.load(os.path.join(folder, '{}.npy'.format(ticker)), allow_pickle=True)
        df = pd.DataFrame(data=value, columns=colomns)
        df.set_index(index_column, drop=True, inplace=True)
        df.fillna(method='ffill', inplace=True)
        return df

    @staticmethod
    def base_load_npz(folder, price, columns):
        file_i = f'{folder}/{price}.npz'
        data_i_folder = os.path.isfile(file_i)
        if not data_i_folder:
            return None
        value = np.load(file_i, allow_pickle=True)
        df = pd.DataFrame(data=value['arr_0'], columns=columns)
        return df
