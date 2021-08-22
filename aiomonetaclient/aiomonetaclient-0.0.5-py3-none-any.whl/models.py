import dataclasses
import json
import typing
from typing import List, Optional, Tuple, Union


KEY = 'key'


@dataclasses.dataclass
class Base:
    def __post_init__(self):
        self.__dataclass_fields__ = {
            field_name: self.__dataclass_fields__[field_name]
            for field_name in self.__dataclass_fields__
            if getattr(self, self.__dataclass_fields__[field_name].name, None) is not None
        }

    def asdict(self):
        return dataclasses.asdict(self)

    def to_json(self, indent: Optional[int] = None):
        return json.dumps(self.asdict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict) -> 'Base':
        res = {}
        for field_name, field in cls.__dataclass_fields__.items():
            replace_field_name = field_name.replace('_', '-')
            if dataclasses.is_dataclass(field.type):
                res[field_name] = field.type.from_dict(data.get(field_name))
            elif isinstance(field.type, typing._GenericAlias):
                value = data.get(field_name, data.get(replace_field_name))
                value_type = field.type.__args__[0]
                if field.type._name in ('List', 'Tuple'):
                    if value is not None:
                        if isinstance(value, (list, tuple)):
                            if dataclasses.is_dataclass(value_type):
                                res[field_name] = [value_type.from_dict(item) for item in value]
                            else:
                                res[field_name] = value
                        else:
                            raise ValueError
                elif field.type._name in ('Optional', 'Union', None):
                    if value is not None:
                        if dataclasses.is_dataclass(value_type):
                            res[field_name] = value_type.from_dict(value)
                        elif isinstance(value_type, typing._GenericAlias) and value_type._name in ('List', 'Tuple'):
                            value_type = value_type.__args__[0]
                            if value is not None:
                                if isinstance(value, (list, tuple)):
                                    if dataclasses.is_dataclass(value_type):
                                        res[field_name] = [value_type.from_dict(item) for item in value]
                                    else:
                                        res[field_name] = value
                                else:
                                    raise ValueError
                        else:
                            res[field_name] = value
            else:
                res[field_name] = data.get(field_name, data.get(replace_field_name))
        return cls(**res)


@dataclasses.dataclass
class UsernameToken(Base):
    Username: str
    Password: str


@dataclasses.dataclass
class Security(Base):
    UsernameToken: UsernameToken


@dataclasses.dataclass
class Header(Base):
    Security: Security

    @classmethod
    def make_auth_header(cls, username: str, password: str) -> 'Header':
        return cls(Security(UsernameToken(Username=username, Password=password)))


@dataclasses.dataclass
class Method(Base):
    __type__ = None

    @classmethod
    def from_dict(cls, data) -> 'Method':
        if cls.__type__ is None:
            return super(Method, cls).from_dict(data)
        return cls(value=cls.__type__(data))

    def is_base_type(self):
        return self.__type__ is None

    def get_id(self):
        if self.is_base_type():
            raise NotImplementedError
        return self.value


@dataclasses.dataclass
class Filter(Base):
    phone: str


@dataclasses.dataclass
class FindProfileInfoRequest(Method):
    filter: Filter

    @classmethod
    def by_phone(cls, phone: str) -> 'FindProfileInfoRequest':
        return cls(Filter(phone=f'CELL_PHONE:{phone}'))


@dataclasses.dataclass
class CreateAccountRequest(Method):
    unitId: int
    alias: str
    paymentPassword: str
    paymentPasswordType: str = 'STATIC'
    currency: str = 'RUB'


@dataclasses.dataclass
class Attribute(Base):
    value: str
    key: str
    approved: Optional[bool] = None


PROFILE_ATTRIBUTES = [
    'timezone',
    'name',
    'parentid',
    'profileid',
    'primaryaccountid',
    'signupdate',
    'profileType',
    'unitid',
    'cell_phone',
    'alias',
    'last_name',
    'first_name',
    'middle_initial_name',
    'nationality',
]

ATTRIBUTE_CLASSES = [
    dataclasses.make_dataclass(
        f'{attribute}Attribute',
        [(KEY, str, dataclasses.field(default=attribute))],
        bases=(Attribute, )
    )
    for attribute in PROFILE_ATTRIBUTES
]

AttributeClasses = dataclasses.make_dataclass(
    'AttributeClasses',
    [
        (field.default, Attribute, dataclasses.field(default=clss))
        for clss in ATTRIBUTE_CLASSES
        for field in dataclasses.fields(clss)
        if field.name == KEY
    ]
)()


@dataclasses.dataclass
class Profile(Base):
    attribute: List[Attribute]

    @classmethod
    def make_anon_profile(cls, phone: str):
        return cls(
            attribute=[
                AttributeClasses.cell_phone(value=phone, approved=True),
                AttributeClasses.alias(value=phone),
            ]
        )

    @property
    def attributes(self):
        return dataclasses.make_dataclass(
            'Attributes',
            [
                (item.key, Optional[str], dataclasses.field(default=None))
                for item in Attribute.__subclasses__()
            ]
        )(**{item.key: item.value for item in self.attribute})


@dataclasses.dataclass
class FindProfileInfoResponse(Method):
    pageNumber: int
    totalSize: int
    pagesCount: int
    size: int
    pageSize: int
    profile: Optional[List[Profile]] = None

    @property
    def profiles(self):
        return {
            profile.attributes.unitid: profile.attributes
            for profile in self.profile
        }

    @property
    def first_profile(self):
        return list(self.profiles.values())[0]

    def profile_by_unit_id(self, unit_id: Union[int, str]) -> Profile:
        return self.profiles.get(str(unit_id))


@dataclasses.dataclass
class CreateProfileRequest(Method):
    unitId: int
    profile: Profile
    profileType: str = 'CLIENT'

    @classmethod
    def make_anon_profile(cls, unit_id: int, phone: str):
        return cls(
            unitId=unit_id,
            profile=Profile.make_anon_profile(phone=phone)
        )

@dataclasses.dataclass
class AttributeInfoField(Base):
    value: str
    name: str


@dataclasses.dataclass
class PaymentStageAttributeField(AttributeInfoField):
    name: str = 'SECUREDFIELD:payment_stage'


@dataclasses.dataclass
class UnsBo79AttributeField(AttributeInfoField):
    name: str = 'SECUREDFIELD:unsBo_79'


@dataclasses.dataclass
class ScenariosAttributeField(AttributeInfoField):
    name: str = 'SECUREDFIELD:SCENARIOS'


@dataclasses.dataclass
class FieldsInfo(Base):
    attribute: List[AttributeInfoField]

    @classmethod
    def get_bank_info(cls):
        return cls(
            attribute=[
                PaymentStageAttributeField(value='2'),
                UnsBo79AttributeField(value='0'),
                ScenariosAttributeField(value='ME2MEPULL')
            ]
        )


@dataclasses.dataclass
class GetNextStepRequest(Method):
    providerId: str
    fieldsInfo: FieldsInfo

    @classmethod
    def get_bank_info(cls):
        return cls(providerId='374.2', fieldsInfo=FieldsInfo.get_bank_info())


@dataclasses.dataclass
class AttributeOperation(Base):
    value: str
    key: str


OPERATION_ATTRIBUTES = [
    'SECUREDFIELD:SBPBANKID',
    'targetcurrencycode',
    'typeid',
    'sourceamount',
    'targetalias',
    'clienttransaction',
    'sourceamountfee',
    'statusid',
    'haschildren',
    'modified',
    'targetaccountid',
    'category',
    'externaltransaction',
    'sourceamounttotal',
    'sourcecurrencycode',
    'isinvoice',
    'invoicerequest',
    'sourceaccounttotal',
    'sourceaccountid',
    'isreversed',
    'errordescription',
    'targettransaction',
]

OPERATION_ATTRIBUTE_CLASSES = [
    dataclasses.make_dataclass(
        f'{attribute.replace(":", "_")}AttributeOperation',
        [(KEY, str, dataclasses.field(default=attribute))],
        bases=(AttributeOperation, )
    )
    for attribute in OPERATION_ATTRIBUTES
]

OperationAttributeClasses = dataclasses.make_dataclass(
    'AttributeClasses',
    [
        (field.default.replace(":", "_"), Attribute, dataclasses.field(default=clss))
        for clss in OPERATION_ATTRIBUTE_CLASSES
        for field in dataclasses.fields(clss)
        if field.name == KEY
    ]
)()


@dataclasses.dataclass
class OperationInfo(Base):
    attribute: List[AttributeOperation]
    id: Optional[int] = None

    @classmethod
    def set_bank_id(cls, bank_id: str):
        return cls(attribute=[OperationAttributeClasses.SECUREDFIELD_SBPBANKID(value=bank_id)])

    @property
    def attributes(self):
        return dataclasses.make_dataclass(
            'OperationAttributes',
            [
                (item.key.replace(":", "_"), Optional[str], dataclasses.field(default=None))
                for item in AttributeOperation.__subclasses__()
            ]
        )(**{
            item.key.replace(":", "_"): item.value
            for item in self.attribute if item.key.replace(":", "_") in OPERATION_ATTRIBUTES
        })


@dataclasses.dataclass
class InvoiceRequest(Method):
    version: str
    payer: str
    payee: int
    amount: str
    clientTransaction: str
    operationInfo: OperationInfo

    @classmethod
    def invoice(cls, payee: int, amount: str, trans_id: str, bank_id: str):
        return cls(
            version='VERSION_2',
            payer='374',
            payee=payee,
            amount=amount,
            clientTransaction=trans_id,
            operationInfo=OperationInfo.set_bank_id(bank_id=bank_id)
        )


@dataclasses.dataclass
class GetOperationDetailsByIdRequest(Method):
    value: int
    __type__ = int


@dataclasses.dataclass
class GetOperationDetailsByIdResponse(Method):
    operation: OperationInfo


@dataclasses.dataclass
class Pager(Base):
    pageNumber: int = 1
    pageSize: int = 25


@dataclasses.dataclass
class FindOperationsListByCTIDRequest(Method):
    accountId: int
    clientTransaction: str
    pager: Optional[Pager] = None


@dataclasses.dataclass
class FindOperationsListByCTIDResponse(Method):
    pageSize: int
    pageNumber: int
    pagesCount: int
    size: int
    totalSize: int
    operation: Optional[List[OperationInfo]] = None


@dataclasses.dataclass
class InvoiceResponse(Method):
    dataTime: str
    operationInfo: OperationInfo
    clientTransaction: str
    transaction: str
    status: str


@dataclasses.dataclass
class InfoFieldItem(Base):
    id: str
    value: str


@dataclasses.dataclass
class InfoFieldEnum(Base):
    item: List[InfoFieldItem]


@dataclasses.dataclass
class InfoField(Base):
    temporary: Optional[bool]
    readonly: Optional[bool]
    hidden: Optional[bool]
    maxlength: int
    attribute_name: str
    orderBy: int
    comment: Optional[str]
    label: str
    id: int
    type: str
    steps: List[str]
    required: Optional[bool]
    enum: Optional[InfoFieldEnum] = None


@dataclasses.dataclass
class InfoFields(Base):
    field: List[InfoField]

@dataclasses.dataclass
class GetNextStepResponse(Method):
    providerId: int
    nextStep: str
    fields: InfoFields

@dataclasses.dataclass
class CreateProfileResponse(Method):
    value: int
    __type__ = int


@dataclasses.dataclass
class RefundRequest(Method):
    transactionId: int
    amount: Optional[str]
    paymentPassword: Optional[str] = None
    clientTransaction: Optional[str] = None
    operationInfo: Optional[OperationInfo] = None
    paymentPasswordChallenge: Optional[str] = None


@dataclasses.dataclass
class RefundResponse(Method, OperationInfo):
    pass


@dataclasses.dataclass
class PaymentRequest(Method):
    payer: int
    payee: int
    amount: Optional[str] = None
    isPayerAmount: Optional[bool] = None
    paymentPassword: Optional[str] = None
    clientTransaction: Optional[str] = None
    description: Optional[str] = None
    operationInfo: Optional[OperationInfo] = None
    paymentPasswordChallenge: Optional[str] = None


@dataclasses.dataclass
class PaymentResponse(Method, OperationInfo):
    pass


@dataclasses.dataclass
class VerifyPaymentRequest(PaymentRequest):
    version: str = 'VERSION_2'


@dataclasses.dataclass
class VerifyPaymentResponse(Method):
    isTransactionValid: bool
    description: str
    errorCode: str


@dataclasses.dataclass
class FindAccountByIdRequest(Method):
    value: int
    version: Optional[str] = None


@dataclasses.dataclass
class AccountAccessInfo(Base):
    accessToWrite: bool
    accessToTakenIn: bool
    accessToTakenOut: bool


@dataclasses.dataclass
class AttributeAccount(Base):
    value: str
    key: str


ACCOUNT_ATTRIBUTES = [
    'paymentPasswordType',
    'paymentPasswordChallengeRequired',
    'paymentPasswordExpirationDate',
    'alias',
    'primary',
    'delegated',
    'balanceChangesDate',
    'bankAccountForCredits',
    'bankAccountForDebits',
    'interfacetype',
    'testmode',
    'paymentsystem_limitids',
    'paymentsystem_unitid',
    'checkurl',
    'payurl',
    'httpmethod',
    'signature',
    'issignaturemandatory',
    'redefinesettingsinurl',
    'successurl',
    'failurl',
    'inprogressurl',
    'returnurl',
    'assistantformtarget',
    'onsuccessdebiturl',
    'onsuccesscrediturl',
    'oncancelleddebiturl',
    'oncancelledcrediturl',
    'onauthoriseurl',
]

ACCOUNT_ATTRIBUTE_CLASSES = [
    dataclasses.make_dataclass(
        f'{attribute.replace(":", "_")}AttributeAccount',
        [(KEY, str, dataclasses.field(default=attribute))],
        bases=(AttributeOperation, )
    )
    for attribute in ACCOUNT_ATTRIBUTES
]

AccountAttributeClasses = dataclasses.make_dataclass(
    'AttributeClasses',
    [
        (field.default.replace(":", "_"), Attribute, dataclasses.field(default=clss))
        for clss in ACCOUNT_ATTRIBUTE_CLASSES
        for field in dataclasses.fields(clss)
        if field.name == KEY
    ]
)()


@dataclasses.dataclass
class AccountInfo(Base):
    id: int
    type: int
    status: int
    alias: Optional[str] = None
    currency: Optional[str] = None
    balance: Optional[str] = None
    availableBalance: Optional[str] = None
    onSuccessfulDebitUrl: Optional[str] = None
    onSuccessfulCreditUrl: Optional[str] = None
    signature: Optional[str] = None
    lowBalanceThreshold: Optional[str] = None
    highBalanceThreshold: Optional[str] = None
    accountAccess: Optional[AccountAccessInfo] = None
    prototypeAccountId: Optional[int] = None
    onCancelledCreditUrl: Optional[str] = None
    onCancelledDebitUrl: Optional[str] = None
    attribute: List[AttributeAccount] = None

    @property
    def attributes(self):
        return dataclasses.make_dataclass(
            'AccountAttributes',
            [
                (item.key.replace(":", "_"), Optional[str], dataclasses.field(default=None))
                for item in AttributeAccount.__subclasses__()
            ]
        )(**{item.key.replace(":", "_"): item.value for item in self.attribute})


@dataclasses.dataclass
class FindAccountByIdResponse(Method):
    account: AccountInfo


@dataclasses.dataclass
class CreateAccountResponse(Method):
    value: int
    __type__ = int


@dataclasses.dataclass
class Detail(Base):
    faultDetail: str


@dataclasses.dataclass
class Fault(Base):
    faultcode: str
    faultstring: str
    detail: Detail


@dataclasses.dataclass
class Body(Base):
    method: Optional[Method] = None
    fault: Optional[Fault] = None

    def __post_init__(self, *args, **kwargs):
        self.__dataclass_fields__['method'].name = self.method.__class__.__name__
        if self.method and self.method.__type__ is not None:
            value = self.method.value
        else:
            value = self.method
        setattr(self, self.method.__class__.__name__, value)
        super().__post_init__(*args, **kwargs)

    @classmethod
    def make_find_profile(cls, phone: str) -> 'Body':
        return cls(method=FindProfileInfoRequest.by_phone(phone))

    @classmethod
    def from_dict(cls, data: dict) -> 'Base':
        res = {}
        for _class in Method.__subclasses__():
            if _class.__name__ in data:
                res['method'] = _class.from_dict(data.get(_class.__name__))
                break
        if 'fault' in data and data['fault'] is not None:
            res['fault'] = Fault.from_dict(data['fault'])
        return cls(**res)

    def get_value(self):
        assert self.method.is_base_type()
        return self.method.value


@dataclasses.dataclass
class Envelope(Base):
    Body: Body
    Header: Optional[Header] = None

    @classmethod
    def make_auth_method(cls, method: Method, username: str, password: str) -> 'Envelope':
        return cls(
            Header=Header.make_auth_header(
                username=username, password=password
            ),
            Body=Body(method=method)
        )


@dataclasses.dataclass
class Request(Base):
    Envelope: Envelope


@dataclasses.dataclass
class Response(Base):
    Envelope: Envelope

    def get_id(self):
        if self.Envelope.Body.method.is_base_type():
            raise ValueError
        return self.Envelope.Body.method.get_id()

    @property
    def is_error(self) -> bool:
        return self.Envelope.Body.fault is not None

    def error_detail(self) -> Tuple[Optional[str], Optional[str]]:
        if self.is_error:
            return (
                self.Envelope.Body.fault.faultcode,
                self.Envelope.Body.fault.faultstring,
                self.Envelope.Body.fault.detail.faultDetail,
            )
        return None, None, None

    @property
    def is_profile_created(self) -> bool:
        return self.Envelope.Body.method.profile is not None

    @property
    def profile_unit_id(self):
        return self.Envelope.Body.method.first_profile.unitid

    def profile_account_unit_id(self, unit_id: Union[str, int]):
        return self.Envelope.Body.method.profile_by_unit_id(unit_id).primaryaccountid
