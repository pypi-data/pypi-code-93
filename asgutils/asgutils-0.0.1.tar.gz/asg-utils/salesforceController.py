import json
import logging
import os
import urllib
from time import sleep

import pandas as pd
import requests
from requests.auth import HTTPProxyAuth

from secretsController import loadSecrets
from dateController import DateController


class SalesforceController:
    data = []

    def __init__(self, credentialsFilePath: str) -> None:
        self.secrets = loadSecrets(credentialsFilePath, key='salesforce')
        self.session = requests.Session()
        self.dates = DateController()

    def getListOfObjects(self, exportTo: str = None) -> dict:
        """This function is used to get all the Salesforce Object available for a specific instance (standard and custom).

        :param exportTo: Directory to export the JSON file, defaults to None
        :type exportTo: str, optional
        :return: The data retrieved from the API
        :rtype: dict
        """

        if os.environ.get('token') is None:
            self._getToken()

        endpoint = '/services/data/v52.0/sobjects/'
        headers = {'Authorization': os.environ['token']}
        url = self.secrets["SALESFORCE_BASE_URL"] + endpoint
        try:
            response = self.session.get(url, headers=headers)
            data = response.json()

            if not exportTo == None:
                dt = self.dates.get_now().format('YYYYMMDD')
                fileName = f"ObjectList_{dt}.json"
                exportPath = os.path.join(exportTo, fileName)
                with open(exportPath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            return data
        except:
            logging.error(f"Error fetching data from Salesforce API", exc_info=True)
            return {}

    def getObjectFields(self, objectType: str = 'Opportunity', exportTo: str = None) -> dict:
        """This function is used to get all the available fields (and details) for a given object.

        :param objectType: Name of the object which metadata to retrieve (accepted values : account, opportunity, mensualisation, action, avantage)
        :type objectType: str, optional, default to < Opportunity >
        :param exportTo: Directory to export the JSON file, defaults to None
        :type exportTo: str, optional
        :return: The data retrieved from the API
        :rtype: dict
        """
        data = self._getObjectMetadata(objectType=objectType)

        if not exportTo == None:
            dt = self.dates.get_now().format('YYYYMMDD')
            fileName = f"{objectType}_{dt}.json"
            exportPath = os.path.join(exportTo, fileName)
            with open(exportPath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        return data

    def getObjectById(self, objectId: str, objectType: str = 'Opportunity', exportTo: str = None) -> dict:
        """This function is used to get all the available the information for a given object ID.

        :param objectId: Salesforce ID for a specific entry
        :type objectType: str
        :param objectType: Name of the object which metadata to retrieve (accepted values : account, opportunity, mensualisation, action, avantage)
        :type objectType: str, optional, default to < Opportunity >
        :param exportTo: Directory to export the JSON file, defaults to None
        :type exportTo: str, optional
        :return: The data retrieved from the API
        :rtype: dict
        """
        data = self._getObjectMetadata(objectType=objectType, objectId=objectId)

        if not exportTo == None:
            dt = self.dates.get_now().format('YYYYMMDD')
            fileName = f"{objectType}_{objectId}_{dt}.json"
            exportPath = os.path.join(exportTo, fileName)
            with open(exportPath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        return data

    def sqlQuery(self, sql: str):
        """This function allows users to fetch data from the Salesforce REST API as a SOQL request.

        :param sql: SOQL request to send to the API
        :type sql: str
        :return: Pandas Dataframe
        :rtype: Pandas Dataframe
        """
        if os.environ.get('token') is None:
            self._getToken()

        base_url = f'{self.secrets["SALESFORCE_BASE_URL"]}/services/data/v43.0/queryAll?q='
        sql_encoded = urllib.parse.quote(sql)
        headers = {'Authorization': os.environ['token']}

        response = self.session.get(base_url + sql_encoded, headers=headers)
        rawdata = response.json()

        if rawdata.get('errorCode', '') != '':
            logging.error(f"Error querying Salesforce API with error : {rawdata['message']}", exc_info=True)

        for record in rawdata['records']:
            self.data.append(record)

        numOfRecords = rawdata['totalSize']
        goNext = True if rawdata['done'] == False else False
        nextUrl = ''
        if rawdata.get('nextRecordsUrl', '') != '':
            nextUrl = rawdata['nextRecordsUrl']

        while goNext:
            if goNext:
                print('NextURL : ', nextUrl)
                d = self._get_next_record(os.environ.get('instance_url') + nextUrl, headers=headers)
                goNext = d['hasNext']
                if goNext:
                    nextUrl = d['nextUrl']

        if numOfRecords > 0:
            if numOfRecords == len(self.data):
                df = pd.DataFrame(list(self.data))
                del df['attributes']
                self.data = []
                return df

    def _getObjectMetadata(self, objectType: str, objectId: str = None) -> dict:
        """This function is used to retrieve metadata information about a specific Salesforce Object (standard or custom).

        :param objectType: Name of the object which metadata to retrieve (accepted values : account, opportunity, mensualisation, action, avantage)
        :type objectType: str
        :param objectId: ID of the object which data is to be retrieved, defaults to None
        :type objectId: str, optional
        :return: Data retrieved from Salesforce API
        :rtype: dict
        """
        obj = {
            'account': 'Account',
            'opportunity': 'Opportunity',
            'mensualisation': 'Mensualisation_Contrat_ComeOnPlace__c',
            'action': 'Action_ComeOnPlace__c',
            'avantage': 'Opportunit_Element__c',
        }

        if os.environ.get('token') is None:
            self._getToken()

        baseUrl = '/services/data/v52.0/sobjects'
        headers = {'Authorization': os.environ['token']}
        try:
            endpoint = f'{baseUrl}/{obj[objectType.lower()]}/describe/' if objectId == None else f'{baseUrl}/{obj[objectType.lower()]}/{objectId}'
            url = self.secrets["SALESFORCE_BASE_URL"] + endpoint
            response = self.session.get(url, headers=headers)
            data = response.json()

            objData = []
            if objectId == None:
                for k in data.keys():
                    if k == 'fields':
                        for i in data[k]:
                            obj = {
                                'fieldNameAPI': i['name'],
                                'fieldName': i['label'],
                                'fieldType': i['type'],
                                'fieldPicklistValues': i['picklistValues'],
                                'fieldCalculated': i['calculated'],
                                'fieldCustom': i['custom'],
                                'fieldHidden': i['deprecatedAndHidden'],
                            }
                            objData.append(obj)
                return objData
            return data
        except:
            logging.error(f"Error fetching data from Salesforce API", exc_info=True)
            return {}

    def _get_next_record(self, nextRecordUrl: str, headers: dict):
        """Lorsqu'une requete retourne plus de 2.000 enregistrements, Salesforce créé un système de pagination. Cette fonction permet de lire chaque occurrence est d'en retourner les données.

        :param nextRecordUrl: URL de la page suivante
        :type nextRecordUrl: str
        :param headers: Headers à envoyer dans la requête
        :type headers: dict
        :return: Les retours d'informations fournies par l'API Salesforce
        :rtype: dict
        """
        response = self.session.get(nextRecordUrl, headers=headers)
        rawdata = response.json()
        for record in rawdata['records']:
            self.data.append(record)
        return {'hasNext': not rawdata['done'], 'nextUrl': '' if rawdata['done'] == True else rawdata['nextRecordsUrl']}

    def _getToken(self, useProxy: bool = True):
        """This function handle the loggin-in to Salesforce API.
            """
        tries = 1
        url = self.secrets['SALESFORCE_LOGIN_URL']
        if useProxy:
            proxies = {
                'http': f"http://{self.secrets['PROXY']}",
                'https': f"http://{self.secrets['PROXY']}",
            }
            authProxy = HTTPProxyAuth(self.secrets['PROXY_LOGIN'], self.secrets['PROXY_PASS'])
            self.session.proxies = proxies
            self.session.auth = authProxy

        payload = {
            'grant_type': 'password',
            'client_id': self.secrets['SALESFORCE_CLIENT_ID'],
            'client_secret': self.secrets['SALESFORCE_CLIENT_SECRET'],
            'username': self.secrets['SALESFORCE_USERNAME'],
            'password': f"{self.secrets['SALESFORCE_PASSWORD']}{self.secrets['SALESFORCE_SECURITY_TOKEN']}"
        }

        try:
            response = self.session.post(url, params=payload)
            data = response.json()
            if data.get('access_token', '') != '':
                os.environ['instance_url'] = data.get('instance_url', '')
                os.environ['token'] = f"{data.get('token_type', '')} {data.get('access_token', '')}"
                os.environ['token_signature'] = data.get('signature', '')
                os.environ['token_issued_at'] = data.get('issued_at', 0)
        except:
            if tries < 5:
                logging.warning(f'Error connecting to Salesforce API, retrying... (try #{tries})')
                sleep(3)
                tries = +1
                self._getToken()
            else:
                logging.error(f'Impossible to connect to Salesforce', exc_info=True)


if __name__ == '__main__':
    pass
