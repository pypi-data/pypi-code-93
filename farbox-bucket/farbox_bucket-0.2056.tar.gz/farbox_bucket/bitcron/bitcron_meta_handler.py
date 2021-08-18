# coding: utf8
import os
import requests
import re
import hashlib
import time

MARKDOWN_EXTS = ['.md', '.markdown', '.txt', '.mk']

def is_a_markdown_file(path):
    if os.path.splitext(path)[1].lower() in MARKDOWN_EXTS:
        return True
    else:
        return False

def is_a_hidden_path(path):
    if re.search('(^|/)(\.|~$)', path):
        return True
    elif re.search(r'~\.[^.]+$', path):
        return True
    elif path.endswith('~'):
        return True
    else:
        return False

def md5_for_file(file_path, block_size=2**20): # block_size=1Mb
    if os.path.isdir(file_path):
        return 'folder'
    if not os.path.exists(file_path):
        return ''
    f = open(file_path, 'rb')
    md5_obj = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5_obj.update(data)
    f.close()
    return md5_obj.hexdigest()

def create_file(filepath, content):
    # 会确保父目录的存在
    if os.path.isdir(filepath):
        return
    parent = os.path.split(filepath)[0]
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)
    if isinstance(content, unicode):
        content = content.encode("utf8")
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as old_f:
            old_content = old_f.read()
        if content == old_content:
            return # 内容没有变化，ignore
    try:
        with open(filepath, 'wb') as f:
            f.write(content)
    except IOError:
        time.sleep(1) # 先重试，不行再report错误
        with open(filepath, 'wb') as f:
            f.write(content)


def bitcron_handle_meta(token, meta, root_path, sync_content_url):
    """
    :param token:
    :param meta:
    :param root_path:
    :param sync_content_url:
    :return: None 表示 ignore，空字符表示成功，反之则是错误信息
    """
    # prefix 更多是一个范围，一般是一个 site folder
    root_path = root_path.rstrip('/')
    relative_path = meta.get("path", "").lstrip('/')  # 这个是大小写敏感的, 相对于根目录下的相对路径
    if not relative_path:
        return
    if relative_path.startswith("_data/email_status/") or relative_path == "_data/email_status": # 批量邮件通知
        return
    if relative_path.startswith("_data/visits/") or relative_path == "_data/visits": # 每日的访问数据统计
        return
    full_path = os.path.join(root_path, relative_path) # 本地电脑的path
    version = meta.get('version', '')
    is_deleted = meta.get('is_deleted', False)
    is_dir = meta.get('is_dir', False)
    file_id = meta.get("_id")
    if not file_id:
        return
    if is_a_hidden_path(relative_path): # 隐藏文件不处理
        return
    if relative_path.startswith('_cache/') or relative_path == '_cache': # cache 文件不处理
        return
    if is_deleted:
        # 不处理 delete 的逻辑
        return
    elif is_dir:
        if not os.path.isdir(full_path):
            try:
                os.makedirs(full_path)
            except:
                pass
        return ""
    else: # 具体的文件
        need_download = True
        if os.path.isfile(full_path):
            old_version = md5_for_file(full_path)
            if old_version == version:
                need_download = False

        if need_download:
            # 需要下载具体的文件
            timeout = 20* 60
            if is_a_markdown_file(full_path):
                timeout = 2*60
            try:
                response = requests.post(sync_content_url, data=dict(token=token, id=file_id), timeout=timeout)
            except:
                return 'failed to get file for %s, maybe network error' % relative_path
            if response.status_code >= 400:
                # ignore
                return 'fail to get %s, status code is %s' % (relative_path, response.status_code)
            content = response.content
            try:
                create_file(full_path, content)
                print("download %s" % relative_path)
                return ""
            except OSError:
                return 'failed to create file then ignore %s' % relative_path
        else:
            print("%s at client already" % relative_path)