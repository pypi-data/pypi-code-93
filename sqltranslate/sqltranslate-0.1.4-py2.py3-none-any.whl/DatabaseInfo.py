import re
import numpy as np

class DatabaseTable:
    def __init__(self,name,params):
        self.name = name
        self.params = params
    
    def getColumns(self):
        return self.params['columns']

    def getRowClassifier(self):
        return self.params['classifier'].upper()
    
    def __hash__(self):
        return hash(name)
    
    def __eq__(self,other):
        return self.name == other.name

class DatabaseTemporalTable(DatabaseTable):
    def __init__(self,name,params):
        super().__init__(self,params)

    def getDateCol(self):
        return self.params['dateCol']

#this class keeps track of database metadata to make SQL queries built from the SQLTranslate module more specific
#also will reduce processing time for SQL Translate as it can access from a cache
class DatabaseInfo:
    def __init__(self, tableInfo, dataCategories=None):
        self.tables = {}
        for table in tableInfo:
            self.tables[table] = DatabaseTemporalTable(table,tableInfo[table]) if tableInfo[table]['temporal'] else DatabaseTable(table,tableInfo[table])
        self.dataCategories = dataCategories
        self.columnChoices = {}
        self.commonColumns = {}
        for table in tableInfo:
            self.generateColumnChoices(table)
        self.temporalDataTables = [table for table in tableInfo if tableInfo[table]['temporal']]

    def generateColumnChoices(self,table):
        for column in self.tables[table].getColumns():
            if(column in self.columnChoices):
                for otherTable in self.columnChoices[column]:
                    self.commonColumns[(table,otherTable)] = column
                self.columnChoices[column].append(table)
            else:
                self.columnChoices[column] = [table]

    def getColumnsAndTablesFromCategories(self,categories):
        columnList = []
        tableList = set()
        for category in categories:
            for table, items in self.dataCategories[category].items():
                tableList.add(table)
                columnList.extend(list(map(lambda columnName: table+"." + columnName.upper(), items)))
        tablePairs = [tablePair for tablePair in self.commonColumns.keys() if (tablePair[0] in tableList) and (tablePair[1] in tableList)]
        commonColumns = list(map(lambda tablePair: (tablePair[0] + "." + self.commonColumns[tablePair], tablePair[1] + "." + self.commonColumns[tablePair]), tablePairs))
        columnList = list(set(columnList))
        return {'columns': columnList,
                'tables': tableList,
                'commonColumns':commonColumns}

    def getColumnsAndTablesFromColumnList(self,columns):
        columnList = list(map(lambda columnName: self.columnChoices[columnName][0]+"."+columnName.upper(),columns))
        tableList = set([self.columnChoices[columnName][0] for columnName in columns])
        tablePairs = [tablePair for tablePair in self.commonColumns.keys() if (tablePair[0] in tableList) and (tablePair[1] in tableList)]
        commonColumns =  list(map(lambda tablePair: (tablePair[0] + "." + self.commonColumns[tablePair], tablePair[1] + "." + self.commonColumns[tablePair]), tablePairs))
        return {'columns': columnList,
                'tables': tableList,
                'commonColumns':commonColumns}

    def getCategories(self):
        return self.dataCategories

    def getRowClassifierColumns(self,tables):
        return list(map(lambda table: table+"."+ self.tables[table].getRowClassifier().upper(),tables))

    def getDateTimeColumns(self,tables):
        return list(map(lambda table: table+ "."+ self.tables[table].getDateCol().upper(),[t for t in self.tables if t in self.temporalDataTables and t in tables]))
    

