
import os
import json
import toml
from superprocessor import cmd


PIPS_PATH = os.path.expanduser(
    '~/.pips'
)

CREDENTIALS_PATH = os.path.join(
    PIPS_PATH, 'credentials'
)


def init_pips():
    if not os.path.exists(PIPS_PATH):
        cmd('mkdir', PIPS_PATH)
    if not os.path.exists(CREDENTIALS_PATH):
        name = input('Org Name: ')
        pips_id = input('PIPS id: ')
        with open(CREDENTIALS_PATH, 'w+') as creds_f:
            toml.dump({'credentials': {'name': name, 'pips_id': pips_id}}, creds_f)
        # cmd('echo', f'"{creds_toml}"', '>', CREDENTIALS_PATH, log=True)


def verify_action():
    res = input('Continue? [y/N]\n -> ')
    if 'y' in res:
        return True
    print('Bye.')
    return False