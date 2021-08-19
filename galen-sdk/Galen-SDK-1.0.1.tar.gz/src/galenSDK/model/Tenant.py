"""
Tenant Class
"""

from datetime import datetime

from galenSDK.enumeration.Status import Status
from galenSDK.model.ContactInfo import ContactInfo
from galenSDK.model.HelperFunctions import str_to_date_time
from galenSDK.model.HelperFunctions import date_time_formater


class Tenant:
    # private String tenantId;
    tenantId = None
    # private String name;
    name = None
    # private String emailAddress;
    emailAddress = None
    # public ContactInfo contactInfo;
    contactInfo = None
    # private String subdomain;
    subdomain = None
    # private String subscriptionLevel;
    subscriptionLevel = None
    # private String logo;
    logo = None
    # private String customCSS;
    customCSS = None
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
    # private String accountId;
    accountId = None

    def __init__(self, tenantId: str = None, name: str = None, emailAddress: str = None, contactInfo: contactInfo = None,
                 subdomain: str = None, subscriptionLevel: str = None, logo: str = None, customCSS: str = None,
                 status: status = None, createdOn: datetime = None, createdBy: str = None,
                 lastUpdatedOn: datetime = None,
                 lastUpdatedBy: str = None, accountId: str = None):
        """
        Initializer for the Tenant Class
        :param tenantId: tenantId to set. Optional.
        :param name: name to set. Optional.
        :param emailAddress: emailAddress to set. Optional.
        :param contactInfo: contactInfo to set. Optional.
        :param subdomain: subdomain to set. Optional.
        :param subscriptionLevel: subscriptionLevel to set. Optional.
        :param logo: logo to set. Optional.
        :param customCSS: customCSS to set. Optional.
        :param status: status to set. Optional.
        :param createdOn: createdOn to set. Optional.
        :param createdBy: createdBy to set. Optional.
        :param lastUpdatedOn: lastUpdatedOn to set. Optional.
        :param lastUpdatedBy: lastUpdatedBy to set. Optional.
        :param accountId: accountId to set. Optional.
        """
        self.tenantId = tenantId
        self.name = name
        self.emailAddress = emailAddress
        self.contactInfo = contactInfo
        self.subdomain = subdomain
        self.subscriptionLevel = subscriptionLevel
        self.logo = logo
        self.customCSS = customCSS
        self.status = status
        self.createdOn = createdOn
        self.createdBy = createdBy
        self.lastUpdatedOn = lastUpdatedOn
        self.lastUpdatedBy = lastUpdatedBy
        self.accountId = accountId

    @staticmethod
    def from_json(json_dict):
        """
        takes in a dictionary and returns a Tenant object [Helper function for SDK]
        :return: Tenant
        """
        json_dict_holder = {}
        if "tenantId" in json_dict:
            json_dict_holder["tenantId"] = json_dict["tenantId"]
        if "name" in json_dict:
            json_dict_holder["name"] = json_dict["name"]
        if "emailAddress" in json_dict:
            json_dict_holder["emailAddress"] = json_dict["emailAddress"]
        if "contactInfo" in json_dict:
            json_dict_holder["contactInfo"] = ContactInfo.from_json(json_dict["contactInfo"])
        if "subdomain" in json_dict:
            json_dict_holder["subdomain"] = json_dict["subdomain"]
        if "subscriptionLevel" in json_dict:
            json_dict_holder["subscriptionLevel"] = json_dict["subscriptionLevel"]
        if "logo" in json_dict:
            json_dict_holder["logo"] = json_dict["logo"]
        if "customCSS" in json_dict:
            json_dict_holder["customCSS"] = json_dict["customCSS"]
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
        if "accountId" in json_dict:
            json_dict_holder["accountId"] = json_dict["accountId"]
        return Tenant(**json_dict_holder)

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

    def get_contact_info(self) -> ContactInfo:
        """
        :return: contactInfo
        """
        return self.contactInfo

    def set_contact_info(self, contactInfo: ContactInfo):
        """
        :param contactInfo: the contactInfo to set
        """
        self.contactInfo = contactInfo

    def get_subdomain(self) -> str:
        """
        :return: subdomain
        """
        return self.subdomain

    def set_subdomain(self, subdomain: str):
        """
        :param subdomain: the subdomain to set
        """
        self.subdomain = subdomain

    def get_subscription_level(self) -> str:
        """
        :return: subscriptionLevel
        """
        return self.subscriptionLevel

    def set_subscription_level(self, subscriptionLevel: str):
        """
        :param subscriptionLevel: the subscriptionLevel to set
        """
        self.subscriptionLevel = subscriptionLevel

    def get_logo(self) -> str:
        """
        :return: logo
        """
        return self.logo

    def set_logo(self, logo: str):
        """
        :param logo: the logo to set
        """
        self.logo = logo

    def get_custom_css(self) -> str:
        """
        :return: customCSS
        """
        return self.customCSS

    def set_custom_css(self, customCSS: str):
        """
        :param customCSS: the customCSS to set
        """
        self.customCSS = customCSS

    def get_status(self) -> Status:
        """
        :return: status
        """
        return self.status

    def set_status(self, status: Status):
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
        """
        self.lastUpdatedBy = lastUpdatedBy

    def get_account_id(self) -> str:
        """
        :return: accountId
        """
        return self.accountId

    def set_account_id(self, accountId: str):
        """
        :param accountId: the accountId to set
        """
        self.accountId = accountId

    def __hash__(self):
        """
        __hash__ overloaded function
        Hash Function for the Tenant Class
        :returns: An int representing the hash value of the object
        """
        prime = 31
        result = 1
        result = prime * result + (0 if self.tenantId is None else self.tenantId.__hash__())
        return result

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this Tenant to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, Tenant):
            return False
        if self.tenantId is None:
            if other.tenantId is not None:
                return False
        elif self.tenantId != other.tenantId:
            return False
        return True

    def __str__(self):
        """
        __str__ overloaded function
        Turns the Tenant object into a string
        :return: string representing the Tenant object
        """
        holder = ""
        holder += "Tenant [tenantId=" + (self.tenantId.__str__() if self.tenantId else "") + \
                  ", name=" + (self.name.__str__() if self.name else "") + \
                  ", emailAddress=" + (self.emailAddress.__str__() if self.emailAddress else "") + \
                  ", contactInfo=" + (self.contactInfo.__str__() if self.contactInfo else "") + \
                  ", subdomain=" + (self.subdomain.__str__() if self.subdomain else "") + \
                  ", subscriptionLevel=" + (self.subscriptionLevel.__str__() if self.subscriptionLevel else "") + \
                  ", logo=" + (self.logo.__str__() if self.logo else "") + \
                  ", customCSS=" + (self.customCSS.__str__() if self.customCSS else "") + \
                  ", status=" + (self.status.__str__() if self.status else "") + \
                  ", createdOn=" + (self.createdOn.__str__() if self.createdOn else "") + \
                  ", createdBy=" + (self.createdBy.__str__() if self.createdBy else "") + \
                  ", lastUpdatedOn=" + (self.lastUpdatedOn.__str__() if self.lastUpdatedOn else "") + \
                  ", lastUpdatedBy=" + (self.lastUpdatedBy.__str__() if self.lastUpdatedBy else "") + \
                  ", accountId=" + (self.accountId.__str__() if self.accountId else "") + "]"
        return holder

    def __dict__(self):
        """
        __dict__ overloaded function
        :return: a dictionary of the Tenant variables.
        """
        x = {
            "tenantId": self.tenantId,
            "name": self.name,
            "emailAddress": self.emailAddress,
            "contactInfo": self.contactInfo.__dict__(),
            "subdomain": self.subdomain,
            "subscriptionLevel": self.subscriptionLevel,
            "logo": self.logo,
            "customCSS": self.customCSS,
            "status": Status.to_string(self.status),
            "createdOn": date_time_formater(self.createdOn),
            "createdBy": self.createdBy,
            "lastUpdatedOn": date_time_formater(self.lastUpdatedOn),
            "lastUpdatedBy": self.lastUpdatedBy,
            "accountId": self.accountId
        }
        return x
