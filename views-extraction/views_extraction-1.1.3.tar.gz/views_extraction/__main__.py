import sys

from colorama import Fore, Style
from simple_term_menu import TerminalMenu

from Assets.lpbi_views_extraction import LpbiViewsExtraction
from Assets.setup_constants import SetupConstants

class ViewsExtraction:
    
    def __init__(self):
        print(Fore.BLUE)
        self.menu_options = ["Setup", "Extract Views", "Exit"]
        self.user_selection = self.get_user_selection()

    def get_user_selection(self):
        terminal_menu = TerminalMenu(self.menu_options, title="Hello there, \nPlease choose an action from the options below: ")
        return terminal_menu.show()

    def run_setup_constants(self):
        setup_constants_inst = SetupConstants()
        setup_constants_inst.main()

    @staticmethod
    def run_lpbi_views_extraction():
        lpbi_inst = LpbiViewsExtraction()
        lpbi_inst.main()
    
    def main(self):
        try:
            if self.user_selection == 0:
                self.run_setup_constants()
            elif self.user_selection == 1:
                self.run_lpbi_views_extraction()
            elif self.user_selection == 2:
                sys.exit(0)
        except (KeyboardInterrupt, EOFError, SystemExit, TypeError):
            sys.exit(0)

if __name__ == '__main__':
    views_extraction_inst = ViewsExtraction()
    views_extraction_inst.main()
    print(Style.RESET_ALL)
