#indicator.py
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

###################### ส่วนที่ใช้ Library ภายใน ###################
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

# สำหรับ getMemberOfIndex    #starfishX Production #__init__ debug Mode
#from starfishX.starfishXfn import loadHistData
exec("from "+prefix+"starfishXfn import loadHistData")
###################### END ส่วนที่ใช้ Library ภายใน ###################


def linregressIndicator(basket,periodDay,startDay="2018-01-01",viewlog=True,viewplot=True):
 symbol_ds = []
 slope_ds = []
 RSquared_ds = []
 
 try:
  periodDay = int(periodDay)
 except:
  if(viewlog==True):      
    print("Data Type Period Day Miss Match")   
  return 0   

 if(not type(periodDay)==int):
   if(viewlog==True):     
     print("Data Type Period Day Miss Match")   
   return 0   
 
 try:
   if(isinstance(basket.tolist(), list)):
      pass
 except:
   if(type(basket)==list):
      pass
   else:
      print("Data type miss match")  
      return 0    
    
 for i in basket:   
  
  df = loadHistData(i,start=startDay).tail(periodDay)
  x = np.arange(0,len(df),1)
  y = df[i].values 
  
  slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
 
  RSquared = ((r_value**2))**0.5
  
  symbol_ds.append(i)
  slope_ds.append(slope)  
  RSquared_ds.append(RSquared)

  k = (slope*RSquared)-slope
  k = (k**2)**0.5  
  
  if(viewlog==True):
    print("%s\tSlope:%f\t  RSquared: %f" % (i,slope, RSquared))  
   

  rp = pd.DataFrame({"Symbol":symbol_ds,"Slope":slope_ds,"RSquared":RSquared_ds})
 

 ########## ส่วน plot graph ##########
 if(viewplot==True):
  rp.sort_values(["Slope","RSquared"],ascending=[False,True]). \
     plot(kind="bar",figsize=(20,6),x="Symbol",y=["Slope","RSquared"],title="Linear least-squares regression : Close Price "+str(periodDay)+" Days")
  
  if(rp['Slope'].max()>rp['RSquared'].max()):
    ylimP = rp['Slope'].max()
  else:
    ylimP = rp['RSquared'].max()
  
  if(rp['Slope'].min()<rp['RSquared'].min()):
    ylimN = rp['Slope'].min()
  else:
    ylimN = rp['RSquared'].min()
    
  plt.ylim(top=ylimP*1.05)
  plt.ylim(bottom=ylimN*1.05)
 ########## END ส่วน plot graph ##########   
 
 return rp   

