from flask import current_app
from jsonclasses.jsonclass_object import JSONClassObject
from jwt import encode


def encode_jwt_token(operator: JSONClassObject) -> str:
    key = current_app.config['jsonclasses_encode_key']
    return encode({'operator': operator._id}, key, algorithm='HS256')
