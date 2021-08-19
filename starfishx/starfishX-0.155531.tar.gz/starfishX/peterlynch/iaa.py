import requests
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np 

def getAnalystForecast(symbol):
    symbol = symbol.replace("&","%26") 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
    url = "https://www.settrade.com/AnalystConsensus/C04_10_stock_saa_p1.jsp?txtSymbol="+symbol
    r = requests.post(url,headers=headers, timeout=5)
    soup = BeautifulSoup(r.content, "lxml")  

    ct = soup.find_all("table",{"class":"table table-info"})  
    if(len(ct)==0):
       return 0
 
    broker_ds = []
    targetPrice_ds = []
    tr = ct[0].find_all("tr") 
    for i in tr:
       td = i.find_all("td")
       if(len(td)>0):
          data = (td[1].text)
          price = (td[9].text)
          try:
            float(data)
          except:
            data = data.strip()
            if(data!="-"):  
              broker_ds.append(data)
              try:
                targetPrice_ds.append(float(price))
              except:
                targetPrice_ds.append(np.NaN)


    return pd.DataFrame({"Broker":broker_ds,"Target Price":targetPrice_ds})        