#DividendDiscountModel.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def findIndexData(strfind,g_data):
  indexat = 0
  cnt = 0
  for i in (g_data):
    if(strfind in i.text):
        indexat = cnt
    cnt+=1
    
  return indexat   

def DividendDiscountModel(symbol,year,k):
 """
    ประเมินมูลค่าหุ้นด้วย Dividend Discount Model
 
    Returns ddm,g,payout,div,eps,roe

    ddm มูลค่าหุ้น , g อัตราการเติบโต , payout ,div เงินปันผลในปีนั้นๆ , eps และ roe
    
    arg1 (str): ตัวย่อของหุ้น เช่น "aot","cpall","ptt"

    arg2 (int): year ปีเป็นพ.ศ.เช่น 2561,2560 

    arg3 (float): k อัตราผลตอบแทนที่คาดหวัง
    
 """  
 if(type(year)==int):
   year = str(year)
 
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
 symbolK = symbol.replace('&', '%26')
 r = requests.get("https://www.set.or.th/set/factsheet.do?symbol="+symbolK+"&ssoPageId=3&language=th&country=TH",headers=headers)
 r.content
 soup = BeautifulSoup(r.content, "lxml") 
    
 g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})   
    
 #### หาปันผลรวมในปีของผลประกอบการนั้นๆ ก่อน #########################
 indexat = findIndexData("การจ่ายปันผล",g_data)
 tr_ds = g_data[indexat].find_all("tr") 


 dd_ds = []
 for i in tr_ds:
  td1 = i.find_all("td")    
   
  contentStr = td1[0].text
  if("ต.ค." in td1[0].text[0:12]):
    if("ก.ย." in (td1[0].text[12:len(td1[0].text)])):
        contentStr = td1[0].text[12:len(td1[0].text)]
  
  if(year in contentStr):  
     dd_tmp = (td1[1].text)
    
     if(":" in dd_tmp):
        print("พบว่าอาจจะมีปันผลเป็นหุ้น กรุณาตรวจสอบด้วยตนเอง")
        return 0,0,0,0,0,0     
     dd_tmp = float(dd_tmp)
     dd_ds.append(dd_tmp)  
      
    
 dd_ds = np.array(dd_ds).sum()   
 if(dd_ds==0):
    print("ไม่พบข้อมูล(Dividend)")
    return 0,0,0,0,0,0
 #### จบส่วนหาปันผล #########################
    
 #### หา EPS ######################### 
 indexat = findIndexData("งบกำไรขาดทุนเบ็ดเสร็จ",g_data)
 tr_ds = g_data[indexat].find_all("tr") 

    
 #หาปีที่ต้องการว่าอยู่หลักไหน
 td1 = tr_ds[0].find_all("td")
 cnt = 0
 colyear = 0
 for i in td1:
   if(year in i.text[0:4]):
     colyear = cnt
   cnt+=1 

 if(colyear==0):
    print("ไม่พบข้อมูล(eps)")
    return 0,0,0,0,0,0
 
 eps = 0 
 for i in tr_ds:
   td1 = i.find_all("td")
   if("กำไรต่อหุ้น (บาท)" in td1[0].text):
      eps = (td1[colyear].text)

      if("N/A" in eps):
       eps = np.NaN
      else:  
       eps = float(eps)

 
 if(eps==0 or np.isnan(eps)):
    print("ไม่พบข้อมูล(eps)")
    return 0,0,0,0,0,0     
 ##### จบส่วนหา EPS ################################

 ###### หา payout #####################
 payout = (dd_ds / eps)
 ##### จบส่วนหา payout ################################ 
    
    
 ###### หา ROE #####################   
 indexat = findIndexData("อัตราส่วนทางการเงิน",g_data)
 tr_ds = g_data[indexat].find_all("tr") 
 

 #หาปีที่ต้องการว่าอยู่หลักไหน
 td1 = tr_ds[1].find_all("td")
 cnt = 0
 colyear = 0
 for i in td1:
   if(year in i.text[0:4]):
     colyear = cnt
   cnt+=1 
 
 if(colyear==0):
    print("ไม่พบข้อมูล(ROE)")
    return 0,0,0,0,0,0
 
 roe = 0
 for i in tr_ds:
   td1 = i.find_all("td")
   if("อัตราผลตอบแทนผู้ถือหุ้น (%)" in td1[0].text):
    roe = (td1[colyear].text)
    if("N/A" in roe):
       roe = np.NaN
    else:
       roe = float(roe)
       roe = roe/100 

 if(roe==0 or np.isnan(roe)):
    print("ไม่พบข้อมูล(ROE)")
    return 0,0,0,0,0,0     
 ###### จบส่วนหา ROE #####################    
 
 ###### หา g ##################### 
 g = roe*(1-payout) 
 ###### จบส่วนที่หา g #####################    
    
 ######## ประเมินมูลค่าหุ้นด้วย DDM ###   
 ddm = (dd_ds*(1+g))/(k-g)   
    
 return ddm,g,payout,dd_ds,eps,roe     