'''
Created on Oct 18, 2016

@author: fan
'''
import numpy as np

def find_isInfNan(self, dataToCheck, countSum=True):
    if(countSum == True):
        isNanCount = np.sum(np.isnan(dataToCheck))
        isInfCount = np.sum(np.isinf(dataToCheck))
        return isNanCount + isInfCount
    else:
        isNanCount = np.isnan(dataToCheck)
        isInfCount = np.isinf(dataToCheck)
        isNanInf = isNanCount | isInfCount
        return isNanInf
