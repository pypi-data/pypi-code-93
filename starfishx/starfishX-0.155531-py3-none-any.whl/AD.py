try:
    #ลำดับมีผลพยายามโหลดที่ ใน folder ที่กำลัง Implement ก่อน
    #import config as con 
    from starfishX import config as con 
except:
    import starfishX.config as con

prefix = "starfishX."

if(con.__mode__=="debug"):
    prefix = ""

 

from sklearn.ensemble import IsolationForest
from sklearn import svm
from sklearn.covariance import EllipticEnvelope
#LocalOutlierFactor
from sklearn.neighbors import LocalOutlierFactor

from sklearn.preprocessing import StandardScaler

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum



from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

class anomalyDetectionAgloType(Enum):
 IsolationForests = "IsolationForests"
 OneClassSVM   = "OneClassSVM"
 GaussianDistribution = "GaussianDistribution"
 LocalOutlierFactor = "LocalOutlierFactor"

class anomalyDetectionDataType(Enum):
 priceChg = "priceChg"
 volume = "Volume"

def AnomalyDetection(dataset,contamination=0.01,Lastday=5,dataType="",algoType="",viewplot=False,viewlog=False,padding=False):
   ###############
   try:
    if(len(dataset.columns)!=2):
     print("dataset Not Match")
     return 0,0
   except:
     print("dataset Not Match")
     return 0,0

   outliers_fraction = contamination
   
   if(dataType==""):
      dataType = anomalyDetectionDataType.volume

   if(algoType==""):
      algoType = anomalyDetectionAgloType.IsolationForests

   if(not isinstance(dataType, anomalyDetectionDataType)):
    print("dataType Not Match")
    return 0,0

   if(not isinstance(algoType, anomalyDetectionAgloType)):
    print("algorithm Type Not Match")
    return 0,0
    
   alType = algoType.value
   dType = dataType.value
   
   if(dType=="priceChg"):
     dataset = dataset[[dataset.columns[0]]]
     dataset = dataset[[dataset.columns[0]]].pct_change().dropna()
   elif(dType=="Volume"):
     dataset = dataset[[dataset.columns[1]]]
     if(not any("Volume" in s for s in dataset.columns)):
      print("DataSet Not Contain Volume")
      return 0,0

   if(alType == "LocalOutlierFactor"):
     #LocalOutlierFactor
     # fit the model for novelty detection (novelty=True)
     n_neighbors = int(len(dataset)*.1)
     clf = LocalOutlierFactor(algorithm="auto",n_neighbors=n_neighbors, novelty=True, contamination=outliers_fraction)
     clf.fit(dataset)
     # DO NOT use predict, decision_function and score_samples on X_train as this
     # would give wrong results but only on new unseen data (not used in X_train),
     # e.g. X_test, X_outliers or the meshgrid
     #y_pred_test = clf.predict(X_test)
     dataset['anomaly'] = clf.predict(dataset)
     labelTitle = "(LocalOutlierFactor For Anomaly Detection)"

   if(alType == "IsolationForests"):
     rng = np.random.RandomState(42)
     data = dataset
     scaler = StandardScaler()
     np_scaled = scaler.fit_transform(data)
     data = pd.DataFrame(np_scaled)
     # train isolation forest
     model =  IsolationForest(behaviour='new',contamination=outliers_fraction,
                      random_state=rng)
     model.fit(data) 
     dataset['anomaly'] = model.predict(data)
     labelTitle = "(Isolation Forests For Anomaly Detection)"
   
   if(alType == "OneClassSVM"):
     data = dataset
     scaler = StandardScaler()
     np_scaled = scaler.fit_transform(data)
     data = pd.DataFrame(np_scaled)
     # train oneclassSVM 
     model = svm.OneClassSVM(nu=outliers_fraction, kernel="rbf", gamma=0.01)
     model.fit(data)
     dataset['anomaly'] =  model.predict(data)
     labelTitle = "(OneClassSVM For Anomaly Detection)"
     if(viewlog==True):
       print("OneClassSVM/rbf/gamma 0.01")

   if(alType == "GaussianDistribution"):
     envelope =  EllipticEnvelope(contamination = outliers_fraction,random_state=42) 
     X_train = dataset.values.reshape(-1,1)
     cov = envelope.fit(X_train)
      
     #k1 = cov.decision_function(X_train)
     dataset["anomaly"] = cov.predict(X_train)
     labelTitle = "(GaussianDistribution For Anomaly Detection)"

   if(viewplot==True): 
    symbol = dataset.columns[0].split(":")[0]
    fig = plt.figure(figsize=(16,8))
    fig.subplots_adjust(hspace=0.4, wspace=0.4)

    if(padding==False):
      ax = fig.add_subplot(1, 1, 1) #แถว #หลัก #รูปที่
      ax.title.set_text(symbol.upper()+' : '+dType+" "+labelTitle)
      ax = dataset[dataset.columns[0]].plot(figsize=(20,8))
      dataset[dataset.columns[0]][(dataset['anomaly']==-1)].plot(ax=ax,marker="*",ms=10,color='r',linewidth=0)
      return 0,0

    elif(padding==True):
      fig, ax = plt.subplots(figsize=(20,8)) #แถว #หลัก #รูปที่
      ax.title.set_text(symbol.upper()+' : '+dType+" "+labelTitle)
      ax.plot(dataset[dataset.columns[0]]) #figsize=(30,8),title=title
      ax.plot(dataset[dataset.columns[0]][(dataset['anomaly']==-1)],"*",ms=10,color="r",linewidth=0)
      plt.margins(0.01,0.05)  
      return 0,0


   #ตรวจ จำนวนวันหลังสุด พบสิ่งผิดปกติไหม
   result = list(map(lambda x: x==-1, dataset.tail(Lastday)['anomaly']))
   if(True in result):
      return dataset.columns[0].split(":")[0],dataset
   else:
      return "Normal",dataset



def viewAnomalyDetectionReportAllType(dataset,dataType,contamination=0.01,padding=False):
 fig = plt.figure(figsize=(24,12))
 fig.subplots_adjust(hspace=0.4, wspace=0.1)
 symbol = dataset.columns[0].split(":")[0]
 
 dType = dataType.value
 outliers_fraction = contamination

 ###############
 ax = fig.add_subplot(2, 2, 1)
 
 kAlgo = sx.anomalyDetectionAgloType.LocalOutlierFactor
 _,rp = sx.AnomalyDetection(dataset,dataType=dataType,algoType=kAlgo
                          ,Lastday=5,contamination=outliers_fraction,viewplot=False)
 
 labelTitle = "("+kAlgo.value+" For Anomaly Detection)"

 if(padding==False):                         
   ax.title.set_text(symbol.upper()+' : '+dType+" "+labelTitle)
   ax = rp[rp.columns[0]].plot(figsize=(24,12))
   rp[rp.columns[0]][(rp['anomaly']==-1)].plot(ax=ax,marker="*",ms=10,color='r',linewidth=0)
 
 if(padding==True):
   ax.title.set_text(symbol.upper()+' : '+dType+" "+labelTitle)
   ax.plot(rp[rp.columns[0]]) #figsize=(30,8),title=title
   ax.plot(rp[rp.columns[0]][(rp['anomaly']==-1)],"*",ms=10,color="r",linewidth=0)
   plt.margins(0.01,0.05)

 ###############
 ax = fig.add_subplot(2, 2, 2)

 kAlgo = sx.anomalyDetectionAgloType.IsolationForests
 _,rp = sx.AnomalyDetection(dataset,dataType=dataType,algoType=kAlgo
                          ,Lastday=5,contamination=outliers_fraction,viewplot=False)
 labelTitle = "("+kAlgo.value+" For Anomaly Detection)"

 if(padding==False):
   ax.title.set_text(symbol.upper()+' : '+dType+" "+labelTitle)
   ax = dataset[rp.columns[0]].plot()
   rp[rp.columns[0]][(rp['anomaly']==-1)].plot(ax=ax,marker="*",ms=10,color='r',linewidth=0)

 if(padding==True):
   ax.title.set_text(symbol.upper()+' : '+dType+" "+labelTitle)
   ax.plot(rp[rp.columns[0]]) #figsize=(30,8),title=title
   ax.plot(rp[rp.columns[0]][(rp['anomaly']==-1)],"*",ms=10,color="r",linewidth=0)
   plt.margins(0.01,0.05)
 ###############

 ###############
 ax = fig.add_subplot(2, 2, 3)

 kAlgo = sx.anomalyDetectionAgloType.GaussianDistribution
 _,rp = sx.AnomalyDetection(dataset,dataType=dataType,algoType=kAlgo
                          ,Lastday=5,contamination=outliers_fraction,viewplot=False)
 labelTitle = "("+kAlgo.value+" For Anomaly Detection)"

 if(padding==False):
   ax.title.set_text(symbol.upper()+' : '+dType+" "+labelTitle)
   ax = rp[rp.columns[0]].plot()
   rp[rp.columns[0]][(rp['anomaly']==-1)].plot(ax=ax,marker="*",ms=10,color='r',linewidth=0)

 if(padding==True):
   ax.title.set_text(symbol.upper()+' : '+dType+" "+labelTitle)
   ax.plot(rp[rp.columns[0]]) #figsize=(30,8),title=title
   ax.plot(rp[rp.columns[0]][(rp['anomaly']==-1)],"*",ms=10,color="r",linewidth=0)
   plt.margins(0.01,0.05)
 ###############

 ###############
 ax = fig.add_subplot(2, 2, 4)

 kAlgo = sx.anomalyDetectionAgloType.OneClassSVM
 _,rp = sx.AnomalyDetection(dataset,dataType=dataType,algoType=kAlgo
                          ,Lastday=5,contamination=outliers_fraction,viewplot=False)
 labelTitle = "("+kAlgo.value+" For Anomaly Detection)"

 if(padding==False):
   ax.title.set_text(symbol.upper()+' : '+dType+" "+labelTitle)
   ax = rp[rp.columns[0]].plot()
   rp[rp.columns[0]][(rp['anomaly']==-1)].plot(ax=ax,marker="*",ms=10,color='r',linewidth=0)

 if(padding==True):
   ax.title.set_text(symbol.upper()+' : '+dType+" "+labelTitle)
   ax.plot(rp[rp.columns[0]]) #figsize=(30,8),title=title
   ax.plot(rp[rp.columns[0]][(rp['anomaly']==-1)],"*",ms=10,color="r",linewidth=0)
   plt.margins(0.01,0.05)
 ###############