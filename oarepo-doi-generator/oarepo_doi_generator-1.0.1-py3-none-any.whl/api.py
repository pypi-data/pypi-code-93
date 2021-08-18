import json

from flask import current_app
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from jsonref import requests

from .json_schema_mapping import schema_mapping


def doi_already_requested(record):
    doi_requested = False

    if "identifiers" not in record:
        return doi_requested
    identifiers_array = record["identifiers"]


    for id in identifiers_array:
        if "status" in id and "doi" in id["scheme"] and "requested" in id["status"]:
            doi_requested = True
            break

    return doi_requested

def doi_request(record):

    #if doi was not already requested
    if not doi_already_requested(record):
        if "identifiers" not in record:
            record['identifiers'] = [{
                "identifier": "",
                "scheme": "doi",
                "status": "requested"
            }]
        else:
            record['identifiers'].append(
                {
                    "identifier": "",
                    "scheme": "doi",
                    "status": "requested"
                }
            )

    record.commit()
    db.session.commit()
    return record

def doi_approved(record, pid_type, test_mode = False):

    if doi_already_requested(record):
        record['identifiers'].remove(
            {
                "identifier": "",
                "scheme": "doi",
                "status": "requested"
            }
        )
        data = schema_mapping(record, pid_type, test_mode=test_mode)
        doi = doi_registration(data=data, test_mode=test_mode)
        if doi != None:
            record['identifiers'].append(
                {
                    "identifier": doi,
                    "scheme": "doi"
                }
            )
            record.commit()

            PersistentIdentifier.create('doi', doi, object_type='rec',
                                    object_uuid=record.id,
                                    status=PIDStatus.REGISTERED)

            db.session.commit()

    return record


def doi_registration(data, test_mode = False):
    username = current_app.config.get("DOI_DATACITE_USERNAME")
    password = current_app.config.get("DOI_DATACITE_PASSWORD")

    if test_mode:
        url = 'https://api.test.datacite.org/dois'
    else:
        url = 'https://api.datacite.org/dois'


    request = requests.post(url=url, json=data, headers = {'Content-type': 'application/vnd.api+json'}, auth=(username, password))

    if request.status_code == 201:
        response = json.loads(request.text)
        doi = response['data']['id']
    else:
        print(request.status_code)

    return doi




