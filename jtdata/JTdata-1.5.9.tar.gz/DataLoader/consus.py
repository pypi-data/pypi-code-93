import os
import abc
import pandas as pd
from .config import data_path
from .tools import print_func_time,to_intdate
from .utils import read_mergeh5
from collections.abc import Iterable
defualt_si = 0
defualt_ei = 1e7

ashare_consus_fy0_30d = os.path.join(data_path,r'AShareConsensusData_FY0_30D')
ashare_consus_fy0_90d = os.path.join(data_path,r'AShareConsensusData_FY0_90D')
ashare_consus_fy0_180d = os.path.join(data_path,r'AShareConsensusData_FY0_180D')
ashare_consus_fy0_180l = os.path.join(data_path,r'AShareConsensusData_FY0_180L')
ashare_consus_fy1_30d = os.path.join(data_path,r'AShareConsensusData_FY1_30D')
ashare_consus_fy1_90d = os.path.join(data_path,r'AShareConsensusData_FY1_90D')
ashare_consus_fy1_180d = os.path.join(data_path,r'AShareConsensusData_FY1_180D')
ashare_consus_fy1_180l = os.path.join(data_path,r'AShareConsensusData_FY1_180L')
ashare_consus_fy2_30d = os.path.join(data_path,r'AShareConsensusData_FY2_30D')
ashare_consus_fy2_90d = os.path.join(data_path,r'AShareConsensusData_FY2_90D')
ashare_consus_fy2_180d = os.path.join(data_path,r'AShareConsensusData_FY2_180D')
ashare_consus_fy2_180l = os.path.join(data_path,r'AShareConsensusData_FY2_180L')
ashare_consus_fy3_30d = os.path.join(data_path,r'AShareConsensusData_FY3_30D')
ashare_consus_fy3_90d = os.path.join(data_path,r'AShareConsensusData_FY3_90D')
ashare_consus_fy3_180d = os.path.join(data_path,r'AShareConsensusData_FY3_180D')
ashare_consus_fy3_180l = os.path.join(data_path,r'AShareConsensusData_FY3_180L')

ashare_consus_rolling_cagr = os.path.join(data_path,r"AShareConsensusRollingData_CAGR")
ashare_consus_rolling_fy0 = os.path.join(data_path,r"AShareConsensusRollingData_FY0")
ashare_consus_rolling_fy1 = os.path.join(data_path,r"AShareConsensusRollingData_FY1")
ashare_consus_rolling_fy2 = os.path.join(data_path,r"AShareConsensusRollingData_FY2")
ashare_consus_rolling_fy3 = os.path.join(data_path,r"AShareConsensusRollingData_FY3")
ashare_consus_rolling_yoy = os.path.join(data_path,r"AShareConsensusRollingData_YOY")
ashare_consus_rolling_yoy2 = os.path.join(data_path,r"AShareConsensusRollingData_YOY2")

ashare_sktrating_30d = os.path.join(data_path,r"AShareStockRatingConsus_30D")
ashare_sktrating_90d = os.path.join(data_path,r"AShareStockRatingConsus_90D")
ashare_sktrating_180d = os.path.join(data_path,r"AShareStockRatingConsus_180D")

suntime_confc_stk = os.path.join(data_path,r"CON_FORECAST_STK")
suntime_confc_roll_stk = os.path.join(data_path,r"CON_FORECAST_ROLL_STK")
suntime_repofc_stk = os.path.join(data_path,r"RPT_FORECAST_STK")
suntime_repofc_stk_tc = os.path.join(data_path,r"RPT_FORECAST_STK_TC")
suntime_earning_adj = os.path.join(data_path,r"RPT_EARNINGS_ADJUST")

suntime_rating_adj = os.path.join(data_path,r"RPT_RATING_ADJUST")
suntime_tgtprice_adj = os.path.join(data_path,r"RPT_TARGET_PRICE_ADJUST")

class BaseConsusDataProvider(abc.ABC):

    @abc.abstractmethod
    def get_repo_data(self,instruments,fields,start_date,end_date):
        raise NotImplementedError

class LoacalConsusProvider(BaseConsusDataProvider):

    def __init__(self, tidx=['est_date','est_report_date']) -> None:
        self.tidx = tidx
        super().__init__()

    def get_repo_data(self,datapath,instruments,fields,**kws):
            """ report table reader """
            if isinstance(instruments,str):
                instruments = [instruments]
            tidx = kws.get("tidx",self.tidx)
            path = os.path.join(datapath,'merged.h5')
            data = read_mergeh5(path,instruments,fields,defualt_si,defualt_ei,tidx)
            if data.empty:
                return data
            if ("start_date" in kws)&("end_date" in kws):
                start_date,end_date = kws.get("start_date"),kws.get("end_date")
                sd,ed = to_intdate(start_date),to_intdate(end_date)
                by = kws.get('by',tidx[0])
                data = data.loc[(data[by] >= sd) & (data[by] <= ed)]

            if self.tidx[1] in kws:
                tgt_rp = kws.get(self.tidx[1],None)
                if not isinstance(tgt_rp,Iterable):
                    tgt_rp = [tgt_rp,]
                data = data.loc[data[self.tidx[1]].isin(tgt_rp)]
            return data
    
    def get_cum_repo_data(self,datapath,instruments = None,fields = None,start_date = None,end_date = None):
        df = pd.read_hdf(os.path.join(datapath,'all.h5'),"data")
        if not instruments is None:
            try:
                df = df.loc[df.index.get_level_values("stockcode").isin(instruments)]
            except KeyError:
                print('Index %s info not found')
                return pd.DataFrame()

        if (start_date is not None) & (end_date is not None):
            start_date,end_date = to_intdate(start_date),to_intdate(end_date)
            dateindices=df.index.get_level_values("create_date")
            df = df.loc[(dateindices <= end_date)&(dateindices >= start_date)]
        
        if not fields is None:
            if isinstance(fields,str):
                fields = [fields]
            df = df[fields]
        return df
        
    @print_func_time
    def consus(self,instruments,fields,foreward_type,window_days,**kws):
        path = eval('_'.join(["ashare_consus",foreward_type,window_days]))
        return self.get_repo_data(path,instruments,fields,**kws)

    @print_func_time
    def consus_rolling(self,instruments,fields,foreward_type,**kws):
        path = eval('_'.join(["ashare_consus_rolling",foreward_type]))
        return self.get_repo_data(path,instruments,fields,tidx = ["est_date"],**kws)

    @print_func_time
    def stk_rating(self,instruments,fields,window_days,**kws):
        path = eval('_'.join(["ashare_sktrating",window_days]))
        return self.get_repo_data(path,instruments,fields,tidx = ["rating_date"],**kws)
    
    @print_func_time
    def suntime_confc_stk(self,instruments,fields,**kws):
        return self.get_repo_data(suntime_confc_stk,instruments,fields,tidx = ["con_date"],**kws)

    @print_func_time
    def suntime_confc_roll_stk(self,instruments,fields,**kws):
        return self.get_repo_data(suntime_confc_roll_stk,instruments,fields,tidx = ["con_date"],**kws)

    @print_func_time
    def suntime_repofc_stk(self,instruments,fields,**kws):
        return self.get_repo_data(suntime_repofc_stk,instruments,fields,tidx = ["create_date"],**kws)

    @print_func_time
    def suntime_repofc_stk_tc(self,instruments = None,fields = None, start_date = None,end_date = None):
        return self.get_cum_repo_data(suntime_repofc_stk_tc,instruments,fields,start_date,end_date)
    
    @print_func_time
    def suntime_earning_adj(self,instruments = None,fields = None,start_date = None,end_date = None):
        return self.get_cum_repo_data(suntime_earning_adj,instruments,fields,start_date,end_date)

    @print_func_time
    def suntime_rating_adj(self,instruments = None,fields = None,start_date = None,end_date = None):
        return self.get_cum_repo_data(suntime_rating_adj,instruments,fields,start_date,end_date)

    @print_func_time
    def suntime_tgtprice_adj(self,instruments = None,fields = None,start_date = None,end_date = None):
        return self.get_cum_repo_data(suntime_tgtprice_adj,instruments,fields,start_date,end_date)
            