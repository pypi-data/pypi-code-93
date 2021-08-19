import starfishX as sx
import pandas as pd

def findGrowth(self,Year=1,header=True):
     def f(Year):
       t = (((self)/(self.shift(Year).abs())))
       t = ((t**(1/Year))-1)*100
       t.columns = [t.columns[0]+" CAGR"+str(Year)+"(%)"]
       return t.T    
    
     if(type(Year)==int):
       if(header):
         return self.T.append(f(Year))
       return f(Year)

     if(type(Year)==list):
       p = pd.DataFrame() 
       for i in Year:
          m = f(i)  
          p = p.append(m)
            
       if(header):
         return self.T.append(p)     
       return p 

 

pd.options.display.float_format = '{:,.2f}'.format
setattr(pd.core.frame.DataFrame, 'findGrowth', findGrowth)
 
