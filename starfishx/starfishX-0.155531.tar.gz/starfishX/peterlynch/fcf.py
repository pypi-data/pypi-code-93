import ssl
from urllib import request, parse
from bs4 import BeautifulSoup

import os
from selenium import webdriver

import pandas as pd
import requests

def getFreeCashFlow(symbol):
    
 #symbol = "splai"
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 symbolMofi = symbol.replace("&","%26")
 url = "https://www.set.or.th/set/companyfinance.do?type=cashflow&symbol="+symbolMofi+"&language=th&country=TH"

 r = requests.get(url,headers)
 soup = BeautifulSoup(r.content, "lxml")

 data = soup.find_all("table",{"class":"table table-hover table-info"})

 #### หา index #### content อยู่ช่องไหน
 i_index = 0
 for i in data:
  if("งบกระแสเงินสด" in i.text):
      m_index = i_index
      break
  i_index+=1

 #######
 
 td = data[m_index].find_all("td")

 #######
 cnt = 0
 lb = []
 value = []
 vaS = 0
 vaE = 0
 k = 0
 multirow = 0
 
 for i in td:
  text = i.text.replace(" ","")  
  ###### 
  if(("เงินสดสุทธิได้มาจาก" in text) and ("กิจกรรมดำเนินงาน" in text) ):
     k = float(td[cnt+1].text.replace(",",""))
     p1 = k 
     lb.append(text)
     value.append(k)
         
  if(("เงินสดจ่ายจากการซื้อที่ดิน" in text)): #เงินสดจ่ายจากการซื้อที่ดิน อาคาร และอุปกรณ์
     k = float(td[cnt+1].text.replace(",",""))
     p1 += k 
     lb.append(text)
     value.append(k) 
       
  if(("สินทรัพย์ไม่มีตัวตน(เพิ่มขึ้น)ลดลง" in text) and not("\xa0" in text) ):  #สินทรัพย์ไม่มีตัวตน (เพิ่มขึ้น) ลดลง
     lbS = text
     vaS = float(td[cnt+1].text.replace(",",""))
     multirow = 1   
        
  if(("สินทรัพย์ไม่มีตัวตน(เพิ่มขึ้น)" in text) and ("\xa0" in text) ):  #สินทรัพย์ไม่มีตัวตน (เพิ่มขึ้น) ลดลง
     lbM = text
     vaM = float(td[cnt+1].text.replace(",",""))
     multirow = 2  
 
   
  #######
  cnt+=1 

 
 if(multirow==1):
     p1 += vaS 
     lb.append(lbS)
     value.append(vaS) 
 elif(multirow==2):
     p1 += vaM 
     lb.append(lbM)
     value.append(vaM)
 
        
 lb.append("กระแสเงินสดอิสระ")
 value.append(p1)
 df = pd.DataFrame({"Label":lb,"Value":value})
 return df   


def getFreeCashFlowWSJ(symbol,period="ANNUAL"):
 '''
 symbol : (str) สัญลักษณ์ชื่อย่อของหุ้น
 period : (str) กรอบระยะเวลา มีให้เลือกสองอย่าง ANNUAL และ QUARTERLY
 '''   
 #symbol = "dtac"
 #period = "ANNUAL"
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 symbolMofi = symbol.replace("&","%26")
 url = "https://www.wsj.com/market-data/quotes/TH/XBKK/"+symbolMofi+"/financials"
 
 print("Processing.",end="")
 os.environ['MOZ_HEADLESS'] = '1'
 print(".",end="")
 driver = webdriver.Firefox()  #อาจต้องลง 
 # Grab the web page
 print(".",end="")   
 driver.get(url)
 print(".",end="")

 test = driver.find_elements_by_xpath("//div[@class='cr_mod_full cr_data cr_data_chart cr_financials cr_financials_cash module']")
 print(".",end="")
 for i in test:
   print(".",end="")     
   for a_data in i.find_elements_by_tag_name("li"):
     #print(a_data.text)
     if(a_data.text==period):
         a_data.click()
     if(a_data.text==period):
         a_data.click()   
        
 #################  
 print(".",end="")
 
 passLabel = 0
 value = 0
 passLabelPershare = 0
 valuePershare = 0
 cnt = 0   
 for event in driver.find_elements_by_class_name("cr_financials_table"):
  for td_data in event.find_elements_by_tag_name("td"):  
    #if("Free Cash Flow" in td_data.text):  
    #cnt+=1
    #print("cnt"+str(cnt))
    #print(".",end="")
    if(("Free Cash Flow" in td_data.text) and not("Per Share" in td_data.text)):
        passLabel = 1
        #print("a",td_data.text)
        print(".",end="")
    else:
        if(passLabel==1): #find next td
          value = td_data.text
          #print("b",td_data.text)
          print(".",end="")  
          passLabel = 2
        
    if("Free Cash Flow Per Share" in td_data.text):
        passLabelPershare = 1
        #print("c",td_data.text)
        print(".",end="")
    else: 
        if(passLabelPershare==1):
          valuePershare = td_data.text
          #print("d",td_data.text)
          print(".",end="")  
          passLabelPershare = 2
          break
 #print(3) 
 print(".End.",end="")
 driver.close() 
 return pd.DataFrame({"Free Cash Flow":[value],"Free Cash Flow/Share":[valuePershare]},index=[symbol.upper()])