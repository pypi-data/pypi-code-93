try:
    #ลำดับมีผลพยายามโหลดที่ ใน folder ที่กำลัง Implement ก่อน
    #import config as con 
    from starfishX import config as con 
except:
    import starfishX.config as con

prefix = "starfishX."

if(con.__mode__=="debug"):
    prefix = ""

import numpy as np
exec("import starfishX as sx")

def checkServices():
  
 #1
 df = sx.loadHistData("aot",start="2019-01-01",end="2019-01-31")
 if(len(df)>0):
    print("loadHistData\t\t\t done.")

 #2
 df = sx.MonthlyReturn(["aot"],startDate="2016-01-01",endDate="2018-12-31",plot=False)
 if(len(df)>0):
    print("MonthlyReturn\t\t\t done.")   
    
 #3
 df = sx.listShareholders("aot")
 if(len(df)>0):
    print("listShareholders\t\t done.")

 #4    
 k = sx.findCASH("aot")
 if(not np.isnan(k)):
   print("findCASH\t\t\t done.")
 else:
   print("findCASH\t\t\t fail.")   

 #5
 df = sx.commonsizeBS("aot")
 if(len(df)>0):
    print("commonsizeBS\t\t\t done.")
    
 #6
 df = sx.commonsizeIS("aot")
 if(len(df)>0):
    print("commonsizeIS\t\t\t done.")  
    
 #7
 df = sx.getFinanceRatio(["scb","ktb"])
 if(len(df)>0):
    print("getFinanceRatio\t\t\t done.")
    
     
 #8
 df = sx.spiderCompare(["mint","cpn"],plot=False)
 if(len(df)>0):
    print("spiderCompare\t\t\t done.")     
    
 #9
 df = sx.getBalanceSheet("aot")
 if(len(df)>0):
    print("getBalanceSheet\t\t\t done.")  
    
 #10
 df = sx.getBalanceSheetCompare(["aot","mint"])
 if(len(df)>0):
    print("getBalanceSheetCompare\t\t done.") 
    
 #11
 df = sx.getMemberOfIndex(sx.indexMarket.SETHD)
 if(len(df)>0):
    print("getMemberOfIndex\t\t done.")  

 #12
 df = sx.listStockInSector("mint")
 if(len(df)>0):
    print("listStockInSector\t\t done.")   
    
 #13
 df = sx.getFundamentalInSector("delta",progress=False)
 if(len(df)>0):
    print("getFundamentalInSector\t\t done.")
    
 #14   
 symbols = ["ptt","cpf","mint","aav"]

 df = sx.loadHistData(symbols,start="2018-01-01")

 k = sx.MarkowitzProcess(df,alias=symbols,random=5000,plot=False)

 if(len(k)>0):
    print("MarkowitzProcess\t\t done.")

 #15
 df = sx.listSecurities(progress=False)
 if(len(df)>0):
    print("listSecurities\t\t\t done.")
    
   

 #16
 df = sx.findMarketCap(["aot","mint"],progress=False)
 if(len(df)>0):
    print("findMarketCap\t\t\t done.")
    
 #17
 df = sx.getIncomeStatement("aot")
 if(len(df)>0):
    print("getIncomeStatement\t\t done.")   
    
    
 #18
 df = sx.getIncomeStatementCompare(["aot","kce"])
 if(len(df)>0):
    print("getIncomeStatementCompare\t done.")    
    
 #19
 try:
  df,K = sx.DuPontROE("aot",year=2561)
  if(len(df)>0):
     print("DuPontROE\t\t\t done.")   
 except:
  if(type(df)==int):
    if(df==0):
     print("DuPontROE\t\t\t fail.") 
    
 #20
 df = sx.InterestBearingDebt("mint",viewlog=False)
 if(len(df)>0):
    print("InterestBearingDebt\t\t done.")   
    
 #21
 df = sx.DA("kce")
 if(len(df)>0):
    print("DA\t\t\t\t done.")     
    
 #22
 df = sx.getEVEBITDA("kce",year=2561)
 if(len(df)>0):
    print("getEVEBITDA\t\t\t done.")  
    
 #23
 try:
  df = sx.analyseEVEBITDA(["kce"],yearstart=2561,yearend=2562,viewlog=False)
  if(len(df)>0):
    print("analyseEVEBITDA\t\t\t done.")  
 except:
  print("analyseEVEBITDA\t\t\t fail.") 

 #24
 df = sx.morningstarGetfn("mint",sx.MStar.EarningsPerShare,printProgress=False)
 if(len(df)>0):
    print("morningstarGetfn\t\t done.")   
    
 #25
 df = sx.DividendDiscountModel("mint",year=2561,k=0.12)
 if(len(df)>0):
    print("DividendDiscountModel\t\t done.") 
    
 #26
 k = sx.governmentBond10year()
 if(type(k)==int):
   if(k==0):  
    print("governmentBond10year\t\t fail.")  
 if(type(k)==float):
    print("governmentBond10year\t\t done.")
    
 #27
 df = sx.beta("mint")
 try:
  if(len(df)>0):
    print("beta\t\t\t\t done.")  
 except:
  if(df==0):
    print("beta\t\t\t\t fail.") 

 #28
 Nday = 40
 rp = sx.linregressIndicator(["ptt","aot"],periodDay=Nday,viewlog=False,viewplot=False)
 try:
   if(len(rp)>0):
     print("linregressIndicator\t\t done.")
 except:
   if(type(rp)==int):
     print("linregressIndicator\t\t fail.")
 
 #29
 rp = sx.marketview(sx.indexMarket.SET,start="2018-01-01",viewplot=False)
 try:
   if(len(rp)>0):
     print("marketview\t\t\t done.")
 except:
   if(type(rp)==int):
     print("marketview\t\t\t fail.")

 #30
 rp = sx.marketViewForeignTrade(sx.indexMarket.SET,start="2018-01-01",viewplot=False)
 try:
   if(len(rp)>0):
     print("marketViewForeignTrade\t\t done.")
 except:
   if(type(rp)==int):
     print("marketViewForeignTrade\t\t fail.")       

 #31
 df = sx.loadHistData("aot",start="2019-01-01",Volume=True)
 symbol,dataset = sx.AnomalyDetection(df,contamination=0.01,Lastday=3)
 try:
  if(type(symbol)==str):
   print("AnomalyDetectionVolume\t\t done.")
 except:
  print("AnomalyDetectionVolume\t\t done.")      

 
 #32
 k = sx.thaibma("2017-01-01",bondtype="")
 if(type(k)==int):
   if(k==0):  
    print("thaibma\t\t\t\t fail.")  
 if(type(k)==float):
    print("thaibma\t\t\t\t done.")


 #33
 marketType = sx.indexMarket.SET
 BondType = sx.BondType.USTreasury10Year
 df = sx.EarningYieldGap(marketType,BondType,start="2019-01-01",viewlog=False,viewplot=False)
 try:
   if(len(df)>0):
       print("EarningYieldGap\t\t\t done.")
 except:
       print("EarningYieldGap\t\t\t fail.")     


 print("complete..")    