#!/usr/bin/python3
from requests import get
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from pyperclip import copy as clipboard_copy

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

#from lib.Template import chembox_part_1, chembox_part_2, chembox_part_3
#from lib.Functions import chemspider_fetch, chebi_fetch
from WikiFiller.lib.Template import chembox_part_1, chembox_part_2, chembox_part_3
from WikiFiller.lib.Functions import chemspider_fetch, chebi_fetch

def main():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--chembox', action="store_true", help="Generates chembox")
    group.add_argument('-d', '--drugbox', action="store_true", help="Generates drugbox")
    parser.add_argument('-n', '--name', type=str, help="Enter pubchem compound name from pubchem url")
    parser.add_argument('-o', '--output', type=str, help="Enter output filename")
    argv = parser.parse_args()

    if not argv.name:
        print("Use --help")
        exit()
    if not argv.chembox and argv.drugbox:
        print("Use --help")
        exit()

    url = f'https://pubchem.ncbi.nlm.nih.gov/compound/{argv.name}'
    compound_data = BeautifulSoup(get(url).text, 'html.parser')

    class Browser:
        def __init__(self):
            self.driver = Firefox()
            self.driver.set_page_load_timeout(18)
            self.driver.implicitly_wait(10)

        def find_element_by_id(self, by, value, first=True):
            try:
                data = self.driver.find_element(by, value).text.split('\n')
                if first:
                    return data[1]
                else:
                    return data
            except NoSuchElementException:
                print(f"No such element: {value}")
                return ""
            except Exception as E:
                print(E)

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
            fixed = f"{elem} = {unfixed.split(elem)[-1]}"
            new_start.append(fixed)
        fixed_molecular = " | ".join(new_start)
        return(fixed_molecular)

    browser_driver = Browser()
    browser_driver.driver.get(url)

    title = compound_data.find_all("meta", {"property":"og:title"})[0].attrs['content']
    pubchem_cid = compound_data.find_all("meta", {"property":"og:url"})[0].attrs['content'].split('/')[-1]

    iupac = browser_driver.find_element_by_id(By.ID,"IUPAC-Name")
    inchi_full = browser_driver.find_element_by_id(By.ID,"InChI")
    inchi = inchi_full.split('=')[-1]
    inchi_key = browser_driver.find_element_by_id(By.ID,"InChI-Key")
    smiles = browser_driver.find_element_by_id(By.ID,"Canonical-SMILES")
    cas_no = browser_driver.find_element_by_id(By.ID,"CAS")
    ec_no = browser_driver.find_element_by_id(By.ID,"European-Community-(EC)-Number")
    unii = browser_driver.find_element_by_id(By.ID,"UNII")
    formula = fix_molecular(browser_driver.find_element_by_id(By.ID,"Molecular-Formula").upper())

    mesh_names = browser_driver.find_element_by_id(By.ID,"MeSH-Entry-Terms", first=False)
    depositor_names = browser_driver.find_element_by_id(By.ID,"Depositor-Supplied-Synonyms", first=False)
    other_1, chembl = "", ""
    chemspider = chemspider_fetch(argv.name) or chemspider_fetch(title) or chemspider_fetch(smiles)
    chebi = chebi_fetch(argv.name) or chebi_fetch(title) or chebi_fetch(inchi_full)
    UNUSED = [mesh_names, depositor_names]

    browser_driver.driver.quit()

    #if argv.chembox:
    chembox_1 = chembox_part_1 % (iupac, other_1)
    chembox_2 = chembox_part_2 % (cas_no, chemspider, chebi, chembl, ec_no, inchi, inchi_key, smiles, pubchem_cid, unii)
    chembox_3 = chembox_part_3 % (formula, title)
    full_chembox_template = chembox_1 + chembox_2 + chembox_3

    print("Copying to clipboard")
    clipboard_copy(full_chembox_template)

    if argv.output:
        with open(argv.output, 'w+') as f:
            f.write(full_chembox_template)
    print("Synonyms")
    print(mesh_names, depositor_names)

if __name__ == '__main__':
    main()
