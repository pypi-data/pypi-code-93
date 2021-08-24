import unittest
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from ._config import PACKAGE_SECRETS_FILE, Show

chromedriver_autoinstaller.install()


class BaseTest(unittest.TestCase):
    def __init__(self, login_page="dopsadmin/login/?next=/dopsadmin/", email="test"):
        super().__init__()
        self.email = email + '@broadinstitute.org'
        self.selenium = webdriver.Chrome(options=self.chrome_options)
        self.login_page = login_page
        self.username, self.password, self.server_url = self.set_credentials()

    @staticmethod
    def set_credentials():
        with open(PACKAGE_SECRETS_FILE, "r") as secrets_file:
            username = secrets_file.readline().rstrip()
            password = secrets_file.readline().rstrip()
            server_url = secrets_file.readline().rstrip()
        return username, password, server_url

    @property
    def chrome_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        return chrome_options

    def visit_page(self, path):
        self.selenium.get('/'.join([self.server_url, path]))

    def log_in(self):
        self.visit_page(self.login_page)
        self.fill_in_form_field('username', self.username)
        self.fill_in_form_field('password', self.password)
        try:
            self.find_element(By.NAME, 'username').submit()
            self.assertTrue(self.selenium.find_element(By.ID, 'user-tools'))
        except NoSuchElementException:
            Show.error("You have used the wrong credentials.")
            Show.info("Confirm your credentials and run dragon setup -u username -p password")
            exit()

    def log_in_and_visit_page(self, path):
        self.log_in()
        self.visit_page(path)

    def find_element(self, by, condition_value):
        try:
            target = self.selenium.find_element(by, condition_value)
            return target
        except NoSuchElementException:
            Show.error(f"Not able to locate element using criteria {str(by)} and condition {condition_value}")
            exit()

    def fill_in_form_field(self, field_name, value):
        target_field = self.find_element(By.NAME, field_name)
        target_field.send_keys(value)

    def select_radio_button(self, field_name, value):
        target_button = self.find_element(By.CSS_SELECTOR,
                                                   f"input[type='radio'][name='{field_name}'][value='{value}']")
        target_button.click()

    def select_select_option(self, field_name, value):
        target_button = self.find_element(By.CSS_SELECTOR,
                                                   f"select[name='{field_name}']>option[value='{value}']")
        target_button.click()

    def select_checkbox(self, field_name):
        target_button = self.find_element(By.CSS_SELECTOR, f"input[type='checkbox'][name='{field_name}']")
        target_button.click()

    def upload_file_from_path(self, field_name, file_path):
        target_field = self.find_element(By.NAME, field_name)
        target_field.send_keys(file_path)

    def assert_form_submitted_successfully(self):
        jira_link = self.find_element(By.ID, 'delivery-success-header')
        self.assertTrue(jira_link)
        main_content = self.find_element(By.ID, 'main-content')
        self.assertIn('issue was created for you', main_content.text)
