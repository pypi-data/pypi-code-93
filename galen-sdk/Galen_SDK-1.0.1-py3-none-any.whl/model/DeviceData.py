"""
DeviceData Class
"""

from galenSDK.model.HelperFunctions import str_to_date_time, date_time_formater


class DeviceData:
    # private String deviceDataId;
    deviceDataId = None
    # private String deviceDataModelId;
    deviceDataModelId = None
    # private String ownerId;
    ownerId = None
    # private String minValueProvidedOn;
    minValueProvidedOn = None
    # private String maxValueProvidedOn;
    maxValueProvidedOn = None
    # private Map<String, Object> data;
    data = []

    def __init__(self, deviceDataId=None, deviceDataModelId=None, ownerId=None, minValueProvidedOn=None,
                 maxValueProvidedOn=None, data=[]):
        """
        Initializer for the DeviceData Class
        :param deviceDataId: deviceDataId to set. Optional.
        :param deviceDataModelId: deviceDataModelId to set. Optional.
        :param ownerId: ownerId to set. Optional.
        :param minValueProvidedOn: minValueProvidedOn to set. Optional.
        :param maxValueProvidedOn: maxValueProvidedOn to set. Optional.
        :param data: data to set. Optional.
        """
        self.deviceDataId = deviceDataId
        self.deviceDataModelId = deviceDataModelId
        self.ownerId = ownerId
        self.minValueProvidedOn = minValueProvidedOn
        self.maxValueProvidedOn = maxValueProvidedOn
        self.data = data

    @staticmethod
    def from_json(json_dict):
        """
        Creates a DeviceData object from json dict
        :param json_dict: json dictionary with all the required parameters to create a DeviceData object. Required.
        :return: DeviceData object
        """
        json_dict_holder = {}
        if "deviceDataId" in json_dict:
            json_dict_holder["deviceDataId"] = json_dict["deviceDataId"]
        if "deviceDataModelId" in json_dict:
            json_dict_holder["deviceDataModelId"] = json_dict["deviceDataModelId"]
        if "ownerId" in json_dict:
            json_dict_holder["ownerId"] = json_dict["ownerId"]
        if "minValueProvidedOn" in json_dict:
            json_dict_holder["minValueProvidedOn"] = str_to_date_time(json_dict["minValueProvidedOn"])
        if "maxValueProvidedOn" in json_dict:
            json_dict_holder["maxValueProvidedOn"] = str_to_date_time(json_dict["maxValueProvidedOn"])
        if "data" in json_dict:
            json_dict_holder["data"] = json_dict["data"]
        return DeviceData(**json_dict_holder)

    def get_device_data_id(self) -> str:
        """
        :return: deviceDataId
        """
        return self.deviceDataId

    def set_device_data_id(self, deviceDataId: str):
        """
        :param deviceDataId: the deviceDataId to set
        """
        self.deviceDataId = deviceDataId

    def get_device_id(self) -> str:
        """
        :return: deviceDataModelId
        """
        return self.deviceDataModelId

    def set_device_id(self, deviceDataModelId: str):
        """
        :param deviceDataModelId: the deviceDataModelId to set
        """
        self.deviceDataModelId = deviceDataModelId

    def get_owner_id(self) -> str:
        """
        :return: ownerId
        """
        return self.ownerId

    def set_owner_id(self, ownerId: str):
        """
        :param ownerId: the ownerId to set
        """
        self.ownerId = ownerId

    def get_min_value_provided_on(self) -> str:
        """
        :return: minValueProvidedOn
        """
        return self.minValueProvidedOn

    def set_min_value_provided_on(self, minValueProvidedOn: str):
        """
        :param minValueProvidedOn: the minValueProvidedOn to set
        """
        self.minValueProvidedOn = minValueProvidedOn

    def get_max_value_provided_on(self) -> str:
        """
        :return: maxValueProvidedOn
        """
        return self.maxValueProvidedOn

    def set_max_value_provided_on(self, maxValueProvidedOn: str):
        """
        :param maxValueProvidedOn: the maxValueProvidedOn to set
        """
        self.maxValueProvidedOn = maxValueProvidedOn

    def get_data(self):  # returns data which should be a dict with {"propertycode":data}
        """
        :return: data
        """
        return self.data

    def set_data(self, data):  # data should be a dict with {"propertycode":data}
        """
        :param data: the data to set
        """
        self.data = data

    def __hash__(self):
        """
        __hash__ overloaded function
        Hash Function for the DeviceData Class
        :returns: An int representing the hash value of the object
        """
        prime = 31
        result = 1
        result = prime * result + (0 if self.deviceDataId is None else self.deviceDataId.__hash__())
        result = prime * result + (0 if self.deviceDataModelId is None else self.deviceDataModelId.__hash__())
        return result

    def __str__(self):
        """
        __str__ overloaded function
        Turns the DeviceData object into a string
        :return: string representing the DeviceData object
        """
        holder = ""
        holder += "DeviceData [deviceDataId=" + (self.deviceDataId.__str__() if self.deviceDataId else "") + \
                  ", deviceDataModelId=" + (self.deviceDataModelId.__str__() if self.deviceDataModelId else "") + \
                  ", ownerId=" + (self.ownerId.__str__() if self.ownerId else "") + \
                  ", minValueProvidedOn=" + (self.minValueProvidedOn.__str__() if self.minValueProvidedOn else "") + \
                  ", maxValueProvidedOn=" + (self.maxValueProvidedOn.__str__() if self.maxValueProvidedOn else "") + \
                  ", data=" + (self.data.__str__() if self.data else "") + "]"
        return holder

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this DeviceData to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, DeviceData):
            return False
        if self.deviceDataId is None:
            if other.deviceDataId is not None:
                return False
        elif self.deviceDataId != other.deviceDataId:
            return False
        if self.deviceDataModelId is None:
            if other.deviceDataModelId is not None:
                return False
        elif self.deviceDataModelId != other.deviceDataModelId:
            return False
        return True

    def __dict__(self):
        """
        __dict__ overloaded function
        :return: a dictionary of the DeviceData variables.
        """
        x = {
            "deviceDataId": self.deviceDataId,
            "deviceDataModelId": self.deviceDataModelId,
            "ownerId": self.ownerId,
            "minValueProvidedOn": date_time_formater(self.minValueProvidedOn),
            "maxValueProvidedOn": date_time_formater(self.maxValueProvidedOn),
            "data": self.data
        }
        return x
