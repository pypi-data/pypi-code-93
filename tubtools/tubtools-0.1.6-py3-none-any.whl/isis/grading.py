import dataclasses
import logging
from typing import List

import bs4
import requests

from .common import ISIS_URL, ISIS_SHIB_URL, ISIS_GRADING_URL, _extract_session_key
from .participants import get_participants, Participant
from ..login import interactive_login


@dataclasses.dataclass
class GradingItem:
    name: str
    itemid: str


def find_grading_items(soup: bs4.BeautifulSoup):
    fieldset = soup.find('fieldset', attrs={'id': 'id_gradeitems'})
    items = []
    for i in fieldset.find_all('input'):
        item_id = i.get('id')
        if item_id and item_id.startswith('id_itemids_'):
            iid = item_id.split('id_itemids_')[1]
            name = i.parent.text.strip()
            items.append(GradingItem(name, iid))

    return items


def get_grading_table(s: requests.Session, course_id: int,
                      include_filter: str = None,
                      exclude_filter: str = None,
                      no_feedback: bool = False):
    get_url = f'{ISIS_GRADING_URL}/export/txt/index.php'
    rsp = s.get(get_url, params={'id': course_id})
    soup = bs4.BeautifulSoup(rsp.text, 'html.parser')
    sesskey = _extract_session_key(soup)
    grading_items = find_grading_items(soup)

    post_url = f'{ISIS_GRADING_URL}/export/txt/export.php'
    data = {
        "mform_isexpanded_id_gradeitems": "1",
        "checkbox_controller1": "0",
        "mform_isexpanded_id_options": "0",
        "id": f"{course_id}",
        "sesskey": f"{sesskey}",
        "_qf__grade_export_form": "1",
        "export_feedback": ["0", "1"] if not no_feedback else '0',
        "export_onlyactive": ["0", "1"],  # 0 and 1 means yes.
        "display[real]": ["0", "1"],  # because reasons!
        "display[percentage]": "0",  # 0 only means no
        "display[letter]": "0",
        "decimals": "2",
        "separator": "comma",
        # "submitbutton": "Herunterladen"   <-- Not necessary
    }

    for g in grading_items:
        include = (include_filter is None or g.name.startswith(include_filter)) and \
                  (exclude_filter is None or not g.name.startswith(exclude_filter))
        data[f'itemids[{g.itemid}]'] = ['0', '1'] if include else '0'

    rsp = s.post(post_url, data=data)
    return rsp.text


def get_student_table(s: requests.Session, course_id: int) -> dict[int, tuple[str, str]]:
    """This function uses the grading table export generate a mapping between student ids and ISIS participants.
    For this to work the account must be a full staff member (not a tutor!) and you only get the students that are
    enrolled in the ISIS course.
    """
    csv = get_grading_table(s, course_id, no_feedback=True)

    # CSV Format:
    # first name, last name, institute, department, email, student id, category 1 ...
    #     0           1          2          3         4        5

    header = True
    id_ix = None

    log = logging.getLogger(__name__)

    table = {}
    for line in csv.splitlines():
        cols = line.split(',')

        if header:
            try:
                id_ix = cols.index('Ordnungsmerkmal')
                header = False
                continue
            except ValueError as e:
                raise ValueError('Could not find student id row in the grading table export. '
                                 'Are you a TUB staff member?') from e

        # The column name is language dependent (except for student id)
        # Therefore we rely on a stable ordering

        email = cols[4]
        fullname = cols[0].strip('"') + ' ' + cols[1].strip('"')

        try:
            student_id = int(cols[id_ix].split('16900')[-1])
        except ValueError as e:
            log.warning(f'Did not find student id for student {fullname} ({email})')
            continue

        table[student_id] = (fullname, email)

    return table


def grading(args):
    _, _, s = interactive_login(ISIS_URL, ISIS_SHIB_URL, user=args.user, pw=args.password,
                                store_creds=args.store_credentials, clear_creds=args.clear_credentials)

    lines = get_grading_table(s, args.course_id, include_filter=args.filter, exclude_filter=args.exclude,
                              no_feedback=args.no_feedback)

    pindex = {}
    if args.include_groups:
        participants: List[Participant] = get_participants(s, args.course_id)

        for p in participants:
            pindex[p.email] = p.groups

    header_skipped = False
    email_ix = -1
    for line in lines.splitlines():
        cols = line.split(',')

        if not header_skipped:
            header_skipped = True

            try:
                email_ix = cols.index('E-Mail-Adresse')
            except ValueError:
                email_ix = cols.index('"Email address"')  # Yay, internationalization!

            if args.include_groups:
                cols.append('Group')
            print(','.join(cols))
            continue

        if args.include_groups:
            if cols[email_ix] in pindex:
                groups = pindex[cols[email_ix]]
                cols.append(groups[0] if len(groups) > 0 else '')

        print(','.join(cols))

