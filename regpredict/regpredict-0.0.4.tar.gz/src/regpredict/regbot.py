import os
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import joblib
import numpy as np
from pkg_resources import resource_filename
import fire


class Regbot:
  reg_model_path = resource_filename(__name__, 'finalized_model.h5') 
  model_scaler_path = resource_filename(__name__, 'logscaler.gz') 


  def __init__(self,*args):
  	self.model_scaler_path = model_scaler_path

  @classmethod
  def loadmodel(cls):
    loaded_model = joblib.load(open(f'{cls.reg_model_path}', 'rb'))
    return loaded_model


  @classmethod
  def prepareInput(cls,opening,closing,volume):
  	ask_ind = closing*volume/(opening + closing)
  	bid_ind = opening*volume/(opening + closing)
  	testdata = np.array([[ask_ind,bid_ind]])
  	scaler = joblib.load(f'{cls.model_scaler_path}')
  	testdata = scaler.transform(testdata)

  	return testdata


  @classmethod
  def buySignalGenerator(cls,opening,closing,volume,alpha):
    scalledInput = cls.prepareInput(opening,closing,volume)
    return (cls.loadmodel().predict_proba(scalledInput)[0:,1] > alpha).astype("int32")[0]
    
  @classmethod
  def sellSignalGenerator(cls,opening,closing,volume,alpha):
    scalledInput = cls.prepareInput(opening,closing,volume)
    return (cls.loadmodel().predict_proba(scalledInput)[0:,0] > alpha).astype("int32")[0]



def signal(opening,closing,volume,alpha,sig):
  if sig == 'buy':
    try:
      return Regbot.buySignalGenerator(opening,closing,volume,alpha)
    except Exception as e:
      print(e)
  elif sig == 'sell':
    try:
      return Regbot.sellSignalGenerator(opening,closing,volume,alpha)
    except Exception as e:
      print(e)
  else:
    return f'{sig} is not a valid entry!'


if __name__ == '__main__':
  fire.Fire(signal)
