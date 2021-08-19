import pandas as pd
import numpy as np
 
from enum import Enum
class TypeVol(Enum):
 hvCloseToClose = "Close To Close" 
 hvParkinson  = "Parkinson"
 hvGarman_Klass = "Garman-Klass"
 hvRogers_Satchell = "Rogers-Satchell"
 hvGarman_Klass_Yang_Zhang_Extension = "GARMAN-KLASS YANG-ZHANG EXTENSION"
 hvYang_Zhang = "Yang-Zhang"


def historicalVolatility(dataframe,N,hisVolArg): 
  '''
  dataframe : pandas dataframe 
              : จำเป็นต้องมี column "OPEN,"HIGH","LOW" และ "CLOSE" ติดมา
  N : int จำนวนวันที่ใช้เป็นแบบ SMA
  '''
  if(not isinstance(hisVolArg, TypeVol)):
    print("Data Type Historical Volatility Not Match")
    return 0
  
  if(hisVolArg.value==TypeVol.hvCloseToClose.value):
     return hvcc(dataframe,N)

  elif(hisVolArg.value==TypeVol.hvParkinson.value):
     return hvp(dataframe,N)

  elif(hisVolArg.value==TypeVol.hvGarman_Klass.value):
     return hvgk(dataframe,N)

  elif(hisVolArg.value==TypeVol.hvRogers_Satchell.value):
     return hvrs(dataframe,N)

  elif(hisVolArg.value==TypeVol.hvGarman_Klass_Yang_Zhang_Extension.value):
     return hvgkyze(dataframe,N)

  elif(hisVolArg.value==TypeVol.hvYang_Zhang.value):   
     return hvyz(dataframe,N)     
     
 

def hvcc(dataframe,N):
  '''
  historical volatility close to close
  dataframe : pandas dataframe
            : จำเป็นต้องมี column "CLOSE" ติดมา
  N : int จำนวนวันที่ใช้เป็นแบบ SMA
  '''
  hvcc = np.sqrt(252) * pd.DataFrame.rolling(np.log(dataframe.CLOSE/dataframe.CLOSE.shift(1)),window=N).std()
  return hvcc

def hvp(dataframe,N):
    '''
    Parkinson's Historical Volatility : high to low
    dataframe : pandas dataframe 
              : จำเป็นต้องมี column "HIGH" และ "LOW" ติดมา
    N : int จำนวนวันที่ใช้เป็นแบบ SMA
    '''
    hvp = np.sqrt(252 / (4* N *np.log(2)) * pd.DataFrame.rolling(np.log(dataframe.HIGH / dataframe.LOW)**2 , window=N).sum())
    return hvp

def hvgk(dataframe,N):
  '''
    Garman-Klass : OHLC
    dataframe : pandas dataframe 
              : จำเป็นต้องมี column "OPEN,"HIGH","LOW" และ "CLOSE" ติดมา
    N : int จำนวนวันที่ใช้เป็นแบบ SMA
  '''
  term1 = (np.log(dataframe.HIGH/dataframe.LOW)**2)
  term2 = ((2*np.log(2))-1)
  term3 = (np.log(dataframe.CLOSE/dataframe.OPEN)**2)
  term4 = (1/2)*term1-(term2*term3)
  term5 = term4.rolling(N+1).sum()/(N+1)
  term6 = np.sqrt(term5*252)  
  hvgk = term6
  return hvgk  


def hvrs(dataframe,N):
  '''
  Rogers-Satchell (OHLC)
  dataframe : pandas dataframe 
              : จำเป็นต้องมี column "OPEN,"HIGH","LOW" และ "CLOSE" ติดมา
  N : int จำนวนวันที่ใช้เป็นแบบ SMA
  '''
  #ตรวจก่อนว่ามี drift ไหม?   drift เป็นศูนย์หรือเปล่า
  r = dataframe.CLOSE.pct_change().cumsum().tail(1)[0]
  if(r>-0.01 and r<0.01):
      print("pct_change : ",r)  
      return 0 
    
  #implement ตามสูตรข้างบน
  term1 = np.log(dataframe.HIGH/dataframe.CLOSE)  
  term2 = np.log(dataframe.HIGH/dataframe.OPEN)  
  term3 = np.log(dataframe.LOW/dataframe.CLOSE) 
  term4 = np.log(dataframe.LOW/dataframe.OPEN)
  term5 = (term1*term2)+(term3*term4)
  term6 = term5.rolling(N+1).sum()
  term7 = np.sqrt(term6)*np.sqrt(252/(N+1))
  #VOLATILITY ROGERS-SATCHELL
  hvrs = term7
  return hvrs


def hvgkyze(dataframe,N):
  '''
  GARMAN-KLASS YANG-ZHANG EXTENSION 
  dataframe : pandas dataframe 
              : จำเป็นต้องมี column "OPEN,"HIGH","LOW" และ "CLOSE" ติดมา
  N : int จำนวนวันที่ใช้เป็นแบบ SMA
  '''
  term1 = (np.log(dataframe.OPEN/dataframe.CLOSE.shift(1))**2)
  term2 = (1/2)*(np.log(dataframe.HIGH/dataframe.LOW)**2)
  term3 = (2*np.log(2)-1)*(np.log(dataframe.CLOSE/dataframe.OPEN)**2)
    
  term4 = (term1+term2-term3)
  term5 = term4.rolling(N+1).sum()
  term6 = np.sqrt(term5)*np.sqrt(252/(N+1)) 
  hvgkyze = term6
  return hvgkyze


def hvyz(dataframe,N):
    #VOLATILITY ROGERS-SATCHELL (***รายวัน Daily***)
    term1 = np.log(dataframe.HIGH/dataframe.CLOSE)  
    term2 = np.log(dataframe.HIGH/dataframe.OPEN)  
    term3 = np.log(dataframe.LOW/dataframe.CLOSE) 
    term4 = np.log(dataframe.LOW/dataframe.OPEN)
    term5 = (term1*term2)+(term3*term4)
    term6 = term5.rolling(N+1).sum()
    term7 = np.sqrt(term6)*np.sqrt(1/(N+1))
    rs = term7
    
    #overnight_volatility
    overnight_volatility_pow2 = (np.log(dataframe.OPEN / dataframe.CLOSE.shift(1)).rolling(N).var())
    yz1 = overnight_volatility_pow2
    #open_to_close_volatility
    open_to_close_volatility_pow2 = (np.log(dataframe.CLOSE / dataframe.OPEN).rolling(N).var())
    yz2 = open_to_close_volatility_pow2
    #k
    k = 0.34 / ( 1.34 + ( N + 1 ) / ( N - 1 ) )
    hvyz = np.sqrt((yz1)+(k*(yz2))+((1-k)*(rs**2)))  * np.sqrt(252)
    
    return hvyz