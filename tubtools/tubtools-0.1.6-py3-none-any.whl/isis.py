#!/usr/bin/python
import getpass
import os
import argparse

from .login import login
from .extract import extract_all_submissions

import bs4

ISIS_URL = 'https://isis.tu-berlin.de'
ISIS_SHIB_URL = f'{ISIS_URL}/auth/shibboleth/index.php'
ISIS_ASSIGNMENTS_URL = f'{ISIS_URL}/mod/assign'


def get_assignments(session, course_id):
    url = f"{ISIS_ASSIGNMENTS_URL}/index.php"
    r = session.get(url, params={'id': course_id})
    soup = bs4.BeautifulSoup(r.text, 'html.parser')

    rows = soup.find_all('tr', attrs={'class': ['', 'lastrow']})
    assignments = []
    for r in rows:
        for cell in r.find_all('td', attrs={'class': 'cell c1'}):
            a = {'name': cell.text,
                 'link': cell.a.get('href'),
                 'id': cell.a.get('href').split('id=')[1]}
            assignments.append(a)

    return assignments


def download_submissions(session, assign_id):
    url = f'{ISIS_ASSIGNMENTS_URL}/view.php'
    r = session.get(url, params={'id': assign_id,
                                 'action': 'downloadall'})

    return r.content


def main():
    # NEVES = 13941

    description = '''This script allows you to download any assignment submissions you want
    from a TU-Berlin ISIS course and extracts it into subfolders based on 
    the students group or individually. If the submission is a tar.gz or a zip
    archive it will automatically try to extract it.

    WARNING: The auto-extraction happens without input sanitation. Only use
    this tool if you trust your students.   
    '''
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('course_id', help='ID of the ISIS course', type=int)
    parser.add_argument('-a', '--all', help='Download submissions for all assignments', action='store_true')
    parser.add_argument('-s', '--separate',
                        help='Extract submission for each student separately instead of one per group.',
                        action='store_true')

    args = parser.parse_args()

    user = input('tubIT-Name: ')
    pw = getpass.getpass(prompt='tubIT-Passwort: ')
    s = login(user, pw, ISIS_URL, ISIS_SHIB_URL)

    if s is None:
        print('Login failed!')
        return
    print('Login Successful')

    assignments = get_assignments(s, args.course_id)
    print('Found {0} assignments.'.format(len(assignments)))

    if not args.all:
        for i, a in enumerate(assignments):
            print(f'[{i}] "{a["name"]}"')
        try:
            selection = int(input('Please select the assignment:'))
        except ValueError:
            print('Invalid selection')
            return -1

        if selection not in range(0, len(assignments)):
            print('Invalid selection')
            return -1

        assignments = [assignments[selection]]

    for a in assignments:
        print(f'Fetching assignment "{a["name"]}"...')
        sub = download_submissions(s, a['id'])
        print('Done.')

        path = f'assignments/{a["name"]}/submissions'
        os.makedirs(path, exist_ok=True)
        extract_all_submissions(path, sub, by_group=(not args.separate))


if __name__ == '__main__':
    main()
