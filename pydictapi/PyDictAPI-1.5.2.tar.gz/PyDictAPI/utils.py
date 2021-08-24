"""
Author: Shawan Mandal
    
MIT License, see LICENSE for more details.
Copyright (c) 2021 Shawan Mandal

"""

import requests
from bs4 import BeautifulSoup

def handleRequests(query):
    '''Returns HTML document'''
    URL = 'https://www.dictionary.com/browse/{0}'.format(query)
    try:
        return requests.get(URL, allow_redirects=False).text
    except Exception:
        raise ConnectionError("Error occured while fetching data from the web, please try checking the internet connection.")

def ParseUsage(query):
    '''Returns HTML document'''
    URL = 'https://www.lexico.com/en/definition/{0}'.format(query)
    try:
        response = requests.get(URL, allow_redirects=False).text
        return response
    except Exception:
        raise ConnectionError("Error occured while fetching data from the web, please try checking the internet connection.")

def ParseSynonymsAndAntonyms(query):
    '''Returns HTML document'''
    URL = 'https://www.thesaurus.com/browse/{0}'.format(query)
    try:
        response = requests.get(URL, allow_redirects=False).text
        return response
    except Exception:
        raise ConnectionError("Error occured while fetching data from the web, please try checking the internet connection.")


def getSoupObj(res):
    '''Returns BeautifulSoup Object'''
    return BeautifulSoup(res, "html.parser")

