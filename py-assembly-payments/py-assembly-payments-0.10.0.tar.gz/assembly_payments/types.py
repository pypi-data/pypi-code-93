from typing import Union, Optional, Any, List

from pydantic.main import BaseModel


class TokenRequest(BaseModel):
    grant_type: Union[None, str]
    client_id: Union[None, str]
    client_secret: Union[None, str]
    scope: Union[None, str]


class Token(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    expires_at: int


class UserBase(BaseModel):
    id: str
    first_name: str
    last_name: Union[None, str]
    email: str
    country: Optional[Union[None, str]]


class UserRequest(UserBase):
    pass


class User(UserBase):
    full_name: Union[None, str]
    created_at: Optional[Union[None, str]]
    updated_at: Optional[Union[None, str]]
    location: Union[None, str]
    related: Optional[dict]


class CompanyBase(BaseModel):
    name: str
    legal_name: str
    tax_number: str


class CompanyRequest(CompanyBase):
    user_id: str
    country: str


class Company(CompanyBase):
    id: str
    charge_tax: Union[None, str]
    address_line_1: Union[None, str]
    address_line_2: Union[None, str]
    city: Union[None, str]
    state: Union[None, str]
    zip: Union[None, str]
    phone: Union[None, str]


class WalletAccount(BaseModel):
    id: str
    active: bool
    created_at: Optional[Union[None, str]]
    updated_at: Optional[Union[None, str]]
    balance: int
    currency: str


class NppDetails(BaseModel):
    pay_id: str
    reference: str
    amount: str
    currency: str


class BpayDetails(BaseModel):
    biller_code: str
    reference: str
    amount: str
    currency: str


class VirtualAccountBase(BaseModel):
    id: str
    wallet_account_id: str


class VirtualAccount(VirtualAccountBase):
    routing_number: int
    account_number: int
    currency: str
    status: str
    created_at: Optional[Union[None, str]]
    updated_at: Optional[Union[None, str]]


class BankAccountBase(BaseModel):
    bank_name: str
    country: str
    account_name: str
    routing_number: str
    account_number: str
    holder_type: str
    account_type: str


class BankDetails(BankAccountBase):
    direct_debit_authority_status: Optional[str]


class BankAccountRequest(BankAccountBase):
    user_id: str


class BankAccount(BaseModel):
    id: str
    active: bool
    verification_status: str
    currency: str
    created_at: Optional[Union[None, str]]
    updated_at: Optional[Union[None, str]]
    bank: Optional[BankDetails]


class SetDisbursementRequest(BaseModel):
    account_id: str


class Disbursement(BaseModel):
    id: str
    amount: int
    currency: str
    batch_id: Optional[Union[None, int]]
    cuscal_payment_transaction_id: Optional[Union[None, str]]
    created_at: Optional[Union[None, str]]
    updated_at: Optional[Union[None, str]]
    state: str


class Transaction(BaseModel):
    description: str
    type: str
    type_method: str
    state: str
    user_id: str
    user_name: str
    account_id: str
    item_name: str
    dynamic_descriptor: str
    amount: int
    currency: str
    debit_credit: str
    created_at: Optional[Union[None, str]]
    updated_at: Optional[Union[None, str]]


class ItemBase(BaseModel):
    id: str
    name: str
    amount: int
    description: Union[None, str]


class ItemRequest(ItemBase):
    payment_type: int
    buyer_id: str
    seller_id: str


class Item(ItemBase):
    created_at: Optional[Union[None, str]]
    updated_at: Optional[Union[None, str]]
    state: str
    payment_type_id: int
    status: int
    deposit_reference: str
    buyer_name: str
    buyer_country: str
    buyer_email: str
    seller_name: str
    seller_country: str
    seller_email: str
    tds_check_state: Optional[str]
    currency: str


class MakePaymentRequest(BaseModel):
    account_id: str


class RefundPaymentRequest(BaseModel):
    refund_amount: Optional[int]
    refund_message: Optional[str]
    account_id: Optional[str]


class AuthorizePaymentRequest(BaseModel):
    account_id: str
    cvv: Optional[str]


class WebhookBase(BaseModel):
    http_method: str
    url: str
    description: Optional[str]


class WebhookRequest(WebhookBase):
    object_type: str


class WebhookUpdateRequest(WebhookBase):
    pass


class Webhook(WebhookBase):
    uuid: str
    enabled: bool
    created_at: str
    updated_at: str
    object_type: str


class Job(BaseModel):
    hashed_payload: str
    updated_at: str
    created_at: str
    webhook_uuid: str
    uuid: str
    payload: dict
    request_responses: List[dict]


class DirectDebitAuthority(BaseModel):
    id: str
    created_at: Optional[Union[None, str]]
    updated_at: Optional[Union[None, str]]
    amount: int
    bank_bsb: str
    debit_user_id: str
    state: str


class DirectDebitAuthorityRequest(BaseModel):
    amount: int
    account_id: str


class WithdrawFundsRequest(BaseModel):
    account_id: str
    amount: int
    custom_descriptor: Optional[Union[None, str]]


class ProcessNppPaymentRequest(BaseModel):
    crn: str
    payid: str
    amount: int
    payee_name: str
    trn: str
    clearing_system_transaction_id: str
    debtor_name: str
    debtor_legal_name: str
    debtor_bsb: str
    debtor_account: str
    remittance_information: str
    pay_id_type: str
    end_to_end_id: str
    npp_payin_internal_id: str
    pay_id: str


class TransactionStatesRequest(BaseModel):
    exported_ids: List[str]
    state: int


class CallbackBase(BaseModel):
    description: str
    url: str
    object_type: str
    enabled: bool


class Callback(CallbackBase):
    id: str
    authorization_token: Optional[Union[None, str]]
    created_at: Optional[Union[None, str]]
    updated_at: Optional[Union[None, str]]


class CallbackRequest(CallbackBase):
    pass


class CallbackUpdateRequest(CallbackBase):
    pass


class BatchTransaction(BaseModel):
    created_at: str
    updated_at: str
    id: int
    uuid: str
    external_reference: Optional[Union[None, str]]
    user_email: str
    first_name: str
    last_name: str
    user_external_id: str
    type: str
    type_method: str
    batch_id: int
    reference: Optional[Union[None, str]]
    deposit_reference: Optional[Union[None, str]]
    state: str
    status: int
    user_id: str
    account_id: str
    from_user_name: str
    from_user_id: int
    amount: int
    currency: str
    debit_credit: str
    description: str
