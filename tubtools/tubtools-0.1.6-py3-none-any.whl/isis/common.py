import re

import bs4

ISIS_URL = 'https://isis.tu-berlin.de'
ISIS_SHIB_URL = f'{ISIS_URL}/auth/shibboleth/index.php'
ISIS_ASSIGNMENTS_URL = f'{ISIS_URL}/mod/assign'
ISIS_COURSE_URL = f'{ISIS_URL}/course'
ISIS_USER_URL = f'{ISIS_URL}/user'
ISIS_AJAX_URL = f'{ISIS_URL}/lib/ajax'
ISIS_SEARCH_URL = f'{ISIS_COURSE_URL}/search.php'
ISIS_GRADING_URL = f'{ISIS_URL}/grade'
ISIS_GROUPS_URL = f'{ISIS_URL}/group/index.php'
ISIS_GROUP_MEMBERS_URL = f'{ISIS_URL}/group/members.php'


def get_course_shortname(session, course_id):
    url = f"{ISIS_COURSE_URL}/edit.php"
    r = session.get(url, params={'id': course_id})
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    input_sname = soup.find('input', attrs={'id': 'id_shortname'})

    # Note: We could get the short name for the course somewhere else without edit rights but
    # a) This is the most reliable source
    # b) You can't download anything without trainer rights anyways

    if input_sname is None:
        print(r.text)
        raise ValueError('Could not find course name on the edit page. Do you have edit rights for this course?')

    return input_sname.get('value')


def _extract_session_key(soup):
    scripts = soup.find_all('script')
    r_sesskey = re.compile('\"sesskey\":\"[a-zA-Z0-9]*\"')
    sesskey = None
    for s in scripts:
        if s.string is None:
            continue

        match = r_sesskey.search(s.string)
        if match is not None:
            sesskey = match.group(0).split(':')[1].strip('"')
            break

    if sesskey is None:
        raise ValueError('Could not find session key on page!')

    return sesskey
