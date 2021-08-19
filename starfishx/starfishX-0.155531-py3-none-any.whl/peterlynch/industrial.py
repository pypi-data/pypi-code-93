import starfishX as sx 

import requests
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np

from starfishX.peterlynch.condition import IndicatorIndustrial as ind

def getListStockInSector(sample_symbol):
    '''
    sample_symbol : (str) ตัวอย่างหุ้นในอุตสาหกรรม
    '''
    return sx.listStockInSector(sample_symbol)


def getYoY(sample_symbol,indicator=ind.NetProfit):
   '''
   str หรือ DataFrame ก็ได้ หากเป็น DataFrame จะใช้ Col ที่ 1
   '''
   if(type(sample_symbol)==str):
    symbol_ds = sample_symbol.upper()   
    symbol_ds,h1,v1,h2,v2 =  getYoYProcess(symbol_ds,indicator) 
    df = pd.DataFrame({"YearT":[h1],"ValueT":[v1],"YearT-1":[h2],"ValueT-1":[v2]},index=[symbol_ds])
    return df 
      

   if(type(sample_symbol)==list): 
     sample_symbol = pd.DataFrame({"symbol":sample_symbol},index=sample_symbol)  
     sample_symbol = sample_symbol[sample_symbol.columns[0]].tolist()
   elif(type(sample_symbol)==pd.core.frame.DataFrame):  
     sample_symbol = sample_symbol[sample_symbol.columns[0]].tolist() 
   
   symbol_ds = [] 
   h1_ds = [] 
   v1_ds = []
   h2_ds = []
   v2_ds = []
     
   print("Processing..",end="")
   for i in sample_symbol:
       i = i.upper()  
       print(i+".",end="")
       s,h1,v1,h2,v2 = getYoYProcess(i,indicator)
       symbol_ds.append(s)
       h1_ds.append(h1)
       v1_ds.append(v1)
 
       h2_ds.append(h2)
       v2_ds.append(v2)

       df = pd.DataFrame({"YearT":h1_ds,"ValueT":v1_ds,"YearT-1":h2_ds,"ValueT-1":v2_ds},index=symbol_ds)
   print(".End.",end="")  
   return df


def getYoYProcess(symbol,indicator): 
 #symbol = "awc"
 symboltmp = symbol.replace("&","%26") 
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 url = "https://www.set.or.th/set/factsheet.do?symbol="+symboltmp+"&ssoPageId=3&language=th&country=TH"
 r = requests.post(url,headers=headers, timeout=5)
 soup = BeautifulSoup(r.content, "lxml")  

 ct = soup.find_all("table",{"class":"table-factsheet-padding0"})  

 if(len(ct)==0):
    return symbol,np.NaN,np.NaN,np.NaN,np.NaN

 #### หา index #### content อยู่ช่องไหน
 i_index = 0
 for i in ct:
  if("งบกำไรขาดทุนเบ็ดเสร็จ (ลบ.)" in i.text):
      m_index = i_index
      break
  i_index+=1

 ##########
 tr = ct[m_index].find_all("tr")
 
 ##########
 noMeet = 0
 for i in tr:
    td = i.find_all("td")
    try:
      if("งบกำไรขาดทุนเบ็ดเสร็จ (ลบ.)" in td[0].text):
        h1 = str(td[1].text).strip() 
        h1 = h1.replace("\xa0","")
        h1 = h1.replace(" ","")
        
        h2 = str(td[2].text).strip()
        h2 = h2.replace("\xa0","")
        h2 = h2.replace(" ","")
    except:
        h1 = np.NaN
        h2 = np.NaN
        v1 = np.NaN 
        v2 = np.NaN 
    
  
    if(indicator.value=="NetProfit"):
     if(("รายได้จากการลงทุนสุทธิ" in td[0].text) or ("กำไร(ขาดทุน)สุทธิ" in td[0].text)):
        noMeet = 1
        try: 
         v1 = float(td[1].text.replace(",",""))
         v2 = float(td[2].text.replace(",",""))   
        except:
         h1 = np.NaN
         h2 = np.NaN
         v1 = np.NaN 
         v2 = np.NaN 
    
    
    if(indicator.value=="Sales"):
      if(("รายได้จากเงินลงทุน" in td[0].text) or ("ยอดขายสุทธิ" in td[0].text) 
                                      or ("รายได้ดอกเบี้ยและเงินปันผลสุทธิ" in td[0].text) 
                                      or ("รายได้ค่านายหน้า" in td[0].text)   ): 
        noMeet = 1
        try:    
         v1 = float(td[1].text.replace(",",""))
         v2 = float(td[2].text.replace(",",""))  
        except:         
         h1 = np.NaN
         h2 = np.NaN
         v1 = np.NaN 
         v2 = np.NaN  

 if(noMeet==0):
   h1 = np.NaN
   h2 = np.NaN
   v1 = np.NaN 
   v2 = np.NaN 
 
 return symbol,h1,v1,h2,v2   