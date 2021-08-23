def boolean_validator(field, value, error):
    if value and value not in ["true", "false"]:
        error(field, "Must be a boolean value: true or false")


S_ADDRESS_CREATE = {
    "street": {"type": "string"},
    "street2": {"type": "string"},
    "zip_code": {"type": "string"},
    "city": {"type": "string"},
    "country": {"type": "string"},
    "state": {"type": "string"},
}

S_CRM_LEAD_RETURN_CREATE = {
    "id": {"type": "integer"}
}

S_CRM_LEAD_CREATE = {
    "partner_name": {"type": "string"},
    "dni": {"type": "string"},
    "birth_date": {"type": "string"},
    "phone": {"type": "string"},
    "email_from": {"type": "string"},
    "street": {"type": "dict", "schema": S_ADDRESS_CREATE},
    "invoice_address": {"type": "dict", "schema": S_ADDRESS_CREATE},
    "portability_number": {"type": "string"},
    "iban": {"type": "string"},
    "language": {"type": "string"},
    "policy_accepted": {"type": "boolean"},
    "tag_ids": {
        "type": "list",
        "schema": {
            "type": "integer",
        }
    },
    "description": {"type": "string"},
}

S_HELPDESK_TICKET_RETURN_CREATE = {
    "id": {"type": "integer"}
}

S_HELPDESK_TICKET_CREATE = {
    "name": {"type": "string"},
    "description": {"type": "string"},
}
