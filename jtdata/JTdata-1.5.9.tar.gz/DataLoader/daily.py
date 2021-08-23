
#%%
import os
import abc

from .config import data_path
from .tools import print_func_time,to_intdate
from .utils import read_mergeh5
from .calendarpd import Tdcal

defualt_si = 0
defualt_ei = 1e7

ashare_eod_price = os.path.join(data_path,r'AShareEODPrices')
ashare_blocktrade = os.path.join(data_path,r'AShareBlockTrade')
ashare_derivative_indicator = os.path.join(data_path,r'AShareEODDerivativeIndicator')
ashare_dividend_record = os.path.join(data_path,r'AShareEXRightDividendRecord')
ashare_l2_indicator = os.path.join(data_path,r'AShareL2Indicators')
ashare_margin_trade = os.path.join(data_path,r'AShareMarginTrade')
ashare_money_flow = os.path.join(data_path,r'AShareMoneyFlow')
ashare_tech_indicator = os.path.join(data_path,r'AShareTechIndicators')
ashareyield = os.path.join(data_path,r'AShareYield')

ashare_dly_specret = os.path.join(data_path,r"CNE5_100_Asset_DlySpecRet")
ashare_dly_prices = os.path.join(data_path,r"CNE5_Daily_Asset_Price")
ashare_rates = os.path.join(data_path,r"CNE5_Rates")
ashare_exposure = os.path.join(data_path,r"CNE5S_100_Asset_Exposure")
ashare_fact_cov = os.path.join(data_path,r"CNE5S_100_Covariance")
ashare_fact_ret = os.path.join(data_path,r"CNE5S_100_DlyFacRet")
ashare_assdata = os.path.join(data_path,r"CNE5S_100_Asset_Data")

aswsindexeod = os.path.join(data_path,r'ASWSIndexEOD')
aindex_eod_price = os.path.join(data_path,r'AIndexEODPrices')
aindex_idueodcitics = os.path.join(data_path,r'AIndexIndustriesEODCITICS')
aindex_freeweight = os.path.join(data_path,r'AIndexFreeWeight')
cmf_indexeod = os.path.join(data_path,r"CMFIndexEOD")

shszstockholding = os.path.join(data_path,r"SHSZstockhoding")
#%%
class BaseDailyTSInfoProvider(abc.ABC):

    @abc.abstractmethod
    def get_daily_data(self,instruments,fields,start_date,end_date):
        raise NotImplementedError


class TradeDayInfoProvider(BaseDailyTSInfoProvider):
    """ Intensive time sereis data with trade day as index """

    tidx = 'trade_dt'
    def get_daily_data(self,datapath,instruments,fields,start_date,end_date,freq = "Tdays",tidx = None):
        if isinstance(instruments,str):
            instruments = [instruments]
        path = os.path.join(datapath,'merged.h5')
        start_index,end_index = Tdcal.locate_index(start_date,end_date,freq = freq)
        if tidx is None:
            tidx = self.tidx # 判断是否使用默认的tidx
        return read_mergeh5(path,instruments,fields,start_index,end_index,tidx)
    
    def get_sparse_daily_data(self,datapath,instruments,**kws):
        if isinstance(instruments,str):
            instruments = [instruments]
        tidx = kws.get("tidx",self.tidx)            # 判断是否使用默认的tidx
        defualt_si,defualt_ei = 0,1e7
        path = os.path.join(datapath,'merged.h5')
        fields = kws.get("fields",None)
        data = read_mergeh5(path,instruments,fields,defualt_si,defualt_ei,tidx)
        if data.empty:
            return data
        if ("start_date" in kws)&("end_date" in kws):
            start_date,end_date = kws.get("start_date"),kws.get("end_date")
            sd,ed = to_intdate(start_date),to_intdate(end_date)
            data = data.loc[(data[self.tidx]>=sd)&(data[self.tidx]<=ed)]
        return data

    @print_func_time
    def get_daily_share_data(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_eod_price,instruments,fields,start_date,end_date)

    @print_func_time
    def get_daily_share_deridi(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_derivative_indicator,instruments,fields,start_date,end_date,freq = "Adays",tidx="ann_date") # derivative 是Adays

    @print_func_time
    def get_daily_share_l2idi(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_l2_indicator,instruments,fields,start_date,end_date)

    @print_func_time
    def get_daily_moneyflow(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_money_flow,instruments,fields,start_date,end_date)

    @print_func_time
    def get_daily_techindi(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_tech_indicator,instruments,fields,start_date,end_date)

    @print_func_time
    def get_daily_yield(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashareyield,instruments,fields,start_date,end_date)

    @print_func_time
    def get_daily_index_data(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(aindex_eod_price,instruments,fields,start_date,end_date)

    @print_func_time
    def get_daily_index_industries(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(aindex_idueodcitics,instruments,fields,start_date,end_date)

    @print_func_time
    def get_daily_aswsindexeod(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(aswsindexeod,instruments,fields,start_date,end_date)
    
    @print_func_time
    def get_daily_cmfidxeod(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(cmf_indexeod,instruments,fields,start_date,end_date)

    @print_func_time
    def get_daily_dly_specret(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_dly_specret ,instruments,fields = fields ,start_date = start_date,end_date = end_date)

    @print_func_time
    def get_daily_dly_prices(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_dly_prices,instruments,fields = fields ,start_date = start_date,end_date = end_date)

    @print_func_time
    def get_daily_rates(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_rates,instruments,fields = fields ,start_date = start_date,end_date = end_date)

    @print_func_time
    def get_daily_ashare_exposure(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_exposure,instruments,fields = fields ,start_date = start_date,end_date = end_date)

    @print_func_time
    def get_barra_dly_data(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_assdata,instruments,fields = fields ,start_date = start_date,end_date = end_date)

    @print_func_time
    def get_daily_ashare_faccov(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_fact_cov,instruments,fields = fields ,start_date = start_date,end_date = end_date)
    
    @print_func_time
    def get_daily_factorRet(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(ashare_fact_ret,instruments,fields = fields ,start_date = start_date,end_date = end_date)

    @print_func_time
    def get_daily_shsz_stkholding(self,instruments,fields,start_date,end_date):
        return self.get_daily_data(shszstockholding,instruments,fields = fields ,start_date = start_date,end_date = end_date)

    @print_func_time
    def get_daily_indexweight(self,instruments,**kws):
        df = self.get_sparse_daily_data(aindex_freeweight,instruments,**kws)
        df['stockcode'] = df['stockcode'].apply(lambda x: bytes.decode(x))
        return df
    
    @print_func_time
    def get_daily_share_divdrec(self,instruments,fields,start_date,end_date):
        return self.get_sparse_daily_data(ashare_dividend_record,instruments,fields = fields ,start_date = start_date,end_date = end_date)
    
    @print_func_time
    def get_daily_blocktrade(self,instruments,fields,start_date,end_date):
        return self.get_sparse_daily_data(ashare_blocktrade,instruments,fields = fields ,start_date = start_date,end_date = end_date)

    @print_func_time
    def get_daily_margintrade(self,instruments,fields,start_date,end_date):
        return self.get_sparse_daily_data(ashare_margin_trade,instruments,fields = fields ,start_date = start_date,end_date = end_date)


if __name__ == '__main__':
    TradeDayInfoProvider().get_daily_indexweight()