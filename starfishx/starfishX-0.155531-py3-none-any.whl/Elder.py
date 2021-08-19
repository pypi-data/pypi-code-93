try:
  import __init__ as sx #starfishX Production #__init__ debug Mode
except:
  import starfishX as sx

def elderSafezone(df,timeframe=10):
 df["DNPen"] = (df["Low"]-df["Low"].shift(-1)).shift(1)
 df.loc[df["DNPen"]<0,"DNPen"]=0
 df["DSUM"] = df["DNPen"].rolling(window=10).sum()
 df["DPENYN"] = 1
 df.loc[df["Low"]<df["Low"].shift(-1),"DPENYN"]=0
 df["DPENYN"] = df["DPENYN"].shift(1)
 df["DNNUM"] = df["DPENYN"].rolling(window=10).sum()
 df["DNAvg"] = (df["DSUM"]/df["DNNUM"]).round(2)
 df["shortStop"] = df["Low"]-(2*df["DNAvg"])
 df["shortStop"] = df["shortStop"].shift(1)
 df["DProtected"] = df["shortStop"].rolling(window=3).max()

 df["HNPen"] = df["High"]-df["High"].shift(1)
 df.loc[df["HNPen"]<0,"HNPen"]=0
 df["HPNUM"] = df["HNPen"].rolling(window=10).sum()
 df["HPENYN"]=1
 df.loc[df["High"]>df["High"].shift(-1),"HPENYN"]=0
 df["HPENYN"] = df["HPENYN"].shift(1)
 df["HNNUM"] = df["HPENYN"].rolling(window=10).sum()
 df["HNAvg"] = (df["HPNUM"]/df["HNNUM"]).round(2)
 df["LongStop"] = df["High"]+(2*df["HNAvg"])
 df["LongStop"] = df["LongStop"].shift(1)
 df["HProtected"] = df["LongStop"].rolling(window=3).min()

 return df[["DProtected","HProtected","Close"]]  