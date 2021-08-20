# -*- coding=utf-8 -*-

import os
import time
import random
import math
import shutil
from enum import Enum

from pymediainfo import MediaInfo

from werkzeug.utils import secure_filename

from .utilities_helper import UtilitiesHelper


class FileMode(Enum):
    R = 'r'
    RB = 'rb'
    R_Plus = 'r+'
    RB_Plus = 'rb+'
    W = 'w'
    WB = 'wb'
    W_Plus = 'w+'
    WB_Plus = 'wb+'
    A = 'a'
    AB = 'ab'
    A_Plus = 'a+'
    AB_Plus = 'ab+'


"""file mode
1.r     Opens a file for reading only. The file pointer is placed at the beginning of the file. This is the default mode.
2.rb    Opens a file for reading only in binary format. The file pointer is placed at the beginning of the file. This is the default mode.
3.r+    Opens a file for both reading and writing. The file pointer placed at the beginning of the file.
4.rb+   Opens a file for both reading and writing in binary format. The file pointer placed at the beginning of the file.
5.w     Opens a file for writing only. Overwrites the file if the file exists. If the file does not exist, creates a new file for writing.
6.wb    Opens a file for writing only in binary format. Overwrites the file if the file exists. If the file does not exist, creates a new file for writing.
7.w+    Opens a file for both writing and reading. Overwrites the existing file if the file exists. If the file does not exist, creates a new file for reading and writing.
8.wb+   Opens a file for both writing and reading in binary format. Overwrites the existing file if the file exists. If the file does not exist, creates a new file for reading and writing.
9.a     Opens a file for appending. The file pointer is at the end of the file if the file exists. That is, the file is in the append mode. If the file does not exist, it creates a new file for writing.
10.ab   Opens a file for appending in binary format. The file pointer is at the end of the file if the file exists. That is, the file is in the append mode. If the file does not exist, it creates a new file for writing.
11.a+   Opens a file for both appending and reading. The file pointer is at the end of the file if the file exists. The file opens in the append mode. If the file does not exist, it creates a new file for reading and writing.
12.ab+  Opens a file for both appending and reading in binary format. The file pointer is at the end of the file if the file exists. The file opens in the append mode. If the file does not exist, it creates a new file for reading and writing.

"""

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'])


class IOHelper(object):

    def __init__(self):
        pass

    @staticmethod
    def check_path(path):
        if not os.path.exists(path):
            os.makedirs(path)
            return False
        return True

    @staticmethod
    def allowed_file(filename, allowed_extensions=None):
        allowed_extensions = ALLOWED_EXTENSIONS if allowed_extensions is None else allowed_extensions
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in allowed_extensions

    @staticmethod
    def save_file(file, path, use_ts=False):
        root_path = UtilitiesHelper.get_proj_root_path()
        path = (path) if path is str else path
        p = os.path.join(root_path, *path)
        if not os.path.exists(p):
            os.makedirs(p)

        file_name = file.filename
        # file_name = secure_filename(file.filename)

        if use_ts:
            file_name = IOHelper.rename_by_ts(file_name)
            # file_name, file_extension = os.path.splitext(file_name)
            # file_name += '_' + UtilitiesHelper.get_timestamp() + str(random.randrange(100, 999))
            # file_name = file_name + file_extension

        file_path = os.path.join(p, file_name)
        # return file_path.replace('\\', '/')
        try:
            file.save(file_path)
            return path + '/' + file_name
        except Exception as e:
            # raise e
            return ''

    @staticmethod
    def save_to_file(file, text, use_ts=False, encoding='utf-8', mode=FileMode.W_Plus):

        file_path, file_name = os.path.split(file)

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        # mode = 'a' if os.path.exists(file_path) else 'w'
        # mode = 'a' if os.path.exists(file) else 'x'

        # file_name = file_path if file_path != None else 'data_'
        if use_ts:
            file_name = IOHelper.rename_by_ts(file_name)
            # file_name, file_extension = os.path.splitext(file_path)
            # file_name += '_' + UtilitiesHelper.get_timestamp() + str(random.randrange(1000, 9999))
            # file_name = file_name + file_extension

        file_path = os.path.join(file_path, file_name)

        # print(mode, file_path)

        args = {}
        if mode.value.find('b') == -1:
            args['encoding'] = encoding

        try:
            with open(file_path, mode.value, **args) as f:
                f.write(text)
                return file_path
        except Exception as e:
            # raise e
            print(e)
            return ''

    @staticmethod
    def append_to_file(file, text, encoding='utf-8'):
        return IOHelper.save_to_file(file, text, False, mode=FileMode.A_Plus)

    @staticmethod
    def rename_by_ts(file_path):
        file_name, file_extension = os.path.splitext(file_path)
        file_name += '_' + UtilitiesHelper.get_timestamp() + str(random.randrange(1000, 9999))
        file_name = file_name + file_extension
        return file_name

    @staticmethod
    def rename(src, dest):
        os.rename(src, dest)

    @staticmethod
    def load_file(file_path, mode=FileMode.R, encoding='utf-8'):
        if not os.path.isfile(file_path):
            return None

        args = {}
        if mode.value.find('b') == -1:
            args['encoding'] = encoding

        with open(file_path, mode.value, **args) as f:
            a = f.read()
            # print(a)
            # return AuthModel(a)
            return a

    @staticmethod
    def get_file_name(path):
        # return os.path.basename(path)
        return os.path.splitext(path)

    @staticmethod
    def join_path(root_path, *path):
        return os.path.join(root_path, *path)

    @staticmethod
    def copy(src_file, dest_path, dest_file_name=None):
        # print(os.path.exists(dest_path))
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        file_path, file_name = os.path.split(src_file)
        if dest_file_name is not None:
            file_name = dest_file_name
        dest = os.path.join(dest_path, file_name)
        shutil.copyfile(src_file, dest)

    @staticmethod
    def remove_dir_tree(path):
        if os.path.exists(path):
            shutil.rmtree(path)

    @staticmethod
    def split_path(path):
        return os.path.split(path)

    @staticmethod
    def loop_dir(path, func):
        fs = os.listdir(path)
        for f in fs:
            f = os.path.join(path, f)
            if os.path.isdir(f):
                IOHelper.loop_dir(f, func)
            else:
                func(f)

    @staticmethod
    def rename_os(src, file_name):
        dir_name = os.path.dirname(src)
        dest = os.path.join(dir_name, file_name)
        # print(src, dest)
        os.rename(src, dest)

    @staticmethod
    def list_dir(path):
        if os.path.exists(path):
            return os.listdir(path)
        return []

    @staticmethod
    def exist_path(path):
        return os.path.exists(path)

    @staticmethod
    def get_filesize(path, unit='K'):
        r = 1
        if unit == 'K':
            r = 1024
        elif unit == 'M':
            r = 1024*1024
        else:
            r = 1

        fsize = os.path.getsize(path)
        fsize = fsize/float(r)
        return round(fsize, 2)

    @staticmethod
    def make_dirs(root, *path):
        # print(*path)
        p = IOHelper.join_path(root, *path)
        # print(p)
        if not os.path.exists(p):
            os.makedirs(p)

    @staticmethod
    def get_file_info(path):
        return os.stat(path)

    @staticmethod
    def get_media_info(path):
        media_info = MediaInfo.parse(path)
        data = media_info.to_json()
        return UtilitiesHelper.json_2_obj(data)

    @staticmethod
    def get_media_base_info(path):
        data = IOHelper.get_media_info(path)
        rst = None
        try:
            tracks = data.get('tracks')
            size = tracks[0].get('file_size')
            other_size = tracks[0].get('other_file_size')[-1]
            width = tracks[1].get('width')
            height = tracks[1].get('height')
            rst = {
                'size': size,
                'other_size': other_size,
                'width': width,
                'height': height
            }
        except Exception as e:
            print('error:', path, '\n', data)

        return rst

    @staticmethod
    def file_upload(file, save_path, *args, **kwargs):

        try:

            if file is None or len(file) == 0:
                return {
                    'code': -901,
                    'msg': 'No File Found'
                }

            file_name, file_ext = IOHelper.get_file_name(file.get('filename'))
            file_name = file_name + '_' + str(UtilitiesHelper.get_timestamp()) + file_ext

            allowed_extensions = kwargs.get('allowed_extensions')
            ext_verified = IOHelper.allowed_file(file.get('filename'), allowed_extensions=allowed_extensions)

            if not ext_verified:
                return {
                    'code': -902,
                    'msg': 'File Extension Invalid'
                }

            # max_file_size = kwargs.get('max_file_size')
            # file_size = IOHelper.get_filesize(file_path, unit='B')
            # file_size = 0
            # if file_size > max_file_size:
            #     self.code = -4
            #     self.msg = '文件大小不能超过' + (max_file_size / 1024/1024) + 'M'

            file_path = IOHelper.join_path(save_path, file_name)
            IOHelper.save_to_file(file_path, file.get('body'), use_ts=False, mode=FileMode.WB)

            return {
                'code': 900,
                'msg': 'File Upload Success'
            }

        except Exception as e:
            print('\r\r-----------------------------------------------------------------------------------------------------------\r')
            print('Time:', UtilitiesHelper.now_time(), '\r')
            print('File Upload Error:', e)
            print('\r-----------------------------------------------------------------------------------------------------------\r')
            return {
                'code': -903,
                'msg': str(e)
            }
