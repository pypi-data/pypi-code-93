import dataclasses
import re
import shlex
import sys

import bs4
import requests

from .common import ISIS_URL, ISIS_SHIB_URL, ISIS_GROUPS_URL, ISIS_GROUP_MEMBERS_URL, _extract_session_key
from .grading import get_student_table
from .participants import Participant, get_participants
from ..login import interactive_login


@dataclasses.dataclass
class Isis_Group:
    name: str
    id: int
    course: int
    members: list[Participant] = dataclasses.field(default_factory=lambda: [])

    def inspect(self, session: requests.Session):
        params = {
            'id': self.course,
            'group': self.id,
            'act_ajax_getmembersingroup': ''
        }

        rsp = session.get(ISIS_GROUPS_URL, params=params)
        d = rsp.json()

        self.members = []
        re_email = re.compile(' (\S*@\S*)$')
        for role in d:
            for user in role['users']:
                match = re_email.search(user['name'])
                if match:
                    fullname = user['name'][0:match.span()[0]]
                    email = user['name'][match.span()[0] + 2:-1]
                    isis_id = user['id']
                    pt = Participant(email, fullname, isis_id)
                    self.members.append(pt)

    def _get_sesskey(self, session) -> int:
        # TODO: We should probably do some caching here
        params = {
            'group': self.id,
        }

        rsp = session.get(ISIS_GROUP_MEMBERS_URL, params=params)
        soup = bs4.BeautifulSoup(rsp.text, 'html.parser')
        return _extract_session_key(soup)

    def add_users(self, session: requests.Session, isis_ids: list[int]):
        sesskey = self._get_sesskey(session)

        params = {
            'group': self.id,
        }
        data = {
            'sesskey': sesskey,
            'addselect[]': isis_ids,
            'addselect_searchtext': '',
            'add': 'foobar'
        }

        session.post(ISIS_GROUP_MEMBERS_URL, params=params, data=data)

    def remove_users(self, session: requests.Session, isis_ids: list[int]):
        sesskey = self._get_sesskey(session)

        params = {
            'group': self.id,
        }
        data = {
            'sesskey': sesskey,
            'removeselect[]': isis_ids,
            'removeselect_searchtext': '',
            'remove': 'foobar'
        }

        session.post(ISIS_GROUP_MEMBERS_URL, params=params, data=data)


def get_all_groups(session: requests.Session, course_id) -> list[Isis_Group]:
    params = {
        'id': course_id
    }

    rsp = session.get(ISIS_GROUPS_URL, params=params)
    soup = bs4.BeautifulSoup(rsp.text, 'html.parser')
    grps = soup.find(id='groups')

    res = []
    for opt in grps.find_all('option'):
        name = ' '.join(opt['title'].split()[:-1])
        value = int(opt['value'])
        res.append(Isis_Group(name, value, course_id))

    return res


def show_groups(args):
    _, _, s = interactive_login(ISIS_URL, ISIS_SHIB_URL, user=args.user, pw=args.password,
                                store_creds=args.store_credentials, clear_creds=args.clear_credentials)

    groups = get_all_groups(s, args.course_id)

    if not args.group and (args.show or args.add or args.remove or args.batch_add or args.batch_remove):
        print('No group name supplied for show/add/remove!')
        sys.exit(-1)

    if not args.group:
        for g in groups:
            print(g.name)
        return

    else:
        try:
            group = next(filter(lambda g: g.name == args.group, groups))

            if args.show or not (args.add or args.remove or args.batch_add or args.batch_remove):
                group.inspect(s)
                for m in group.members:
                    print(m.email, shlex.quote(m.fullname))
                return
            elif args.add:
                pts = get_participants(s, args.course_id)

                if args.add.isnumeric():  # Assume a student id
                    student_ids = get_student_table(s, args.course_id)

                    try:
                        _, email = student_ids[int(args.add)]
                    except KeyError:
                        print(f'No student found for id {args.add}!')
                        print(student_ids)
                        sys.exit(-1)
                else:  # assume its an email
                    email = args.add

                try:
                    user = next(filter(lambda p: p.email == email, pts))
                    group.add_users(s, [user.isis_id])
                except StopIteration:
                    print(f'No participant found for email {args.add}!')
                    sys.exit(-1)

            elif args.remove:
                pts = get_participants(s, args.course_id)
                if args.remove.isnumeric():
                    student_ids = get_student_table(s, args.course_id)

                    try:
                        _, email = student_ids[int(args.remove)]
                    except KeyError:
                        print(f'No student found for id {args.remove}!')
                        sys.exit(-1)

                else:  # assume its an email
                    email = args.remove

                try:
                    user = next(filter(lambda p: p.email == email, pts))
                    group.remove_users(s, [user.isis_id])
                except StopIteration:
                    print(f'No participant found for email {args.remove}!')
                    sys.exit(-1)

            elif args.batch_add or args.batch_remove:
                pts = get_participants(s, args.course_id)
                student_ids = get_student_table(s, args.course_id)

                def convert_to_isis_id(row: str):
                    if row.isnumeric():
                        try:
                            _, email = student_ids[int(row)]
                        except KeyError:
                            print(f'No student found for id {row}!')
                            return None
                    else:
                        email = row

                    try:
                        user = next(filter(lambda p: p.email == email, pts))
                        return user.isis_id
                    except StopIteration:
                        print(f'No participant found for email {row}!')
                        return None

                rows = map(str.strip, sys.stdin.readlines())
                isis_ids = list(filter(lambda r: r is not None, map(convert_to_isis_id, rows)))

                print(isis_ids)

                if args.batch_add:
                    group.add_users(s, isis_ids)
                else:
                    group.remove_users(s, isis_ids)

        except StopIteration:
            print(f'No group named "{args.group}" found!')
            sys.exit(-1)
