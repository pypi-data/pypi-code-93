from bs4 import BeautifulSoup
from requests import get
from urllib.parse import urlparse
from traceback import format_exc
from string import ascii_uppercase

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

def fix_molecular(formula):
    organics = tuple(ascii_uppercase)
    organic_present = [elem for elem in organics if elem in formula]
    start = []
    for elem_i, elem in enumerate(organic_present):
        initial_index = None
        final_index = None
        for letter_i, letter in enumerate(formula):
            if elem == letter:
                initial_index = letter_i
            else:
                if (elem_i + 1) < len(organic_present):
                    if organic_present[int(elem_i + 1)] == letter:
                        final_index = letter_i
                        break
                else:
                    final_index = None
        start.append((elem, initial_index, final_index))
    new_start = []
    for l in start:
        elem, initial, final = l[0], l[1], l[2]
        if final:
            unfixed = formula[initial:final]
        else:
            unfixed = formula[initial:]
        fixed = f"{elem} = {unfixed.split(elem)[-1]}"
        new_start.append(fixed)
    fixed_molecular = " | ".join(new_start)
    return(fixed_molecular)


