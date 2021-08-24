import termios
import warnings

import getpass4

from dateutil import parser
from Auto_Data_Removal.auto_data_removal import AutoDataRemoval
from Email_Sender.email_sender import EmailSender
from Summation.summation_main import SummationMain
from Webscraping.webscrape_data import WebscrapeData
from Webscraping.webscrape_ids import WebscrapeIDs

class LpbiViewsExtraction:

    def __init__(self):
        pass

    @staticmethod
    def get_date():
        """Get the date from the user.

        Returns:
            A datetime.date object.
        """
        date_input = input("Enter a date in the format MM/DD/YYYY or YYYY: ")
        date = list(map(int, date_input.split('/')))
        if len(date) == 1 and date[0] == 2012:
            return parser.parse("04/01/{}".format(date[0]))
        else:
            return parser.parse(date_input)

    @staticmethod
    def get_user_credentials() -> tuple:
        f_username = input("Enter your Username: ")
        f_password = ''
        try:
            f_password = getpass4.getpass(prompt="Enter your Password: ")
        except termios.error:
            print("", end='\r')
            print("Note: Your password is not hidden.")
            f_password = input("Enter your Password: ")
        finally:
            return f_username, f_password

    def main(self):
        warnings.filterwarnings('ignore')
        auto_data_removal = AutoDataRemoval()
        auto_data_removal.main()

        start_date = self.get_date()
        end_date = self.get_date()

        v_username, v_password = self.get_user_credentials()

        scrape_ids_inst = WebscrapeIDs(v_username, v_password)
        scrape_ids_inst.main()

        main_inst = WebscrapeData(v_username, v_password)
        main_inst.main()

        summation_inst = SummationMain(start_date, end_date)
        summation_inst.main()

        EmailSender()


if __name__ == '__main__':
    LpbiViewsExtraction.main()
