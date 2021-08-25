import copy
import datetime
import json
import re


def json_dumps(data):

    if isinstance(data, dict):
        data_copy = copy.deepcopy(data)

        for key in data_copy.keys():
            value = data_copy[key]

            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%dT%H:%M:%S')
            elif isinstance(value, datetime.date):
                value = value.strftime('%Y-%m-%d')
            else:
                continue

            data_copy[key] = value

        return json.dumps(data_copy)
    elif isinstance(data, list):
        vector = []
        for item in data:
            item_json = json_dumps(item)
            vector.append(item_json)

        return vector
    else:
        return json_dumps(data)


def _loads_datetime(value):
    if not isinstance(value, str):
        return value

    matcher_datetime = re.compile(
        '^(\d\d\d\d)-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)$')
    matcher_date = re.compile('^(\d\d\d\d)-(\d\d)-(\d\d)$')

    match_datetime = matcher_datetime.search(value)
    match_date = matcher_date.search(value)

    if match_datetime:
        ano = int(match_datetime.group(1))
        mes = int(match_datetime.group(2))
        dia = int(match_datetime.group(3))
        hora = int(match_datetime.group(4))
        minuto = int(match_datetime.group(5))
        segundo = int(match_datetime.group(6))

        return datetime.datetime(year=ano, month=mes, day=dia, hour=hora, minute=minuto, second=segundo)
    elif match_date:
        ano = int(match_date.group(1))
        mes = int(match_date.group(2))
        dia = int(match_date.group(3))

        return datetime.date(year=ano, month=mes, day=dia)
    else:
        return value


def _internal_loads(data):
    if isinstance(data, dict):
        for key in data.keys():
            data[key] = _internal_loads(data[key])
        return data

    elif isinstance(data, list):
        vector = []
        for item in data:
            vector.append(_internal_loads(item))
        return vector

    else:
        return _loads_datetime(data)


def json_loads(str_json: str):
    if isinstance(str_json, str):
        data = json.loads(str_json)
    else:
        data = str_json

    return _internal_loads(data)


# texto = """{
#     "id": "74dd6e30-8d62-4a9c-bb8b-78c9b7bd7006",
#     "pubsub_message_id": "2428659124732084",
#     "tenant": "nasajon",
#     "rpa_id": "BUG",
#     "received_data": {
#         "outro": "dado"
#     },
#     "status": 200,
#     "return": {
#         "file_url": "http://www.google.com.br"
#     },
#     "created_at": "2021-06-14T23:28:00"
# }"""

# dicio = json_loads(texto)
# print(dicio)
