"""
DeviceDataView Class [Extends DeviceData Class]
"""

from galenSDK.model.DeviceData import DeviceData
from galenSDK.model.HelperFunctions import parse_owner_helper
from galenSDK.enumeration.Scope import Scope


class DeviceDataView(DeviceData):
    # owner - Object of supplier, practice, or user that represents the owner of the data
    owner = None
    # Scope - Denotes the type of the owner, weather it is a tenant, supplier, practice, or user.
    scope = None

    def __init__(self, deviceDataId=None, deviceDataModelId=None, ownerId=None, minValueProvidedOn=None,
                 maxValueProvidedOn=None, data=[], owner=None, scope: Scope = None):
        super().__init__(deviceDataId, deviceDataModelId, ownerId, minValueProvidedOn, maxValueProvidedOn, data)
        """
        Initializer for the DeviceDataView Class
        :param deviceDataId: deviceDataId to set. Optional.
        :param deviceDataModelId: deviceDataModelId to set. Optional.
        :param ownerId: ownerId to set. Optional.
        :param minValueProvidedOn: minValueProvidedOn to set. Optional.
        :param maxValueProvidedOn: maxValueProvidedOn to set. Optional.
        :param data: data to set. Optional.
        :param owner: Owner object to set. May be Tenant, Supplier, Practice or User. Optional.
        :param scope: scope enum to set. Tells what type of object owner is. Optional.
        """
        self.owner = owner
        self.scope = scope

    @staticmethod
    def from_json(json_dict):
        """
        Creates a DeviceDataView object from json dict
        :param json_dict: json dictionary with all the required parameters to create a DeviceDataView object. Required.
        :return: DeviceDataView object
        """
        json_dict_holder = {}
        if "deviceDataId" in json_dict:
            json_dict_holder["deviceDataId"] = json_dict["deviceDataId"]
        if "deviceDataModelId" in json_dict:
            json_dict_holder["deviceDataModelId"] = json_dict["deviceDataModelId"]
        if "owner" in json_dict:
            json_dict_holder["ownerId"] = json_dict["ownerId"]
        if "minValueProvidedOn" in json_dict:
            json_dict_holder["minValueProvidedOn"] = json_dict["minValueProvidedOn"]
        if "maxValueProvidedOn" in json_dict:
            json_dict_holder["maxValueProvidedOn"] = json_dict["maxValueProvidedOn"]
        if "data" in json_dict:
            json_dict_holder["data"] = json_dict["data"]

        if "scope" in json_dict:
            json_dict_holder["scope"] = Scope.string_to_scope(json_dict["scope"])
            if "owner" in json_dict:
                json_dict_holder["owner"] = parse_owner_helper(json_dict_holder["scope"], json_dict["owner"])
        return DeviceDataView(**json_dict_holder)

    def get_owner(self):
        """
        :return: the owner
        """
        return self.owner

    def set_owner(self, owner):
        """
        :param owner: the owner to set
        """
        self.owner = owner

    def get_scope_type(self) -> Scope:
        """
        :return: the scope
        """
        return self.scope

    def set_scope_type(self, scope: Scope):
        """
        :param scope: the scope to set
        """
        self.scope = scope

    def __str__(self):
        """
        __str__ overloaded function
        Turns the DeviceDataView object into a string
        :return: string representing the DeviceDataView object
        """
        holder = ""
        holder += "DeviceDataView [deviceDataId=" + (self.deviceDataId.__str__() if self.deviceDataId else "") + \
                  ", deviceDataModelId=" + (self.deviceDataModelId.__str__() if self.deviceDataModelId else "") + \
                  ", ownerId=" + (self.ownerId.__str__() if self.ownerId else "") + \
                  ", minValueProvidedOn=" + (self.minValueProvidedOn.__str__() if self.minValueProvidedOn else "") + \
                  ", maxValueProvidedOn=" + (self.maxValueProvidedOn.__str__() if self.maxValueProvidedOn else "") + \
                  ", data=" + (self.data.__str__() if self.data else "") + \
                  ", scope=" + (Scope.to_string(self.scope) if self.scope else "") + \
                  ", data=" + (self.owner.__str__() if self.owner else "") + \
                  "]"
        return holder
