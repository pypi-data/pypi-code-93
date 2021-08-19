######### moc.py
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


import pandas as pd
import requests
import numpy as np
from bs4 import BeautifulSoup
import json
import matplotlib.pyplot as plt
 
#%config InlineBackend.figure_format ='retina'
import matplotlib as mpl
import matplotlib.font_manager as font_manager

import matplotlib.dates as mdates
from datetime import datetime




def mocExport(keyword,year,month,notkeyword="xyzabc0123456789"):

   #
   #set title ภาษาไทย
   #https://stackoverflow.com/questions/16574898/how-to-load-ttf-file-in-matplotlib-using-mpl-rcparams
   path = 'DB_Helvethaica_X.ttf'
   prop = font_manager.FontProperties(fname=path)
   mpl.rcParams['font.family'] = prop.get_name()
 
   params = {'legend.title_fontsize':0,
          'legend.fontsize': 20,
          'figure.figsize': (16, 8),
          'axes.labelsize': 20,
          'axes.titlesize':20,
          'xtick.labelsize':20,
          'ytick.labelsize':20}
   plt.rcParams.update(params)


   #keyword = "อัญมณี"
   year = str(year)
   #month = ["7","8","9"]

   url = "https://dataapi.moc.go.th/products?keyword="+keyword+"&revision=2017&imex_type=export&order_by=com_code"
   headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
  
   r = requests.get(url,headers)
   jsonContent = json.loads(r.content)
   print("Cat Item : "+str(len(jsonContent)).strip())
   if(len(jsonContent)>30):
     print("Keyword มากเกินไป เพิ่มคำระบุในการค้นหา")
     return 0,0
   
   if(len(jsonContent)==0):
     print("ไม่พบข้อมูล")
     return 0,0
   ###################  # hs_description_th com_description_th
   keyCodeDS = pd.DataFrame(jsonContent).groupby("com_code")[["com_code","com_description_th","hs_description_th"]].max()
   
   content_ds = []
   for i,col in enumerate(keyCodeDS["com_code"],0):
    com_code = keyCodeDS["com_code"][i]
    print(keyCodeDS["com_code"][i],keyCodeDS["com_description_th"][i].strip())
    for m in month:
     url = "https://dataapi.moc.go.th/export-commodity-countries?year="+ \
        year+"&month="+str(m)+"&com_code="+keyCodeDS["com_code"][i]+"&limit="
     r = requests.get(url,headers)
     itemContent = json.loads(r.content) 
     df = pd.DataFrame(itemContent)
     if(len(df)>0):
       value_item = df[["country_name_th","value_baht"]]["value_baht"].sum()
     else:
       value_item = 0
       
     value_item = value_item/1000000   
   
     #print(year,m)
     month_ds = datetime(int(year),int(m),1)
     desc = keyCodeDS["com_description_th"][i].strip().replace(" ","")
     
     try:
      descDetail = keyCodeDS["hs_description_th"][i].strip().replace(" ","")
     except:
      descDetail = "None"

     #ตรวจสอบเช่นตาไก่ จะเป็นอุปกรณ์ไม่ใช่สินค้าเกษตร
     if(not((notkeyword in descDetail) or (notkeyword in desc)) ):
        content_ds.append({"Month":month_ds,"Label":desc,"Value":value_item,"Detail":descDetail})
        
   #######################
   k = pd.DataFrame(content_ds) 
    
   pivot_df = k.pivot(index='Month', columns='Label', values='Value') 
   labels = [l.strftime('%Y-%m') for l in pivot_df.index]
    
   ax = pivot_df.plot(figsize=(10,6),kind="bar",stacked=True,title="ยอดส่งออกสินค้า")
   ax.set_xticklabels(labels)
   ax.set_ylabel("ล้านบาท")
   plt.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0))
   plt.rc('font', family='serif', size='12.0')
   

   return k,pivot_df