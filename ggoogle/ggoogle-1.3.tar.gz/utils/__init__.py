from selenium import webdriver
import sys
import webbrowser


__version__ = '1.3'


class Googler(object):
    def __init__(self, query):
        super(Googler, self).__init__()
        self.google_link = 'https://www.google.com/search?q='
        self.query = self.google_link + '+'.join(query)

    def search_in_new_tab(self):
        webbrowser.open_new_tab(self.query)
        return self.query

    def search_in_new_private_tab(self):
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
        driver = webdriver.Firefox(firefox_profile=firefox_profile)
        driver.get(self.query)
        return  self.query

