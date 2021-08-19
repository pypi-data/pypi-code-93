"""
DeviceDataRecord Class
"""


class DeviceDataRecord:
    # private String deviceDataId;
    deviceDataId = None
    # private String ownerId;
    ownerId = None
    # private Map<String, Object> data;
    data = None

    def __init__(self, deviceDataId: str, userId: str, data):
        self.deviceDataId = deviceDataId
        self.userId = userId
        self.data = data

    def get_device_data_id(self) -> str:
        """
        :return: the deviceDataId
        """
        return self.deviceDataId

    def set_device_data_id(self, deviceDataId: str):
        """
        :param deviceDataId: the deviceDataId to set
        """
        self.deviceDataId = deviceDataId

    def get_user_id(self):
        """
        :return: the userId
        """
        return self.userId

    def set_user_id(self, userId: str):
        """
        :param userId: the userId to set
        """
        self.userId = userId

    def get_data(self):
        """
        :return: the data
        """
        return self.data

    def set_data(self, data):
        """
        :param data: the data to set
        """
        self.data = data

    def __hash__(self):
        """
        __hash__ overloaded function
        Hash Function for the DeviceCriteria Class
        :returns: An int representing the hash value of the object
        """
        prime = 31
        result = 1
        result = prime * result + (0 if self.data is None else self.data.__hash__())
        result = prime * result + (0 if self.deviceDataId is None else self.deviceDataId.__hash__())
        result = prime * result + (0 if self.userId is None else self.userId.__hash__())
        return result

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this DeviceDataRecord to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, DeviceDataRecord):
            return False
        if self.data is None:
            if other.data is not None:
                return False
        elif self.data != other.data:
            return False
        if self.deviceDataId is None:
            if other.deviceDataId is not None:
                return False
        elif self.deviceDataId != other.deviceDataId:
            return False
        if self.userId is None:
            if other.userId is not None:
                return False
        elif self.userId != other.userId:
            return False
        return True

    def __str__(self):
        """
        __str__ overloaded function
        Turns the DeviceDataRecord object into a string
        :return: string representing the DeviceDataRecord object
        """
        holder = ""
        holder += "DeviceDataArray [deviceDataId=" + self.deviceDataId
        holder += ", userId=" + self.userId
        holder += ", data=" + self.data + "]"
        return holder
