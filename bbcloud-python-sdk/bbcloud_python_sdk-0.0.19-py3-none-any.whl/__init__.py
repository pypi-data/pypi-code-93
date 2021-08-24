import base64
import codecs
import glob
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile
from urllib import request, parse
from urllib.parse import quote, urlparse
from collections import Counter

import requests

from bbcloud_python_sdk.FileCache import FileCache

logging.basicConfig(level=logging.WARNING)


def download_file(url, save_path):
    """
    下载文件
    :param url: URL
    :param save_path: 保存文件名
    :return:
    """
    try:
        content = request.urlopen(url)
        basename = os.path.dirname(save_path)
        if not os.path.exists(basename):
            os.makedirs(basename)
        with open(save_path, 'wb') as f:
            f.write(content.read())
        return 'ok'
    except Exception as e:
        return e


def execute(command, cwd='/', login=False):
    """
    执行本地命令
    :param command: 命令
    :param cwd: 执行环境
    :return: 输出，错误信息(bytes类型)
    """
    if login:
        command = 'bash --login -c "%s" ' % command

    sub = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, shell=True)
    (stdout, stderr) = sub.communicate(timeout=3600)
    print(stdout.decode('utf-8', 'ignore'))
    if sub.returncode != 0:
        raise Exception(stderr.decode('utf-8', 'ignore'))


def delete_dir_then_move_dir(file_from, file_to):
    """
    删除文件夹并移动新文件夹替换之
    :param file_from:
    :param file_to:
    :return:
    """
    if os.path.exists(file_from):
        if os.path.exists(file_to):
            shutil.rmtree(file_to)
        shutil.move(file_from, file_to)


def delete_dir_then_copy_dir(file_from, file_to, symlinks=False, ignore=None):
    """
    删除文件夹并复制新文件夹替换之
    :param file_from:
    :param file_to:
    :param symlinks:
    :param ignore:
    :return:
    """
    if os.path.exists(file_from):
        if os.path.exists(file_to):
            shutil.rmtree(file_to)
        try:
            shutil.copytree(file_from, file_to, symlinks, ignore)
        except Exception as e:
            if isinstance(e, shutil.Error):
                pass


def make_dir(target_dir):
    """
    递归新建目录
    :param target_dir:
    :return:
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


def remake_dir(target_dir):
    """
    删除并重建目录
    :param target_dir:
    :return:
    """
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)


def pull_git_project(project_dir, git_branch):
    project_branch_dir = os.path.join(project_dir, git_branch)
    execute('git checkout .', project_branch_dir)
    execute('git clean -xfd ', project_branch_dir)
    execute('git pull origin %s' % (git_branch), project_branch_dir)


def clone_git_project(git_url, git_branch, clone_dir, origin_object_branch="master"):
    git_origin_object_branch_dir = os.path.join(clone_dir, origin_object_branch)
    clone_branch_dir = os.path.join(clone_dir, git_branch)
    if os.path.exists(clone_branch_dir) == False:
        make_dir(clone_branch_dir)

    if os.path.exists(git_origin_object_branch_dir):
        execute('git init', clone_branch_dir)
        execute('git remote add origin %s' % (git_url), clone_branch_dir)
        execute("echo ../../../%s/.git/objects/ > .git/objects/info/alternates" % (origin_object_branch),
                clone_branch_dir)
        execute("git pull origin %s:%s" % (git_branch, git_branch), clone_branch_dir)
        execute("git checkout %s" % (git_branch), clone_branch_dir)
    else:
        execute('git clone -b %s %s %s' % (origin_object_branch, git_url, origin_object_branch), clone_dir)
        clone_git_project(git_url, git_branch, clone_dir, origin_object_branch)


def sync_project_git_branch_dir(git_url, project_dir, branch_name):
    if os.path.exists(project_dir) == False:
        make_dir(project_dir)

    project_dir_branch_dir = os.path.join(project_dir, branch_name)
    if os.path.exists(os.path.join(project_dir_branch_dir, '.git')):
        pull_git_project(project_dir, branch_name)
    else:
        clone_git_project(git_url, branch_name, project_dir)


def get_gitlab_project_info_by_id(host, token, project_id):
    return json.loads(request.urlopen(
        '%s/api/v4/projects/%s?private_token=%s' % (host, project_id, token)).read())


def get_gitlab_project_info_by_url(web_url, token):
    parse = urlparse(web_url)
    host = parse.netloc
    path = parse.path[1:]
    url = 'http://%s/api/v4/projects/%s?private_token=%s' % (host, quote(path, safe=''), token)
    return json.loads(request.urlopen(url).read())


def download_gitlab_project(host, token, project_id, git_branch, dst_dir):
    download_file(
        "%s/api/v4/projects/%s/repository/archive.zip?sha=%s&private_token=%s" % (
            host,
            project_id, quote(git_branch), token), dst_dir)


def get_dir_files_size(src_path, file_size_dict={}, ignore_dir=''):
    files = os.listdir(src_path)
    for file in files:
        if os.path.splitext(file)[0].startswith('.') or \
                os.path.join(src_path, file) == os.path.join(src_path, ignore_dir):
            # 排除.开头的隐藏文件和目录
            continue
        file_path = os.path.join(src_path, file)
        if os.path.isdir(file_path):
            get_dir_files_size(file_path, file_size_dict)
        else:
            # 去除掉公共目录起始再存入json
            file_size_dict[file_path] = os.path.getsize(file_path)

    return file_size_dict


def create_json_file(dst_path, dist):
    with open(dst_path, 'w+', encoding='utf-8') as f:
        json.dump(dist, f, ensure_ascii=False, indent=4)


def get_md5_sum(file_path, block=4096):
    """
    获取MD5校验值
    :param file_path:
    :param block:
    :return:
    """
    with open(file_path, 'rb') as f:
        md5_obj = hashlib.md5()
        while 1:
            data = f.read(block)
            if not data:
                break
            md5_obj.update(data)

    return str(md5_obj.hexdigest()).lower()


def rm_dir_tree(path_list):
    """
    递归删除文件夹
    :param path_list: 文件路径列表
    :return:
    """
    for path in path_list:
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)


def untar(file_name, dst_dir):
    tar = tarfile.open(file_name, "r:gz")
    file_names = tar.getnames()
    for file_name in file_names:
        tar.extract(file_name, dst_dir)
    tar.close()


def rm_file_by_path(path_list):
    """
    删除文件
    :param path_list: 文件路径列表
    :return:
    """
    for path in path_list:
        if os.path.exists(path):
            os.remove(path)


def copy_anything(src_path, dst_path, make_dirs=True):
    """
     自动识别是文件还是文件夹，并拷贝
    :param src_path:
    :param dst_path:
    :param make_dirs:
    :return:
    """
    if os.path.isfile(src_path):
        dst_folder_path = os.path.split(dst_path)[0]
        if not os.path.exists(dst_folder_path) and make_dirs:
            os.makedirs(dst_folder_path)
        shutil.copy(src_path, dst_path)
    else:
        shutil.copytree(src_path, dst_path)


def delete_then_replace_file(file_from, file_to):
    """
    删除文件并复制新文件替换之
    :param file_from:
    :param file_to:
    :return:
    """
    if os.path.exists(os.path.dirname(file_to)):
        if os.path.exists(file_to):
            os.remove(file_to)
    else:
        os.makedirs(os.path.dirname(file_to))
    shutil.copy(file_from, file_to)


def rm_dir(path):
    """
    递归删除文件夹
    :param path: 文件路径
    :return:
    """
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)


def fory_tree(from_path, to_path, symlinks=False, is_pre_del=False):
    """
    递归复制文件夹
    :param from_path: 起始目录
    :param to_path: 目标目录
    :param symlinks: 是否保持符号链接
    :param is_pre_del: 是否执行前先删除目标目录
    :return:
    """
    if os.path.exists(from_path):
        if is_pre_del and os.path.exists(to_path):
            shutil.rmtree(to_path)

        try:
            shutil.copytree(from_path, to_path, symlinks)
        except Exception as e:
            if isinstance(e, shutil.Error):
                pass


def copy_dir_replace_file(src_path, dst_path, ignore=[], skip_hide_dir=True, skip_hide_file=True, replace=True):
    """
    递归复制目录，自动创建目录，遇到同名文件时可选是否替换
    :param src_path:
    :param dst_path:
    :param skip_hide_dir: 跳过隐藏目录
    :param skip_hide_file: 跳过隐藏文件
    :param replace: 替换同名文件
    :return:
    """
    if not os.path.exists(src_path):
        pass
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if root.startswith('.') and skip_hide_dir:
                # 排除.开头的隐藏目录
                continue
            if os.path.splitext(file)[0].startswith('.') and skip_hide_file:
                # 排除.开头的隐藏文件
                continue
            in_ignore = False
            for item in ignore:
                if item in root:
                    in_ignore = True
            if in_ignore:
                continue

            dst_target_path = dst_path + root.split(src_path)[1]
            if not os.path.exists(dst_target_path):
                os.makedirs(dst_target_path)
            if replace:
                shutil.copy(os.path.join(root, file), dst_target_path)
            elif not os.path.isfile(os.path.join(dst_target_path, file)):
                shutil.copy(os.path.join(root, file), dst_target_path)


def aapt_verify_data_legality(dir_name):
    """
    检验文件的合法性
    :param dir_name:
    :return:
    """
    command = 'aapt package -A %s' % (dir_name)
    execute(command)


def fix_copy_tree(src, dest):
    try:
        shutil.copytree(src, dest)
    except Exception as e:
        if isinstance(e, shutil.Error):
            # 因为是远程共享目录，文件系统不一样，在复制的时候会因为元数据产生一些问题，但是文件似乎没有问题
            pass
        else:
            raise e


def replace_strings_in_file(old_new, file_path, encoding='utf-8'):
    """
    替换文件中的字符串
    :param old_new: 要替换的字符串,目标字符串
    :param file_path: 文件路径
    :param encoding: 编码格式
    :return:
    """
    with codecs.open(file_path, 'r', encoding) as f:
        strings = f.read()
        for old, new in old_new:
            strings = strings.replace(old, new)

    with open(file_path, 'wb+') as f:
        f.write(strings.encode('utf-8'))


def add_strings_in_file(new, file_path, encoding='utf-8'):
    """
    向文件添加新行写入字符串
    :param new: 新字符串
    :param file_path: 文件路径
    :param encoding: 编码格式
    :return:
    """
    with codecs.open(file_path, 'r', encoding) as f:
        m_str = f.read() + '\n' + new

    with open(file_path, 'w', encoding=encoding) as f:
        f.write(m_str)


def replace_string_in_file(old, new, file_path, encoding='utf-8'):
    """
    替换文件中的字符串
    :param old: 要替换的字符串
    :param new: 目标字符串
    :param file_path: 文件路径
    :param encoding: 编码格式
    :return:
    """
    with codecs.open(file_path, 'r', encoding) as f:
        strings = f.read().replace(old, new)
    with open(file_path, 'wb') as f:
        f.write(strings.encode('utf-8'))


def scramble(list_1, list_2):
    """
    判断list_1是否属于list2
    :return:
    """
    return len(Counter(list_1) - Counter(list_2)) == 0


def get_result_dict(log_obj):
    """
    获取结果返回值
    :return:
    """
    result_list = []
    for log_dict in log_obj.log_list:
        result_list.append('[code:%s]：%s' % (str(list(log_dict.keys())[0]), str(list(log_dict.values())[0])))
    log = '\n'.join(result_list)

    result_list.clear()
    for err_dict in log_obj.err_list:
        result_list.append('[code:%s]：%s' % (str(list(err_dict.keys())[0]), str(list(err_dict.values())[0])))
    err_log = '\n'.join(result_list)

    return {'log': log, 'err_log': err_log}


def remove_null_dir(target_path):
    """
    递归删除空目录
    :param target_path:
    :return:
    """
    if not os.path.exists(target_path):
        logging.info("[警告]尝试删除掉一个不存在的目录：%s" % target_path)
        return
    if os.path.isdir(target_path):
        for p in os.listdir(target_path):
            d = os.path.join(target_path, p)
            if os.path.isdir(d):
                remove_null_dir(d)
    if not os.listdir(target_path):
        os.rmdir(target_path)


def remove_hide_dir_file(path):
    """
    删除.开头的隐藏目录和文件
    :param path:
    :return:
    """
    for item in os.listdir(path):
        cur_path = os.path.join(path, item)
        if item.startswith('.'):
            if os.path.isdir(cur_path):
                shutil.rmtree(cur_path)
            else:
                try:
                    os.remove(cur_path)
                except OSError:
                    shutil.rmtree(cur_path)
        else:
            if os.path.isdir(cur_path):
                remove_hide_dir_file(cur_path)


def move_dir_replace_dir(src_path, dst_path, replace=True):
    """
    递归复制目录，自动创建目录，遇到同名文件时可选是否替换，完成之后再删除原目录（其实就相当于是剪切文件夹）
    :param src_path:
    :param dst_path:
    :param replace:
    :return:
    """
    copy_dir_replace_file(src_path, dst_path, replace=replace)
    if os.path.exists(src_path):
        shutil.rmtree(src_path)


def move_replace_dir(dir_from, dir_to):
    """
    移动并替换目录（dir_to只要指定到目标目录的父目录即可，否则会导致移动到dir_to里头的dir_to目录去）
    :param dir_from:
    :param dir_to:
    :return:
    """
    if os.path.exists(os.path.join(dir_to, os.path.basename(dir_from))):
        shutil.rmtree(os.path.join(dir_to, os.path.basename(dir_from)))

    if os.path.exists(dir_from):
        shutil.move(dir_from, dir_to)


def delete_file_rewrite_strings_to_file(file_path, content, encoding='utf-8'):
    """
    删除文件并重新写入字符串到文件
    :param file_path:
    :param content:
    :param encoding:
    :return:
    """
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'wb+') as f:
        content_byte = content if isinstance(content, bytes) else content.encode(encoding)
        f.write(content_byte)


def replace_strings_in_string(old_new, string):
    """
    替换字符串中的字符串
    :param old_new: 要替换的字符串,目标字符串
    :param string: 字符串
    :return: 新字符串
    """
    for old, new in old_new:
        string = string.replace(old, new)
    return string


def post(url, data):
    """
    post请求
    :param url:
    :param data:
    :return:
    """
    req = request.Request(url)
    data = parse.urlencode(data)
    opener = request.build_opener(request.HTTPCookieProcessor())
    response = opener.open(req, data.encode('utf-8'))
    return response.read()


def remove_chinese_file(assets_dir):
    """
    移除中文文件
    :param path: 文件夹
    :return:
    """

    def is_chinese(char):
        """判断是否包含中文"""
        if not isinstance(char, str):
            char = char.decode('utf8')
        return re.search(r"[\u4e00-\u9fa5]+", char) is not None

    def is_space(char):
        """判断是否包含空格"""
        return re.search(r"\s", char) is not None

    def is_startswith(char):
        """检查字符串是否是以指定子字符串开头"""
        return char.startswith('%')

    res = []
    for root, dirs, files in os.walk(assets_dir):
        for f in files:
            if is_chinese(f) or is_space(f) or is_startswith(f):
                res.append(os.path.join(root, f))
        for d in dirs:
            if is_chinese(d) or is_space(d) or is_startswith(d):
                res.append(os.path.join(root, d))

    for r in res:
        if os.path.exists(r):
            if os.path.isdir(r):
                shutil.rmtree(r)
            else:
                os.remove(r)


def get_json_value(key, path, file_name='config.json'):
    """
    获得配置值
    :param key: 键
    :param path: 文件所在路径
    :param file_name: 文件名称
    :return:
    """
    c_file = os.path.join(path, file_name)

    if os.path.exists(c_file):
        with open(c_file) as f:
            c = json.load(f)
            if key in c:
                return c[key]
    return


def glud_snd(zh_path, zht_path):
    """
    传入两个i18n 替换zh的音频到zht
    :param zh_path: 简体中文目录
    :param zht_path: 繁体中文目录
    :return:
    """
    if not os.path.exists(zht_path):
        if os.path.exists(zh_path):
            shutil.copytree(zh_path, zht_path)
    elif os.path.exists(zh_path):
        m_list = os.walk(zh_path)
        for dirs, root, files in m_list:
            for m_file in files:
                tmp_dir = dirs.replace(zh_path, zht_path)
                if not os.path.exists(tmp_dir):
                    os.makedirs(tmp_dir)
                # 两边文件夹一致了，开始比较文件
                from_file = os.path.join(dirs, m_file)
                to_file = os.path.join(tmp_dir, m_file)
                if not os.path.exists(to_file):
                    shutil.copy(from_file, to_file)


def iterator_get_file_md5sum_to_json(path, rlt):
    """
    迭代获取目录下所有文件md5值
    :param path: 路径
    :param rlt: 结果
    :return:
    """
    paths = os.listdir(path)
    for _, item in enumerate(paths):
        sub_path = os.path.join(path, item)
        if os.path.isdir(sub_path):
            rlt[item] = {}
            iterator_get_file_md5sum_to_json(sub_path, rlt[item])
        else:
            rlt[item] = get_md5_sum(sub_path)


def iterator_get_file_md5sum_to_json_file(res_path, json_path):
    """
    迭代获取目录下所有文件md5值，并保存到json文件
    :param res_path: 路径
    :param json_path: 保存的json路径
    :return:
    """
    result = {}
    iterator_get_file_md5sum_to_json(res_path, result)
    with open(json_path, 'w') as f:
        json.dump(result, f)


def zip_files(zip_filename, file_list, arc_name=''):
    """
    压缩文件（列表）
    :param zip_filename: 压缩包名称
    :param file_list: 文件列表
    :param arc_name: 压缩包内的目录名称
    :return:
    """
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in file_list:
                zf.write(file, os.path.join(arc_name, os.path.basename(file)))
    except Exception as e:
        raise Exception(e)


def zip_files_by_arc(zip_filename, file_dict):
    """
    压缩文件（集合）
    :param zip_filename: 压缩包名称
    :param file_dict: 文件列表
    :return:
    """
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in file_dict:
                zf.write(file_dict[file], os.path.join(file, os.path.basename(file_dict[file])))
        return ''

    except Exception as e:
        return str(e)


def zip_dirs(zip_filename, file_dir, arc_name=''):
    """
    压缩目录
    :param zip_filename: 压缩包名称
    :param file_dir: 文件目录
    :param arc_name: 压缩包内的目录名称
    :return:
    """
    file_list = []

    try:
        for root, dirs, files in os.walk(file_dir):
            for dir_path in dirs:
                file_list.append(os.path.join(root, dir_path))
            for name in files:
                file_list.append(os.path.join(root, name))

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            for tar in file_list:
                zip_name = tar[len(file_dir):]
                if arc_name:
                    zip_name = os.path.join(arc_name, os.path.basename(zip_name))
                zf.write(tar, zip_name)
    except Exception as e:
        raise Exception(e)


def md5_convert(string):
    """
    计算字符串md5值
    :param string: 输入字符串
    :return: 字符串md5
    """
    m = hashlib.md5()
    m.update(string.encode())
    return m.hexdigest()


def base64_convert(string):
    """
    计算字符串base64值
    :param string: 输入字符串
    :return: 字符串base64
    """
    encodestr = base64.b64encode(string.encode('utf-8'))
    return encodestr


def retry(func):
    def inner(*args, **kwargs):
        count = 0
        while count < 3:
            try:
                func(*args, **kwargs)
                return
            except Exception as e:
                count += 1
                time.sleep(2)

    return inner


def get_middle_str(content, startStr, endStr):
    """
    获取文本字符串中间
    :param content:
    :param startStr:
    :param endStr:
    :return:
    """
    startIndex = content.index(startStr)
    if startIndex >= 0:
        startIndex += len(startStr)
    endIndex = content.index(endStr, startIndex)
    return content[startIndex:endIndex]


def get_right_string(html, start_str):
    """
    获取文本字符串右边
    :param html:
    :param start_str:
    :return:
    """
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        return html[start:-1].strip()
    return ""


def unzip(file_name, dst_dir=None):
    r = zipfile.is_zipfile(file_name)
    if r:
        fz = zipfile.ZipFile(file_name, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
        fz.close()
    else:
        print('This is not zip')


def get_last_commit_sha_by_branch(git_host, git_token, git_project_id, git_branch):
    url = '%s/api/v4/projects/%s/repository/commits/%s' % (
        git_host, git_project_id, quote(git_branch, 'utf-8'))
    res = requests.request('GET', url,
                           params={
                               'private_token': git_token
                           },
                           stream=True)

    if res.status_code == 200:
        return json.loads(res.content)['id']
    else:
        raise Exception('commit sha get failure %s' % url)


def get_gitlab_last_pipeline_id_by_branch(git_host, git_token, git_project_id, git_branch):
    url = '%s/api/v4/projects/%s/pipelines' % (
        git_host, git_project_id)
    res = requests.request('GET', url,
                           params={
                               'private_token': git_token,
                               'status': 'success',
                               'ref': quote(git_branch, 'utf-8'),
                               'per_page': 1,
                               'order_by': 'id',
                               'sort': 'desc'
                           },
                           stream=True)

    if res.status_code == 200:
        return json.loads(res.content)[0]['id']
    else:
        raise Exception('pipeline id get failure %s %s' % (url, res.status_code))
