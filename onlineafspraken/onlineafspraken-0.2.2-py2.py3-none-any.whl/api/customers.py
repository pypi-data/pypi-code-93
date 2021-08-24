from onlineafspraken.api.client import OnlineAfsprakenAPI, client
from onlineafspraken.schema.customer import (
    GetCustomerResponse,
    GetCustomersResponse,
    GetFieldsResponse,
    PasswordRecoveryResponse,
    SetCustomerResponse,
)


def get_customer(customer_id) -> GetCustomerResponse:

    resp = client.get("getCustomer", id=customer_id)

    return GetCustomerResponse.parse_obj(resp)


def get_customers(
    limit=None,
    offset=None,
    update_after=None,
    email=None,
    birth_date=None,
    account_number=None,
) -> GetCustomersResponse:
    api = OnlineAfsprakenAPI()
    resp = api.get(
        "getCustomers",
        Limit=limit,
        Offset=offset,
        UpdateAfter=update_after,
        Email=email,
        BirthDate=birth_date,
        AccountNumber=account_number,
    )

    return GetCustomersResponse.parse_obj(resp)


def get_fields(agenda_id, appointment_type_id=None) -> GetFieldsResponse:

    resp = client.get(
        "getFields", agendaId=agenda_id, appointmentTypeId=appointment_type_id
    )

    return GetFieldsResponse.parse_obj(resp)


def login_customer(username, password) -> GetCustomerResponse:

    resp = client.get("loginCustomer", username=username, password=password)

    return GetCustomerResponse.parse_obj(resp)


def login_customer_with_facebook(facebook_id) -> GetCustomerResponse:
    api = OnlineAfsprakenAPI()
    resp = api.get("loginCustomerWithFacebook", facebookId=facebook_id)

    return GetCustomerResponse.parse_obj(resp)


def password_recovery(email) -> PasswordRecoveryResponse:
    api = OnlineAfsprakenAPI()
    resp = api.get("passwordRecovery", email=email)

    return PasswordRecoveryResponse.parse_obj(resp)


def set_customer(
    first_name: str,
    last_name: str,
    email: str,
    customer_id: int = None,
    account_number: int = None,
    phone: str = None,
    mobile_phone: str = None,
    insertions: str = None,
    birth_date: str = None,
    gender: str = None,
    street: str = None,
    house_nr: int = None,
    house_nr_addition: str = None,
    zip_code: str = None,
    city: str = None,
    country: str = None,
    status: int = None,
) -> SetCustomerResponse:
    api = OnlineAfsprakenAPI()
    resp = api.get(
        "setCustomer",
        FirstName=first_name,
        LastName=last_name,
        Email=email,
        Id=customer_id,
        AccountNumber=account_number,
        Phone=phone,
        MobilePhone=mobile_phone,
        Insertions=insertions,
        BirthDate=birth_date,
        Gender=gender,
        Street=street,
        HouseNr=house_nr,
        HouseNrAddition=house_nr_addition,
        ZipCode=zip_code,
        City=city,
        Country=country,
        Status=status,
    )

    return SetCustomerResponse.parse_obj(resp)
