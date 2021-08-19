import os
from os import path
import sys
# import DatabaseInfo
from .DatabaseInfo import *
# import sqltranslate
from .sqltranslate import *
import json
import pickle


"""for running sql translate on shell through command line"""

def getDBObj():
    cacheOutOfDate = False
    if(os.path.exists("DatabaseInfoCache")):
        if(os.path.exists("tableInfo.json") and os.path.getmtime("tableInfo.json")>os.path.getmtime("DatabaseInfoCache")):
            cacheOutOfDate = True
        if(os.path.exists("dataCategories.json") and os.path.getmtime("dataCategories.json")>os.path.getmtime("DatabaseInfoCache")):
            cacheOutOfDate = True
    else:
        cacheOutOfDate = True

    if(cacheOutOfDate):
        if(os.path.exists("tableInfo.json")):
            with open("tableInfo.json","r") as f:
                try:
                    tableInfo = json.load(f)
                except json.decoder.JSONDecodeError:
                    print("improper file format '{}".format("tableInfo.json"),file=sys.stderr)
                    sys.exit()
            dataCategories = None
            if(os.path.exists("dataCategories.json")):
                with open("dataCategories.json","r") as f:
                    try:
                        dataCategories = json.load(f)
                    except json.decoder.JSONDecodeError:
                        print("improper file format '{}".format("dataCategories.json"),file=sys.stderr)
                        sys.exit()
        else:
            print("database info file does not exist '{}'".format("tableInfo.json"),file=sys.stderr)
            sys.exit()
        dbInfo = DatabaseInfo(tableInfo,dataCategories)
        with open("DatabaseInfoCache","wb") as f:
            pickle.dump(dbInfo,f,protocol = pickle.HIGHEST_PROTOCOL)

    if(not cacheOutOfDate):
        with open("DatabaseInfoCache","rb") as f:
            f.seek(0)
            dbInfo = pickle.load(f)
    return dbInfo


def getParams(databaseInfo):
    number = re.compile('\\d+')
    params = {}
    temporalColumnChoices = [column for column in databaseInfo.columnChoices if any(table in databaseInfo.temporalDataTables for table in databaseInfo.columnChoices[column])]
    temporalDataCategories = [category for category in databaseInfo.dataCategories if any(column in list(databaseInfo.dataCategories[category].values())[0] for column in temporalColumnChoices)]
    nonTemporalColumnChoices = list(set(databaseInfo.columnChoices.keys()) - set(temporalColumnChoices))
    nonTemporalDataCategories = list(set(databaseInfo.dataCategories.keys()) - set(temporalDataCategories))

    temporal = True if input("temporal data? (y/n)")=="y" else False
    categorical = True if input("choose data from categories or columns? (cat/col)")=='cat' else False
    params['categorical']=categorical
    filters = {}
    if(temporal):
        if(categorical):
            print(temporalDataCategories)
            selected = input("choose from these categories, separate by commas ").strip().split(',')
            params['categories'] = selected
        else:
            print(temporalColumnChoices)
            selected = input("choose from columns, separate by commas ").strip().split(',')
            params['columnList'] = selected
            print("select filter type and values for each column. press enter for none:")
            for selection in selected:
                filterType = input(selection + ": filter by range, equality, or none (press enter)? (r/e)").strip()
                if(len(filterType)):
                    if(filterType=='r'):
                        values = input("enter lower and upper bound of range (inclusive) separated by comma: ").strip().split(',')
                    else:
                        values = input("enter values you want " + selection + " to be equal to separated by commas ").strip().split(',')
                    if(re.match(number,values[0])!=None):
                        values = [int(value) for value in values]
                    filters[selection] = {'type': 'range' if filterType=='r' else 'equal','values':values}
        
        aggregateBy = input("how frequently to aggregate data? (year/month/day) ").strip()
        aggregate = {}
        if(aggregateBy!="day"):
            print("select aggregation functions for each selection (avg/sum/med):")
            for selection in selected:
                method = input(selection + ": ")
                aggregate[selection] = method
        
        dateRange = input("select date range (lower and upper bound separated by comma, enter for none): ").strip()
        if(len(dateRange)):
            params['dateRange'] = dateRange.split(',')
        params['aggregateBy'] = aggregateBy
        params['aggregate'] = aggregate
    else:
        if(categorical):
            print(nonTemporalDataCategories)
            selected = input("choose from these categories, separate by commas ").strip().split(',')
            params['categories'] = selected
        else:
            print(nonTemporalColumnChoices)
            selected = input("choose from columns, separate by commas ").strip().split(',')
            params['columnList'] = selected
            for selection in selected:
                filterType = input(selection + ": filter by range, equality, or none (press enter)? (r/e)").strip()
                if(len(filterType)):
                    if(filterType=='r'):
                        values = input("enter lower and upper bound of range (inclusive) separated by comma: ").strip().split(',')
                    else:
                        values = input("enter values you want " + selection + " to be equal to separated by commas ").strip().split(',')
                    if(re.match(number,values[0])!=None):
                        values = [int(value) for value in values]
                    filter[selection] = values
        if(input("choose aggregate functions for selected? (y/n)")=="y"):
            aggregate = {}
            print(selection + ": select aggregation functions for each selection (avg/sum/med):")
            for selection in selected:
                method = input(selection + ": ").strip()
                if(len(method)):
                    aggregate[selection] = method
            if(len(aggregate)):
                params['aggregate'] = aggregate

    params['filters'] = filters
    return params
    

if __name__=='__main__':
    dbInfo = getDBObj()
    params = getParams(dbInfo)
    print(params)
    if('dateRange' in params):
        SQLTran = SQLTranslateTemporal(dbInfo,params)
    elif('aggregate' in params and len(params['aggregate'])):
        SQLTran = SQLTranslateAggregate(dbInfo,params)
    else:
        SQLTran = SQLTranslate(dbInfo,params)
    print(SQLTran)