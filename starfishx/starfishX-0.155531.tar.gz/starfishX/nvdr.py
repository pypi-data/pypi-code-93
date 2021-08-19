import requests
from bs4 import BeautifulSoup
import pandas as pd

import datetime

from urllib import request, parse
import ssl
def getNVDRTrading(symbol,date):
    tmpd = date.split("-")
    year = tmpd[0]
    month = tmpd[1]
    day = tmpd[2]
    
    newdate_format = day+"/"+month+"/"+year
   
    ### ดึง soup ####
    #url = "https://www.set.or.th/set/nvdrbystock.do"
    
    #values = {"sort":"",
    #          "type" : "volume",
    #          "language" :"th",
    #          "country" : "TH",
    #          "date":newdate_format }

    #context = ssl._create_unverified_context()
    #data = parse.urlencode(values).encode()
    #req =  request.Request(url, data=data) # this will make the method "POST"
    #resp = request.urlopen(req,context=context)
    
    #soup = BeautifulSoup(resp.read() , "lxml")
    url = "https://www.set.or.th/set/nvdrbystock.do?sort=&type=volume&language=th&country=TH&date="+day+"%2F"+month+"%2F"+year
     
    #?sort=&type=volume&language=th&country=TH&date="+day+"%2F"+month+"%2F"+year
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    r = requests.post(url,headers)
    soup = BeautifulSoup(r.content, "lxml")  
    
    ct = soup.find_all("table", {"class" : "table table-info table-striped"})[0].find_all("tbody")
    ct = ct[0].find_all("td")
    
    ### process text ###
    p = 0
    buy = 0
    sell = 0
    for i in range(len(ct)):
     #มีมา 6 แถว     
     if(ct[i].text==symbol):
        #print(ct[i].text)
        p = 1
     if(p==1):  
      buydata = ct[i+1].text.strip()
      selldata = ct[i+2].text.strip()
      if(buydata=="-"):
         buydata = "0"
      if(selldata=="-"):
         selldata = "0"
            
      buy = float(buydata.replace(",","")) #ปริมาณซื้อ
      sell = float((selldata).replace(",","")) #ปริมาณขาย
      break 

    return (symbol,buy,sell)


def getNVDRVolume(symbol,startdate):
 '''
 symbol (string) : สัญลักษณ์ของหุ้นไทย เช่น 'AOT' 
 startdate (string) : วันที่เริ่มดึงข้อมูล เช่น '2021-01-01'
 '''  
 symbol = symbol.upper()   
 symbolDS = []
 buyDS = []
 sellDS = []
 dateActive = []

 #### ส่วนของการสร้างวัน #####
 base = datetime.datetime.today()
 x=0
 date_list=[]
 while(True):
    d = base - datetime.timedelta(days=x)
    date_list.append(d)
    x+=1
    if(startdate==d.strftime("%Y-%m-%d")):  #วนจากวันที่ปัจจุบันมาวันที่เริ่มต้น
      break   
 #########################    
 
 print("process",end="")
 for d in date_list:
    date = (d.strftime("%Y-%m-%d"))
    try:
     symbol,buy,sell = getNVDRTrading(symbol,date)
     symbolDS.append(symbol)
     buyDS.append(buy)
     sellDS.append(sell)
     dateActive.append(d)   
     print(".",end="")
    except:
     print("-",end="")   
 print("end",end="")

 ##### คืนค่า dataframe #######
 df = pd.DataFrame({"symbol":symbolDS,"buy":buyDS,"sell":sellDS},index=dateActive)
 df.index = df.index.date #เทคนิค เอาเวลาออกจาก date คือตัด HH:MM:SS ออก
 return df

def reduceXtickfrequency(ax,n):
 '''
 ax : (plot)
 n  : จำนวนวันของแกน y 
 ax = df[["buy","sell"]].sort_index().plot(title="{} / NVDR Volume (Share)".format(symbol),
                                   kind="bar",figsize=(12,5),grid=True)
 sx.reduceXtickfrequency(ax,n=7)
 '''   
 ticks = ax.xaxis.get_ticklocs()
 ticklabels = [l.get_text() for l in ax.xaxis.get_ticklabels()]
 ax.xaxis.set_ticks(ticks[::n])
 ax.xaxis.set_ticklabels(ticklabels[::n])

