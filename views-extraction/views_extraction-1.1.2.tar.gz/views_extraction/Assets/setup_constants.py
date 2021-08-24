import sys
import os
import re
from simple_term_menu import TerminalMenu

sys.path.append(os.path.dirname(os.path.realpath(__file__)))


class SetupConstants:
    def __init__(self):
        self.constants_path = os.path.dirname(
            os.path.realpath(__file__)) + "/../constants.py"
        self.orig_dict_options = None
        self.menu_options = self.format_constant_file()
        self.user_selection = self.get_user_selection()

    def get_user_selection(self):
        terminal_menu = TerminalMenu(
            self.menu_options, title="What would you like to change: ")
        return terminal_menu.show()

    def read_constants_file(self):
        with open(self.constants_path, "r") as constants_file:
            constants_file_contents = constants_file.readlines()
        return constants_file_contents

    def parse_lines(self, line):
        line = line.replace('\n', '')
        line, _, _ = line.partition('#')
        if 'import ' in line or line == '':
            return None
        return line

    def get_only_alterable_constants(self, line_list):
        return line_list[line_list.index('ALTERABLE_CONSTANTS = True') + 1:]

    def make_dict_for_constants(self, line_list):
        constants_dict = {}
        for lines in line_list:
            split_line = list(
                filter(None, re.sub(':.*?=', '', lines).split(' ')))
            if len(split_line) == 2:
                constants_dict[split_line[0]] = split_line[1]
            elif len(split_line) > 2:
                constants_dict[split_line[0]] = ' '.join(split_line[1:])
            else:
                raise Exception('Invalid line in constants file: ' + lines)
        return constants_dict

    def format_constant_file(self):
        constants_file_contents = self.read_constants_file()
        formatted_lines = []
        for line in constants_file_contents:
            result = self.parse_lines(line)
            if result is not None:
                formatted_lines.append(result)
        formatted_lines = self.get_only_alterable_constants(formatted_lines)
        self.orig_dict_options = self.make_dict_for_constants(formatted_lines)
        formatted_options = [option.capitalize()
                             for option in self.orig_dict_options.keys()]
        formatted_options.append("Exit")
        return formatted_options

    def set_output_type(self, str_output_type):
        self.orig_dict_options['OUTPUT_TYPE'] = str_output_type.lower()

    def output_type_menu(self):
        menu_options = ['CSV', 'Excel', 'JSON']
        terminal_menu = TerminalMenu(
            menu_options, title="Choose an output file type: ")
        self.set_output_type(menu_options[terminal_menu.show()])

    def set_recipient_email(self, email_str):
        self.orig_dict_options['RECIPIENT'] = email_str[:-2]

    def recipient_menu(self):
        number_of_recipients = int(
            input("How many recipients do you wish to send the output file to: "))
        recipient_email_str = ''
        for _ in range(number_of_recipients):
            recipient_email = input("Enter recipient email: ")
            recipient_email_str += recipient_email + ', '
        self.set_recipient_email(recipient_email_str)

    def set_email_from(self):
        self.orig_dict_options['EMAIL_FROM'] = input(
            "Enter the email you would like to use for sending the output file: ")

    def set_password(self):
        self.orig_dict_options['PASSWORD'] = input(
            "Enter the password for the email you wish to use: ")

    def determine_action(self):
        if self.menu_options[self.user_selection] == 'Output_type':
            self.output_type_menu()
        elif self.menu_options[self.user_selection] == 'Recipient':
            self.recipient_menu()
        elif self.menu_options[self.user_selection] == 'Email_from':
            self.set_email_from()
        elif self.menu_options[self.user_selection] == 'Password':
            self.set_password()
        elif self.menu_options[self.user_selection] == 'Exit':
            sys.exit(0)

    def write_constants_file(self):
        constants_file_content = self.read_constants_file()
        with open(self.constants_path, "w") as constants_file:
            for key, value in self.orig_dict_options.items():
                for line_idx in range(len(constants_file_content)):
                    line = constants_file_content[line_idx]
                    if key in line:
                        line = line.split('\'')
                        line = line[0] + '\'' + \
                            value.replace('\'', '') + '\'' + line[2]
                        constants_file_content[line_idx] = line
            constants_file.writelines(constants_file_content)

    def main(self):
        try:
            self.determine_action()
            self.write_constants_file()
        except (KeyboardInterrupt, EOFError, SystemExit, TypeError):
            sys.exit(0)


if __name__ == '__main__':
    setup_constant_inst = SetupConstants()
    setup_constant_inst.main()
