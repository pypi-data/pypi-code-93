# coding: utf8
import os
from .bitcron_meta import get_bitcron_metas
from .bitcron_meta_handler import bitcron_handle_meta
from .bitcron_utils import bitcron_sync_content_url, bitcron_sync_list_url, get_bitcron_sync_cursor, set_bitcron_sync_cursor


def sync_from_bitcron_server(root, token):
    if not os.path.isdir(root):
        return
    old_cursor = get_bitcron_sync_cursor(root)
    new_cursor, metas = get_bitcron_metas(token, cursor=old_cursor, sync_list_url=bitcron_sync_list_url)
    if not metas:
        print("no need to sync from server, no metas found")
        return
    else:
        print('will try to sync %s files from server.' % len(metas))
    error_logs = []
    should_set_cursor = True
    for meta in metas:
        error_log = bitcron_handle_meta(token, meta, root, bitcron_sync_content_url)
        if error_log:
            error_logs.append(error_log)
            if "network error" in error_log:
                should_set_cursor = False
    if new_cursor and should_set_cursor: # 处理之后，再保存cursor
        set_bitcron_sync_cursor(root, new_cursor)
    if new_cursor is None and not metas:
        print("syncing maybe failed, check your sync config?")