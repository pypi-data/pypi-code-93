#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
doc:
https://open-trip.meituan.com/index.html#/doc/entrance/accessDetail?anchor=ba
"""
import hmac
import logging
import base64
import hashlib

from mtba.logger import conf_logger

logger = logging.getLogger('debug')


def b64_encode(s):
    """

    :param s: str/byte
    :return: byte
    """
    if isinstance(s, str):
        s = s.encode()
    return base64.b64encode(s)


def b64_encode_str(s):
    """

    :param s:
    :return: str
    """
    data_byte = b64_encode(s)
    return data_byte.decode()


def b64_decode(s):
    """

    :param s: byte
    :return: str
    """
    if isinstance(s, str):
        s = s.encode()
    return base64.b64decode(s)


def b64_decode_str(s):
    """

    :param s:
    :return: str
    """
    return b64_decode(s).decode()


def make_ba(client_secret=None, string_to_sign=None, encoding='utf-8'):
    """

    :param client_secret:
    :param string_to_sign:
    :param encoding:
    :return:
    """

    sign = hmac.new(
        client_secret.encode(encoding),
        string_to_sign.encode(encoding),
        hashlib.sha1
    ).digest()
    digest_b64 = base64.b64encode(sign)
    s = digest_b64.decode(encoding).replace("\n", "")
    logger.debug("make_ba client_secret:{}\nstring_to_sign:{}".format(
        client_secret, string_to_sign))
    return s


def make_ba_fmt(method='GET', uri='', gmt_fmt_str=''):
    """
    签名前:"POST /rhone/lv/deal/change/notice"
    + "\n" + "Wed, 06 May 2015 10:34:20 GMT";

    secret=123456ce8b61f8e608eaf2e9702864a9

    签名后:hVQHFpzOXtxzOy5INj2IohJ85Y0=

    :param method: POST
    :param uri: /rhone/lv/deal/change/notice
    :param gmt_fmt_str: "Wed, 06 May 2015 10:34:20 GMT"
    :return:
    """
    method = method.upper()
    fmt = "{method} {uri}\n{date_fmt_str}".format(
        method=method, uri=uri, date_fmt_str=gmt_fmt_str)
    return fmt


def main():
    # sign = "ojsTe2PoiOB/SuCXDfDVGSDp59A="
    uri = '/scenic/data/center/api/pmsCheckout/ticketingNotice'
    method = 'POST'
    client_secret = '50f620304b6e02865c226af14fd9114d'
    gmt_time_str = "Tue, 23 Mar 2021 02:58:57 GMT"
    string_to_sign = make_ba_fmt(
        method, uri, gmt_time_str
    )
    logger.info(string_to_sign)
    s = make_ba(client_secret, string_to_sign)
    logger.info("s:{}".format(s))
    # assert sign == s


if __name__ == '__main__':
    conf_logger(logger, debug=False)
    print(logger)
    main()
    # data_src = "abc"
    # data = b64_encode_str(data_src)
    # assert b64_decode_str(data) == data_src
