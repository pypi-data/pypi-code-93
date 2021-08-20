import base64
from typing import Optional


def normalize_gql(field: str) -> Optional[str]:
    if field:
        return field.replace('_', '-').lower()


def read_as_base64(path: str) -> bytes:
    with open(path, 'rb') as fp:
        return base64.b64encode(fp.read())
