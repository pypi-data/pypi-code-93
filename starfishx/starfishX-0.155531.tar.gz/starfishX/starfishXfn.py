#starfishXfn.py
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import pandas as pd
import html5lib
import numpy as np

from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import csv

import ffn as loaddata
from math import pi
import math

#สำหรับ Function setTHforPlot()
import matplotlib as mpl
import matplotlib.font_manager as font_manager

#สำหรับ Function report10years()
import json

from tqdm import tqdm

#สำหรับ Monthly Return #######
import seaborn as sns
import datetime

from datetime import datetime as dtt #ใช้ในฟังก์ชั่น fillHistData 

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#%config InlineBackend.figure_format ='retina'

    
###################### ส่วนที่ใช้ Library ภายใน ###################
try:
    #ลำดับมีผลพยายามโหลดที่ ใน folder ที่กำลัง Implement ก่อน
    #import config as con 
    from starfishX import config as con
except:
    import starfishX.config as con

prefix = "starfishX."

if(con.__mode__=="debug"):
    prefix = ""   

# สำหรับ getMemberOfIndex    #starfishX Production #__init__ debug Mode
#from starfishX.indexMarket import indexMarket
exec("from "+prefix+"indexMarket import indexMarket")

exec("from "+prefix+"listSecurities import listSecurities")
###################### END ส่วนที่ใช้ Library ภายใน ###################



#AOR ช่วยในการตรวจสอบภายใน บลจ.
#backoffice ในการเปิดบัญชี
#MM การจัดการเงิน น้อยราย
#บลน.
#STA #ฟรีวิ่ว



########### load ราคาย้อนหลัง ######################
def loadHistData(symbol,start,end="",Volume=False,OHLC=False,US=False,col_clean=True):
    """
    Returns DataFrame ราคาปิดและปริมาณการซื้อขาย 
    
    arg1 (symbol) : หุ้นรายตัวหรือจะเป็น list ก็ได้เช่น "aot" หรือ ["aot","ptt"]
    
    arg2 (str)    : start ปี โดยเป็นปี พ.ศ. เช่น "2010-01-01" YYYYMMDD 

    arg3 (str)    : end ปี โดยเป็นปี พ.ศ. เช่น "2010-01-01" YYYYMMDD  ถ้าไม่ระบุจะเป็นวันที่ล่าสุด
    
    arg4 (Boolean): ต้องการปริมาณการซื้อขายหรือไม่ ถ้าไม่ระบุจะเป็นไม่แสดงปริมาณการซื้อขาย 
    
    arg5 (Boolean): แสดง OHLC หรือไม่ ถ้าไม่ระบุจะเป็น Close Price เท่านั้น

    arg6 (Boolean): หุ้น USA หรือหรือไทย หากหุ้นไทยไม่ต้องระบุ

    arg7 (Boolean): ต้องการ clean หัวของคอลัมน์หรือไม่ เช่น ':Close' เป็นต้น
    """ 
    if(end==""):
     now = datetime.datetime.now()
     end = (str(now.year).strip()+"-"+str(now.month).strip()+"-"+str(now.day).strip())
    
    endDate = end


    ##### ตรวจว่าเป็นดัชนีไหม 18 มิถุนายน 2020
    contain_index = False  
    symbol_index_only = []
    symbol_stock_only = []
    ##### 
    if(isinstance(symbol, list)):
      
      ############## block และคัดกรองส่วนของ index เท่านั้นก่อน ##########
      for i in range(len(symbol)):
        if(symbol[i][0]=="^"):
            symbol_index_only.append(symbol[i].replace("^",""))
            contain_index = True
        else:
            symbol_stock_only.append(symbol[i].replace("^",""))
      ############## endblock และคัดกรองส่วนของ index เท่านั้นก่อน ##########

     
      
      #return 0
      #print(symbol)
      qs = 0
      if(len(symbol_stock_only)>0):
       qs = crateQueryString(symbol_stock_only,Volume=Volume,OHLC=OHLC)
       if(US==False):
        k = qs.replace(".bk","")
       symbol_stock_only = k.split(",")
     
       #if(Volume==True):
       #  tmpsymbol = []
       #  for i in symbol:
       #    tmpsymbol.append(i)
       #    tmpsymbol.append(i+":Volume")
       #  symbol = tmpsymbol

    ########## จบส่วนเช็คแบบ List #########

    if(isinstance(symbol, str)):
      ##### ตรวจว่าเป็นดัชนีไหม 18 มิถุนายน 2020 
      if(symbol[0]=="^"):
        symbol = symbol.replace("^","")
        df = loadHistDataIndex(symbol,start,end)
        return df #ถ้าเป็น str แล้วเป็นชนิด index คืนค่าออกไปเลย -- 18 มิถุนายน 2020
        ###################################
        ###################################

      if(US==False):
        qs = symbol+".bk:Close"
      else:
        qs = symbol  
      tmpsymbol = [symbol]
      if(OHLC==True):
        if(US==False):
          qs = symbol+".bk:Open"+","+symbol+".bk:High"+","+symbol+".bk:Low"+","+symbol+".bk:Close" 
        else:
          qs = symbol+":Open"+","+symbol+":High"+","+symbol+":Low"+","+symbol+":Close"  

        tmpsymbol = ["Open","High","Low","Close"]  
      if(Volume==True):
         if(US==False):
          qs+=","+symbol+".bk:Volume"
         else:
          qs+=","+symbol

         #symbol = [symbol,symbol+":Volume"]
         tmpsymbol.append("Volume")
      else:   
         symbol = [symbol]
      
      symbol = tmpsymbol
 
    #จบส่วนของเช็ค str

    print(qs)
    if(qs!=0): #คือมีชุด query String ของหุ้นรายตัว*  ต่อมาสำเร็จ กรณีไม่สำเร็จเช่น ["^set","^set50"]
     try:
      df = loaddata.get(qs,start=start,end=endDate)
      
      if(len(symbol_stock_only)==0):
          symbol_stock_only = symbol
        
      df.columns = symbol_stock_only #symbol
      if(col_clean):
            df = col_cleanFn(df)
     except:
       print("Can't Load Data")
       return 0   
 
    if(contain_index):
       rpIndex = loadHistDataIndex(symbol_index_only,start=start,end=end)
       if(qs!=0):
         tmp = pd.merge(df,rpIndex,on='Date',how='inner')
         if(col_clean):
            tmp = col_cleanFn(tmp)
         return tmp   
       else:
         return rpIndex  


    ##### จบ กิจกรรม #####
    return df  
    
##################################################

#### col clean ####
def col_cleanFn(df):
 tmp_col = []
 for i in df.columns:
  tmp_col.append(i.replace(":Close","").upper())   
 df.columns = tmp_col
 return df
##################

############## update 18 มีถุนายน 2020 ############# 
############## รุ่นแก้ โหลดข้อมูลดัชนี #############   
from datetime import datetime as dt
def loadHistDataIndex(symbol,start,end):
 if(type(symbol)==str):
   if(not("sSET" in symbol)):
      symbol = symbol.upper()
 if(type(symbol)==list):
   #symbol = [i.upper() for i in symbol] 
   symbol_ = []
   for i in symbol:
     if(not("sSET" in i)):
       symbol_.append(i.upper())
     else:
       symbol_.append(i)  
   symbol = symbol_    

 #url
 url = "https://www.set.or.th/static/mktstat/setindex.csv"   
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   

 ##gen filename
 date = dt.now().strftime('%Y-%m-%d')
 filename = "setindex_"+date+".csv"
 r = requests.get(url,headers=headers)

 # open method to open a file on your system and write the contents
 with open(filename, "wb") as code:
    code.write(r.content)
 ##############################################
 df = pd.read_csv(filename,date_parser=["Date"] ,parse_dates=True,skipinitialspace=True)
 
 ##############################################   
 #specify input format '%d-%m-%Y' and output format '%Y-%m-%d' 
 #or change output as desired i.e. %d/%m/%Y to give dd/mm/yyyy
 #https://stackoverflow.com/questions/52089360/how-to-change-dd-mm-yyyy-date-format-to-yyyy-dd-mm-in-pandas/52114869#52114869
 df['Date'] = pd.to_datetime(df['Date'],format='%d/%m/%Y').dt.strftime('%Y-%m-%d')   
 df["Date"] = pd.to_datetime(df['Date'])
 df = df.set_index("Date")
    
 if(type(symbol)==str):
   return df[[symbol]][(df.index>=start) & (df.index<=end)]
 if(type(symbol)==list):
   return df[symbol][(df.index>=start) & (df.index<=end)]

############## end รุ่นแก้ โหลดข้อมูลดัชนี #############   

############  ผู้ถือหุ้น Shareholders #################
def listShareholders_Preprocess(symbol,eventdate):
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  

  symbolMofi = symbol.replace("&","%26")
    
  url = "https://www.set.or.th/set/companyholder.do?symbol="+symbolMofi
  r = requests.post(url,headers)
  soup = BeautifulSoup(r.content, "lxml")  

  #k = soup.find_all("table",{"class":"table table-hover table-info-wrap"})
  k = soup.find_all("tbody")
  dsSymbol  = []
  dsName    = []
  dsShares  = []
  dsPercent = []
  
  if(len(k)==0):
    return 0
   
  if("ไม่มีข้อมูล" in k[0].text):
    return 0

 

  for i in k[0].find_all("tr"):
   tr = i.find_all("td")
   name    = (tr[1].text.strip())
   Shares  = (tr[2].text.strip().replace(",","")) 
   Percent = (tr[3].text.strip())
    
   dsSymbol.append(symbol)   
   dsName.append(name)
   dsShares.append(float(Shares))
   dsPercent.append(float(Percent))
    
   
  df = pd.DataFrame({"Symbol":dsSymbol,"Name":dsName,"Share":dsShares,"Percent":dsPercent}) 
   
  if(eventdate==True):

    if(len(symbol)>=3): #เช่น S-R สั้นสุดคือ ชื่อหุ้น 1 ตัวอักษร
       twoLastSymbol = symbol[-2]+symbol[-1]
    else:
       twoLastSymbol = ""

    if("-R" == twoLastSymbol): #กรณี ส่ง -R เข้ามา
       
      dttmp = soup.find_all("table",{"class":"table table-hover table-info-wrap"})   
      dttmp = (dttmp[0].find_all("caption")[0].text)
      k_date = dttmp.replace("\xa0","").split("วันที่")[1]
      tmp = k_date.split("/")
      date = str(int(tmp[2])-543)+"-"+str(tmp[1])+"-"+str(tmp[0])
      df["Date"] = pd.to_datetime(date)

      symbol_no_R = symbol[0:len(symbol)-2]

      dfTypeDate = listShareholders(symbol_no_R,eventdate=True)
      TypeDate = dfTypeDate["Type"].iloc[0]

      if("n/a" in TypeDate):
         TypeDate = "n/a"

      df["Type"] = TypeDate

    else:    
      k = soup.find_all("tr",{"class":"topicbg"})
     
      d = k[1].td.text.replace("\xa0","").split("วันที่")[1].split("ประเภท:")
    
      #d[0],d[1]
      if(len(d)==2): #กรณีไม่มีประเภทของการปิดสมุดส่งมา
       k_date = d[0]
       k_type = d[1]
      else:
       k_date = d[0]
       k_type = "n/a:"+d[0]
    
      tmp = k_date.split("/")
      date = str(int(tmp[2])-543)+"-"+str(tmp[1])+"-"+str(tmp[0])
      df["Date"] = pd.to_datetime(date)

      if("n/a" in k_type):
         k_type = "n/a"
      df["Type"] = k_type

  pd.options.display.float_format = '{:,.2f}'.format  
  return df

def listShareholders(symbol,csv="",eventdate=False): 
  savefile = False  
  if(not(csv=="")):
    try:
      df = pd.read_csv(csv)
      df = df.set_index('no')
      return df  
    except:
      savefile = True 
      
        
  if( (isinstance(symbol, object))  and  (not(isinstance(symbol, list)))  and  (not(isinstance(symbol, str)))) :
      symbol = symbol.values.tolist()
        
  if(isinstance(symbol, list)):
     print("Processing..",end="")
     pListStock = []
     cnt = len(symbol)
     for i in range(len(symbol)):
            
       if(i<cnt-1):
         print(symbol[i],end=",")
       else:
         print(symbol[i],end="") 
            
       k = listShareholders_Preprocess(symbol[i],eventdate)
       if(type(k)==int): #พวกหุ้นเข้าใหม่
         pass
       else: 
         pListStock.append(k)
        
     ds = pd.concat(pListStock) 
     ds['no'] = np.arange(1,len(ds)+1)
     ds = ds.set_index('no')
     print(" Complete",end="") 
        
     if(savefile==True):
        ds.to_csv(csv)
     return ds
  else:
     ds = listShareholders_Preprocess(symbol,eventdate)
     if(type(ds)==int): #พวกหุ้นเข้าใหม่
        return 0
     ds['no'] = np.arange(1,len(ds)+1)
     ds = ds.set_index('no')  
     return ds  

def findPathShareholders(self,who):
    return self[self['Name'].str.contains(who)==True]

#Dynamically Add a Method to a Class in Python
#https://medium.com/@mgarod/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
setattr(pd.core.frame.DataFrame, 'findPathShareholders', findPathShareholders)
#############################

 
#%config InlineBackend.figure_format ='retina'
def RelativeStrength_hist(dateStart,dateStop,setUni,plotState,sp_data=None,numColPerRow=10,market=None):
 '''
 ตัวอย่าง
 df = sx.RelativeStrength_hist(dateStart="2020-07-01",
                              dateStop="2020-07-17",setUni=sx.indexMarket.SET100,
                              plotState=True,sp_data=["JMART"])

 dateStart : (str) วันที่เริ่มต้น
 dateStop : (str) วันที่จบการเทรด
 setUni : (indexMarket) เช่น set50, set100 ถ้าเป็น set อาจจะกินเวลานานมาก
 sp_date : (list) กรณีอยากเสริมหุ้นที่อยู่นอกเหนือดัชนี      
 plotState : (Boolean) True/False แสดงผลกราฟหรือไม่แสดง  
 numColPerRow : (int) จำนวนแถวที่แสดงข้อมูล ถ้า plotState เป็น True                        
 ''' 
 #symbol = ["tdex"] 
 #qs = crateQueryString(symbol)
 #tdex = loaddata.get(qs,start=dateStart) #จะใช้ startDate เป็นจุดเริ่มต้น และ Dateปัจจุบันเป็น EndDate
 #tdex.columns = ['close']

 if(market==None):
   market = setUni

 symbol = "^"+market.value
 #print(symbol)
 tdex = loadHistData(symbol,start=dateStart,end=dateStop) 
 tdex.columns = ['close']
 

 tdexbusket = pd.DataFrame({"startDate":tdex.iloc[0],"endDate":tdex.iloc[-1],"symbol":"tdex"})
 tdexbusket = tdexbusket.set_index('symbol')  
 
 #ดึงรายชื่อหุ้นใน set50 หรือ set100  
 #busketDS = getMemberOfIndex(indexMarket.SET50)   
 busketDS = getMemberOfIndex(setUni)
 #print(type(busketDS))

 if(sp_data!=None):
   key_index = np.array(range(len(busketDS),len(busketDS)+len(sp_data)))
   new_data = pd.DataFrame({"symbol":sp_data},index=key_index)
   busketDS  = busketDS.append(new_data)


 #print(busketDS)
 #return 0
 busket = pd.DataFrame()
 busketDS = np.array(busketDS)
 cnt = len(busketDS)
 for i in range(cnt):
    symbol = busketDS[i][0]
    qs = crateQueryString([symbol])
    if(i<cnt-1):
      print(symbol,end=",")
    else:
      print(symbol,end="")  
    

    df = loaddata.get(qs,start=dateStart,end=dateStop)
    df.columns = [symbol]
    
    if(i==0):
     busket = df
    else:
     busket = busket.join(df)
  
 tmpRSX = pd.DataFrame()
 dayCnt = len(busket)
 stockCnt = len(busket.columns) 

 for i in range(1,dayCnt): #each day
  rs_ds = []
  for j in range(stockCnt): #each stock
    beginStockPrice = busket[busket.columns[j]].iloc[0]
    endStockPrice = busket[busket.columns[j]].iloc[i]
    
    #print(tdex)
    #return 0
    
    beginIndex = tdex.iloc[0].values[0]
    endIndex = tdex.iloc[i].values[0]

    #print(endStockPrice,beginStockPrice,beginIndex,endIndex)
    #print(beginIndex,endIndex)
    #return 0

    rs = ((endStockPrice/beginStockPrice) /  (endIndex/beginIndex))
    rs_ds.append(rs)

  if(i==1):
   tmpRS = pd.DataFrame(rs_ds).T
   tmpRS.columns = busket.columns
   tmpRS['Date'] = tdex.index[i]

   tmpRSX = tmpRS.set_index("Date")  
  else:
   tmpRS = pd.DataFrame(rs_ds).T
   tmpRS.columns = busket.columns
   tmpRS['Date'] = tdex.index[i]
   tmpRS = tmpRS.set_index("Date") 
   tmpRSX = tmpRSX.append(tmpRS) 

 print("..",end="")
 print(" End Process")   

 
 tmpRSX_rank = pd.DataFrame()
 for i in range(len(tmpRSX)):

  t = pd.DataFrame(tmpRSX.iloc[i].sort_values(ascending=False))
  t['RANK'] = list(range(len(t), 0,-1))
  t.columns = ['RS','RANK']
  maxRank = t['RANK'].max()
  minRank = t['RANK'].min()
  maxScope = 99
  minScope = 1
  S = (minScope-maxScope)/(minRank-maxRank)
  Int = minScope - S*minRank
  t['RS_Rank'] = t['RANK']*S+Int
    
  if(i==0):   
   tmpRS_rank = pd.DataFrame(t['RS_Rank'])
   tmpRS_rank = tmpRS_rank.sort_index()
   tmpRS_rank = tmpRS_rank.T
   tmpRS_rank['Date'] = tmpRSX.index[i]
   tmpRSX_rank = tmpRS_rank.set_index("Date")
  else:
   tmpRS_rank = pd.DataFrame(t['RS_Rank'])
   tmpRS_rank = tmpRS_rank.sort_index()
   tmpRS_rank = tmpRS_rank.T
   tmpRS_rank['Date'] = tmpRSX.index[i]  
   tmpRS_rank = tmpRS_rank.set_index("Date") 

   tmpRSX_rank = tmpRSX_rank.append(tmpRS_rank)  



 from pylab import rcParams
 rcParams['figure.figsize'] = 50, 50   
 num_row = int(np.ceil(len(busketDS)/numColPerRow))
 #print(num_row,numColPerRow)  

 if(plotState):   
  fig, axes = plt.subplots(nrows=num_row, ncols=numColPerRow)
  k = 0
  for i in range(num_row):
   for j in range(numColPerRow):  
    symbol = tmpRSX_rank.columns[k]
    ax = tmpRSX_rank[symbol].plot(ax=axes[i,j],figsize=(30,30),title=symbol) 
    axes[i,j].axhline(90,color='red',ls='--')
    axes[i,j].axhline(95,color='red',ls='--')
    axes[i,j].set_ylim(0,100)
    ax.get_xaxis().set_visible(False)    
    k=k+1      
    if(k==len(busketDS)): #ตรวจสอบความยาวของ Uni 
       break

 tmpRSX_rank.index = tmpRSX_rank.index.date #เทคนิค เอาเวลาออกจาก date คือตัด HH:MM:SS ออก   
 return tmpRSX_rank  

#หาอัตราการเปรียบเปลี่ยนราคาเปรียบเทียบกับดัชนี
#Function RelativeStrengthRank(dateStart,setUni)
#parameter 
#  setUni ตัวแทนทั้งหมดที่จะนำไปเปรียบเทียบ  ตอนนี้ส่งค่าเป็น 'SET50' หรือ 'SET100'
#  dateStart วันที่เริ่มต้น โดยวันที่สุดท้ายจะเป็นวันปัจจุบัน เช่น 

#return DataFrame ของ RelativeStrength Rank คะแนน 1-99


def RelativeStrengthRank(dateStart,dateStop,setUni,dataset=0,viewlog=False):
  '''
  dateStart : (str) "YYYY-MM-DD"
  dateStop : (str) "YYYY-MM-DD"
  setUni : (str) เช่น "set","set50","set100"
  '''
  #เตรียมส่วนของดัชนี  
  setUni = setUni.lower() #ป้องกันคนกรอกมาเป็นตัวใหญ่
  if(setUni=="set50"):
    #symbol = ["tdex"] 
    symbol = ["^set50"] 
    setUni = indexMarket.SET50
  elif(setUni=="set100"):
    #symbol = ["bset100"]
    symbol = ["^set100"]
    setUni = indexMarket.SET100
  elif(setUni=="set"):
    #symbol = ["tdex"]
    symbol = ["^set"]
    #setUni = indexMarket.SET
  elif(setUni=="join"):
    symbol = ["tdex"]

  
  qs = crateQueryString(symbol)
  
  #print(f"loadHistDataIndex({symbol},start='{dateStart}')",symbol,dateStart)
  #return 0
  #ETFIndex = loaddata.get(qs,start=dateStart,end=dateStop) #จะใช้ startDate เป็นจุดเริ่มต้น และ Dateปัจจุบันเป็น EndDate
  ETFIndex = loadHistData(symbol,start=dateStart,end=dateStop)
   

  ETFIndex.columns = ['close']  
  
  ETFbusket = pd.DataFrame({"startDate":ETFIndex.iloc[0],"endDate":ETFIndex.iloc[-1],"symbol":symbol})
  ETFbusket = ETFbusket.set_index('symbol')
    
  #ดึงรายชื่อหุ้นใน set50 หรือ set100  
  if(setUni=="set"):
    tmpbusketDS = listSecurities().index
    busketDS = pd.DataFrame({"symbol":tmpbusketDS.tolist()})  
  elif(setUni=="join"):
    busketDS = dataset
  else:
    busketDS = getMemberOfIndex(setUni) 
 
  
  busket = pd.DataFrame()
  busketDS = np.array(busketDS)
  cnt = len(busketDS)
  print(cnt)
  if(viewlog==True):
    print("Process Data...",end="")
  for i in range(cnt):
    symbol = busketDS[i][0]
    symbol = symbol.replace("&","%26") 
    qs = crateQueryString([symbol])
    if(i<cnt-1):
      if(viewlog==True):
        print(symbol,end=",")
    else:
      if(viewlog==True):
        print(symbol,end="")  
    
    try:
     df = loaddata.get(qs,start=dateStart,end=dateStop)
     df.columns = ['close']
     print(symbol,end=" ")

     k1 = pd.DataFrame({"startDate":df.iloc[0],"endDate":df.iloc[-1],"symbol":symbol}) 
     k1 = k1.set_index('symbol')
     busket = busket.append(k1) 
    except:
      print("Can't Get -- "+qs)

  rs_data = []
  for i in range(len(busket)):
    t1 = (busket['endDate'].values[i] / busket['startDate'].values[i])
    t2 = (ETFbusket['endDate'].values[0] / ETFbusket['startDate'].values[0])
    rs_tmp = t1/t2
    rs_data.append(rs_tmp)
    
    
  busket['RS'] = rs_data
  busket = busket.sort_values(by=['RS'], ascending=False)
  busket['RANK'] = list(range(len(busket), 0,-1))
  maxRank = busket['RANK'].max()
  minRank = busket['RANK'].min()
  maxScope = 99
  minScope = 1
  S = (minScope-maxScope)/(minRank-maxRank)
  Int = minScope - S*minRank
  busket['RS_Rank'] = busket['RANK']*S+Int  
    
  return busket 



exec("from "+prefix+"loadHistData_v2 import loadHistData_v2")

#%config InlineBackend.figure_format ='retina'
def RelativeStrength_hist_with_progress1(dateStart,dateStop,setUni,plotState,sp_data=None,numColPerRow=10,market=None):

 if(market==None):
   market = setUni

 symbol = "^"+market.value
 #print(symbol)
 tdex = loadHistData(symbol,start=dateStart,end=dateStop) 
 tdex.columns = ['close']
 

 tdexbusket = pd.DataFrame({"startDate":tdex.iloc[0],"endDate":tdex.iloc[-1],"symbol":"tdex"})
 tdexbusket = tdexbusket.set_index('symbol')  
 
 #ดึงรายชื่อหุ้นใน set50 หรือ set100  
 #busketDS = getMemberOfIndex(indexMarket.SET50)   
 busketDS = getMemberOfIndex(setUni)
 #print(type(busketDS))

 if(sp_data!=None):     
   key_index = np.array(range(len(busketDS),len(busketDS)+len(sp_data)))
   new_data = pd.DataFrame({"symbol":sp_data},index=key_index)
   #busketDS  = busketDS.append(new_data)
   busketDS = pd.concat([new_data, busketDS], ignore_index=True)
   busketDS = busketDS.sort_values('symbol',ascending=False)

 #print(busketDS)
 #return 0
 busket = pd.DataFrame()
 busketDS = np.array(busketDS)
 cnt = len(busketDS)
 for i in range(cnt):
    symbol = busketDS[i][0]
   
    qs = crateQueryString([symbol])
    #if(i<cnt-1):
    #  print(symbol,end=",")
    #else:
    #  print(symbol,end="")  
    
    print(qs)

    #fix bug กณณี load ไม่ขึ้น 
    try:
      df = loaddata.get(qs,start=dateStart,end=dateStop)
      df.columns = [symbol]
    except:  

      df = loadHistData_v2(symbol=symbol,start=dateStart,end=dateStop)[['Close']]
      df.columns = [symbol]
    
    yield df 
  
def RelativeStrength_hist_with_progress2(basket,setUni,dateStart='2021-01-01',dateStop='2021-06-30',market=None):
 if(market==None):
   market = setUni

 symbol = "^"+market.value
 print(symbol)
 tdex = loadHistData(symbol,start=dateStart,end=dateStop) 
 tdex.columns = ['close']

 tmpRSX = pd.DataFrame()
 dayCnt = len(basket)
 stockCnt = len(basket.columns) 

 for i in range(1,dayCnt): #each day
  rs_ds = []
  for j in range(stockCnt): #each stock
    beginStockPrice = basket[basket.columns[j]].iloc[0]
    endStockPrice = basket[basket.columns[j]].iloc[i]
    
    #print(tdex)
    #return 0
    
    beginIndex = tdex.iloc[0].values[0]
    endIndex = tdex.iloc[i].values[0]

    #print(endStockPrice,beginStockPrice,beginIndex,endIndex)
    #print(beginIndex,endIndex)
    #return 0

    rs = ((endStockPrice/beginStockPrice) /  (endIndex/beginIndex))
    rs_ds.append(rs)

  if(i==1):
   tmpRS = pd.DataFrame(rs_ds).T
   tmpRS.columns = basket.columns
   tmpRS['Date'] = tdex.index[i]

   tmpRSX = tmpRS.set_index("Date")  
  else:
   tmpRS = pd.DataFrame(rs_ds).T
   tmpRS.columns = basket.columns
   tmpRS['Date'] = tdex.index[i]
   tmpRS = tmpRS.set_index("Date") 
   tmpRSX = tmpRSX.append(tmpRS) 

 print("..",end="")
 print(" End Process")   

 
 tmpRSX_rank = pd.DataFrame()
 for i in range(len(tmpRSX)):

  t = pd.DataFrame(tmpRSX.iloc[i].sort_values(ascending=False))
  t['RANK'] = list(range(len(t), 0,-1))
  t.columns = ['RS','RANK']
  maxRank = t['RANK'].max()
  minRank = t['RANK'].min()
  maxScope = 99
  minScope = 1
  S = (minScope-maxScope)/(minRank-maxRank)
  Int = minScope - S*minRank
  t['RS_Rank'] = t['RANK']*S+Int
    
  if(i==0):   
   tmpRS_rank = pd.DataFrame(t['RS_Rank'])
   tmpRS_rank = tmpRS_rank.sort_index()
   tmpRS_rank = tmpRS_rank.T
   tmpRS_rank['Date'] = tmpRSX.index[i]
   tmpRSX_rank = tmpRS_rank.set_index("Date")
  else:
   tmpRS_rank = pd.DataFrame(t['RS_Rank'])
   tmpRS_rank = tmpRS_rank.sort_index()
   tmpRS_rank = tmpRS_rank.T
   tmpRS_rank['Date'] = tmpRSX.index[i]  
   tmpRS_rank = tmpRS_rank.set_index("Date") 

   tmpRSX_rank = tmpRSX_rank.append(tmpRS_rank)  


 

 tmpRSX_rank.index = tmpRSX_rank.index.date #เทคนิค เอาเวลาออกจาก date คือตัด HH:MM:SS ออก   
 return tmpRSX_rank  


#หาอัตราการเปรียบเปลี่ยนราคาเปรียบเทียบกับดัชนี
#Function RelativeStrengthRank(dateStart,setUni)
#parameter 
#  setUni ตัวแทนทั้งหมดที่จะนำไปเปรียบเทียบ  ตอนนี้ส่งค่าเป็น 'SET50' หรือ 'SET100'
#  dateStart วันที่เริ่มต้น โดยวันที่สุดท้ายจะเป็นวันปัจจุบัน เช่น 

#return DataFrame ของ RelativeStrength Rank คะแนน 1-99


#หาอัตราการเปรียบเปลี่ยนราคาเปรียบเทียบกับดัชนี
#Function RelativeStrengthRank(dateStart,setUni)
#parameter 
#  setUni ตัวแทนทั้งหมดที่จะนำไปเปรียบเทียบ  ตอนนี้ส่งค่าเป็น 'SET50' หรือ 'SET100'
#  dateStart วันที่เริ่มต้น โดยวันที่สุดท้ายจะเป็นวันปัจจุบัน เช่น 

#return DataFrame ของ RelativeStrength Rank คะแนน 1-99


############################# find_zone ############################
def plotNormal(df,priceNow,bins):
    fig, ax = plt.subplots(figsize=(10,8))
    df.plot(kind='kde',ax=ax, legend=False, title='Histogram : Close Price')
    k = df.hist(grid=True, bins=bins,density=True, ax=ax)
    for i in k:
      ymax = i.dataLim.ymax
    ax.vlines(priceNow, 0, ymax, lw=1, color='r')
####################################################################

def findzone(df,layer,title):
    xt = np.arange(0,1,0.1)
    xt = np.append(xt,1)
    cnt = df.count().values[0]
    #layer = 30 #คล้ายๆ กับ อันตรภาคชั้น
    
    df.columns = ['close']
    k = pd.DataFrame((df.groupby(pd.cut(df["close"], layer)).count()['close']/cnt))
    price = df['close'].tail(1).values[0]
    p = pd.cut(df["close"], layer).cat.categories
    what_layer = 1
    k_index = 1
    for i in p:
     if(price in i):
      #print(i.right) #print(i.left) #กรอบบนกรอบล่างของ อันตรภาคชั้น
      what_layer = k_index
     k_index+=1 

    i_right = k['close'].iloc[0:what_layer].sum()
    i_left = k['close'].iloc[0:what_layer-1].sum()
    position_price_now = (i_right + i_left) / 2
    
    report = "Lower-Upper : "+str(round(i_left,4)).rstrip()+"%-"+str(round(i_right,4)).strip()+"%"
    print(report)
    k['close'].iloc[0:what_layer]#.sum()

    ax = pd.DataFrame(k.T.values).plot(kind='barh', stacked=True,xticks=xt,figsize=(10,8),title=str(title[0].upper()))
    plt.legend(k.index,bbox_to_anchor=(1, 1))
    ax.vlines(position_price_now, -1, 1, lw=1, color='r') #vlines(x, ymin, ymax, ...)

from matplotlib.colors import LogNorm

############################# Monthly Return #######################
def MonthlyReturn(symbol,startDate,endDate="",plot=True,OutPutfilename=""):
  qs = crateQueryString(symbol)
  if(endDate==""):
     now = datetime.datetime.now()
     endDate = (str(now.year).strip()+"-"+str(now.month).strip()+"-"+str(now.day).strip())   
  
  if("^" in qs):
    df = loadHistData(symbol,start=startDate,end=endDate) 
  else:
    df = loaddata.get(qs, start=startDate,end=endDate)
  
  df.columns = symbol
  df = df.rebase()
    
  df = df.dropna()
  #ignore divide by zero encountered in true_divide
  np.seterr(all='ignore')  
    
  perf = df.calc_stats() 
  K = perf[symbol[0]].return_table.drop(['YTD'], axis=1)
  
  if((plot==False) & (OutPutfilename=="")):
     return df,K

  sns.set()

  a4_dims = (12, 12)
  fig, ax = plt.subplots(figsize=a4_dims)
  snsPlot = sns.heatmap(K,center=0,ax=ax,annot=True, fmt=".2f")
  title = "Return "+symbol[0].upper()+" (Monthly)"
  ax.set_title(title,fontsize=18)

  if(OutPutfilename!=""):
    fig = ax.get_figure()
    fig.savefig(OutPutfilename) 
  return df,K
####################################################################


##################### Markowitz ##################################################
def crateQueryString(symbol,Volume=False,OHLC=False):
    QueryString = ""
    r = 0
    for i in symbol:
        if(Volume==False):
          if(OHLC==False):
            QueryString += i+".bk:"+"Close" 
          elif(OHLC==True):
            QueryString += i+".bk:"+"Open,"+i+".bk:"+"High,"+i+".bk:"+"Low,"+i+".bk:"+"Close"
        if(Volume==True):
          if(OHLC==False):
            QueryString += i+".bk:"+"Close,"+i+".bk:Volume"
          elif(OHLC==True):
            QueryString += i+".bk:"+"Open,"+i+".bk:"+"High,"+i+".bk:"+"Low,"+i+".bk:"+"Close,"+i+".bk:"+"Volume"

        if(r<len(symbol)-1):
          QueryString += ","   
        r+=1
    return QueryString

def MarkowitzPreload(symbol,startDate,stopDate):
    QueryString = crateQueryString(symbol)
    
    df = loaddata.get(QueryString, start=startDate,end=stopDate)
    return df
def MarkowitzProcess(df,alias,random=1000,plot=True):
    df.columns = alias
    stocks = np.array(df.columns)
    data = df
    data.sort_index(inplace=True)

    #convert daily stock prices into daily returns
    returns = data.pct_change()

    #calculate mean daily return and covariance of daily returns
    mean_daily_returns = returns.mean()
    cov_matrix = returns.cov()

    #set number of runs of random portfolio weights
    num_portfolios = random

    #set up array to hold results
    #We have increased the size of the array to hold the weight values for each stock
    results = np.zeros((4+len(stocks)-1,num_portfolios))

    for i in range(num_portfolios):
     #select random weights for portfolio holdings
     weights = np.array(np.random.random(len(stocks)))
     #rebalance weights to sum to 1
     weights /= np.sum(weights)
    
     #calculate portfolio return and volatility
     portfolio_return = np.sum(mean_daily_returns * weights) * 252
     portfolio_std_dev = np.sqrt(np.dot(weights.T,np.dot(cov_matrix, weights))) * np.sqrt(252)
    
     #store results in results array
     results[0,i] = portfolio_return
     results[1,i] = portfolio_std_dev
     #store Sharpe Ratio (return / volatility) - risk free rate element excluded for simplicity
     results[2,i] = results[0,i] / results[1,i]
     #iterate through the weight vector and add data to results array
     for j in range(len(weights)):
        results[j+3,i] = weights[j]

     #convert results array to Pandas DataFrame
    stocks = np.insert(stocks,0,"sharpe")
    stocks = np.insert(stocks,0,"stdev")
    stocks = np.insert(stocks,0,"return_port")
    results_frame = pd.DataFrame(results.T,columns=stocks)
  
    #locate position of portfolio with highest Sharpe Ratio
    max_sharpe_port = results_frame.iloc[results_frame['sharpe'].idxmax()]
    #locate positon of portfolio with minimum standard deviation
    min_vol_port = results_frame.iloc[results_frame['stdev'].idxmin()]


    if(plot==True):
      #create scatter plot coloured by Sharpe Ratio
      plt.scatter(results_frame.stdev,results_frame.return_port,c=results_frame.sharpe,cmap='RdYlBu')
      plt.xlabel('stdev')
      plt.ylabel('Returns')
      plt.colorbar()
      #plot red star to highlight position of portfolio with highest Sharpe Ratio
      plt.scatter(max_sharpe_port[1],max_sharpe_port[0],marker=(len(df.columns),1,0),color='r',s=200)
      #plot green star to highlight position of minimum variance portfolio
      plt.rcParams["figure.figsize"] = (8,8)
      #plt.scatter(min_vol_port[1],min_vol_port[0],marker=(5,1,0),color='g',s=200)

    return max_sharpe_port    


##################### EndPartofMarkowitz #########################################

##################### Who Hold #########################################
def getInitListWhoHold():  
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 #if(not re.match('^[a-zA-Z0-9\.]*$',symbol)):
 #  name = symbol
 #else:
 #  url = "https://www.set.or.th/set/companyprofile.do?symbol="+symbol+"&ssoPageId=4&language=th&country=TH"
 #  r = requests.post(url,headers)
 #  soup = BeautifulSoup(r.content, "lxml")
 #  name = soup.find_all("div", {"class" :"col-xs-12 col-md-12 col-lg-8"} )[0].find_all("h3")[0].text.split(":")[1].lstrip().rstrip()

 #mktcap = soup.find_all("table",{"class":"table"})[0].find_all("div",{"class":"col-xs-9 col-md-5"})[3].text.strip().replace(",","")
 #mktcapMain = float(mktcap)

 df = pd.read_csv("list_symbol_stock_market.csv")
 df = df.dropna()   

 symbolchild = []
 sharechild = []
 pricechild = []
 namehold = []
 i = 0
 for s in tqdm(df.Symbol):
  s = s.strip()
  url = "https://www.set.or.th/set/companyholder.do?symbol="+s+"&ssoPageId=6&language=th&country=TH"
  r = requests.post(url,headers)
  soup = BeautifulSoup(r.content, "lxml")
  if(len(soup.find_all("div",attrs={'style':'text-align:center;color:red;'}))==0):
   listshare = soup.find_all("table",{"class":"table table-hover table-info-wrap"})
   listshare = listshare[2].find_all("tr")
   for j in (range(1,len(listshare))):
    k = listshare[j].find_all("td")[1].text.strip()
    #if(name in k):
    namehold.append(k)
    symbolchild.append(s)
    pricechild.append(df.iloc[i]['Closing Price'])
    sharechild.append(float(listshare[j].find_all("td")[2].text.strip().replace(",",""))) 
  i=i+1

 dfreport = pd.DataFrame({"name":namehold,"symbol":symbolchild,"share":sharechild,"price":pricechild})
 #dfreport = pd.DataFrame({"name":namehold,"symbol":symbolchild})  
 dfreport.to_csv('whoHold.csv')
 return dfreport

def getWhoHold(string):
  df = pd.read_csv("whoHold.csv")  
  #df["price"] = df["price"].astype(float)
  #df["share"] = df["share"].astype(float)
  return df[["name","symbol","share","price"]][df['name'].str.contains(string)] 

def getWhoHoldCommonSize(StringSearch,angle):
 df = pd.read_csv("whoHold.csv")  
 df = df[["name","symbol","share","price"]][df['name'].str.contains(StringSearch)]
 
 #ตัดพวกที่ดึงราคาไม่ได้ออก 
 df = df[df["price"]!="-"]  

 df["price"] = df["price"].astype(float)
 df["share"] = df["share"].astype(float)

 df = df[["symbol","share","price"]].groupby(["symbol"]).agg({'share':'sum', 'price':'mean'})
 df["mktcap"] = df["share"] * df["price"] 
 df["commonsize"] = (df["mktcap"] / df["mktcap"].sum())
 dfx = pd.DataFrame({'commonsize': np.array(df.commonsize)},index=df.index)

 dfx.plot(kind="pie",y='commonsize',shadow=True,startangle=angle,figsize=(8, 8),autopct='%2.2f%%',title="Commonsize")
 plt.axis('off')
 plt.legend(loc='center left', bbox_to_anchor=(1.05, 0.5),fancybox=True, shadow=True) 
    
########################################################################




############## load info set ############################
def loadDB_set_mai():
 #df = pd.read_csv("file.csv",index_col="TIMESTAMP", parse_dates=True)
 return pd.read_csv("lab_find_cash.csv")
############## end load info set ############################

############## FindCash ############################
def findCASH(s):
 symbol = s
 #load data
 r = requests.post("https://www.set.or.th/set/factsheet.do?symbol="+symbol+"&ssoPageId=3&language=th&country=TH")
 r.content
 soup = BeautifulSoup(r.content, "lxml")  
 if len(soup.find_all("table", {"class" : "table-factsheet-padding0"}))==0:
   return np.NaN
 g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[17]
    
 if(g_data.find_all("td")[0].text!='งบแสดงฐานะการเงิน (ลบ.)'):
   g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[18]

 if(g_data.find_all("td")[0].text!='งบแสดงฐานะการเงิน (ลบ.)'):
   g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[19]
 
 if (g_data.find_all("td")[0].text!='งบแสดงฐานะการเงิน (ลบ.)'):
   g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[20] 

 
 #process string
 cash = g_data.find_all("tr")[1].find_all("td",{"class":"factsheet","align": "right"})[0].text.strip()
 cash = cash.replace(',', '')
 return np.float(cash)

############## EndFindCash ############################


############## CommonSizeBS ############################
def commonsizeBS(symbol):
 r = requests.post("https://www.set.or.th/set/companyfinance.do?type=balance&symbol="+symbol+"&language=th&country=TH")
 r.content
 soup = BeautifulSoup(r.content, "lxml") 
   
 g_data = soup.find_all("table", {"class" : "table table-hover table-info"})[2].find_all("td")
    
 #สร้าง DataFrame เปล่าๆ
 df = pd.DataFrame(columns=[symbol])
 totalasset = 0
 totalequity = 0
 totalliability =0
 for i in range(0,len(g_data)):
   s = trimstring2float(g_data[i])
   if(s=="รวมสินทรัพย์"):
     totalasset = float(trimstring2float(g_data[i+1]))
   if(s=="รวมหนี้สิน"):
     totalliability = float(trimstring2float(g_data[i+1]))
   if(s=="รวมส่วนของผู้ถือหุ้น"):
     totalequity = float(trimstring2float(g_data[i+1]))      

 for i in range(0,len(g_data)):
   s = trimstring2float(g_data[i])
   if(s=="รวมสินทรัพย์หมุนเวียน"):   
     df.loc["รวมสินทรัพย์หมุนเวียน",symbol] = float(trimstring2float(g_data[i+1]))
     df.loc["รวมสินทรัพย์หมุนเวียน","commonsize"] = (float(trimstring2float(g_data[i+1]))/totalasset)*100
   elif(s=="รวมสินทรัพย์ไม่หมุนเวียน"):
     df.loc["รวมสินทรัพย์ไม่หมุนเวียน",symbol] = float(trimstring2float(g_data[i+1]))
     df.loc["รวมสินทรัพย์ไม่หมุนเวียน","commonsize"] = (float(trimstring2float(g_data[i+1]))/totalasset)*100
   elif(s=="รวมหนี้สินหมุนเวียน"):
     df.loc["รวมหนี้สินหมุนเวียน",symbol] = float(trimstring2float(g_data[i+1]))
     df.loc["รวมหนี้สินหมุนเวียน","commonsize"] = (float(trimstring2float(g_data[i+1]))/totalasset)*100
   elif(s=="รวมหนี้สินไม่หมุนเวียน"):
     df.loc["รวมหนี้สินไม่หมุนเวียน",symbol] = float(trimstring2float(g_data[i+1]))
     df.loc["รวมหนี้สินไม่หมุนเวียน","commonsize"] = (float(trimstring2float(g_data[i+1]))/totalasset)*100  
   elif(s=="รวมส่วนของผู้ถือหุ้น"):
     df.loc["รวมส่วนของผู้ถือหุ้น",symbol] = float(trimstring2float(g_data[i+1]))
     df.loc["รวมส่วนของผู้ถือหุ้น","commonsize"] = (float(trimstring2float(g_data[i+1]))/totalasset)*100 
    
 return df  

############## CommonSizeIncomeStatement ############################
def commonsizeIS(symbol):
   r = requests.post("https://www.set.or.th/set/companyfinance.do?type=income&symbol="+symbol+"&language=th&country=TH")
   r.content
   soup = BeautifulSoup(r.content, "lxml") 
   
   g_data = soup.find_all("table", {"class" : "table table-hover table-info"})[2].find_all("td")

   #สร้าง DataFrame เปล่าๆ
   df = pd.DataFrame(columns=[symbol])
    
   total = 0
   for i in range(0,len(g_data)):
     s = trimstring2float(g_data[i])
     if(s=="รวมรายได้"):
        df.loc["รวมรายได้",symbol] = float(trimstring2float(g_data[i+1]))
        total = float(trimstring2float(g_data[i+1]))
        df.loc["รวมรายได้","commonsize"] = (float(trimstring2float(g_data[i+1]))/total)*100
     elif(s=="ต้นทุนขายสินค้าและหรือต้นทุนการให้บริการ"):
        df.loc["ต้นทุนขายสินค้าและหรือต้นทุนการให้บริการ",symbol] = float(trimstring2float(g_data[i+1]))
        df.loc["ต้นทุนขายสินค้าและหรือต้นทุนการให้บริการ","commonsize"] = (float(trimstring2float(g_data[i+1]))/total)*100
     elif(s=="ต้นทุนขายสินค้า"):
        df.loc["ต้นทุนขายสินค้า",symbol] = float(trimstring2float(g_data[i+1]))
        df.loc["ต้นทุนขายสินค้า","commonsize"] = (float(trimstring2float(g_data[i+1]))/total)*100
     elif(s=="ค่าใช้จ่ายในการขาย"):
        df.loc["ค่าใช้จ่ายในการขาย",symbol] = float(trimstring2float(g_data[i+1]))
        df.loc["ค่าใช้จ่ายในการขาย","commonsize"] = (float(trimstring2float(g_data[i+1]))/total)*100
     elif(s=="ค่าใช้จ่ายในการบริหาร"):
        df.loc["ค่าใช้จ่ายในการบริหาร",symbol] = float(trimstring2float(g_data[i+1]))
        df.loc["ค่าใช้จ่ายในการบริหาร","commonsize"] = (float(trimstring2float(g_data[i+1]))/total)*100
     elif(s=="ต้นทุนการให้บริการ"):
        df.loc["ต้นทุนการให้บริการ",symbol] = float(trimstring2float(g_data[i+1]))
        df.loc["ต้นทุนการให้บริการ","commonsize"] = (float(trimstring2float(g_data[i+1]))/total)*100 
     elif(s=="ค่าใช้จ่ายอื่น"):
        df.loc["ค่าใช้จ่ายอื่น",symbol] = float(trimstring2float(g_data[i+1]))
        df.loc["ค่าใช้จ่ายอื่น","commonsize"] = (float(trimstring2float(g_data[i+1]))/total)*100     
     elif(s=="ต้นทุนทางการเงิน"):
        df.loc["ต้นทุนทางการเงิน",symbol] = float(trimstring2float(g_data[i+1]))
        df.loc["ต้นทุนทางการเงิน","commonsize"] = (float(trimstring2float(g_data[i+1]))/total)*100
     elif(s=="ภาษีเงินได้"):
        df.loc["ภาษีเงินได้",symbol] = float(trimstring2float(g_data[i+1])) 
        df.loc["ภาษีเงินได้","commonsize"] = (float(trimstring2float(g_data[i+1]))/total)*100
     elif(s=="กำไร (ขาดทุน) สุทธิ"):
        df.loc["กำไร (ขาดทุน) สุทธิ",symbol] = float(trimstring2float(g_data[i+1]))
        df.loc["กำไร (ขาดทุน) สุทธิ","commonsize"] = (float(trimstring2float(g_data[i+1]))/total)*100

   
   #ป้องกันการรวมรายการมา
   passc1 = 0
   passc2 = 0
   for i in df.index:
    if(i=="ต้นทุนขายสินค้าและหรือต้นทุนการให้บริการ"):
      passc1=1
    if(i=="ต้นทุนขายสินค้า"):
      passc2=1 
    
   if(passc1==1 & passc2==1):
    df = df.drop(['ต้นทุนขายสินค้าและหรือต้นทุนการให้บริการ'])


   passc1 = 0
   passc2 = 0
   for i in df.index:
    if(i=="ต้นทุนขายสินค้าและหรือต้นทุนการให้บริการ"):
     passc1=1
    if(i=="ต้นทุนการให้บริการ"):
     passc2=1 
    
   if(passc1==1 & passc2==1):
    df = df.drop(['ต้นทุนขายสินค้าและหรือต้นทุนการให้บริการ'])
   
   return df
#####################################################################

def commonsizePlot(df):
    setTHforPlot()
    try:
      width= 1
      symbol = df.columns[0]
      plt.figure(figsize=(8,8))
      ax = plt.subplot(111)
      
      legend = ['รวมสินทรัพย์ไม่หมุนเวียน','รวมสินทรัพย์หมุนเวียน','รวมส่วนของผู้ถือหุ้น','รวมหนี้สินไม่หมุนเวียน','รวมหนี้สินหมุนเวียน']
      a1 = df["commonsize"]["รวมสินทรัพย์ไม่หมุนเวียน"]
      a2 = df["commonsize"]["รวมสินทรัพย์หมุนเวียน"]
      e1 = df["commonsize"]["รวมส่วนของผู้ถือหุ้น"]
      L1 = df["commonsize"]["รวมหนี้สินไม่หมุนเวียน"]
      L2 = df["commonsize"]["รวมหนี้สินหมุนเวียน"]
    
      plt.bar(0,a1, color='red', edgecolor='white', width=width)
      plt.bar(0,a2,bottom=a1,color='green', edgecolor='white', width=width)
      first_legend = plt.legend(['รวมสินทรัพย์ไม่หมุนเวียน','รวมสินทรัพย์หมุนเวียน'],loc=1,
                 prop={'size': 20},bbox_to_anchor=(1.6, 1))
      # Add the legend manually to the current Axes.
      plt.gca().add_artist(first_legend)
        
      
      plt.bar(1.1,e1, color='yellow', edgecolor='white', width=width)
      plt.bar(1.1,L1,bottom=e1,color='blue', edgecolor='white', width=width)
      plt.bar(1.1,L2,bottom=e1+L1,color='pink', edgecolor='white', width=width)  
      
      red_patch = mpatches.Patch(color='yellow', label='รวมส่วนของผู้ถือหุ้น')
      red_patch2 = mpatches.Patch(color='blue', label='รวมหนี้สินไม่หมุนเวียน')
      red_patch3 = mpatches.Patch(color='pink', label='รวมหนี้สินหมุนเวียน')
      plt.legend(handles=[red_patch,red_patch2,red_patch3],loc=4,
                 prop={'size': 20},bbox_to_anchor=(1.6, 0.5))
        
      ax.set_title("Common-size analysis of "+symbol,fontsize=30)
      plt.yticks(fontsize=20, rotation=0)
      plt.yticks(np.arange(0,101, 10))
      plt.xticks(fontsize=20, rotation=0)
      plt.xticks(np.arange(2), ('สินทรัพย์', 'หนี้สินและส่วนของผู้ถือหุ้น'))
    
    except:
      ########### ส่วนนี้ส่วนของ incomestatement  
      symbol = df.columns[0]
      width = 0.1
      colorlist = ['red','green','blue','brown','yellow','pink','cyan','purple']
      plt.figure(figsize=(8,8))
      sumzone = 0
      c = 0
      legend = []
      ax = plt.subplot(111)
      for i in reversed(df.index):
        pcg = (df["commonsize"][i]/df["commonsize"]['รวมรายได้'])*100
   
        if(i=="รวมรายได้"):
          continue
        #if(i=="ต้นทุนขายสินค้า"):
        #   plt.bar(0,100-pcg, bottom=sumzone,color=colorlist[c], edgecolor='white', width=width)
        #   continue     
  
        if(c==0):
          plt.bar(0,pcg, color=colorlist[c], edgecolor='white', width=width)
          sumzone+=pcg
          legend.append(i)
        else:
          plt.bar(0,pcg, bottom=sumzone,color=colorlist[c], edgecolor='white', width=width)
          sumzone+=pcg
          legend.append(i)

        c+=1

      ax.set_title("Common-size analysis of "+symbol,fontsize=30)
      plt.yticks(fontsize=20, rotation=0)
      plt.yticks(np.arange(0,101, 10))
      plt.xticks(fontsize=0, rotation=0)
      plt.legend(legend,loc=1,prop={'size': 20},bbox_to_anchor=(1.8, 1))
      
#####################################################################

################ utility ############################################
def trimstring2float(s):
    s = str(s.text.strip())
    s = s.rstrip()
    s = s.lstrip()
    s = s.replace(",","")
    return s

def setTHforPlot(fontsize=20.0):
   #set title ภาษาไทย
   #https://stackoverflow.com/questions/16574898/how-to-load-ttf-file-in-matplotlib-using-mpl-rcparams
   mpl.rcParams['font.size'] = fontsize
   path = 'DB_Helvethaica_X.ttf'
   prop = font_manager.FontProperties(fname=path)
   mpl.rcParams['font.family'] = prop.get_name()
    
 

############## spiderCompare #######################################
def spiderCompare(liststock,plot=True):
 if(len(liststock)!=2):
    print("Columns miss match.,spiderCompare Fn. Require 2 Columns Only.")
    return 0
 
 k = getFinanceRatio(liststock)
 if type(k) is int:#ตรวจสอบกรณีไม่พบข้อมูล เพราะจะ return 0 มาให้
        return 0

 if(plot==False):
   if(len(k)>0):
      return k

 checkLessThanZero = (k>0)
 passCheck = checkLessThanZero.eq(True).all().all()  
 if(passCheck==False):
    print("Can't run this Fn.,Because contain negative value.")
    return 0

 #ส่วนเริ่มต้นถ้าไม่มีค่าติดลบมา
 k_commonsize = k.sum(axis=1)   
 z = pd.DataFrame()
 z[k.columns[0]+"(%)"] = k[k.columns[0]]/k_commonsize 
 z[k.columns[1]+"(%)"] = k[k.columns[1]]/k_commonsize
    
 data = z
 symbol = liststock   
 #data = data.drop(data[data[symbol[0]+'.rate']=='-'].index)
 #data = data.drop(data[data[symbol[1]+'.rate']=='-'].index)
 categories=list(data.index)
 N = len(categories)   
 queryString = symbol
  
 # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
 angles = [n / float(N) * 2 * pi for n in range(N)]
 angles += angles[:1]
 
 # Initialise the spider plot
 ax = plt.subplot(111,polar=True)
 

 # If you want the first axis to be on top:
 ax.set_theta_offset(pi / 2)
 ax.set_theta_direction(-1)
 
 # Draw one axe per variable + add labels labels yet
 plt.xticks(angles[:-1], categories,fontsize=12)

    
 # Draw ylabels
 values1 = pd.to_numeric(data[data.columns[0]].values,errors='ignore').tolist() 
 values2 = pd.to_numeric(data[data.columns[0]].values,errors='ignore').tolist()    
 c = math.ceil(max(max(values1,values2)))
 c = int(math.ceil(c / 1.0)) * 1

 ax.set_rlabel_position(0)
 plt.yticks([0.1,0.2,0.3,0.4,0.4,0.5,0.6,0.7,0.8,0.9], color="grey", size=16)
 plt.ylim(0,c)


 # ------- PART 2: Add plots
 
 # Plot each individual = each line of the data
 # I don't do a loop, because plotting more than 3 groups makes the chart unreadable
 
 # Ind1
 #values=df.loc[0].drop('stock').values.flatten().tolist()
 values = pd.to_numeric(data[data.columns[0]].values,errors='ignore').tolist()   
 values += values[:1]
 ax.plot(angles, values, linewidth=1, linestyle='solid', label=queryString[0])
 ax.fill(angles, values, 'b', alpha=0.1)


 # Ind2
 #values=df.loc[1].drop('stock').values.flatten().tolist()
 values = pd.to_numeric(data[data.columns[1]].values,errors='ignore').tolist()   
 values += values[:1]
 ax.plot(angles, values, linewidth=1, linestyle='solid', label=queryString[1])
 ax.fill(angles, values, 'r', alpha=0.2)
 # Add legend
 plt.legend(loc='upper right', bbox_to_anchor=(1.0, 1.0),fontsize=12)
 plt.rcParams["figure.figsize"] = [7,7]   


'''
def spiderCompare(symbol):
 # ------- PART 1: Create background
 # number of variable
 #categories=list(df)[0:5]

 data = get_profit_ability(symbol)
 data = data.drop(data[data[symbol[0]+'.rate']=='-'].index)
 data = data.drop(data[data[symbol[1]+'.rate']=='-'].index)
 categories=list(data[symbol[0]+".profit_ability"])
 N = len(categories)   
 queryString = symbol
  
 # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
 angles = [n / float(N) * 2 * pi for n in range(N)]
 angles += angles[:1]
 
 # Initialise the spider plot
 ax = plt.subplot(111,polar=True)
 

 # If you want the first axis to be on top:
 ax.set_theta_offset(pi / 2)
 ax.set_theta_direction(-1)
 
 # Draw one axe per variable + add labels labels yet
 plt.xticks(angles[:-1], categories,fontsize=20)

    
 # Draw ylabels
 values1 = pd.to_numeric(data[queryString[0]+".rate"].values,errors='ignore').tolist() 
 values2 = pd.to_numeric(data[queryString[0]+".rate"].values,errors='ignore').tolist()    
 c = math.ceil(max(max(values1,values2)))
 c = int(math.ceil(c / 10.0)) * 10

 ax.set_rlabel_position(0)
 plt.yticks([10,20,30,40,50],range(10,c+10,10), color="grey", size=16)
 plt.ylim(0,c)


 # ------- PART 2: Add plots
 
 # Plot each individual = each line of the data
 # I don't do a loop, because plotting more than 3 groups makes the chart unreadable
 
 # Ind1
 #values=df.loc[0].drop('stock').values.flatten().tolist()
 values = pd.to_numeric(data[queryString[0]+".rate"].values,errors='ignore').tolist()   
 values += values[:1]
 ax.plot(angles, values, linewidth=1, linestyle='solid', label=queryString[0])
 ax.fill(angles, values, 'b', alpha=0.1)


 # Ind2
 #values=df.loc[1].drop('stock').values.flatten().tolist()
 values = pd.to_numeric(data[queryString[1]+".rate"].values,errors='ignore').tolist()   
 values += values[:1]
 ax.plot(angles, values, linewidth=1, linestyle='solid', label=queryString[1])
 ax.fill(angles, values, 'r', alpha=0.2)
 # Add legend
 plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.2),fontsize=20)
 plt.rcParams["figure.figsize"] = [12,9]
'''    
############## END spider_compare #######################################    
    
    

def getFinaceRationInDus(sample_in_sector,_year):
 ind = listStockInSector(sample_in_sector)
 year = _year
 symbol_list = []
 de = []
 roe = []
 for i in range(len(ind)):
    symbol = ind.iloc[i].values[0]
    try:
     symbol_list.append(symbol)
     ds = getFinanceRatio(ind.iloc[i].values[0])
     try:
      de.append(float(ds[ds["อัตราส่วนทางการเงิน"]=="อัตราส่วนหนี้สินต่อส่วนของผู้ถือหุ้น (เท่า)"][year]))
      roe.append(float(ds[ds["อัตราส่วนทางการเงิน"]=="อัตราผลตอบแทนผู้ถือหุ้น (%)"][year]))
      print(symbol, end=' ')
     except:
      de.append(np.NaN)
      roe.append(np.NaN)
    except:
     #print(symbol+" Data Invalid")
     de.append(np.NaN) 
     roe.append(np.NaN)   

 df = pd.DataFrame({'symbol':symbol_list,'de':de,'roe':roe})
 df = df.set_index('symbol')
 df = df.dropna()
 return df


def getFinanceRatio(liststock):

 if type(liststock) is list:
    ds = []
    for i in range(len(liststock)):
      k = getFinanceRatioProcess(liststock[i])
      if type(k) is int:#ตรวจสอบกรณีไม่พบข้อมูล เพราะจะ return 0 มาให้
        return 0
      ds.append(k)
    
    ##### เช็คประเภทธุรกิจ ######
    BusinessType = True
    for i in range(len(ds)):
      if(BusinessType==False):
        break
      for j in range(len(ds)):
       chk = np.array_equal(ds[i][ds[i].columns[0]],ds[j][ds[j].columns[0]])
       BusinessType = chk
       if(BusinessType==False):
         print("Can not compare Ratio")
         break
        
    if(BusinessType==False):
      return 0    
    #########################
    
    p = []
    s0 = ds[0][[ds[0].columns[0]]]
    p.append(s0)
    for i in range(len(ds)):
     s0 = ds[i][[ds[i].columns[1]]]
     s0.columns = [liststock[i]+"."+s0.columns[0]]
     p.append(s0)  

    z = pd.concat(p, axis=1) 
    
    z = z.set_index("Ratios")
    for i in range(len(z.columns)):
      z[z.columns[i]] = z[z.columns[i]].astype(float)
    return z

 elif type(liststock) is str:
    z = getFinanceRatioProcess(liststock)
    if type(z) is int:#ตรวจสอบกรณีไม่พบข้อมูล เพราะจะ return 0 มาให้
        return 0
    z = z.set_index("Ratios")
    for i in range(len(z.columns)):
      z[z.columns[i]] = z[z.columns[i]].astype(float)

    return z


def getFinanceRatioProcess(symbol): 
   headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
   r = requests.post("https://www.set.or.th/set/factsheet.do?symbol="+symbol+"&language=en&country=US",headers)
   r.content
   soup = BeautifulSoup(r.content, "lxml") 

   if len(soup.find_all("table", {"class" : "table-factsheet-padding0"}))==0:
    print("ไม่พบข้อมูล")
    return 0
    
   #มีการปรับใช้ภาษาอังกฤษแทน เพราะว่ากังวลเรื่อง font TH ที่ต้อง plugin เข้าไป Version 0.15496

   #### หา index #### content อยู่ช่องไหน
   ct = soup.find_all("table", {"class" : "table-factsheet-padding0"})
   i_index = 0
   for i in ct:
    if("Annualized: ROE, ROA" in i.text):
      m_index = i_index
      break
    i_index+=1
   ####################################

   g_data = soup.find_all("table", {"class" : "table-factsheet-padding0"})[i_index].find_all("td")
    
   if not "Annualized: ROE, ROA" in str(g_data):
      print("ไม่พบข้อมูล")
      return 0

   #delete "ปรับข้อมูลเต็มปี: อัตราผลตอบแทนผู้ถือหุ้น, อัตราผลตอบแทนจากสินทรัพย์"
   lenstep = int(g_data[0].get("colspan"))+1
   g_data.remove(g_data[0])


   ds  = []
   row = []
   cnt = 1
   
   for i in range(0,len(g_data)):
    s = str(g_data[i].text.strip())
    s = s.rstrip()
    s = s.lstrip()
    s = s.replace(',','')
    
 
    
    row.append(s)
    #print(g_data[i].text.strip())
    cnt+=1
    if(cnt==lenstep): 
      ds.append(row)
      row = []
      cnt = 1
    
   
   df = pd.DataFrame(ds)
   df.columns = df.iloc[0]
   df = df.drop([0])
   return df
 

# ==============================
class bs:
  assets = 0
  liabilities = 0
  equity = 0
  cash = 0
  def __init__(self, df):
        self.ds = df  
        self.cash = df[df["งบแสดงฐานะการเงิน(ลบ.)"]=="เงินสด"]
        self.assets = df[df["งบแสดงฐานะการเงิน(ลบ.)"]=="รวมสินทรัพย์"]
        self.liabilities = df[df["งบแสดงฐานะการเงิน(ลบ.)"]=="รวมหนี้สิน"]
        self.equity = df[df["งบแสดงฐานะการเงิน(ลบ.)"]=="ส่วนของผู้ถือหุ้นบริษัทใหญ่"]
  def report(self):
      return self.ds 

    
def getBalanceSheetCompare(liststock):
 ds = []
 if type(liststock) is list:
  for i in liststock:
    t = getBalanceSheet(i)#.report()
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
      print("Can not compare Balance Sheet")
      break

 if(BusinessType==False):
    return 0

 #p = []
 #s0 = ds[0][[ds[0].columns[0]]]
 #p.append(s0)
 #for i in range(len(ds)):
 # s0 = ds[i][[ds[i].columns[1]]]
 # s0.columns = [liststock[i]+"."+s0.columns[0]]
 # p.append(s0)  

 #z = pd.concat(p, axis=1)
 #return z
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

'''

def getBalanceSheetCompare(symbol,period="now"):
 ds = []
 if type(symbol) is list:
  for i in symbol:
    t = getBalanceSheet(i)#.report()
    t = trim_columnsname(t)
    ds.append(t)
    #ds[0]
 #check business
 if len(ds) == 2:
  #ตรวจ feild ในงบ      
  if period=="now":
    x = np.array(ds[0][ds[0].columns[0]])
    y = np.array(ds[1][ds[1].columns[0]])  
    p1 = np.array_equal(x,y)
    
    #ตรวจช่วงเวลาของงบ  
    x = np.array(ds[0].columns[1])
    y = np.array(ds[1].columns[1]) 
    p2 = np.array_equal(x,y)

    passcheckbusiness = False    
    if (p1==True) and (p2 == True):
      print("Check Business Type : True")
    else:
      print("Can not compare Balance Sheet") 
      return 0
    
    p1 = pd.DataFrame({"Label":ds[0][ds[0].columns[0]]})
    p2 = pd.DataFrame({ds[0].columns[1]+"."+symbol[0]:ds[0][ds[0].columns[1]]})
    p3 = pd.DataFrame({ds[1].columns[1]+"."+symbol[1]:ds[1][ds[1].columns[1]]})
    
    #p4 = pd.DataFrame({ds[2].columns[2]+"."+symbol[2]:ds[2][ds[2].columns[2]]})
    #result = pd.concat({"Label":ds[0][ds[0].columns[0]],
    #                ds[0].columns[1]+"."+symbol[0]:ds[0][ds[0].columns[1]],
    #                     ds[1].columns[1]+"."+symbol[1]:ds[1][ds[1].columns[1]]},axis=1)
    
    result = pd.concat([p1, p2, p3], axis=1)

    return result 

    #result['No.'] = np.array(range(1,len(result)+1))
    #result.index = result["No."]  
    #result = result.drop('No.', 1)
  
  else: #case not period=="now":
    x = np.array(ds[0][ds[0].columns[0]])
    y = np.array(ds[1][ds[1].columns[0]])  
    p1 = np.array_equal(x,y)
    
    #ตรวจช่วงเวลาของงบ  
    x = np.array(period)
    y = np.array(period) 
    p2 = np.array_equal(x,y)

    passcheckbusiness = False    
    if (p1==True) and (p2 == True):
      print("Check Business Type : True")
    else:
      print("Can not compare Balance Sheet") 
      return 0

    p1 = pd.DataFrame({"Label":ds[0][ds[0].columns[0]]})
    p2 = pd.DataFrame({period+"."+symbol[0]:ds[0][period]})
    p3 = pd.DataFrame({period+"."+symbol[1]:ds[1][period]})
    result = pd.concat([p1, p2, p3], axis=1)
    return result.style.set_properties(**{'text-align': 'left'})

    #result = pd.concat({"Label":ds[0][ds[0].columns[0]],
    #                     period+"."+symbol[0]:ds[0][period],
    #                     period+"."+symbol[1]:ds[1][period]},axis=1)
    
    #result['No.'] = np.array(range(1,len(result)+1)) 
    #result.index = result["No."] 
    #result = result.drop('No.', 1)   
    
    #return result
'''
# ==============================

def getBalanceSheet(symbol):  
 symbolMofi = symbol.replace("&","%26") 
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
 r = requests.post("https://www.set.or.th/set/factsheet.do?symbol="+symbolMofi,headers)
 r.content
 soup = BeautifulSoup(r.content, "lxml") 

 if len(soup.find_all("table", {"class" : "table-factsheet-padding0"}))==0:
    print("ไม่พบข้อมูล")
    return "ไม่พบข้อมูล"
 
 tmpdata = soup.find_all("table", {"class" : "table-factsheet-padding0"})  
 if("งบแสดงฐานะการเงิน (ลบ.)" in tmpdata[19].text):
    g_data = tmpdata[19].find_all("td")
    findStep = tmpdata[19].find_all("tr")      
 elif("งบแสดงฐานะการเงิน (ลบ.)" in tmpdata[20].text):
    g_data = tmpdata[20].find_all("td")
    findStep = tmpdata[20].find_all("tr")
 elif("งบแสดงฐานะการเงิน (ลบ.)" in tmpdata[18].text):
    g_data = tmpdata[18].find_all("td")
    findStep = tmpdata[18].find_all("tr")
 elif("งบแสดงฐานะการเงิน (ลบ.)" in tmpdata[17].text):
    g_data = tmpdata[17].find_all("td")
    findStep = tmpdata[17].find_all("tr")
 elif("งบแสดงฐานะการเงิน (ลบ.)" in tmpdata[16].text):
    g_data = tmpdata[16].find_all("td")
    findStep = tmpdata[16].find_all("tr")
 elif("งบแสดงฐานะการเงิน (ลบ.)" in tmpdata[15].text):
    g_data = tmpdata[15].find_all("td")
    findStep = tmpdata[15].find_all("tr")      

 ds  = []
 row = []
 cnt = 1
 
 #lenstep = 6    
 #if "M" in str(g_data[1]):
 #   lenstep = 7
 
 #ปรับโค้ดในการหาจำนวนคอลัมม์ที่แสดง เช่นกรณี vranda หุ้นใหม่จะมีคอลัมม์มาแค่ 3 คอลัมม์
 #0.15493
 lenstep = len(findStep[0].text.strip().split("\n"))+1    
 
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
    
 #ซ่อมสร้างคอลัมน์   
 
 #print(cc)   
    
 #df.columns = cc# df.iloc[0] 
 #df.index = df["งบแสดงฐานะการเงิน (ลบ.)"]
 #df.index = range(0,len(df))  
 df = df.drop(df.index[[0]])  
 #df.drop('งบแสดงฐานะการเงิน (ลบ.)', axis=1, inplace=True) 
 #df = df.style.set_properties(**{'text-align': 'left'}) 
   
 #df.columns = list(string.ascii_lowercase)[0:len(df.columns)]

 #obj = bs(trim_columnsname(df))  
 trim_columnsname(df)
 df = df.set_index("งบแสดงฐานะการเงิน(ลบ.)")
 return df#.style.set_properties(**{'text-align': textalign})


# ========= ev/ebitda =====================
def evperebitda(symbol):
  if type(symbol) is str:
    r = requests.post("https://quotes.wsj.com/TH/XBKK/"+symbol+"/financials")
    r.content
    soup = BeautifulSoup(r.content, "lxml")  
    g_data = soup.find_all("table", {"class" : "cr_dataTable cr_sub_valuation"})
 
    lb = g_data[0].find_all("span",{"class":"data_lbl"})
    data = g_data[0].find_all("span",{"class":"data_data"})  
    c = 0
    for i in lb:
      if(i.text.strip()=="Enterprise Value to EBITDA"):
        return float((data[c].text.strip()))
      c+=1
    return "n.a"

  if type(symbol) is list:
   df = pd.DataFrame(columns=["EV/EBITDA"])  
   for i in range(len(symbol)):
     symbol_ = symbol[i]
     r = requests.post("https://quotes.wsj.com/TH/XBKK/"+symbol_+"/financials")
     r.content
     soup = BeautifulSoup(r.content, "lxml")  
     g_data = soup.find_all("table", {"class" : "cr_dataTable cr_sub_valuation"})
 
     lb = g_data[0].find_all("span",{"class":"data_lbl"})
     data = g_data[0].find_all("span",{"class":"data_data"})  
     c = 0
     for i in lb:
      if(i.text.strip()=="Enterprise Value to EBITDA"):
        df.loc[symbol_,"EV/EBITDA"] = float((data[c].text.strip()))
        break
      c+=1
   return df



# ==============================
''' Error ไปแล้ว 28 may 2020 เหมือนว่า wsj เปลี่ยนระบบ 
def getProfitAbility(symbol):   
 if type(symbol) is str:   
  symbol = symbol.lower()  
  #https://www.wsj.com/market-data/quotes/TH/XBKK/ADVANC/financials  
  #r = requests.post("https://quotes.wsj.com/TH/XBKK/"+symbol+"/financials")
  url = "https://www.wsj.com/market-data/quotes/TH/XBKK/"+symbol+"/financials"
  
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   

  r = requests.post(url,headers)
  r.content
  
  soup = BeautifulSoup(r.content, "lxml")  
  g_data = soup.find_all("table",{"class" : "cr_dataTable cr_sub_profitability"})  
   
  print(soup)

  lb = g_data[0].find_all("span",{"class":"data_lbl"})
  data = g_data[0].find_all("span",{"class":"data_data"})   

  lb_ds = []
  data_ds = []

  for i in lb:
    lb_ds.append(i.text.strip())
  for i in data:
    data_ds.append(i.text.strip())
    
  df = pd.DataFrame(lb_ds)   
  df[1] = data_ds
  #df = df.T   
  df.columns = [symbol+".profit_ability",symbol+".rate"]
  return df

 if type(symbol) is list:
  datasource = pd.DataFrame()      
  for i in range(len(symbol)):
    tmp = symbol[i].lower()    
    r = requests.post("https://quotes.wsj.com/TH/XBKK/"+tmp+"/financials")
    r.content
    soup = BeautifulSoup(r.content, "lxml")  
    g_data = soup.find_all("table", {"class" : "cr_dataTable cr_sub_profitability"})
 
    lb = g_data[0].find_all("span",{"class":"data_lbl"})
    data = g_data[0].find_all("span",{"class":"data_data"})   

    lb_ds = []
    data_ds = []

    for m in lb:
      lb_ds.append(m.text.strip())
    for m in data:
      data_ds.append(m.text.strip())
    
    datasource[i*2] = lb_ds   
    datasource[(i*2)+1] = data_ds
  

  c = []
  for i in range(len(symbol)):
    print(symbol[i]+".profit_ability")
    c.append(symbol[i]+".profit_ability")
    c.append(symbol[i]+".rate")
  datasource.columns = c  
 return datasource
'''

# ==============================
def getohlc(symbol):
    data = loaddata.get(symbol, start='2015-01-01')
    return data



# ==============================
def getMemberOfIndex(indexType):
 '''
    arg1 (indexMarket): ตัวอย่างเช่น sx.indexMarket.SET50 ประกอบด้วย SET50,SET100,sSET,SETCLMV,SETHD,SETTHSI,SETWB 
           
    Returns (dataFrame) 
 '''
 #if(symbol.lower()=="sset"):
 #  symbol = "sSET"
 #else:
 #  symbol = symbol.upper()
 
 if(not isinstance(indexType, indexMarket)):
    print("Data Type indexMarket Not Match")
    return 0
    
 symbol = indexType.value

 if(symbol=="SET"):
   print("SET NOT Support ,หรืออาจใช้ sx.listSecurities เรียกใช้แทน")
   return 0

 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
                  
 r = requests.post("https://marketdata.set.or.th/mkt/sectorquotation.do?sector="+symbol+"&language=th&country=TH",verify=False,headers=headers)
 r.content
 soup = BeautifulSoup(r.content, "lxml")  
 dtmpCheck = soup.find_all("table", {"class" : "table-info"})


 ################# ปรับสำหรับ mai เพราะจะมีหลายกลุ่มอุตสาหกรรม #####################################
 if(symbol=="mai"):
  datasource = []
  for ttable in range(2,len(dtmpCheck)):
    g_data = dtmpCheck[ttable].find_all("td",{"style":"text-align: left;"})
    for i in g_data:
      datasource.append(i.text.strip()) 
 
  df = pd.DataFrame(datasource)
  df.columns = ["symbol"]
  return df
 ################# End Case mai  #########################


 if(len(dtmpCheck)==0):
   print("ไม่พบข้อมูล")
   return 0
 g_data = dtmpCheck[2].find_all("td",{"style":"text-align: left;"})
  
 datasource = []
 for i in g_data:
  datasource.append(i.text.strip())   
 
 df = pd.DataFrame(datasource)
 df.columns = ["symbol"]
 return df

class portfolio:
    updatedate = ""
    port = ""
    
def getLastPrice(symbol,date="now",ordersymbol=False):
 if type(symbol) is str: 
   r = requests.post("https://marketdata.set.or.th/mkt/stockquotation.do?symbol="+symbol+"&ssoPageId=1&language=th&country=TH")
   r.content
   soup = BeautifulSoup(r.content, "lxml")  
   g_data = soup.find_all("table", {"class" : "table table-hover table-set col-3-center table-set-border-yellow"})
   s = g_data[0].find_all("td")[5].text.strip()  
   s = s.replace(',', '')
   s = s.rstrip()
   s = s.lstrip() 
   return float(s)  
 elif type(symbol) is list:
   ds = []     
   for i in symbol:
     r = requests.post("https://marketdata.set.or.th/mkt/stockquotation.do?symbol="+i+"&ssoPageId=1&language=th&country=TH")
     r.content
     soup = BeautifulSoup(r.content, "lxml")  
     g_data = soup.find_all("table", {"class" : "table table-hover table-set col-3-center table-set-border-yellow"})
     s = g_data[0].find_all("td")[5].text.strip()  
     s = s.replace(',', '')
     s = s.rstrip()
     s = s.lstrip()
        
     ds.append(s)
    
   df = pd.DataFrame(ds)
   df = df.T  
   df.columns = symbol 
   if ordersymbol==True:
      obj = portfolio()  
      obj.port = df.sort_index().T
      obj.updatedate = g_data[0].find_all("td")[0].text.strip() 
      return obj
   return df.T


def trimdata(s):
  s = s.replace(',', '')
  s = s.replace('*', '')
  #s = s.replace('-', '0')
  s = s.rstrip()
  s = s.lstrip() 
  return s

def listStockInSector(sample_in_sector):
 sample_in_sector = sample_in_sector.replace("&","%26")  
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   
 r = requests.post("http://www.settrade.com/C04_08_stock_sectorcomparison_p1.jsp?txtSymbol="+sample_in_sector,headers=headers)
 #r.content
 soup = BeautifulSoup(r.content, "lxml")  
 g_data = soup.find_all("table", {"class" : "table table-info"})
 
 if(len(g_data)==0):
   print("ไม่พบข้อมูล")  
   return 0
 
 g_data = g_data[0].find_all("td",{"class" : "text-left"})
 
 listname_Sector = []
 for k in g_data:
   listname_Sector.append(k.text.strip())
 
 p = pd.DataFrame(listname_Sector)   
 p.columns = ["symbol"]   
 return p



######################################
def getdata(symbol,returntype="ar"):
 symboltmp = symbol.replace('&', '+%26+') 
 datasource = []   
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"} 
 #url = "http://www.settrade.com/C04_06_stock_financial_p1.jsp?txtSymbol="+symboltmp  

 #แก้ไขใน version 2021-10-เมษายน เพราะ url เดิมไม่ได้คืนค่ามาให้ version 0.155530
 url = 'https://www.settrade.com/sims/dat/finstmt/files/'+symboltmp+'_th_TH.html'

 #แก้ไขใน version 2021-10-เมษายน เปลี่ยนเป็น get version 0.155530
 r = requests.get(url,headers)
 #r.content
 
 soup = BeautifulSoup(r.content, "lxml")  

 try:
  g_data = soup.find_all("table", {"class" : "table table-hover table-info"})[0].find_all("tr")
 except:
  #case S&J
  return 0
 #################    

 col = []
 datasource.append(symbol)
  
 for k in g_data:
    td = k.find_all("td")
    for m in td:
       tmp = m.text.strip()
  
       if(tmp!=""):
        tmp = tmp.replace(',', '') 
        
        if(tmp=="สินทรัพย์รวม"):
           col.append(tmp)
           lenindex = len(td)
           tmp = k.find_all("td")[lenindex-1].text.strip()
           tmp = trimdata(tmp)
         
           if(tmp==""):
             tmp = k.find_all("td")[lenindex-2].text.strip()
             tmp = trimdata(tmp)
           
           if(tmp=="-"): #fix bug 0.15541 กรณี ข้อมูลส่งมาเป็น "-"
             tmp = np.nan

           if(tmp=="" or lenindex<=2): #เป็นพวกกองทุนรวม
             return 0
           datasource.append(float(tmp))   
           break

        if(tmp=="หนี้สินรวม"):
           col.append(tmp)
           lenindex = len(td)
           tmp = k.find_all("td")[lenindex-1].text.strip()
           tmp = trimdata(tmp)
           
           if(tmp==""):
             tmp = k.find_all("td")[lenindex-2].text.strip()
             tmp = trimdata(tmp)
           
           if(tmp=="-"): #fix bug 0.15541 กรณี ข้อมูลส่งมาเป็น "-"
             tmp = np.nan

           if(tmp=="" or lenindex<=2): #เป็นพวกกองทุนรวม
             return 0
           datasource.append(float(tmp))   
           break

        if(tmp=="ส่วนของผู้ถือหุ้น"):
           col.append(tmp)
           lenindex = len(td)
           tmp = k.find_all("td")[lenindex-1].text.strip()
           tmp = trimdata(tmp)
            
           if(tmp==""):
             tmp = k.find_all("td")[lenindex-2].text.strip()
             tmp = trimdata(tmp)
           
           if(tmp=="-"): #fix bug 0.15541 กรณี ข้อมูลส่งมาเป็น "-"
             tmp = np.nan

           if(tmp=="" or lenindex<=2): #เป็นพวกกองทุนรวม
             return 0
           datasource.append(float(tmp))   
           break
            
        if(tmp=="รายได้รวม"):
           col.append(tmp)
           lenindex = len(td)
           tmp = k.find_all("td")[lenindex-1].text.strip()
           tmp = trimdata(tmp)
            
           if(tmp==""):
             tmp = k.find_all("td")[lenindex-2].text.strip()
             tmp = trimdata(tmp)
           
           if(tmp=="-"): #fix bug 0.15541 กรณี ข้อมูลส่งมาเป็น "-"
             tmp = np.nan

           if(tmp==""): #เป็นพวกกองทุนรวม
             return 0
            
           datasource.append(float(tmp))   
           break

        if(tmp=="กำไรสุทธิ"):
           col.append(tmp)
           lenindex = len(td)
           tmp = k.find_all("td")[lenindex-1].text.strip()
           tmp = trimdata(tmp)
           
          
           if(tmp==""):
             tmp = k.find_all("td")[lenindex-2].text.strip()
             tmp = trimdata(tmp)

           if(tmp=="-"): #fix bug 0.15541 กรณี ข้อมูลส่งมาเป็น "-"
             tmp = np.nan
              
           if(tmp==""): #เป็นพวกกองทุนรวม
             return 0
           datasource.append(float(tmp))   
           break
            
        if(tmp=="ROE(%)"):
           col.append(tmp)
           lenindex = len(td)
           tmp = k.find_all("td")[lenindex-1].text.strip()
           tmp = trimdata(tmp)
            
           if(tmp==""):
             tmp = k.find_all("td")[lenindex-2].text.strip()
             tmp = trimdata(tmp)
                   
           if(tmp=='N/A' or tmp=='N.A.'):
              tmp = np.nan  
           if(tmp=="-"): #fix bug 0.15541 กรณี ข้อมูลส่งมาเป็น "-"
             tmp = np.nan

           if(tmp==""): #เป็นพวกกองทุนรวม
             return 0     
           datasource.append(float(tmp))   
           break
            
        if(tmp=="มูลค่าหลักทรัพย์ตามราคาตลาด"):
           col.append(tmp)
           lenindex = len(k.find_all("td"))
           tmp = k.find_all("td")[lenindex-1].text.strip()
           tmp = trimdata(tmp) 
            
           if(tmp==""):
             tmp = k.find_all("td")[lenindex-2].text.strip()
             tmp = trimdata(tmp)
          
           if(tmp=="-"): #fix bug 0.15541 กรณี ข้อมูลส่งมาเป็น "-"
             tmp = np.nan
           datasource.append(float(tmp))   
           break
            
        if(tmp=="P/E (เท่า)"):
           col.append(tmp)
           lenindex = len(k.find_all("td"))
           tmp = k.find_all("td")[lenindex-1].text.strip()
           tmp = trimdata(tmp) 
            
           if(tmp==""):
             tmp = k.find_all("td")[lenindex-2].text.strip()
             tmp = trimdata(tmp)
            
           if(tmp=='N/A' or tmp=='N.A.'):
              tmp = np.nan 
           if(tmp=="-"): #fix bug 0.15541 กรณี ข้อมูลส่งมาเป็น "-"
             tmp = np.nan

           datasource.append(float(tmp))   
           break
            
        if(tmp=="P/BV (เท่า)"):
           col.append(tmp)
           lenindex = len(k.find_all("td"))
           tmp = k.find_all("td")[lenindex-1].text.strip()
           tmp = trimdata(tmp) 
            
           if(tmp==""):
             tmp = k.find_all("td")[lenindex-2].text.strip()
             tmp = trimdata(tmp)
            
           if(tmp=='N/A'):
              tmp = 0  
           if(tmp=="-"): #fix bug 0.15541 กรณี ข้อมูลส่งมาเป็น "-"
             tmp = np.nan   
           datasource.append(float(tmp))   
           break    
        
        if(tmp=="อัตราส่วนเงินปันผลตอบแทน(%)"):
           col.append(tmp)
           lenindex = len(k.find_all("td"))
           tmp = k.find_all("td")[lenindex-1].text.strip()
           tmp = trimdata(tmp) 
            
           if(tmp==""):
             tmp = k.find_all("td")[lenindex-2].text.strip()
             tmp = trimdata(tmp)
            
           if(tmp=='N/A' or tmp=='N.A.'):
              tmp = np.nan  
           if(tmp=="-"): #fix bug 0.15541 กรณี ข้อมูลส่งมาเป็น "-"
             tmp = np.nan    
           datasource.append(float(tmp))   
           break
 
 
 if returntype=="df":
     datasource = pd.DataFrame(datasource).T
     datasource.columns = ["symbol","สินทรัพย์รวม","หนี้สินรวม","ส่วนของผู้ถือหุ้น","รายได้รวม","กำไรสุทธิ","ROE(%)","มูลค่าหลักทรัพย์ตามราคาตลาด","P/E (เท่า)","P/BV (เท่า)","อัตราส่วนเงินปันผลตอบแทน(%)"]  
            
 return datasource 


def ar2df(ar):
  datasource = pd.DataFrame(ar)  
  datasource.columns = ["symbol","สินทรัพย์รวม","หนี้สินรวม","ส่วนของผู้ถือหุ้น","รายได้รวม","กำไรสุทธิ","ROE(%)","มูลค่าหลักทรัพย์ตามราคาตลาด","P/E (เท่า)","P/BV (เท่า)","อัตราส่วนเงินปันผลตอบแทน(%)"]
  return datasource  

#แก้ใน version 0.1544
def getFundamentalInSector(sample_in_sector,progress=True):
 datasource = []
 p = listStockInSector(sample_in_sector=sample_in_sector) 
 #print(p)   
 for k in range(len(p)):
    r = p.loc[k].values
    s = getdata(str(r[0]))
    if(s!=0):
     if(progress==True): 
       print(r, end='')   
     datasource.append(s) 

 if(progress==True): 
   print("..Complete", end='')
 datasource = pd.DataFrame(datasource)
 datasource.columns = ["symbol","สินทรัพย์รวม","หนี้สินรวม","ส่วนของผู้ถือหุ้น","รายได้รวม","กำไรสุทธิ","ROE(%)","มูลค่าหลักทรัพย์ตามราคาตลาด","P/E (เท่า)","P/BV (เท่า)","อัตราส่วนเงินปันผลตอบแทน(%)"]   
 return datasource  




def trim_columnsname(df):
 cc = []
 for i in range(len(df.columns)):
   tmp = df.columns[i]
   tmp = tmp.replace("\xa0", "")
   tmp = tmp.replace(" ", "")  
   cc.append(tmp)
 df.columns = cc
 return df




#ใช้สำหรับซ่อมข้อมูลที่หายไป
def fillHistData(symbol,source):
 
  if(len(source.columns)<4):
     s1 = symbol.lower()
     s2 = source.columns[0].lower()
     if(s1!=s2):
        print("DataSource Not Match")
        return 0
    
  #ใช้สำหรับซ่อมข้อมูลที่หายไป
  url = "https://www.set.or.th/set/historicaltrading.do?symbol="+symbol

  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
  r = requests.post(url,headers)
  soup = BeautifulSoup(r.content, "lxml") 

  ####
  ct = soup.find_all("tbody")  

  rowData =[]
  for i in ct:
    row = i.find_all("tr")
    for tr in row:
     colData = []
     j = tr.find_all("td")
     dt = j[0].text
    
     dt = dt.split("/")
     dt[1] = dt[1]
     dt[2] = int(dt[2])-543 #year
     k = str(dt[2])+'-'+str(dt[1])+'-'+str(dt[0])
     date = dtt.strptime(k,'%Y-%m-%d')
     #need YYYY-MM-DD
     open = j[1].text
     high = j[2].text
     low = j[3].text
     close = j[4].text
     volume_ = j[7].text.replace(",","")
        
     colData.append(date)
    
     #if(OHLC==True):
     if(len(source.columns)==4):   
      colData.append(np.float(open))
      colData.append(np.float(high))
      colData.append(np.float(low))
      colData.append(np.float(close)) 
    
     elif(len(source.columns)==5):
      colData.append(np.float(open))
      colData.append(np.float(high))
      colData.append(np.float(low))
      colData.append(np.float(close))       
      colData.append(np.float(volume_))
    
     #if(Volume==True):
     elif(len(source.columns)==2): 
      colData.append(np.float(close))  
      colData.append(np.float(volume_))
     
     #if(Volume==True):
     elif(len(source.columns)==1): 
      colData.append(np.float(close))
    
     rowData.append(colData)
        
  ########
  datareplace = pd.DataFrame(rowData)
  #print(datareplace)
  #if(Volume==True and OHLC==True):
  if(len(source.columns)==5):  
    datareplace.columns = ["Date","Open","High","Low","Close","Volume"]  
  #if(Volume==True and OHLC==False):
  elif(len(source.columns)==2): 
    tmpsymbol = source.columns[0]
    datareplace.columns = ["Date",tmpsymbol,"Volume"]
  #elif(Volume==False and OHLC==True):
  elif(len(source.columns)==4):  
    datareplace.columns = ["Date","Open","High","Low","Close"]
  #elif(Volume==False and OHLC==False):
  elif(len(source.columns)==1):  
     tmpsymbol = source.columns[0]
     datareplace.columns = ["Date",tmpsymbol]  

 
  source = source.reset_index()
  fdf = pd.concat([source,datareplace]).drop_duplicates(['Date'],keep='last').sort_values("Date",ascending=True)
  fdf = fdf.set_index("Date")  
  return fdf #final DataFrame  