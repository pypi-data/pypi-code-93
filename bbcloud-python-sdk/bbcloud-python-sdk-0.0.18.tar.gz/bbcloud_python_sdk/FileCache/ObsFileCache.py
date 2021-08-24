import logging
import os
import random
import re
import string

from obs import ObsClient

import bbcloud_python_sdk


class ObsFileCache():
    def __init__(self, access_key_id, secret_access_key, endpoint, bucket_name, cache_path_root):
        self.bucket_name = bucket_name
        self.cache_path_root = cache_path_root
        self.obs = ObsClient(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            server=endpoint
        )

    def random_str(self, num):
        salt = ''.join(random.sample(string.ascii_letters + string.digits, num))

        return salt

    def set_namespace(self, namespace):
        self.namespace = namespace
        logging.info('setting namespace %s' % namespace)
        return self

    def set(self, key, file_path, del_local=True):
        """
        缓存文件到OBS
        @param key: 缓存键
        @param file_path: 文件路径 url|本地目录|本地文件
        @param del_local: 缓存后是否删除本地文件
        """
        local_path = '/tmp/%s.%s' % (self.random_str(30), self.random_str(30))
        object_key = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)

        if file_path:
            if isinstance(file_path, str) and re.match("http", file_path) and file_path is not None:
                bbcloud_python_sdk.download_file(url=file_path, save_path=local_path)
            elif isinstance(file_path, dict) or isinstance(file_path, list):
                bbcloud_python_sdk.create_json_file(dst_path=local_path, dist=file_path)
            elif os.path.isdir(file_path):
                bbcloud_python_sdk.zip_dirs(zip_filename=local_path, file_dir=file_path)
            elif os.path.isfile(file_path):
                local_path = file_path

            resp = self.obs.putFile(
                bucketName=self.bucket_name,
                objectKey=object_key,
                file_path=local_path
            )
            if resp.status < 300:
                print('requestId:', resp.requestId)
                print('etag:', resp.body.etag)
                print('versionId:', resp.body.versionId)
                print('storageClass:', resp.body.storageClass)
                if del_local:
                    if os.path.exists(local_path):
                        os.remove(local_path)
                return True
            else:
                print('errorCode:', resp.errorCode)
                print('errorMessage:', resp.errorMessage)
                return False

    def get(self, key, local_file):
        """
        从OBS获取缓存文件
        @param key: 缓存键
        @param local_file: 文本保存路径
        """
        cache_path = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)

        try:
            resp = self.obs.getObject(
                bucketName=self.bucket_name,
                objectKey=cache_path,
                downloadPath=local_file
            )
            if resp.status < 300:
                print('requestId:', resp.requestId)
                print('url:', resp.body.url)
                return True
            else:
                print('errorCode:', resp.errorCode)
                print('errorMessage:', resp.errorMessage)
                return False
        except:
            import traceback
            print(traceback.format_exc())

    def delete(self, key):
        """
        删除OSS缓存文件
        @param key:
        """
        cache_path = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)
        resp = self.obs.deleteObject(
            bucketName=self.bucket_name,
            objectKey=cache_path
        )
        if resp.status < 300:
            print('requestId:', resp.requestId)
            print('deleteMarker:', resp.body.deleteMarker)
            print('versionId:', resp.body.versionId)
            return True
        else:
            print('errorCode:', resp.errorCode)
            print('errorMessage:', resp.errorMessage)
            return False

    def exist(self, key):
        """
        判断缓存文件是否存在
        :param key:
        :return: True|False
        """
        cache_path = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)

        resp = self.obs.getObjectMetadata(
            bucketName=self.bucket_name,
            objectKey=cache_path
        )
        if resp.status < 300:
            return True
        else:
            return False

    def list_cache_objects(self):
        """
        获取OBS命名空间下的缓存文件
        """
        prefix_path = "%s/%s" % (self.cache_path_root, self.namespace)
        list_dir = []
        marker = ''
        begin = False
        while (marker != '') or (not begin):
            list_objects = self.obs.listObjects(
                bucketName=self.bucket_name,
                prefix=prefix_path,
                max_keys=100,
                marker=marker
            )
            marker = list_objects.next_marker
            begin = True
            for i in list_objects.contents:
                list_dir.append(i)
        return list_dir

    def list_dir(self, ):
        prefix_path = "%s/%s" % (self.cache_path_root, self.namespace)
        all_list_dir = []
        one_list_dir = []
        marker = ''
        begin = False
        while (marker != '') or (not begin):
            list_objects = self.obs.listObjects(
                bucketName=self.bucket_name,
                prefix=prefix_path,
                max_keys=100,
                marker=marker
            )
            marker = list_objects.next_marker
            begin = True
            for i in list_objects.contents:
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
