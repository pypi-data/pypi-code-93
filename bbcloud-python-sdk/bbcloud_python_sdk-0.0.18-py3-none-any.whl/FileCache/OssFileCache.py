import calendar
import datetime
import logging
import os
import random
import re
import string
import time
import traceback
from collections import Counter
from distutils.sysconfig import PREFIX

import bbcloud_python_sdk
import oss2 as oss2


class OssFileCache():
    def __init__(self, access_key_id, access_key_secret, endpoint, bucket_name, cache_path_root,
                 namespace=''):
        self.cache_path_root = cache_path_root
        self.namespace = namespace
        auth = oss2.Auth(access_key_id=access_key_id,
                         access_key_secret=access_key_secret)
        self.bucket = oss2.Bucket(auth=auth, endpoint=endpoint,
                                  bucket_name=bucket_name)

    def random_str(self, num):
        salt = ''.join(random.sample(string.ascii_letters + string.digits, num))

        return salt

    def set_namespace(self, namespace):
        self.namespace = namespace
        logging.info('setting namespace %s' % namespace)
        return self

    def set(self, key, file_path, del_local=True):
        """
        缓存文件到OSS
        @param key: 缓存键
        @param file_path: 文件路径 url|本地目录|本地文件
        @param del_local: 缓存后是否删除本地文件
        """
        local_path = '/tmp/%s.%s' % (self.random_str(30), self.random_str(30))
        cache_path = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)

        if file_path:
            if isinstance(file_path, str) and re.match("http", file_path) and file_path is not None:
                bbcloud_python_sdk.download_file(url=file_path, save_path=local_path)
            elif isinstance(file_path, dict) or isinstance(file_path, list):
                bbcloud_python_sdk.create_json_file(dst_path=local_path, dist=file_path)
            elif os.path.isdir(file_path):
                bbcloud_python_sdk.zip_dirs(zip_filename=local_path, file_dir=file_path)
            elif os.path.isfile(file_path):
                local_path = file_path

            self.bucket.put_object_from_file(cache_path, local_path)

            if del_local:
                if os.path.exists(local_path):
                    os.remove(local_path)
            return True

    def get(self, key, local_file):
        """
        从OSS获取缓存文件
        @param key: 缓存键
        @param local_file: 文本保存路径
        """
        cache_path = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)

        try:
            self.bucket.get_object_to_file(cache_path, local_file)
            return True
        except oss2.exceptions.NoSuchKey:
            if os.path.exists(local_file):
                os.remove(local_file)
            return False

    def delete(self, key):
        """
        删除OSS缓存文件
        @param key:
        """
        cache_path = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)

        try:
            self.bucket.delete_object(cache_path)
            return True
        except oss2.exceptions.NoSuchKey:
            return False

    def exist(self, key):
        """
        判断缓存文件是否存在
        :param key:
        :return: True|False
        """
        cache_path = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)

        return self.bucket.object_exists(cache_path)

    def list_cache_objects(self):
        """
        获取文件夹OSS缓存文件
        """
        prefix_path = "%s/%s" % (self.cache_path_root, self.namespace)
        list_dir = []
        marker = ''
        begin = False
        while (marker != '') or (not begin):
            list_objects = self.bucket.list_objects(prefix=prefix_path, max_keys=100, marker=marker)
            marker = list_objects.next_marker
            begin = True
            for i in list_objects.object_list:
                list_dir.append(i)
        return list_dir

    def list_dir(self, deep_num):
        prefix_path = "%s/%s" % (self.cache_path_root, self.namespace)
        all_list_dir = []
        one_list_dir = []
        marker = ''
        begin = False
        while (marker != '') or (not begin):
            list_objects = self.bucket.list_objects(prefix=prefix_path, max_keys=100, marker=marker)
            marker = list_objects.next_marker
            begin = True
            for i in list_objects.object_list:
                all_list_dir.append(i.key.rsplit("/", 1)[0])
        for data in all_list_dir:
            tmp_dir = data.rsplit("/", len(data.split('/')) - len(prefix_path.split('/')) - deep_num)[0]
            if tmp_dir not in one_list_dir:
                one_list_dir.append(tmp_dir)
        if self.cache_path_root in one_list_dir:
            one_list_dir.remove(self.cache_path_root)
        if prefix_path in one_list_dir:
            one_list_dir.remove(prefix_path)
        return one_list_dir
