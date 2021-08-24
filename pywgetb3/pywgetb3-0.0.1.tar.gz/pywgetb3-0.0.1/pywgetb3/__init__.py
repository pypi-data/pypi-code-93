"""This module do download from b3 historical data."""
__version__ = "0.0.1"

from urllib import urlretrieve
from datetime import datetime
import os

today = datetime.now()
base_url = "http://bvmf.bmfbovespa.com.br/InstDados/SerHist/"


def _create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def anual(year=today.year, destiny='.\\downloads\\anual\\'):
    _create_dir(destiny)
    base_name = "COTAHIST_A{:04d}.ZIP"
    file_name = base_name.format(year)
    url = base_url + file_name
    try:
        urlretrieve(url, filename=destiny + '\\' + file_name)
        return True
    except:
        return False


def monthly(year=today.year, month=today.month, destiny='.\\downloads\\monthly\\'):
    _create_dir(destiny)
    base_name = "COTAHIT_M{:02d}{:04d}.ZIP"
    file_name = base_name.format(month, year)
    url = base_url + file_name
    try:
        urlretrieve(url, filename=destiny + '\\' + file_name)
        return True
    except:
        return False


def daily(year=today.year, month=today.month, day=today.day, destiny='.\\downloads\\daily\\'):
    _create_dir(destiny)
    base_name = "COTAHIT_M{:02d}{:02d}{:04d}.ZIP"
    file_name = base_name.format(day, month, year)
    url = base_url + file_name
    try:
        urlretrieve(url, filename=destiny + '\\' + file_name)
        return True
    except:
        return False
