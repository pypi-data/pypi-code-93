#pehistory.py

import requests
from bs4 import BeautifulSoup
import re
import json
import numpy as np
import pandas as pd

def getPEHistory(symbol):
 symboltmp = symbol.replace("&","%26")
 url = "http://financials.morningstar.com/valuate/valuation-history.action?&t=XBKK:"+symboltmp+"&region=tha&culture=en-US&cur=&type=price-earnings"
    
 #symboltmp = symbol.replace("&","%26") 
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 #url = "https://www.set.or.th/set/factsheet.do?symbol="+symboltmp+"&ssoPageId=3&language=th&country=TH"
 r = requests.post(url,headers=headers, timeout=5)
 soup = BeautifulSoup(r.content, "lxml") 

 #######
 regex = "ticks.*tickFormatter"
 p = re.findall(regex,soup.script.text,re.DOTALL)
 p = p[0].replace("ticks:","")
 p = p.replace("\n","")
 p = p.replace("\t","")
 p = p.replace("tickFormatter","")
 ######
 header = re.findall('[0-9][0-9][0-9][0-9]', p, re.DOTALL)
 ######
    
 ######
 td = soup.find_all("table")[0].find_all("td")
 cnt = 0
 pe_hist = []
 for i in td:
  try:
    pe_hist.append(float(i.text))
    cnt+=1
    if(cnt==10):
      break
  except:
    if(i.text=="—"):
      cnt+=1
      pe_hist.append(np.NaN)
 ######
 return pd.DataFrame({"P/E":pe_hist},index=header)