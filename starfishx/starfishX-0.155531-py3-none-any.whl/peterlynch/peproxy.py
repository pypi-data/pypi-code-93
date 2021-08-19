# P/E Proxy หาตัวแทนของ P/E 
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def getPEProxyProcess(symbol):  
 '''
 หา PE ของหุ้น  
 parameter : รายชื่อหุ้น symbol

 return  
 - PE บริษัท
 '''  
 symbol = symbol.replace("&","%26") 
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 url = "https://www.set.or.th/set/factsheet.do?symbol="+symbol+"&ssoPageId=3&language=th&country=TH"
 r = requests.post(url,headers=headers, timeout=5)
 soup = BeautifulSoup(r.content, "lxml")  

 ct = soup.find_all("table",{"class":"table-factsheet-padding0"})  

 if(len(ct)==0):
    pass#return 0

 #### หา index #### content อยู่ช่องไหน
 i_index = 0
 for i in ct:
  if("มูลค่าหลักทรัพย์ตามราคาตลาด" in i.text):
      m_index = i_index
      break
  i_index+=1
 
 #######
 tr = ct[m_index].find_all("tr")
   
 for i in tr:
  td = i.find_all("td")
  if("มูลค่าหลักทรัพย์ตามราคาตลาด" in td[0].text):
      try:
       marketCap  = float(td[1].text.replace(",",""))
      except: 
       marketCap  = np.NaN  
  if("P/E" in td[0].text):
      try:
       PE  = float(td[1].text.replace(",",""))
      except: 
       PE  = np.NaN  
      
      Earning = marketCap/PE  
 #######################################

 return marketCap,Earning

def upper(n):
 return n.upper()

def getPEProxy(symbollist):
 '''
 Symbol List รายชื่อของหุ้น เช่น ["ADVANC","DTAC","TRUE"]
 return PE,log
 '''
 marketCap = []
 earning = []
 pe_avg = []
 if(type(symbollist)==str):
    symbollist = [symbollist]
    
 for i in symbollist:
    m,e = getPEProxyProcess(i)
    marketCap.append(m)
    earning.append(e)
 
 ########
 df = pd.DataFrame({"Market Cap.":marketCap,"Earning":earning},index=symbollist) 
 df["P/E"] = df["Market Cap."]/df["Earning"]
 PEProxy = df["Market Cap."].sum()/df["Earning"].sum()

 df.index = df.index.map(upper)
 return PEProxy,df  