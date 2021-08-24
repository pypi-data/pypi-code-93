# noinspection PyUnresolvedReferences
import json
from datetime import datetime
from time import sleep
from tqdm import tqdm
from colorama import Fore

import pandas as pd
from constants import *
from selenium import common, webdriver
from webdriver_manager.chrome import ChromeDriverManager


class Worker:
    def __init__(self, namespace, position: int, c_username: str, c_password: str, list_data: list):
        self.namespace = namespace
        self.save_worker_files = SAVE_WORKER_FILES
        self.progress_bar_position = position
        self.chrome_options = None
        self.driver = None
        self.data_list = list_data
        self.current_id = self.update_id()
        self.get_driver()
        self.sign_in_url = self.compile_traffic_url()
        self.log_in(c_username, c_password)
        self.button_submit = None
        self.field_email = None
        self.field_password = None
        self.run_program = True
        self.download_url = None
        self.table_df = pd.DataFrame(
            {'Year': [], 'Jan': [], 'Feb': [], 'Mar': [], 'Apr': [], 'May': [], 'Jun': [], 'Jul': [], 'Aug': [],
             'Sep': [], 'Oct': [], 'Nov': [], 'Dec': [], 'Total': []})

        self.invalid_posts = ["No Post Available", "", "Auto Draft"]
        self.post_title = None
        self.table = None
        self.empty_df = pd.DataFrame()
        self.process_pid = os.getpid()
        self.output_file_path = self.setup_output_file(OUTPUT_FOLDER)
        self.number_of_total_rows = None
        self.invalid_ids = []
        self.invalid_ids_file_path = INVALID_IDS_FILE_PATH

    def get_driver(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--disable-application-cache')
        self.chrome_options.headless = True
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=self.chrome_options)
        return self.driver

    def compile_traffic_url(self) -> str:
        return 'https://pharmaceuticalintelligence.wordpress.com/wp-admin/index.php?page=stats&view=' \
               'post&post={}'.format(self.current_id)

    def sign_in_email(self, username):
        self.field_email = self._extracted_from_sign_in_password_2(
            '#usernameOrEmail', username
        )

    def sign_in_password(self, password):
        self.field_password = self._extracted_from_sign_in_password_2(
            '#password', password
        )

    def _extracted_from_sign_in_password_2(self, arg0, arg1):
        result = self.driver.find_element_by_css_selector(arg0)
        result.send_keys(arg1)
        self.button_submit = self.driver.find_element_by_class_name('button')
        self.button_submit.click()
        return result

    def log_in(self, p_username: str, p_password: str):
        print('Url using to sign in', self.sign_in_url)
        self.driver.get(self.sign_in_url)
        sleep(5)
        self.sign_in_email(p_username)
        sleep(5)
        self.sign_in_password(p_password)
        sleep(3)

    @staticmethod
    def get_first_id():
        return 0

    def update_id(self):
        for element in self.data_list:
            if element['Title'] == '':
                return int(element['ID'])
        else:
            self.run_program = False

    def no_view_table(self, header, data):
        for row in data:
            row = list(map(int, row))
        num_zeros_to_add = len(header) - len(data[0])
        for row in data:
            for _ in range(num_zeros_to_add):
                row.append(0)
        self.table_df = pd.DataFrame(data, columns=header)
        self.table_df = self.table_df[self.table_df['Year'].astype(
            int) >= 2012]
        self.table_df.reset_index(drop=True, inplace=True)
        # self.table_df.set_index('Year', inplace=True)

    def format_table(self, table):
        lines = table.split('\n')
        header = ("Year " + lines[0]).split(" ")
        data = lines[1:]
        data = [row.split(' ') for row in data]
        if int(data[0][0]) < 2012:
            self.no_view_table(header, data)
        else:
            self._extracted_from_format_table_9(data, header)
        self.table_df.replace(',', '', regex=True, inplace=True)
        self.table_df = self.table_df.astype('int')
        self.table_df.sort_values(by=['Year'], inplace=True)
        self.table_df.reset_index(drop=True, inplace=True)

    def _extracted_from_format_table_9(self, data, header):
        tmp = []
        for idx in range(len(data)):
            length_of_row = len(data[idx])
            if length_of_row < len(header) and len(data) == 1:
                current_month = datetime.now().month
                num_of_0_to_add_before = (current_month + 2) - length_of_row
                tmp_2 = data[idx]
                for idx_2 in range(1, num_of_0_to_add_before + 1):
                    tmp_2.insert(idx_2, 0)
                num_of_0_to_add_after = len(header) - len(data[idx])
                for _ in range(len(data[idx]) - num_of_0_to_add_after, len(data[idx])):
                    tmp_2.insert(len(data[idx]) - 1, 0)
                tmp.append(tmp_2)
            elif length_of_row < len(header) and idx == 0:
                num_of_0_to_add = len(header) - length_of_row
                tmp_2 = data[idx]
                for idx_2 in range(1, num_of_0_to_add + 1):
                    tmp_2.insert(idx_2, 0)
                tmp.append(tmp_2)
            elif length_of_row < len(header) and idx == len(data) - 1:
                tmp_2 = data[idx]
                num_of_0_to_add = len(header) - length_of_row
                for _ in range(length_of_row - num_of_0_to_add, length_of_row):
                    tmp_2.insert(length_of_row - 1, 0)
                tmp.append(tmp_2)
            else:
                tmp.append(data[idx])
        data = tmp
        self.number_of_total_rows = int(data[0][0]) - 2012
        for years_to_add in range(1, self.number_of_total_rows + 1):
            remaining_year = int(data[0][0]) - years_to_add
            filler_list = [remaining_year]
            for _ in range(len(data[0]) - 1):
                filler_list.append(0)
            data.append(filler_list)
        for idx in range(len(data)):
            self.table_df.loc[idx] = data[idx]

    def check_post_title(self):
        title_list = self.post_title.split('.')
        if len(title_list) == 1:
            return True
        elif len(title_list[-1]) == 0:
            return True
        else:
            return False

    def append_data(self, p_id: int, title: str, table):
        if isinstance(table, pd.DataFrame):
            table = table.to_dict()
        for element in self.data_list:
            if int(element['ID']) == p_id:
                element['Title'] = title
                element['Table'] = table

    def scrape_title_and_table(self):
        try:
            self.download_url = self.compile_traffic_url()
            self.driver.get(self.download_url)
            sleep(2)
            self.post_title = self.driver.find_element_by_class_name(
                'statscolumn').text.split("\n")[0][11:]
            self.table = self.driver.find_elements_by_xpath("//table")
            if len(self.table) == 4:
                self.table = self.table[1].text
            else:
                self.table = self.table[0].text
            self.format_table(self.table)
            if self.post_title != '':
                self.append_data(
                    self.current_id, self.post_title, self.table_df)
                self.current_id = self.update_id()
            else:
                self.invalid_ids.append(self.current_id)
                self.append_data(
                    self.current_id, "No Post Available", dict(self.empty_df))
                self.current_id = self.update_id()
        except (common.exceptions.NoSuchElementException, common.exceptions.WebDriverException):
            pass
        except IndexError:
            self.invalid_ids.append(self.current_id)
            self.append_data(
                self.current_id, "No Post Available", dict(self.empty_df))
            self.current_id = self.update_id()

    def main(self):
        with tqdm(total=len(self.data_list), bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Fore.RESET), position=self.progress_bar_position) as pbar:
            pbar.set_description(
                "[Worker ID: {}]Extracting Data: ".format(self.process_pid))
            while self.run_program:
                self.scrape_title_and_table()
                pbar.update(1)
        pbar.close()
        self.driver.close()
        self.save_data_list(self.data_list)
        if len(self.invalid_ids) > 0:
            self.save_invalid_ids()

    def save_invalid_ids(self):
        with open(self.invalid_ids_file_path + '/invalid_ids_{}'.format(self.process_pid) + ".txt", 'w') as f:
            for idx in self.invalid_ids:
                f.write(str(idx) + '\n')

    def setup_output_file(self, output_file_path: str) -> str:
        return output_file_path + '/output_{}'.format(self.process_pid) + ".json"

    def save_data_list(self, data):
        """Save the data into a json file or in the namespace depending on the boolean"""
        if self.save_worker_files:
            with open(self.output_file_path, 'w+') as outfile:
                outfile.seek(0)
                json.dump(data, outfile)
        else:
            manager_namespace = self.namespace.data
            manager_namespace.extend(data)
            self.namespace.data = manager_namespace


if __name__ == '__main__':
    import os
    import sys
    sys.path.append('../../')
    data_list = [
        {
            "ID": "20552",
            "Title": "",
            "Table": ""
        },
        {
            "ID": "20566",
            "Title": "",
            "Table": ""
        },
        {
            "ID": "20560",
            "Title": "",
            "Table": ""
        }
    ]
    # noinspection PyArgumentList
    worker_inst = Worker(None, 0, "", "", data_list)
    worker_inst.main()
