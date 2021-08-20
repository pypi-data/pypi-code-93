import base64
import os

from tornado.web import decode_signed_value

_serial = None
_config = {}


def config():
    return _config

def register(serial, config):
    """Register the teams version

    :param str serial: Register serial
    :param dict config: Capability configuration for teams version
     * footer: bool, whether to show the footer.
    :return: Return your brand name if register succeed, else ``None`` will be returned
    """
    global _serial, _config
    brand_name = biz_brand(serial)
    if brand_name:
        _serial = serial
        _config = config
        return brand_name


def biz_brand(serial=None):
    token = serial or os.environ.get('PYWEBIO_SERIAL')
    if not token:
        return False
    token = base64.b64decode(token)
    name = decode_signed_value("pywebio", "PYWEBIO", token, max_age_days=366)
    if not name:
        return False

    return name.decode('utf8')
