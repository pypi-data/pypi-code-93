"""
CustomField Class
"""

from galenSDK.enumeration.FieldArea import FieldArea
from galenSDK.enumeration.FieldType import FieldType
import datetime


class CustomField:
    # private String fieldId;
    fieldId = None
    # private String tenantId;
    tenantId = None
    # public FieldArea area;
    area = None
    # private String name;
    name = None
    # public FieldType type;
    type = None
    # public List<String> optionValues = new ArrayList<String>();
    optionValues = None
    # public boolean required = false;
    required = False
    # public int displayOrder = -1;
    displayOrder = -1
    # private String validationExpression;
    validationExpression = None
    # public LocalDateTime createdOn;
    createdOn = None
    # private String createdBy;
    createdBy = None
    # public LocalDateTime lastUpdatedOn;
    lastUpdatedOn = None
    # private String lastUpdatedBy;
    lastUpdatedBy = None

    def __init__(self, fieldId=None, tenantId=None, area=None, name=None, type=None, optionValues=None, required=False,
                 displayOrder=-1, validationExpression=None, createdOn=None, createdBy=None, lastUpdatedOn=None,
                 lastUpdatedBy=None):
        """
        Initializer for the CustomField class
        :param fieldId: fieldId to use. Optional.
        :param tenantId: tenantId to use. Optional.
        :param area: area to use. Optional.
        :param name: name to use. Optional.
        :param type: type to use. Optional.
        :param optionValues: optionValues to use. Optional.
        :param required: required to use. Optional.
        :param displayOrder: displayOrder to use. Optional.
        :param validationExpression: validationExpression to use. Optional.
        :param createdOn: createdOn to use. Optional.
        :param createdBy: createdBy to use. Optional.
        :param lastUpdatedOn: lastUpdatedOn to use. Optional.
        :param lastUpdatedBy: lastUpdatedBy to use. Optional.
        """
        self.fieldId = fieldId
        self.tenantId = tenantId
        self.area = area
        self.name = name
        self.type = type
        self.optionValues = optionValues
        self.required = required
        self.displayOrder = displayOrder
        self.validationExpression = validationExpression
        self.createdOn = createdOn
        self.createdBy = createdBy
        self.lastUpdatedOn = lastUpdatedOn
        self.lastUpdatedBy = lastUpdatedBy

    @staticmethod
    def from_json(json_dict):
        """
        takes in a dictionary and returns an CustomField object [Helper function for SDK]
        :return: User
        """
        json_dict_holder = {}
        if "fieldId" in json_dict:
            json_dict_holder["fieldId"] = json_dict["fieldId"]
        if "tenantId" in json_dict:
            json_dict_holder["tenantId"] = json_dict["tenantId"]
        if "area" in json_dict:
            json_dict_holder["area"] = FieldArea.from_string(json_dict["area"])
        if "name" in json_dict:
            json_dict_holder["name"] = json_dict["name"]
        if "type" in json_dict:
            json_dict_holder["type"] = FieldType.from_string(json_dict["type"])
        if "optionValues" in json_dict:
            json_dict_holder["optionValues"] = json_dict["optionValues"]
        if "required" in json_dict:
            json_dict_holder["required"] = json_dict["required"]
        if "displayOrder" in json_dict:
            json_dict_holder["displayOrder"] = json_dict["displayOrder"]
        if "validationExpression" in json_dict:
            json_dict_holder["validationExpression"] = json_dict["validationExpression"]
        if "createdOn" in json_dict:
            json_dict_holder["createdOn"] = json_dict["createdOn"]
        if "createdBy" in json_dict:
            json_dict_holder["createdBy"] = json_dict["createdBy"]
        if "lastUpdatedOn" in json_dict:
            json_dict_holder["lastUpdatedOn"] = json_dict["lastUpdatedOn"]
        if "lastUpdatedBy" in json_dict:
            json_dict_holder["lastUpdatedBy"] = json_dict["lastUpdatedBy"]
        return CustomField(**json_dict_holder)

    def get_field_id(self) -> str:
        """
        :return: fieldId
        """
        return self.fieldId

    def set_field_id(self, fieldId: str):
        """
        :param fieldId: the fieldId to set
        """
        self.fieldId = fieldId

    def get_tenant_id(self) -> str:
        """
        :return: tenantId
        """
        return self.tenantId

    def set_tenant_id(self, tenantId: str):
        """
        :param tenantId: the tenantId to set
        """
        self.tenantId = tenantId

    def get_area(self) -> FieldArea:
        """
        :return: area
        """
        return self.area

    def set_area(self, area: FieldArea):
        """
        :param area: the area to set
        """
        self.area = area

    def get_name(self) -> str:
        """
        :return: name
        """
        return self.name

    def set_name(self, name: str):
        """
        :param name: the name to set
        """
        self.name = name

    def get_type(self) -> FieldType:
        """
        :return: type
        """
        return self.type

    def set_type(self, type: FieldType):
        """
        :param type: the type to set
        """
        self.type = type

    def get_option_values(self) -> [str]:
        """
        :return: optionValues [a list of strings]
        """
        return self.optionValues

    def set_option_values(self, optionValues: [str]):
        """
        :param optionValues: the optionValues to set
        """
        self.optionValues = optionValues

    def is_required(self) -> bool:
        """
        :return: required [boolean]
        """
        return self.required

    def set_required(self, required: bool):
        """
        :param required: if required input True, else input false
        """
        self.required = required

    def get_display_order(self) -> int:
        """
        :return: displayOrder
        """
        return self.displayOrder

    def set_display_order(self, displayOrder: int):
        """
        :param displayOrder: the displayOrder to set
        """
        self.displayOrder = displayOrder

    def get_validation_expression(self) -> str:
        """
        :return: validationExpression
        """
        return self.validationExpression

    def set_validation_expression(self, validationExpression: str):
        """
        :param validationExpression: the validationExpression to set
        """
        self.validationExpression = validationExpression

    def get_created_on(self) -> datetime:
        """
        :return: createdOn [datetime]
        """
        return self.createdOn

    def set_created_on(self, createdOn: datetime):
        """
        :param createdOn: the createdOn to set [datetime]
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
        Hash Function for the CustomField Class
        :returns: An int representing the hash value of the object
        """
        prime = 31
        result = 1
        result = prime * result + (0 if self.fieldId is None else self.fieldId.__hash__())
        return result

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this CustomField to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, CustomField):
            return False
        if self.fieldId is None:
            if other.fieldId is not None:
                return False
        elif self.fieldId != other.fieldId:
            return False
        return True

    def __str__(self):
        """
        __str__ overloaded function
        Turns the CustomField object into a string
        :return: string representing the CustomField object
        """
        holder = ""
        holder += "CustomField [fieldId=" + (self.fieldId.__str__() if self.fieldId else "") + \
                  ", tenantId=" + (self.tenantId.__str__() if self.tenantId else "") + \
                  ", area=" + (self.area.__str__() if self.area else "") + \
                  ", name=" + (self.name.__str__() if self.name else "") + \
                  ", type=" + (self.type.__str__() if self.type else "") + \
                  ", optionValues=" + (self.optionValues.__str__() if self.optionValues else "") + \
                  ", required=" + (self.required.__str__() if self.required else "") + \
                  ", displayOrder=" + (self.displayOrder.__str__() if self.displayOrder else "") + \
                  ", validationExpression=" + (
                      self.validationExpression.__str__() if self.validationExpression else "") + \
                  ", createdOn=" + (self.createdOn.__str__() if self.createdOn else "") + \
                  ", createdBy=" + (self.createdBy.__str__() if self.createdBy else "") + \
                  ", lastUpdatedOn=" + (self.lastUpdatedOn.__str__() if self.lastUpdatedOn else "") + \
                  ", lastUpdatedBy=" + (self.lastUpdatedBy.__str__() if self.lastUpdatedBy else "") + \
                  "]"
        return holder

    def __dict__(self):
        """
        __dict__ overloaded function
        :return: a dictionary of the CustomField variables.
        """
        x = {
            "fieldId": self.fieldId,
            "tenantId": self.tenantId,
            "area": FieldArea.to_string(self.area),
            "name": self.name,
            "type": FieldType.to_string(self.type),
            "optionValues": self.optionValues,
            "required": self.required,
            "displayOrder": self.displayOrder,
            "validationExpression": self.validationExpression,
            "createdOn": self.createdOn,
            "createdBy": self.createdBy,
            "lastUpdatedOn": self.lastUpdatedOn,
            "lastUpdatedBy": self.lastUpdatedBy
        }
        return x
