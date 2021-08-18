"""PubSub Events.

Declare here all PubSub topics which will be used.

These Topics will be created on AWS, when you send his first message.

"""
from enum import Enum


class UserEvents(Enum):
    USER_REGISTERED = "user_registered"
    USER_ACTIVATED = "user_activated"
    USER_LOGGED_IN = "user_logged_in"


class AccountEvents(Enum):
    BANK_ACCOUNT_REGISTERED = "bank_account_registered"
    AD_ACCOUNT_REGISTERED = "google_ad_account_registered"
    POLISHED_STATEMENT_TABLE = "polished_statement_table"
    STATEMENT_TABLE_UPDATED = "statement_table_updated"


class ProposalEvents(Enum):
    PROPOSAL_SELECTED = "proposal_selected"
    PROPOSAL_APPROVED = "proposal_approved"
    PROPOSAL_ACCEPTED = "proposal_accepted"
    PROPOSAL_INDICATIVE = "proposal_indicative"
    PROPOSAL_REFUSED = "proposal_refused"
    PROPOSAL_EXPIRED = "proposal_expired"


class CompanyEvents(Enum):
    COMPANY_REGISTERED = "company_registered"


class HubspotEvents(Enum):
    ORIGINATION_REGISTERED = "origination_registered"
    ORIGINATION = "origination"
    ADDITIONAL_DATA_SENT = "additional_data_sent"


class AdsEvents(Enum):
    ADS_ACCOUNT_CONNECTION = "ads_account_connection"


class CredentialEvents(Enum):
    NEW_TAX_ID_REGISTERED = "new_tax_id_registered"


class PartnerEvents(Enum):
    I_WANT_TO_BE_A_PARTNER = "i_want_to_be_a_partner"


class ClientManagerEvents(Enum):
    SHAREHOLDER_REGISTRATION = "shareholder_registration"
    GUARANTOR_REGISTRATION = "guarantor_registration"
    PROCURATOR_REGISTER = "procurator_register"
    EXECUTIVE_REGISTRATION = "executive_registration"
    PEP_FORM = "pep_form"


class DocumentationEvents(Enum):
    GENERATED_DOCUMENTATION = "generated_documentation"
    DOCUMENTATION_OK = "documentation_ok"
    DISBURSEMENT_MADE = "disbursement_made"
