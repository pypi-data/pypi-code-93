#openInterest.py
import requests
from bs4 import BeautifulSoup
import pandas as pd

from datetime import datetime
def str2Date(dt):
 k = dt.split(" ")
 if(k[1]=="ธ.ค."):
    k[1]=12
 elif(k[1]=="พ.ย."):
    k[1]=11    
 elif(k[1]=="ต.ค."):
    k[1]=10
 elif(k[1]=="ก.ย."):
    k[1]=9
 elif(k[1]=="ส.ค."):
    k[1]=8
 elif(k[1]=="ก.ค."):
    k[1]=7
 elif(k[1]=="มิ.ย."):
    k[1]=6
 elif(k[1]=="พ.ค."):
    k[1]=5
 elif(k[1]=="เม.ย."):
    k[1]=4
 elif(k[1]=="มี.ค."):
    k[1]=3
 elif(k[1]=="ก.พ."):
    k[1]=2    
 elif(k[1]=="ม.ค."):
    k[1]=1          
 k[2] = int(k[2])-543
 k = str(k[0])+"/"+str(k[1])+"/"+str(k[2])
 dt = datetime.strptime(k,'%d/%m/%Y')
 return dt

def listSSF(where=""): #,yesterday=False
 """
 ดูข้อมูลของ SSF ในซีรีย์ที่มีสถานะอยู่
 where : (string) คัดกองเฉพาะหุ้นแม่ที่สนใจ
 yesterday : (Boolean) ขอข้อมูลวันก่อนหน้าแทน
 """  
 #url = "https://www.tfex.co.th/tfex/dailyMarketReport.html?locale=en_US&marketListId=SF&instrumentId=&selectedDate=C&periodView=A"
 url = "https://www.tfex.co.th/tfex/dailyMarketReport.html?locale=en_US&marketListId=SF&instrumentId=&selectedDate=C&periodView=A"
 #if(yesterday==True):
 #    url = 'https://www.tfex.co.th/tfex/dailyMarketReport.html?locale=en_US'

 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
  #https://www.tfex.co.th/th/products/stock-mktdata.html
 r = requests.get(url,headers)
 soup = BeautifulSoup(r.content, "lxml")    
 #print(soup)
 cnt = 0
 underlying_ds = []
 ssf_ds = []
 underlying_name = ""
 if(len(soup.find_all("tbody"))==0):
    print("no content")    
    return 0
 for rowi,row in enumerate(soup.find_all("tbody")[0].find_all("tr"),0):
    if(rowi>0):
     c = row.find_all("td")
     #for j,k in enumerate(c,0):
     tmp = c[0].text.strip()   
     #--- fixbug 18 มิถุนายน 2020 --- 
     #--- เพราะรู้สึกมีการแก้หน้า HTML ของเพจ ทำให้ listSSF ออกมาผิดพลาด ---
     if( not(("Total" in tmp) or ("Futures" in tmp)) ):
        #if(cnt%4==0):
           underlying_name = tmp.replace("Futures","").strip()
        #if(cnt%4!=0):
           ssf_ds.append(tmp)
           underlying_ds.append(underlying_name)
        #cnt+=1
 df = pd.DataFrame({"underlying":underlying_ds},index=ssf_ds)
 if(where!=""):   
   return df[df["underlying"].str.upper().str.contains(where.upper())].index.tolist() 
 return df

def OpenInterestContractsProcess(symbol):
  url = "https://www.tfex.co.th/tfex/historicalTrading.html?locale=th_TH&symbol="+symbol+"&decorator=excel&locale=th_TH"
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
  
  r = requests.get(url,headers)
  soup = BeautifulSoup(r.content, "lxml")
    
  ct = soup.find_all("table")[2]
  rowData = ct.find_all("tr")
 
  date_ds = []
  data_oi = []
  for td in rowData:
    d = td.find_all("td")
    if((d[0].text.strip()!="วันที่") and (d[0].text.strip()!="รวมทั้งหมด")):
        date_ds.append(str2Date(d[0].text.strip()))
        oi = d[9].text.strip().replace(",","").replace("-","0")
        data_oi.append(float(oi))
        
  df = pd.DataFrame({"OI":data_oi},index=date_ds)
  return df

def OpenInterestContracts(listSymbol):
   """
   listSymbol : (list) ส่งค่าซีรีย์ SSF ที่ต้องการ ตัวอย่าง การดึงค่าจาก sx.listSSF(where='KCE')
                df = sx.OpenInterestContracts(["KCEU20","KCEZ20","KCEH21","KCEM21"])
   """
   if(type(listSymbol)==str):
      return OpenInterestContractsProcess(listSymbol)
   if(type(listSymbol)==list): 
      datasource = []
      for i in listSymbol:
         datasource.append(OpenInterestContractsProcess(i))
            
      k = pd.concat(datasource, axis=1, join='outer')#.sum(axis=1) 
      m = pd.DataFrame({"OI":k.sum(axis=1)})
      return m   