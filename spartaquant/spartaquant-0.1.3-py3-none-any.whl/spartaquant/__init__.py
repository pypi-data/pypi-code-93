import importlib
import sys
import os
import getpass

import requests
import inspect
import json
import base64
import cloudpickle
import sqlite3

global bInternalJupyterDesktop
global urlExternalApi
global userIdExternalApi

def decodeMainUrl(accessKey):
    return decodeFunc(decodeFunc(accessKey).split('__sq__')[0])

def decodeb64(thisStr):
    return base64.b64decode(thisStr).decode('utf-8')
    
def decodeFunc(thisStr):
    return decodeb64(decodeb64(decodeb64(thisStr)))

def getDBAuthFunc():
    try:
        currentDirPath = os.path.dirname(os.path.abspath(__file__))
        currentDirPath = os.path.dirname(currentDirPath)
        currentDirPath = os.path.dirname(currentDirPath)
        currentDirPath = os.path.dirname(currentDirPath)
        currentDirPath = os.path.dirname(currentDirPath)
        dbPath = currentDirPath+'\desktop.sqlite3'
        conn = sqlite3.connect(dbPath)  
        data  = conn.execute("SELECT * FROM config").fetchall()
        nbRow = len(data)
        conn.close()
        if nbRow > 0:
            return decodeMainUrl(data[-1][0]), base64.b64decode(data[-1][1]).decode('utf-8')
        else:
            return None
    except:
        return None

def getDBAuth():
    global bInternalJupyterDesktop
    if bInternalJupyterDesktop:
        return getDBAuthFunc()
    else:
        global urlExternalApi
        global userIdExternalApi
        return urlExternalApi, userIdExternalApi

def sendRequests(funcName, *args):
    try:
        URL_BASE, USER_ID = getDBAuth()
    except:
        print("Authentication failed. You may need to restart the kernel")
        return 
    thisUrl = URL_BASE+"jupyterAPI"
    newJson = dict()
    json_data = dict()
    argsSerialized = []
    for thisArg in args:
        data_bin = cloudpickle.dumps(thisArg)
        serializedObj = str(base64.b64encode(data_bin), "utf-8")
        argsSerialized.append(serializedObj)
    
    json_data['userId'] = 'POD_APP_'+str(base64.b64encode(str(USER_ID).encode()), 'utf-8')
    json_data['funcName'] = funcName
    json_data['args'] = argsSerialized
    newJson['jsonData'] = json.dumps(json_data)
    newJsonB = json.dumps(newJson)
    res = requests.post(thisUrl, data=newJsonB, verify=False)
    resJson = json.loads(res.text)
    if int(resJson['res']) == 1:
        return cloudpickle.loads(base64.b64decode(resJson['serializedObj']))
    else:
        print("Could not proceed the request")
        return {'res': -1}

def getDataDB():
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName)

def getData(thisData):
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName, thisData)

def getDataDates(thisDates, formula, bBusiness=True, formatDate='%Y%m%d'):
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName, thisDates, formula, bBusiness, formatDate)

def getDates(startDate, endDate, freq='b', bBusiness=True, orderBased='desc', formatDate='%Y%m%d'):
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName, startDate, endDate, freq, bBusiness, orderBased, formatDate)

def getFunctionsDB():
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName)

def getMTD():
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName)

def getQTD():
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName)

def getYTD():
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName)

def putExec(str2Eval, name):
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName, str2Eval, name)

def runFunction(functionName, *args):
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName, functionName, *args)

def createFunction(functionObj):
    functionSource = inspect.getsource(functionObj)
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName, functionSource)

def updateFunction(functionName2Create, functionObj):
    functionSource = inspect.getsource(functionObj)
    funcName = str(inspect.stack()[0][0].f_code.co_name)
    return sendRequests(funcName, functionName2Create, functionSource)

def testFunction(functionObj, *args):
    print("test function")
    print("args")
    print(len(args))
    print(args)
    try:
        functionObj.__call__(args)
    except Exception as e:
        print("Error")
        print(e)
    # functionSource = inspect.getsource(functionObj)
    # funcName = str(inspect.stack()[0][0].f_code.co_name)
    return "Function tested"

def printError():
    print("Authentication failed. Make sure you have entered the correct accessKey")

# **********************************************************************************************************************
bInternalJupyterDesktop = False
try:
    thisUrl, USER_ID = getDBAuthFunc()
    bInternalJupyterDesktop = True
except Exception as e:
    pass

if not bInternalJupyterDesktop:
    accessKey = getpass.getpass(prompt="Enter your access key")
    mainUrl = decodeMainUrl(accessKey)
    validateUrl = mainUrl+'validateMainUrlExternalApi'
    newJson = dict()
    json_data = dict()
    json_data['accessKey'] = accessKey
    newJson['jsonData'] = json.dumps(json_data)
    newJsonB = json.dumps(newJson)
    try:
        res = requests.post(validateUrl, data=newJsonB, verify=False)
        statusCode = res.status_code
        if int(statusCode) == 200:
            resJson = json.loads(res.text)
            res = resJson['res']
            if res == 1:
                urlExternalApi = mainUrl
                userIdExternalApi = decodeb64(decodeb64(resJson['userId']))
            else:
                printError()
        else:
            printError()
    except:
        printError()

# **********************************************************************************************************************