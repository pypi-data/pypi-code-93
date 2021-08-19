"""
Supplier Class
"""

import datetime
from galenSDK.enumeration.Status import Status
from galenSDK.model.CustomFieldData import CustomFieldData
from galenSDK.model.ContactInfo import ContactInfo
from galenSDK.model.HelperFunctions import str_to_date_time, date_time_formater


class Supplier:
    # private String supplierId;
    supplierId = None
    # private String tenantId;
    tenantId = None
    # private String name;
    name = None
    # private String emailAddress;
    emailAddress = None
    # public ContactInfo contactInfo;
    contactInfo = None
    # public Status status;
    status = None
    # public LocalDateTime createdOn;
    createdOn = None
    # private String createdBy;
    createdBy = None
    # public LocalDateTime lastUpdatedOn;
    lastUpdatedOn = None
    # private String lastUpdatedBy;
    lastUpdatedBy = None
    # CustomFieldData list
    customData = []

    # tenantId, name,emailAddress, and contactInfo required
    def __init__(self, supplierId: str = None, tenantId: str = None, name: str = None, emailAddress: str = None,
                 contactInfo: ContactInfo = None, status: Status = None, createdOn: datetime = None,
                 createdBy: str = None, lastUpdatedOn: datetime = None, lastUpdatedBy: str = None,
                 customData=[]):
        """
        Initializer for the Supplier Class
        :param supplierId: supplierId to set. Optional.
        :param tenantId: tenantId to set. Optional.
        :param name: name to set. Optional.
        :param emailAddress: emailAddress to set. Optional.
        :param contactInfo: contactInfo to set. Optional.
        :param status: status to set. Optional.
        :param createdOn: createdOn to set. Optional.
        :param createdBy: createdBy to set. Optional.
        :param lastUpdatedOn: lastUpdatedOn to set. Optional.
        :param lastUpdatedBy: lastUpdatedBy to set. Optional.
        :param customData: customData to set. Optional.
        """
        self.set_supplier_id(supplierId)
        self.set_tenant_id(tenantId)
        self.set_name(name)
        self.set_email_address(emailAddress)
        self.set_contact_info(contactInfo)
        self.set_status(status)
        self.set_created_on(createdOn)
        self.set_created_by(createdBy)
        self.set_last_updated_on(lastUpdatedOn)
        self.set_last_updated_by(lastUpdatedBy)
        self.set_custom_data(customData)

    @staticmethod
    def from_json(json_dict):
        """
        takes in a dictionary and returns a Supplier object [Helper function for SDK]
        :return: Supplier
        """
        json_dict_holder = {}

        if "supplierId" in json_dict:
            json_dict_holder["supplierId"] = json_dict["supplierId"]
        if "tenantId" in json_dict:
            json_dict_holder["tenantId"] = json_dict["tenantId"]
        if "name" in json_dict:
            json_dict_holder["name"] = json_dict["name"]
        if "emailAddress" in json_dict:
            json_dict_holder["emailAddress"] = json_dict["emailAddress"]
        if "contactInfo" in json_dict:
            json_dict_holder["contactInfo"] = ContactInfo.from_json(json_dict["contactInfo"])
        if "status" in json_dict:
            json_dict_holder["status"] = Status.string_to_status(json_dict["status"])
        if "createdOn" in json_dict:
            json_dict_holder["createdOn"] = str_to_date_time(json_dict["createdOn"])
        if "createdBy" in json_dict:
            json_dict_holder["createdBy"] = json_dict["createdBy"]
        if "lastUpdatedOn" in json_dict:
            json_dict_holder["lastUpdatedOn"] = str_to_date_time(json_dict["lastUpdatedOn"])
        if "lastUpdatedBy" in json_dict:
            json_dict_holder["lastUpdatedBy"] = json_dict["lastUpdatedBy"]
        if "customData" in json_dict:
            json_dict_holder["customData"] = json_dict["customData"]
        return Supplier(**json_dict_holder)

    def get_supplier_id(self) -> str:
        """
        :return: supplierId
        """
        return self.supplierId

    def set_supplier_id(self, supplierId: str):
        """
        :param supplierId: the supplierId to set
        """
        self.supplierId = supplierId

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

    def get_email_address(self) -> str:
        """
        :return: emailAddress
        """
        return self.emailAddress

    def set_email_address(self, emailAddress: str):
        """
        :param emailAddress: the emailAddress to set
        """
        self.emailAddress = emailAddress

    def get_contact_info(self) -> contactInfo:
        """
        :return: contactInfo
        """
        return self.contactInfo

    def set_contact_info(self, contactInfo: contactInfo):
        """
        :param contactInfo: the contactInfo to set
        """
        self.contactInfo = contactInfo

    def get_status(self) -> status:
        """
        :return: status
        """
        return self.status

    def set_status(self, status: status):
        """
        :param status: the status to set
        """
        self.status = status

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
        :return:
        """
        self.lastUpdatedBy = lastUpdatedBy

    def get_custom_data(self) -> [CustomFieldData]:
        """
        :return: a list of customFieldData
        """
        return self.customData

    def add_custom_data(self, customData: CustomFieldData):
        """
        :param customData: a customFieldData to add to the customDataField List
        """
        self.customData.append(customData)

    def set_custom_data(self, customData: [CustomFieldData]):
        """
        :param customData: the list of customFieldData to set
        """
        self.customData = customData

    def __hash__(self):
        """
        __hash__ overloaded function
        Hash Function for the Supplier Class
        :returns: An int representing the hash value of the object
        """
        prime = 31
        result = 1
        result = prime * result + (0 if self.supplierId is None else self.supplierId.__hash__())
        return result

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this Supplier to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, Supplier):
            return False
        if self.supplierId is None:
            if other.supplierId is not None:
                return False
        elif self.supplierId != other.supplierId:
            return False
        return True

    def __str__(self):
        """
        __str__ overloaded function
        Turns the Supplier object into a string
        :return: string representing the Supplier object
        """
        # format customDataList
        custom_data_list = []
        if self.customData is not None:
            for cd in self.customData:
                custom_data_list.append(cd.__str__())

        holder = ""
        holder += "Supplier [supplierId=" + (self.supplierId.__str__() if self.supplierId else "") + \
                  ", tenantId=" + (self.tenantId.__str__() if self.tenantId else "") + \
                  ", name=" + (self.name.__str__() if self.name else "") + \
                  ", emailAddress=" + (self.emailAddress.__str__() if self.emailAddress else "") + \
                  ", contactInfo=" + (self.contactInfo.__str__() if self.contactInfo else "") + \
                  ", status=" + (self.status.__str__() if self.status else "") + \
                  ", createdOn=" + (self.createdOn.__str__() if self.createdOn else "") + \
                  ", createdBy=" + (self.createdBy.__str__() if self.createdBy else "") + \
                  ", lastUpdatedOn=" + (self.lastUpdatedOn.__str__() if self.lastUpdatedOn else "") + \
                  ", lastUpdatedBy=" + (self.lastUpdatedBy.__str__() if self.lastUpdatedBy else "") + \
                  ", customData=" + custom_data_list.__str__() + "]"
        return holder

    def __dict__(self):
        """
        __dict__ overloaded function
        :return: a dictionary of the Supplier variables.
        """
        x = {
            "supplierId": self.supplierId,
            "tenantId": self.tenantId,
            "name": self.name,
            "emailAddress": self.emailAddress,
            "contactInfo": self.contactInfo.__dict__(),
            "status": Status.to_string(self.status),
            "createdOn": date_time_formater(self.createdOn),
            "createdBy": self.createdBy,
            "lastUpdatedOn": date_time_formater(self.lastUpdatedOn),
            "lastUpdatedBy": self.lastUpdatedBy
        }
        return x
