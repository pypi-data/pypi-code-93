from requests import get
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from traceback import format_exc

def change_molecular(molecular_list: list, atom_changes: list = []) -> list:
    if not atom_changes:
        changed_list = ["".join(changable) for changable in molecular_list]
        return changed_list

    atom_dict = {elem[0]: elem[1] for elem in molecular_list}
    for atom_change in atom_changes:
        atom_type, atom_name, atom_number = atom_change[0], atom_change[1], atom_change[2]
        if atom_type == "+":
            new_atom_number = str(int(atom_dict[atom_name]) + int(atom_number))
            atom_dict[atom_name] = new_atom_number
        elif atom_type == "_":
            new_atom_number = str(int(atom_dict[atom_name]) - int(atom_number))
            atom_dict[atom_name] = new_atom_number
    new_list = ["".join(l) for l in list(atom_dict.items())]
    return new_list

def fix_molecular(formula: str) -> list:
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
    return new_start

def molecular_formula_fetch_nist(molecular_formula: str) -> list:
    url = f"https://webbook.nist.gov/cgi/cbook.cgi?Formula={molecular_formula}&NoIon=on&Units=SI"
    r = BeautifulSoup(get(url).text, 'html.parser')
    if not molecular_formula or 'Not Found' in r.find_all('title')[0].string:
        return []
    compounds = [elem.string for elem in [elem.findChildren("a") for elem in r.find_all('ol')][0]]
    return compounds

def molecular_formula_fetch_wiki(molecular_formula: str) -> list:
    url = f'https://en.wikipedia.org/wiki/{molecular_formula}'
    response = get(url)
    r = BeautifulSoup(response.text, 'html.parser')
    if not molecular_formula or 'Wikipedia does not have an article' in r:
        return []
    if not molecular_formula in r.find_all('title')[0].string:
        return []
    compound_li = r.find_all('div', {'class':'mw-parser-output'})[0].find_all('li')
    titles = [l.find_all('a', {"title":True}) for l in compound_li]
    final_titles = [t[0]['title'] for t in titles if t]
    href = [l.find_all('a', {"href":True})[0]['href'].split('/wiki')[-1] for l in compound_li]
    final_href = [h for h in href if not '#' in h]
    return ["".join(f) for f in zip(final_titles, final_href)]

