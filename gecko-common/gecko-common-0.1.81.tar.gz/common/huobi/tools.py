import base64
import hmac
from hashlib import sha256
from urllib import parse


def generate_signature(api_secret: str, method: str, uri: str, params: dict) -> str:
    url_path_result = parse.urlparse(uri)
    sorted_params = sorted(params.items(), key=lambda d: d[0], reverse=False)
    encode_params = parse.urlencode(sorted_params)
    payload = [method.upper(), url_path_result.netloc, url_path_result.path, encode_params]
    payload = "\n".join(payload)
    payload = payload.encode(encoding="UTF8")
    secret_key = api_secret.encode(encoding="utf8")
    digest = hmac.new(secret_key, payload, digestmod=sha256).digest()
    signature = base64.b64encode(digest)
    signature = signature.decode()
    return signature
