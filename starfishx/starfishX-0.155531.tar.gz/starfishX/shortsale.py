######### moc.py
try:
    #ลำดับมีผลพยายามโหลดที่ ใน folder ที่กำลัง Implement ก่อน
    from starfishX import config as con 
    #print("Dev")
except:
    #print("Debug")
    import starfishX.config as con

prefix = "starfishX."

if(con.__mode__=="debug"):
    prefix = ""

    

import urllib
import ssl
from bs4 import BeautifulSoup

import pandas as pd
import calendar
import time
from urllib import request, parse

import datetime
from dateutil.parser import parse as pt

def getShortSale(date): #วัน/เดือน/ปี
 context = ssl._create_unverified_context()
 url = 'https://www.set.or.th/set/shortsales.do'
 values = {'from' : date,
          'to' :date,
          'format' : 'html' }

 
 data = parse.urlencode(values).encode()
 req =  request.Request(url, data=data) # this will make the method "POST"
 resp = request.urlopen(req,context=context)
 
 soup = BeautifulSoup(resp.read() , "lxml")
 
 ct = soup.find_all("table",{"class":"table-info"}) 
  
 if(len(ct)>0):
   dt = ct[0].find_all("td")   
   return dt
 else:
   return 0




def shortsale(symbol,dateStart,shorttype="sum"):
  #dateStart="2019-10-09" #10กันยา2019
  symbol = symbol.upper()
  base = datetime.datetime.today()
  x=0
  date_list=[]
  while(True):
    d = base - datetime.timedelta(days=x)
    date_list.append(d)
    x+=1
    if(dateStart==d.strftime("%Y-%m-%d")):
      break   
    
  ############ จบส่วนสร้างช่วงของเวลา
  #symbol = "ADVANC"
  symbolDs = []
  volumeDs = []
  volumnsTotal = []
  dateDs = []
  for i in date_list:
    if(i.weekday()<5):
      #print(calendar.day_name[i.weekday()])
      d=i.strftime("%d/%m/%Y")
      dt = getShortSale(d)
      if(type(dt)!=int):
       k = 0
       for j in range(len(dt)):
        if(symbol in dt[j].text):
         print(".",end="")
         symbolDs.append(dt[j].text)
         volumeDs.append(float(dt[j+1].text.replace(",","")))
         dateDs.append(pt(i.strftime("%Y-%m-%d")))
         k+=1 
         if(k==2):
            break  
  print(" Complete",end="")
  ######################
    
  ###### จัดโครงสร้าง DataFrame
  df = pd.DataFrame({"symbol":symbolDs,"volume":volumeDs,"date":dateDs})
  df = df.set_index("date") 

  rp = df.groupby(df.index)[["volume"]].sum()
  rp.index = rp.index.date  #เอาเวลาออกจาก date คือตัด HH:MM:SS ออก
  return rp



def shortsaleByDay(date,shorttype="sum"):
 date = datetime.datetime.strptime(date,'%Y-%m-%d').strftime("%d/%m/%Y")
   
 context = ssl._create_unverified_context()
 url = 'https://www.set.or.th/set/shortsales.do'
 values = {'from' : date,
          'to' :date,
          'format' : 'html' }

 
 data = parse.urlencode(values).encode()
 req =  request.Request(url, data=data) # this will make the method "POST"
 resp = request.urlopen(req,context=context)
 
 soup = BeautifulSoup(resp.read() , "lxml")
 
 ct = soup.find_all("table",{"class":"table-info"})

 #####
 cr = ct[0].find_all("tr")
 #####
 row = 0
 symbolDs = []
 volumeDs = []   
 for i in cr:
   if(row>0):
      k = i.find_all("td")
      td = 0  
      for j in k:
        if(td==0): 
           symbolDs.append(j.text.replace("-R",""))
        if(td==3): #3 คือ %Short Sale Volume Comparing with Auto Matching
           volumeDs.append(float(j.text.replace(",","").replace("%","")))
           break 
        td+=1
   row+=1    
 
 #######
 df = pd.DataFrame({"symbol":symbolDs,"%ShortSale/AutoMatching":volumeDs})  
 df = df.groupby("symbol")[["%ShortSale/AutoMatching"]].sum()   
 return df