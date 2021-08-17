"""
Elipse Plant Manager - EPM Web API
Copyright (C) 2018 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
"""

from .epmdataobject import EpmDataObject
from .itempathjson import ItemPathJSON
from .epmproperty import EpmProperty
from .epmnodeids import EpmNodeIds

import collections


class EpmObject(object):
    """description of class"""

    def __init__(self, epmConnection, identity, path, name, type = ''):
        self._epmConnection = epmConnection
        self._itemPath = ItemPathJSON('OPCUA.NodeId', None, identity)
        self._path = path
        self._type = type
        self._name = name

    # Public Methods

    #def getProperty(self, property):
    #    if self._propertiesNames.index(property) < 0:
    #        raise Exception('Invalid property name')
    #    return EpmProperty(self._epmConnection, property, self._browsePath + '/1:' + property)

    def enumObjects(self):
        result = self._epmConnection._browse([self._itemPath], EpmNodeIds.HasComponent.value).references()[0]
        if len(result) < 1:
            return []
        childObjects = collections.OrderedDict()
        types = {}
        for item in result:
            if item._nodeClass == 4:  # Method is ignored
                continue
            childObjects[item._displayName] = EpmObject(self._epmConnection, item._identity,
                                                        self._path + '/' + item._displayName, item._displayName,
                                                        item._type)
            types[item._type] = ItemPathJSON('OPCUA.NodeId', '', item._type)
        typeNames = self._epmConnection._read(list(types.values()), [4] * len(types.values())).values()
        for x in typeNames:
            types[x.identity] = x.value.value
        for x in childObjects:
            childObjects[x].type = types[childObjects[x].type]

        return childObjects

    def enumProperties(self):
      result = self._epmConnection._browse([ self._itemPath ], EpmNodeIds.HasProperty.value)
      childProperties = collections.OrderedDict()
      for item in result.references()[0]:
        childProperties[item._displayName] = EpmProperty(self._epmConnection, item._displayName, self._path + '/' + item._displayName, item._identity)
      return childProperties

    # Public Properties

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

