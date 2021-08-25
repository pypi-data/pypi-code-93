import argparse

from .assignments import main as main_assignments
from .grading import grading
from .groups import show_groups
from .participants import main as main_participants
from .search import search
from ..credentials import clear_credentials

description_dl = '''This script allows you to download any assignment submissions you want
from a TU-Berlin ISIS course and extracts it into subfolders based on 
the students group or individually. If the submission is a tar.gz or a zip
archive it will automatically try to extract it.
'''

epilog_dl = '''WARNING: The auto-extraction happens without input sanitation. 
Only use this tool if you trust your students.'''

description_pt = '''This script allows you to retrieve a list of all users currently subscribed to an ISIS course.

It provides full names, emails, roles and groups of the participants.
'''

description_s = ''' Search courses on the TU Berlin ISIS platform.
'''

description_gd = ''' Retrieve grading table for assignments on the TU Berlin ISIS platform.
By default all categories are included in the table.
'''

description_grp = '''WIP: This script allows you to search and modify groups on the TU Berlin ISIS platform.'''


def legacy_isisdl():
    parser = argparse.ArgumentParser(prog='isisdl', description=description_dl, epilog=epilog_dl)
    setup_parser_dl(parser)
    args = parser.parse_args()
    main_assignments(args)


def setup_parser_dl(parser_dl):
    parser_dl.set_defaults(func=main_assignments)
    parser_dl.add_argument('-u', '--user')
    parser_dl.add_argument('-p', '--password')
    parser_dl.add_argument('course_id', help='ID of the ISIS course', type=int)
    parser_dl.add_argument('-a', '--all', help='Download submissions for all assignments', action='store_true')
    parser_dl.add_argument('-s', '--separate',
                           help='Extract submission for each student separately instead of one per group.',
                           action='store_true')

    creds_group = parser_dl.add_mutually_exclusive_group()
    creds_group.add_argument('--store-credentials',
                             help='Stores credentials for the given user in the default keyring backend.',
                             action='store_true')
    creds_group.add_argument('--clear-credentials',
                             help='Deletes any stored credentials for the given user.',
                             action='store_true')


def setup_parser_pt(parser_pt):
    parser_pt.set_defaults(func=main_participants)

    parser_pt.add_argument('course_id', help='ID of the ISIS course', type=int)
    parser_pt.add_argument('-u', '--user')
    parser_pt.add_argument('-p', '--password')
    parser_pt.add_argument('-j', '--json', action='store_true',
                           help='Format output as JSON')
    parser_pt.add_argument('-g', '--grouped', action='store_true',
                           help='Filter out participants that are not assigned to a group.')
    parser_pt.add_argument('-G', '--group',
                           help='Filter for a specific group')
    parser_pt.add_argument('-r', '--role',
                           help='Only list participants with a specified role.')
    parser_pt.add_argument('-n', '--name',
                           help='Filter for students with the given string in their name')

    creds_group = parser_pt.add_mutually_exclusive_group()
    creds_group.add_argument('--store-credentials',
                             help='Stores credentials for the given user in the default keyring backend.',
                             action='store_true')
    creds_group.add_argument('--clear-credentials',
                             help='Deletes any stored credentials for the given user.',
                             action='store_true')


def setup_parser_s(parser_s):
    parser_s.set_defaults(func=search)
    parser_s.add_argument('query', help='Query string to search for', type=str)
    parser_s.add_argument('-l', '--limit', help='Limit number of results', type=int)
    parser_s.add_argument('-j', '--json', action='store_true',
                          help='Format output as JSON (Shows more info)')


def setup_parser_gd(parser_gd):
    parser_gd.set_defaults(func=grading)
    parser_gd.add_argument('course_id', help='ID of the ISIS course', type=int)
    parser_gd.add_argument('-u', '--user')
    parser_gd.add_argument('-p', '--password')
    parser_gd.add_argument('-f', '--filter', help='Only export grading items based on prefix.', type=str)
    parser_gd.add_argument('-e', '--exclude', help='Exclude grading items based on prefix.', type=str)
    parser_gd.add_argument('--no-feedback', help='Do not export feedback', action='store_true')
    parser_gd.add_argument('-g', '--include-groups',
                           help='Fetch participant groups and add them in an extra column',
                           action='store_true')

    creds_group = parser_gd.add_mutually_exclusive_group()
    creds_group.add_argument('--store-credentials',
                             help='Stores credentials for the given user in the default keyring backend.',
                             action='store_true')
    creds_group.add_argument('--clear-credentials',
                             help='Deletes any stored credentials for the given user.',
                             action='store_true')


def setup_parser_groups(parser_groups):
    parser_groups.set_defaults(func=show_groups)
    parser_groups.add_argument('course_id', help='ID of the ISIS course', type=int)

    parser_groups.add_argument('-u', '--user')
    parser_groups.add_argument('-p', '--password')

    parser_groups.add_argument('-g', '--group', help='Exact name of the group to show/modify', type=str)

    mod_group = parser_groups.add_mutually_exclusive_group()
    mod_group.add_argument('-a', '--add', type=str, help='Add participant with given student id or email from group')
    mod_group.add_argument('-r', '--remove', type=str, help='Remove participant with student id or email from group')
    mod_group.add_argument('-s', '--show', action='store_true', help='Just show group members (default).')
    mod_group.add_argument('--batch-add', action='store_true',
                           help='Read emails/student ids from stdin and add them to the group')
    mod_group.add_argument('--batch-remove', action='store_true',
                           help='Read emails/student ids from stdin and remove them from the group')

    creds_group = parser_groups.add_mutually_exclusive_group()
    creds_group.add_argument('--store-credentials',
                             help='Stores credentials for the given user in the default keyring backend.',
                             action='store_true')
    creds_group.add_argument('--clear-credentials',
                             help='Deletes any stored credentials for the given user.',
                             action='store_true')


def setup_parser_dpw(parser_dpw):
    parser_dpw.set_defaults(func=lambda args: clear_credentials(args.user))
    parser_dpw.add_argument('user', help='TUB account to be forgotten.', type=str)


def main():
    description = '''A collection of scraping tools for the TU Berlin ISIS platform.
    '''
    parser = argparse.ArgumentParser(prog='isis', description=description)
    subparsers = parser.add_subparsers(help='Available subcommands', dest='subcommand')

    parser_pt = subparsers.add_parser('participants', aliases=['pt'], description=description_pt)
    setup_parser_pt(parser_pt)

    parser_dl = subparsers.add_parser('assignments', aliases=['dl'], description=description_dl, epilog=epilog_dl)
    setup_parser_dl(parser_dl)

    parser_s = subparsers.add_parser('search', aliases=['s'], description=description_s)
    setup_parser_s(parser_s)

    parser_gd = subparsers.add_parser('grading', aliases=['gd'], description=description_gd)
    setup_parser_gd(parser_gd)

    parser_dpw = subparsers.add_parser('deletepw', aliases=['gd'], description='Deletes a saved TUB password.')
    setup_parser_dpw(parser_dpw)

    parser_groups = subparsers.add_parser('groups', aliases=['grp'], description=description_grp)
    setup_parser_groups(parser_groups)

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_usage()
        return

    args.func(args)


if __name__ == '__main__':
    main()
