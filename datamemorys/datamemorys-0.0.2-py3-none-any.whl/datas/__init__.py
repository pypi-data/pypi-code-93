from pandas import DataFrame
import pandas
import json
import requests
from datamemorys.core import SYCM_DATAS
class SYCMDataFrame(DataFrame):
    def __init__(self,sycm_tablename,loginnNickName):
        loginnNickName=loginnNickName.split(":")[0]
        j=requests.get(SYCM_DATAS[sycm_tablename].format(loginnNickName)).json()
        if j['code']!=0:            
            super().__init__()
        else:
            d=j['data']
            c=j['comments']            
            data=[]
            for x in d:
                v={}               
                for y in x.keys():                   
                    v[c[y]['cName']]=x[y]
                data.append(v)
            super().__init__(data)


            


    def Mysqlsqlstr(self,tablename):
        df=self.astype(str)
        kk=df.keys()
        d=[[df[y][x] for y in kk] for x in df.index]
        d=["('"+"','".join(x)+"')" for x in d]
        sql="insert into {}(`".format(tablename)+"`,`".join(kk)+"`) values"+ ",".join(d)
        return sql