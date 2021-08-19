#Ke.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


import json
import datetime

from enum import Enum

from datetime import datetime as dt, timedelta
from dateutil.relativedelta import relativedelta

class BondType(Enum):
 USTreasury10Year = "USTreasury10Year"
 ThaiGovernmentBond10Year   = "ThaiGovernmentBond10Year"
 USTreasury10YearAnd2Year = "USTreasury10YearAnd2Year"



def validate(date_string):
 date_format = '%Y-%m-%d'
 try:
  date_obj = datetime.datetime.strptime(date_string, date_format)
  return 1
 except ValueError:
  print("Incorrect data format, should be YYYY-MM-DD")
  return 0


def thaibma_series(date="",bondtype=BondType.ThaiGovernmentBond10Year,viewlog=True):
 #date = "2020-01-01"
 
 d = date.split("-")   
 date = dt(int(d[0]),int(d[1]),int(d[2]))#startdate
 stop = dt.now()
 
 

 logYeild = []
 dateIndex = []
 for i in range(365*10): #เดาว่าไม่เกิน 1000 เดือน
  if((stop.month==date.month) & (stop.year==date.year) & (stop.day==date.day) ):
    break
    
  try:      
   dt_str = date.strftime('%Y-%m-%d')

   k = thaibma(dt_str,bondtype=bondtype)
   y = float(k)
 
   logYeild.append(float(k))
   dateIndex.append(date)

   date = date + relativedelta(days=+1)
    
   print(".",end="")
    
  except:
    dt_str = date.strftime('%Y-%m-%d')
    print("error"+dt_str,end=" ")
    date = date + relativedelta(days=+1)
    
 print("End.",end="")   
 df = pd.DataFrame({bondtype.value:logYeild},index=dateIndex)
 return df








#http://www.thaibma.or.th/EN/Market/YieldCurve/Government.aspx
def thaibma(date="",bondtype="",viewlog=True):  
 if(date==""):
    date = datetime.datetime.now().strftime("%Y-%m-%d")

 if(validate(date)==0):
     return 0
 
 if(bondtype==""):
    bondtype = BondType.USTreasury10Year
 
 if(not isinstance(BondType.USTreasury10Year,BondType)):
    print("dataType Not Match")
    return 0,0
  
 bondtype_ = bondtype.value
  
 if(bondtype_=="USTreasury10Year" or bondtype_=="USTreasury10YearAnd2Year"): 
    jsonKey = "USTreasury"  
    url = "http://www.thaibma.or.th/yieldcurve/uszyc/"+date

 if(bondtype_=="ThaiGovernmentBond10Year"):
    jsonKey = "Curve"  
    url = "http://www.thaibma.or.th/yieldcurve/gov/"+date

 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
 r = requests.get(url,headers=headers)
 r.content
 soup = BeautifulSoup(r.content, "lxml") 
    
 data  = json.loads(soup.text)  
 try: 
  if(bondtype_=="USTreasury10Year"):
   for i in data[jsonKey]:     
    if((str(i['X']))=="10.0"):
     return ((float(i['Y']))/100)
  
  if(bondtype_=="ThaiGovernmentBond10Year"):
   for i in data[jsonKey]:     
    if((str(i['X']))=="10.0"):
     return ((float(i['Y']))/100)

  if(bondtype_=="USTreasury10YearAnd2Year"):  
    p = 0
    k2 = 0 
    k10 = 0
    for i in data[jsonKey]:  
      if((str(i['X']))=="2.0"):  
         p = p+1  
         k2 = ((float(i['Y']))/100)
      if((str(i['X']))=="10.0"):
         p = p+1 
         k10 = ((float(i['Y']))/100)
      if(p==2):
         return {"USTreasury2Year":round(k2,4),"USTreasury10Year":round(k10,4)}
 except:
    if(viewlog==True):
      print("ไม่พบข้อมูล",end=" ")
    return 0


#http://www.thaibma.or.th/EN/Market/YieldCurve/Government.aspx
def governmentBond10year(date=""):  
 if(date==""):
   date = datetime.datetime.now().strftime("%Y-%m-%d")

 if(validate(date)==0):
     return 0
    
 url = "http://www.thaibma.or.th/yieldcurve/gov/"+date
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
 r = requests.get(url,headers=headers)
 r.content
 soup = BeautifulSoup(r.content, "lxml") 
    
 data  = json.loads(soup.text)   
 for i in data['Curve']:     
  if((str(i['X']))=="10.0"):
    return ((float(i['Y']))/100)
 
 print("ไม่พบข้อมูล")
 return 0


def findIndexData(strfind,g_data):
  indexat = 0
  cnt = 0
  for i in (g_data):
    if(strfind in i.text):
        indexat = cnt
    cnt+=1
    
  return indexat  

def beta(symbol):
 #ป้องกันพวก &
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
 mrkCap = np.NAN
 symbolK = symbol.replace('&', '%26')
 r = requests.get("https://www.set.or.th/set/factsheet.do?symbol="+symbolK+"&ssoPageId=3&language=th&country=TH",headers=headers)
 r.content
 soup = BeautifulSoup(r.content, "lxml")  

 g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})#[2].find_all("td")
 if(len(g_data)==0):
   print("ไม่พบข้อมูล")  
   return 0
 
 ##########################################
 indexat = findIndexData("ข้อมูลสถิติ",g_data)
 tr_ds = g_data[indexat].find_all("tr")
 ##########################################
    
    
 th_ds = []   
 data_ds = []
 for i in tr_ds:
    tddata = i.find_all("td")
    #print(tddata[0].text)
    if("ข้อมูลสถิติ" in tddata[0].text):
       for k in tddata:
          th_ds.append(k.text)
    if("Beta" in tddata[0].text):
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