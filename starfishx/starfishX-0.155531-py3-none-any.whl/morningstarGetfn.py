#morningstarGetfn.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

 

########################################
from enum import Enum
class MStar(Enum):
 Revenue = "Revenue"
 GrossMargin = "Gross Margin %"
 OperatingIncome = "Operating Income"
 OperatingMargin = "Operating Margin %"
 NetIncome = "Net Income"
 EarningsPerShare = "Earnings Per Share"
 Dividends = "Dividends"
 PayoutRatio = "Payout Ratio %"
 Shares = "Shares"
 BookValuePerShare = "Book Value Per Share"
 OperatingCashFlow = "Operating Cash Flow"
 CapSpending = "Cap Spending"
 FreeCashFlow = "Free Cash Flow"
 FreeCashFlowPerShare = "Free Cash Flow Per Share"
 WorkingCapital = "Working Capital"
 
    
 TaxRate = "Tax Rate %"   
 NetMargin = "Net Margin %"
 AssetTurnoverAvg = "Asset Turnover (Average)"
 ROA = "Return on Assets %"
 FinancialLeverage = "Financial Leverage"
 ROE = "Return on Equity %"
 ROIC = "Return on Invested Capital %"
 InterestCoverage = "Interest Coverage"

    
######## main URL http://financials.morningstar.com/ratios/r.html?t=mint&region=THA&culture=en-us    
########################################   
def morningstarGetfn(symbol,Indicates,printProgress=False):
  """
    ดึงข้อมูลย้อนหลัง 10 ปีจาก morningstar
 
    Returns DataFrame
    
    arg1 (str): ตัวย่อของหุ้น เช่น "aot","cpall","ptt"

    arg2 (class MStar): ตัวคัดกรองที่ต้องการ เช่น ปันผลใช้ sx.MStar.Dividends
    
  """ 

  if(not isinstance(Indicates, MStar)):
    print("Data Type MStar Not Match")
    return 0
    
  IndicatesCheck = Indicates.value

  
  
  keywordlist = ["Tax Rate","Net Margin","Asset Turnover (Average)",
                "Return on Assets","Financial Leverage","Return on Equity",
                "Return on Invested Capital","Interest Coverage"]
  
  #if("Return on Equity" in Indicates):
  if any(s in IndicatesCheck for s in keywordlist):  
    #filename = "getKeyStatPart"
    #zoneU = True
    #print("zone2")
    return morningstarGetfnPart2inWeb(symbol,Indicates,printProgress)
  else:
    filename = "getFinancePart"
  
  Indicates = Indicates.value
  
  if(printProgress):
    print("Process.."+Indicates)
    
    
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
  symbolMofi = symbol.replace("&","%26")  
   # r = requests.get("http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=?&t=XBKK:KTC&region=tha&culture=en-US&cur=",headers=headers)


  r = requests.get("http://financials.morningstar.com/finan/financials/"+filename+".html?&callback=?&t=XBKK:"+symbol+"&region=tha&culture=en-US",headers=headers, timeout=5)
    
  #r.content
  soup = BeautifulSoup(r.content, "lxml")   
  
 
  data = soup.find_all("table")  
   
    
  IndicatesDS = []
  year_ds = []
 
  if(len(data)==0):
    print("ไม่พบข้อมูล")
    return 0
  
  meetData = False
  for i in data[0].find_all("tr"):    
    k = i.find_all("th")
    if(len(k)>=10):
      for j in k:
         datatmp = j.text.replace("-01","")
         datatmp = datatmp.replace("-02","") 
         datatmp = datatmp.replace("-03","")
         datatmp = datatmp.replace("-04","")    
         datatmp = datatmp.replace("-05","")
         datatmp = datatmp.replace("-06","")
         datatmp = datatmp.replace("-07","")
         datatmp = datatmp.replace("-08","")
         datatmp = datatmp.replace("-09","")
         datatmp = datatmp.replace("-10","")
         datatmp = datatmp.replace("-11","")
         datatmp = datatmp.replace("-12","")
         
          
          
         year_ds.append(datatmp)    
        
    if(Indicates in i.text and meetData==False):
      meetData = True  
      k = i.find_all("td")
      for j in k:   
         if("—" in j.text):
           IndicatesDS.append(np.NAN) 
         else:   
           if(j.text !=""): 
             m = j.text
             m = m.replace(",","")
             IndicatesDS.append(float(m))
  
  year_ds.pop(len(year_ds)-1)
  IndicatesDS.pop(len(IndicatesDS)-1) 
  year_ds.pop(0)

  year_ds_np = np.array(year_ds)
  year_ds = year_ds_np.astype(np.int)  
    
  df = pd.DataFrame({"year":year_ds,Indicates:IndicatesDS})  
  df = df.set_index("year")  
  return df    


def morningstarGetfnPart2inWeb(symbol,Indicates,printProgress=False):
  if(not isinstance(Indicates, MStar)):
    print("Data Type MStar Not Match")
    return 0
    
  Indicates = Indicates.value

  filename = "getKeyStatPart"
  
  if(printProgress):
    print("Process.."+Indicates)
    
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
  symbolMofi = symbol.replace("&","%26")  
   # r = requests.get("http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=?&t=XBKK:KTC&region=tha&culture=en-US&cur=",headers=headers)

  url = "http://financials.morningstar.com/finan/financials/"+filename+".html?&callback=?&t=XBKK:"+symbol+"&region=tha&culture=en-US"
  r = requests.get(url,headers=headers, timeout=5)
 
  soup = BeautifulSoup(r.content, "lxml")   
  

  dataz = soup.find_all("tbody")
  if(len(dataz)==0):
    print("ไม่พบข้อมูล")
    return 0
    
  data = dataz[1]#,{"class" : "classr_table1 text2 print97"})
  #data = data[1]
  #print(url) 

  #################################################
  IndicatesDS = []
  year_ds = []

  row = soup.find_all("thead")[1].find_all("th")
  cnt = 0  
  for i in row:
    if(cnt>0 and cnt <len(row)-1):
      year_ds.append(i.text.replace("-12",""))   
    cnt+=1
    
    
  for i in data:
    #if("table" in i.find_all("td")[0].text):
    rowDataKey = i.find_all("th")
    if(len(rowDataKey))>0:
       if(Indicates in rowDataKey[0].text):
         if(len(i.find_all("td")[0].find_all("div"))==0):
         #for(k in i):
         #  print(k)
          for k in i.find_all("td"):
            if("—" in k.text):
              IndicatesDS.append(np.NAN) 
            else:
              IndicatesDS.append(float(k.text))
            
  ################################################# 
  IndicatesDS.pop(len(IndicatesDS)-1)
  df = pd.DataFrame({"year":year_ds,Indicates:IndicatesDS})  
  df = df.set_index("year") 
  return df 