import os
import argparse

from ._config import PACKAGE_SECRETS_FILE, Show
from ._helpers import TEST_CLASSES, TEST_CLASSES_LIST


def handle_setup(args):
    Show.warning("Dragon is setting up your username and password")
    with open(PACKAGE_SECRETS_FILE, "w") as secret_file:
        secret_file.write(args.username + "\n")
        secret_file.write(args.password + "\n")
        secret_file.write(args.server + "\n")
    Show.success("Set up has completed successfully. Run dragon -h to see more on how to use")


def run_tests(test):
    test_class = TEST_CLASSES.get(test)
    if test_class:
        Show.warning("Loading done, now running tests, please wait ...... ")
        test_class().submit_test_form()
        exit()


def handle_program(args, parser):
    if args.program == "help":
        Show.warning(parser.format_help())
    elif args.program == "update":
        Show.info("Dragon is updating it's resources please wait")
        Show.error('This function has not been implemented at the moment')
    elif args.program == "list":
        Show.error('Below are the tests available at the moment')
        for test in TEST_CLASSES_LIST:
            Show.info(f'{test}')
        Show.success('Please run dragon test {name_of_class} example: dragon test sample_test')
    else:
        Show.warning(f"Dragon is loading test for {args.program}")
        run_tests(args.program)


def parse_commandline():
    parser = argparse.ArgumentParser(prog='dragon')
    subparsers = parser.add_subparsers(help='sub-command help', dest="command",
                                       description="The main category command to be run", title="command",
                                       required=True)

    parser_test = subparsers.add_parser('test', help='Run the program commands', )
    choices = ['list', 'update', 'help'] + TEST_CLASSES_LIST
    parser_test.add_argument('program', choices=choices,
                             help='The command you would like to run. Run ')

    parser_setup = subparsers.add_parser('setup', help='Run the initial setup for the program')
    parser_setup.add_argument("-u", dest="username", required=True)
    parser_setup.add_argument("-p", dest="password", required=True)
    parser_setup.add_argument("-s", dest="server", required=True)
    return parser


def main():
    Show.warning("Dragon is loading your commands!!")
    parser = parse_commandline()
    args = parser.parse_args()
    if args.command == 'setup':
        handle_setup(args)
    else:
        handle_program(args, parser)


if __name__ == '__main__':
    main()
