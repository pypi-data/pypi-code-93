import dataclasses
import json

import bs4

from .common import ISIS_USER_URL, ISIS_AJAX_URL, ISIS_URL, ISIS_SHIB_URL, _extract_session_key
from ..login import interactive_login


@dataclasses.dataclass
class Participant:
    email: str
    fullname: str
    isis_id: int
    groups: list = dataclasses.field(default_factory=lambda: [])
    roles: list = dataclasses.field(default_factory=lambda: [])


def get_participants(session, course_id):
    url = f"{ISIS_USER_URL}/index.php"
    r = session.get(url, params={'id': course_id})
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    sesskey = _extract_session_key(soup)

    url = f"{ISIS_AJAX_URL}/service.php"

    data = [{
        'index': 0,
        'methodname': 'core_table_get_dynamic_table_content',
        "args":
            {
                "component": "core_user",
                "handler": "participants",
                "uniqueid": "user-index-participants-{0}".format(course_id),
                "sortdata": [{"sortby": "lastname", "sortorder": 4}], "jointype": 1,
                "filters": {
                    "courseid": {
                        "name": "courseid",
                        "jointype": 1,
                        "values": [course_id]
                    }
                },
                "firstinitial": "",
                "lastinitial": "",
                "pagenumber": "1",
                "pagesize": "5000",
                "hiddencolumns": [],
                "resetpreferences": False
            }
    }]

    params = {'sesskey': sesskey,
              'info': 'core_table_get_dynamic_table_content'
              }
    r = session.post(url, json=data, params=params)

    html = r.json()[0]['data']['html']
    soup = bs4.BeautifulSoup(html, 'html.parser')
    table = soup.find('table', attrs={'id': 'participants'})

    participants = []
    for row in table.find('tbody').find_all('tr'):
        if 'emptyrow' in row.attrs['class']:
            continue

        cols = list(row.find_all('td'))
        email = cols[1].text
        fullname = cols[4].contents[0].get('data-fullname')
        isis_id = cols[0].find('input').get('id').split('user')[1]

        roles = []
        roles_available = json.loads(cols[2].find('span').get('data-options'))['options']
        roles_selected = map(lambda x: int(x), json.loads(cols[2].find('span').get('data-value')))

        for key in roles_selected:
            try:
                roles.append(next(r for r in roles_available if r['key'] == key)['value'])
            except StopIteration:
                pass

        groups = []
        groups_available = json.loads(cols[3].find('span').get('data-options'))['options']
        groups_selected = map(lambda x: int(x), json.loads(cols[3].find('span').get('data-value')))

        for key in groups_selected:
            try:
                groups.append(next(r for r in groups_available if r['key'] == key)['value'])
            except StopIteration:
                pass

        participants.append(Participant(email, fullname, isis_id, groups, roles))

    return participants


def main(args):
    _, _, s = interactive_login(ISIS_URL, ISIS_SHIB_URL, user=args.user, pw=args.password,
                                store_creds=args.store_credentials, clear_creds=args.clear_credentials)

    l = list(
        filter(lambda p: args.name is None or args.name in p.fullname,
               filter(lambda p: not args.grouped or len(p.groups) > 0,
                      filter(lambda p: args.group is None or args.group in p.groups,
                             filter(lambda p: args.role is None or args.role in p.roles,
                                    get_participants(s, args.course_id))))))

    if args.json:
        l = list(
            map(lambda p: dataclasses.asdict(p),
                l))
        print(json.dumps(l, indent=4, ensure_ascii=False))
    else:
        for p in l:
            print(f"{p.fullname}, {p.email}, {p.groups}, {p.roles}")
