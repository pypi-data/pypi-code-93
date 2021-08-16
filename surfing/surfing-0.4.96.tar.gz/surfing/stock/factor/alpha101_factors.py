import numpy as np
import pandas as pd

from .factor_types import Alpha101Factor
from .basic_factors import StockPostPriceFactor, StockHighPriceFactor, StockOpenPriceFactor, StockLowPriceFactor, StockVolumeFactor, StockVWAPFactor, MarketValueFactor
from .utils import normalize


def Brank_cs(x):
    return (x.rank(axis=1).T/x.rank(axis=1).max(axis=1)).T

def Brank_ts(x):
    return x.rank()/x.rank().max()

def rolling_rank(data_array):
        return (data_array.argsort(axis = 0).argsort(axis = 0) + 1)[-1, :]
            
def ts_rank(data, timewindow = 5):
    data_array = data.to_numpy()
    ts_array = np.zeros(shape = data_array.shape)
    for raw_index in range(ts_array.shape[0] + 1):
        real_index = raw_index - 1
        if real_index < timewindow - 1:
            ts_array[real_index, :] = np.nan
        else:
            ts_array[real_index, :] = rolling_rank(data_array[real_index - (timewindow - 1): real_index + 1, :])
    return pd.DataFrame(ts_array, columns = data.columns,index = data.index)

def ts_min(data, timewindow = 3):
    data_array = data.to_numpy()
    ts_min = np.zeros (shape = data_array.shape)
    for raw_index in range(ts_min.shape[0] + 1):
        real_index = raw_index - 1
        if real_index < timewindow - 1:
            ts_min[real_index, :] = np.nan
        else:
            ts_min[real_index, :] = (data_array[real_index - (timewindow - 1): real_index + 1, :]).min(axis = 0)
    return pd.DataFrame(ts_min, columns = data.columns,index = data.index)

def ts_max(data, timewindow = 3):
    data_array = data.to_numpy()
    ts_max = np.zeros(shape = data_array.shape)
    for raw_index in range(ts_max.shape[0] + 1):
        real_index = raw_index - 1
        if real_index < timewindow - 1:
            ts_max[real_index, :] = np.nan
        else:
            ts_max[real_index, :] = (data_array[real_index - (timewindow - 1): real_index + 1, :]).max(axis = 0)
    return pd.DataFrame(ts_max, columns = data.columns,index = data.index)

def decay_linear(data, period = 3):
        data_array = data.to_numpy()
        na_lwma = np.zeros_like(data_array)
        na_lwma[:period, :] = data_array[:period, :]
        divisor = period * (period + 1) / 2
        y = (np.arange(period) + 1) * 1.0 / divisor
        for row in range(period - 1, data_array.shape[0]):
            x = data_array[row - period + 1: row + 1, :]
            na_lwma[row, :] = (np.dot(x.T, y))
        return pd.DataFrame(na_lwma, columns = data.columns,index = data.index)

def ts_argmax(data, timewindow = 3):
        data_array = data.to_numpy()
        ts_argmax = np.zeros(shape = data_array.shape)
        for raw_index in range(ts_argmax.shape[0] + 1):
            real_index = raw_index - 1
            if real_index < timewindow - 1:
                ts_argmax[real_index, :] = np.nan
            else:
                ts_argmax[real_index, :] = (data_array[real_index - (timewindow - 1): real_index + 1, :]).argmax(axis = 0)
        return pd.DataFrame(ts_argmax+1, columns = data.columns,index = data.index)

class Alpha101_1_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('1')

    def calc(self):
        spp = StockPostPriceFactor().get()
        ret = spp.apply(np.log).diff()
        std = ret.rolling(20).std()
        helper = ret[ret>0].apply(np.sign).replace(np.nan,0)
        x1 = (1 - helper) * std + helper * spp
        x2 = x1.apply(np.sign) * (x1 ** 2)
        x3 = x2.rolling(5).apply(lambda x: x.argmax(), raw=True)
        self._factor = Brank_cs(x3) - 0.5

class Alpha101_2_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('2')

    def calc(self):
        vlm = StockVolumeFactor().get()
        op = StockOpenPriceFactor().get()
        cl = StockPostPriceFactor().get()
        x1 = vlm.apply(np.log).diff(2)
        x2 = Brank_cs(x1)
        y1 = (cl-op)/op
        y2 = Brank_cs(y1)
        self._factor = -x2.rolling(6).corr(y2)

class Alpha101_3_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('3')

    def calc(self):
        vlm = StockVolumeFactor().get()
        op = StockOpenPriceFactor().get()
        x1 = Brank_cs(vlm)
        y1 = Brank_cs(op)
        self._factor = -x1.rolling(10).corr(y1)

class Alpha101_4_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('4')

    def calc(self):
        low = StockLowPriceFactor().get()
        x1 = Brank_cs(low)
        self._factor = ts_rank(x1)

class Alpha101_5_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('5')

    def calc(self):
        vwap =  StockVWAPFactor().get()
        op = StockOpenPriceFactor().get()
        cl = StockPostPriceFactor().get()
        x1 = Brank_cs(op - vwap.rolling(10).mean())
        y1 = -(Brank_cs((cl-vwap).apply(np.abs)))
        self._factor = x1*y1

class Alpha101_6_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('6')

    def calc(self):
        vlm = StockVolumeFactor().get()
        op = StockOpenPriceFactor().get()
        self._factor = op.rolling(10).corr(vlm)

class Alpha101_7_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('7')

    def calc(self):
        vlm = StockVolumeFactor().get()
        cl = StockPostPriceFactor().get()
        helper = vlm[vlm<vlm.rolling(20).mean()].apply(np.sign).replace(np.nan,0)
        x1 = helper * (-ts_rank(cl.diff(7).apply(np.abs))*cl.diff(7).apply(np.sign))
        self._factor = x1.replace(0,-1)

class Alpha101_8_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('8')

    def calc(self):
        cl = StockPostPriceFactor().get()
        op = StockOpenPriceFactor().get()
        ret = cl.apply(np.log).diff()
        x1 = op.rolling(5).sum()*ret.rolling(5).sum()
        self._factor = -Brank_cs(x1.diff(10))

class Alpha101_9_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('9')

    def calc(self):
        cl = StockPostPriceFactor().get()
        temp = ts_min(cl.diff(), timewindow=5)
        helper = temp[temp<0].apply(np.sign).replace(np.nan,0)
        temp2 = ts_max(cl.diff(), timewindow=4)
        helper2 = temp2[temp2<0].apply(np.sign).replace(np.nan,0)
        x1 = helper2 * cl.diff() + (1 - helper2) * -(cl.diff())        
        self._factor = helper * cl.diff() + (1 - helper) * x1

class Alpha101_10_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('10')

    def calc(self):
        cl = StockPostPriceFactor().get()
        op = StockOpenPriceFactor().get()
        ret = cl.apply(np.log).diff()
        x1 = op.rolling(5).sum()*ret.rolling(5).sum()
        self._factor = -Brank_cs(x1.diff(10))

class Alpha101_11_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('11')

    def calc(self):
        vwap =  StockVWAPFactor().get()
        cl = StockPostPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = Brank_cs(ts_max(vwap-cl))
        y1 = Brank_cs(ts_min(vwap-cl))
        z1 = Brank_cs(vlm.diff(3))
        self._factor = (x1 + y1) * z1

class Alpha101_12_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('12')

    def calc(self):
        cl = StockPostPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = vlm.diff().apply(np.sign)
        y1 = -cl.diff()
        self._factor = x1 * y1

class Alpha101_13_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('13')

    def calc(self):
        cl = StockPostPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = Brank_cs(cl)
        y1 = Brank_cs(vlm)
        z1 = x1.rolling(5).cov(y1)
        self._factor = -Brank_cs(z1)

class Alpha101_14_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('14')

    def calc(self):
        cl = StockPostPriceFactor().get()
        vlm = StockVolumeFactor().get()
        op = StockOpenPriceFactor().get()
        ret = cl.apply(np.log).diff()
        x1 = Brank_cs(ret.diff(3))
        y1 = op.rolling(10).corr(vlm)
        self._factor = -x1*y1

class Alpha101_15_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('15')

    def calc(self):
        high = StockHighPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = Brank_cs(high)
        x2 = Brank_cs(vlm)
        y1 = x1.rolling(3).corr(x2)
        y2 = Brank_cs(y1)
        self._factor = -y2.rolling(3).sum()

class Alpha101_16_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('16')

    def calc(self):
        high = StockHighPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = Brank_cs(high)
        y1 = Brank_cs(vlm)
        z1 = x1.rolling(5).cov(y1)
        self._factor = -Brank_cs(z1)

class Alpha101_17_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('17')

    def calc(self):
        cl = StockPostPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = -Brank_cs(ts_rank(cl, timewindow=10))
        y1 = Brank_cs((cl.diff()).diff())
        z1 = Brank_cs(ts_rank(vlm/vlm.rolling(20).mean(), 10))
        self._factor = x1*y1*z1

class Alpha101_18_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('18')

    def calc(self):
        cl = StockPostPriceFactor().get()
        op = StockOpenPriceFactor().get()
        x1 = ((cl-op).apply(np.abs)).rolling(5).std()+cl-op
        y1 = cl.rolling(10).corr(op)
        self._factor = -1*Brank_cs(x1+y1)

class Alpha101_19_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('19')

    def calc(self):
        cl = StockPostPriceFactor().get()
        ret = cl.apply(np.log).diff()
        x1 = -1*(cl-cl.shift(7)+cl.diff(7)).apply(np.sign)
        y1 = Brank_cs(1 + ret.rolling(250).sum())
        self._factor = x1 * y1

class Alpha101_20_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('20')

    def calc(self):
        cl = StockPostPriceFactor().get()
        op = StockOpenPriceFactor().get()
        high = StockHighPriceFactor().get()
        low = StockLowPriceFactor().get()
        x1 = -Brank_cs(op - high.shift(1))
        y1 = Brank_cs(op - cl.shift(1))
        z1 = Brank_cs(op - low.shift(1))
        self._factor = x1 * y1 * z1

class Alpha101_22_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('22')

    def calc(self):
        cl = StockPostPriceFactor().get()
        high = StockHighPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = (high.rolling(5).corr(vlm)).diff(5)
        y1 = Brank_cs(cl.rolling(20).std())
        self._factor = -1 * x1 * y1

class Alpha101_23_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('23')

    def calc(self):
        high = StockHighPriceFactor().get()
        helper = high[high.rolling(20).mean()<high].apply(np.sign).replace(np.nan,0)
        x1 = helper * -1 * (high.diff(2))
        self._factor = x1

class Alpha101_25_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('25')

    def calc(self):
        cl = StockPostPriceFactor().get()
        vwap =  StockVWAPFactor().get()
        high = StockHighPriceFactor().get()
        vlm = StockVolumeFactor().get()
        ret = cl.apply(np.log).diff()
        x1 = (-1 * ret) * vlm.rolling(20).mean() * vwap
        self._factor = Brank_cs(x1 * (high - cl))

class Alpha101_33_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('33')

    def calc(self):
        cl = StockPostPriceFactor().get()
        op = StockOpenPriceFactor().get()
        self._factor = Brank_cs(-1 * (1 - (op / cl)))

class Alpha101_34_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('34')

    def calc(self):
        cl = StockPostPriceFactor().get()
        ret = cl.apply(np.log).diff()
        x1 = Brank_cs(ret.rolling(2).std() / ret.rolling(5).std())
        x2 = Brank_cs(cl.diff())
        self._factor = (1 - x1) + (1 -x2)

class Alpha101_40_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('40')

    def calc(self):
        high = StockHighPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = Brank_cs(high.rolling(10).std())
        x2 = high.rolling(10).corr(vlm)
        self._factor = -1 * x1 * x2

class Alpha101_41_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('41')

    def calc(self):
        low = StockLowPriceFactor().get()
        vwap = StockVWAPFactor().get()
        high = StockHighPriceFactor().get()
        self._factor = ((low * high).apply(np.sqrt) - vwap)

class Alpha101_42_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('42')

    def calc(self):
        cl = StockPostPriceFactor().get()
        vwap = StockVWAPFactor().get()
        x1 = Brank_cs(vwap-cl)
        y1 = Brank_cs(vwap+cl)
        self._factor = x1 / y1

class Alpha101_43_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('43')

    def calc(self):
        cl = StockPostPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = ts_rank((vlm / vlm.rolling(20).mean()), 20)
        x2 = ts_rank((-1* cl.diff(7)), 8)
        self._factor = x1 * x2

class Alpha101_44_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('44')

    def calc(self):
        high = StockHighPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = Brank_cs(vlm)
        self._factor = -1 * high.rolling(5).corr(x1)


class Alpha101_53_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('53')

    def calc(self):
        cl = StockPostPriceFactor().get()
        low = StockLowPriceFactor().get() 
        high = StockHighPriceFactor().get()
        x1 = ((cl - low) - (high - cl))/(cl - low)
        self._factor = -1 * x1.diff(9)

class Alpha101_54_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('54')

    def calc(self):
        cl = StockPostPriceFactor().get()
        low = StockLowPriceFactor().get() 
        op = StockOpenPriceFactor().get()
        high = StockHighPriceFactor().get()
        x1 = (low - cl) * (op ** 5)/((low - high)*(cl ** 5))
        self._factor = -1 * x1

class Alpha101_55_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('55')

    def calc(self):
        cl = StockPostPriceFactor().get()
        low = StockLowPriceFactor().get() 
        high = StockHighPriceFactor().get()
        vlm = StockVolumeFactor().get()
        x1 = cl - ts_min(low, 12)
        x2 = ts_max(high, 12) - ts_min(low, 12)
        y1 = Brank_cs(x1 / x2)
        y2 = Brank_cs(vlm)
        self._factor = -1 * y1.rolling(6).corr(y2)

class Alpha101_56_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('56')

    def calc(self):
        cl = StockPostPriceFactor().get()
        cap = MarketValueFactor().get()
        ret = cl.apply(np.log).diff()
        x1 = ret.rolling(2).sum()
        x2 = x1.rolling(3).sum()
        x3 = ret.rolling(10).sum()
        y1 = x3/x2
        y2 = cap * ret
        self._factor = -1 * Brank_cs(y1) * Brank_cs(y2)

class Alpha101_57_Factor(Alpha101Factor):
    def __init__(self):
        super().__init__('57')

    def calc(self):
        cl = StockPostPriceFactor().get()
        vwap =  StockVWAPFactor().get()
        x1 = Brank_cs(ts_argmax(cl,30))
        self._factor = -1 * (cl - vwap)/decay_linear(x1, 2)



    

         















        

    







    










    