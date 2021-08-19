'''
This script contains a class for representing the date.
Additionally, the class Scraper get the HTML code of a
Wikipedia page and extracts the name of celebrities that
were born in a certain date
'''
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from Scraper import Scraper
from Date import Date

if __name__ == '__main__':
    date_object = Date(27, 3, 1991)
    scraper = Scraper()
    celebrities = scraper.get_celebrities('February_30')
    print(celebrities)
