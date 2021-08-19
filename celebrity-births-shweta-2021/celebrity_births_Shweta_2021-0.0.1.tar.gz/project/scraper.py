'''
Additionally, the class Scraper get the HTML code of a
Wikipedia page and extracts the name of celebrities that
were born in a certain date
'''

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class Scraper:
    '''
    Scraping the data

    Attributes:
        ROOT: It takes the website url that is to be scraped
    '''

    def __init__(self):
        self.ROOT = 'https://en.wikipedia.org/wiki/'

    def _get_soup(self, date: str) -> BeautifulSoup:
        # private method, you don't need a docstring
        r = requests.get(self.ROOT + date)
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup

    def _get_birth_header(self, date: str) -> BeautifulSoup:
        # Private
        soup = self._get_soup(date)
        span = soup.find(
            'span', {'class': 'mw-headline'}, text=re.compile("Births"))
        # If the list is empty because it didn't find anything
        if not span:
            raise ValueError('The given date has no birth data')
        h2 = span.find_parent()
        return h2

    def _get_celebrity_list(self, date: str) -> list:
        # Add <ul> tags until you find the next <h2> tag
        next_node = self._get_birth_header(date)
        celebrities_list = []
        while True:
            next_node = next_node.find_next_sibling()
            if getattr(next_node, 'name') == 'ul':
                celebrities_list.extend(next_node.find_all('li'))
            elif getattr(next_node, 'name') == 'h2':
                break
        return celebrities_list

    def _clean_li(self, li: BeautifulSoup) -> str:
        # Private method
        li_complete = li.text.split('–')
        name_complete = li_complete[1].split(',')
        name = name_complete[0].strip()
        return name

    def get_celebrities(self, date: str = None) -> list:
        '''
        Add a proper docstring
        '''
        if date is None:
            date = 'January_1'
        cel_list = self._get_celebrity_list(date)
        celebrities = []
        for li in cel_list:
            celebrities.append(self._clean_li(li))
        return celebrities



