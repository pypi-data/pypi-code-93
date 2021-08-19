#DuPontROE.py
import pandas as pd
import requests
from bs4 import BeautifulSoup
 
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
#from starfishX.starfishXfn import loadHistData
#from starfishX.incomestatement import getIncomeStatement
#from starfishX.starfishXfn import getBalanceSheet
exec("from "+prefix+"incomestatement import getIncomeStatement")
exec("from "+prefix+"starfishXfn import getBalanceSheet")
###################### END ส่วนที่ใช้ Library ภายใน ###################


def DuPontROE_kVersion(symbol,year):  
 headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}  
 symbolMofi = symbol.replace("&","%26")
 url = "https://www.set.or.th/set/companyhighlight.do?symbol="+symbolMofi
 r = requests.get(url,headers)
 soup = BeautifulSoup(r.content, "lxml")

 data = soup.find_all("table",{"class":"table table-hover table-info"})
 
 #ถ้า symbol มั่วๆ มาเช่น หุ้น CAT,DOG,RAT
 if(len(data)==0):
    print("Incomplete data")
    return 0,0

 tr = data[0].find_all("tr")  


 cnt = 0
 tddataAr = []
 trdataAr = []
 for trdata in tr:
  tddataAr = []
  if(cnt==0):
    td = trdata.find_all("th")
    for tddata in td:
        k = str(tddata.strong).replace("<br/>"," ")
        k = k.replace("<strong>","")
        k = k.replace("</strong>","")
        tddataAr.append(k)
  else:
    td = trdata.find_all("td")
    for tddata in td:
        p = str(tddata.text.strip())
        #print(tddata.text)
        if("บัญชีทางการเงินที่สำคัญ" in p):
            break
        elif("อัตราส่วนทางการเงินที่สำคัญ" in p):
            break
        elif("วันที่ของงบการเงินที่ใช้คำนวณค่าสถิติ" in p):
            break    
        #else:
            #continue
            #print(p,"-")
            #tddata.append(p)
        tddataAr.append(p)    
  cnt=+1
  if(len(tddataAr)>0):
   trdataAr.append(tddataAr)

  #######################
  #ประมวลผลข้อมูลในการสร้าง DataFrame
  df = pd.DataFrame(trdataAr)
  df.columns = trdataAr[0]
 
  df = df.drop(0)
 
  #หาคอลัมม์ของข้อมูล
  colIndex = -1
  cnt = 0
  for i in df.columns:
   k = str(i) 
   if(year in k):
     colIndex = cnt
   cnt+=1
 
 if(colIndex==-1 or colIndex==1):
   print("Incomplete data")
   return 0,0
 
 if("ไตรมาส" in df.columns[colIndex]):
   print("Incomplete data")
   return 0,0

 


 #ดึงค่าไปส่งรายงาน
 SALE = df[df[df.columns[0]]=="รายได้รวม"][df.columns[colIndex]]
 NI = df[df[df.columns[0]]=="กำไรสุทธิ"][df.columns[colIndex]]
 TA = df[df[df.columns[0]]=="สินทรัพย์รวม"][df.columns[colIndex]]
 E1 = df[df[df.columns[0]]=="ส่วนของผู้ถือหุ้น"][df.columns[colIndex]]
 E2 = df[df[df.columns[0]]=="ส่วนของผู้ถือหุ้น"][df.columns[colIndex-1]]

 SALE = float(SALE.values[0].replace(",",""))
 NI   = float(NI.values[0].replace(",",""))
 TA   = float(TA.values[0].replace(",",""))
 E1   = float(E1.values[0].replace(",",""))
 E2   = float(E2.values[0].replace(",",""))

 E = (E1+E2)/2

 ROE = [{'NI/SALE':NI/SALE,'SALE/TA':SALE/TA,'TA/E':TA/E}] 
 df1 = pd.DataFrame(ROE)
 df1['year'] = int(year)+2500
 df1 = df1.set_index("year")  

 df2 = pd.DataFrame({"NI":[NI],"SALE":[SALE],"TA":[TA],"E":[E]})
 df2['year'] = int(year)+2500
 df2 = df2.set_index("year")
 return df1,df2
################################# end function #####################################







def getCol(dfis,year):
 year = str(year)   
 for i in range(len(dfis.columns)):
  if(dfis.columns[i].startswith(year)):
   try:
    return dfis.columns[i],dfis.columns[i+1]
   except:
    return 1,0    
 return 0,0

 # ==============================
def DuPontROE(symbol,year,firstLine=False):  
 """
    Returns df,detail : df ประกอบด้วย NI/SALE , SALE/TA และ TA/E  
    
                        ส่วน detail ประกอบด้วย NI,SALE,TA และ E
    
    arg1 (string) : symbol ตัวย่อของหุ้น
    
    arg2 (int)    : year ปี โดยเป็นปี พ.ศ. เช่น 2561 
    
    arg3 (Boolean): firstLine เป็น True จะใช้ SALE เป็นรายได้ในบรรทัดบนสุด ถ้าเป็น False จะใช้รายได้รวมทั้งหมด

 """    
 #เช็ค type ของ year   
 try:
   int(year)
   pass
 except:
   print("Year type miss match.")   
   return 0,0
 
 if(firstLine==False):
    year = str(int(year)-2500)
    Dupont,Detail = DuPontROE_kVersion(symbol,year)
    return Dupont,Detail
    
    
 dfis = getIncomeStatement(symbol)
 dfbs = getBalanceSheet(symbol)
 
 majorYear,minorYear = getCol(dfis,year) 

 if(majorYear==1 and minorYear==0):
    print("Incomplete data.,MinorYear Not Found")
    return 0,0

 if(majorYear==0 and minorYear==0):
    print("Incomplete data")
    return 0,0

 if (type(dfis) == int) or (type(dfbs) == int):
    return 0,0
 
 NI = dfis[dfis["งบกำไรขาดทุนเบ็ดเสร็จ(ลบ.)"]=="กำไร(ขาดทุน)สุทธิ"][majorYear]
 
 SALE = dfis[dfis["งบกำไรขาดทุนเบ็ดเสร็จ(ลบ.)"]=="ยอดขายสุทธิ"][majorYear]
 if(len(SALE)==0):
  SALE = dfis[dfis["งบกำไรขาดทุนเบ็ดเสร็จ(ลบ.)"]=="รายได้ดอกเบี้ยและเงินปันผล"][majorYear]
 
     
 TA = dfbs[dfbs["งบแสดงฐานะการเงิน(ลบ.)"]=="รวมสินทรัพย์"][majorYear]
 E1 = dfbs[dfbs["งบแสดงฐานะการเงิน(ลบ.)"]=="ส่วนของผู้ถือหุ้นบริษัทใหญ่"][majorYear]
 E2 = dfbs[dfbs["งบแสดงฐานะการเงิน(ลบ.)"]=="ส่วนของผู้ถือหุ้นบริษัทใหญ่"][minorYear]  
 
 NI = str(NI.values[0]).replace(",","")  
 NI = NI.replace("-","")
 NI = float(NI)
 
 SALE = str(SALE.values[0]).replace(",","")
 if("-" in SALE):
   print("Incomplete data")
   return 0,0   
 SALE = float(SALE)
 
 TA = float(str(TA.values[0]).replace(",",""))
 E1 = float(str(E1.values[0]).replace(",",""))
 E2 = float(str(E2.values[0]).replace(",",""))
 
 E = (E1+E2)/2
    
 ROE = [{'NI/SALE':NI/SALE,'SALE/TA':SALE/TA,'TA/E':TA/E}]  
 
 df1 = pd.DataFrame(ROE)
 df1['year'] = year
 df1 = df1.set_index("year")  

 df2 = pd.DataFrame({"NI":[NI],"SALE":[SALE],"TA":[TA],"E":[E]})
 df2['year'] = year
 df2 = df2.set_index("year")
 return df1,df2

# ==============================