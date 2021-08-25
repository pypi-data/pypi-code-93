#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : amazon.py
@Time    : 2020-02-09 8:53
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2020 WingEase Technology Co.,Ltd. All Rights Reserved.
"""
import re
from decimal import Decimal, getcontext


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance


# 参考：http://docs.developer.amazonservices.com/en_US/dev_guide/DG_Endpoints.html
MARKETPLACES = {
    # North America
    'BR': 'www.amazon.com.br',  # Brazil
    'CA': 'www.amazon.ca',  # Canada
    'MX': 'www.amazon.com.mx',  # Mexico
    'US': 'www.amazon.com',  # US
    # Europe region
    'AE': 'www.amazon.ae',  # United Arab Emirates (U.A.E.)
    'DE': 'www.amazon.de',  # Germany
    'EG': '',  # Egypt
    'ES': 'www.amazon.es',  # Spain
    'FR': 'www.amazon.fr',  # France
    'UK': 'www.amazon.co.uk',  # UK
    'GB': 'www.amazon.co.uk',  # UK
    'IN': 'www.amazon.in',  # India
    'IT': 'www.amazon.it',  # Italy
    'NL': 'www.amazon.nl',  # Netherlands
    'PL': 'www.amazon.pl',  # Poland
    'SA': 'www.amazon.sa',  # Saudi Arabia
    'SE': 'www.amazon.se',  # Sweden
    'TR': 'www.amazon.com.tr',  # Turkey
    # Far East region
    'SG': 'www.amazon.sg',  # Singapore
    'AU': 'www.amazon.com.au',  # Australia
    'JP': 'www.amazon.co.jp',  # Japan
    # China
    'CN': 'www.amazon.cn',  # China
}

MARKETPLACE_IDS = {
    # North America
    'BR': 'A2Q3Y263D00KWC',  # Brazil
    'CA': 'A2EUQ1WTGCTBG2',  # Canada
    'MX': 'A1AM78C64UM0Y8',  # Mexico
    'US': 'ATVPDKIKX0DER',  # US
    # Europe region
    'AE': 'A2VIGQ35RCS4UG',  # United Arab Emirates (U.A.E.)
    'DE': 'A1PA6795UKMFR9',  # Germany
    'EG': 'ARBP9OOSHTCHU',  # Egypt
    'ES': 'A1RKKUPIHCS9HS',  # Spain
    'FR': 'A13V1IB3VIYZZH',  # France
    'UK': 'A1F83G8C2ARO7P',  # UK
    'GB': 'A1F83G8C2ARO7P',  # UK
    'IN': 'A21TJRUUN4KGV',  # India
    'IT': 'APJ6JRA9NG5V4',  # Italy
    'NL': 'A1805IZSGTT6HS',  # Netherlands
    'PL': 'A1C3SOZRARQ6R3',  # Poland
    'SA': 'A17E79C6D8DWNP',  # Saudi Arabia
    'SE': 'A2NODRKZP88ZB9',  # Sweden
    'TR': 'A33AVAJ2PDY3EV',  # Turkey
    # Far East region
    'SG': 'A19VAU5U5O7RUS',  # Singapore
    'AU': 'A39IBJ37TRP1C6',  # Australia
    'JP': 'A1VC38T7YXB528',  # Japan
    # China
    'CN': 'AAHKV2X7AFYLW',
}

MWS_ENDPOINTS = {
    # North America
    'BR': 'https://mws.amazonservices.com',  # Brazil
    'CA': 'https://mws.amazonservices.ca',  # Canada
    'MX': 'https://mws.amazonservices.com.mx',  # Mexico
    'US': 'https://mws.amazonservices.com',  # US
    # Europe region
    'AE': 'https://mws.amazonservices.ae',  # United Arab Emirates (U.A.E.)
    'DE': 'https://mws-eu.amazonservices.com',  # Germany
    'EG': 'https://mws-eu.amazonservices.com',  # Egypt
    'ES': 'https://mws-eu.amazonservices.com',  # Spain
    'FR': 'https://mws-eu.amazonservices.com',  # France
    'UK': 'https://mws-eu.amazonservices.com',  # UK
    'GB': 'https://mws-eu.amazonservices.com',  # UK
    'IN': 'https://mws.amazonservices.in',  # India
    'IT': 'https://mws-eu.amazonservices.com',  # Italy
    'NL': 'https://mws-eu.amazonservices.com',  # Netherlands
    'PL': 'https://mws-eu.amazonservices.com',  # Poland
    'SA': 'https://mws-eu.amazonservices.com',  # Saudi Arabia
    'SE': 'https://mws-eu.amazonservices.com',  # Sweden
    'TR': 'https://mws-eu.amazonservices.com',  # Turkey
    # Far East region
    'SG': 'https://mws-fe.amazonservices.com',  # Singapore
    'AU': 'https://mws.amazonservices.com.au',  # Australia
    'JP': 'https://mws.amazonservices.jp',  # Japan
    # China
    'CN': 'https://mws.amazonservices.com.cn',
}


class MarketPlaces(Singleton):
    # North America
    BR = None
    CA = None
    MX = None
    US = None
    # Europe region
    AE = None
    DE = None
    EG = None
    ES = None
    FR = None
    UK = None  # GB
    GB = None
    IN = None
    IT = None
    NL = None
    PL = None
    SA = None
    SE = None
    TR = None
    # Far East region
    SG = None
    AU = None
    JP = None
    # China
    CN = None

    def __init__(self):
        for country_code, domain in MARKETPLACES.items():
            setattr(self, country_code, domain)

    @staticmethod
    def all():
        return MARKETPLACES

    @staticmethod
    def domains():
        return list(MARKETPLACES.values())

    @staticmethod
    def ids():
        return list(MARKETPLACE_IDS.values())

    @staticmethod
    def endpoints():
        return list(MWS_ENDPOINTS.values())


def extract_star(star):
    if star:
        tmp = str.replace(star, ',', '.')
        tmp = re.findall(r'(\d+[,.]*\d*)', tmp)
        tmp = float(min(tmp))
        return tmp
    return None


def extract_review_count(review):
    tmp = re.findall('([\d,.]+)', review)
    if len(tmp) > 0:
        tmp = tmp[0]
        tmp = str.replace(tmp, ',', '')
        tmp = str.replace(tmp, '.', '')
        tmp = int(tmp)
        return tmp
    return None


def extract_price(price, thousands_symbol=',', decimal_symbol='.', precision=2):
    tmp = re.findall('([\d,.]+)', price)
    if len(tmp) > 0:
        tmp = tmp[0]
        tmp = str.replace(tmp, thousands_symbol, '')
        tmp = str.replace(tmp, decimal_symbol, '.')
        getcontext().prec = precision
        tmp = Decimal(tmp)
        return tmp
    return None


if __name__ == '__main__':
    e = extract_star('4.6 of 5')
    # e = extract_price('1,199.88')
    print(e)
