
from threading import Thread
from .tools import print_func_time,bisect_left,bisect_right,print_func_time
from .calendarpd import Tdcal

import pandas as pd
import numpy as np
import numba as nb
import h5py

calendar,calendar_index = Tdcal._get_calendar(freq = 'Tdays')

class Mythread(Thread):

    def __init__(self,target,args,name = '',**kwargs):
        Thread.__init__(self)
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self.name = name

    @property
    def result(self):
        return getattr(self,'_result',None)
    
    def run(self):
        """Method representing the thread's activity."""
        try:
            if self._target:
                self._result = self._target(*self._args, **self._kwargs)
        finally:
            del self._target, self._args, self._kwargs

def wrap_dset(pth,key):
    'numpy 数据结构提取, mmap加速'
    with h5py.File(pth, 'r') as f:
        ds = f[key]
        offset = ds.id.get_offset()
        assert ds.chunks is None
        assert ds.compression is None
        assert offset > 0
        dtype = ds.dtype
        shape = ds.shape
    arr = np.memmap(pth, mode = 'r', shape = shape, offset = offset, dtype = dtype)
    return arr

@print_func_time
def read_mergeh5(path,ori_instruments,fields,start_index,end_index,tidx = 'trade_dt'):
    with h5py.File(path,'r') as h5:
        instlist = h5['instlist'][:].astype(str)            # inst code list
        instloc = h5['instloc'][:]     
        rsilist = h5['rsilist'][:]
        reilist = h5['reilist'][:]   
        cidx =  h5['data'].shape[0]  

    dset = wrap_dset(path,'data')
    if isinstance(ori_instruments,None.__class__):
        ori_instruments = instlist
    labels,infoloc = get_availables(ori_instruments,instlist)
    if len(infoloc) == 0:
        return pd.DataFrame()
    mask,amounts = gen_idxs(cidx,infoloc,instloc,rsilist,reilist,start_index,end_index)

    if isinstance(tidx,str):
            tidx = [tidx]
    if not isinstance(fields,None.__class__):
        if isinstance(fields,str):
            fields = [fields]
        data = dset[mask][tidx+fields]
    else:
        data = dset[mask]
    
    mask2 = ~(data[tidx[0]] == 0)
    data = data[mask2]

    data = pd.DataFrame(data).dropna(axis = 0,how = 'all')
    data['code'] = np.repeat(labels.values,amounts)[mask2]
    return data

@print_func_time
def get_availables(instruments,availables):
    instloc = pd.Series(np.arange(availables.shape[0]),index = availables)
    series = pd.Series(instruments)
    series.index = series#.str#.split('.').map(lambda x:''.join(x[::-1]))
    labels = series.reindex(availables).dropna()
    instloc = instloc.reindex(labels.index)
    return labels,instloc

@print_func_time
def gen_idxs(cidx,infoloc,instloc,rsilist,reilist,start_index,end_index):
    mask = np.zeros(cidx,dtype = bool)
    amounts = []
    for i in infoloc:
        if (end_index < rsilist[i]) | (start_index > reilist[i]) | (start_index > end_index):
            amounts.append(0)
            continue
        instsiloc = instloc[i]
        tsi = max(start_index - rsilist[i],0)
        tei = min(end_index - rsilist[i], reilist[i] - rsilist[i])
        h5si,h5ei = tsi + instsiloc,tei + instsiloc
        amounts.append(h5ei - h5si + 1)
        mask[h5si:h5ei + 1] = True
        # assert amounts[-1]>0
    return mask,amounts

@nb.jit(nopython = True,cache=True)
def match_amt(value,idx,ref_stt_idx,ref_end_idx):
    value = np.append([np.nan],value)
    fidx = np.append([ref_stt_idx],idx)
    bidx = np.roll(fidx,-1)
    bidx[-1] = ref_end_idx + 1
    amt = bidx - fidx
    return value,amt

@print_func_time
def to_ndns_reports(df,value_label,start_date,end_date,key1 = 'report_period',key2 = 'ann_date'):
    df['si'] = df[key2].apply(lambda x:bisect_left(calendar,x))
    dfs = {}
    ref_stt_idx = bisect_left(calendar,int(start_date))
    ref_end_idx = bisect_right(calendar,int(end_date)) - 1
    index = Tdcal.calendar(start_date,end_date)
    for inst,df_i in df.groupby(df['code']):
        df_i = df_i.sort_values([key2,key1]).drop_duplicates(key2,keep='last')
        value,amt = match_amt(df_i[value_label].values,df_i.si.values,ref_stt_idx,ref_end_idx)
        dfs[inst] = np.repeat(value,amt)
        assert dfs[inst].shape[0] == 3492
    return pd.DataFrame(dfs,index = index)

