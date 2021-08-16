# Created by Jan Rummens at 19/01/2021
from bs4 import BeautifulSoup
from nemonet.plugin.handle_zephyr import set_jira_item_status

class Reporter(object):


    status_passed = 1
    status_failed = 2


    def publish(self, from_file_name, execution_status):
        with open( from_file_name + ".xml") as fp:
            soup = BeautifulSoup(fp, "lxml")
        for zephyr in soup.find_all('zephyr'):
            set_jira_item_status(jira_number=zephyr['id'], jira_project=zephyr['project'], status=execution_status)