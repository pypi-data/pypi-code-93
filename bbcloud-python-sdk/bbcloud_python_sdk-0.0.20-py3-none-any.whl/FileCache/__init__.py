import logging
import os

import bbcloud_python_sdk as utils
from .ObsFileCache import ObsFileCache

from .OssFileCache import OssFileCache

from .SynologyFileCache import SynologyFileCache


def runtime_logging(func):
    def wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        logging.info(
            'FileCache:%s:%s:%s:%s' % (func.__name__, args[0].namespace, args if len(args) > 1 else kwargs, res))
        return res

    return wrap


class FileCache():
    def __init__(self, available_area, using_area):
        self.namespace = ''
        self.using_area = using_area
        self.available_area = available_area
        self.default_engine = self.getEngine(using_area=using_area)

    def getEngine(self, using_area=None):
        if not using_area:
            using_area = self.using_area
        engine = self.available_area[using_area]['engine']
        config = self.available_area[using_area]['config']
        if engine == 'OssFileCache':
            return OssFileCache(access_key_id=config['access_key_id'],
                                access_key_secret=config['access_key_secret'],
                                endpoint=config['endpoint'],
                                bucket_name=config['bucket_name'],
                                cache_path_root=config.get('cache_path_root', 'OssFileCache')
                                )
        elif engine == 'SynologyFileCache':
            return SynologyFileCache(
                ip_address=config['ip_address'],
                port=config['port'],
                username=config['username'],
                password=config['password'],
                cache_path_root=config.get('cache_path_root', 'SynologyFileCache')
            )
        elif engine == 'ObsFileCache':
            return ObsFileCache(
                access_key_id=config['access_key_id'],
                secret_access_key=config['access_key_secret'],
                endpoint=config['endpoint'],
                bucket_name=config['bucket_name'],
                cache_path_root=config.get('cache_path_root', 'ObsFileCache'))

    def set_namespace(self, namespace):
        self.namespace = namespace
        return self

    @runtime_logging
    def set(self, key, file_path, del_local=True, set_all_area=False):
        if set_all_area:
            self.default_engine.set_namespace(namespace=self.namespace).set(key=key, file_path=file_path,
                                                                            del_local=del_local)
            for area in self.available_area:
                if area is not self.using_area:
                    self.getEngine(using_area=area).set_namespace(namespace=self.namespace).set(key=key,
                                                                                                file_path=file_path,
                                                                                                del_local=del_local)
        else:
            return self.default_engine.set_namespace(namespace=self.namespace).set(key=key, file_path=file_path,
                                                                                   del_local=del_local)

    @runtime_logging
    def get(self, key, local_file, default=None, auto_unzip=False, auto_delete_local_zip=True, auto_untar=False,
            auto_delete_local_tar=True):

        if not os.path.exists(os.path.dirname(local_file)):
            utils.make_dir(os.path.dirname(local_file))

        is_get = self.default_engine.set_namespace(namespace=self.namespace).get(key=key, local_file=local_file)
        if not is_get:
            if default:
                self.set(key=key, file_path=default, del_local=True)
                is_get = self.get(key=key, local_file=local_file)
            else:
                return False

        if is_get:
            if os.path.splitext(local_file)[-1] == '.zip' and auto_unzip:
                unzip_dir = os.path.dirname(local_file)
                if os.path.exists(local_file):
                    utils.unzip(file_name=local_file, dst_dir=unzip_dir)
                    if auto_delete_local_zip:
                        os.remove(local_file)
            elif os.path.splitext(local_file)[-1] == '.gz' and auto_untar:
                untar_dir = os.path.dirname(local_file)
                if os.path.exists(local_file):
                    utils.untar(file_name=local_file, dst_dir=untar_dir)
                    if auto_delete_local_tar:
                        os.remove(local_file)
            return True
        else:
            return False

    @runtime_logging
    def delete(self, key, delete_all_area=False):
        if delete_all_area:
            self.default_engine.set_namespace(namespace=self.namespace).delete(key=key)

            for area in self.available_area:
                if area is not self.using_area:
                    self.getEngine(using_area=area).set_namespace(namespace=self.namespace).delete(key=key)
            return True
        else:
            return self.default_engine.set_namespace(namespace=self.namespace).delete(key=key)

    @runtime_logging
    def exist(self, key):
            return self.default_engine.set_namespace(namespace=self.namespace).exist(key=key)

    @runtime_logging
    def list_cache_objects(self):
        return self.default_engine.set_namespace(namespace=self.namespace).list_cache_objects()

    @runtime_logging
    def list_dir(self, deep_num):
        return self.default_engine.set_namespace(namespace=self.namespace).list_dir(deep_num=deep_num)
