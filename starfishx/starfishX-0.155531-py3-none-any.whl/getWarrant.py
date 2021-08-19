import requests
import pandas as pd
from datetime import datetime as dt
import numpy as np
from bs4 import BeautifulSoup

import re
import os

def getWarrantProcess(symbol,url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"} 
    r = requests.get(url,headers=headers)

    soup = BeautifulSoup(r.content, "lxml") 
    data = soup.find_all("table",{"class","table table-hover table-info"})
    
    if(len(data)==0):
        print('no content')
        return 0
    
    data = data[0]
    date_ds = []
    open_ds = []
    high_ds = []
    low_ds = []
    close_ds = []
    vol_ds = []
    row = data.find_all('tbody')[0].find_all('tr')
    for i in row:
        td = i.find_all('td')
        
        d = td[0].text.split('/')
        year = str(int(d[2])-543)
        mo = (d[1])
        day = (d[0])
        dc = year+'-'+mo+'-'+day
        dc  = dt.strptime(dc, '%Y-%m-%d')
        
        date_  = (dc)
        open_ = float(td[1].text)
        high_ = float(td[2].text)
        low_ = float(td[3].text)
        close_ = float(td[4].text)
        vol_ = float((td[7]).text.replace(',',''))
    
        date_ds.append(date_)
        open_ds.append(open_)
        high_ds.append(high_)
        low_ds.append(low_)
        close_ds.append(low_)
        vol_ds.append(vol_)

    df = pd.DataFrame({'open':open_ds,'high':high_ds,'low':low_ds,'close':close_ds,'vol':vol_ds},index=date_ds)
    return df

def getRealTime(symbol):
 url = 'https://marketdata.set.or.th/mkt/stockquotation.do?symbol='+symbol+'&language=th&country=TH'

 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"} 
 r = requests.get(url,headers=headers)

 soup = BeautifulSoup(r.content, "lxml") 
 data = soup.find_all("table",{"class","table table-hover table-set col-3-center table-set-border-yellow"})
 #...
 row = data[0].find_all('tr')
 for i in row:
    td = i.find_all('td')
    for j in td:
     #print(j)
     if('ข้อมูลล่าสุด' in j.text):
        k = j.text.split('ข้อมูลล่าสุด')
        k = k[1].strip().split(' ')
        year = str(int(k[2])-543)
        mo = monthThai2Dec(k[1])
        d = k[0]
        
        date_ = year+'-'+mo+'-'+d
        date_  = dt.strptime(date_, '%Y-%m-%d')
     if('เปิด' in j.text):
        open_ = (float(j.findNext('td').text))
     if('สูงสุด' in j.text):
        high_ = (float(j.findNext('td').text))
     if('ต่ำสุด' in j.text):
        low_ = (float(j.findNext('td').text))
     if(('ล่าสุด' in j.text) and ('ข้อมูลล่าสุด' not in j.text)):
        #open_ = (float(j.findNext('td').text))
        txt = j.findNext('td').text
        #print(txt)
        close_ = re.findall("\d+\.\d+", txt)
        if(len(close_)==1):
            close_ = float(close_[0])
            
     if('ปริมาณ' in j.text):
        vol_ = float((j.findNext('td').text.replace(',','')))      
        
 df = pd.DataFrame({'open':[open_],'high':[high_],'low':[low_],'close':[close_],'vol':vol_},index=[date_])
 return(df)   

def monthThai2Dec(m):
    if(m=='ม.ค.'):
        return '01'
    elif(m=='ก.พ.'):
        return '02'
    elif(m=='มี.ค.'):
        return '03'
    elif(m=='เม.ย.'):
        return '04'
    elif(m=='พ.ค.'):
        return '05'
    elif(m=='มิ.ย.'):
        return '06'
    elif(m=='ก.ค.'):
        return '07'
    elif(m=='ส.ค.'):
        return '08'
    elif(m=='ก.ย.'):
        return '09'
    elif(m=='ต.ค.'):
        return '10'
    elif(m=='พ.ย.'):
        return '11'
    elif(m=='ธ.ค.'):
        return '12'

def getWarrant(symbol):
    '''
    ดึงราคา Warrant หรือใบสําคัญแสดงสิทธิ symbol : string เช่น mint-w7,jmart-w4
    '''
    url = 'https://www.set.or.th/set/historicaltrading.do?symbol='+symbol+ \
        '&page='+str(0)+'&language=th&country=TH&type=trading'
    
    df = getWarrantProcess(symbol,url)
    if(type(df)==int):
        return 0 
    
    firstKey = df.index[0]
    page = 0
    
    nextFirstKey = ''
    while(firstKey!=nextFirstKey):
     page+=1
     url = 'https://www.set.or.th/set/historicaltrading.do?symbol='+symbol+ \
        '&page='+str(page)+'&language=th&country=TH&type=trading'
     tmp = getWarrantProcess(symbol,url)
     nextFirstKey = tmp.index[0]
     if(firstKey!=nextFirstKey):
        df = df.append(tmp)
    
    
    ###### ต่อวันที่ล่าสุดมา #####
    df_now = getRealTime(symbol)
    if(df.index[0]!=df_now.index[0]):
      df = df_now.append(df)
    ###########
    return df

