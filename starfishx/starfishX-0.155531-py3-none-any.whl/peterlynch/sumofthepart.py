import starfishX as sx
import pandas as pd
import numpy as np
from datetime import date
import datetime

import requests
from bs4 import BeautifulSoup

pd.options.display.float_format = '{:,.2f}'.format

def findName(symbol):
 symbol = symbol.replace("&","%26") 
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 url = "https://www.set.or.th/set/factsheet.do?symbol="+symbol+"&ssoPageId=3&language=th&country=TH"
 r = requests.post(url,headers=headers, timeout=5)
 soup = BeautifulSoup(r.content, "lxml") 
 
 try:
  ct = soup.find_all("table",{"class":"table-factsheet-padding3"})  
  return ct[0].find_all("td")[1].text.replace(" ","")
 except:
  return 0

def getSumOfThePart(symbol,aliasNote):
 '''
    symbol:str ชื่อย่อของหุ้นแม่ที่ต้องการวิเคราะห์
    aliasNote:str ชื่อของ fileNote ที่ใช้สำหรับสร้าง csv ไฟล์ในการคำนวณ
 '''
 print("Process..",end="")
 aliasNote = aliasNote+".csv"
 try:      
  df_ = pd.read_csv(aliasNote)  
 except:
  bs = sx.listSecurities()
  df_ = sx.listShareholders(bs.index.tolist(),csv=aliasNote)
 
 print(".",end="")
   
 #preprocess
 keyword = findName(symbol)
 #print(keyword)
 keyword = keyword.replace("บริษัท","")
 keyword = keyword.replace("จำกัด","")
 keyword = keyword.replace("(มหาชน)","")
 df_["Name"] = df_["Name"].str.replace(" ","")
 ls_hold = df_[(df_["Name"].str.contains(keyword))]
 #print(ls_hold)
 #############    
 today = date.today()
 d1 = today.strftime("%Y-%m-%d")  
 d2 = today - datetime.timedelta(days=10)
 #############

 if(len(ls_hold)==0):
     print("no-data")
     return 0,0  

 p_hold = sx.loadHistData(ls_hold["Symbol"].tolist(),start=d2,end=d1)
 
 
 pnow = p_hold.T[[p_hold.T.columns[-1]]] #-1 คือวันสุดท้าย
 p = pnow[pnow.columns[0]].tolist()
 


 #q = np.array(ls_hold["Share"].str.replace(",","").astype(float)) 
 q = np.array(ls_hold["Share"]).astype(float)
 

 rp = pd.DataFrame({"price close":p,"name":ls_hold["Name"].values,"qty":q},index=ls_hold["Symbol"].tolist())

 rp["value"] = rp["price close"]*rp["qty"]
 #############

 
 
 p_hold = sx.loadHistData(symbol,start=d2,end=d1).values[-1] 


 sjmart = float(sx.getTotalShare(symbol))*1_000_000
 v = p_hold*sjmart
 p_hold = pd.DataFrame({"price close":p_hold,"qty":[sjmart],"value":v},index=[symbol.upper()])
 #############   
 print(".End.",end="")    
 return rp,p_hold