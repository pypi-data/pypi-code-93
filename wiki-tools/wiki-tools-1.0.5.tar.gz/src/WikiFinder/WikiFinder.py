#!/usr/bin/python3
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from requests import get
from pyperclip import copy as clipboard_copy

from WikiFinder.lib.Functions import change_molecular, fix_molecular
from WikiFinder.lib.Functions import molecular_formula_fetch_nist
from WikiFinder.lib.Functions import molecular_formula_fetch_wiki

# from lib.Functions import change_molecular, fix_molecular
# from lib.Functions import molecular_formula_fetch

def main():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-m', '--molecular-formula', type=str, help="Outputs list of chemicals from molecular formula")
    group.add_argument('-n', '--name', type=str, help="Enter pubchem compound name to get compounds matching its molecular formula")
    parser.add_argument('-c', '--change', default=[], nargs='*', help="Enter atom change of compound using spaces. '+' increases atom while '_' decreases. Eg -c '-C1' '+H3'")
    parser.add_argument('-o', '--output', type=str, help="Enter output filename")
    argv = parser.parse_args()

    if not argv.molecular_formula and not argv.name:
        print("Use --help")
        exit()

    def molecular_formula_from_name(name):
        url = f'https://pubchem.ncbi.nlm.nih.gov/compound/{name}'
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

        browser_driver = Browser()
        browser_driver.driver.get(url)
        title = compound_data.find_all("meta", {"property":"og:title"})[0].attrs['content']
        molecular_formula = change_molecular(fix_molecular(browser_driver.find_element_by_id(By.ID,"Molecular-Formula").upper()), argv.change)
        browser_driver.driver.quit()
        return molecular_formula
    if argv.name:
        molecular_formula = molecular_formula_from_name(argv.name)
    else:
        molecular_formula = argv.molecular_formula
    compounds_nist = molecular_formula_fetch_nist(molecular_formula)
    compounds_wiki = molecular_formula_fetch_wiki(molecular_formula)
    final_compounds = compounds_nist + compounds_wiki
    compounds = "\n".join(final_compounds)
    print(compounds)
    clipboard_copy(compounds)

    if argv.output:
        with open(argv.output, 'w+') as f:
            f.write(compounds)

if __name__ == '__main__':
    main()
