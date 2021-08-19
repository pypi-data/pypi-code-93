import re
import pandas as pd
import ssl
from urllib import request, parse
from bs4 import BeautifulSoup

import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import datetime

from IPython.display import HTML

from urllib.parse import quote 


import requests
 

pd.set_option('display.max_colwidth',-1)

def filterThai(str_data):
    return re.sub(r'[^a-zA-Z]', "", str_data)

def getValueCompanyR59(wordSearch):
 '''
 wordSearch : str เช่น เจ มาร์ท , ท่าอากาศ เป็นต้น
              ใช้คำบางส่วนของชื่อบริษัท
 '''  
 context = ssl._create_unverified_context()
 url = 'https://market.sec.or.th/public/idisc/th/r59'
 
 #data = parse.urlencode(values).encode()
 req =  request.Request(url) # this will make the method "POST"
 resp = request.urlopen(req,context=context)
 
 soup = BeautifulSoup(resp.read() , "lxml")
 
 ct = soup.find_all("select")

 for i in ct[0].find_all('option'):
   if(wordSearch in i.text):
      print(i.text)
      print(i["value"])

def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = "รายละเอียด"
    #link = link
    return f'<a target="_blank" href="{link}">{text}</a>'

def getReportR59(dateFrom,dateTo,Company="",report=True,Viewmore=False):
  '''
  ใช้วันที่เป็น พ.ศ. #DD/MM/YYYY 
  ตัวอย่าง getReportR59(dateFrom="01/01/2563",dateTo="30/05/2563",Company="0000003725") 
  Company : (string) รหัสของบริษัท จะคืนค่านี้มาจาก getValueCompanyR59 
  dateFrom : (string) ฟังก์ชันนี้กำหนดค่าเป็น พศ. DD/MM/YYYY
  dateTo : (string) ฟังก์ชันนี้กำหนดค่าเป็น พศ. DD/MM/YYYY
  Viewmore : (Boolean) หากกำหนดเป็น True จะคืนค่ามากกว่า 100 รายการได้

  หากใช้งานไม่ได้ ทดลองติดตั้งเพิ่มเติมด้วยคำสั่ง
  conda install -c conda-forge geckodriver
  ''' 
  if(Viewmore==True):
   d1 = dateFrom.split('/')
   dateFrom = str(int(d1[2])-543)+d1[1]+d1[0]
   
   d2 = dateTo.split('/')
   dateTo = str(int(d2[2])-543)+d2[1]+d2[0]

   url = 'https://market.sec.or.th/public/idisc/th/Viewmore/r59-2?DateType=1&DateFrom='+dateFrom+'&DateTo='+dateTo
   headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
   r = requests.post(url,headers=headers, timeout=5)
   soup = BeautifulSoup(r.content, "lxml") 
   rows = soup.find_all('table',{'table table-striped table-hover'})     
   rows = rows[0]
    
  else:
   #dateFrom = "01/01/2563"
   #dateTo = "10/01/2563"
   #Company = "0000008180"  
   #dateFrom="01/01/2563"
   #dateTo="30/04/2563"
   #Company="0000028632"
   if 'google.colab' in str(get_ipython()):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
   else:   
    os.environ['MOZ_HEADLESS'] = '1'  
    driver = webdriver.Firefox()  #อาจต้องลง 
   # Grab the web page
    
   driver.get("https://market.sec.or.th/public/idisc/th/r59")
   #กำหนดค่าใน textbox
   k = driver.find_element_by_id("BSDateFrom")
   k.clear()
   k.send_keys(dateFrom)
   driver.find_element_by_id("BSDateFrom").get_attribute("value")
    
   ### Dateto
   k = driver.find_element_by_id("BSDateTo")
   k.clear()
   k.send_keys(dateTo)
   driver.find_element_by_id("BSDateTo").get_attribute("value")

   if(Company!=""):
   ### Select
    k = Select(driver.find_element_by_id("ctl00_CPH_ddlCompany"))
    k.select_by_value(Company)
    #driver.find_element_by_id("BSDateTo").get_attribute("value")
   elif(Company==""):
    k = Select(driver.find_element_by_id("ctl00_CPH_ddlCompany"))  
    k.select_by_value("")  

   ### หาปุ่ม submit และกด click
   btn_input = driver.find_element_by_id("ctl00_CPH_btSearch")
   # Then we'll fake typing into it
   btn_input.click()  

   ### เริ่ม parser
   # We can feed that into Beautiful Soup
   doc = BeautifulSoup(driver.page_source,"html.parser")  
   rows = doc.find('table', id='gPP09T01')  
  
  ############################################# 
  if("ไม่พบข้อมูล" in str(rows)):
    return 0
    #print(1)

  tr = []
  td = []
     
  for i in rows.find_all("tr"):
    td = []  
    cnt_td = 0
    k = i.find_all("td")
    for j in k:
     if(cnt_td==4): #หา date
        tmp = j.text.split("/")
        date_time_str = str(int(tmp[2])-543)+"-"+tmp[1]+"-"+tmp[0]
        dt = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')
        #print(date_time_str)
        td.append(dt) 
     
     elif(cnt_td==8):
        td.append(j.a['href'])
     else:   
        td.append(j.text)   
        
     cnt_td+=1
    tr.append(td.copy())
    
  #สร้าง DataFrame  
  df = pd.DataFrame(tr)
  #จัดทรง DataFrame  
  df = df.dropna()
  
   
  df.columns = ["Company","Management","Relationship","TypesAsset","Date","Amount","AvgPrice","Methods","Remark"] 
  df["Company"] = [filterThai(j) for j in df["Company"]]
  #del df['Remark']
  
  try:
   df["Amount"] = df["Amount"].str.replace(",","").astype(float) 
  except:
   df["Amount"] = df["Amount"].str.replace(",","")

  try: 
   df["AvgPrice"] = df["AvgPrice"].str.replace(",","").astype(float)
  except:
   df["AvgPrice"] = df["AvgPrice"].str.replace(",","")

  
  if(Viewmore==False):
   driver.close()  

  #เพิ่ม link HTML รายละเอียด

  if(report==True):
   df['Remark'] = df['Remark'].apply(make_clickable)
   df = HTML(df.to_html(escape=False))
  return df  







#### แบบรายงาน R246
def getReportR246(symbolOrName,datefrom,dateto,person=False):
    '''
    pl.getReportR246(symbolOrName='',datefrom='2020-10-01',dateto='2020-10-30')
    symbolOrName : (string) ชื่อหุ้น หากไม่ระบุจะคืนค่าทุกตัวในช่วงวันนั้นๆ
    datefrom : (string) ระบุเป็นคศ. YY-MM-DD
    dateto :  (string) ระบุเป็นคศ. YY-MM-DD
    '''
    ###########
    datefrom = datefrom.replace("-","")
    dateto = dateto.replace("-","")
    
    if(person==False):
     url =  "https://market.sec.or.th/public/idisc/th/Viewmore/r246-2" \
      + "?SearchSymbol="+symbolOrName+"&ListedType=listed&DateType=1&DateFrom="+datefrom \
      +"&DateTo="+dateto
    if(person):
       person = quote(symbolOrName) #.encode('utf-8')
       url =  "https://market.sec.or.th/public/idisc/th/Viewmore/r246-2" \
          + "?SearchPerson="+person+"&ListedType=listed&DateType=1&DateFrom="+datefrom \
          +"&DateTo="+dateto  
       #print(url)
    
    ###########
    context = ssl._create_unverified_context()
    req =  request.Request(url) # this will make the method "POST"
    resp = request.urlopen(req,context=context)
    soup = BeautifulSoup(resp.read() , "lxml")
    
    ###########
    rows = soup.find('table', id='gPP10T01')
    
    ct = 0
    data = rows.find_all("tr")
    symbolDS = []
    nameDS = []
    type_rDS = []
    type_assetDS = []
    pct_beforeDS = []
    ptc_actionDS = []
    ptc_afterDS = []
    date_actionDS = []
    
    for i in range(len(data)):
     if(i>0):   
      tdData = (data[i].find_all("td"))
    
      if("ไม่พบข้อมูล" in tdData[0]):
          print(tdData[0].text)  
          return 0
            
      symbol = (tdData[0].text)
      symbolDS.append(symbol) 
    
      name = (tdData[1].text)   
      nameDS.append(name) 
    
      type_r = (tdData[2].text)
      type_rDS.append(type_r)
    
      type_asset = (tdData[3].text) 
      type_assetDS.append(type_asset)
    
      pct_before = (tdData[4].text)
      pct_beforeDS.append(pct_before)
    
      ptc_action = (tdData[5].text)
      ptc_actionDS.append(ptc_action)
    
      ptc_after = (tdData[6].text)
      ptc_afterDS.append(ptc_after)
    
      date_action = (tdData[7].text) 
      date_actionDS.append(date_action)
    
    ###########
    df = pd.DataFrame({"symbol":symbolDS,"name":nameDS,"type":type_rDS,"asset":type_assetDS,
              "pctBefore":pct_beforeDS,"pctAction":ptc_actionDS,"pctAfter":ptc_afterDS,"date":date_actionDS})
    
    return df