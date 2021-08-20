import base64
import hmac
import json
from hashlib import sha256


def generate_signature(method: str, request_path: str, timestamp: str, params, body, secret_key) -> str:
    if body is None or body == {}:
        body = ''
    else:
        body = json.dumps(body)

    if method.upper() == "GET":
        if params:
            request_path = request_path + "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    msg = timestamp + method.upper() + request_path + body
    digest = hmac.new(bytes(secret_key, encoding='utf8'), bytes(msg, encoding='utf8'), digestmod=sha256).digest()
    return base64.b64encode(digest).decode('utf-8')


def create_ws_payload(channel: str, payload: dict):
    payload['channel'] = channel
    return payload
