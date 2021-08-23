
#%%
import os
import abc
import pandas as pd
from datetime import datetime
from .config import data_path,stk_uiverse
from .tools import print_func_time,to_intdate

aindex_member = os.path.join(data_path,r'AIndexMembers')
aindex_membercitics = os.path.join(data_path,r'AIndexMembersCITICS')
aindex_altermember = os.path.join(data_path,r'AIndexAlternativeMembers')

ashare_description = os.path.join(data_path,r'AShareDescription')
ashare_st = os.path.join(data_path,r'AShareST')
ashare_suspension = os.path.join(data_path,r'AShareTradingSuspension')
suntime_typedict = os.path.join(data_path,r'RPT_RATING_COMPARE')

ashare_idu_citics = os.path.join(data_path,r"AShareIndustriesClass_CITICS")
ashare_idu_cs = os.path.join(data_path,r"AShareIndustriesClass_CS")
ashare_idu_gics =os.path.join(data_path,r"AShareIndustriesClass_GICS")
ashare_idu_sw = os.path.join(data_path,r'AShareIndustriesClass_SW')
ashare_idu_wind = os.path.join(data_path,r'AShareIndustriesClass_WIND')
ashare_idu_code = os.path.join(data_path,r'AShareIndustriesCode')

class BaseStatusInfoProvider(abc.ABC):

    @abc.abstractmethod
    def get_status_data(self,instruments,fields,start_date,end_date):
        raise NotImplementedError

class LocalIndexStatusProvider(BaseStatusInfoProvider):
    """ index, stockcode, indate, outdate"""

    def get_status_data(self,datapath,indexcode,start_date =None,end_date = None):
       
        df = pd.read_hdf(os.path.join(datapath,'all.h5'),"data")
        try:
            df = df.loc[indexcode]
            dfcp = df['outdate'].fillna(int(datetime.now().strftime("%Y%m%d")))
            if (start_date is not None) & (end_date is not None):
                start_date,end_date = to_intdate(start_date),to_intdate(end_date)
                df = df.loc[(df.indate <= end_date)&(dfcp >= start_date)]
            return df
        except KeyError:
            print('Index %s info not found'%indexcode)
            return pd.DataFrame()
    
    @print_func_time
    def index_member(self,indexcode,start_date =None,end_date = None):
        """ AIndexMembers """
        return self.get_status_data(aindex_member,indexcode,start_date,end_date)
    
    @print_func_time
    def index_member_citics(self,indexcode,start_date =None,end_date = None):
        """ AIndexMembersCITICS """
        return self.get_status_data(aindex_membercitics,indexcode,start_date ,end_date)
    
    @print_func_time
    def index_member_alternative(self,indexcode,start_date =None,end_date = None):
        """AIndexAlternativeMembers"""
        return self.get_status_data(aindex_altermember,indexcode,start_date ,end_date)


    
class LocalInstStatusProvider(BaseStatusInfoProvider):
    """ index, stockcode, indate, outdate"""

    def get_status_data(self,datapath,stkcodes,fields = None):
        path = os.path.join(datapath,'all.h5')
        df = pd.read_hdf(path,'data')

        if stkcodes:
            if isinstance(stkcodes,str):
                stkcodes = [stkcodes,]
            df = df.loc[df.index.isin(stkcodes)]
            if fields:
                df = df[fields]
        df = df.dropna(how='all',axis=0)
        return df

    @print_func_time
    def list_instrument(self,univ,start_date,end_date):
        start_date,end_date = to_intdate(start_date),to_intdate(end_date)
        if univ == 'all':
            path = os.path.join(ashare_description,'all.h5')
            df = pd.read_hdf(path,'data')
            dfcp = df['delistdate'].fillna(int(datetime.now().strftime("%Y%m%d")))
            if (start_date is not None) & (end_date is not None):
                start_date,end_date = to_intdate(start_date),to_intdate(end_date)
                df = df.loc[(df.listdate <= end_date)&(dfcp >= start_date)]
            return df
        else:
            univ = stk_uiverse.get(univ)
            IdxSP = LocalIndexStatusProvider()
            return IdxSP.index_member(univ,start_date,end_date).set_index("stockcode")

    @print_func_time
    def ashare_ipodate(self,stkcode,fields = None):
        """ AIndexMembers """
        return self.get_status_data(ashare_description,stkcode,fields)

    @print_func_time
    def ashare_st(self,stkcode,fields = None):
        """ AIndexMembers """
        return self.get_status_data(ashare_st,stkcode,fields)
            
    @print_func_time
    def ashare_suspension(self,stkcode,fields = None):
        """ AIndexMembers """
        return self.get_status_data(ashare_suspension,stkcode,fields)   

    @print_func_time
    def suntime_typedict(self,organcode,fields = None):
        """RPT_RATING_COMPARE"""
        return self.get_status_data(suntime_typedict,organcode,fields)   

class LocalIndustryMemberProvider:

    def get_indexmember(self,datapath,stockcode = None,level = None):
        """ indexmenber reader """
        path = os.path.join(datapath,'all.h5')
        df = pd.read_hdf(path,'data')
        if level:
            df = df[[level, "entry_date", "remove_date"]]
        if stockcode:
            df = df.loc[stockcode]
        return df

    @print_func_time
    def Industrycompo_citics(self,stockcode = None,level = None):
        return self.get_indexmember(ashare_idu_citics,stockcode,level)

    @print_func_time
    def Industrycompo_sw(self,stockcode = None,level = None):
        return self.get_indexmember(ashare_idu_sw,stockcode,level)

    @print_func_time
    def Industrycompo_cs(self,stockcode = None,level = None):
        return self.get_indexmember(ashare_idu_cs,stockcode,level)

    @print_func_time
    def Industrycompo_gics(self,stockcode = None,level = None):
        return self.get_indexmember(ashare_idu_gics,stockcode,level)

    @print_func_time
    def Industrycompo_wind(self,stockcode = None,level = None):
        return self.get_indexmember(ashare_idu_wind,stockcode,level)
    
    @print_func_time
    def Industrycodes(self):
        return pd.read_hdf(os.path.join(ashare_idu_code,"all.h5"),"data")
