"""
User Class
"""
import datetime
from galenSDK.enumeration.Gender import Gender
from galenSDK.enumeration.Role import Role
from galenSDK.enumeration.Status import Status
from galenSDK.model.UserRole import UserRole
from galenSDK.model.CustomFieldData import CustomFieldData
from galenSDK.model.ContactInfo import ContactInfo
from galenSDK.model.Tenant import Tenant
from galenSDK.model.HelperFunctions import str_to_date_time, date_time_formater


class User:
    # private String userId;
    userId = None
    # private String firstName;
    firstName = None
    # private String middleName;
    middleName = None
    # private String lastName;
    lastName = None
    # private String emailAddress;
    emailAddress = None
    # private ContactInfo contactInfo;
    contactInfo = None
    # private List<UserRole> roles = new ArrayList<UserRole>();
    roles = []  # HOLDER FOR NOW ***********************
    # private Tenant tenant;
    tenant = None
    # private Gender gender;
    gender = None
    # private String dateOfBirth;
    dateOfBirth = None
    # private float height;
    height = None
    # private float weight;
    weight = None
    # private Status status;
    status = None
    # private int failedLoginAttempts;
    failedLoginAttempts = None
    # private boolean lockOut;
    lockOut = None
    # private LocalDateTime lockOutDate;
    lockOutDate = None
    # private boolean acceptedTermsOfUse;
    acceptedTermsOfUse = None
    # private String language;
    language = None
    # private String timeZone;
    timeZone = None
    # private LocalDateTime createdOn;
    createdOn = None
    # private String createdBy;
    createdBy = None
    # private LocalDateTime lastUpdatedOn;
    lastUpdatedOn = None
    # private String lastUpdatedBy;
    lastUpdatedBy = None
    # CustomDataField
    customData = []

    def __init__(self, userId: str = None, firstName: str = None, middleName: str = None, lastName: str = None,
                 emailAddress: str = None, contactInfo: contactInfo = None, roles=[], tenant: Tenant = None,
                 gender: Gender = None, dateOfBirth: str = None, height: float = None, weight: float = None,
                 status: status = None, failedLoginAttempts: int = None, lockOut: bool = None,
                 lockOutDate: datetime = None, acceptedTermsOfUse: bool = None, language: str = None,
                 timeZone: str = None, createdOn: datetime = None, createdBy: str = None,
                 lastUpdatedOn: datetime = None, lastUpdatedBy: str = None, customData=[]):
        """
        Initializer for the User Class
        :param userId: userId to set. Optional.
        :param firstName: firstName to set. Optional.
        :param middleName: middleName to set. Optional.
        :param lastName: lastName to set. Optional.
        :param emailAddress: emailAddress to set. Optional.
        :param contactInfo: contactInfo to set. Optional.
        :param roles: roles to set. Optional.
        :param tenant: tenant to set. Optional.
        :param gender: gender to set. Optional.
        :param dateOfBirth: dateOfBirth to set. Optional.
        :param height: height to set. Optional.
        :param weight: weight to set. Optional.
        :param status: status to set. Optional.
        :param failedLoginAttempts: failedLoginAttempts to set. Optional.
        :param lockOut: lockOut to set. Optional.
        :param lockOutDate: lockOutDate to set. Optional.
        :param acceptedTermsOfUse: acceptedTermsOfUse to set. Optional.
        :param language: language to set. Optional.
        :param timeZone: timeZone to set. Optional.
        :param createdOn: createdOn to set. Optional.
        :param createdBy: createdBy to set. Optional.
        :param lastUpdatedOn: lastUpdatedOn to set. Optional.
        :param lastUpdatedBy: lastUpdatedBy to set. Optional.
        :param customData: customData to set. Optional.
        """
        self.userId = userId
        self.firstName = firstName
        self.middleName = middleName
        self.lastName = lastName
        self.emailAddress = emailAddress
        self.contactInfo = contactInfo
        self.roles = roles
        self.tenant = tenant
        self.gender = gender
        self.dateOfBirth = dateOfBirth
        self.height = height
        self.weight = weight
        self.status = status
        self.failedLoginAttempts = failedLoginAttempts
        self.lockOut = lockOut
        self.lockOutDate = lockOutDate
        self.acceptedTermsOfUse = acceptedTermsOfUse
        self.language = language
        self.timeZone = timeZone
        self.createdOn = createdOn
        self.createdBy = createdBy
        self.lastUpdatedOn = lastUpdatedOn
        self.lastUpdatedBy = lastUpdatedBy
        self.customData = customData

    @staticmethod
    def from_json(json_dict):
        """
        Takes in a dictionary and returns an User object [Helper function for SDK]
        :param json_dict: dictionary to turn into User Object
        :return: User
        """
        json_dict_holder = {}

        if "userId" in json_dict:
            json_dict_holder["userId"] = json_dict["userId"]
        if "firstName" in json_dict:
            json_dict_holder["firstName"] = json_dict["firstName"]
        if "middleName" in json_dict:
            json_dict_holder["middleName"] = json_dict["middleName"]
        if "lastName" in json_dict:
            json_dict_holder["lastName"] = json_dict["lastName"]
        if "emailAddress" in json_dict:
            json_dict_holder["emailAddress"] = json_dict["emailAddress"]
        if "contactInfo" in json_dict:
            json_dict_holder["contactInfo"] = ContactInfo.from_json(json_dict["contactInfo"])
        if "roles" in json_dict:
            list_of_roles = []
            list_of_roles_dicts = json_dict["roles"]
            for role in list_of_roles_dicts:
                list_of_roles.append(UserRole.from_json(role))
            json_dict_holder["roles"] = list_of_roles
        if "tenant" in json_dict:
            json_dict_holder["tenant"] = Tenant.from_json(json_dict["tenant"])
        if "gender" in json_dict:
            json_dict_holder["gender"] = Gender.string_to_gender(json_dict["gender"])
        if "dateOfBirth" in json_dict:
            json_dict_holder["dateOfBirth"] = json_dict["dateOfBirth"]
        if "height" in json_dict:
            json_dict_holder["height"] = json_dict["height"]
        if "weight" in json_dict:
            json_dict_holder["weight"] = json_dict["weight"]
        if "status" in json_dict:
            json_dict_holder["status"] = Status.string_to_status(json_dict["status"])
        if "failedLoginAttempts" in json_dict:
            json_dict_holder["failedLoginAttempts"] = json_dict["failedLoginAttempts"]
        if "lockOut" in json_dict:
            json_dict_holder["lockOut"] = json_dict["lockOut"]
        if "lockOutDate" in json_dict:
            json_dict_holder["lockOutDate"] = json_dict["lockOutDate"]
        if "acceptedTermsOfUse" in json_dict:
            json_dict_holder["acceptedTermsOfUse"] = json_dict["acceptedTermsOfUse"]
        if "language" in json_dict:
            json_dict_holder["language"] = json_dict["language"]
        if "timeZone" in json_dict:
            json_dict_holder["timeZone"] = json_dict["timeZone"]
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
        return User(**json_dict_holder)

    def get_user_id(self) -> str:
        """
        :return: userId
        """
        return self.userId

    def set_user_id(self, userID: str):
        """
        :param userID: the userId to set
        """
        self.userId = userID

    def get_first_name(self) -> str:
        """
        :return: firstName
        """
        return self.firstName

    def set_first_name(self, firstName: str):
        """
        :param firstName: the firstName to set
        """
        self.firstName = firstName

    def get_middle_name(self) -> str:
        """
        :return: middleName
        """
        return self.middleName

    def set_middle_name(self, middleName: str):
        """
        :param middleName: the middleName to set
        """
        self.middleName = middleName

    def get_last_name(self) -> str:
        """
        :return: lastName
        """
        return self.lastName

    def set_last_name(self, lastName: str):
        """
        :param lastName: the lastName to set
        """
        self.lastName = lastName

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

    def get_roles(self):  # return List<UserRole>
        """
        :return: roles [list of UserRole]
        """
        return self.roles

    def add_role(self, role: Role):
        """
        :param role: a UserRole to add to the list of UserRoles
        """
        self.roles.append(role)

    def set_roles(self, roles):  # roles is type List<UserRole>
        """
        :param roles: the roles to set
        """
        self.roles = roles

    def get_tenant(self) -> Tenant:
        """
        :return: tenant
        """
        return self.tenant

    def set_tenant(self, tenant: Tenant):
        """
        :param tenant: the tenant to set
        """
        self.tenant = tenant

    def get_gender(self) -> Gender:
        """
        :return: gender
        """
        return self.gender

    def set_gender(self, gender: Gender):
        """
        :param gender: the gender to set
        """
        self.gender = gender

    def get_date_of_birth(self) -> str:
        """
        :return: dateOfBirth
        """
        return self.dateOfBirth

    def set_date_of_birth(self, dateOfBirth: str):
        """
        :param dateOfBirth: the dateOfBirth to set
        """
        self.dateOfBirth = dateOfBirth

    def get_height(self):  # output is float
        """
        :return: height
        """
        return self.height

    def set_height(self, height):  # height is type float
        """
        :param height: the height to set
        """
        self.height = height

    def get_weight(self):  # output is type float
        """
        :return: weight
        """
        return self.weight

    def set_weight(self, weight):  # weight is type float
        """
        :param weight: the weight to set
        """
        self.weight = weight

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

    def get_failed_login_attempts(self) -> int:
        """
        :return: failedLoginAttempts
        """
        return self.failedLoginAttempts

    def set_failed_login_attempts(self, failedLoginAttempts: int):
        """
        :param failedLoginAttempts: the failedLoginAttempts to set
        """
        self.failedLoginAttempts = failedLoginAttempts

    def is_lock_out(self) -> bool:
        """
        :return: lockOut
        """
        return self.lockOut

    def set_lock_out(self, lockOut: bool):
        """
        :param lockOut: the lockOut to set
        """
        self.lockOut = lockOut

    def get_lock_out_date(self) -> datetime:
        """
        :return: lockOutDate
        """
        return self.lockOutDate

    def set_lock_out_date(self, lockOutDate: datetime):
        """
        :param lockOutDate: the lockOutDate to set
        """
        self.lockOutDate = lockOutDate

    def is_accepted_terms_of_use(self) -> bool:
        """
        :return: acceptedTermsOfUse
        """
        return self.acceptedTermsOfUse

    def set_accepted_terms_of_use(self, acceptedTermsOfUse: bool):
        """
        :param acceptedTermsOfUse: the acceptedTermsOfUse to set
        """
        self.acceptedTermsOfUse = acceptedTermsOfUse

    def get_language(self) -> str:
        """
        :return: language
        """
        return self.language

    def set_language(self, language: str):
        """
        :param language: the language to set
        """
        self.language = language

    def get_time_zone(self) -> str:
        """
        :return: timeZone [datetime]
        """
        return self.timeZone

    def set_time_zone(self, timeZone: str):
        """
        :param timeZone: the timeZone to set
        """
        self.timeZone = timeZone

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
        Hash Function for the User Class
        :returns: An int representing the hash value of the object
        """
        prime = 31
        result = 1
        result = prime * result + (0 if self.tenantId is None else self.tenantId.__hash__())
        return result

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this User to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, User):
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
        Turns the User object into a string
        :return: string representing the user object
        """
        # format customDataList
        custom_data_list = []
        if self.customData is not None:
            for cd in self.customData:
                custom_data_list.append(cd.__str__())

        holder = ""
        holder += "User [userId=" + (self.userId.__str__() if self.userId else "") + \
                  ", firstName=" + (self.firstName.__str__() if self.firstName else "") + \
                  ", middleName=" + (self.middleName.__str__() if self.middleName else "") + \
                  ", lastName=" + (self.lastName.__str__() if self.lastName else "") + \
                  ", emailAddress=" + (self.emailAddress.__str__() if self.emailAddress else "") + \
                  ", contactInfo=" + (self.contactInfo.__str__() if self.contactInfo else "") + \
                  ", roles=" + (self.roles.__str__() if self.roles else "") + \
                  ", tenant=" + (self.tenant.__str__() if self.tenant else "") + \
                  ", gender=" + (self.gender.__str__() if self.gender else "") + \
                  ", dateOfBirth=" + (self.dateOfBirth.__str__() if self.dateOfBirth else "") + \
                  ", height=" + (self.height.__str__() if self.height else "") + \
                  ", weight=" + (self.weight.__str__() if self.weight else "") + \
                  ", status=" + (self.status.__str__() if self.status else "") + \
                  ", failedLoginAttempts=" + (self.failedLoginAttempts.__str__() if self.failedLoginAttempts else "") +\
                  ", lockOut=" + (self.lockOut.__str__() if self.lockOut else "") + \
                  ", lockOutDate=" + (self.lockOutDate.__str__() if self.lockOutDate else "") + \
                  ", acceptedTermsOfUse=" + (self.acceptedTermsOfUse.__str__() if self.acceptedTermsOfUse else "") + \
                  ", language=" + (self.language.__str__() if self.language else "") + \
                  ", timeZone=" + (self.timeZone.__str__() if self.timeZone else "") + \
                  ", createdOn=" + (self.createdOn.__str__() if self.createdOn else "") + \
                  ", createdBy=" + (self.createdBy.__str__() if self.createdBy else "") + \
                  ", lastUpdatedOn=" + (self.lastUpdatedOn.__str__() if self.lastUpdatedOn else "") + \
                  ", lastUpdatedBy=" + (self.lastUpdatedBy.__str__() if self.lastUpdatedBy else "") + \
                  ", customData=" + custom_data_list.__str__() + "]"
        return holder

    ###################################################################################################################
    ###################################################################################################################

    # Helps set up roles so that we can pass it into a json file happy-leee
    @staticmethod
    def dict_role_helper(roles) -> [UserRole]:
        """
        Helper function to put the roles [from role object or json format] into a list so we can put it into dictionary
        format - helper function
        :param roles: list of roles
        :return: list of roles to be used in __dict__
        """
        if roles is None:
            return []
        else:
            dictHolder = []
            for role in roles:
                if isinstance(role, dict):
                    dictHolder.append(role)
                else:
                    dictHolder.append(role.__dict__())

            return dictHolder

    def __dict__(self):
        """
        __dict__ overloaded function
        :return: a dictionary of the user variables. CustomData not included.
        """
        x = {
            "userId": self.userId,
            "firstName": self.firstName,
            "middleName": self.middleName,
            "lastName": self.lastName,
            "emailAddress": self.emailAddress,
            "tenant": self.tenant.__dict__(),
            "contactInfo": self.contactInfo.__dict__(),
            "roles": User.dict_role_helper(self.get_roles()),
            "gender": Gender.to_string(self.gender),
            "dateOfBirth": self.dateOfBirth,
            "height": self.height,
            "weight": self.weight,
            "status": Status.to_string(self.status),
            "failedLoginAttempts": self.failedLoginAttempts,
            "lockOut": self.lockOut,
            "lockOutDate": self.lockOutDate,
            "acceptedTermsOfUse": self.acceptedTermsOfUse,
            "language": self.language,
            "timeZone": self.timeZone,
            "createdOn": date_time_formater(self.createdOn),
            "createdBy": self.createdBy,
            "lastUpdatedOn": date_time_formater(self.lastUpdatedOn),
            "lastUpdatedBy": self.lastUpdatedBy
        }
        return x
