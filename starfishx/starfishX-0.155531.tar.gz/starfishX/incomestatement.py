#incomestatement.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

 
def getIncomeStatement(symbol):
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
  symbolMofi = symbol.replace("&","%26")  
  r = requests.post("https://www.set.or.th/set/factsheet.do?symbol="+symbolMofi,headers=headers)
  r.content
  soup = BeautifulSoup(r.content, "lxml") 

  if len(soup.find_all("table", {"class" : "table-factsheet-padding0"}))==0:
     print("ไม่พบข้อมูล")
     return 0

  #g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[19].find_all("td")
  #findStep = soup.find_all("table", {"class" : "table-factsheet-padding0"})[19].find_all("tr")
  #if not "งบกำไรขาดทุนเบ็ดเสร็จ (ลบ.)" in str(g_data):
  #  g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[20].find_all("td")
  #  findStep = soup.find_all("table", {"class" : "table-factsheet-padding0"})[20].find_all("tr")
  

  tmpdata = soup.find_all("table", {"class" : "table-factsheet-padding0"})
  if("งบกำไรขาดทุนเบ็ดเสร็จ (ลบ.)" in tmpdata[19].text):
    g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[19].find_all("td")
    findStep = soup.find_all("table", {"class" : "table-factsheet-padding0"})[19].find_all("tr")
  elif("งบกำไรขาดทุนเบ็ดเสร็จ (ลบ.)" in tmpdata[20].text):
    g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[20].find_all("td")
    findStep = soup.find_all("table", {"class" : "table-factsheet-padding0"})[20].find_all("tr")
  elif("งบกำไรขาดทุนเบ็ดเสร็จ (ลบ.)" in tmpdata[18].text):
    g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[18].find_all("td")
    findStep = soup.find_all("table", {"class" : "table-factsheet-padding0"})[18].find_all("tr") 
  elif("งบกำไรขาดทุนเบ็ดเสร็จ (ลบ.)" in tmpdata[17].text):
    g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[17].find_all("td")
    findStep = soup.find_all("table", {"class" : "table-factsheet-padding0"})[17].find_all("tr")   
  elif("งบกำไรขาดทุนเบ็ดเสร็จ (ลบ.)" in tmpdata[16].text):
    g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[16].find_all("td")
    findStep = soup.find_all("table", {"class" : "table-factsheet-padding0"})[16].find_all("tr") 
  elif("งบกำไรขาดทุนเบ็ดเสร็จ (ลบ.)" in tmpdata[21].text):
    g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[21].find_all("td")
    findStep = soup.find_all("table", {"class" : "table-factsheet-padding0"})[21].find_all("tr")
    
  ds  = []
  row = []
  cnt = 1
 
  #lenstep = 6    
  #if "M" in str(g_data[1]):
  #   lenstep = 7

  #ปรับโค้ดในการหาจำนวนคอลัมม์ที่แสดง เช่นกรณี vranda หุ้นใหม่จะมีคอลัมม์มาแค่ 3 คอลัมม์
  #0.15493
  lenstep = len(findStep[0].text.strip().split("\n"))+1    
  #print(lenstep)

  for i in range(0,len(g_data)-1):
    s = str(g_data[i].text.strip())
    s = s.rstrip()
    s = s.lstrip()
    
    row.append(s)
    #print(g_data[i].text.strip())
    cnt+=1
    if(cnt==lenstep): 
      ds.append(row)
      row = []
      cnt = 1
    
  df = pd.DataFrame(ds)
  df.columns = df.iloc[0]   
  
  #edit version 1.543
  df = df.drop(0)
  trim_columnsname(df) 
  df = df.set_index("งบกำไรขาดทุนเบ็ดเสร็จ(ลบ.)")
  return df


def getIncomeStatementCompare(liststock):
 ds = []
 if type(liststock) is list:
  for i in liststock:
    t = getIncomeStatement(i)#.report()
    #t = sx.trim_columnsname(t)
    ds.append(t)
    
 BusinessType = True
 for i in range(len(ds)):
  if(BusinessType==False):
    break
  for j in range(len(ds)):
   #chk = np.array_equal(ds[i][ds[i].columns[0]],ds[j][ds[j].columns[0]])
   chk = np.array_equal(ds[i].index,ds[j].index)
   BusinessType = chk
   if(BusinessType==False):
      print("Can not compare Income Statement")
      break
    
 if(BusinessType==False):
    return 0

 p = []
 #s0 = ds[0][[ds[0].columns[0]]]
 #s0 = ds[0].index 
 #p.append(s0)
 for i in range(len(ds)):
  #s0 = ds[i][[ds[i].columns[0]]]
  #s0.columns = [liststock[i]+"."+s0.columns[0]]
  s0 = ds[i][ds[i].columns[0]]  
  p.append(s0)  

 z = pd.concat(p, axis=1)
 return z



def trim_columnsname(df):
 cc = []
 for i in range(len(df.columns)):
   tmp = df.columns[i]
   tmp = tmp.replace("\xa0", "")
   tmp = tmp.replace(" ", "")  
   cc.append(tmp)
 df.columns = cc
 return df