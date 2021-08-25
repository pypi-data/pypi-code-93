from requests import get
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from traceback import format_exc

def change_molecular(molecular_list: list, atom_changes: list) -> list:
    if not atom_changes:
        changed_list = "".join(("".join(changable) for changable in molecular_list))
        return changed_list
    changed_list = []
    for changable in molecular_list:
        original_atom, original_number = changable
        original_number = int(original_number)
        for atom_change in atom_changes:
            matching_atom = atom_change[1]
            if matching_atom == original_atom:
                change_type, change_number = atom_change[0], int(atom_change[-1])
                if change_type == "+":
                    changed_number = original_number + change_number
                elif change_type == "-":
                    changed_number = original_number - change_number
                else:
                    print("Wrong calculation happened")
                changed_list.append("".join((matching_atom, str(changed_number))))
    return changed_list

def fix_molecular(formula):
    from string import ascii_uppercase
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
        fixed_element, element_atom = elem, unfixed.split(elem)[-1]
        new_start.append((fixed_element, element_atom))

def molecular_formula_fetch_nist(molecular_formula):
    url = f"https://webbook.nist.gov/cgi/cbook.cgi?Formula={molecular_formula}&NoIon=on&Units=SI"
    r = BeautifulSoup(get(url).text, 'html.parser')
    if 'Not Found' in r:
        return []
    compounds = [elem.string for elem in [elem.findChildren("a") for elem in r.find_all('ol')][0]]
    return compounds

def molecular_formula_fetch_wiki(molecular_formula):
    url = f'https://en.wikipedia.org/wiki/{molecular_formula}'
    r = BeautifulSoup(get(url).text, 'html.parser')
    if 'Wikipedia does not have an article' in r:
        return []
    compound_li = BeautifulSoup(r).find_all('div', {'class':'mw-parser-output'})[0][0].find_all('li')
    return [":".join((li.findChildren('a')[0]['title'], li.findChildren('a')[0]['href'].strip('/'))) for li in compound_li]
