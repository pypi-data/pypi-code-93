GENDER_DEFAULT = [
    {'id': 'https://d-nb.info/standards/vocab/gnd/gender#notKnown'}
]


def fetch_gender(gnd_payload):
    try:
        gender_list = gnd_payload.get(
            'gender', GENDER_DEFAULT
        )
    except AttributeError:
        return GENDER_DEFAULT[0]['id']
    return gender_list[0]['id']
