"""
CustomFieldData Class
"""

import datetime
from galenSDK.model.CustomField import CustomField


class CustomFieldData:
    # private String fieldDataId;
    fieldDataId = None
    # public CustomField field;
    field = None
    # private String entityId;
    entityId = None
    # public Object fieldData;
    fieldData = None
    # public LocalDateTime createdOn;
    createdOn = None
    # private String createdBy;
    createdBy = None
    # public LocalDateTime lastUpdatedOn;
    lastUpdatedOn = None
    # private String lastUpdatedBy;
    lastUpdatedBy = None

    def __init__(self, fieldDataId: str = None, field: CustomField = None, entityId: str = None,
                 fieldData: object = None, createdOn: datetime = None, createdBy: str = None,
                 lastUpdatedOn: datetime = None, lastUpdatedBy: str = None):
        self.fieldDataId = fieldDataId
        self.field = field
        self.entityId = entityId
        self.fieldData = fieldData
        self.createdOn = createdOn
        self.createdBy = createdBy
        self.lastUpdatedOn = lastUpdatedOn
        self.lastUpdatedBy = lastUpdatedBy

    @staticmethod
    def from_json(json_dict):
        """
        takes in a dictionary and returns an CustomFieldData object [Helper function for SDK]
        :return: CustomFieldData
        """
        json_dict_holder = {}

        if "fieldDataId" in json_dict:
            json_dict_holder["fieldDataId"] = json_dict["fieldDataId"]
        if "field" in json_dict:
            json_dict_holder["field"] = CustomField.from_json(json_dict["field"])
        if "entityId" in json_dict:
            json_dict_holder["entityId"] = json_dict["entityId"]
        if "fieldData" in json_dict:
            json_dict_holder["fieldData"] = json_dict["fieldData"]
        if "createdOn" in json_dict:
            json_dict_holder["createdOn"] = json_dict["createdOn"]
        if "createdBy" in json_dict:
            json_dict_holder["createdBy"] = json_dict["createdBy"]
        if "lastUpdatedOn" in json_dict:
            json_dict_holder["lastUpdatedOn"] = json_dict["lastUpdatedOn"]
        if "lastUpdatedBy" in json_dict:
            json_dict_holder["lastUpdatedBy"] = json_dict["lastUpdatedBy"]

        return CustomFieldData(**json_dict_holder)

    def get_field_data_id(self) -> str:
        """
        :return: fieldDataId
        """
        return self.fieldDataId

    def set_field_data_id(self, fieldDataId: str):
        """
        :param fieldDataId: the fieldDataId to set
        """
        self.fieldDataId = fieldDataId

    def get_field(self) -> CustomField:
        """
        :return: field
        """
        return self.field

    def set_field(self, field: CustomField):
        """
        :param field: the field to set
        """
        self.field = field

    def get_entity_id(self) -> str:
        """
        :return: entityId
        """
        return self.entityId

    def set_entity_id(self, entityId: str):
        """
        :param entityId: the entityId to set
        """
        self.entityId = entityId

    def get_field_data(self) -> object:
        """
        :return: fieldData
        """
        return self.fieldData

    def set_field_data(self, fieldData: object):
        """
        :param fieldData: the fieldData to set
        """
        self.fieldData = fieldData

    def get_created_on(self) -> datetime:
        """
        :return: createdOn
        """
        return self.createdOn

    def set_created_on(self, createdOn: datetime):
        """
        :param createdOn: the createdOn to set
        """
        self.createdOn = createdOn

    def get_created_by(self) -> str:
        """
        :return: createdBy
        """
        return self.createdBy

    def set_created_by(self, createdBy: str):
        """
        :param createdBy: the createdBy to set
        """
        self.createdBy = createdBy

    def get_last_updated_on(self) -> datetime:
        """
        :return: lastUpdatedOn
        """
        return self.lastUpdatedOn

    def set_last_updated_on(self, lastUpdatedOn: datetime):
        """
        :param lastUpdatedOn: the lastUpdatedOn to set
        """
        self.lastUpdatedOn = lastUpdatedOn

    def get_last_updated_by(self) -> str:
        """
        :return: lastUpdatedBy
        """
        return self.lastUpdatedBy

    def set_last_updated_by(self, lastUpdatedBy: str):
        """
        :param lastUpdatedBy: the lastUpdatedBy to set
        """
        self.lastUpdatedBy = lastUpdatedBy

    def __hash__(self):
        """
        __hash__ overloaded function
        Hash Function for the CustomFieldData Class
        :returns: An int representing the hash value of the object
        """
        prime = 31
        result = 1
        result = prime * result + (0 if self.fieldDataId is None else self.fieldDataId.__hash__())
        return result

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this CustomFieldData to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, CustomFieldData):
            return False
        if self.fieldDataId is None:
            if other.fieldDataId is not None:
                return False
        if self.fieldDataId != other.fieldDataId:
            return False
        return True

    def __str__(self):
        """
        __str__ overloaded function
        Turns the CustomFieldData object into a string
        :return: string representing the CustomFieldData object
        """
        holder = ""
        holder += "CustomFieldData [fieldDataId=" + (self.fieldDataId.__str__() if self.fieldDataId else "") + \
                  ", field=" + (self.field.__str__() if self.field else "") + \
                  ", entityId=" + (self.entityId.__str__() if self.entityId else "") + \
                  ", fieldData=" + (self.fieldData.__str__() if self.fieldData else "") + \
                  ", createdOn=" + (self.createdOn.__str__() if self.createdOn else "") + \
                  ", createdBy=" + (self.createdBy.__str__() if self.createdBy else "") + \
                  ", lastUpdatedOn=" + (self.lastUpdatedOn.__str__() if self.lastUpdatedOn else "") + \
                  ", lastUpdatedBy=" + (self.lastUpdatedBy.__str__() if self.lastUpdatedBy else "") + \
                  "]"
        return holder

    def __dict__(self):
        """
        __dict__ overloaded function
        :return: a dictionary of the CustomFieldData variables.
        """
        x = {
            "fieldDataId": self.fieldDataId,
            "field": self.field.__dict__(),
            "entityId": self.entityId,
            "fieldData": self.fieldData,
            "createdOn": self.createdOn,
            "createdBy": self.createdBy,
            "lastUpdatedOn": self.lastUpdatedOn,
            "lastUpdatedBy": self.lastUpdatedBy
        }

        return x
