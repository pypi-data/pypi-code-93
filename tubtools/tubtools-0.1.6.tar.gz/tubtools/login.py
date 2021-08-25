import sys

import requests

from .credentials import load_credentials, store_credentials, clear_credentials, fallback


def login(user, pw, url, shib_url):
    s = requests.Session()
    s.get(url)  # Create a flow for this session

    r = s.get(shib_url)  # We will be redirected so save response

    # I have no idea what this does but without this first post we cant login
    payload = {
        'shib_idp_ls_exception.shib_idp_session_ss':'',
        'shib_idp_ls_success.shib_idp_session_ss': True,
        'shib_idp_ls_value.shib_idp_session_ss': '',
        'shib_idp_ls_exception.shib_idp_persistent_ss': '',
        'shib_idp_ls_success.shib_idp_persistent_ss': True,
        'shib_idp_ls_value.shib_idp_persistent_ss': '',
        'shib_idp_ls_supported': '',
        '_eventId_proceed': True
    }
    r = s.post(r.url, data=payload)

    payload = {
        'j_username': user,
        'j_password': pw,
        '_eventId_proceed': ''
    }

    r = s.post(r.url, data=payload)

    for h in r.history:
        for c in h.cookies.keys():
            if '_shibsession_' in c:
                return s

    return None


def interactive_login(url: str, shib_url: str, user=None, pw=None, clear_creds=False, store_creds=False):
    if user is None:
        user = input('Username:')

    if clear_creds:
        clear_credentials(user)

    if pw is None:
        pw = load_credentials(user)

        if pw is None:
            pw = fallback()
            store_creds = store_creds or input('Save pw? [Y/n]:') in ['', 'Y', 'y']

    s = login(user, pw, url, shib_url)

    if s is None:
        print('Login failed!')
        sys.exit(1)

    # print('Login Successful')

    if store_creds:
        store_credentials(user, pw)

    return user, pw, s



