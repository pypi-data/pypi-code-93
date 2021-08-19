#listSecurities.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

 

def findSector(symbol):
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
    return symbol,np.float(mrkCap)

