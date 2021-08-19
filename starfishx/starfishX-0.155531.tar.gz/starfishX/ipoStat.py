#IPO_stat
#IPO Performance


import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import json

def ipoStat(start,end): 
 start = str(start)
 end = str(end)   
 '''
 สถิติหุ้น IPO
 start (string)  : ช่วงเวลาเริ่มต้น ใส่เป็นปี คศ. เช่น 2000
 end   (string)  : ช่วงเวลาเริ่มต้น ใส่เป็นปี คศ. เช่น 2000
 '''   
 #ipo-performance
 url = 'https://api.settrade.com/api/ipo/highlight/list?market=&industry=&type=&faId=&fromYear='+start+'&toYear='+end+'&language=th'

 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 r = requests.get(url,headers=headers, timeout=5)
 soup = BeautifulSoup(r.content, "lxml")  

 #####
 JSONData = soup.find_all('p')[0].text

 #####
 storedata = json.loads(JSONData)
 ipoDS = (storedata['ipoHighlights'])
 #####

 symbolDS = []
 marketDS = []
 industryDS = []
 firstTradeDateDS = []
 ipoPriceDS = []
 financialAdvisorsDS = []
 firstTradePriceCloseDS = []
 firstTradePriceOpenDS = []
 ipoMarketCapDS = []
 ipoPEDS = []
 ipoPBVDS = []
 for i in ipoDS:
   symbol = i['symbol']
   market = i['market']
   industry = i['industry']
   firstTradeDate = i['firstTradeDate'] 
   firstTradeDate = pd.to_datetime(firstTradeDate.split('T')[0])
   ipoPrice = float(i['ipoPrice'])
   firstTradePriceClose = float(i['firstTradePrice']['close'])
   firstTradePriceOpen = float(i['firstTradePrice']['open'])
   
 
   ipoMarketCap = float(i['ipoStatistic']['marketCap'])
   try: 
    ipoPE = float(i['ipoStatistic']['pe'])
   except:
    ipoPE = np.NaN
    
   try: 
    ipoPBV = float(i['ipoStatistic']['pbv']) 
   except:
    ipoPBV = np.NaN
 
    
   try:
    financialAdvisors = np.array(i['financialAdvisors']).tolist()
    if(len(financialAdvisors)>1):
     t = financialAdvisors[0]
     for i in range(1,len(financialAdvisors)):
       t=t+'@'+(financialAdvisors[i])
     financialAdvisorsContext = t
    else:
     financialAdvisorsContext = financialAdvisors[0]
   except:
    financialAdvisorsContext = i['financialAdvisors'] 
    
   symbolDS.append(symbol)
   marketDS.append(market)
   industryDS.append(industry)
   firstTradeDateDS.append(firstTradeDate)
   ipoPriceDS.append(ipoPrice) 
   firstTradePriceCloseDS.append(firstTradePriceClose) 
   firstTradePriceOpenDS.append(firstTradePriceOpen) 

   financialAdvisorsDS.append(financialAdvisorsContext) 
   ipoMarketCapDS.append(ipoMarketCap)
   ipoPEDS.append(ipoPE)
   ipoPBVDS.append(ipoPBV)

  ############################  
 df = pd.DataFrame({'symbol':symbolDS,
                    'market':marketDS,
                    'industry':industryDS,
                    'ipoPrice':ipoPriceDS,
                    'ipoMarketCap':ipoMarketCapDS,
                    'ipoPE':ipoPEDS,
                    'ipoPBV':ipoPBVDS,
                    'firstTradeDate':firstTradeDateDS,
                    'firstTradePriceOpen':firstTradePriceOpenDS,
                    'firstTradePriceClose':firstTradePriceCloseDS,
                    'financialAdvisors':financialAdvisorsDS})

 ###########
 # 
 # 
 #
 df = df.sort_values('firstTradeDate')
 df = df.set_index('symbol')
 return df                   