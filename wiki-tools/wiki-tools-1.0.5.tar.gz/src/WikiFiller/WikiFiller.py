#!/usr/bin/python3
from requests import get
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from pyperclip import copy as clipboard_copy

from WikiFiller.lib.Browser import Browser
from WikiFiller.lib.Template import chembox_part_1, chembox_part_2, chembox_part_3
from WikiFiller.lib.Functions import chemspider_fetch, chebi_fetch, fix_molecular

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

    browser_driver = Browser()
    browser_driver.driver.get(url)

    url = f'https://pubchem.ncbi.nlm.nih.gov/compound/{argv.name}'
    compound_data = BeautifulSoup(get(url).text, 'html.parser')
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
    molecular_formula = fix_molecular(browser_driver.find_element_by_id(By.ID,"Molecular-Formula").upper())
    wiki_formula = wiki_molecular(molecular_formula)
    mesh_names = browser_driver.find_element_by_id(By.ID,"MeSH-Entry-Terms", first=False)
    depositor_names = browser_driver.find_element_by_id(By.ID,"Depositor-Supplied-Synonyms", first=False)
    other_1, chembl = "", ""
    chemspider = chemspider_fetch(argv.name) or chemspider_fetch(title) or chemspider_fetch(smiles)
    chebi = chebi_fetch(argv.name) or chebi_fetch(title) or chebi_fetch(inchi_full)
    UNUSED = [mesh_names, depositor_names]

    browser_driver.driver.quit()

    if argv.chembox:
        chembox_1 = chembox_part_1 % (iupac, other_1)
        chembox_2 = chembox_part_2 % (cas_no, chemspider, chebi, chembl, ec_no, inchi, inchi_key, smiles, pubchem_cid, unii)
        chembox_3 = chembox_part_3 % (wiki_formula, title)
        full_chembox_template = chembox_1 + chembox_2 + chembox_3
    elif argv.drugbox:
        print("Not yet developed")

    print("Copying to clipboard")
    clipboard_copy(full_chembox_template)

    if argv.output:
        with open(argv.output, 'w+') as f:
            f.write(full_chembox_template)
    print("Synonyms")
    print(mesh_names, depositor_names)

if __name__ == '__main__':
    main()
