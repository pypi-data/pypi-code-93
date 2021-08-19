#getEVEBITDA.py
import pandas as pd

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
#from starfishX.findMarketCap import findMarketCap
#from starfishX.incomestatement import getIncomeStatement
#from starfishX.starfishXfn import getBalanceSheet
exec("from "+prefix+"findMarketCap import findMarketCap")
exec("from "+prefix+"incomestatement import getIncomeStatement")
exec("from "+prefix+"starfishXfn import getBalanceSheet")
###################### END ส่วนที่ใช้ Library ภายใน ###################


def analyseEVEBITDA(basket,yearstart,yearend,viewlog=True):
 """
    วิเคราะห์คุณภาพของ EV/EBITDA
 
    Returns ไม่มี
    
    arg1 (list): list ของตัวย่อของหุ้น เช่น ["aot","cpall","ptt"]
    
 """ 
 pcheck = 0    
 try:
   if(isinstance(basket.tolist(), list)):
      pass
 except:
   if(type(basket)==list):
      pass
   else:
      print("Data type miss match")  
      return 0  
 

 for s in basket: 
  if(viewlog==True): 
    print(s,end=" ")   
  _,k1 = getEVEBITDA(s,yearend)
  if(type(k1)==int):
    continue  
    
  _,k2 = getEVEBITDA(s,yearstart)
  if(type(k1)==int or type(k2)==int):
    continue
  
  if(viewlog==False): #เช็คแค่ตัวแรกของ basket
    return k1,k2

  marketCap61 = k1['marketCap'][0]
  marketCap60 = k2['marketCap'][0]

  TL61 = k1['TL'][0]
  TL60 = k2['TL'][0]

  cash61 = k1['cash'][0]
  cash60 = k2['cash'][0]

  ebitda61 = k1['ebitda'][0]
  ebitda60 = k2['ebitda'][0]
 
  ev61 = (marketCap61+TL61-cash61)  #EV
  ev60 = (marketCap60+TL60-cash60)  #EV
 
  evebitda61 = (ev61/ebitda61)  #EV/EBITDA
  evebitda60 = (ev60/ebitda60)  #EV/EBITDA

  p1 = False
  pctP1 = 0
  if(evebitda61<evebitda60):
    p1 = True
    pctP1 = (evebitda60 - evebitda61)/evebitda60
  else:
    pctP1 = (evebitda61 - evebitda60)/evebitda60

  pctP2 = 0
  p2 = False
  if( (ev61>ev60) ):
    p2 = True
    pctP2 = (ev61-ev60)/ev60
  else:
    pctP2 = (ev60-ev61)/ev60
    
    
  pctP3 = 0  
  p3 = False
  if(marketCap61>marketCap60):
    p3 = True 
    pctP3 = (marketCap61-marketCap60)/marketCap60
  else:
    pctP3 = (marketCap60-marketCap61)/marketCap60
    
    
  pctP4 = 0  
  p4 = False
  if(TL61<TL60):
    p4 = True 
    pctP4 = (TL60 - TL61)/TL60
  else:
    pctP4 = (TL61 - TL60)/TL60
    
  pctP5 = 0  
  p5 = False
  if(ebitda61>ebitda60):
    p5 = True 
    pctP5 = (ebitda61-ebitda60)/ebitda60
  else:
    pctP5 = (ebitda60-ebitda61)/ebitda60
    
 
  pctP1 = round(pctP1, 4)
  pctP2 = round(pctP2, 4)
  pctP3 = round(pctP3, 4)
  pctP4 = round(pctP4, 4)
  pctP5 = round(pctP5, 4)
         

  if(p1 and p2 and p3 and p4 and p5): #1evebitda 2ev 3marketcap 4TL 5ebitda
     print("***",end=" ")
  elif(p1 and p2 and p5): 
     print("**",end=" ")
  elif(p4 and p5): 
     print("*",end=" ")
 
  #สัญลักษณ์ต่างๆ 
  #http://xahlee.info/comp/unicode_arrows.html  ⬇⬆ ↑↓  ↑ ↓  ↑ ↓
  if(p1):
    if(pctP1>0.1):   
      print("EV/EBITDA⬇("+str(pctP1),end=") ")
    else:
      print("EV/EBITDA↓("+str(pctP1),end=") ")
  else:
    if(pctP1>0.1):
      print("EV/EBITDA⬆("+str(pctP1),end=") ")
    else:
      print("EV/EBITDA↑("+str(pctP1),end=") ")  
    
    
  if(p2):
    if(pctP2>0.1):
      print("EV⬆("+str(pctP2),end=") ")
    else:
      print("EV↑("+str(pctP2),end=") ")  
  else:
    if(pctP2>0.1):
      print("EV⬇("+str(pctP2),end=") ")
    else:
      print("EV↓("+str(pctP2),end=") ")
    
  if(p3):
    if(pctP3>0.1):
      print("Market Cap.⬆("+str(pctP3),end=") ")
    else:
      print("Market Cap.↑("+str(pctP3),end=") ")  
  else:
    if(pctP3>0.1):
      print("Market Cap.⬇("+str(pctP3),end=") ")
    else:
      print("Market Cap.↓("+str(pctP3),end=") ")
    
    
  if(p4):
    if(pctP4>0.1):
      print("Total Liabilities⬇("+str(pctP4),end=") ")
    else:
      print("Total Liabilities↓("+str(pctP4),end=") ")  
  else:
    if(pctP2>0.1):
      print("Total Liabilities⬆("+str(pctP4),end=") ")
    else:
      print("Total Liabilities↑("+str(pctP4),end=") ")
    
    
  if(p5):
    if(pctP5>0.1):
       print("EBITDA⬆("+str(pctP5)+")")
    else:
       print("EBITDA↑("+str(pctP5)+")") 
  else:
    if(pctP5>0.1):
       print("EBITDA⬇("+str(pctP5)+")")   
    else:
       print("EBITDA↓("+str(pctP5)+")") 
  

#############################################

def getEVEBIT(symbol,year,marketCapYTD=True):
  """
    Returns EV/EBIT,Log : จาก ( market cap. + หนี้สินรวม - เงินสด ) / EBIT
    
    ส่วน Log จะเป็น DataFrame ของข้อมูลดิบเอาไว้ตรวจสอบ
    
    arg1 (string): ตัวย่อของหุ้น
    
    arg2 (int): ปีพ.ศ. เช่น 2561 หรือ 2560

    * ไม่ support กลุ่ม bank และเช่าซื้อ
  """  
  if(type(year)==int):
    year=str(year)
    
  df1 = findMarketCap(symbol,withHist=True)
  if(type(df1)==int):
    return 0,0

  if(marketCapYTD==True):
   marketCap = df1.iloc[0][0] #เอา marketcap ล่าสุด
  else:  
   marketCap =  df1.getData(row="หลักทรัพย์",col=year)
  
  if(marketCap==0):
    return 0,0


    
  df2 = getIncomeStatement(symbol) 
  ebit = df2.getData(row="กำไรก่อนด/บ และภาษีเงินได้",col=year)
  if(ebit==0):
    #print("ไม่พบ ebitda,ไม่สามารถคำนวณได้") 
    return 0,0 
  if(ebit<0):
    print("EBIT ติดลบ,ไม่สามารถคำนวณได้") 
    return 0,0


  df3 = getBalanceSheet(symbol)
  cash = df3.getData(row="เงินสด",col=year)
  TL = df3.getData(row="รวมหนี้",col=year)

  bvebit  = (marketCap+TL-cash)/(ebit)
  rp = pd.DataFrame({"marketCap":[marketCap],"ebit":[ebit],"cash":[cash],"TL":[TL]})  
  return bvebit,rp




def getEVEBITDA(symbol,year):
  """
    Returns EV/EBITDA,Log : จาก ( market cap. + หนี้สินรวม - เงินสด ) / EBITDA
    
    ส่วน Log จะเป็น DataFrame ของข้อมูลดิบเอาไว้ตรวจสอบ
    
    arg1 (string): ตัวย่อของหุ้น
    
    arg2 (int): ปีพ.ศ. เช่น 2561 หรือ 2560

    * ไม่ support กลุ่ม bank และเช่าซื้อ
  """  
  if(type(year)==int):
    year=str(year)
    
  df1 = findMarketCap(symbol,withHist=True)
  if(type(df1)==int):
    return 0,0

  marketCap =  df1.getData(row="หลักทรัพย์",col=year)
  if(marketCap==0):
    return 0,0
    
  df2 = getIncomeStatement(symbol) 
  ebitda = df2.getData(row="ebitda",col=year)
  if(ebitda==0):
    #print("ไม่พบ ebitda,ไม่สามารถคำนวณได้") 
    return 0,0 
  if(ebitda<0):
    print("EBITDA ติดลบ,ไม่สามารถคำนวณได้") 
    return 0,0

  df3 = getBalanceSheet(symbol)
  cash = df3.getData(row="เงินสด",col=year)
  TL = df3.getData(row="รวมหนี้",col=year)

  bvebitda  = (marketCap+TL-cash)/ebitda
  rp = pd.DataFrame({"marketCap":[marketCap],"ebitda":[ebitda],"cash":[cash],"TL":[TL]})  
  return bvebitda,rp

#############################################
def getData(self,row,col):
    try:
       if(type(col)==int):
        self.columns[col]
    except:
       print("out of index") 
       return 0 

    ############ กรณี int ############ 
    if((type(row))==int and (type(col)==int)):
     d = self[self.columns[col]].iloc[row]
     if(type(d)==str):
        d = float(d.replace(",",""))
     
     return d   
        
    ############ กรณี string ############    
    if(type(row)==str):  
      rows = ""
      for i in self.index:
       if(row in str.lower(i)):
        rows = i
 
      cols = ""
      if(type(col)==int):
         cols = self.columns[col]
      elif(type(col)==str): 
       for i in self.columns:
        if(col in str.lower(i)[0:5]):
         cols = i
    
    if(rows==""):
      print("out of index,Rows") 
      return 0
    
    if(cols==""):
      print("out of index,Cols") 
      return 0  
    
    d = self[self.index==rows][cols]
    d = d.values[0]
    if(type(d)==str):
     d = float(d.replace(",",""))
        
    return d

#############################################
setattr(pd.core.frame.DataFrame, 'getData', getData)   
#############################################