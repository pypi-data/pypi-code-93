import os
import abc

from .config import data_path
from .tools import print_func_time,to_intdate
from .utils import read_mergeh5
from collections.abc import Iterable
defualt_si = 0
defualt_ei = 1e7

ashare_cashflow = os.path.join(data_path,r'AShareCashFlow')
ashare_cashflow_q = os.path.join(data_path,r'AShareCashFlow_quarterly')
ashare_income = os.path.join(data_path,r'AShareIncome')
ashare_income_q = os.path.join(data_path,r'AShareIncome_quarterly')
ashare_balancesheet = os.path.join(data_path,r'AShareBalanceSheet')
ashare_profit_expr = os.path.join(data_path,r'AShareProfitExpress')
ashare_profit_noti = os.path.join(data_path,r'AShareProfitNotice')
ashare_ttmhis = os.path.join(data_path,r'AShareTTMHis')
ashare_holdernumber = os.path.join(data_path,r'AShareHolderNumber')
ashare_insideholder =  os.path.join(data_path,r'AShareInsideHolder')
ashare_holderdata =  os.path.join(data_path,r'AShareinstHolderDerData')
ashare_managerewr = os.path.join(data_path,r'AShareManagementHoldReward')
ashare_dividend = os.path.join(data_path,r'AShareDividend')

ashare_issuedate_pre = os.path.join(data_path,r'AShareIssuingDatePredict')
ashare_fanc_indicator = os.path.join(data_path,r'AShareFinancialIndicator')

fund_qdii_secu_portfolio =  os.path.join(data_path,r"QDIISecuritiesPortfolio")
fund_mu_fund_stkportfolio =  os.path.join(data_path,r"ChinaMutualFundStockPortfolio")

class BaseFincReportsProvider(abc.ABC):

    @abc.abstractmethod
    def get_repo_data(self,instruments,fields,start_date,end_date):
        raise NotImplementedError

class LoacalFincReportsProvider(BaseFincReportsProvider):

    def __init__(self, tidx=['ann_date','report_period']) -> None:
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
            if not ((start_date is None) | (start_date is None)):
                sd,ed = to_intdate(start_date),to_intdate(end_date)
                by = kws.get('by',tidx[0])
                data = data.loc[(data[by] >= sd) & (data[by] <= ed)]

        if self.tidx[1] in kws:
            tgt_rp = kws.get(self.tidx[1],None)
            if not isinstance(tgt_rp,Iterable):
                tgt_rp = [tgt_rp,]
            data = data.loc[data[self.tidx[1]].isin(tgt_rp)]
        return data

    @print_func_time
    def repo_cashflow(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_cashflow,instruments,fields,**kws)
    
    @print_func_time
    def repo_cashflow_q(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_cashflow_q,instruments,fields,**kws)  

    @print_func_time
    def repo_income(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_income,instruments,fields,**kws)
    
    @print_func_time
    def repo_income_q(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_income_q,instruments,fields,**kws)  

    @print_func_time
    def repo_balancesheet(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_balancesheet,instruments,fields,**kws)

    @print_func_time
    def repo_profit_expr(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_profit_expr,instruments,fields,**kws)
    
    @print_func_time
    def repo_profit_noti(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_profit_noti,instruments,fields,**kws)  

    @print_func_time
    def repo_ttmhis(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_ttmhis,instruments,fields,**kws) 
    
    @print_func_time
    def repo_holder_number(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_holdernumber,instruments,fields,tidx = ["ann_date"],**kws) 

    @print_func_time
    def repo_inside_holder(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_insideholder,instruments,fields,tidx = ["ann_date","report_period"],**kws) 

    @print_func_time
    def repo_holder_data(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_holderdata,instruments,fields,tidx = ["ann_date","report_period"],**kws) 

    @print_func_time
    def repo_manage_rewr(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_managerewr,instruments,fields,tidx = ["ann_date","end_date","manid"],**kws) 

    @print_func_time
    def repo_issuedate_pre(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_issuedate_pre,instruments,fields,**kws) 

    @print_func_time
    def repo_fanc_indicator(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_fanc_indicator,instruments,fields,**kws)

    @print_func_time
    def repo_ashare_dividend(self,instruments,fields,**kws):
        return self.get_repo_data(ashare_dividend,instruments,fields,**kws)

class LoacalFundReportsProvider(BaseFincReportsProvider):

    def __init__(self, tidx=['ann_date','prt_enddate']) -> None:
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
            if not ((start_date is None) | (start_date is None)):
                sd,ed = to_intdate(start_date),to_intdate(end_date)
                by = kws.get('by',tidx[0])
                data = data.loc[(data[by] >= sd) & (data[by] <= ed)]

        if self.tidx[1] in kws:
            tgt_rp = kws.get(self.tidx[1],None)
            if not isinstance(tgt_rp,Iterable):
                tgt_rp = [tgt_rp,]
            data = data.loc[data[self.tidx[1]].isin(tgt_rp)]
        return data

    @print_func_time
    def frepo_qdii_secuportfolio(self,instruments,fields,**kws):
        return self.get_repo_data(fund_qdii_secu_portfolio,instruments,fields,tidx = ["ann_date","enddate"],**kws) 

    @print_func_time
    def frepo_mufund_stkportfolio(self,instruments,fields,**kws):
        return self.get_repo_data(fund_mu_fund_stkportfolio,instruments,fields,**kws)

