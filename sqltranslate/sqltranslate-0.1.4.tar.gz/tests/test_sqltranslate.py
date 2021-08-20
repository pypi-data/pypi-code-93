#!/usr/bin/env python

"""Tests for `sqltranslate` package."""

import pytest
from click.testing import CliRunner
from sqltranslate.sqltranslate import *
from sqltranslate import cli
from sqltranslate.DatabaseInfo import *
#from sqltranslate.__main__ import *

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string

HDDatabase = None

def test_databaseinfo_constructor():
    tableInfo = {
        'climatic':                                       
        {                                                 
            'temporal': True,
            'dateCol': 'day',                          
            'classifier': 'staid',
            'columns': ['tmmx','tmmn','pr','pet','vpd',
            'rmax','rmin','th','vs','day','staid']
        },
        'streamflow':                                     
        {                                                 
            'temporal': True,
            'dateCol': 'date',                             
            'classifier':'staid',
            'columns':['streamflow','date','staid']
        },
        'stations':                                       
        {
            'temporal': False,
            'classifier':'staid',
            'columns':['staid','lat','lng']
        }
    }
    dataCategories = {
        'Streamflow': {
           'streamflow':['streamflow']
        },
        'Temperature':{
               'climatic': ['tmmx','tmmn']
        },
        'Precipitation':{
            'climatic': ['pr']
        },
        'Humidity': {
            'climatic': ['pet', 'vpd','rmax','rmin']
        },
        'Wind':{
           'climatic': ['th','vs']
        }
    }
    global HDDatabase
    HDDatabase = DatabaseInfo(tableInfo,dataCategories)
    

# def test_databaseinfo_categories():
#     global HDDatabase
#     result = HDDatabase.getColumnsAndTablesFromCategories(['Temperature','Streamflow'])
    
# def test_databaseinfo_columnlist():
#     global HDDatabase
#     result = HDDatabase.getColumnsAndTablesFromColumnList(['tmmx','tmmn','streamflow','pet'])

# def test_databaseinfo_rowclassifiers():
#     global HDDatabase
#     result = HDDatabase.getRowClassifierColumns(['climatic','streamflow'])

# def test_databaseinfo_datetime():
#     global HDDatabase
#     result = HDDatabase.getDateTimeColumns(['climatic','streamflow','stations'])

def test_sqltranslate():
    global HDDatabase
    param1 = {
        'categorical':False,
        'columnList':['tmmx','tmmn','streamflow','pet'],
        'filters': {
            'tmmx': {
                'type':'range',
                'values': [150,160]
            },
            'staid': {
                'type':'equal',
                'values':[1,2]
            }
        }
    }
    SQLTran1 = SQLTranslate(HDDatabase,param1)
    param2 = {
        'categorical':True,
        'categories':["Temperature","Streamflow"],
    }
    SQLTran2 = SQLTranslate(HDDatabase,param2)
    param3 = {
        'categorical':False,
        'columnList':['lat','lng']
    }
    SQLTran3 = SQLTranslate(HDDatabase,param3)
    #print(SQLTran3)

def test_sqltranslate_agg():
    global HDDatabase
    param1 = {'categorical':False,
    'columnList':['tmmx','tmmn','streamflow','pet'],
    'aggregate':{'tmmx':'avg','tmmn':'avg','streamflow':'sum','pet':'avg'},
    'filters':{}
    }
    SQLTran1 = SQLTranslateAggregate(HDDatabase,param1)
    param2 =  { 
    'categorical':True,
    'categories':['Temperature','Streamflow','Humidity'],
    'aggregate':{'Temperature':'avg','Streamflow':'sum','Humidity':'avg'},
    'filters':{}
    }
    SQLTran2 = SQLTranslateAggregate(HDDatabase,param2)
    
def test_sqltranslate_tmp():
    global HDDatabase 
    param1 = {   'categorical':False,
    'columnList':['tmmx','tmmn','streamflow','pet'],
    'aggregate':{'tmmx':'avg','tmmn':'avg','streamflow':'sum','pet':'avg'},
    'dateRange':['01-01-2004','01-01-2006'],
    'aggregateBy':'year'
    }
    SQLTran1 = SQLTranslateTemporal(HDDatabase, param1)
    param2 = {   'categorical':False,
    'columnList':['tmmx','tmmn','streamflow','pet'],
    'aggregate':{'tmmx':'avg','tmmn':'avg','streamflow':'sum','pet':'avg'},
    'dateRange':['01-01-2004','01-01-2006'],
    'aggregateBy':'month'
    }
    SQLTran2 = SQLTranslateTemporal(HDDatabase, param2)
    param3 = {   'categorical':False,
    'columnList':['tmmx','tmmn','streamflow','pet'],
    'filters':{'staid': {'type':'equal', 'values':[1,2]}},
    'aggregate':{'tmmx':'avg','tmmn':'avg','streamflow':'sum','pet':'avg'},
    'dateRange':['01-01-2004','01-01-2006'],
    'aggregateBy':'day'
    }
    
    SQLTran3 = SQLTranslateTemporal(HDDatabase, param3)
    #print(SQLTran3)
    param4 = {   'categorical':True,
    'categories': ['Temperature','Streamflow'],
    'aggregate':{'Temperature':'avg','Streamflow':'sum'},
    'dateRange':['01-01-2004','01-01-2006'],
    'aggregateBy':'year'
    }
    SQLTran4 = SQLTranslateTemporal(HDDatabase, param4)
  
    param5 = {   'categorical':False,
    'columnList':['streamflow'],
    'filters':{'staid': {'type':'equal', 'values':[1,2]}},
    'aggregate':{'streamflow':'sum'},
    'dateRange':[],
    'aggregateBy':'month'
    }
    SQLTran5 = SQLTranslateTemporal(HDDatabase, param5)
    print(SQLTran5)
    param6 = {   'categorical':False,
    'columnList':['tmmx'],
    'filters':{'staid': {'type':'equal', 'values':[1,2]}},
    'aggregate':{'tmmx':'avg'},
    'dateRange':['01-01-2004','01-01-2006'],
    'aggregateBy':'month'
    }
    SQLTran6 = SQLTranslateTemporal(HDDatabase, param6)
    #print(SQLTran6)