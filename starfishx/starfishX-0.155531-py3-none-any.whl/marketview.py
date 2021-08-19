#marketview.py
import pandas as pd
import requests
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt

###################### ส่วนที่ใช้ Library ภายใน ###################
try:
    #ลำดับมีผลพยายามโหลดที่ ใน folder ที่กำลัง Implement ก่อน
    from starfishX import config as con 
    #print("Dev")
except:
    #print("Debug")
    import starfishX.config as con

prefix = "starfishX."

if(con.__mode__=="debug"):
    prefix = ""

# สำหรับ getMemberOfIndex    #starfishX Production #__init__ debug Mode
#from starfishX.indexMarket import indexMarket
exec("from "+prefix+"indexMarket import indexMarket")
###################### END ส่วนที่ใช้ Library ภายใน ###################

 

class Market(Enum):
 PE = "PE"
 Index = "Index"

def processHistMarket(MarketType):
 typeH = MarketType.value   
 ##############################################   
 if(typeH=="PE"):
  url = "https://www.set.or.th/static/mktstat/Table_PE.xls"
  filename = "Table_PE.html"

 if(typeH=="Index"):
  url = "https://www.set.or.th/static/mktstat/Table_Index.xls"
  filename = "Table_Index.html"
 
 # download the file contents in binary format
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
   
 r = requests.get(url,headers=headers)

 # open method to open a file on your system and write the contents
 with open(filename, "wb") as code:
    code.write(r.content)
 ##############################################

 ##############################################   
 df = pd.read_html(filename) 
 ##############################################
 if(typeH=="Index"):
  rp = pd.DataFrame({ "SET":df[1].columns[1],"SET50":df[1].columns[2]
                   ,"SET100":df[1].columns[3],"sSET":df[1].columns[4]
                   ,"SETCLMV":df[1].columns[5],"SETHD":df[1].columns[6]
                   ,"SETTHSI":df[1].columns[7],"SETWB":df[1].columns[8]
                   ,"mai":df[1].columns[9]},index=df[1].columns[0])

  rp = rp.drop(rp.index[0])
  rp = rp.drop(rp.index[0])

  for i in rp.columns:
    rp[i] = rp[i].str.replace(",","")
    rp[i] = pd.to_numeric(rp[i], errors='coerce')
    #rp[i] = rp[i].astype(float)
    
  rp = rp.sort_index()   
  rp.index = pd.to_datetime(rp.index)
    
 ##############################################   
 if(typeH=="PE"):
  rp = df[1]
  rp.columns = rp.iloc[0]
  rp = rp.set_index("Month-Year")
  rp = rp.drop(rp.index[0])
  rp.index = pd.to_datetime(rp.index)

  rp = rp.sort_index()
  for i in rp.columns:
    rp[i] = rp[i].astype(float)  
    
 ##############################################
 return rp

##############################################
##############################################
def marketview(indexType,start="1900-01-01",viewplot=True):
 """
    Returns Close Index,PE : Close Index ตามประเภทของ Index นั้นๆ , PE ของ Index
    
    arg1 (indexMarket) : ประเภทของดัชนีที่เราต้องการ เช่น sx.indexMarket.SET , sx.indexMarket.SET50 เป็นต้น
    
    arg2 (str)    : start ปี โดยเป็นปี พ.ศ. เช่น "2010-01-01" YYYYMMDD 

    arg3 (Boolean) : viewplot แสดงกราฟผลของราคาปิดดัชนีและ PE หรือไม่ 
    
 """     
 if(not isinstance(indexType, indexMarket)):
    print("Data Type indexMarket Not Match")
    return 0

 marketType = indexType.value
    
 p1 = processHistMarket(Market.Index)
 p2 = processHistMarket(Market.PE)
 
 rp = pd.concat([p1[marketType], p2[marketType]],axis=1)
 rp.columns = ["index","pe"]
    
 rp = rp.dropna()  
 
 if(start!=""):
    rp = rp[rp.index>=start]   

 if(viewplot==True):   
  plt.subplot(211)
  rp['index'].plot(title=marketType.upper()+" INDEX",figsize=(20,10))
  plt.subplot(212)
  rp['pe'].plot(title=marketType.upper()+" INDEX : P/E",figsize=(20,10))
 
 return rp[rp.index>=start] 




def marketViewForeignTrade(indexType,start="",viewplot=True,widthP=20,heightP=6):
 """
    Returns DataFrame : ปริมาณซื้อและขายของนักลงทุนต่างชาติแยกตามประเภทตลาด SET และ mai
    
    arg1 (indexMarket) : ประเภทของดัชนีที่เราต้องการ เช่น sx.indexMarket.SET , sx.indexMarket.mai โดยใช้ได้เพียง 2 ตลาดเท่าน้ัน
    
    arg2 (str)    : year ปี โดยเป็นปี พ.ศ. เช่น "2010-01-01" YYYYMMDD 

    arg3 (Boolean) : viewplot แสดงกราฟผลของราคาปิดดัชนีและ PE หรือไม่ 
    
 """  
 #ตรวจ data type   
 if(not isinstance(indexType, indexMarket)):
    print("Data Type indexMarket Not Match")
    return 0
 
 #support แค่ set และ mai   
 typeM = indexType.value
    
 if(not (typeM=="SET" or typeM=="mai")): 
  print("NOT SUPPORT., "+typeM)  
  return 0 
        
 filename = "Table_ForeignTrade.html"
 url = "https://www.set.or.th/static/mktstat/Table_ForeignTrade.xls"
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
   
 r = requests.get(url,headers=headers)

 # open method to open a file on your system and write the contents
 with open(filename, "wb") as code:
    code.write(r.content)
 ##############################################
 
 ##############################################   
 df = pd.read_html(filename) 
 ##############################################
 rp = df[1]
 rp = rp.drop(rp.index[0])
 rp = rp.drop(rp.index[0])  
 rp.columns = ["Date","SET.BUY","SET.SELL","mai.BUY","mai.SELL"]   
 rp["Date"] = pd.to_datetime(rp["Date"])
 rp = rp.set_index("Date")   
 rp = rp.sort_index()
   
 ##############################################
 # clean กับ ปรับ data type เอาพวกค่าว่างออก   
 for i in rp.columns:
    rp[i] = rp[i].str.replace(",","")
    rp[i] = pd.to_numeric(rp[i], errors='coerce')
 
 ##############################################
 rp['SET.NET'] = rp['SET.BUY']-rp['SET.SELL']
 rp['mai.NET'] = rp['mai.BUY']-rp['mai.SELL']
 
 ##############################################
 if(viewplot==True):
   #ป้อง date format ที่มีชั่วโมงนาที 
   rp['DateReport'] = pd.to_datetime(rp.index)
   rp['DateReport'] = rp['DateReport'].dt.strftime('%Y-%m') 
   
   typeMC = typeM+".NET" 

   if(start!=""):  
     rp[rp.index>=start][["DateReport",typeMC]]. \
        plot(figsize=(widthP,heightP),kind="bar",x="DateReport",y=[typeMC],title="Foreign Trade on "+typeM) 
   else:
     rp[["DateReport",typeMC]]. \
        plot(figsize=(widthP,heightP),kind="bar",x="DateReport",y=[typeMC],title="Foreign Trade on "+typeM)
        
 return rp       