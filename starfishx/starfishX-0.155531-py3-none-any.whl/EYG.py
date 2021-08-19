### EYG.py
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

 
 
import numpy as np

import matplotlib.dates as mdates

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import matplotlib.pyplot as plt
import pandas as pd

exec("from "+prefix+"marketview import marketview")
exec("from "+prefix+"Ke import thaibma")

def twoTenSpread(start="2000-01-01",bondtype="",viewplot=True,padding=False):
 
 ####### เตรียมข้อมูล #########
 date = datetime(2000,1,1)#startdate
 bt = bondtype
 stop = datetime.now()

 k2ds = []
 k10ds = []
 dateIndex = []
 for i in range(1000): #เดาว่าไม่เกิน 1000 เดือน
  dt_str = date.strftime('%Y-%m-%d')
 
  k2_10 = thaibma(date=dt_str,bondtype=bt,viewlog=False)

  if(k2_10==0): #พยายามเลื่อนวันถัดไป ถ้าดึงข้อมูลไม่ได้
    for dNext in range(10): 
      dt_str = (date + pd.DateOffset(dNext)).strftime('%Y-%m-%d')
      k2_10 = thaibma(date=dt_str,bondtype=bt,viewlog=False)    
      if(k2_10!=0):
        break
 
  dateIndex.append(dt_str)
  k2ds.append(k2_10["USTreasury2Year"])
  k10ds.append(k2_10["USTreasury10Year"]) 
       
  if((stop.month-1==date.month) & (stop.year==date.year)):
   break

  date = date + relativedelta(months=+1)
    
    
 ############## 
 #https://stackoverflow.com/questions/45704366/modify-date-ticks-for-pandas-plot
 # convert date objects from pandas format to python datetime
 index = pd.date_range(start = "2000-01-01", end = "2019-06-01", freq = "MS")
 dateIndex = [pd.to_datetime(date, format='%Y-%m-%d').date() for date in index]
 df = pd.DataFrame({"USTreasury2Year":k2ds,"USTreasury10Year":k10ds},index=dateIndex)    
 df["2-10Spread"] = df["USTreasury10Year"] - df["USTreasury2Year"]

 ####### จบส่วนเตรียมข้อมูล #######   
    
 fig = plt.figure(figsize=(20,10))
 fig.subplots_adjust(hspace=0.4, wspace=0.1)
 ax = fig.add_subplot(1, 1, 1)
 ax.plot(df["2-10Spread"])  

 ax.title.set_text("2-10 Spread : (USTreasury10Year - USTreasury2Year)")
 ax.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
 ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
 # set formatter
 ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
 #ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m'))
 plt.grid()
 plt.gcf().autofmt_xdate()
 plt.margins(0.01,0.05)    
    
 return df


def utilityTwinXPlot(Left,Right,LeftYLim,RightYLim,title):
 fig, ax1 = plt.subplots(figsize=(20,10))
 ax1.title.set_text(title)

 ax1.plot(Left.index,Left,color='red',label=Left.columns[0]+"(LHS)")
 ax1.set_ylim(LeftYLim)

 ax1.legend(loc='upper right', bbox_to_anchor=(1,1))

 ax1.grid()
 ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
 ax1.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
 # set formatter
 ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
 #ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m'))

 plt.gcf().autofmt_xdate()
 plt.margins(0.01,0.05)


 ax2 = ax1.twinx()
 ax2.plot(Left.index,Right,color="blue",label=Right.columns[0]+"(RHS)")
 ax2.set_ylim(RightYLim)
 ax2.legend(loc='upper right')

 ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=12))
 ax2.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
 # set formatter
 ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
 #ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m'))
 ax2.legend(loc='upper right', bbox_to_anchor=(1,0.9))
 plt.grid()
 plt.gcf().autofmt_xdate()
 plt.margins(0.01,0.05)

 fig.tight_layout()  # otherwise the right y-label is slightly clipped
 plt.show()   


def EarningYieldGap(marketType,BondType,start,viewlog=True,viewplot=True):
 '''
 ตัวอย่างการใช้พารามิเตอร์
 #marketType = sx.indexMarket.SET50
 #BondType = sx.BondType.USTreasury10Year
 '''

 marketDictKey = marketType.value
 df = marketview(marketType,viewplot=False,start=start)
 ep = "E/P "+marketDictKey
 df[ep] = 1/df["pe"]
 bondYield = []
 for i in df.index:
  dt = i.strftime('%Y-%m-%d') #จัดรูปแบบ Date ใหม่  คือตัดช่วงของเวลาออก 00:00:00
  by = thaibma(dt,bondtype=BondType,viewlog=False)
  if(by==0): #พยายามเลื่อนวันถัดไป ถ้าดึงข้อมูลไม่ได้
    for k in range(10): 
      dt = (i + pd.DateOffset(k)).strftime('%Y-%m-%d')
      by = thaibma(dt,bondtype=BondType,viewlog=False)    
      if(by!=0):
        break
  
  if(viewlog==True):
    print(".",end="")   
  bondYield.append(by)

 if(viewlog==True):
   print("complete")

 typeBondKey = "BondYield "+BondType.value
 df[typeBondKey] = bondYield
 ######## end process data #######
 
 ###### part plot ########   
 if(viewplot==True):
  fig = plt.figure(figsize=(20, 20))
  grid = plt.GridSpec(4, 1, wspace=0.4, hspace=0.3)
  ax = plt.subplot(grid[0, 0])
  df["index"].plot(ax=ax,title=marketDictKey+" Index")

  ax = plt.subplot(grid[1, 0])
  df["pe"].plot(ax=ax,title=df.columns[1].upper()+" "+marketDictKey+ " Index")

  ax = plt.subplot(grid[2:, 0])
  df[[ep,typeBondKey]].plot(ax=ax,
                kind="line",style='--',title="Earning Yield Gap ("+marketDictKey+" & "+typeBondKey+")")

 
 ######### end part plot #######
 return df               