import math
import numpy as np
import pandas as pd
from functools import reduce
from scipy.stats import rankdata
from scipy.stats.mstats import rankdata as mrankdata
from tempfile import TemporaryFile
import boto3
import uuid
import requests
import json

STOCK_ZERO_CODE = '000000'

def dict_to_wit_data(dict_data, default_value=None):
    wit_data = WitData(default_value)
    wit_data.init_with_dict(dict_data)
    return wit_data

def np_to_wit_data(dates, stock_codes, data, default_value=None):
    wit_data = WitData(default_value)
    wit_data.init_with_np(np.array(dates), np.array(stock_codes), np.array(data))
    return wit_data

def bytes_to_wit_data(text):
    wit_data = WitData()
    wit_data.init_with_bytes(text)
    return wit_data

def file_to_wit_data(filename):
    text = b''
    with open(filename, "rb") as f:
        text = f.read()
    
    return bytes_to_wit_data(text)

def db_rows_to_wit_data(rows, trade_date_column='tradeDate', stock_code_column='stockCode', value_column='itemValue', default_value=None):
    wit_data = None
    if len(rows) > 0:
        wit_data = WitData(default_value)
        wit_data.init_with_db_rows(rows, trade_date_column, stock_code_column, value_column)
    return wit_data

def dataframe_to_wit_data(df, default_value=None):
    wit_data = WitData(default_value)
    wit_data.init_with_dataframe(df)
    return wit_data

def wit_id_to_wit_data(api_key, wit_id):
    wit_data = WitData()
    wit_data.init_with_wit_id(api_key, wit_id)

    return wit_data

def reshape_wit_data_list(wit_data_list):
    if len(wit_data_list) < 2: return
    std_wit = get_std_wit(wit_data_list)

    all_dates = reduce(np.union1d, (wit.dates for wit in wit_data_list if isinstance(wit, WitData)))
    all_stock_codes = reduce(np.union1d, (wit.stock_codes for wit in wit_data_list if isinstance(wit, WitData)))

    if len(all_stock_codes) > 1 or all_stock_codes[0] != STOCK_ZERO_CODE:
        all_stock_codes = np.delete(all_stock_codes, np.where(all_stock_codes==STOCK_ZERO_CODE))

    for i, a_wit in enumerate(wit_data_list):
        if not isinstance(a_wit, WitData):
            if a_wit is None: a_wit = std_wit.default_value 
            wit_data_list[i] = np_to_wit_data(all_dates, all_stock_codes, np.repeat(np.array([a_wit]), len(all_dates) * len(all_stock_codes)).reshape(len(all_dates), len(all_stock_codes)), default_value=std_wit.default_value)

    for a_wit in wit_data_list:
        for date in all_dates[np.logical_not(np.isin(all_dates, a_wit.dates))]:
            date_index = np.where(all_dates==date)[0]
            a_wit.dates = np.insert(a_wit.dates, date_index, date)
            a_wit.data = np.insert(a_wit.data, date_index, a_wit.default_value, axis=0)

        if a_wit.is_zero_code():
            a_wit.data = np.repeat(a_wit.data, len(all_stock_codes)).reshape((len(a_wit.dates), len(all_stock_codes)))
        else:
            for stock_code in all_stock_codes[np.logical_not(np.isin(all_stock_codes, a_wit.stock_codes))]:
                stock_index = np.where(all_stock_codes==stock_code)[0]
                a_wit.data = np.insert(a_wit.data, stock_index, a_wit.default_value, axis=1)
                a_wit.stock_codes = np.insert(a_wit.stock_codes, stock_index, stock_code)
        a_wit.stock_codes = all_stock_codes

def _init_wit_data_for_calculation(operands):
    wit_data_list = []
    for operand in operands:
        a_wit = operand.copy() if isinstance(operand, WitData) else operand
        wit_data_list.append(a_wit)
    reshape_wit_data_list(wit_data_list)

    return wit_data_list

def get_std_wit(wit_data_list):
    std_wit = wit_data_list[0]
    for a_wit in wit_data_list:
        if isinstance(std_wit, WitData):
            if std_wit.is_zero_code():
                if isinstance(a_wit, WitData) and not a_wit.is_zero_code():
                    std_wit = a_wit
        else:
            if isinstance(a_wit, WitData):
                std_wit = a_wit
    return std_wit

def vectorize(func, operand):
    v_func = np.vectorize(func)
    return v_func(operand)

def single_calculation(func, operand):
    return np_to_wit_data(operand.dates, operand.stock_codes, func(operand.data), operand.default_value)

def sequantial_calculation(func, operands):
    if len(operands) < 2: return operands

    new_operands = [operand.copy() if isinstance(operand, WitData) else operand for operand in operands]

    wit_data_list = _init_wit_data_for_calculation(new_operands)

    data = [a_wit.data for a_wit in wit_data_list]
    std_wit = get_std_wit(wit_data_list)

    return np_to_wit_data(std_wit.dates, std_wit.stock_codes, func(data), wit_data_list[0].default_value)

def sequantial_compare_calculation(func, operands):
    if len(operands) < 2: return operands

    new_operands = [operand.copy() if isinstance(operand, WitData) else operand for operand in operands]

    wit_data_list = _init_wit_data_for_calculation(new_operands)

    data = [a_wit.data for a_wit in wit_data_list]
    std_wit = get_std_wit(wit_data_list)

    result_np = np.ones(std_wit.data.shape, dtype=bool)
    for index, a_data in enumerate(data):
        if index > 0:
            result_np = result_np & (func(data[index-1], a_data))

    return np_to_wit_data(std_wit.dates, std_wit.stock_codes, result_np)

def two_elements_calculation(func, operand1, operand2):
    new_operand1 = operand1.copy() if isinstance(operand1, WitData) else operand1
    new_operand2 = operand2.copy() if isinstance(operand2, WitData) else operand2

    wit_data_list = _init_wit_data_for_calculation([new_operand1, new_operand2])
    std_wit = get_std_wit(wit_data_list)

    return np_to_wit_data(std_wit.dates, std_wit.stock_codes, func(wit_data_list[0].data, wit_data_list[1].data), wit_data_list[0].default_value)

def plus(operands):
    return sequantial_calculation(lambda data : reduce(lambda x, y : x + y, data), operands)

def multiply(operands):
    return sequantial_calculation(lambda data : reduce(lambda x, y : x * y, data), operands)

def minus(operand1, operand2):
    return two_elements_calculation(lambda data1, data2 : data1 - data2, operand1, operand2)

def divide(operand1, operand2):
    return two_elements_calculation(lambda data1, data2 : data1 / data2, operand1, operand2)

def min(operands):
    return sequantial_calculation(lambda data : np.minimum(*data), operands)

def max(operands):
    return sequantial_calculation(lambda data : np.maximum(*data), operands)

def avg(operands):
    return sequantial_calculation(lambda data : np.mean(data, axis=0), operands)

def greater_than(operands):
    return sequantial_compare_calculation(lambda data1, data2 : (data1 > data2), operands)

def greater_than_or_equal(operands):
    return sequantial_compare_calculation(lambda data1, data2 : (data1 >= data2), operands)

def less_than(operands):
    return sequantial_compare_calculation(lambda data1, data2 : (data1 < data2), operands)

def less_than_or_equal(operands):
    return sequantial_compare_calculation(lambda data1, data2 : (data1 <= data2), operands)

def equals(operands):
    return sequantial_compare_calculation(lambda data1, data2 : (data1 == data2), operands)

def not_equals(operand1, operand2):
    return two_elements_calculation(lambda data1, data2 : (data1 != data2), operand1, operand2)

def ands(operands):
    return sequantial_compare_calculation(lambda data1, data2 : (data1 & data2), operands)

def ors(operands):
    return sequantial_compare_calculation(lambda data1, data2 : (data1 | data2), operands)

def nots(operand):
    return single_calculation(np.logical_not, operand) if isinstance(operand, WitData) else not operand

def top_rank(operands):
    rank_wit_data = rank(operands[1:], method='ordinal')
    data = rank_wit_data.data <= int(operands[0])
    return np_to_wit_data(rank_wit_data.dates, rank_wit_data.stock_codes, data)

def top_percent(operands):
    rank_wit_data = rank(operands[1:], method='ordinal')
    data = rank_wit_data.data <= np.count_nonzero(np.logical_not(np.isnan(rank_wit_data.data)), axis=1)[:,np.newaxis] * (float(operands[0]) / 100)
    return np_to_wit_data(rank_wit_data.dates, rank_wit_data.stock_codes, data)

def rank(operands, method='min'):
    new_operands = [operand.copy() if isinstance(operand, WitData) else operand for operand in operands]
    inited_operands = _init_wit_data_for_calculation([new_operands[1], new_operands[2]])
    scope = inited_operands[0]
    target = inited_operands[1]

    masked_operand = np.ma.masked_invalid(target.data)
    masked_operand.mask = masked_operand.mask | np.logical_not(scope.data)
    for i, line in enumerate(masked_operand.mask):
        if len(np.unique(line)) == 1 and line[0] == True:
            masked_operand.data[i] = np.zeros(len(masked_operand.data[i]))
            masked_operand.mask[i] = np.zeros(len(masked_operand.mask[i]), dtype=bool)
    result = mrankdata(masked_operand, axis=1)
    if operands[0]: #상위
        result = 0 - result
    else: #하위
        result[np.where(result==0.0)] = len(scope.stock_codes)

    result = rankdata(result, method=method, axis=1)
    result = np.array(result, dtype=float)
    result[np.logical_not(scope.data)] = np.nan

    return np_to_wit_data(inited_operands[0].dates, inited_operands[0].stock_codes, result)

def np_to_byte(val):
    a_file = TemporaryFile()
    np.save(a_file, val)
    a_file.seek(0)
    return a_file.read()

def np_from_byte(b):
    a_file = TemporaryFile()
    a_file.write(b)
    a_file.seek(0)
    return np.load(a_file, allow_pickle=True)














class WitData:
    def __init__(self, default_value=None):
        self.split_size = 8
        self.default_value = default_value

    def __str__(self):
        return str(self.to_dataframe())
        #return f"""dates :\n{self.dates}\n\nstock_codes :\n{self.stock_codes}\n\ndata :\n{self.data}"""

    def __repr__(self):
        return str(self.to_dataframe())

    def init_with_dict(self, dict_data):
        self.dates = np.sort(np.array(list(dict_data.keys())))
        self.stock_codes = np.array(['X'])
        for one_date in self.dates:
            if one_date != 'returnType':
                self.stock_codes = np.union1d(self.stock_codes, list(dict_data[one_date].keys()))
        self.stock_codes = np.delete(self.stock_codes, np.where(self.stock_codes == 'X'))

        self.data = np.empty((len(self.dates), len(self.stock_codes)))
        self.data[:, :] = self.default_value

        if isinstance(list(list(dict_data.values())[0].values())[0], dict):
            for i, one_date in enumerate(self.dates):
                for j, stock_code in enumerate(self.stock_codes):
                    try:
                        self.data[i, j] = list(dict_data[one_date][stock_code].values())[0]
                    except:
                        self.data[i, j] = self.default_value
        else:
            for i, one_date in enumerate(self.dates):
                for j, stock_code in enumerate(self.stock_codes):
                    try:
                        self.data[i, j] = dict_data[one_date][stock_code]
                    except:
                        self.data[i, j] = self.default_value

    def init_with_np(self, dates, stock_codes, data):
        self.dates = dates.copy()
        self.stock_codes = stock_codes.copy()
        self.data = data.copy()

    def init_with_bytes(self, b):
        default_value_size = int.from_bytes(b[:self.split_size], byteorder='big')
        dates_size = int.from_bytes(b[self.split_size:self.split_size*2], byteorder='big')
        stocks_codes_size = int.from_bytes(b[self.split_size*2:self.split_size*3], byteorder='big')
        start_index = self.split_size * 3
        default_value_end_index = start_index + default_value_size
        dates_end_index = default_value_end_index + dates_size
        stock_codes_end_index = dates_end_index + stocks_codes_size
        bs = [b[start_index : default_value_end_index], b[default_value_end_index : dates_end_index], b[dates_end_index : stock_codes_end_index], b[stock_codes_end_index:]]
        nps = []
        for a_b in bs:
            nps.append(np_from_byte(a_b))
        self.default_value = nps[0].item()
        self.init_with_np(nps[1], nps[2], nps[3])

    def init_with_db_rows(self, rows, trade_date_column='tradeDate', stock_code_column='stockCode', value_column='itemValue'):
        df = pd.DataFrame.from_records(rows)
        if stock_code_column is None:
            df = df.set_index(trade_date_column)
            df = df.sort_index()
            df.columns = [STOCK_ZERO_CODE]
        else:
            df = df.pivot(index=trade_date_column, columns=stock_code_column, values=value_column)
        self.init_with_dataframe(df)

    def init_with_dataframe(self, df):
        self.dates = df.index.to_numpy()
        self.stock_codes = df.columns.to_numpy()
        self.data =  df.to_numpy()

    def init_with_wit_id(self, api_key, wit_id):
        data = dict()
        data['apiKey'] = api_key
        data['witId'] = wit_id
        response = requests.post('https://swxvc99i7g.execute-api.ap-northeast-2.amazonaws.com/Prod/wit', data=json.dumps(data)).json()

        file_name = wit_id
        s3Resource = boto3.resource('s3')
        bucket = s3Resource.Bucket('ffolio.motoo.temp')
        obj = bucket.Object(key = file_name)
        temp_file_bytes = obj.get()['Body'].read()

        self.init_with_bytes(temp_file_bytes)
        obj.delete()

    def to_dataframe(self):
        data = np.nan_to_num(self.data, posinf=np.nan, neginf=np.nan)
        df = pd.DataFrame(data=data, index=self.dates, columns=self.stock_codes)
        return df.where(pd.notnull(df), None)

    def to_dict(self):
        return self.to_dataframe().to_dict('index')

    def to_factor_dict(self):
        v_func = np.vectorize(lambda x : {'itemValue':x if not math.isnan(x) else None})
        new_wit = self.copy()
        new_wit.data = v_func(new_wit.data)
        return new_wit.to_dict()

    def to_bytes(self):
        arr = [self.default_value, self.dates, self.stock_codes, self.data]
        bs = []
        for ele in arr:
            bs.append(np_to_byte(ele))
        return b''.join([len(bs[0]).to_bytes(self.split_size, byteorder='big'), len(bs[1]).to_bytes(self.split_size, byteorder='big'), len(bs[2]).to_bytes(self.split_size, byteorder='big'), \
            bs[0], bs[1], bs[2], bs[3]])
    
    def save(self, filename):
        data = self.to_bytes()
        with open(filename, "wb") as f:
            f.write(data)
    
    def to_tempfile(self):
        data = self.to_bytes()
        file = TemporaryFile()
        file.write(data)
        file.seek(0)
        return file
    
    def register(self, api_key=None, title=None, description=None):
        tempfile = self.to_tempfile()
        s3Client = boto3.client('s3',
            aws_access_key_id='AKIAVWWT2XJMYRDE24M4', # account only for s3 upload
            aws_secret_access_key='iSrUX71dQ2iKyzizk6fk1zcLRaEeL1cgEbk0eivK ')
        temp_wit_id = str(uuid.uuid1()).replace('-','')
        s3Client.upload_fileobj(tempfile, "ffolio.motoo.temp", temp_wit_id)

        data = dict()
        data['apiKey'] = api_key
        data['title'] = title
        data['desc'] = description
        data['witId'] = temp_wit_id
        return requests.post('https://c5awm0ehw3.execute-api.ap-northeast-2.amazonaws.com/Prod/wit', data=json.dumps(data)).text

    def copy(self):
        wit_data = np_to_wit_data(self.dates, self.stock_codes, self.data, default_value=self.default_value)
        return wit_data

    def get_date_index(self, date):
        date_key = -1
        if date in self.dates:
            date_key = np.where(self.dates==date)[0][0]
        else:
            print(f"DateKeyError(WitData) : {(date, self.dates)}")
        return date_key

    def get_stock_code_index(self, stock_code):
        stock_code_key = -1
        if len(np.where(self.stock_codes==stock_code)[0]) > 0:
            stock_code_key = np.where(self.stock_codes==stock_code)[0][0]
        else:
            print(f"StockCodeKeyError(WitData) : {stock_code}")
        return stock_code_key

    def get(self, date, stock_code):
        date_key = self.get_date_index(date)
        stock_code_key = self.get_stock_code_index(stock_code)

        try:
            return_value = self.data[date_key, stock_code_key]
        except:
            print(f"KeyError(WitData) : {date}, {stock_code}")
            return None

        return return_value

    def get_stock_data(self, stock_code):
        stock_code_key = self.get_stock_code_index(stock_code)

        try:
            return_value = np_to_wit_data(self.dates.copy(), np.array([stock_code]), self.data[:, [stock_code_key]], default_value=self.default_value)
        except:
            print(f"KeyError(WitData) : {stock_code}")
            return None

        return return_value

    def get_stocks_data(self, stock_codes):
        stock_code_flags = np.where(np.isin(self.stock_codes, stock_codes))[0]
        return np_to_wit_data(self.dates, np.array(stock_codes), self.data[:, stock_code_flags], default_value=self.default_value)

    def get_date_data(self, dates):
        wit_data = np_to_wit_data(self.dates[np.isin(self.dates, dates)], self.stock_codes, self.data[np.isin(self.dates, dates)], default_value=self.default_value)
        return wit_data

    def switch_data(self, original_dates, data):
        for i, original_date in enumerate(original_dates):
            self.data[self.get_date_index(original_date)] = data[i]

    def get_date_slicing(self, start_date=None, end_date=None):
        start_index = None
        end_index = None

        if start_date is None or start_date < self.dates[0]:
            start_index = 0
        elif start_date > self.dates[-1]:
            return None
        else:
            start_index = np.min(np.where(self.dates >= start_date))

        if end_date is None or end_date > self.dates[-1]:
            end_index = len(self.dates)
        elif end_date < self.dates[0]:
            return None
        else:
            end_index = np.max(np.where(self.dates <= end_date)) + 1

        return self.get_slicing(start_index, end_index)

    def get_slicing(self, start_index=None, end_index=None):
        wit_data = np_to_wit_data(self.dates[start_index:end_index], self.stock_codes, self.data[start_index:end_index], default_value=self.default_value)
        return wit_data

    def get_shift_days(self, days):
        if len(self.dates) > abs(days):
            wit_data = self 
            if days > 0:
                wit_data = np_to_wit_data(self.dates[:-days], self.stock_codes, self.data[days:], default_value=self.default_value)
            elif days < 0:
                wit_data = np_to_wit_data(self.dates[-days:], self.stock_codes, self.data[:days], default_value=self.default_value)
            return wit_data
        else:
            return None
            #raise ValueError(f"dates : {self.dates}\ndays : {days}")

    def is_zero_code(self):
        return len(self.stock_codes) == 1 and self.stock_codes[0] == STOCK_ZERO_CODE

    def get_sliding_window(self, window):
        shape = tuple(np.array(self.data.shape) - np.array(window) + 1) + window
        strides = self.data.strides + self.data.strides
        return np.lib.stride_tricks.as_strided(self.data, shape=shape, strides=strides)

    def __add__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data + (new_other.data if isinstance(new_other, WitData) else new_other), default_value=new_self.default_value)

    def __sub__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data - (new_other.data if isinstance(new_other, WitData) else new_other), default_value=new_self.default_value)

    def __mul__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data * (new_other.data if isinstance(new_other, WitData) else new_other), default_value=new_self.default_value)

    def __truediv__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data / (new_other.data if isinstance(new_other, WitData) else new_other), default_value=new_self.default_value)

    def __mod__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data % (new_other.data if isinstance(new_other, WitData) else new_other), default_value=new_self.default_value)

    def __pow__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data ** (new_other.data if isinstance(new_other, WitData) else new_other), default_value=new_self.default_value)

    def __and__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data & (new_other.data if isinstance(new_other, WitData) else new_other))

    def __or__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data | (new_other.data if isinstance(new_other, WitData) else new_other))

    def __iadd__(self, other):
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([self, new_other])
        self.data = self.data + (new_other.data if isinstance(new_other, WitData) else new_other)
        return self

    def __isub__(self, other):
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([self, new_other])
        self.data = self.data - (new_other.data if isinstance(new_other, WitData) else new_other)
        return self

    def __imul__(self, other):
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([self, new_other])
        self.data = self.data * (new_other.data if isinstance(new_other, WitData) else new_other)
        return self

    def __idiv__(self, other):
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([self, new_other])
        self.data = self.data / (new_other.data if isinstance(new_other, WitData) else new_other)
        return self

    def __imod__(self, other):
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([self, new_other])
        self.data = self.data % (new_other.data if isinstance(new_other, WitData) else new_other)
        return self

    def __ipow__(self, other):
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([self, new_other])
        self.data = self.data ** (new_other.data if isinstance(new_other, WitData) else new_other)
        return self

    def __iand__(self, other):
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([self, new_other])
        self.data = self.data & (new_other.data if isinstance(new_other, WitData) else new_other)
        return self

    def __ior__(self, other):
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([self, new_other])
        self.data = self.data | (new_other.data if isinstance(new_other, WitData) else new_other)
        return self

    def __neg__(self):
        return np_to_wit_data(self.dates.copy(), self.stock_codes.copy(), -self.data, default_value=self.default_value)

    def __pos__(self):
        return np_to_wit_data(self.dates.copy(), self.stock_codes.copy(), +self.data, default_value=self.default_value)

    def __abs__(self):
        return np_to_wit_data(self.dates.copy(), self.stock_codes.copy(), abs(self.data), default_value=self.default_value)

    def __lt__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data < (new_other.data if isinstance(new_other, WitData) else new_other))

    def __le__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data <= (new_other.data if isinstance(new_other, WitData) else new_other))

    def __eq__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data == (new_other.data if isinstance(new_other, WitData) else new_other))

    def __ne__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data != (new_other.data if isinstance(new_other, WitData) else new_other))

    def __ge__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data >= (new_other.data if isinstance(new_other, WitData) else new_other))

    def __gt__(self, other):
        new_self = self.copy()
        new_other = other.copy() if isinstance(other, WitData) else other
        reshape_wit_data_list([new_self, new_other])
        return np_to_wit_data(new_self.dates, new_self.stock_codes, new_self.data > (new_other.data if isinstance(new_other, WitData) else new_other))
