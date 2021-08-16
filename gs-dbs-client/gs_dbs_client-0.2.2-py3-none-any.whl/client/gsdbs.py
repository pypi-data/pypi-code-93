import io

import os

import sys
import asyncio

import json
import yaml
import requests
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import pandas as pd


class GSDBS:
    def __init__(self, creadPath):
        self.version = "0.1.28"
        self.credentials = None
        self.accessToken = None
        self.dtablename = None
        self.superdtablename = None
        self.sriBuildInfo = list()
        self.data = pd.DataFrame()
        self.statement = None
        self.creadPath = creadPath
        self.readCredentials()
        self.getToken()
        self.CGSResponseCode = {}
        self.setupCGSResponseCodes()
        self.debugModus = False
        self.querybuffer = ''
        return

    def setDebugModus(self, debugModus):
        self.debugModus = debugModus

    def readCredentials(self):
        try:
            print(f'GS-DBMS Python client version: {self.version}')
            f = open(self.creadPath + "/gscred.yml", "r")
            cred = f.read()
            f.close()
            self.credentials = yaml.safe_load(cred)['cred']

            if (('graphqlapiurl' not in self.credentials.keys())
                    or ('oauthurl' not in self.credentials.keys())
                    or ('user' not in self.credentials.keys())
                    or ('password' not in self.credentials.keys())
                    or ('client_id' not in self.credentials.keys())
                    or ('client_secret' not in self.credentials.keys())):
                raise ValueError('error: credentials')
                return
        except Exception as e:
            print(e)
        return

    def getToken(self):
        try:
            data = {'grant_type': 'password', 'username': self.credentials['user'],
                    'password': self.credentials['password']}
            access_token_response = requests.post(self.credentials['oauthurl'], data=data, verify=True,
                                                  allow_redirects=False,
                                                  auth=(
                                                      self.credentials['client_id'], self.credentials['client_secret']))
            self.accessToken = json.loads(access_token_response.text)
            if 'error' in self.accessToken:
                raise ValueError('error:' + self.accessToken['error'])
        except Exception as e:
            print(e)
        return

    def setupCGSResponseCodes(self):
        self.CGSResponseCode['0'] = 'SUCCESS'
        self.CGSResponseCode['-1'] = 'MISSING (SUPER) DTABLE NAME'
        self.CGSResponseCode['-2'] = 'MISSING DATA LINK LIST'
        self.CGSResponseCode['-3'] = 'MISSING SRI BUILD INFO'
        self.CGSResponseCode['-4'] = 'MISSING DATA'
        self.CGSResponseCode['-5'] = 'MISSING DATALINK FOR SRI BUILD INFO in DATAFRAME'
        self.CGSResponseCode['-6'] = 'QUERY RESULT IS NULL'
        self.CGSResponseCode['-7'] = 'DATAFRAME DATATYPE DOESN\'T MATCHES DTABEL DATATYPE'
        self.CGSResponseCode['-8'] = 'EXECUTION FAILED'
        self.CGSResponseCode['-9'] = 'MISSING STATEMENT TO EXECUTE'
        self.CGSResponseCode['-10'] = 'STATEMENT ERROR'
        self.CGSResponseCode['-11'] = 'ERROR IN DATASCHEMA'
        self.CGSResponseCode['-12'] = 'TYPE ERROR'
        self.CGSResponseCode['-13'] = 'Missing DTABLE'
        self.CGSResponseCode['-14'] = 'Missing DTABLE SCHEMA'
        self.CGSResponseCode['-15'] = 'Missing QUERY'

    def setDTableName(self, dTableName, superDTableName="DTABLE"):
        if dTableName is None or superDTableName is None:
            self.dtablename = None
            self.superdtablename = None
            return -1;
        if (not (isinstance(dTableName, str) and isinstance(superDTableName, str))):
            self.dtablename = None
            self.superdtablename = None
            return -1;
        self.dtablename = dTableName
        self.superdtablename = superDTableName
        return 0

    def clearDTableName(self):
        self.dtablename = None
        self.superdtablename = None
        return 0

    def checkDTableName(self):
        if self.dtablename is None or self.superdtablename is None:
            return -1
        return 0

    def setSriBuildInfo(self, dataLinkList):
        if (dataLinkList is None):
            self.sriBuildInfo = None
            return -2;
        if not isinstance(dataLinkList, list):
            self.sriBuildInfo = None
            return -2
        if (len(dataLinkList) == 0):
            self.sriBuildInfo = None
            return -2
        self.sriBuildInfo = dataLinkList
        return 0

    def getSriBuildInfo(self):
        buidInfo = str()
        for dl in self.sriBuildInfo:
            if len(buidInfo) == 0:
                buidInfo += f'${{{dl}}}'
            else:
                buidInfo += f'-${{{dl}}}'
        return buidInfo

    def clearSriBuildInfo(self):
        self.sriBuildInfo = None
        return 0

    def checkSriBuildInfo(self):
        if (self.sriBuildInfo is None):
            return -3
        if (self.data is None):
            return -4
        for dl in self.sriBuildInfo:
            if dl not in self.data.columns:
                return -5
        return 0

    def setData(self, data):
        if data is None:
            self.data = None
            return -4
        if not isinstance(data, pd.DataFrame):
            self.data == None
            return -4
        if len(data.index) == 0:
            self.data = None
            return -4
        self.data = data
        return 0

    def getGSDBSType(self, pyType):
        if pyType == "object":
            return "STRING"
        elif pyType == "str":
            return "STRING"
        elif pyType == "int":
            return "INTEGER"
        elif pyType == "integer":
            return "INTEGER"
        elif pyType == "int32":
            return "INTEGER"
        elif pyType == "int64":
            return "LONG"
        elif pyType == "float":
            return "FLOAT"
        elif pyType == "float32":
            return "FLOAT"
        elif pyType == "float64":
            return "DOUBLE"
        elif pyType == "bool":
            return "BOOLEAN"
        elif pyType == "datetime":
            return "DATETIME"
        elif pyType == "datetime64":
            return "DATETIME"
        elif pyType == "datetime64[ns]":
            return "DATETIME"
        else:
            return None

    def getDataSchema(self):
        s = str()
        for col in self.data:
            gsDbsType = self.getGSDBSType(str(self.data.dtypes[col]))
            if gsDbsType == None:
                return -12
            s += f"""\t\t\t{{alias: "{col}", locale: DE, superPropertyURI: DYNAMIC_DATALINK, DataType: {gsDbsType}}},\n"""
        if len(s) > 0:
            s = s[:-2]
        return s

    def getData(self):
        # ["webcam2", "2020", "1337","10", "20", "100", "200", "0.5"]
        s = str()

        s += f"\t\t\t["
        for col in self.data:
            s += f""""{col}", """
        s = s[:-2]
        if len(self.data) > 0:
            s += "], \n"
        else:
            s += "]\n"

        for i in range(len(self.data)):
            s += f"\t\t\t["
            for col in self.data:
                s += f""""{str(self.data.loc[i, col])}", """
            s = s[:-2]
            if i < (len(self.data) - 1):
                s += "], \n"
            else:
                s += "]\n"
        return s

    def clearData(self):
        self.data = None
        return 0

    def checkData(self):
        if (self.data is None):
            return -4
        for col in self.data:
            gsDbsType = self.getGSDBSType(str(self.data.dtypes[col]))
            if gsDbsType == None:
                return -12
        return 0

    def generateMutationStatement(self):

        buildInfo = self.getSriBuildInfo()
        if buildInfo == None:
            return
        dataSchema = self.getDataSchema()
        if dataSchema == None:
            return

        self.statement = \
            f"""mutation {{\n\taddDTable(dtablename: "{self.dtablename}", \n\t\tsuperDTable: [{self.superdtablename}], \n\t\tsriBuildInfo: "{buildInfo}", \n\t\tdataLinks: [\n{dataSchema}\n\t\t], \n\t\tdata: [\n{self.getData()}\t\t]\n\t)\n}}"""
        return

    async def asyncSchemaCheck(self):
        # check mutation content
        rc = self.checkDTableName()
        if rc != 0: return rc
        rc = self.checkData()
        if rc != 0: return rc
        rc = self.checkSriBuildInfo()
        if rc != 0: return rc

        iQuery = await self.asyncSchemaQuery(self.dtablename)
        if iQuery == None: return -6

        if iQuery['__type'] == None: return 0  # dtable doesn't exist, do what you want
        rc = self.schemaLinkCheck(iQuery)
        return rc

    def schemaCheck(self):
        # check mutation content
        rc = self.checkDTableName()
        if rc != 0: return rc
        rc = self.checkData()
        if rc != 0: return rc
        rc = self.checkSriBuildInfo()
        if rc != 0: return rc

        iQuery = self.schemaQuery(self.dtablename)
        if iQuery == None: return -6

        if iQuery['__type'] == None: return 0  # dtable doesn't exist, do what you want
        rc = self.schemaLinkCheck(iQuery)
        return rc

    def schemaLinkCheck(self, iQuery):
        schema = dict(iQuery['__type'])
        schemaName = schema["name"]
        schemaLinks = schema["fields"]

        for col in self.data:
            dfType = self.getGSDBSType(str(self.data.dtypes[col]))
            linkType = self.getLinkType(schemaLinks, col)
            if dfType.upper() != linkType.upper():
                print('ERROR: dataframe datatype ', dfType, ' doesnt\' matches dTable datatype', linkType)
                return -7
        return 0

    def getLinkType(self, schemaLinks, linkName):
        if linkName == None:
            return -1
        for link in schemaLinks:
            if link['name'] == linkName:
                return link['type']['name']
        return None

    async def asyncAddDObject(self, dtablename, sribuildinfo, dataframe, superdtablename="DTABLE", schemaCheck=True):
        self.superdtablename = superdtablename
        rc = self.setDTableName(dtablename)
        if rc != 0: return rc
        rc = self.setSriBuildInfo(sribuildinfo)
        if rc != 0: return rc
        rc = self.setData(dataframe)
        if rc != 0: return rc

        if schemaCheck == True:
            rc = await self.asyncSchemaCheck()
            if rc != 0: return rc

        self.generateMutationStatement()
        if self.debugModus:
            print(self.statement)

        try:
            rc = await self.asyncExecuteStatement()
        except Exception as e:
            print(e)
            return e

        return rc

    def addDObject(self, dtablename, sribuildinfo, dataframe, superdtablename="DTABLE", schemaCheck=True):
        self.superdtablename = superdtablename
        rc = self.setDTableName(dtablename)
        if rc != 0: return rc
        rc = self.setSriBuildInfo(sribuildinfo)
        if rc != 0: return rc
        rc = self.setData(dataframe)
        if rc != 0: return rc

        if schemaCheck == True:
            rc = self.schemaCheck()
            if rc != 0: return rc

        self.generateMutationStatement()
        if self.debugModus:
            print(self.statement)

        try:
            rc = self.executeStatement()
        except Exception as e:
            print(e)
            return e

        return rc

    async def asyncSchemaQuery(self, dtablename):
        statement = "{ __type(name: \"" + dtablename + "\") {name fields { name type { name kind } } } }"

        try:
            result = await self.asyncExecuteStatement(statement)
        except Exception as e:
            print(e)
            return e

        return result

    def schemaQuery(self, dtablename):
        statement = "{ __type(name: \"" + dtablename + "\") {name fields { name type { name kind } } } }"

        try:
            result = self.executeStatement(statement)
        except Exception as e:
            print(e)
            return e

        return result

    async def asyncExecuteStatement(self, statement=None):
        if statement == None:
            if self.statement == None: return -9
            query = gql(self.statement)
        else:
            query = gql(statement)

        api_call_headers = {'Authorization': 'Bearer ' + self.accessToken['access_token']}
        client = Client(transport=AIOHTTPTransport(url=self.credentials['graphqlapiurl'],
                                                    headers=api_call_headers),
                                                    fetch_schema_from_transport=False)

        try:
            result = await client.execute_async(query)
        except Exception as e:
            print(e)
            return e

        return result

    def executeStatement(self, statement=None):
        if statement == None:
            if self.statement == None: return -9
            query = gql(self.statement)
        else:
            query = gql(statement)

        api_call_headers = {'Authorization': 'Bearer ' + self.accessToken['access_token']}
        client = Client(transport=AIOHTTPTransport(url=self.credentials['graphqlapiurl'],
                                                   headers=api_call_headers, timeout=3600),
                                                   fetch_schema_from_transport=False)

        try:
            result = client.execute(query)
        except Exception as e:
            print(e)
            return e

        return result

    async def asyncDropDTable(self, dtablename):
        statement = f"""mutation {{\n\tdropDTable(dtablename: {dtablename})\n}}"""
        result = await self.asyncExecuteStatement(statement)
        return result

    def dropDTable(self, dtablename):
        statement = f"""mutation {{\n\tdropDTable(dtablename: {dtablename})\n}}"""
        result = self.executeStatement(statement)
        return result

    def getDTableFullQuery(self, dtablename):
        try:
            self.querybuffer = 'query {\n'
            self.querybuffer += dtablename + '\n'
            self.getDTableQuery(dtablename)
            self.querybuffer += '}'
        except Exception as e:
            return e
        return self.querybuffer

    def getDTableQuery(self, dtablename):
        statement = f"""{{
          __type(name: \"{dtablename}\") {{
            name
            fields {{
              name
              type {{
                name
                kind
                ofType {{
                  name
                  kind
                }}
              }}
            }}
          }}
        }}"""
        result = self.executeStatement(statement)
        if result == None:
            raise ValueError('MISSING DTABLE')

        schema = dict(result['__type'])
        if schema == None:
           raise ValueError('MISSING DTABLE SCHEMA')

        schemaName = schema["name"]

        self.querybuffer += '{\n'
        for field in schema["fields"]:
            if field['name'] == 'episodes':
                continue
            if field['name'] == 'dynamic_snapshot_timestamp':
                continue
            if field['name'] == 'totalrowcount':
                continue
            self.querybuffer += field['name'] + "\n"
            if field['type'] != None:
                if field['type']['ofType'] != None:
                    self.getDTableQuery(field['type']['ofType']['name'])
        self.querybuffer += '}\n'
        return 0

    def getForeignDTableName(self, dtablename, foreignLinkName):
        statement = f"""{{
          __type(name: \"{dtablename}\") {{
            name
            fields {{
              name
              type {{
                name
                kind
                ofType {{
                  name
                  kind
                }}
              }}
            }}
          }}
        }}"""
        result = self.executeStatement(statement)
        if result == None:
            raise ValueError('MISSING DTABLE')
        schema = dict(result['__type'])
        if schema == None:
           raise ValueError('MISSING DTABLE SCHEMA')
        schemaName = schema["name"]

        for field in schema["fields"]:
            if field['name'] == foreignLinkName:
                if field['type'] != None:
                    if field['type']['ofType'] != None:
                        return field['type']['ofType']['name']
        return None

    def getFileFromCloud(self, filename):
        filename = filename.replace("/","$")
        storageURL = "https://glass-sphere-ai.de/storage/file/" + filename
        # storageURL = "http://localhost:8085/storage/file/" + filename
        headers = {'Authorization': 'Bearer ' + self.accessToken['access_token']}
        resp = requests.get(storageURL, headers=headers)
        buf = io.BytesIO(resp.content)
        return buf
