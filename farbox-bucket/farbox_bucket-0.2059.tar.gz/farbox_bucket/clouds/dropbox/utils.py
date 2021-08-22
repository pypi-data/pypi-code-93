# coding: utf8
from farbox_bucket.utils import string_types
from farbox_bucket.utils.env import get_env
from farbox_bucket.utils.ssdb_utils import hset, hdel, hget


Dropbox_APP_KEY = get_env("dropbox_app_key")
Dropbox_APP_SECRET = get_env("dropbox_app_secret")

if Dropbox_APP_KEY and Dropbox_APP_SECRET:
    is_dropbox_server_valid = True
else:
    is_dropbox_server_valid = False

__DROPBOX_COLLECTION_DB_NAMES = [
    "dropbox_account"
    "dropbox_bucket",
    "dropbox_cursor",
]


def get_dropbox_cursor_key(account_id, bucket):
    if not account_id or not bucket:
        return None
    if not isinstance(account_id, string_types) or not isinstance(bucket, string_types):
        return None
    key = "%s-%s" % (account_id, bucket)
    return key


def get_dropbox_cursor(account_id, bucket):
    key = get_dropbox_cursor_key(account_id, bucket)
    if not key:
        return None
    return hget("dropbox_cursor", key)


def set_dropbox_cursor(account_id, bucket, cursor):
    key = get_dropbox_cursor_key(account_id, bucket)
    if not key:
        return
    if isinstance(cursor, string_types):
        hset("dropbox_cursor", key, cursor)


def clear_dropbox_cursor(account_id, bucket):
    key = get_dropbox_cursor_key(account_id, bucket)
    if not key:
        return
    hdel("dropbox_cursor", key)






