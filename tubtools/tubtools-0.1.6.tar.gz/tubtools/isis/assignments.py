#!/usr/bin/python
import os
import bs4

from ..login import interactive_login
from ..extract import extract_all_submissions
from .common import ISIS_ASSIGNMENTS_URL, ISIS_URL, ISIS_SHIB_URL, get_course_shortname


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


def main(args):
    # NEVES = 13941

    _, _, s = interactive_login(ISIS_URL, ISIS_SHIB_URL, user=args.user, pw=args.password,
                                store_creds=args.store_credentials, clear_creds=args.clear_credentials)

    sname = get_course_shortname(s, args.course_id)
    print('Fetching assignments for course {0}...'.format(sname))
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
