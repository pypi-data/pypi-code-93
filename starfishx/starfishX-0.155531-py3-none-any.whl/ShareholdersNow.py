import pandas as pd
import difflib 

def ShareholdersNow(keyword):
 '''
    keyword : str
    คืนค่ารายชื่อผู้ถือหุ้นที่เทียบกับปิดสมุดล่าสุด
 '''
 df = pd.read_csv("ShareholdersTB.csv")
 df["Date"] = pd.to_datetime(df["Date"],format='%Y-%m-%d')
 df["NameSer"] = df["Name"].str.lower() 

 keyword = keyword.lower()
 df["Date"] = pd.to_datetime(df["Date"],format='%Y-%m-%d')
 df1 = df[df["NameSer"].str.contains(keyword)].groupby(["Symbol"]).max()
    
 df2 = pd.merge(df,df1,on=["Symbol"]).groupby("Symbol")[["Date_x"]].max()
 df2.columns = ["Date"]   
    
 df3 = pd.merge(df,df2,on=["Symbol","Date"])
 df4 = df3[df3["NameSer"].str.contains(keyword)]  
 df4 = df4[["Symbol","Name","Share","Percent","Date","Type"]]   
 return df4.set_index("Symbol")


#fix bug การ merge fuzzy
def get_close(x,xcol_c):
    if(type(x)==str): 
     tmp = difflib.get_close_matches(x,xcol_c)
     if(len(tmp)>0):
        return tmp[0]
     else:
        return x

def ShareholdersHist(symbol):
  '''
    symbol : str
    คืนค่ารายชื่อผู้ถือหุ้นที่เทียบแต่ละวันของการปิดสมุดล่าสุด
  ''' 
  #โหลดข้อมูลพื้นฐานทั้งหมดมาก่อน
  df = pd.read_csv("ShareholdersTB.csv")
  df["Date"] = pd.to_datetime(df["Date"],format='%Y-%m-%d') 
    
  #หาวันที่ปิดสมุด
  symbol = symbol.upper()#"JMART"
  date_hist = df[df["Symbol"]==symbol].groupby("Date")  \
           [["Date","Type"]].min().sort_index(ascending=True)
  
  
  #merge data แต่ละของวันที่ปิดสมุดเข้าด้วยกัน
  hist_Name  = []
  hist_Share = []
  hist_Percent  = []
  rp = pd.DataFrame()

  for i in range(len(date_hist)):
    dt_label = date_hist.iloc[[i]]["Date"][[0]].dt.strftime('%Y-%m-%d')[0]
    
    hist_Name.append("Name-"+dt_label)  
    hist_Share.append("Share-"+dt_label)
    hist_Percent.append("Percent-"+dt_label) 
    
    df_tmp = df[(df["Symbol"]==symbol) & (df["Date"]==dt_label) ][["Name","Share","Percent"]]
    df_tmp.columns = ["Name-"+dt_label,"Share-"+dt_label,"Percent-"+dt_label]  
    df_tmp = df_tmp.sort_values("Share-"+dt_label,ascending=False) 
   
    #df_tmp['Name-'+dt_label] = df_tmp['Name-'+dt_label].str.strip()
    #df_tmp['Name-'+dt_label] = df_tmp['Name-'+dt_label].str.replace(' ','@')
    #df_tmp['Name-'+dt_label] = df_tmp['Name-'+dt_label].str.replace('  ','@')
    #df_tmp['Name-'+dt_label] = df_tmp['Name-'+dt_label].str.replace('@','')
    #print(df_tmp['Name-'+dt_label])

    if(i==0):
      rp = df_tmp
    else:   
      #return rp,df_tmp
      #k = rp[rp.columns[0]].map(lambda x:get_close(x,df_tmp[df_tmp.columns[0]]) )
      #print(k)
      #if(i==2):
      #  return rp,df_tmp
      rp[rp.columns[0]] = rp[rp.columns[0]].map(lambda x:get_close(x,df_tmp[df_tmp.columns[0]]) )
      rp = rp.merge(df_tmp, left_on=hist_Name[i-1], right_on=hist_Name[i],how='outer')  
    
  #เรียงข้อมูลล่าสุด
  tmp = rp.sort_values(rp.columns[-1],ascending=False)
  

  #สร้างรายชื่อผู้ถือหุ้นทั้งหมด
  holdername = []
  for i in range(len(tmp.columns)):
    if("Name" in tmp.columns[i]):
     if(len(holdername)==0): #first columns
       holdername = tmp[tmp.columns[i]].values.copy()
    
    col = tmp.columns[i]
    for j in range(len(tmp[tmp.columns[0]])):   
     newitem = tmp[[col]].iloc[j].values[0]
     if(type(newitem)==str):  
       holdername[j] = newitem   
    
  tmp["Name"] = holdername  
  
    
  #เอาเฉพาะชื่อ คอลัมน์ที่ต้องการ
  c = ["Name"]
  for i in zip(hist_Share,hist_Percent):
    c.append(i[0])
    c.append(i[1])

  #เรียง index ใหม่
  tmp['no'] = (list(range(1,len(tmp[c])+1)))
  tmp = tmp.set_index("no")

  #กำหนดรูปแบบ float_format
  pd.options.display.float_format = '{:,.2f}'.format 
    
  #คืนค่าทั้งหมด
  return tmp[c] 