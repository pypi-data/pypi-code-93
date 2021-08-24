from bs4 import BeautifulSoup
from requests import get
from urllib.parse import urlparse
from traceback import format_exc

def chemspider_fetch(name):
    try:
        request = get(f'http://www.chemspider.com/Search.aspx?q={name}')
        if not request.history:
            print("Chemspider fetch failed")
            return ""
        else:
            code = BeautifulSoup(request.history[0].text, 'html.parser')
            link = code.find_all('a')[0]
            chemspider = urlparse(link['href']).path.split('.html')[0].split('.')[-1]
            return chemspider
    except Exception as E:
        print(E)
        format_exc()

def chebi_fetch(name):
    match_string = "Sorry, no results"
    try:
        code = get(f'https://www.ebi.ac.uk/chebi/advancedSearchFT.do?searchString={name}').text
        if match_string in code:
            print("ChEBI fetch failed")
            return ""
        link = BeautifulSoup(code, 'html.parser').find_all('a', {'target': '_top'})[0]
        chebi = urlparse(link['href']).query.split(':')[-1]
        return chebi
    except Exception as E:
        print(E)
        format_exc()
