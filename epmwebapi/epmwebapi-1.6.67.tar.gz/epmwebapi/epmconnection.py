"""
Elipse Plant Manager - EPM Web API
Copyright (C) 2018 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
"""
import ctypes
import os

import numpy as np
import requests
import json

from .epmmodelobject import EpmModelObject, ObjectDependenciesException, InstanceNameDuplicatedException, \
    InvalidObjectNameException, InvalidSourceVariableException, InvalidObjectTypeException, \
    InvalidObjectPropertyException
from .epmproperty import EpmProperty
from .queryperiod import QueryPeriod
from .aggregatedetails import AggregateDetails
from .aggregatedetails import AggregateType
from .datavaluejson import DataValueJSON
from .annotationvaluejson import AnnotationValueJSON
from .itempathjson import ItemPathJSON
from .browsemodeljson import BrowseModelJSON
from .browseresultmodeljson import BrowseResultModelJSON
from .browseitemmodeljson import BrowseItemModelJSON
from .browseresultitemmodeljson import BrowseResultItemModelJSON
from .historyupdatedatamodeljson import HistoryUpdateDataModelJSON
from .historyupdatedataitemmodeljson import HistoryUpdateDataItemModelJSON
from .readitemmodeljson import ReadItemModelJSON
from .readmodeljson import ReadModelJSON
from .readresultitemmodeljson import ReadResultItemModelJSON
from .readresultmodeljson import ReadResultModelJSON
from .epmdataobject import EpmDataObject, EpmDataObjectPropertyNames, EpmDataObjectAttributeIds, getDiscreteValue, \
    getDomainValue
from .epmobject import EpmObject
from .basicvariable import BasicVariable, BasicVariableAlreadyExistsException, BasicVariableInvalidNameException, \
    StorageSetDoesNotExistException, InterfaceDoesNotExistException
from .writeitemmodeljson import WriteItemModelJSON
from .writemodeljson import WriteModelJSON
from .itempathandcontinuationpointjson import ItemPathAndContinuationPointJSON
from .historyrawmodeljson import HistoryRawModelJSON
from .numpyextras import NumpyExtras
from .historyprocessedmodeljson import HistoryProcessedModelJSON
from .authorizationservice import AuthorizationService
from .querymodeljson import QueryModelJSON
from .queryresultmask import QueryResultMask
from .queryresultitemmodeljson import QueryResultItemModelJSON
from .diagnosticmodeljson import DiagnosticModelJSON
from .dataobjectattributes import DataObjectAttributes
from .epmnodeids import EpmNodeIds
from .nodeclassmask import NodeClassMask
from .dataobjectsfilter import DataObjectsFilterType, DataObjectsFilter
from .domainfilter import DomainFilter
from .nodeattributes import NodeAttributes
from .portalresources import PortalResources
from .processorresources import ProcessorResources
from .historyupdatetype import HistoryUpdateType
from .customtypedefinition import CustomTypeDefinition, SimpleProperty, ObjectProperty, \
    CustomTypeAlreadyExistsException, InvalidCustomTypeNameException, CustomTypeDependenciesException, \
    InvalidIconException, DuplicatedPropertiesNamesException, DuplicatedPropertiesTypeException, \
    InvalidPropertyNameException, MissingPropertyNameException, InvalidPropertyTypeException
from .datasetconfig import DatasetConfig, DatasetConfigLocal, DatasetConfigServer
from enum import Enum
import collections


class ImportMode(Enum):
    OnlyAdd = 0
    OnlyEdit = 1
    AddAndEdit = 2


class EpmConnection(object):
    """description of class"""

    def __init__(self, authServer = None, webApi = None, userName = None, password = None, clientId='EpmRestApiClient',
                 programId='B39C3503-C374-3227-83FE-EEA7A9BD1FDC', connectionContext=None):
        if connectionContext != None:
          self._webApi = connectionContext.getWebApi()
          self._authorizationService = AuthorizationService(connectionContext)
        else:
          self._webApi = webApi
          from .epmconnectioncontext import EpmConnectionContext
          self._authorizationService = AuthorizationService(EpmConnectionContext(authServer, webApi, clientId, programId, userName, password))

    # Public Methods
    def getPortalResourcesManager(self):
        return PortalResources(self._authorizationService, self._webApi)

    def getProcessorResourcesManager(self):
        return ProcessorResources(self._authorizationService, self._webApi)

    def getDataObjects(self, names=None, attributes=DataObjectAttributes.Unspecified):
        if names == None:
            return self._getAllDataObjects(attributes, EpmNodeIds.HasComponent)
        else:
            return self._getDataObjects(names, attributes)

    def getBasicVariables(self, names=None, attributes=DataObjectAttributes.Unspecified):
        if names == None:
            return self._getAllDataObjects(attributes, EpmNodeIds.HasTags, '/1:BasicVariables')
        else:
            return self._getDataObjects(names, attributes, '/1:BasicVariables')

    def getExpressionVariables(self, names=None, attributes=DataObjectAttributes.Unspecified):
        if names == None:
            return self._getAllDataObjects(attributes, EpmNodeIds.HasComponent, '/1:ExpressionVariables')
        else:
            return self._getDataObjects(names, attributes, '/1:ExpressionVariables')

    def createBasicVariable(self, name, description=None, tagType=None, realTimeEnabled=None, deadBandFilter=None,
                            deadBandUnit=None,
                            eu=None, lowLimit=None, highLimit=None, scaleEnable=None, inputLowLimit=None,
                            inputHighLimit=None, clamping=None,
                            domain=None, interface=None, ioTagAddress=None, processingEnabled=None, isRecording=None,
                            isCompressing=None,
                            storeMillisecondsEnabled=None, storageSet=None):

        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/BV'
        header = {'Authorization': 'Bearer {}'.format(token)}

        discrete = getDiscreteValue(domain)

        jsonRequest = {'Items': [{'name': name, 'description': description if description != None else '',
                                  'tagType': tagType, 'realTimeEnabled': realTimeEnabled,
                                  'eu': eu, 'lowLimit': lowLimit, 'highLimit': highLimit, 'scaleEnable': scaleEnable,
                                  'inputLowLimit': inputLowLimit, 'inputHighLimit': inputHighLimit,
                                  'rangeClamping': clamping,
                                  'discrete': discrete, 'interface': interface, 'ioTagAddress': ioTagAddress,
                                  'processingEnabled': processingEnabled,
                                  'isRecording': isRecording, 'isCompressing': isCompressing,
                                  'storeMillisecondsEnabled': storeMillisecondsEnabled,
                                  'storageSet': storageSet, 'deadBandFilter': deadBandFilter,
                                  'deadBandUnit': deadBandUnit}]}

        response = requests.post(url, headers=header, json=jsonRequest, verify=False)
        if response.status_code != 200:
            if response.status_code == 400:
                if 'EpmErrorTagAlreadyExists' in response.text:
                    raise BasicVariableAlreadyExistsException('BasicVariable ' + name + ' already exists')
                if 'Invalid format Name' in response.text:
                    raise BasicVariableInvalidNameException('BasicVariable ' + name + ' has an invalid format')
                if 'Invalid StorageSet name' in response.text:
                    raise StorageSetDoesNotExistException('StorageSet ' + str(storageSet) + ' does not exists')
                if 'Invalid Interface name' in response.text:
                    raise InterfaceDoesNotExistException('Interface path ' + str(interface) + ' does not exists')
            raise Exception(
                "CreateBasicVariable call error + '" + str(response.status_code) + "'. Reason: " + response.reason)

        json_result = json.loads(response.text)

        bvInfo = json_result['items'][0]

        identity = 'ns=1;i=' + str(bvInfo['id'])

        bv = BasicVariable(self, identity, name=bvInfo['name'], description=bvInfo['description'],
                           deadBandFilter=bvInfo['deadBandFilter'], deadBandUnit=bvInfo['deadBandUnit'],
                           eu=bvInfo['eu'], lowLimit=bvInfo['lowLimit'], highLimit=bvInfo['highLimit'],
                           tagType=bvInfo['tagType'], realTimeEnabled=bvInfo['realTimeEnabled'],
                           scaleEnable=bvInfo['scaleEnable'],
                           inputLowLimit=bvInfo['inputLowLimit'], inputHighLimit=bvInfo['inputHighLimit'],
                           clamping=bvInfo['rangeClamping'],
                           domain=getDomainValue(bvInfo['discrete']), interface=bvInfo['interface'],
                           ioTagAddress=bvInfo['ioTagAddress'],
                           processingEnabled=bvInfo['processingEnabled'], isRecording=bvInfo['isRecording'],
                           isCompressing=bvInfo['isCompressing'],
                           storeMillisecondsEnabled=bvInfo['storeMillisecondsEnabled'], storageSet=bvInfo['storageSet'])

        return bv

    def updateBasicVariable(self, name, newName=None, description=None, tagType=None, realTimeEnabled=None,
                            deadBandFilter=None, deadBandUnit=None,
                            eu=None, lowLimit=None, highLimit=None, scaleEnable=None, inputLowLimit=None,
                            inputHighLimit=None, clamping=None,
                            domain=None, interface=None, ioTagAddress=None, processingEnabled=None, isRecording=None,
                            isCompressing=None,
                            storeMillisecondsEnabled=None, storageSet=None):

        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/BV'
        header = {'Authorization': 'Bearer {}'.format(token)}

        discrete = getDiscreteValue(domain)

        jsonRequest = {'Items': [{'name': name, 'newName': newName, 'description': description,
                                  'tagType': tagType, 'realTimeEnabled': realTimeEnabled,
                                  'eu': eu, 'lowLimit': lowLimit, 'highLimit': highLimit, 'scaleEnable': scaleEnable,
                                  'inputLowLimit': inputLowLimit, 'inputHighLimit': inputHighLimit,
                                  'rangeClamping': clamping,
                                  'discrete': discrete, 'interface': interface, 'ioTagAddress': ioTagAddress,
                                  'processingEnabled': processingEnabled,
                                  'isRecording': isRecording, 'isCompressing': isCompressing,
                                  'storeMillisecondsEnabled': storeMillisecondsEnabled,
                                  'storageSet': storageSet, 'deadBandFilter': deadBandFilter,
                                  'deadBandUnit': deadBandUnit}]}

        response = requests.patch(url, headers=header, json=jsonRequest, verify=False)
        if response.status_code != 200:
            if response.status_code == 400:
                if 'EpmErrorTagAlreadyExists' in response.text:
                    raise BasicVariableAlreadyExistsException('BasicVariable ' + name + ' already exists')
                if 'Invalid format Name' in response.text:
                    raise BasicVariableInvalidNameException('BasicVariable ' + name + ' has an invalid format')
                if 'Invalid StorageSet name' in response.text:
                    raise StorageSetDoesNotExistException('StorageSet ' + str(storageSet) + ' does not exists')
                if 'Invalid Interface name' in response.text:
                    raise InterfaceDoesNotExistException('Interface path ' + str(interface) + ' does not exists')
            raise Exception(
                "UpdateBasicVariable call error + '" + str(response.status_code) + "'. Reason: " + response.reason)

    def deleteBasicVariable(self, names):

        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/BV'
        header = {'Authorization': 'Bearer {}'.format(token)}

        jsonRequest = {'Items': names}

        response = requests.delete(url, headers=header, json=jsonRequest, verify=False)
        if response.status_code != 200:
            raise Exception(
                "DeleteBasicVariable call error + '" + str(response.status_code) + "'. Reason: " + response.reason)

        json_result = json.loads(response.text)

        # [ItemPathJSON('OPCUA.NodeId', '', item['identity']) for item in json_result['items']]
        if 'diagnostics' in json_result:
            return [True if item == 1 else False for item in json_result['diagnostics']]
        else:
            return True

    def getAllCustomTypes(self):
        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/usertypes'
        header = {'Authorization': 'Bearer {}'.format(token)}

        response = requests.get(url, headers=header, verify=False)

        if response.status_code != 200:
            raise Exception("GetAllCustomTypes call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        types_list = json.loads(response.text)

        return types_list

    def getCustomType(self, name):
        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/usertypes/' + name
        header = {'Authorization': 'Bearer {}'.format(token)}

        response = requests.get(url, headers=header, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['diagnostic']['code']
            if responseCode != 0:
                if responseCode == 2158690304:
                    raise InvalidCustomTypeNameException('Custom type ' + name + ' not found')
                elif responseCode == 2151022592:
                    raise BadArgumentException('Cannot parse path with name ' + name)
                else:
                    raise Exception(response.json()['diagnostic']['message'])
        else:
            raise Exception("GetCustomType call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        json_response = json.loads(response.text)['item']

        icon = json_response["icon"]

        aliasProperties = []
        for dic in json_response["aliasProperties"]:
            aliasProperties.append(dic.get('name'))

        simpleProperties = []
        for dic in json_response["simpleProperties"]:
            simple = SimpleProperty(dic.get('name'), dic.get('initialValue'))
            simpleProperties.append(simple)

        objectProperties = []
        for dic in json_response["objectProperties"]:
            obj = ObjectProperty(dic.get('name'), dic.get('type'))
            objectProperties.append(obj)

        placeHolderTypes = []
        for dic in json_response["placeHolderProperties"]:
            placeHolder = dic.get('type')
            placeHolderTypes.append(placeHolder)

        return CustomTypeDefinition(self, name, icon, aliasProperties, simpleProperties, objectProperties,
                                    placeHolderTypes)

    def createCustomType(self, name, propertiesFilePath=None):
        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/usertypes'
        header = {'Authorization': 'Bearer {}'.format(token)}
        customTypes = self.getAllCustomTypes()

        if propertiesFilePath is None:
            jsonRequest = {'name': name, 'icon': "", 'aliasProperties': [],
                           'simpleProperties': [], 'objectProperties': [],
                           'placeHolderProperties': []}
        else:
            with open(propertiesFilePath) as json_file:
                properties = json.load(json_file)

            for obj in properties['objectProperties']:
                if obj["type"] not in customTypes:
                    raise CustomTypeDependenciesException("Object properties dependencies does not exist")

            for placeHolder in properties['placeHolderProperties']:
                if placeHolder["type"] not in customTypes:
                    raise CustomTypeDependenciesException("PlaceHolder dependencies does not exist")

            jsonRequest = {'name': name, 'icon': properties['icon'],
                           'aliasProperties': properties['aliasProperties'],
                           'simpleProperties': properties['simpleProperties'],
                           'objectProperties': properties['objectProperties'],
                           'placeHolderProperties': properties['placeHolderProperties']}

        response = requests.post(url, headers=header, json=jsonRequest, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2153840640:
                    if 'There is already a type with the same name!' in response.json()["message"]:
                        raise CustomTypeAlreadyExistsException('Custom type ' + name + ' already exists')
                    else:
                        raise DuplicatedPropertiesNamesException('Duplicated properties names provided')
                elif responseCode == 2153775104:
                    if 'BadBrowseNameInvalid' in response.json()["message"]:
                        raise InvalidCustomTypeNameException('Invalid custom type name')
                    else:
                        raise InvalidPropertyNameException('Invalid property format name provided')
                elif responseCode == 2152923136:
                    raise DuplicatedPropertiesTypeException('Duplicated PlaceHolder types provided')
                elif responseCode == 2147549184:
                    raise MissingPropertyNameException('Missing property name')
                elif responseCode == 2160590848:
                    if 'PlaceHolder' in response.json()["message"]:
                        raise InvalidPropertyTypeException('Invalid or missing PlaceHolder property type')
                    else:
                        raise InvalidPropertyTypeException('Invalid or missing object property type')
                elif responseCode == 2158690304:
                    raise InvalidIconException('Invalid icon string')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("CreateCustomType call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        return self.getCustomType(name)

    def updateCustomType(self, propertiesJson):
        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/usertypes'
        header = {'Authorization': 'Bearer {}'.format(token)}

        jsonRequest = propertiesJson

        response = requests.patch(url, headers=header, json=jsonRequest, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2158690304:
                    if 'Unknown type name' in response.json()["message"]:
                        raise InvalidCustomTypeNameException('Custom type ' + jsonRequest['name'] + ' not found')
                    else:
                        raise InvalidIconException('Invalid icon string')
                elif responseCode == 2153840640:
                    raise DuplicatedPropertiesNamesException('Duplicated properties names provided')
                elif responseCode == 2153775104:
                    raise InvalidPropertyNameException('Invalid property format name provided')
                elif responseCode == 2152923136:
                    raise DuplicatedPropertiesTypeException('Duplicated PlaceHolder types provided')
                elif responseCode == 2147549184:
                    raise MissingPropertyNameException('Missing property name')
                elif responseCode == 2160590848:
                    if 'PlaceHolder' in response.json()["message"]:
                        raise InvalidPropertyTypeException('Invalid or missing PlaceHolder property type')
                    else:
                        raise InvalidPropertyTypeException('Invalid or missing object property type')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("UpdateCustomType call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

    def deleteCustomType(self, name):
        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/usertypes/' + name
        header = {'Authorization': 'Bearer {}'.format(token)}

        response = requests.delete(url, headers=header, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2158690304:
                    raise InvalidCustomTypeNameException('Custom type ' + name + ' not found')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("DeleteCustomType call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

    def exportCustomTypes(self, fileName, pathName=None):
        typesJson = []
        typesNames = self.getAllCustomTypes()
        if typesNames is not None:
            for typeName in typesNames:
                customType = self.getCustomType(typeName)
                typesJson.append(customType.exportJSON())

        jsonText = {'Items': typesJson}

        if pathName is None:
            pathName = os.getcwd()
        fileName = fileName + ".json"
        with open(os.path.join(pathName, fileName), 'w') as outfile:
            json.dump(jsonText, outfile)

    def importCustomTypes(self, filePath, importMode=ImportMode.OnlyAdd):
        if importMode != ImportMode.OnlyAdd:
            raise BadArgumentException("Invalid ImportMode argument")

        with open(filePath) as json_file:
            jsonItems = json.load(json_file)

        customTypes = jsonItems['Items']
        customTypesPrev = self.getAllCustomTypes()

        for customType in customTypes:
            if customType['name'] in customTypesPrev:
                raise CustomTypeDependenciesException("Custom types dependencies already exists")

            for obj in customType['objectProperties']:
                if obj['type'] in customTypesPrev:
                    raise CustomTypeDependenciesException("Custom types dependencies already exists")

            for placeHolder in customType['placeHolderProperties']:
                if placeHolder['type'] in customTypesPrev:
                    raise CustomTypeDependenciesException("Custom types dependencies already exists")

        customTypesDefs = []
        itemsObjectProperties = []
        itemsPlaceHolderProperties = []
        for customType in customTypes:
            self.createCustomType(customType['name'])
            customTypeDef = CustomTypeDefinition(self, name=customType['name'], icon=customType['icon'])

            for aliasProperty in customType['aliasProperties']:
                customTypeDef.addAliasProperty(aliasProperty['name'])

            for simpleProperty in customType['simpleProperties']:
                customTypeDef.addSimpleProperty(simpleProperty['name'], simpleProperty['initialValue'])

            itemsObjectProperties.append(customType['objectProperties'])

            itemsPlaceHolderProperties.append(customType['placeHolderProperties'])

            customTypesDefs.append(customTypeDef)

        for customTypeDef in customTypesDefs:
            customTypeDef.save()

        for (customTypeDef, objectProperties, placeHolderProperties) in zip(customTypesDefs, itemsObjectProperties,
                                                                            itemsPlaceHolderProperties):
            for objectProperty in objectProperties:
                customTypeDef.addObjectProperty(objectProperty['name'], objectProperty['type'])

            for placeHolderType in placeHolderProperties:
                customTypeDef.addPlaceHolderType(placeHolderType['type'])

        for customTypeDef in customTypesDefs:
            customTypeDef.save()

        # Pode ocorrer ordem diferente de processamento no Server

    def filterDataObjects(self, filter=None, attributes=DataObjectAttributes.Unspecified):

        if filter == None:
            filter = DataObjectsFilter()

        typesFilter = []
        if DataObjectsFilterType.BasicVariable in filter.type:
            typesFilter.append(ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.BasicVariableType.value))
        if DataObjectsFilterType.ExpressionVariable in filter.type:
            typesFilter.append(ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.ExpressionVariableType.value))

        dataObjects = self._query(filter.name, filter.description, filter.eu, filter.domain, typesFilter)

        self._fillDataObjectsAttributes(list(dataObjects.values()), attributes)

        return dataObjects

    def getObjects(self, objectsPaths):
        paths = []
        browsePaths = []

        if type(objectsPaths) is str:
            paths.append(objectsPaths)
            browsePath = self._translatePathToBrowsePath(objectsPaths)
            browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))
        else:
            for path in objectsPaths:
                paths.append(path)
                browsePath = self._translatePathToBrowsePath(path)
                browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))

        # Verifica se todos os itens existem
        results = self._read(browsePaths, [NodeAttributes.NodeId.value] * len(browsePaths)).items()

        typesResults = self._browse(browsePaths, EpmNodeIds.HasTypeDefinition.value).references()

        objs = collections.OrderedDict()
        for index in range(0, len(paths)):
            if results[index][1].code == 0:
                if typesResults[index][0]._displayName == "PropertyType":
                    objs[paths[index]] = EpmProperty(self, paths[index].split('/')[-1], paths[index],
                                                     results[index][0]._identity)
                else:
                    splitPath = paths[index].split("/")
                    if splitPath[0] == '':
                        del splitPath[0]
                    if "epmmodel" in splitPath[1].lower():
                        objs[paths[index]] = EpmModelObject(self, results[index][0]._identity, paths[index],
                                                            paths[index].split('/')[-1],
                                                            typesResults[index][0]._displayName)
                    else:
                        objs[paths[index]] = EpmObject(self, results[index][0]._identity, paths[index],
                                                       paths[index].split('/')[-1], typesResults[index][0]._displayName)
            else:
                objs[paths[index]] = None

        return objs

    def getEpmModelObjects(self, objectsPaths):
        paths = []
        browsePaths = []
        resultPaths = []

        if type(objectsPaths) is str:
            resultPaths.append(objectsPaths)
            if objectsPaths == '' or objectsPaths[0] == '/':
                objectsPaths = '/Models/EPMModel' + objectsPaths
            else:
                objectsPaths = '/Models/EPMModel/' + objectsPaths
            paths.append(objectsPaths)
            browsePath = self._translatePathToBrowsePath(objectsPaths)
            browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))
        else:
            for path in objectsPaths:
                resultPaths.append(path)
                if path == '' or path[0] == '/':
                    path = '/Models/EPMModel' + path
                else:
                    path = '/Models/EPMModel/' + path
                paths.append(path)
                browsePath = self._translatePathToBrowsePath(path)
                browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))

        # Verifica se todos os itens existem
        results = self._read(browsePaths, [NodeAttributes.NodeId.value] * len(browsePaths)).items()

        typesResults = self._browse(browsePaths, EpmNodeIds.HasTypeDefinition.value).references()

        objs = collections.OrderedDict()
        for index in range(0, len(paths)):
            if results[index][1].code == 0:
                if typesResults[index][0]._displayName == "PropertyType":
                    objs[resultPaths[index]] = EpmProperty(self, paths[index].split('/')[-1], paths[index],
                                                           results[index][0]._identity)
                else:
                    objs[resultPaths[index]] = EpmModelObject(self, results[index][0]._identity, paths[index],
                                                              paths[index].split('/')[-1],
                                                              typesResults[index][0]._displayName)
            else:
                objs[paths[index]] = None

        return objs

    def getElipseDataModelObjects(self, objectsPaths):
        paths = []
        browsePaths = []

        if type(objectsPaths) is str:
            objectsPaths = '/Models/ElipseDataModel/' + objectsPaths
            paths.append(objectsPaths)
            browsePath = self._translatePathToBrowsePath(objectsPaths)
            browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))
        else:
            for path in objectsPaths:
                path = '/Models/ElipseDataModel/' + path
                paths.append(path)
                browsePath = self._translatePathToBrowsePath(path)
                browsePaths.append(ItemPathJSON('OPCUA.BrowsePath', '', browsePath))

        # Verifica se todos os itens existem
        results = self._read(browsePaths, [NodeAttributes.NodeId.value] * len(browsePaths)).items()

        typesResults = self._browse(browsePaths, EpmNodeIds.HasTypeDefinition.value).references()

        objs = collections.OrderedDict()
        for index in range(0, len(paths)):
            if results[index][1].code == 0:
                if typesResults[index][0]._displayName == "PropertyType":
                    objs[objectsPaths[index]] = EpmProperty(self, paths[index].split('/')[-1], paths[index],
                                                            results[index][0]._identity)
                else:
                    objs[objectsPaths[index]] = EpmObject(self, results[index][0]._identity, paths[index],
                                                          paths[index].split('/')[-1],
                                                          typesResults[index][0]._displayName)
            else:
                objs[paths[index]] = None

        return objs

    def addInstancesEpmModel(self, path, names, objTypes):
        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/epmmodel/' + path
        header = {'Authorization': 'Bearer {}'.format(token)}
        paths = []
        objs = {}

        if type(names) is str:
            if type(objTypes) is not str:
                raise BadArgumentException("If names is a string ObjTypes must be a string too")
            jsonRequest = {'items': [{'name': names, 'type': objTypes}]}
            paths.append(path + "/" + names)
        else:
            if type(objTypes) is str:
                requestList = []
                for name in names:
                    requestList.append({'name': name, 'type': objTypes})
                    paths.append(path + "/" + name)
                jsonRequest = {'items': requestList}
            else:
                if len(names) != len(objTypes):
                    raise BadArgumentException("Names and ObjTypes must have the same size")
                requestList = []
                for (name, objType) in zip(names, objTypes):
                    requestList.append({'name': name, 'type': objType})
                    paths.append(path + "/" + name)
                jsonRequest = {'items': requestList}

        response = requests.post(url, headers=header, json=jsonRequest, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2153840640:
                    raise InstanceNameDuplicatedException('Instance name duplicated')
                elif responseCode == 2154758144:
                    raise InvalidObjectNameException('EPM Model object not found')
                elif responseCode == 2153512960:
                    raise ObjectDependenciesException('Instance type creation not allowed')
                elif responseCode == 2158690304:
                    raise InvalidObjectTypeException('Invalid type name')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("AddInstanceEpmModel call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        for obj in self.getEpmModelObjects(paths).values():
            objs[obj.name] = obj

        return objs

    def removeInstanceEpmModel(self, path):
        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/epmmodel/' + path
        header = {'Authorization': 'Bearer {}'.format(token)}

        response = requests.delete(url, headers=header, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('EPM Model object not found')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("RemoveInstanceEpmModel call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

    def setBindedVariables(self, objectPath, aliasProperties, variablesNames, isEpmModel=True):
        token = self._authorizationService.getToken()
        header = {'Authorization': 'Bearer {}'.format(token)}
        if isEpmModel:
            url = self._webApi + '/epm/v1/epmmodel/' + objectPath
        else:
            raise BadArgumentException('Invalid isEpmModel argument')

        response = requests.get(url, headers=header, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['diagnostic']['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('Object not found')
                else:
                    raise Exception(response.json()['diagnostic']['message'])
        else:
            raise Exception("SetBindedVariables call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

        json_response = json.loads(response.text)

        if type(aliasProperties) is str:
            if type(variablesNames) is not str:
                raise BadArgumentException('aliasProperties and variablesNames must be the same size')
            counter = 1
            for dic in json_response['items']:
                if dic['name'] == aliasProperties and dic['type'] == 'AliasProperty':
                    counter = counter - 1
        else:
            if type(variablesNames) is str:
                raise BadArgumentException('aliasProperties and variablesNames must be the same size')
            if len(aliasProperties) != len(variablesNames):
                raise BadArgumentException('aliasProperties and variablesNames must be the same size')
            counter = len(aliasProperties)
            for dic in json_response['items']:
                if dic['name'] in aliasProperties and dic['type'] == 'AliasProperty':
                    counter = counter - 1

        if counter != 0:
            raise InvalidObjectPropertyException('Invalid alias property name')

        if type(aliasProperties) is str:
            jsonRequest = {'items': [{'propertyName': aliasProperties, 'value': variablesNames}]}
        else:
            itemsList = []
            for (aliasProperty, variableName) in zip(aliasProperties, variablesNames):
                itemsList.append({'propertyName': aliasProperty, 'value': variableName})
            jsonRequest = {'items': itemsList}

        response = requests.patch(url, headers=header, json=jsonRequest, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('Object not found')
                elif responseCode == 2153775104:
                    raise InvalidSourceVariableException('Invalid source variable provided')
                else:
                    raise Exception(response.json()['message'])
        else:
            raise Exception("SetBindedVariables call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + ". Text: " + response.text)

    def exportEpmModel(self, fileName, pathName=None):
        items = self._epmModelInstancesToJson('')
        jsonWrite = {'items': items}

        if pathName is None:
            pathName = os.getcwd()
        fileName = fileName + ".json"
        with open(os.path.join(pathName, fileName), 'w') as outfile:
            json.dump(jsonWrite, outfile)

    def importEpmModel(self, filePath, importMode=ImportMode.OnlyAdd):
        with open(filePath) as json_file:
            jsonRead = json.load(json_file)

        self._jsonToEpmModelInstances(jsonRead['items'], '', importMode)


    def _epmModelInstancesToJson(self, path):
        token = self._authorizationService.getToken()
        header = {'Authorization': 'Bearer {}'.format(token)}
        url = self._webApi + '/epm/v1/epmmodel/' + path

        response = requests.get(url, headers=header, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['diagnostic']['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('Object ' + path + ' not found')
                else:
                    raise Exception(response.json()['diagnostic']['message'])
        else:
            raise Exception("_epmModelInstancesToJson call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + " Path: '" + path + "'. Text: " + response.text)

        json_response = json.loads(response.text)
        itemsList = []

        for dic in json_response['items']:
            if dic['type'] != 'Property' and dic['type'] != 'AliasProperty':
                if path == '':
                    items = self._epmModelInstancesToJson(dic['name'])
                else:
                    items = self._epmModelInstancesToJson(path + '/' + dic['name'])
                dic['items'] = items
            elif dic['type'] == 'Property':
                propPath = path + '/' + dic['name']
                prop = self.getEpmModelObjects(propPath)[propPath]
                dic['value'] = prop.read().value
            itemsList.append(dic)

        return itemsList

    def _jsonToEpmModelInstances(self, items, path, importMode):
        token = self._authorizationService.getToken()
        header = {'Authorization': 'Bearer {}'.format(token)}
        url = self._webApi + '/epm/v1/epmmodel/' + path

        response = requests.get(url, headers=header, verify=False)

        if response.status_code == 200:
            responseCode = response.json()['diagnostic']['code']
            if responseCode != 0:
                if responseCode == 2154758144:
                    raise InvalidObjectNameException('Object ' + path + ' not found')
                else:
                    raise Exception(response.json()['diagnostic']['message'])
        else:
            raise Exception("JsonToEpmModelInstances call error + '" + str(response.status_code) + "'. Reason: " +
                            response.reason + " Path: '" + path + "'. Text: " + response.text)

        objInstances = json.loads(response.text)
        createdInstances = []
        for instance in objInstances['items']:
            createdInstances.append(instance['name'])

        obj = self.getEpmModelObjects(path)[path]

        if importMode == ImportMode.OnlyAdd:
            for item in items:
                try:
                    if item['type'] == 'Property':
                        propPath = path + '/' + item['name']
                        prop = self.getEpmModelObjects(propPath)[propPath]
                        prop.write(item['value'])
                    elif item['type'] == 'AliasProperty':
                        if item['source']:
                            obj.setBindedVariables(item['name'], item['source'])
                    else:
                        if path != '':
                            objType = self.getCustomType(obj.type)
                            if item['type'] in objType.placeHolderTypes:
                                objPropertiesNames = []
                                for objProp in objType.objectProperties:
                                    objPropertiesNames.append(objProp.name)
                                if item['name'] not in createdInstances:
                                    obj.addInstances(item['name'], item['type'])
                                elif item['name'] not in objPropertiesNames:
                                    raise InvalidObjectNameException(item['name'] + ' already exists')
                            objPath = path + '/' + item['name']
                            self._jsonToEpmModelInstances(item['items'], objPath, importMode)
                        else:
                            if item['name'] not in createdInstances:
                                obj.addInstances(item['name'], item['type'])
                            else:
                                raise InvalidObjectNameException(item['name'] + ' already exists')
                            self._jsonToEpmModelInstances(item['items'], item['name'], importMode)
                except InvalidObjectNameException as err:
                    raise err
                except:
                    raise BadArgumentException("Argument error on " + item['name'])
        elif importMode == ImportMode.OnlyEdit:
            for item in items:
                try:
                    if item['type'] == 'Property':
                        propPath = path + '/' + item['name']
                        prop = self.getEpmModelObjects(propPath)[propPath]
                        prop.write(item['value'])
                    elif item['type'] == 'AliasProperty':
                        if item['source']:
                            obj.setBindedVariables(item['name'], item['source'])
                    else:
                        if item['name'] not in createdInstances:
                            raise InvalidObjectNameException(item['name'] + ' does not exist')
                        if path == '':
                            self._jsonToEpmModelInstances(item['items'], item['name'], importMode)
                        else:
                            objPath = path + '/' + item['name']
                            self._jsonToEpmModelInstances(item['items'], objPath, importMode)
                except InvalidObjectNameException as err:
                    raise err
                except:
                    raise BadArgumentException("Argument error on " + item['name'])
        elif importMode == ImportMode.AddAndEdit:
            for item in items:
                try:
                    if item['type'] == 'Property':
                        propPath = path + '/' + item['name']
                        prop = self.getEpmModelObjects(propPath)[propPath]
                        prop.write(item['value'])
                    elif item['type'] == 'AliasProperty':
                        if item['source']:
                            obj.setBindedVariables(item['name'], item['source'])
                    else:
                        if item['name'] not in createdInstances:
                            obj.addInstances(item['name'], item['type'])
                        if path == '':
                            self._jsonToEpmModelInstances(item['items'], item['name'], importMode)
                        else:
                            objPath = path + '/' + item['name']
                            self._jsonToEpmModelInstances(item['items'], objPath, importMode)
                except:
                    raise BadArgumentException("Argument error on " + item['name'])
        else:
            raise BadArgumentException("Invalid ImportMode argument")

    def newDataset(self, name, description=None):
        return DatasetConfig(self, name, description=description)

    def newDatasetLocal(self, name, description = None):
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        documentsFolder = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, documentsFolder)
        documentsFolder = documentsFolder.value.replace('\\', '/')
        filesPath = documentsFolder + '/Elipse Software/EPM Studio/Datasets/'
        files = os.listdir(filesPath)
        for file in files:
            if str.lower(name) == str.lower(file.title()[:-11]):
                raise BadArgumentException("Dataset name already exists")
        filePath = filesPath + name + '.epmdataset'
        dataset = DatasetConfigLocal(self, name, description=description, filePath=filePath)
        dataset.save()

        return dataset

    def newDatasetServer(self, name, description = None):
        for datasetName in self.listDatasetServer():
            if str.lower(name) == str.lower(datasetName):
                raise BadArgumentException("Dataset name already exists")
        dataset = DatasetConfigServer(self, name, description=description)
        dataset.save()

        return dataset

    def loadDatasetFile(self, filePath):
        if str.lower(filePath).endswith('.epmdataset'):
            if '\\' in filePath:
                filePath = filePath.value.replace('\\', '/')
            name = filePath.split('/')[-1]
            name = name[:-11]
            with open(filePath, "r") as file:
                content = file.read()

            return DatasetConfigLocal(self, name, content, filePath=filePath)
        else:
            raise BadArgumentException("Invalid file extension")

    def loadDatasetLocal(self, fileName):
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        documentsFolder = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, documentsFolder)
        documentsFolder = documentsFolder.value.replace('\\', '/')
        filePath = documentsFolder + '/Elipse Software/EPM Studio/Datasets/' + fileName + '.epmdataset'
        name = fileName

        with open(filePath, "r") as file:
            content = file.read()

        return DatasetConfigLocal(self, name, content, filePath=filePath)

    def loadDatasetServer(self, name):
        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/resource'
        header = {'Authorization': 'Bearer {}'.format(token)}
        datasetAddress = "1:Datasets/1:" + name
        itemPath = ItemPathJSON("OPCUA.BrowsePath", None, datasetAddress)
        continuationPoint = None
        jsonRequest = {"continuationPoint": continuationPoint, "paths": [itemPath.toDict()]}
        response = requests.post(url, headers=header, json=jsonRequest, verify=False)
        jsonResponse = json.loads(response.text)
        content = jsonResponse['items'][0]['content']
        description = jsonResponse['items'][0]['description']

        return DatasetConfigServer(self, name, description, content)

    def _saveDatasetFile(self, content, filePath, overwrite = False):
        if overwrite is False:
            if os.path.exists(filePath):
                raise Exception("Dataset file already exists")

        content = content.replace('\r\n', '\n')
        with open(filePath, "w") as file:
            file.write(content)

    def _saveDatasetServer(self, name, description, content, overwrite = False, oldName = None):
        exists = False
        for datasetName in self.listDatasetServer():
            if str.lower(name) == str.lower(datasetName):
                exists = True

        if exists is False:
            if oldName is None:
                identity = None
            else:
                token = self._authorizationService.getToken()
                url = self._webApi + '/epm/v1/resource'
                header = {'Authorization': 'Bearer {}'.format(token)}
                datasetAddress = "1:Datasets/1:" + oldName
                itemPath = ItemPathJSON("OPCUA.BrowsePath", None, datasetAddress)
                continuationPoint = None
                jsonRequest = {"continuationPoint": continuationPoint, "paths": [itemPath.toDict()]}
                response = requests.post(url, headers=header, json=jsonRequest, verify=False)
                jsonResponse = json.loads(response.text)
                identity = jsonResponse['items'][0]['identity']
        else:
            if overwrite is False:
                raise Exception("Dataset already exists")
            else:
                token = self._authorizationService.getToken()
                url = self._webApi + '/epm/v1/resource'
                header = {'Authorization': 'Bearer {}'.format(token)}
                datasetAddress = "1:Datasets/1:" + name
                itemPath = ItemPathJSON("OPCUA.BrowsePath", None, datasetAddress)
                continuationPoint = None
                jsonRequest = {"continuationPoint": continuationPoint, "paths": [itemPath.toDict()]}
                response = requests.post(url, headers=header, json=jsonRequest, verify=False)
                jsonResponse = json.loads(response.text)
                identity = jsonResponse['items'][0]['identity']

        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/resource/update'
        header = {'Authorization': 'Bearer {}'.format(token)}
        resourceModelJson = {"identity": identity, "name": name, "description": description,
                             "typeId": "{041582AB-CD7B-4313-8477-1D3AC4A43256}", "content": content}
        jsonRequest = {"items": [resourceModelJson]}
        response = requests.post(url, headers=header, json=jsonRequest, verify=False)
        jsonResponse = json.loads(response.text)
        errorCode = jsonResponse['diagnostics'][0]['code']
        if errorCode != 0:
            raise Exception("Dataset save did not succeed")

    def _deleteDatasetFile(self, filePath):
        if filePath is not None and os.path.exists(filePath) and filePath.endswith('.epmdataset'):
            os.remove(filePath)
        else:
            raise BadArgumentException("Dataset file does not exist")

    def _deleteDatasetServer(self, name):
        exists = False
        for datasetName in self.listDatasetServer():
            if str.lower(name) == str.lower(datasetName):
                exists = True
        if exists is True:
            token = self._authorizationService.getToken()
            url = self._webApi + '/epm/v1/resource/remove'
            header = {'Authorization': 'Bearer {}'.format(token)}
            datasetAddress = "1:Datasets/1:" + name
            itemPath = ItemPathJSON("OPCUA.BrowsePath", None, datasetAddress)
            jsonRequest = {"paths": [itemPath.toDict()]}
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            jsonResponse = json.loads(response.text)
            errorCode = jsonResponse['diagnostics'][0]['code']
            if errorCode != 0:
                raise Exception("Dataset delete did not succeed")
        else:
            raise BadArgumentException("Dataset does not exist")

    def listDatasetLocal(self):
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        documentsFolder = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, documentsFolder)
        documentsFolder = documentsFolder.value.replace('\\', '/')
        filesPath = documentsFolder + '/Elipse Software/EPM Studio/Datasets/'
        files = os.listdir(filesPath)
        datasetNames = []
        for file in files:
            if str.lower(file.title()).endswith('.epmdataset'):
                datasetNames.append(str.lower(file.title()[:-11]))

        return datasetNames

    def listDatasetServer(self):
        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/resource/list'
        header = {'Authorization': 'Bearer {}'.format(token)}
        continuationPoint = None
        datasetTypeId = "{041582AB-CD7B-4313-8477-1D3AC4A43256}"
        jsonRequest = {"continuationPoint": continuationPoint, "types": [datasetTypeId]}
        response = requests.post(url, headers=header, json=jsonRequest, verify=False)
        jsonResponse = json.loads(response.text)
        datasetNames = []
        for item in jsonResponse['items']:
            datasetNames.append(item['name'])

        return datasetNames

    def close(self):
        self._authorizationService.close()

    def open(self):
        self._authorizationService.restart()

    def historyUpdate(self, variables, numpyArrays):
        self._historyUpdate(HistoryUpdateType.Update.value, [variable._itemPath for variable in variables], numpyArrays)
        return

    # region Private Methods

    def _historyUpdate(self, updateType, itemPaths, numpyArrays, dataTypeId=None):
        if len(itemPaths) != len(numpyArrays):
            raise Exception('Invalid number of item in numpyArrays')

        # updateType = 3 # Update
        blockSize = 80000
        totalValues = 0

        historyUpdateRequests = []

        for index in range(len(itemPaths)):
            valuesCount = len(numpyArrays[index])
            if (valuesCount == 0):
                continue

            if (not numpyArrays[index].dtype.names == ('Value', 'Timestamp', 'Quality')):
                raise Exception('Invalid array definition')

            if valuesCount > blockSize:
                if len(historyUpdateRequests) > 0:
                    self._historyUpdateCall(HistoryUpdateDataModelJSON(historyUpdateRequests))
                    historyUpdateRequests.clear()
                # Prepare big call
                chunks = [numpyArrays[index][x:x + blockSize] for x in range(0, len(numpyArrays[index]), blockSize)]
                for chunk in chunks:
                    dataValueArray = []
                    for i in iter(range(0, len(chunk))):
                        dataType = dataTypeId if i < 1 else None
                        if 'numpy' in str(type(chunk['Value'][i])):
                            dataValueArray.append(DataValueJSON((chunk['Value'][i]).item(), (chunk['Quality'][i]),
                                                            chunk['Timestamp'][i], dataTypeId=dataType))
                        else:
                            dataValueArray.append(DataValueJSON((chunk['Value'][i]), (chunk['Quality'][i]),
                                                            chunk['Timestamp'][i], dataTypeId=dataType))
                    historyUpdateRequest = HistoryUpdateDataModelJSON(
                        [HistoryUpdateDataItemModelJSON(itemPaths[index], updateType, dataValueArray)])
                    self._historyUpdateCall(historyUpdateRequest)
                totalValues = 0
            else:
                dataValueArray = []
                for i in range(len(numpyArrays[index])):
                    dataType = dataTypeId if i < 1 else None
                    if 'numpy' in str(type(numpyArrays[index]['Value'][i])):
                        dataValueArray.append(DataValueJSON((numpyArrays[index]['Value'][i].item()),
                                                            (numpyArrays[index]['Quality'][i]),
                                                            numpyArrays[index]['Timestamp'][i],
                                                            dataTypeId=dataType))
                    else:
                        dataValueArray.append(DataValueJSON((numpyArrays[index]['Value'][i]),
                                                            (numpyArrays[index]['Quality'][i]),
                                                            numpyArrays[index]['Timestamp'][i],
                                                            dataTypeId=dataType))
                historyUpdateRequests.append(
                    HistoryUpdateDataItemModelJSON(itemPaths[index], updateType, dataValueArray))
                if totalValues + valuesCount > blockSize:
                    self._historyUpdateCall(HistoryUpdateDataModelJSON(historyUpdateRequests))
                    historyUpdateRequests.clear()
                    totalValues = 0
                else:
                    totalValues = totalValues + valuesCount
        if len(historyUpdateRequests) > 0:
            self._historyUpdateCall(HistoryUpdateDataModelJSON(historyUpdateRequests))
        return

    def _historyUpdateCall(self, historyUpdateRequest):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/history/update/data'
        header = {'Authorization': 'Bearer {}'.format(token)}

        jsonRequest = historyUpdateRequest.toDict()

        response = requests.post(url, headers=header, json=jsonRequest, verify=False)
        if response.status_code != 200:
            raise Exception(
                "HistoryUpdate call error + '" + str(response.status_code) + "'. Reason: " + response.reason)

        json_result = json.loads(response.text)
        if json_result['diagnostics'][0]['code'] != 0:
            raise Exception("HistoryUpdate call error. Reason: " + str(json_result['diagnostics'][0]['code']))

        return json_result

    def _historyUpdateAnnotation(self, annotationPath, updateType, annotations):

        blockSize = 1000
        totalValues = 0

        historyUpdateRequests = []

        valuesCount = len(annotations)
        if (valuesCount == 0):
            return

        import datetime

        dataValueArray = []

        for i in range(len(annotations)):
            dataValueArray.append(AnnotationValueJSON(annotations[i][2], annotations[i][1], annotations[i][0]))

        annotationType = ItemPathJSON('OPCUA.NodeId', None, EpmNodeIds.AnnotationType.value)
        historyUpdateRequest = HistoryUpdateDataModelJSON(
            [HistoryUpdateDataItemModelJSON(annotationPath, updateType, dataValueArray, annotationType)])
        self._historyUpdateCall(historyUpdateRequest)

        return

    def _write(self, paths, attributeIds, values):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/write'
        header = {'Authorization': 'Bearer {}'.format(token)}

        writeItems = []
        for x in range(0, len(paths)):
            writeItems.append(WriteItemModelJSON(paths[x], attributeIds[x], values[x]))

        request = WriteModelJSON(writeItems)
        jsonRequest = request.toDict()
        response = requests.post(url, headers=header, json=jsonRequest, verify=False)
        if response.status_code != 200:
            print(response.reason)
            raise Exception(
                "Write service call http error '" + str(response.status_code) + "'. Reason: " + response.reason + ". Message: " + response.text)
        json_result = json.loads(response.text)
        if json_result == None:
            raise Exception("Write Failed no result")
        elif len(json_result['diagnostics']) != len(writeItems):
            raise Exception("Write Failed with error '" + str(json_result['diagnostics'][0]) + "'")
        elif json_result['diagnostics'][0]['code'] != 0:
            raise Exception(
                "Write Failed with error code: " + str(json_result['diagnostics'][0]['code']) + " and message: '" + str(
                    json_result['diagnostics'][0]['message']) + "'")
        return

    def _read(self, paths, attributeIds):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/read'
        header = {'Authorization': 'Bearer {}'.format(token)}

        readItems = []
        for x in range(0, len(paths)):
            readItems.append(ReadItemModelJSON(paths[x], attributeIds[x]))

        continuationPoint = None

        resultItems = []
        diagnostics = []

        while True:
            request = ReadModelJSON(readItems, continuationPoint)
            jsonRequest = request.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Read service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("Read Failed no result")
            elif len(json_result['diagnostics']) != len(readItems):
                raise Exception("Read Failed with error '" + str(json_result['diagnostics'][0]) + "'")

            for diagnostic, item in zip(json_result['diagnostics'], json_result['items']):
                diagnostics.append(DiagnosticModelJSON(diagnostic['code']))
                if diagnostic['code'] == 0:
                    readItem = ReadResultItemModelJSON(item['identity'],
                                                       DataValueJSON(item['value']['value'], item['value']['quality'],
                                                                     item['value']['timestamp']))
                else:
                    readItem = None
                resultItems.append(readItem)

            # for item in json_result['items']:
            #  readItem = ReadResultItemModelJSON(item['identity'], DataValueJSON(item['value']['value'], item['value']['quality'], item['value']['timestamp']))
            #  resultItems.append(readItem)

            continuationPoint = json_result['continuationPoint']
            if continuationPoint == None:
                break

        return ReadResultModelJSON(resultItems, diagnostics)

    def _browse(self, paths, referenceType, nodeClassMask = NodeClassMask.Unspecified):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/browse'
        header = {'Authorization': 'Bearer {}'.format(token)}

        itemsModels = []

        for item in paths:
            itemsModels.append(BrowseItemModelJSON(item, nodeClassMask.value, [referenceType]))

        continuationPoint = None

        requestResults = []
        diagnostics = []

        while True:
            request = BrowseModelJSON(itemsModels, continuationPoint)
            jsonRequest = request.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Browse service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("Browse Failed no result")
            elif len(json_result['diagnostics']) != len(paths):
                raise Exception("Invalid browse result items!")

            for json_item, json_diags in zip(json_result['items'], json_result['diagnostics']):
                diagnostics.append(DiagnosticModelJSON(json_diags['code']))
                if json_diags['code'] == 0:
                    resultItems = []
                    for item in json_item:
                        browseItem = BrowseResultItemModelJSON(item['identity'], item['displayName'],
                                                               item['relativePath'], item['type'], item['nodeClass'])
                        resultItems.append(browseItem)
                    requestResults.append(resultItems)
                else:
                    requestResults.append(None)
            continuationPoint = json_result['continuationPoint']
            if continuationPoint == None:
                break

        return BrowseResultModelJSON(requestResults, diagnostics)

    def _historyReadAggregate(self, aggregateType, queryPeriod, itemPath):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/history/processed'
        header = {'Authorization': 'Bearer {}'.format(token)}

        if aggregateType.type == AggregateType.Trend.name:
            aggregatePath = ItemPathJSON('OPCUA.NodeId', None, "ns=1;i=245")
        elif aggregateType.type == AggregateType.PercentInStateZero.name:
            aggregatePath = ItemPathJSON('OPCUA.NodeId', None, "ns=1;i=270")
        elif aggregateType.type == AggregateType.PercentInStateNonZero.name:
            aggregatePath = ItemPathJSON('OPCUA.NodeId', None, "ns=1;i=271")
        else:
            basePath = "/Server/ServerCapabilities/AggregateFunctions/"
            aggregatePath = ItemPathJSON('OPCUA.BrowsePath', '', basePath + aggregateType.type)
        continuationPoint = None
        dataValues = []

        processingInterval = aggregateType.interval.total_seconds() * 1000

        while True:
            itemPathAndCP = ItemPathAndContinuationPointJSON(itemPath, continuationPoint, False)
            historyReadRequest = HistoryProcessedModelJSON(aggregatePath, processingInterval, queryPeriod.start,
                                                           queryPeriod.end, [itemPathAndCP])
            jsonRequest = historyReadRequest.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("historyReadAggregate Failed no result")
            elif len(json_result['diagnostics']) != 1:
                raise Exception("historyReadAggregate Failed with error '" + str(json_result['diagnostics'][0]) + "'")
            elif json_result['diagnostics'][0]['code'] != 0:
                raise Exception("historyReadAggregate Failed with error code: " + str(
                    json_result['diagnostics'][0]['code']) + " and message: '" + str(
                    json_result['diagnostics'][0]['message']) + "'")
            dataValues.extend(json_result['dataValues'][0]['dataValues'])
            continuationPoint = json_result['dataValues'][0]['continuationPoint']
            if continuationPoint == None:
                break
        util = NumpyExtras()
        numpyArray = util.numpyArrayFromDataValues(dataValues)
        return numpyArray

    def _historyReadAnnotation(self, queryPeriod, annotationPath):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/history/raw'
        header = {'Authorization': 'Bearer {}'.format(token)}

        continuationPoint = None
        annotations = []

        import dateutil.parser

        while True:
            itemPathAndCP = ItemPathAndContinuationPointJSON(annotationPath, continuationPoint, False)
            historyReadRequest = HistoryRawModelJSON(queryPeriod.start, queryPeriod.end, False, [itemPathAndCP])
            jsonRequest = historyReadRequest.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("historyReadAnnotation Failed no result")
            elif len(json_result['diagnostics']) != 1:
                raise Exception("historyReadAnnotation Failed with error '" + str(json_result['diagnostics'][0]) + "'")
            elif json_result['diagnostics'][0]['code'] != 0:
                raise Exception("historyReadAnnotation Failed with error code: " + str(
                    json_result['diagnostics'][0]['code']) + " and message: '" + str(
                    json_result['diagnostics'][0]['message']) + "'")

            for value in json_result['dataValues'][0]['dataValues']:
                if ('userName' in value['value'] and
                        'annotationTime' in value['value'] and
                        'message' in value['value']):
                    annotationTime = dateutil.parser.parse(value['value']['annotationTime'])
                    annotations.append((annotationTime, value['value']['userName'],
                                        value['value']['message']))
            # dataValues.extend(json_result['dataValues'][0]['dataValues'])
            continuationPoint = json_result['dataValues'][0]['continuationPoint']
            if continuationPoint == None:
                break

        return annotations

    def _historyReadRaw(self, queryPeriod, itemPath, bounds=False):
        token = self._authorizationService.getToken()
        url = self._webApi + '/opcua/v1/history/raw'
        header = {'Authorization': 'Bearer {}'.format(token)}

        # itemPath = ItemPathJSON('OPCUA.BrowsePath', '', variablePath)
        continuationPoint = None
        dataValues = []

        while True:
            itemPathAndCP = ItemPathAndContinuationPointJSON(itemPath, continuationPoint, False)
            historyReadRequest = HistoryRawModelJSON(queryPeriod.start, queryPeriod.end, bounds, [itemPathAndCP])
            jsonRequest = historyReadRequest.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("historyReadRaw Failed no result")
            elif len(json_result['diagnostics']) != 1:
                raise Exception("historyReadRaw Failed with error '" + str(json_result['diagnostics'][0]) + "'")
            elif json_result['diagnostics'][0]['code'] != 0:
                raise Exception("historyReadRaw Failed with error code: " + str(
                    json_result['diagnostics'][0]['code']) + " and message: '" + str(
                    json_result['diagnostics'][0]['message']) + "'")

            dataValues.extend(json_result['dataValues'][0]['dataValues'])
            continuationPoint = json_result['dataValues'][0]['continuationPoint']
            if continuationPoint == None:
                break
        util = NumpyExtras()
        numpyArray = util.numpyArrayFromDataValues(dataValues)
        return numpyArray

    def _query(self, browseNameFilter, descriptionFilter, euNameFilter, domainFilter, typeFilter):
        token = self._authorizationService.getToken()
        url = self._webApi + '/epm/v1/query'
        header = {'Authorization': 'Bearer {}'.format(token)}

        continuationPoint = None

        items = collections.OrderedDict()

        while True:
            model = QueryModelJSON(continuationPoint, False,
                                   QueryResultMask.Name.value | QueryResultMask.Identity.value, browseNameFilter,
                                   descriptionFilter, euNameFilter, typeFilter, domainFilter.value)
            jsonRequest = model.toDict()
            response = requests.post(url, headers=header, json=jsonRequest, verify=False)
            if response.status_code != 200:
                print(response.reason)
                raise Exception(
                    "Service call http error '" + str(response.status_code) + "'. Reason: " + response.reason)
            json_result = json.loads(response.text)
            if json_result == None:
                raise Exception("Query Failed no result")
            elif json_result['diagnostic']['code'] != 0:
                raise Exception(
                    "query Failed with error code: " + str(json_result['diagnostic']['code']) + " and message: '" + str(
                        json_result['diagnostic']['message']) + "'")
            continuationPoint = json_result['continuationPoint']

            resultTypes = self._browse(
                [ItemPathJSON('OPCUA.NodeId', '', item['identity']) for item in json_result['items']],
                EpmNodeIds.HasTypeDefinition.value).references()

            index = 0
            for item in json_result['items']:
                if resultTypes[index][0]._identity == EpmNodeIds.BasicVariableType.value:
                    dataObject = BasicVariable(self, item['identity'], item['name'])
                else:
                    dataObject = EpmDataObject(self, item['name'], item['identity'])
                items[item['name']] = dataObject
                index = index + 1
            if continuationPoint == None:
                break
        return items

    def _getAllDataObjects(self, attributes, reference, rootNode='/1:DataObjects'):

        itemPath = ItemPathJSON('OPCUA.BrowsePath', '', rootNode)
        browseResult = self._browse([itemPath], reference.value, NodeClassMask.Variable).references()
        if len(browseResult) < 1:
            return []

        epmVariables = collections.OrderedDict()

        for item in browseResult[0]:
            if item._type == EpmNodeIds.BasicVariableType.value:
                epmVariables[item._displayName] = BasicVariable(self, item._identity, item._displayName)
            else:
                epmVariables[item._displayName] = EpmDataObject(self, item._displayName, item._identity)

        self._fillDataObjectsAttributes(list(epmVariables.values()), attributes)

        return epmVariables

    def _getDataObjects(self, doNames, attributes, rootNode='/1:DataObjects'):
        names = []
        paths = []
        if type(doNames) is str:
            names.append(doNames)
            paths.append(ItemPathJSON('OPCUA.BrowsePath', '', rootNode + '/1:' + doNames))
        else:
            names = doNames
            for item in doNames:
                paths.append(ItemPathJSON('OPCUA.BrowsePath', '', rootNode + '/1:' + item))

        # Verifica se todos os itens existem
        resultIds = self._read(paths, [NodeAttributes.NodeId.value] * len(paths)).items()
        resultTypes = self._browse(paths, EpmNodeIds.HasTypeDefinition.value).references()

        readProperties = []

        epmVariables = collections.OrderedDict()
        for index in range(0, len(names)):
            if resultIds[index][1].code == 0:
                if resultTypes[index][0]._identity == EpmNodeIds.BasicVariableType.value:
                    epmVariables[names[index]] = BasicVariable(self, resultIds[index][0]._identity, names[index])
                else:
                    epmVariables[names[index]] = EpmDataObject(self, names[index], resultIds[index][0]._identity)
            else:
                epmVariables[names[index]] = None

        self._fillDataObjectsAttributes(list(epmVariables.values()), attributes)

        return epmVariables

    def _fillDataObjectsAttributes(self, dataObjects, attributes):

        propertyPaths = []
        if attributes == DataObjectAttributes.Unspecified.value:
            return dataObjects

        for index in range(0, len(dataObjects)):
            # for item in dataObjects:
            variable = dataObjects[index]
            if variable == None:
                continue
            if DataObjectAttributes.Name in attributes:
                propertyPaths.append((variable, DataObjectAttributes.Name, ItemPathJSON('OPCUA.NodeId', None,
                                                                                        variable._encodePropertyIdentity(
                                                                                            EpmDataObjectAttributeIds.Name.value))))
            if DataObjectAttributes.Description in attributes:
                propertyPaths.append((variable, DataObjectAttributes.Description, ItemPathJSON('OPCUA.NodeId', None,
                                                                                               variable._encodePropertyIdentity(
                                                                                                   EpmDataObjectAttributeIds.Description.value))))
            if DataObjectAttributes.EU in attributes:
                propertyPaths.append((variable, DataObjectAttributes.EU, ItemPathJSON('OPCUA.NodeId', None,
                                                                                      variable._encodePropertyIdentity(
                                                                                          EpmDataObjectAttributeIds.EU.value))))
            if DataObjectAttributes.LowLimit in attributes:
                propertyPaths.append((variable, DataObjectAttributes.LowLimit, ItemPathJSON('OPCUA.NodeId', None,
                                                                                            variable._encodePropertyIdentity(
                                                                                                EpmDataObjectAttributeIds.LowLimit.value))))
            if DataObjectAttributes.HighLimit in attributes:
                propertyPaths.append((variable, DataObjectAttributes.HighLimit, ItemPathJSON('OPCUA.NodeId', None,
                                                                                             variable._encodePropertyIdentity(
                                                                                                 EpmDataObjectAttributeIds.HighLimit.value))))
            if DataObjectAttributes.Clamping in attributes:
                propertyPaths.append((variable, DataObjectAttributes.Clamping, ItemPathJSON('OPCUA.NodeId', None,
                                                                                            variable._encodePropertyIdentity(
                                                                                                EpmDataObjectAttributeIds.Clamping.value))))
            if DataObjectAttributes.Domain in attributes:
                propertyPaths.append((variable, DataObjectAttributes.Domain, ItemPathJSON('OPCUA.NodeId', None,
                                                                                          variable._encodePropertyIdentity(
                                                                                              EpmDataObjectAttributeIds.Domain.value))))
            if DataObjectAttributes.Active in attributes:
                propertyPaths.append((variable, DataObjectAttributes.Active, ItemPathJSON('OPCUA.NodeId', None,
                                                                                          variable._encodePropertyIdentity(
                                                                                              EpmDataObjectAttributeIds.Active.value))))
            if DataObjectAttributes.TagType in attributes:
                propertyPaths.append((variable, DataObjectAttributes.TagType, ItemPathJSON('OPCUA.NodeId', None,
                                                                                          variable._encodePropertyIdentity(
                                                                                              EpmDataObjectAttributeIds.TagType.value))))

        chunks = [propertyPaths[x:x + 1000] for x in range(0, len(propertyPaths), 1000)]

        for chunk in chunks:
            if len(chunk) > 0:
                readResults = self._read(list(zip(*chunk))[2], [13] * len(chunk)).items()
                for index in range(0, len(readResults)):
                    dataObject = chunk[index][0]
                    attributeId = chunk[index][1]
                    if readResults[index][1].code == 0:
                        dataObject._setAttribute(attributeId, readResults[index][0].value.value)

            # Private Methods

    def _translatePathToBrowsePath(self, path):
        if len(path) == 0:
            return ''
        if path[0] == '/':
            path = path[1:]

        browsePath = ''
        splittedPath = path.split('/')
        for relativePath in splittedPath:

            splittedRelativePath = relativePath.split(':')
            currentPath = relativePath
            if len(splittedRelativePath) == 1:
                currentPath = '1:' + relativePath
            browsePath = browsePath + '/' + currentPath

        return browsePath

class BadArgumentException(Exception):
    pass
