#LongTermDebt

import pandas as pd
import os
from selenium import webdriver

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

def getLongTermDebt(symbol):
  url = "http://financials.morningstar.com/balance-sheet/bs.html?t="+symbol+"&region=tha&culture=en-US"
  #os.environ['MOZ_HEADLESS'] = '1'  
 
  options = Options()
  options.add_argument('-headless')
  
  driver = webdriver.Safari()
  #driver = webdriver.Safari(options)
  #driver = webdriver.Firefox()  #อาจต้องลง 
  # Grab the web page
  #driver.manage().timeouts().implicitlyWait(10, TimeUnit.SECONDS);
  print("Processing..",end="")  
  driver.get(url)  
  wait = WebDriverWait(driver, 5)
  print(".",end="")  
  ################
  data = []  
  header = []
  ################  
  k = driver.find_element_by_id("data_i50")
  for i in k.find_elements_by_tag_name("div"):
    data.append(float(i.text.replace(",","")))
    print(".",end="")   
    
  k = driver.find_element_by_id("Year")
  for i in k.find_elements_by_tag_name("div"):
    header.append(i.text) 
    print(".",end="")   
    
  df = pd.DataFrame({"Long Term Debt":data},index=header)
  print(".",end="") 
  driver.close()
  print(".End.",end="")  
  return df