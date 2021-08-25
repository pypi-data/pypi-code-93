from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

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

