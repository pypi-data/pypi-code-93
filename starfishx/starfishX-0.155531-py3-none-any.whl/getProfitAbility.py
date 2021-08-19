import re
import pandas as pd
import ssl
from urllib import request, parse
from bs4 import BeautifulSoup

import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import datetime

def getProfitAbility(symbol): 
 symbol = symbol.replace("&","%26")    
 symbol = symbol.upper()   
 os.environ['MOZ_HEADLESS'] = '1'  
 driver = webdriver.Firefox()  #อาจต้องลง 
 driver.get("https://www.wsj.com/market-data/quotes/TH/XBKK/"+symbol+"/financials")
 
 #########
    
 lb = []
 data = []
 for i in driver.find_elements_by_class_name("cr_sub_profitability"): 
    #print(i.text+"_")
    for j in i.find_elements_by_class_name("data_lbl"):
     lb.append(j.text)
    for j in i.find_elements_by_class_name("data_data"):
     t = j.text.replace("+","").replace("-","")
     data.append(float(t))
        
 #########
 return pd.DataFrame({symbol:data},index=lb)