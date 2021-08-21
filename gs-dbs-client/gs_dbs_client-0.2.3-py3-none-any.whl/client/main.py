import json
import yaml
import requests
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import pandas as pd



class GSDBS:
    def __init__(self):
        self.version = 0.1
        self.credentials = None
        self.accessToken = None
        self.dtablename = None
        self.superdtablename = None
        self.sriBuildInfo = list()
        self.data = pd.DataFrame()
        self.statement = None
        self.readCredentials()
        self.getToken()
        return

    def readCredentials(self):
        try:
            print(f'GS-DBMS Python client version: {self.version}')
            f = open("gscred.yml", "r")
            cred = f.read()
            f.close()
            self.credentials = yaml.safe_load(cred)['cred']

            if (('graphqlapiurl' not in self.credentials.keys())
                    or ('oauthurl' not in self.credentials.keys())
                    or ('apiurl' not in self.credentials.keys())
                    or ('user' not in self.credentials.keys())
                    or ('password' not in self.credentials.keys())
                    or ('client_id' not in self.credentials.keys())
                    or ('client_secret' not in self.credentials.keys())):
                print('Error in credentials')
                return
        except:
            print('Missing Credentials')
        return

    def getToken(self):
        data = {'grant_type': 'password', 'username': self.credentials['user'],
                'password': self.credentials['password']}
        access_token_response = requests.post(self.credentials['oauthurl'], data=data, verify=True,
                                              allow_redirects=False,
                                              auth=(self.credentials['client_id'], self.credentials['client_secret']))
        self.accessToken = json.loads(access_token_response.text)
        return

    def setDTableName(self, dTableName, superDTableName="DTABLE"):
        if dTableName is None or superDTableName is None:
            print("error: missing (super)dtablename data")
            self.dtablename = None
            self.superdtablename = None
            return -1;
        if (not (isinstance(dTableName, str) and isinstance(superDTableName, str))):
            print("error: missing (super)dtablename datatype \"str\"")
            self.dtablename = None
            self.superdtablename = None
            return -2;

        self.dtablename = dTableName
        self.superdtablename = superDTableName
        return 0

    def clearDTableName(self):
        self.dtablename = None
        self.superdtablename = None
        return 0

    def checkDTableName(self):
        if self.dtablename is None or self.superdtablename is None:
            print("error: missing (super)dtablename datatype \"str\"")
            return -1
        return 0

    def setSriBuildInfo(self, dataLinkList):
        if (dataLinkList is None):
            print("error: missing datalink")
            self.sriBuildInfo = None
            return -1;
        if not isinstance(dataLinkList, list):
            print("error: missing datatype \"list\"")
            self.sriBuildInfo = None
            return -2
        if (len(dataLinkList) == 0):
            print("error: missing data")
            self.sriBuildInfo = None
            return -3
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
            print("error: missing sri build info")
            return -1
        if (self.data is None):
            print("error: missing data")
            return -2
        for dl in self.sriBuildInfo:
            if dl not in self.data.columns:
                print("error: datalink " + dl + "not included in dataframe")
                return -3
        return 0

    def setData(self, data):
        if data is None:
            self.data = None
            print("error: missing data")
            return -1
        if not isinstance(data, pd.DataFrame):
            self.data == None
            print("error: missing datatype \"dataframe\"")
            return -2
        if len(data.index) == 0:
            self.data = None
            print("error: missing data rows")
            return -3
        self.data = data
        return 0

    def getGSDBSType(self, pyType):
        if pyType == "object":
            return "STRING"
        elif pyType == "int32":
            return "INTEGER"
        elif pyType == "int64":
            return "INTEGER"
        elif pyType == "float32":
            return "FLOAT"
        elif pyType == "float64":
            return "FLOAT"
        elif pyType == "bool":
            return "BOOLEAN"
        else:
            return None

    def getDataSchema(self):
        s = str()
        for col in self.data:
            gsDbsType = self.getGSDBSType(str(self.data.dtypes[col]))
            if gsDbsType == None:
                return -1
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
            print("error: missing data")
            return -1
        return 0

    def schemaCheck(self):
        # check mutation content
        if self.checkDTableName() != 0:
            return -1
        if self.checkData() != 0:
            return -2
        if self.checkSriBuildInfo() != 0:
            return -3

        # self.dtablename = "auf1"
        iQuery = self.schemaQuery(self.dtablename)
        if iQuery['__type'] == None:
            return 0  # dtable doesn't exist, do what you want

        schema = dict(iQuery['__type'])
        schemaName = schema["name"]
        schemaLinks = schema["fields"]
        # ... SRI DL müssen vorhanden sein und vom Typ her passen

        # print(type(schema))
        # print(schema.keys())
        # print(schema.values())
        # print(introspectionquery['__type'])
        #
        # colNameList = list(dataframe.columns)
        # for colName in colNameList:
        #     print(colName)
        #     print(dataframe[colName])
        #
        #     print(type(dataframe[colName]))
        #
        # # print(dataframe.dtypes)
        # # print(type(dataframe.dtypes))
        return 0

    def addDObject(self, dtablename, sribuildinfo, dataframe, superdtablename="DTABLE"):
        self.superdtablename = superdtablename
        rc = self.setDTableName(dtablename)
        if rc != 0: return rc

        rc = self.setSriBuildInfo(sribuildinfo)
        if rc != 0: return rc

        rc = self.setData(dataframe)
        if rc != 0: return rc

        rc = self.schemaCheck()
        if rc != 0: return rc

        rc = self.generateStatement()
        if rc != 0: return rc

        rc = self.executeStatement()
        return rc

    def generateStatement(self):
        i = 1
        self.statement = \
            f"""mutation {{\n\taddDTable(dtablename: "{self.dtablename}", \n\t\tsuperDTable: [{self.superdtablename}], \n\t\tsriBuildInfo: "{self.getSriBuildInfo()}", \n\t\tdataLinks: [\n{self.getDataSchema()}\n\t\t], \n\t\tdata: [\n{self.getData()}\t\t]\n\t)\n}}"""
        print(self.statement)

        return 0

    def executeStatement(self, statement=None):
        if statement == None:
            if self.statement == None:
                return -1
            query = gql(self.statement)
        else:
            query = gql(statement)

        api_call_headers = {'Authorization': 'Bearer ' + self.accessToken['access_token']}
        client = Client(
            transport=AIOHTTPTransport(url="https://glass-sphere-ai.de/gsgraphql",
                                       headers=api_call_headers),
            fetch_schema_from_transport=False)
        result = None
        try:
            result = client.execute(query)
        except:
            print("Error: statement execution")
        return result

    def schemaQuery(self, dtablename):
        self.statement = "{ __type(name: \"" + dtablename + "\") {name fields { name type { name kind } } } }"
        api_call_headers = {'Authorization': 'Bearer ' + self.accessToken['access_token']}
        client = Client(
            transport=AIOHTTPTransport(url="https://glass-sphere-ai.de/gsgraphql",
                                       headers=api_call_headers),
            fetch_schema_from_transport=False)
        query = gql(self.statement)
        schema = None
        try:
            schema = client.execute(query)
        except:
            print("Error: statement execution")

        return schema
