#listSecurities.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def getMarketCapWithHist(symbol):
 '''
 symbol : str ชื่อย่อของหุ้น
 '''  
 #ป้องกันพวก &
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
 mrkCap = np.NAN
 symbolK = symbol.replace('&', '%26')
 r = requests.post("https://www.set.or.th/set/factsheet.do?symbol="+symbolK+"&ssoPageId=3&language=th&country=TH",headers=headers)
 r.content
 soup = BeautifulSoup(r.content, "lxml")  

 g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})#[2].find_all("td")
 if(len(g_data)==0):
   print("ไม่พบข้อมูล")  
   return 0
 
 ##########################################
 if("มูลค่าหลักทรัพย์ตามราคาตลาด" in g_data[13].text):
    tr_ds = g_data[13].find_all("tr")
 elif("มูลค่าหลักทรัพย์ตามราคาตลาด" in g_data[14].text):
    tr_ds = g_data[14].find_all("tr")
 elif("มูลค่าหลักทรัพย์ตามราคาตลาด" in g_data[15].text):
    tr_ds = g_data[15].find_all("tr")
 elif("มูลค่าหลักทรัพย์ตามราคาตลาด" in g_data[12].text):
    tr_ds = g_data[12].find_all("tr")
 elif("มูลค่าหลักทรัพย์ตามราคาตลาด" in g_data[11].text):
    tr_ds = g_data[11].find_all("tr") 
 elif("มูลค่าหลักทรัพย์ตามราคาตลาด" in g_data[16].text):
    tr_ds = g_data[16].find_all("tr")
 elif("มูลค่าหลักทรัพย์ตามราคาตลาด" in g_data[10].text):
    tr_ds = g_data[10].find_all("tr")


 th_ds = []   
 data_ds = []
 for i in tr_ds:
    tddata = i.find_all("td")
    #print(tddata[0].text)
    if("ข้อมูลสถิติ" in tddata[0].text):
       for k in tddata:
          th_ds.append(k.text)
    if("มูลค่าหลักทรัพย์ตามราคาตลาด" in tddata[0].text):
       z = 0 
       for k in tddata:
          m = k.text  
          if(z>0):  
            if("-" in m):
                print("ไม่พบข้อมูล")
                return 0
            m = float(m.replace(",",""))
          data_ds.append(m)     
          z+=1
            
 ##########################################
 df = pd.DataFrame({"ind":th_ds,"ds":data_ds}).T
 df.columns = th_ds   
 df = df.drop(df[df["ข้อมูลสถิติ"]=="ข้อมูลสถิติ"].index)
 df = df.set_index("ข้อมูลสถิติ")
 return df 

def findMarketCapProcess(symbol):
    #ป้องกันพวก &
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
    mrkCap = np.NAN
    symbolK = symbol.replace('&', '%26')
    r = requests.post("https://www.set.or.th/set/factsheet.do?symbol="+symbolK+"&ssoPageId=3&language=th&country=TH",headers=headers)
    r.content
    soup = BeautifulSoup(r.content, "lxml")  

    g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})#[2].find_all("td")
 
    if(len(g_data)==0):
       print("ไม่พบข้อมูล")  
       return 0,0

    #หาจาก table บน  
    k = g_data[2].find_all("tr")    
 
    #ตั้งไว้หา lable
    tLabel = k[0].find_all("td")
    indexdata = 0
    for i in tLabel:
     if("Market Cap" in i.text):
       mrkCap = k[1].find_all("td")[indexdata].text.strip().replace(",","")
       #print("Market Cap",symbol,mrkCap)
     indexdata +=1 
     #####################

    #ป้องกัน พวกข้อมูลที่เป็น '-'  
    try:
      mrkCap = np.float(mrkCap)  
    except:
      mrkCap = np.nan 

    return symbol,mrkCap

def findMarketCap(liststock,withHist=False,progress=True):
  '''
  คืนค่ามูลค่าตลาดของบริษัท : liststock เป็น str|list 
  str ถ้าต้องการคืนค่าครั้งละบริษัท เช่น sx.findMarketCap('aot') และสามารถใช้ withHist=True ได้
  list ถ้าต้องการคืนค่าครั้งละหลายๆ บริษัท เช่น sx.findMarketCap(['jmart','jmt']) แต่ไม่สามารถใช้ withHist=True ได้
  ''' 
  if(isinstance(liststock, str) and withHist==False):
    s,m = findMarketCapProcess(liststock)
    return m    
  
  if(withHist):
     if(isinstance(liststock, str)):
       return getMarketCapWithHist(liststock)
     else:
       print("not support format") 
       return 0

  ds_symbol = []
  ds_mrkcap = []  

  if(progress==True):
    print("Processing..",end="")
  pcnt = 0  
  cnt = len(liststock)
  for symbol in liststock:
    symbol,mrkCap = findMarketCapProcess(symbol)
    ds_symbol.append(symbol)
    ds_mrkcap.append(mrkCap)
    
    if(progress==True):
     if(pcnt==cnt-1):
      print(symbol,end="")
     else:
      print(symbol,end=",")
    
    pcnt +=1 
  df = pd.DataFrame({"symbol":ds_symbol,"MarketCap.":ds_mrkcap})
  df = df.set_index("symbol")

  if(progress==True):
   print(" Complete",end="")  
  return df  