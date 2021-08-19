try:
    #ลำดับมีผลพยายามโหลดที่ ใน folder ที่กำลัง Implement ก่อน
    from starfishX import config as con 
    #print("Dev")
except:
    #print("Debug")
    import starfishX.config as con

prefix = "starfishX."

if(con.__mode__=="debug"):
    prefix = ""


exec("from "+prefix+"starfishXfn import setTHforPlot")

#from starfishX.starfishXfn import loadHistData
exec("from "+prefix+"starfishXfn import loadHistData")

#from starfishX.starfishXfn import MonthlyReturn
exec("from "+prefix+"starfishXfn import MonthlyReturn")

#from starfishX.starfishXfn import listShareholders
exec("from "+prefix+"starfishXfn import listShareholders")

#from starfishX.starfishXfn import findCASH
exec("from "+prefix+"starfishXfn import findCASH")

#from starfishX.starfishXfn import commonsizeBS
exec("from "+prefix+"starfishXfn import commonsizeBS")

#from starfishX.starfishXfn import commonsizeIS
exec("from "+prefix+"starfishXfn import commonsizeIS")

#from starfishX.starfishXfn import getFinanceRatio
exec("from "+prefix+"starfishXfn import getFinanceRatio")

#from starfishX.starfishXfn import spiderCompare
exec("from "+prefix+"starfishXfn import spiderCompare")

#from starfishX.starfishXfn import getBalanceSheet
exec("from "+prefix+"starfishXfn import getBalanceSheet")

#from starfishX.starfishXfn import getBalanceSheetCompare
exec("from "+prefix+"starfishXfn import getBalanceSheetCompare")

#exec("from "+prefix+"starfishXfn import getProfitAbility")  #ยกเลิกก่อน  เพราะ wsj หยุดให้บริการแบบ free
exec("from "+prefix+"getProfitAbility import getProfitAbility")  #ยกเลิกก่อน  เพราะ wsj หยุดให้บริการแบบ free

#from starfishX.starfishXfn import getMemberOfIndex
exec("from "+prefix+"starfishXfn import getMemberOfIndex")

#from starfishX.starfishXfn import listStockInSector
exec("from "+prefix+"starfishXfn import listStockInSector")

#from starfishX.starfishXfn import getFundamentalInSector
exec("from "+prefix+"starfishXfn import getFundamentalInSector")

#from starfishXfn import evperebitda #ยกเลิกก่อน

#from starfishX.starfishXfn import MarkowitzProcess
exec("from "+prefix+"starfishXfn import MarkowitzProcess")

#from starfishX.listSecurities import listSecurities
exec("from "+prefix+"listSecurities import listSecurities")

#from starfishX.findMarketCap import findMarketCap
exec("from "+prefix+"findMarketCap import findMarketCap")

#from starfishX.incomestatement import getIncomeStatement
exec("from "+prefix+"incomestatement import getIncomeStatement")

#from starfishX.incomestatement import getIncomeStatementCompare
exec("from "+prefix+"incomestatement import getIncomeStatementCompare")

#from starfishX.DuPontROE import DuPontROE
exec("from "+prefix+"DuPontROE import DuPontROE")

#from starfishX.InterestBearingDebt import InterestBearingDebt
exec("from "+prefix+"InterestBearingDebt import InterestBearingDebt")

#from starfishX.depreciationAndAmortisation import DA
exec("from "+prefix+"depreciationAndAmortisation import DA")

#from starfishX.getEVEBITDA import getEVEBITDA
exec("from "+prefix+"getEVEBITDA import getEVEBITDA")

#from starfishX.getEVEBITDA import getEVEBITDA
exec("from "+prefix+"getEVEBITDA import getEVEBIT")

#from starfishX.getEVEBITDA import analyseEVEBITDA
exec("from "+prefix+"getEVEBITDA import analyseEVEBITDA")

#from starfishX.morningstarGetfn import MStar
exec("from "+prefix+"morningstarGetfn import MStar")

#from starfishX.morningstarGetfn import morningstarGetfn
exec("from "+prefix+"morningstarGetfn import morningstarGetfn")

#from starfishX.DividendDiscountModel import DividendDiscountModel
exec("from "+prefix+"DividendDiscountModel import DividendDiscountModel")

#from starfishX.Ke import governmentBond10year
exec("from "+prefix+"Ke import governmentBond10year")

#from starfishX.Ke import beta
exec("from "+prefix+"Ke import beta")

#from starfishX.checkServices import checkServices
exec("from "+prefix+"checkServices import checkServices")

#from starfishX.indicator import linregressIndicator
exec("from "+prefix+"indicator import linregressIndicator")

#from starfishX.indexMarket import indexMarket
exec("from "+prefix+"indexMarket import indexMarket")

#from starfishX.marketview  import marketview
exec("from "+prefix+"marketview import marketview")

#from starfishX.marketview  import marketview
exec("from "+prefix+"marketview import marketViewForeignTrade")

#from starfishX.AD  import AnomalyDetectionVolume
exec("from "+prefix+"AD import AnomalyDetection")

#from starfishX.AD  import AnomalyDetectionVolume
exec("from "+prefix+"AD import anomalyDetectionAgloType")

#from starfishX.AD  import AnomalyDetectionVolume
exec("from "+prefix+"AD import anomalyDetectionDataType")

#from starfishX.AD  import AnomalyDetectionVolume
exec("from "+prefix+"AD import viewAnomalyDetectionReportAllType")

#from starfishX.Ke import governmentBond10year
exec("from "+prefix+"Ke import thaibma")
exec("from "+prefix+"Ke import thaibma_series")
exec("from "+prefix+"Ke import BondType") #enum bondType

exec("from "+prefix+"EYG import EarningYieldGap")

exec("from "+prefix+"EYG import twoTenSpread")
exec("from "+prefix+"EYG import utilityTwinXPlot")


exec("from "+prefix+"starfishXfn import RelativeStrengthRank")
exec("from "+prefix+"starfishXfn import RelativeStrength_hist")
exec("from "+prefix+"starfishXfn import RelativeStrength_hist_with_progress1")
exec("from "+prefix+"starfishXfn import RelativeStrength_hist_with_progress2")

exec("from "+prefix+"Elder import elderSafezone")


exec("from "+prefix+"openInterest import listSSF")   
exec("from "+prefix+"openInterest import OpenInterestContracts")

exec("from "+prefix+"moc import mocExport")

exec("from "+prefix+"marketValueDaily import marketValueDaily")

exec("from "+prefix+"marketValueDaily import getTotalShare")

exec("from "+prefix+"shortsale import shortsale")
exec("from "+prefix+"shortsale import shortsaleByDay")


#from starfishX.starfishXfn import loadHistData
exec("from "+prefix+"starfishXfn import fillHistData")

exec("from "+prefix+"utility import *")

exec("from "+prefix+"risk_kit import *")


exec("from "+prefix+"nvdr import getNVDRVolume")
exec("from "+prefix+"nvdr import reduceXtickfrequency") 


exec("from "+prefix+"news_api import news_api")
exec("from "+prefix+"news_api import NewsTypeMatch")

#exec("from "+prefix+"sentimentAnalysis import sentimentAnalysis")


exec("from "+prefix+"ShareholdersNow import ShareholdersNow")
exec("from "+prefix+"ShareholdersNow import ShareholdersHist")

exec("from "+prefix+"holidayMarket import getHolidayMarket")

exec("from "+prefix+"ipoStat import ipoStat")


#from starfishX.starfishXfn import loadHistData
exec("from "+prefix+"loadHistData_v2 import loadHistData_v2")
exec("from "+prefix+"loadHistData_v2 import timeFrame")

exec("from "+prefix+"getWarrant import getWarrant")

__version__ = 0.155531  #19 สิงหาคม 2564 update 0.155531

__doc__ = """starfishX Version จัดเตรียมข้อมูลสำหรับประมวลผลการลงทุนในตลาดหุ้นไทย """