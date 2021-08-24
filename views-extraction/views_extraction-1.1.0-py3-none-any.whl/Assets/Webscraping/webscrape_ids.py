import json
from time import sleep, time

from constants import *
from selenium import common, webdriver
from tqdm import trange
from colorama import Fore
# noinspection PyUnresolvedReferences
from webdriver_manager.chrome import ChromeDriverManager


class WebscrapeIDs:
    def __init__(self, v_username, v_password):
        self.extract_views_url = 'https://pharmaceuticalintelligence.com/wp-admin/edit.php?post_status=publish&post_type=post'
        self.chrome_options = None
        self.driver = None
        self.download_url = None
        self.field_email = None
        self.field_password = None
        self.button_submit = None
        self.button = None
        self.c_username = v_username
        self.c_password = v_password
        self.run_program = True
        self.output_file = OUTPUT_NAME
        self.post_limit = 0

    def get_driver(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--disable-application-cache')
        self.chrome_options.headless = True
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=self.chrome_options)
        return self.driver

    def signing_in(self, driver, p_username: str, p_password: str):
        print('Url using to sign in', self.extract_views_url)
        driver.get(self.extract_views_url)
        sleep(5)
        self.field_email = driver.find_element_by_css_selector(
            '#usernameOrEmail')
        self.field_email.send_keys(p_username)
        self.button_submit = driver.find_element_by_class_name('button')
        self.button_submit.click()
        sleep(5)
        self.field_password = driver.find_element_by_css_selector('#password')
        self.field_password.send_keys(p_password)
        self.button_submit = driver.find_element_by_class_name('button')
        self.button_submit.click()
        sleep(3)

    @staticmethod
    def get_total_num_of_articles(driver):
        return int(driver.find_element_by_class_name('displaying-num').text.split(" ")[0].replace(",", ""))

    @staticmethod
    def set_parameters(driver):
        screen_options_button = driver.find_element_by_class_name(
            'show-settings')
        screen_options_button.click()
        sleep(1)
        num_of_items = driver.find_element_by_class_name('screen-per-page')
        num_of_items.clear()
        num_of_items.send_keys(999)  # LLJW and Srini
        apply_button = driver.find_element_by_name('screen-options-apply')
        apply_button.click()

    def save_output(self, p_id: int):
        content = {"ID": p_id, "Title": '', "Table": ''}
        with open(self.output_file, 'r+') as file:
            file_data = json.load(file)
            file_data.append(content)
            file.seek(0)
            json.dump(file_data, file, indent=4)

    def scrape(self, driver):
        driver.get(self.extract_views_url)
        print("Sleeping 2 Seconds...")
        sleep(2)
        self.post_limit = self.get_total_num_of_articles(driver)
        self.set_parameters(driver)
        sleep(5)
        with trange(self.post_limit, bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Fore.RESET)) as pbar:
            pbar.set_description("Extracting IDs: ")
            try:
                current_num_of_posts = 0
                while current_num_of_posts <= self.post_limit:
                    elements = driver.find_elements_by_xpath(
                        "//td[@class = 'stats column-stats']//a")
                    for element in elements:
                        link = element.get_attribute('href')
                        post_id = link.split("=")[-1]
                        self.save_output(post_id)
                        pbar.update(1)
                        current_num_of_posts += 1
                    next_button = driver.find_elements_by_xpath(
                        "//a[@class = 'next-page button']")
                    next_page_link = ''
                    for element in next_button:
                        next_page_link = element.get_attribute('href')
                    try:
                        driver.get(next_page_link)
                    except common.exceptions.InvalidArgumentException:
                        pass
                if pbar.n >= self.post_limit:
                    pbar.set_description("Extraction Complete: ")
                    pbar.bar_format = "{l_bar}%s{bar}%s{r_bar}" % (
                        Fore.GREEN, Fore.RESET)
            except (common.exceptions.NoSuchElementException, IndexError) as e:
                print("Error: \n{}".format(e))
                pbar.set_description("Error Occurred: ")
                pbar.bar_format = "{l_bar}%s{bar}%s{r_bar}" % (
                    Fore.RED, Fore.RESET)

    def main(self):
        program_start_time = time()
        self.driver = self.get_driver()
        self.signing_in(self.driver, p_username=self.c_username,
                        p_password=self.c_password)
        self.scrape(self.driver)
        self.driver.quit()
        program_end_time = time()
        print("Webscraping Ids took {} seconds to execute.".format(
            program_end_time - program_start_time))


if __name__ == '__main__':
    start_time = time()
    scrape_ids_inst = WebscrapeIDs("", "")
    scrape_ids_inst.main()
    end_time = time()
    print("The program took {} seconds to execute.".format(end_time - start_time))
