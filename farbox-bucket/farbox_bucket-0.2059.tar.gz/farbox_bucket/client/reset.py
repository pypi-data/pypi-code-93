#coding: utf8
import os
from farbox_bucket.utils.path import join
from farbox_bucket.utils.client_sync.sync_utils import clear_sync_meta_data

def reset_farbox_sync_meta(root, app_name_for_sync=None):
    if not os.path.isdir(root):
        return
    app_name_for_sync = app_name_for_sync or 'farbox_bucket'
    cursor_file = join(root, ".farbox.cursor")
    if os.path.isfile(cursor_file):
        os.remove(cursor_file)
    clear_sync_meta_data(root=root, app_name=app_name_for_sync)