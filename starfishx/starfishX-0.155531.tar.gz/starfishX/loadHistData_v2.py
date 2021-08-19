import requests
import pandas as pd
from datetime import datetime as dt
import numpy as np
import os

import mplfinance as fplt

from enum import Enum 
class timeFrame(Enum):
    day = '1d'
    week = '1wk'
    month = '1mo'

def loadHistData_v2(symbol,start,end,timeframe=timeFrame.day,typedata='history'):
  '''
  symbol :(str) 
  start :(str) วันที่เริ่มต้น YYYY-MM-DD คศ. เช่น 2020-01-01
  end :(str) วันที่สุดท้าย YYYY-MM-DD คศ. เช่น 2020-01-01
  typedata :(str) ตอนนี้มี 2 type 1.'history' และ 2. 'div'
  timeframe : class TimeFrame มี Day/Week และ Month
  
  ตัวอย่าง
  1.df = loadHistData(symbol='spali',start='2000-01-01',end='2021-01-09',timeframe=sx.timeFrame.week)
  2.df = loadHistData(symbol='spali',start='2000-01-01',end='2021-01-09',typedata='div')
  ''' 

  k = dt.strptime(start, '%Y-%m-%d')
  start = str(int(dt.timestamp(k)))
  k = dt.strptime(end, '%Y-%m-%d')
  end = str(int(dt.timestamp(k)))
 
  symbol_ = symbol + '.BK'
  filename = symbol+ '.csv'
    
  if(typedata=='history'): 
    if(timeframe==timeFrame.day):
       timeframe_ = '1d' 
    elif(timeframe==timeFrame.week):
       timeframe_ = '1wk' 
    elif(timeframe==timeFrame.month):    
       timeframe_ = '1mo' 
    
    url = 'https://query1.finance.yahoo.com/v7/finance/download/' + \
       symbol_+'?period1='+start+'&period2='+end+'&interval='+timeframe_+'&events=history'\
       '&includeAdjustedClose=true' 
    
  elif(typedata=='div'):
    url = 'https://query1.finance.yahoo.com/v7/finance/download/'+ \
       symbol_+'?period1='+start+'&period2='+end+'&interval=1d&events=div&includeAdjustedClose=true'
    
  #####
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}   

  filename = symbol+'.BK'   
  try:
   r = requests.get(url,headers=headers)
   if('404 Not Found' in r.text):
     print(r.text)   
     return 0

   with open(filename, "wb") as code:
    code.write(r.content) 
  except:
    print('can\'t load data')
    return 0

  df = pd.read_csv(filename) 
  df = df.set_index('Date')
  df.index = pd.to_datetime(df.index)  
  os.remove(filename)
  return df.sort_index()


def plotCandle(self,filename=''):
  if(filename!=''):
    saving_params = dict(fname=filename,  bbox_inches='tight',pad_inches = 0.1)
    fplt.plot(
            self[['Open','High','Low','Close','Volume']],
            type='candle',
            style='charles',
            volume=True,
            figratio=(2,1),
            #title='',
            #ylabel='',
            axisoff=True,
            show_nontrading=False,
            savefig=saving_params
        )
  else:
    fplt.plot(
            self[['Open','High','Low','Close','Volume']],
            type='candle',
            style='charles',
            volume=True,
            figratio=(2,1),
            #title='',
            #ylabel='',
            axisoff=False,
            show_nontrading=False,
            #savefig=saving_params
        )
    
setattr(pd.core.frame.DataFrame, 'plotCandle', plotCandle)