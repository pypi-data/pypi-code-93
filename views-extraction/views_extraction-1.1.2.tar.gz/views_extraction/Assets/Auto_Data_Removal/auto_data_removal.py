from os import listdir
from os.path import isfile, join
from simple_term_menu import TerminalMenu

from constants import *


class AutoDataRemoval:
    def __init__(self):
        self.path_to_dir = OUTPUT_FOLDER
        self.files = [f for f in listdir(
            self.path_to_dir) if isfile(join(self.path_to_dir, f))]
        self.num_of_files = len(self.files)
        self.question = None

    @staticmethod
    def create_output_file():
        print("No Files to Delete\nCreating Output File")
        with open(OUTPUT_NAME, "w") as output_file:
            output_file.write("[]")
        print("Output File Created")

    def get_user_confirmation(self):
        menu_options = ["[Y] Yes", "[N] No"]
        terminal_menu = TerminalMenu(
            menu_options, title="There are {} files in the Output Folder. Do you want to delete them: ".format(self.num_of_files))
        menu_entry_index = terminal_menu.show()
        self.question = menu_options[menu_entry_index][1].lower()

    def delete_files(self, response):
        if response == 'y':
            for file_path in self.files:
                os.remove(self.path_to_dir + "/" + file_path)
            self.create_output_file()
        else:
            print("No Files Deleted")

    def main(self):
        if self.num_of_files > 0:
            self.get_user_confirmation()
            self.delete_files(self.question)
        elif self.num_of_files == 0:
            self.create_output_file()


if __name__ == '__main__':
    auto_data_removal = AutoDataRemoval()
    auto_data_removal.main()
