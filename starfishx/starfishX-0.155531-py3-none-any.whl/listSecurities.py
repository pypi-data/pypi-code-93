#listSecurities.py
import requests
from bs4 import BeautifulSoup
import pandas as pd

#https://www.set.or.th/set/commonslookup.do?language=th&country=TH&prefix=NUMBER
#https://www.set.or.th/set/commonslookup.do?language=th&country=TH&prefix=A 
def listSecurities(progress=True,industry=False):
    #สร้าง index ที่จะไปโหลดข้อมูลของ set
    ABC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    listA = []
    for i in ABC:
      listA.append(i)
    
    listA.append("NUMBER")
    
    
    cnt = 0
    for i in listA:
     headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
     url = "https://www.set.or.th/set/commonslookup.do?language=th&country=TH&prefix="+i
     r = requests.get(url,headers)
     soup = BeautifulSoup(r.content, "lxml")

     listshare = soup.find_all("table",{"class":"table table-profile table-hover table-set-border-yellow"})
     listshare = listshare[0].find_all("tr")
    
     symbol = []
     namestock = []
     typemarket = []
     industry_ds = []
     for j in (range(1,len(listshare))): 
          k1 = listshare[j].find_all("td")[0].text.strip() 
          symbol.append(k1)
          k2 = listshare[j].find_all("td")[1].text.strip() 
          namestock.append(k2)
          k3 = listshare[j].find_all("td")[2].text.strip() 
          typemarket.append(k3)
          
          if(industry):
            k1 = k1.replace("&","%26")
            headers_detail = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            url_detail = "https://www.set.or.th/set/factsheet.do?symbol="+k1+"&ssoPageId=3&language=th&country=TH"
            r_detail = requests.get(url_detail,headers_detail)
            soup_detail = BeautifulSoup(r_detail.content, "lxml")
            
            ctx = soup_detail.find_all("table",{"class":"table-factsheet-padding0"})
            k4 = ctx[0].find_all("tr")[0].find_all("td")[0].text.strip()
            industry_ds.append(k4)

     if(cnt==0):  
      cnt = cnt+1 
      if(progress==True):
        print("Processing.",end="") 

      if(industry):
       sData = pd.DataFrame({"symbol":symbol,"name":namestock,"market":typemarket,"industry":industry_ds})
      else:    
       sData = pd.DataFrame({"symbol":symbol,"name":namestock,"market":typemarket})

     else:
      if(industry): 
        sTmp = pd.DataFrame({"symbol":symbol,"name":namestock,"market":typemarket,"industry":industry_ds})
      else:
        sTmp = pd.DataFrame({"symbol":symbol,"name":namestock,"market":typemarket})

      sData = sData.append(sTmp) 

     if(progress==True):   
       print(".",end="") 

    if(progress==True):
      print("Complete")
    sData = sData.set_index("symbol")
    return sData