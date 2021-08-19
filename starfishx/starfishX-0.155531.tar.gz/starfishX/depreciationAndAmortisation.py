#depreciationAndAmortisation.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def DA(symbol):
 """
    Returns DA,Log : Depreciation และ Amortization  และ Log ของรายการ 
    
    arg1 (string): ตัวย่อของหุ้น

 """   
###### zone1 ดึงข้อมูล
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 symbolMofi = symbol.replace("&","%26")
 #url = "https://www.set.or.th/set/companyhighlight.do?symbol="+symbolMofi
 url = "https://www.set.or.th/set/companyfinance.do?type=cashflow&symbol="+symbolMofi+"&language=th&country=TH"
 r = requests.get(url,headers)
 soup = BeautifulSoup(r.content, "lxml")
 #print(soup)
###### zone2 หาส่วนที่จะใช้
 #data = soup.find_all("table",{"class":"table table-hover table-info"})  
 data = soup.find_all("table",{"class":"table table-info-wrap"})   #19 สิงหาคม 2564 update
 #print(data)
 if(len(data)==0):
    print("ไม่พบข้อมูล2")
    return 0,0
 tr = data[2].find_all("tr") 

###### zone3 เตรียมดาต้ามาประมวลผล
 p = 0
 lableItem = []
 valueItem = []
    
 sublabelItem = []
 subvalueItem = []
 previousKey = ""   
 for td in tr:
   tddata = td.find_all("td")
   #for i in range(len(tddata)):
   try:
      if("ค่าเสื่อมราคาและค่าตัดจำหน่าย" in tddata[0].text):     #19 สิงหาคม 2564 update
         print(tddata[0].text,tddata[1].text)
         lableItem.append(tddata[0].text)
         valueItem.append(tddata[1].text)
         previousKey = tddata[1].text
         
      elif("\xa0" in tddata[0].text[1] and previousKey=="ค่าเสื่อมราคาและค่าตัดจำหน่าย"):
         sublabelItem.append(tddata[0].text) 
         subvalueItem.append(tddata[1].text)     
      
      else:
         previousKey = tddata[0].text         
   except:
     pass            
        
   
###### zone4 clear report    
 if(len(valueItem)==0):
    depre_and_m = np.NAN
    log = ""
 else:   
    depre_and_m = valueItem[0].replace(",","")
    depre_and_m = float(depre_and_m)   
    lableItem[0],valueItem[0]
    
    '''log = []
    for i in range(len(sublabelItem)):
      k1 = sublabelItem[i].replace("\xa0","")
      k2 = subvalueItem[i].replace(",","")
      log.append(k1+" "+k2)  '''
    
    log = lableItem[0] +" "+valueItem[0] #19 สิงหาคม 2564 update
     
###### zone5 return ผลลัพธ์
 return depre_and_m,log







