import itertools
import pandas as pd
import datetime as dt
from xirr.math import xirr
import goldenowl.asset.asset

class Holding:
    def __init__(self, aName, aAsset):
        self.m_name = aName;
        self.m_inst_pr_map = aAsset;
        self.m_tran_details={};

    def getName(self):
        return self.m_name;

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
        inst_val = self.m_inst_pr_map.getValue(norm_date);
        if (inst_val == 0):
            return;
        units = aAmount/inst_val;
        self.buyUnits(units, norm_date);

    def sellAmount(self,aAmount, aDate):
        norm_date = pd.to_datetime(aDate);
        inst_val = self.m_inst_pr_map.getValue(norm_date);
        if (inst_val == 0):
            return;
        units = aAmount/inst_val;
        self.sellUnits(units, norm_date);

    def getValue(self,aDate):
        norm_date = pd.to_datetime(aDate); 
        holding_units = 0;
        filtered = dict(itertools.filterfalse(lambda i:i[0] > norm_date, self.m_tran_details.items()))
        holding_units += sum(filtered.values());
        value = (self.m_inst_pr_map.getValue(norm_date))*holding_units;
        return value;

    def getXIRR(self, aDate):
        norm_date = pd.to_datetime(aDate);
        cash_flow = {key:val*self.m_inst_pr_map.getValue(key) for (key, val) in self.m_tran_details.items()};
        filtered = dict(itertools.filterfalse(lambda i:i[0] > norm_date, cash_flow.items()))
        final_val = self.getValue(aDate);
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

    while(sip_date < norm_end_date):
        hldng.buyAmount(100, sip_date);
        sip_date+=dt.timedelta(days=aFreq);

    return hldng.getXIRR(norm_end_date);
