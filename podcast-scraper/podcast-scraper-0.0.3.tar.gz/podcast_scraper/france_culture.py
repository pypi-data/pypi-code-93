import re

from podcast_scraper.generic_parser import GenericParser


class FranceCulture(GenericParser):
    def get_urls(self, content):
        p = re.compile(r'data-url="(.+?\.mp3)"', flags=re.MULTILINE)
        m = p.findall(content)
        return m

    def get_next(self, webdriver):
        try:
            next = webdriver.find_element_by_css_selector(
                "#main-content > article > section > div.teasers-list > div.pager-container > ul > li.pager-item.next > a"
            )
            new_url = next.get_attribute("href")
            webdriver.get(new_url)
            return new_url
        except Exception as e:
            return False
