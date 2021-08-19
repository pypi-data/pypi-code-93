#utility.py
import pandas as pd
import numpy as np
from IPython.display import HTML

def remove_comma(content):
      try:
       k = (content.replace(",",""))
       return(float(k))
      except:
       return (float(content))

def to_removecomma(self):
      col = (self.columns[0])
      data = pd.DataFrame({col:self.values.flatten()})
      return data[col].apply(remove_comma)



def make_meter(content,min_=0,max_=0):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = str(content*100)+"%"
    value =  np.round(content,2)      
    min_ = np.round(min_,2)
    max_ = np.round(max_,2)
    return f'<meter value="{value}" min={min_} max={max_}>{text}</meter>'
    #return f'<a target="_blank" href="{link}">{text}</a>'

# link is the column with hyperlinks
#data['commonsize_g'] = data['data'].apply(make_meter,args=(10,90))
#HTML(data.to_html(escape=False))

def to_meter(self,min_,max_):
    #self["m"] = self.apply(make_meter,args=(min_,max_))
    #print(self["m"])
    col = (self.columns[0])
    data = pd.DataFrame({col:self.values.flatten()})
    data[col+"_m"] = data[col].apply(make_meter,args=(min_,max_))
    return HTML(data.to_html(escape=False))#HTML(self.to_html(escape=False))


setattr(pd.core.frame.DataFrame, 'to_meter', to_meter)
setattr(pd.core.frame.DataFrame, 'to_removecomma', to_removecomma)