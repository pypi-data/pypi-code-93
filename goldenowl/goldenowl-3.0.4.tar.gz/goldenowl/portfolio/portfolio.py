import itertools
import pandas as pd
import datetime as dt
from xirr.math import xirr
import goldenowl.asset.asset as at
import goldenowl.portfolio.holding as hd

class Portfolio:
    def __init__(self, aName, aAssetRatioList):
        self.m_name = aName;
        self.m_holdingMap={asset.getName(): hd.Holding(asset.getName(), asset) for asset, ratio in aAssetRatioList};
        self.m_assetRatioMap={asset.getName(): ratio for asset, ratio in aAssetRatioList}
        self.m_cashFlow = {};

    def rebalance(self, aDate):
        tot_amount = 0;
        norm_date = pd.to_datetime(aDate);
        for a, hld in self.m_holdingMap.items():
            tot_amount += hld.getValue(aDate);

        if (tot_amount == 0):
            return;

        cur_ratio = {ast: hold.getValue(aDate)/tot_amount for ast, hold in self.m_holdingMap.items() };
        adj_ratio = {key: val - cur_ratio[key] for key, val in self.m_assetRatioMap.items() };
        for astName, hldObj in self.m_holdingMap.items():
            ratio = adj_ratio[astName];
            if ratio > 0:
                hldObj.buyAmount(tot_amount*ratio, aDate);
                self.m_cashFlow[norm_date] = tot_amount*ratio;
            else:
                hldObj.sellAmount(-1*tot_amount*ratio, aDate);
                self.m_cashFlow[norm_date] = tot_amount*ratio;


    def addAmount(self, aAmount, aDate):
        norm_date = pd.to_datetime(aDate);
        for asset, ratio in self.m_assetRatioMap.items():
            self.m_holdingMap[asset].buyAmount(aAmount * ratio, aDate);
        self.m_cashFlow[norm_date] = aAmount;

    def removeAmount(self, aAmount, aDate):
        norm_date = pd.to_datetime(aDate);
        for asset, ratio in self.m_assetRatioMap.items():
            self.m_holdingMap[asset].sellAmount(aAmount * ratio, aDate);
        self.m_cashFlow[norm_date] = -aAmount;

    def getValue(self, aDate):
        value = 0;
        for asset, holding in self.m_holdingMap.items():
            value += holding.getValue(aDate);
        return value;
    
    def getXIRR(self, aDate):
        norm_date = pd.to_datetime(aDate);
        cash_flow =self.m_cashFlow;
        filtered = dict(itertools.filterfalse(lambda i:i[0] > norm_date, cash_flow.items()))
        final_val = self.getValue(aDate);
        if (norm_date in filtered.keys()):
            filtered[norm_date]-= final_val;
        else:
            filtered[norm_date]= -final_val;
        return xirr(filtered)


#Free floating functions below

def getSIPReturn(aInstrRatioList, aSipFreq, aRebalanceFreq, aStart, aEnd):
    prtf = Portfolio('Calc', aInstrRatioList);
    norm_date = pd.to_datetime(aStart);
    norm_end_date = pd.to_datetime(aEnd);
    sip_date = norm_date;
    rebal_date = norm_date;

    while(sip_date < norm_end_date):
        prtf.addAmount(100, sip_date);
        sip_date+=dt.timedelta(days=aSipFreq);

    while(rebal_date < norm_end_date):
        prtf.rebalance(rebal_date);
        rebal_date+=dt.timedelta(days=aRebalanceFreq);

    return prtf.getXIRR(norm_end_date);

