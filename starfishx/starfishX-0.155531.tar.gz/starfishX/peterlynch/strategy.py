#scan Peter Lynch

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

import starfishX as sx


import re
import ssl
from urllib import request, parse

import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import datetime

from IPython.display import HTML

#สำหรับหาความแข็งแกร่งของแนวโน้ม
from scipy import stats


pd.options.display.float_format = '{:,.2f}'.format
#pd.set_option('precision', 2)


def getPE(symbol):
 '''
 หา PE ของหุ้น ,อุตสาหกรรม และตลาด
 parameter : รายชื่อหุ้น symbol

 return  
 - PE บริษัท
 - PE อุตสาหกรรม
 - PE ของตลาด (SET)
 '''  
 symbol = symbol.replace("&","%26") 
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 url = "https://www.set.or.th/set/factsheet.do?symbol="+symbol+"&ssoPageId=3&language=th&country=TH"
 r = requests.post(url,headers=headers, timeout=5)
 soup = BeautifulSoup(r.content, "lxml")  

 ct = soup.find_all("table",{"class":"table-factsheet-padding0"})  

 if(len(ct)==0):
    return 0

 #### หา index #### content อยู่ช่องไหน
 i_index = 0
 for i in ct:
  if("เปรียบเทียบหมวดอุตสาหกรรม" in i.text):
      m_index = i_index
      break
  i_index+=1

 #######
 tr = ct[m_index].find_all("tr")
 for i in tr:
  td = i.find_all("td")
  if("P/E" in td[0].text):
      try:
       PE_self  = float(td[1].text)
       PE_indus = float(td[2].text)
       PE_SET   = float(td[3].text)  
       pe_df = pd.DataFrame({"PE":PE_self,"PE_INDS":PE_indus,"PE_SET":PE_SET},index=[symbol.upper()])  
       return pe_df
      except: 
       return 0  


def getEPSGrowth(symbol,backwardYear=5):
    '''
    หาอัตราการเติบโตของ EPS ย้อนหลังกี่ปี ถ้าไม่ระบุจะใช้ 5 ปี
    symbol หุ้น
    backward_year : จำนวนปีย้อนหลังนับจากปีปัจจุบัน
    
    return g และ log
    '''
    eps_g = sx.morningstarGetfn(symbol,sx.MStar.EarningsPerShare)
    
    eps_now = eps_g.iloc[-1].values[0]
    eps_backward = eps_g.iloc[-backwardYear].values[0]

    k = eps_now/eps_backward 
    if(k>=0):
      g = (k**(1/backwardYear))-1
      return g,eps_g
    else:
      return np.NaN,eps_g 

def getListedShare(symbol,andPrice=False):
 '''
 หา จำนวนหุ้นของบริษัทจดทะเบียน(ล้านหุ้น)
 symbol : str สัญลักษณ์ชื่อของหุ้น
 andPrice : boolean ถ้าเป็น True จะคืนค่าราคาแถมมาด้วย
 return  
 - float (ล้านหุ้น) , ราคาหุ้นล่าสุด
 '''  
 symbol = symbol.replace("&","%26") 
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 url = "https://www.set.or.th/set/factsheet.do?symbol="+symbol+"&ssoPageId=3&language=th&country=TH"
 r = requests.post(url,headers=headers, timeout=5)
 soup = BeautifulSoup(r.content, "lxml")  

 ct = soup.find_all("table",{"class":"table-factsheet-padding0"})  

 if(len(ct)==0):
    return 0

 #### หา index #### content อยู่ช่องไหน
 i_index = 0
 for i in ct:
  if("จำนวนหุ้นจดทะเบียน (ล้านหุ้น)" in i.text):
      m_index = i_index
      break
  i_index+=1

 #######

 tr = ct[m_index].find_all("tr")
 for i in tr:
  td = i.find_all("td") 
  if("จำนวนหุ้นจดทะเบียน" in td[0].text):
      listedShare  = td[1].text
      try:
       listedShare = float(listedShare.replace(",",""))
      except:
       return 0
   
  if("ราคา (บาท/หุ้น)" in td[0].text):
      priceNow  = td[1].text
      try:
       priceNow = float(priceNow.replace(",",""))
      except:
       return 0
       
      if(andPrice==True):
         #ls_df = pd.DataFrame({"listedShare":listedShare,"price":priceNow},index=[symbol]) 
         return priceNow
      else:
         #ls_df = pd.DataFrame({"listedShare":listedShare},index=[symbol])
         return listedShare
      #return ls_df  

def getInterestBearingDebt(symbol, keywordlist=['เงินกู้', 'ตราสารหนี้', 'หุ้นกู้', 'เงินเบิกเกินบัญชี','หนี้สินระยะยาว - สุทธิจากส่วนที่ถึงกำหนดชำระภายในหนึ่งปี','ส่วนของหนี้สินระยะยาวที่ถึงกำหนดชำระภายในหนึ่งปี'], viewlog=False):
  TL,IBD,Log = sx.InterestBearingDebt(symbol, keywordlist, viewlog)
  return TL,IBD,Log

def getCash(symbol):
   bs = getBalanceSheet(symbol)
   cash = bs[bs.columns[0]][bs.index=="เงินสด"]
   cash = float(cash.values[0].replace(",",""))
   return cash

def getEquity(symbol):
   bs = getBalanceSheet(symbol)
   eq = bs[bs.columns[0]][bs.index=="ส่วนของผู้ถือหุ้นบริษัทใหญ่"]
   eq = float(eq.values[0].replace(",",""))
   return eq

def getBalanceSheet(symbol):
   bs = sx.getBalanceSheet(symbol)
   return bs

def getPrice(symbol):
   price = getListedShare(symbol,andPrice=True)
   #price = price_df["price"].values[0]
   return price

def reportHelper(*condition,symbol,backwardYear=5):
  rp = pd.DataFrame()  
  for i in condition:
    if(i.value=="epsGrowth"):
        g,log = (getEPSGrowth(symbol,backwardYear))
        rp["Eps Growth"] = [g]
    
    
    if(i.value=="PE/G"):
        pe_df  = (getPE(symbol))
        pe_self  = pe_df["PE"].values[0]  
        pe_indus = pe_df["PE_INDS"].values[0] 
        pe_set = pe_df["PE_SET"].values[0]  
        rp["P/E"] = [pe_self]
        rp["P/E Indus"] = [pe_indus]
        rp["P/E SET"] = [pe_set]

        try:
           peg = pe_self/g
           rp["PE/G"] = [peg]
        except:
           g,log = (getEPSGrowth(symbol,backwardYear))
           peg = pe_self/(g*100)
           rp["Eps Growth("+str(backwardYear)+"Years)"] = [g]
           rp["PE/G"] = [peg]

    if(i.value=="PE"):
        pe_df  = (getPE(symbol))
        pe_self  = pe_df["PE"].values[0]  
        pe_indus = pe_df["PE_INDS"].values[0] 
        pe_set = pe_df["PE_SET"].values[0]  
        rp["P/E"] = [pe_self]
        rp["P/E Indus"] = [pe_indus]
        rp["P/E SET"] = [pe_set]

    if(i.value=="cash"):
        bs = getBalanceSheet(symbol)
        cash = bs[bs.columns[0]][bs.index=="เงินสด"]
        cash = float(cash.values[0].replace(",",""))
        rp["Cash"] = [cash]
        
    if(i.value=="listedShare"):
        share = getListedShare(symbol,andPrice=False)
        #share = share_df["listedShare"].values[0]
        rp["ListedShare"] = [share] 
        
    if(i.value=="price"):
        price = getPrice(symbol)
        rp["Price"] = [price]    
        
    if(i.value=="interestBearingDebt"):
        TL,IBD,Log = getInterestBearingDebt(symbol,viewlog=False)
        rp["Total Liabilities"] = [TL]
        rp["Interest Bearing Debt"] = [IBD]

    if(i.value=="equity"):
        equity = getEquity(symbol)
        rp["Equity"] = [equity]    
    
    if(i.value=="de"):
        try:
           DE = IBD/equity
           rp["DE"] = [DE]
        except:
           TL,IBD,Log = getInterestBearingDebt(symbol,viewlog=False)
           rp["Total Liabilities"] = [TL]
           rp["Interest Bearing Debt"] = [IBD]

           equity = getEquity(symbol)
           rp["Equity"] = [equity] 
           DE = IBD/equity
           rp["D/E"] = [DE]   

    if(i.value=="stockRepurchases"):
        stockRepurchases = getStockRepurchasesCheck(symbol)
        rp["Stock Repurchases"] = [stockRepurchases] 

    if(i.value=="cashPerShare"):
        try:
           cashPerShare = (cash - IBD)/ share
           rp["Cash/Share"] = [cashPerShare]
        except:   
           bs = getBalanceSheet(symbol)
           cash = bs[bs.columns[0]][bs.index=="เงินสด"]
           cash = float(cash.values[0].replace(",",""))
           rp["Cash"] = [cash]  

           TL,IBD,Log = getInterestBearingDebt(symbol,viewlog=False)
           rp["Total Liabilities"] = [TL]
           rp["Interest Bearing Debt"] = [IBD]

           share = getListedShare(symbol,andPrice=False)
           #share = share_df["listedShare"].values[0]
           rp["ListedShare"] = [share]

           cashPerShare = (cash - IBD)/ share
           rp["Cash/Share"] = [cashPerShare]
    
  ###end for
  rp = rp.T
  rp.columns = [symbol.upper()] 
  return rp.round(2)



def getStockRepurchasesCheck(symbol,action="history"): 
 '''
 action : str จะมีสองค่าคือ "history" และ "today"
   - ถ้า today จะตรวจสอบวันล่าสุด
   - ถ้า history จะตรวจสอบประมาณ 2-3 เดือนย้อนหลัง
 '''  
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 symbolMofi = symbol.replace("&","%26")  
 r = requests.get("https://www.set.or.th/set/companynews.do?symbol="+symbolMofi+"&ssoPageId=8&language=th&country=TH",headers=headers, timeout=5)
 soup = BeautifulSoup(r.content, "lxml")  
 ct = soup.find_all("table",{"class":"table table-hover table-info-wrap"})  
 p = 0
 
 if(action=="today"):
  if("ซื้อหุ้นคืน" in ct[0].text):
    p = 1
 else:
   for i in ct: 
    if("ซื้อหุ้นคืน" in i.text):
      p = 1
    
 if(p==1):
    return True
 else:
    return False


def getDividends(symbol):
  return sx.morningstarGetfn(symbol,sx.MStar.Dividends)

def getPayoutRatio(symbol):
  return sx.morningstarGetfn(symbol,sx.MStar.PayoutRatio)


