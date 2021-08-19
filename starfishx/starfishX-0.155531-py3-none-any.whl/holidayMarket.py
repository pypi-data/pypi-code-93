import requests
import pandas as pd
from bs4 import BeautifulSoup

def getHolidayMarket(year):
   '''
   year : int เป็นปี คศ.เช่น 2020 โดยเริ่มต้นจาก 1992
   ref : https://www.bot.or.th/Thai/FinancialInstitutions/FIholiday/Pages/2021.aspx
   '''
   ######## 
   url = "https://www.bot.or.th/Thai/FinancialInstitutions/FIholiday/Pages/"+str(year)+".aspx"
    
   headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
   r = requests.post(url,headers=headers, timeout=5)
   soup = BeautifulSoup(r.content, "lxml")   
   ########
   idzone = soup.find_all("div",{"class","ms-rtestate-field"})  
   if(len(idzone)>1):#support ปี 2014
         idzone[0] = idzone[-1]
   tb = (idzone[0].find_all("tr"))
    
   '''tb = soup.find_all("table",{"class":"bot-rteTable-mytable2"})

   if(len(tb)==1):
     tb = tb[0].find_all("tr") 
    
   if(len(tb)==0): #support ปี 1998
     tb = soup.find_all("table",{"class":"bot-rteTable-mytable"}) 
     tb = tb[1]
     tb = tb.find_all("tr")   
        
   if(not "มกราคม" in tb): #support ปี 2011
     idzone = soup.find_all("div",{"class","pageContent"})
     if(len(idzone)==0): #support ปี 2013
       idzone = soup.find_all("div",{"class","ms-rtestate-field"})  
       if(len(idzone)>1):#support ปี 2014
         idzone[0] = idzone[-1]
     tb = (idzone[0].find_all("tr"))   '''   
   ########
   monthTH = ["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน", \
             "พฤษภาคม","มิถุนายน","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]
   monthEN = ["01","02","03","04","05","06","07","08","09","10","11","12"]
   #print(soup)
   ds = []
   holiday = []
   for tbi in tb:
     try:
       data = tbi.find_all("td") 
       mt = data[3].text.strip()
       mt = mt.replace("​","")
       d = data[2].text.strip().replace("​","") 
     except:
       continue  
     
     if(len(d)==1):
        d = "0"+d  
     #k = [i for i in range(len(monthTH)) if monthTH[i]==mt][0]
     p = 0
     for i in range(len(monthTH)):
        if(monthTH[i]==mt):
           k = i
           p = 1
        
     if(p==0):
       continue

     m = monthEN[k]
     date = str(year)+"-"+m+"-"+d 
     whoday = data[4].text.replace("\r\n","").replace("\n","")
        
     if("ยกเลิก" in whoday):
        continue
        
     ds.append(date)
     holiday.append(whoday)

   return pd.DataFrame({"ds":pd.to_datetime(ds),"holiday":holiday}) 