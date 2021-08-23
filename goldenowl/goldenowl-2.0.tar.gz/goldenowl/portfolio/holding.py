import itertools
import pandas as pd
import datetime as dt
from xirr.math import xirr

class Holding:
    def __init__(self, aName, aInstPriceMap):
        self.m_name = aName;
        self.m_inst_pr_map = aInstPriceMap;
        self.m_tran_details={};

    def buyUnits(self,aUnits,aDate):
        norm_date = pd.to_datetime(aDate);
        if (norm_date in self.m_tran_details.keys()):
            self.m_tran_details[norm_date]+= aUnits;
        else:
            self.m_tran_details[norm_date]= aUnits;

    def sellUnits(self,aUnits, aDate):
        norm_date = pd.to_datetime(aDate);
        if (norm_date in self.m_tran_details.keys()):
            self.m_tran_details[norm_date]-= aUnits;
        else:
            self.m_tran_details[norm_date]= -aUnits;

    def buyAmount(self,aAmount, aDate):
        norm_date = pd.to_datetime(aDate);
        units = aAmount/self.m_inst_pr_map[norm_date];
        self.buyUnits(units, norm_date);

    def sellAmount(self,aAmount, aDate):
        norm_date = pd.to_datetime(aDate);
        units = aAmount/self.m_inst_pr_map[norm_date];
        self.sellUnits(units, norm_date);

    def getHoldingValue(self,aDate):
        norm_date = pd.to_datetime(aDate); 
        holding_units = 0;
        filtered = dict(itertools.filterfalse(lambda i:i[0] > norm_date, self.m_tran_details.items()))
        holding_units += sum(filtered.values());
        value = (self.m_inst_pr_map[norm_date])*holding_units;
        return value;

    def getXIRR(self, aDate):
        norm_date = pd.to_datetime(aDate);
        cash_flow = {key:val*self.m_inst_pr_map[key] for (key, val) in self.m_tran_details.items()};
        filtered = dict(itertools.filterfalse(lambda i:i[0] > norm_date, cash_flow.items()))
        final_val = self.getHoldingValue(aDate);
        if (norm_date in filtered.keys()):
            filtered[norm_date]-= final_val;
        else:
            filtered[norm_date]= -final_val;
        return xirr(filtered)


#Free floating functions below

def getSIPReturn(aInstPr,aFreq,aStart,aEnd):
    hldng = Holding('Calc', aInstPr);
    norm_date = pd.to_datetime(aStart);
    norm_end_date = pd.to_datetime(aEnd);
    sip_date = norm_date;

    while (not(sip_date in aInstPr.keys())):
        sip_date+=dt.timedelta(days=1);
    hldng.buyAmount(100, sip_date);

    while(sip_date < norm_end_date):
        temp_date=sip_date+dt.timedelta(days=aFreq);
        while (not(temp_date in aInstPr.keys())):
            if (temp_date >= norm_end_date):
                break;
            temp_date+=dt.timedelta(days=1);
            
        if (temp_date in aInstPr.keys()):
            sip_date = temp_date;
            hldng.buyAmount(100, sip_date);

        if (temp_date >= norm_end_date):
            break;

    return hldng.getXIRR(sip_date);
