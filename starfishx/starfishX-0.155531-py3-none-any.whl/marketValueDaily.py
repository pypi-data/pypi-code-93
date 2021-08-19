try:
    #ลำดับมีผลพยายามโหลดที่ ใน folder ที่กำลัง Implement ก่อน
    #import config as con 
    from starfishX import config as con 
except:
    import starfishX.config as con

prefix = "starfishX."

if(con.__mode__=="debug"):
    prefix = ""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

#import squarify
import matplotlib
import matplotlib.pyplot as plt
#%config InlineBackend.figure_format ='retina'
from pylab import rcParams


exec("import "+prefix+"squarify")

def getTotalShare(symbol):
 url = "https://www.set.or.th/set/factsheet.do?symbol="+symbol+"&ssoPageId=3&language=th&country=TH"
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
 r = requests.get(url,headers,verify=False)
 soup = BeautifulSoup(r.content, "lxml")
 
 indexData = 11
    
 data = soup.find_all("table",{"class":"table-factsheet-padding0"})[indexData] #[2].find_all("tr") 
 #print(data.find_all("td"))
 
 if(not ("จำนวนหุ้นจดทะเบียน" in data.text)):
 #if(data.find_all("td")[0].text!='งบแสดงฐานะการเงิน (ลบ.)'):   
    indexData = 12
    data = soup.find_all("table",{"class":"table-factsheet-padding0"})[indexData]
 
 if(not ("จำนวนหุ้นจดทะเบียน" in data.text)):
 #if(data.find_all("td")[0].text!='งบแสดงฐานะการเงิน (ลบ.)'):   
    indexData = 13
    data = soup.find_all("table",{"class":"table-factsheet-padding0"})[indexData]
    
 if(not ("จำนวนหุ้นจดทะเบียน" in data.text)):
 #if(data.find_all("td")[0].text!='งบแสดงฐานะการเงิน (ลบ.)'):   
    indexData = 14
    data = soup.find_all("table",{"class":"table-factsheet-padding0"})[indexData]
    
 if(not ("จำนวนหุ้นจดทะเบียน" in data.text)):
 #if(data.find_all("td")[0].text!='งบแสดงฐานะการเงิน (ลบ.)'):   
    indexData = 15
    data = soup.find_all("table",{"class":"table-factsheet-padding0"})[indexData]   
 

 #print(indexData)
 p = 0
 totalShare = 0
 #print(data)
 for i in data.find_all("td"):
  if("จำนวนหุ้นจดทะเบียน" in i.text):
     p = 1
  else:
     if(p==1):
        totalShare = i.text.replace(",","")
        totalShare = float(totalShare)
        p = 0
        break
 return totalShare  



def marketValueDaily(marketype,sector="main"):
 """
 arg1 : indexMarket เช่น  sx.indexMarket.SET
 
 arg2 : sector จะใช้เฉพาะเมื่อ indexMarket เป็น SET เท่านั้น นอกนั้นไม่ต้องส่งค่านี้

 """ 
 rcParams['figure.figsize'] = 10, 10
 font = {'family' : 'normal','size': 10}
 matplotlib.rc('font', **font)
 
 typemarket = marketype.value
 if(typemarket=="SET" or typemarket=="mai"):
   url = "https://marketdata.set.or.th/mkt/sectorialindices.do?market="+typemarket+"&language=th&country=TH"
   if(typemarket=="mai" and sector!="main"):
     print("index not need Parameter 'sector' ")  
     return 0  
 else:
   url = "https://marketdata.set.or.th/mkt/sectorquotation.do?sector="+typemarket+"&language=th&country=TH"   
   if(sector!="main"):
      print("index not need Parameter 'sector' ")  
      return 0
    
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
 r = requests.get(url,headers,verify=False)
 soup = BeautifulSoup(r.content, "lxml")

 data = soup.find_all("tbody")[2].find_all("tr") 
 #print(data)
 secLB_DS =[]
 secValue_DS = []
 for i in data:
  try:
    if(i.get("class")[0]=="industry"):
      #print(1)
      info = i.find_all("td")  
      sec = info[0].text.strip()
      value = info[5].text.strip().replace(",","") 
      #print(sec,value)  
      if(sector=="main"):
        secLB_DS.append(sec)  
        secValue_DS.append(float(value)) 
  except:
      #print(2)
      kIndex = 5
      if(typemarket!="mai" and typemarket!="SET"): 
         kIndex = kIndex+6

      info = i.find_all("td")
      sec = info[0].text.strip()
      value = info[kIndex].text.strip() .replace(",","") 
      #print("\t",sec,value)
     
      if(sector=="sub" or typemarket=="mai" or typemarket!="SET"):  
       secLB_DS.append(sec)  
       secValue_DS.append(float(value)) 
      
 #print(secValue_DS)

 c = (sum(secValue_DS)**2)**(1/2)
 col = np.array(secValue_DS)/c
 cm = plt.cm.get_cmap('Spectral_r')

 # create a color palette, mapped to these values
 cmap = matplotlib.cm.Reds
 mini=min(secValue_DS)
 maxi=max(secValue_DS)
 norm = matplotlib.colors.Normalize(vmin=mini, vmax=maxi)
 colors = [cmap(norm(value)) for value in secValue_DS]

 ax = squarify.plot(sizes=secValue_DS, label=secLB_DS, color=cm(col), alpha=1.0)

 ax.set_title("Value : Industry/Sector") 
 plt.show()
 return pd.DataFrame({"lb":secLB_DS,"value":secValue_DS})