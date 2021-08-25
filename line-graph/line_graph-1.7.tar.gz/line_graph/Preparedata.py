import pandas as pd
import numpy as np

class PrepareData:
    
    def __init__(self):
        
        self.df = []
        self.x = []
        self.y =[]
    
    def calculate_average(self):
            
        avg = np.mean(self.y)

        self.mean = avg

        return self.mean
    
    def percentage_change(self):
        
        self.y_pchange = self.y.pct_change().mul(100).fillna(0).round(3)
        
        self.y_pchange = ['{0:+g}'.format(x)+ '%' for x in self.y_pchange]
        
        return self.y_pchange
    
    def read_data_file(self, file_name):

        df = pd.read_csv(file_name, usecols=[0,1], thousands=',')

        self.df = df

        self.x = df.iloc[:,0]

        self.y = df.iloc[:,1]

        self.y_pchange = self.percentage_change()

        self.mean = self.calculate_average()

        return self.df, self.x, self.y, self.y_pchange, self.mean 