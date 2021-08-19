import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def getAssets(symbol,viewlog=False):

 """
    Returns DataFrame : รายละเอียดของ Asset พร้อมประเภททรัพย์สิน 
    
    arg1 (string): ตัวย่อของหุ้น
    
    arg2 (list): keywordlist เป็นตัวคัดกรองข้อมูลส่วน keywordlist เป็นตัวคัดกรองข้อมูล

 """   
 ###### zone1 ดึงข้อมูล
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 symbolMofi = symbol.replace("&","%26")
 #url = "https://www.set.or.th/set/companyhighlight.do?symbol="+symbolMofi
 url = "https://www.set.or.th/set/companyfinance.do?type=balance&symbol="+symbolMofi+"&language=th&country=TH"
 r = requests.get(url,headers)
 soup = BeautifulSoup(r.content, "lxml")

 ###### zone2 หาส่วนที่จะใช้
 #data = soup.find_all("table",{"class":"table table-hover table-info"})
 data = soup.find_all("table",{"class":"table table-info-wrap"})   #19 สิงหาคม 2564 update
 if(len(data)==0):
    print("ไม่พบข้อมูล")
    #return 0,0,0   
 tr = data[2].find_all("tr") 
 
 ###### zone3 เตรียมดาต้ามาประมวลผล
 asset = []
    
 assetlb = [] #version peter lynch   
 asset_type = "Current Assets" #version peter lynch     
 asset_type_ds = [] #version peter lynch     
    
 lb = []
 valuelb = []
 eq = []
 g = 0
 rp = []  
 previousKey = ""
 for i in tr:
   td = i.find_all("td") 
   #print(td[0].text)
   if(len(td)==1):
     if(td[0].text=="สินทรัพย์(หน่วย: ล้านบาท)"): #19 สิงหาคม 2564 update  ตลาดเติมคำว่า  (หน่วย: ล้านบาท) เข้ามา
         g+=1
        
     if(td[0].text=="หนี้สิน(หน่วย: ล้านบาท)"): #19 สิงหาคม 2564 update
         g+=1
     if(td[0].text=="ส่วนของผู้ถือหุ้น(หน่วย: ล้านบาท)"):   #19 สิงหาคม 2564 update
         g+=1    
   if(len(td)>1):
    m = td[1].text.replace(",","")
    m = float(m)   
    #print(m)
    if("\xa0" in td[0].text[0]):
      #print(td[1].text) 
      pass   
 
    if(g==1):
       #version peter lynch   
       if(td[0].text=="รวมสินทรัพย์หมุนเวียน"): #หาว่าหมดสินทรัพย์หมุนเวียนแล้วหรือยัง
          asset_type = "Non-Current Assets"  
            
       if( (td[0].text!="รวมสินทรัพย์หมุนเวียน") and (td[0].text!="รวมสินทรัพย์ไม่หมุนเวียน")  ):
         asset.append(td[0].text)  
         assetlb.append(td[1].text) #version peter lynch  
         asset_type_ds.append(asset_type) #version peter lynch  
        
    if(g==2):
       break
    
    
 ###### zone4 clean พวกแถวที่จะทำให้รายการคำนวณผิด
 mainlabel = []
 valuemainlabel = []
 mainindex = -1
 sublabel = []
 valuesublabel = []
 asset_type_main_ds = [] 
 asset_type_sub_ds = []
 for i in range(len(asset)-1): # -1 คือเอา รวมทรัพย์สิน ออก
  if("\xa0" in asset[i][0]):
    sublabel.append("("+str(mainindex)+") "+asset[i])
    valuesublabel.append(assetlb[i]) 
    asset_type_sub_ds.append(asset_type_ds[i])
  else:
    mainindex+=1
    mainlabel.append("("+str(mainindex)+") "+asset[i])
    valuemainlabel.append(assetlb[i]) 
    asset_type_main_ds.append(asset_type_ds[i])
  
 ##################
 rp1 = [] 
 rpv = []
 rpt = []   
 for i in range(len(mainlabel)):
  k = 0
  indexSub = 0
  for j in range(len(sublabel)):
    if(mainlabel[i][0:3] in sublabel[j][0:3]):
      k+=1
      subjective = mainlabel[i]+" "+sublabel[j]
      rp1.append(mainlabel[i]+" "+sublabel[j])   # + " "+str(valuesublabel[j])
      rpv.append(float(str(valuesublabel[j]).replace(",","")))
      rpt.append(asset_type_sub_ds[j])

  if(k==0):
    subjective = mainlabel[i].strip()#+" "+sublabel[j]
    rp1.append(mainlabel[i]) #+" "+str(valuemainlabel[i])
    rpv.append(float(str(valuemainlabel[i]).replace(",","")))
    rpt.append(asset_type_main_ds[i])   
    
 #########
 for i in range(len(rp1)): 
  rp1[i] = rp1[i].replace("\xa0","")
  rp1[i] = rp1[i].replace("(1)","")
  rp1[i] = rp1[i].replace("(2)","")
  rp1[i] = rp1[i].replace("(3)","")
  rp1[i] = rp1[i].replace("(4)","")
  rp1[i] = rp1[i].replace("(5)","")
  rp1[i] = rp1[i].replace("(6)","")
  rp1[i] = rp1[i].replace("(7)","")
  rp1[i] = rp1[i].replace("(8)","")
  rp1[i] = rp1[i].replace("(9)","")
  rp1[i] = rp1[i].replace("(10)","")  
  rp1[i] = rp1[i].replace("(11)","")
  rp1[i] = rp1[i].replace("(12)","")
  rp1[i] = rp1[i].replace("(13)","")
  rp1[i] = rp1[i].replace("(14)","")
  rp1[i] = rp1[i].replace("(15)","")
  rp1[i] = rp1[i].replace("(16)","")
  rp1[i] = rp1[i].replace("(0)","")
 ########
 pd.options.display.max_colwidth = 100
 df = pd.DataFrame({"Label":rp1,"Value":rpv,"Type":rpt})   
 return df   





def getLiabilities(symbol,keywordlist = ['เงินกู้','ตราสารหนี้','หุ้นกู้','เงินเบิกเกินบัญชี','หนี้สินระยะยาว - สุทธิจากส่วนที่ถึงกำหนดชำระภายในหนึ่งปี','ส่วนของหนี้สินระยะยาวที่ถึงกำหนดชำระภายในหนึ่งปี'],viewlog=False):
 """
    Returns TL,IBD,Log : หนี้สินรวม , หนี้สินที่คาดว่ามีดอกเบี้ย และ Log ของรายการ 
    
    arg1 (string): ตัวย่อของหุ้น
    
    arg2 (list): keywordlist เป็นตัวคัดกรองข้อมูลส่วน keywordlist เป็นตัวคัดกรองข้อมูล

 """   
###### zone1 ดึงข้อมูล
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 symbolMofi = symbol.replace("&","%26")
 #url = "https://www.set.or.th/set/companyhighlight.do?symbol="+symbolMofi
 url = "https://www.set.or.th/set/companyfinance.do?type=balance&symbol="+symbolMofi+"&language=th&country=TH"
 r = requests.get(url,headers)
 soup = BeautifulSoup(r.content, "lxml")

###### zone2 หาส่วนที่จะใช้
 #data = soup.find_all("table",{"class":"table table-hover table-info"})
 data = soup.find_all("table",{"class":"table table-info-wrap"})   #19 สิงหาคม 2564 update
 if(len(data)==0):
    print("ไม่พบข้อมูล")
    return 0,0,0   
 tr = data[2].find_all("tr") 

###### zone3 เตรียมดาต้ามาประมวลผล
 lb = []
 valuelb = []
 
 lb_type = "Current Liabilities"
 lb_type_ds = []
 
 g = 0
 rp = []  
 previousKey = ""
 for i in tr:
   td = i.find_all("td") 
   if(len(td)==1):
     if(td[0].text=="สินทรัพย์(หน่วย: ล้านบาท)"):
         g+=1
     if(td[0].text=="หนี้สิน(หน่วย: ล้านบาท)"):
         g+=1
     if(td[0].text=="ส่วนของผู้ถือหุ้น(หน่วย: ล้านบาท)"):
         g+=1    
   if(len(td)>1):
    #print(td[1].text)
    #rp.append(td[1].text)
    m = td[1].text.replace(",","")
    m = float(m)   
    #print(m)
    if("\xa0" in td[0].text[0]):
      #print(td[1].text) 
      pass   
 
    if(g==1):
       #asset.append(td[1].text) 
       pass  
    if(g==2):
       
       if(td[0].text=="รวมหนี้สินหมุนเวียน"): #หาว่าหมดสินทรัพย์หมุนเวียนแล้วหรือยัง
          lb_type = "Non-Current Liabilities" 

       if( (td[0].text!="รวมหนี้สินไม่หมุนเวียน") and (td[0].text!="รวมหนี้สินหมุนเวียน")  ):
        
        if(viewlog):
          print(td[0].text+" "+str(m))   
        
        #fix bug 1 may version ของ peter lynch
        previousKey = td[0].text.strip()  
        lb.append(td[0].text)
        valuelb.append(m)

        lb_type_ds.append(lb_type)
        
          
    if(g==3): 
        break      
        
###### zone4 clean พวกแถวที่จะทำให้รายการคำนวณผิด
 mainlabel = []
 valuemainlabel = []
 mainindex = -1
 sublabel = []
 valuesublabel = []
  
 lia_type_main_ds = [] 
 lia_type_sub_ds = []

 #rp1 = []
 for i in range(len(lb)-1): # -1 คือเอา รวมหนี้สิน ออก
  #print(lb[i])
  #rp1.append(lb[i])
  if("\xa0" in lb[i][0]):
    #print(lb[i]) 
    sublabel.append("("+str(mainindex)+") "+lb[i])
    valuesublabel.append(valuelb[i]) 
    lia_type_sub_ds.append(lb_type_ds[i])
  else:
    mainindex+=1
    mainlabel.append("("+str(mainindex)+") "+lb[i])
    valuemainlabel.append(valuelb[i]) 
    lia_type_main_ds.append(lb_type_ds[i])
    
 
###### zone5 คำนวณผลรวม      
 sumlb = 0
 InterestBearingDebt = 0
 #keywordlist = ['เงินกู้','ตราสารหนี้']

 
 rp1 = [] 
 rpv = []  
 rpt = [] 
 rpIBD = []
 for i in range(len(mainlabel)):
  k = 0
  indexSub = 0
  for j in range(len(sublabel)):
    if(mainlabel[i][0:3] in sublabel[j][0:3]):
      k+=1
      subjective = mainlabel[i]+" "+sublabel[j]
      #print(mainlabel[i]+" "+sublabel[j]+ " "+str(valuesublabel[j]))
      #print(subjective)   
 
      rp1.append(mainlabel[i]+" "+sublabel[j])   # + " "+str(valuesublabel[j])
      rpv.append(float(str(valuesublabel[j])))
      InterestBearingDebt += valuesublabel[j]
      rpt.append(lia_type_sub_ds[j])
      #print(valuesublabel[j])         
      sumlb += valuesublabel[j]
      if any(s in subjective for s in keywordlist): 
         rpIBD.append("IBD")
      else:
         rpIBD.append("Non-IBD")

  if(k==0):
    #print(mainlabel[i])# + " "+str(valuemainlabel[i]))
    subjective = mainlabel[i].strip()#+" "+sublabel[j]
    #print(subjective) 
    rp1.append(mainlabel[i]) #+" "+str(valuemainlabel[i])
    rpv.append(float(str(valuemainlabel[i])))
    InterestBearingDebt += valuemainlabel[i]
    rpt.append(lia_type_main_ds[i])
    #print(valuemainlabel[i])   
    sumlb += valuemainlabel[i]
    if any(s in subjective for s in keywordlist): 
         rpIBD.append("IBD")
    else:
         rpIBD.append("Non-IBD") 

  
###### zone6 clear report    
 for i in range(len(rp1)): 
  rp1[i] = rp1[i].replace("\xa0","")
  rp1[i] = rp1[i].replace("(1)","")
  rp1[i] = rp1[i].replace("(2)","")
  rp1[i] = rp1[i].replace("(3)","")
  rp1[i] = rp1[i].replace("(4)","")
  rp1[i] = rp1[i].replace("(5)","")
  rp1[i] = rp1[i].replace("(6)","")
  rp1[i] = rp1[i].replace("(7)","")
  rp1[i] = rp1[i].replace("(8)","")
  rp1[i] = rp1[i].replace("(9)","")
  rp1[i] = rp1[i].replace("(10)","")
  rp1[i] = rp1[i].replace("(11)","")
  rp1[i] = rp1[i].replace("(12)","")
  rp1[i] = rp1[i].replace("(13)","")
  rp1[i] = rp1[i].replace("(14)","")
  rp1[i] = rp1[i].replace("(0)","")
###### zone7 return ผลลัพธ์
 rp = pd.DataFrame({"Label":rp1,"Value":rpv,"Type":rpt,"IBD":rpIBD},index=np.array(range(1,len(rp1)+1)))


 ###########
 type_debt = []
 for i in rp["Label"]:
    if("ตราสารหนี้" in i):
       type_debt.append("Bond")
    elif("สถาบันการเงิน" in i):
       type_debt.append("Institute")
    else:
       type_debt.append("N/A")
    
    
 rp["From"] = type_debt

 return rp