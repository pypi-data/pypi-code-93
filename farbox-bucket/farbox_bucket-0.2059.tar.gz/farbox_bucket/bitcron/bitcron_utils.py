# coding: utf8
import os

bitcron_sync_list_url = "https://bitcron.com/service/sync_list"
bitcron_sync_content_url = "https://bitcron.com/service/sync_content"
# bitcron_sync_should_url = "https://bitcron.com/service/sync_should"
# bitcron_sync_url = "https://bitcron.com/service/sync"



def get_bitcron_sync_cursor_filepath(root):
    filepath = os.path.join(root, "bitcron.cursor")
    return filepath

def get_bitcron_sync_cursor(root):
    filepath = get_bitcron_sync_cursor_filepath(root)
    try:
        with open(filepath, "rb") as f:
            cursor = f.read().strip()
        return cursor
    except:
        pass
    return ""


def set_bitcron_sync_cursor(root, cursor):
    filepath = get_bitcron_sync_cursor_filepath(root)
    try:
        with open(filepath, "wb") as f:
            f.write(cursor)
    except:
        pass
