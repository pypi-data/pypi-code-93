"""Main module."""
from itertools import repeat, combinations
from .DatabaseInfo import *
from .__main__ import *



class SQLTranslate:
    def __init__(self,databaseInfo,params):
        self.params = params
        self.databaseInfo = databaseInfo
        self.selected = databaseInfo.getColumnsAndTablesFromCategories(self.params['categories']) if self.params['categorical'] else databaseInfo.getColumnsAndTablesFromColumnList(self.params['columnList'])
        self.selectedColumns = self.selected['columns']
        self.selectedTables = self.selected['tables']
        self.selectedColumns.extend(self.databaseInfo.getRowClassifierColumns(self.selectedTables))
        self.join = self.selected['commonColumns']
        self.filters = []
        if(not self.params['categorical'] and 'filters' in self.params):
            colSet = set()
            for i in range(len(self.selectedColumns)):
                currCol = self.selectedColumns[i].split('.')[1].lower()
                if(currCol in self.params['filters'] and not currCol in colSet):
                    colSet.add(currCol)
                    currFilt = self.params['filters'][currCol]
                    if(currFilt['type']=='range'):
                        self.filters.append(("(" + self.selectedColumns[i] + " BETWEEN " + "\"" + currFilt['values'][0] + "\" AND " + "\"" + currFilt['values'][1] + "\")") if isinstance(currFilt['values'][0],str) else self.filters.append("(" + self.selectedColumns[i] + " BETWEEN " +  str(currFilt['values'][0]) + " AND " + str(currFilt['values'][1]) + ")"))
                    else:
                        self.filters.extend(list(map(lambda filt: "(" + selectedColumns[i] + "=" + "\"" + filt + "\")", currFilt['values']))) if isinstance(currFilt['values'][0],str) else self.filters.extend(list(map(lambda filt: "(" + self.selectedColumns[i] + "=" +  str(filt) + ")", currFilt['values'])))

    def select(self):
        return "SELECT " + ', '.join(list(set(self.selectedColumns)))
    
    def fromTables(self):
        return "FROM " + ' inner join '.join(list(map(lambda t: "\"" + t.upper() + "\" as " + t, self.selectedTables)))
    
    def on(self):
        if(len(self.join)):
            return "on " + ' and '.join(list(map(lambda pair: pair[0] + "=" + pair[1],self.join)))
        return ""

    def where(self):
        if(len(self.filters)):
            return "WHERE " + ' and '.join([filter for filter in self.filters if filter!=None])
        return ""

    def command(self):
        return '\n'.join([string for string in [self.select(),self.fromTables(),self.on(),self.where()] if len(string)])

    def __str__(self):
        return self.command()

class SQLTranslateAggregate(SQLTranslate):
    def __init__(self,databaseInfo,params):
        super().__init__(databaseInfo,params)
        self.groupByCols = []
        self.aggregate = []
        if(self.params['categorical']):
            for category in self.params['categories']:
                categoryDict = self.databaseInfo.dataCategories[category]
                self.aggregate.extend([self.params['aggregate'][category]]*len(list(categoryDict.values())[0]))
            self.groupByCols.extend([self.selectedColumns[i] for i in range(len(self.aggregate),len(self.selectedColumns))])
            self.aggregate.extend([None]*(len(self.selectedColumns)-len(self.aggregate)))
        else:
            for column in self.selectedColumns:
                currCol = column.split('.')[1].lower()
                if(currCol in self.params['aggregate']):
                    self.aggregate.append(self.params['aggregate'][currCol])
                else:
                    self.aggregate.append(None)
                    self.groupByCols.append(column)
        self.selectedColumns = list(map(lambda i: self.aggregate[i].upper() + "(" + self.selectedColumns[i] + ")" if self.aggregate[i]!=None else self.selectedColumns[i],[i for i in range(len(self.selectedColumns))]))
    
    def groupBy(self):
        return "GROUP BY " + ", ".join(list(set(self.groupByCols) ))

    def command(self):
        return '\n'.join(string for string in [super().command(), self.groupBy()] if len(string))

class SQLTranslateTemporal(SQLTranslateAggregate):
    def __init__(self,databaseInfo,params):
        self.aggregateBy = params['aggregateBy']
        self.dateRange = list(map(lambda date: "\"" + date + "\"", params['dateRange'])) if self.aggregateBy == 'day' else list(map(lambda date: self.aggregateBy.upper() + "(\"" + date +"\")",params['dateRange']))
        super().__init__(databaseInfo,params)
    
    def select(self):
        dateCol = self.databaseInfo.getDateTimeColumns(self.selectedTables)[0]
        if(self.aggregateBy=='month'):
            self.selectedColumns.extend(["MONTH("+dateCol+")","YEAR("+dateCol+")"])
        elif(self.aggregateBy=='year'):
            self.selectedColumns.append("YEAR("+dateCol+")")
        else:
            self.selectedColumns.append(dateCol)
        return super().select()

    def on(self):
        dateCols = self.databaseInfo.getDateTimeColumns(self.selectedTables)
        datePairs = list(combinations(dateCols,2))
        self.join.extend(datePairs)
        return super().on()

    def where(self):
        dateCol = self.databaseInfo.getDateTimeColumns(self.selectedTables)[0]
        if('dateRange' in self.params and len(self.params['dateRange'])):
            self.filters.append(f"({dateCol} BETWEEN DATE(\"{self.params['dateRange'][0]}\") AND DATE(\"{self.params['dateRange'][1]}\"))")
        return super().where()

    def groupBy(self):
        dateCol = self.databaseInfo.getDateTimeColumns(self.selectedTables)[0]
        if(self.aggregateBy=='month'):
            self.groupByCols.extend(["MONTH("+dateCol+")","YEAR("+dateCol+")"])
        elif(self.aggregateBy=='year'):
            self.groupByCols.append("YEAR("+dateCol+")")
        else:
            self.groupByCols.append(dateCol)
        return super().groupBy()

def run(params):
    dbInfo = getDBObj()
    if('dateRange' in params):
        SQLTran = SQLTranslateTemporal(dbInfo,params)
    elif('aggregate' in params and len(params['aggregate'])):
        SQLTran = SQLTranslateAggregate(dbInfo,params)
    else:
        SQLTran = SQLTranslate(dbInfo,params)
    return SQLTran