"""
adapter.py
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/25/21 5:14 PM
"""

import io
import os
import shutil
import time
import mimetypes

from PIL import Image
from abc import ABCMeta, abstractmethod, ABC


class AdapterInterface:
    """
    适配器接口
    """

    __metaclass__ = ABCMeta

    THUMBS_NAME: str = '__thumbs'

    NEW_FOLDER_NAME_FORMAT = '{new_folder_name}({num})'

    NEW_FILE_NAME_FORMAT = '{file_name}({num}){file_extension}'

    DEFAULT_CHUNK_SIZE = 64 * 2 ** 10

    def __init__(self, acl, resource_type_info: dict, config: dict = None, **kwargs):
        """
        初始化
        :param config: 配置信息
        :param adapter_info:
        """

        self.acl = acl

        if config is None:
            config = {}
        self.config = config
        self.resource_type_info = resource_type_info
        self.base_path = resource_type_info.get('path', None)

        # 检查目录是否可用
        if not self.base_path:
            raise ValueError('BASE_PATH 不可用')

    @abstractmethod
    def get_folders(self, path: str) -> list:
        """
        获取目录列表
        :param path:
        :return:
        """

    @abstractmethod
    def get_files(self, path: str) -> list:
        """
        获取文件列表
        :param path:
        :return:
        """

    def move_file(self, old_path: str, old_file_name: str, new_path: str, new_file_name: str) -> bool:
        """
        移动文件
        :param old_path:
        :param old_file_name:
        :param new_path:
        :param new_file_name:
        :return:
        """

    def copy_file(self, old_path: str, old_file_name: str, new_path: str, new_file_name: str) -> bool:
        """
        复制文件
        :param old_path:
        :param old_file_name:
        :param new_path:
        :param new_file_name:
        :return:
        """

    @abstractmethod
    def image_resize(self, path: str, file_name: str, width: int, height: int) -> str:
        """
        修改图片尺寸
        :param path:
        :param file_name:
        :param width:
        :param height:
        :return:
        """

    @abstractmethod
    def create_folder(self, path: str, new_folder_name: str) -> bool:
        """
        创建子目录
        :param path:
        :param new_folder_name:
        :return:
        """

    @abstractmethod
    def image_info(self, path: str, file_name: str) -> dict:
        """
        获取图像信息
        :param path:
        :param file_name:
        :return:
        """

    @abstractmethod
    def thumbnail(self, path: str, file_name: str, width: int, height: int) -> tuple:
        """
        缩略图
        :param path:
        :param file_name:
        :param width:
        :param height:
        :return:
        """

    def file_upload(self, path: str, file_name: str, file_obj) -> bool:
        """
        文件上传
        :param path: 目录
        :param file_name: 文件名
        :param file_obj: 文件对象
        :return:
        """

        return self.write(self.get_full_path(path, file_name), file_obj)

    def image_preview(self, path: str, file_name: str, width: int, height: int) -> tuple:
        """
        图片预览
        :param path:
        :param file_name:
        :param width:
        :param height:
        :return:
        """

        return self.thumbnail(path, file_name, width, height)

    @abstractmethod
    def get_full_path(self, *paths, add_base_path: bool = True) -> str:
        """
        获取完整路经
        :param paths:
        :param add_base_path:
        :return:
        """

    @abstractmethod
    def isdir(self, path: str) -> bool:
        """
        判断是否为目录
        :param path:
        :return:
        """

    @abstractmethod
    def isfile(self, path: str) -> bool:
        """
        判断是否为文件
        :param path:
        :return:
        """

    @abstractmethod
    def has(self, path: str) -> bool:
        """
        判断文件或目录是否存在
        :param path:
        :return:
        """

    def get_new_file_name(self, path: str, file_name: str, file_extension: str, num: int = 0) -> str:
        """
        获取新的文件名 - 检查文件是否存在，并进行重命名
        :param path:
        :param file_name:
        :param file_extension:
        :param num:
        :return:
        """

        num = self._get_new_file_name(path, file_name, file_extension, num)
        if num > 0:
            return self.NEW_FILE_NAME_FORMAT.format(file_name=file_name, file_extension=file_extension, num=num)
        else:
            return file_name + file_extension

    def _get_new_file_name(self, path: str, file_name: str, file_extension: str, num: int = 0) -> int:
        """
        获取新的文件名 - 检查文件是否存在，并进行重命名
        :param path:
        :param file_name:
        :param file_extension:
        :param num:
        :return:
        """

        if num > 0:
            file_full_name = self.NEW_FILE_NAME_FORMAT.format(
                file_name=file_name,
                num=num,
                file_extension=file_extension
            )
        else:
            file_full_name = file_name + file_extension

        if self.has(self.get_full_path(path, file_full_name)):
            num = num + 1
            return self._get_new_file_name(path, file_name, file_extension, num)
        else:
            return num

    def get_new_folder_name(self, path: str, new_folder_name: str, num: int = 0) -> str:
        """
        检查目录是否存在，并进行重命名
        :param path:
        :param new_folder_name:
        :param num:
        :return:
        """
        num = self._get_new_folder_name(path, new_folder_name, num)
        if num > 0:
            return self.NEW_FOLDER_NAME_FORMAT.format(new_folder_name=new_folder_name, num=num)
        else:
            return new_folder_name

    def _get_new_folder_name(self, path: str, new_folder_name: str, num: int = 0) -> int:
        if num > 0:
            folder_name = self.NEW_FOLDER_NAME_FORMAT.format(new_folder_name=new_folder_name, num=num)
        else:
            folder_name = new_folder_name
        if self.has(self.get_full_path(path, folder_name)):
            num = num + 1
            return self._get_new_folder_name(path, new_folder_name, num)
        return num

    @staticmethod
    def get_resized_images_data(images: list, sizes_config: dict) -> dict:
        """
        缩略图数据整合
        :param images:
        :param sizes_config:
        :return:
        """
        data = {}
        __custom = images
        for k, v in sizes_config.items():
            for image in images:
                _file_name, _file_extension = os.path.splitext(image)
                if image.endswith('__' + v + _file_extension):
                    data[k] = image
                    __custom.remove(image)
        data['__custom'] = __custom
        return data

    @abstractmethod
    def delete(self, path: str, is_dir: bool = None) -> bool:
        """
        通用删除
        :param path:
        :param is_dir:
        :return:
        """

    @abstractmethod
    def rename(self, src: str, dst: str, is_dir=None) -> bool:
        """
        通用重命名
        :param src:
        :param dst:
        :param is_dir:
        :return:
        """

    @abstractmethod
    def write(self, path: str, content: io.BytesIO) -> bool:
        """
        写入BytesIO到文件
        :param path:
        :param content:
        :return:
        """

    @abstractmethod
    def read(self, path) -> bytes:
        """
        读取文件
        :param path:
        :return:
        """

    @abstractmethod
    def get_file_size(self, path: str) -> float:
        """
        获取文件大小
        :param path:
        :return:
        """

    @abstractmethod
    def get_file_date(self, path: str) -> str:
        """
        获取文件时间
        :param path:
        :return:
        """

    @abstractmethod
    def get_file_mimetype(self, path: str) -> str:
        """
        获取文件mimetype
        :param path:
        :return:
        """

    @staticmethod
    def _get_resize_name(file_name: str, width: int, height: int) -> str:
        """
        获取修改尺寸后的图片名
        :param file_name:
        :param width:
        :param height:
        :return:
        """

        _file_name, _file_extension = os.path.splitext(file_name)
        resize_name = _file_name + '__' + str(width) + 'x' + str(height) + _file_extension
        return resize_name

    def _get_resize_path(self, path: str) -> str:
        """
        获取修改尺寸后的图片保存目录
        :param path:
        :return:
        """

        basename = os.path.basename(path)
        dirname = os.path.dirname(path)
        resize_path = os.path.join(dirname, self.THUMBS_NAME, basename)
        return resize_path


class LocalAdapter(AdapterInterface, ABC):
    """
    本地存储适配器
    """

    def __init__(self, acl, resource_type_info: dict, config: dict = None, **kwargs):
        """
        初始化
        :param kwargs:
        """

        super().__init__(
            acl=acl,
            resource_type_info=resource_type_info,
            config=config,
            **kwargs
        )

        # 根目录不存在时自动创建
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)

    def create_folder(self, path: str, new_folder_name: str) -> bool:
        _path = self.get_full_path(path, new_folder_name)
        os.mkdir(_path)
        return self.has(_path)

    def get_folders(self, path) -> list:
        return self.get_children_all(path)

    def get_files(self, path) -> list:
        return self.get_children_all(path)

    def get_children_all(self, path):
        return os.listdir(self.get_full_path(path))

    def move_file(self, old_path: str, old_file_name: str, new_path: str, new_file_name: str) -> bool:
        """
        移动文件
        :param old_path:
        :param old_file_name:
        :param new_path:
        :param new_file_name:
        :return:
        """

        old_file_path = self.get_full_path(old_path, old_file_name)

        if not self.has(old_file_path):
            return False

        new_file_path = self.get_full_path(new_path, new_file_name)

        if old_file_path == new_file_path:
            return True

        shutil.move(old_file_path, new_file_path)
        return self.has(new_file_path)

    def copy_file(self, old_path: str, old_file_name: str, new_path: str, new_file_name: str) -> bool:
        """
        复制文件
        :param old_path:
        :param old_file_name:
        :param new_path:
        :param new_file_name:
        :return:
        """

        old_file_path = self.get_full_path(old_path, old_file_name)

        if not self.has(old_file_path):
            return False

        new_file_path = self.get_full_path(new_path, new_file_name)

        if old_file_path == new_file_path:
            return True

        shutil.copyfile(old_file_path, new_file_path)
        return self.has(new_file_path)

    def image_resize(self, path: str, file_name: str, width: int, height: int) -> str:
        """
        修改图片尺寸
        :param path:
        :param file_name:
        :param width:
        :param height:
        :return:
        """

        path = self.get_full_path(path, file_name)

        new_file_name = self._get_resize_name(file_name, width, height)

        save_dir = self._get_resize_path(path)
        save_path = os.path.join(save_dir, new_file_name)

        if os.path.isfile(save_path):
            return new_file_name

        image = Image.open(path)

        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
        out = image.resize((width, height), Image.ANTIALIAS)
        out.save(save_path)
        return new_file_name

    def thumbnail(self, path: str, file_name: str, width: int, height: int) -> tuple:
        _path = self.get_full_path(path, file_name)
        image = Image.open(_path)
        size = (width, height) if width and height else image.size
        image.thumbnail(size)
        output = io.BytesIO()
        image.save(output, image.format)
        content = output.getvalue()
        output.close()
        file_type, file_encoding = mimetypes.guess_type(_path)
        return content, file_type, file_encoding

    def image_info(self, path: str, file_name: str) -> dict:
        _path = self.get_full_path(path, file_name)
        im = Image.open(_path)
        img_info = {
            "date": self.get_file_date(_path),
            "size": self.get_file_size(_path),
            'width': im.width,
            'height': im.height,
        }
        return img_info

    def get_full_path(self, *paths, add_base_path: bool = True) -> str:
        """
        获取完整路经
        :param paths:
        :param add_base_path:
        :return:
        """

        paths = (i.replace('\\', '/').strip('/') for i in paths)
        if add_base_path:
            path = os.path.join(self.base_path, *paths)
        else:
            path = os.path.join(*paths)
        return path

    def isdir(self, path: str) -> bool:
        return os.path.isdir(path)

    def isfile(self, path: str) -> bool:
        return os.path.isfile(path)

    def has(self, path: str) -> bool:
        """
        判断文件或目录是否存在
        :param path:
        :return:
        """
        return os.path.exists(path)

    def delete(self, path: str, is_dir: bool = None) -> bool:
        """
        通用删除
        :param path:
        :param is_dir:
        :return:
        """

        if not os.path.exists(path):
            return True
        if is_dir is None:
            is_dir = os.path.isdir(path)

        if is_dir:
            shutil.rmtree(path)
        else:
            os.remove(path)

        return not os.path.exists(path)

    def rename(self, src: str, dst: str, is_dir=None) -> bool:
        """
        通用重命名
        :param src:
        :param dst:
        :param is_dir:
        :return:
        """
        os.rename(src, dst)
        return os.path.exists(dst)

    def write(self, path: str, content: io.BytesIO) -> bool:
        """
        写入BytesIO到文件
        :param path:
        :param content:
        :return:
        """

        with open(path, 'wb') as f:
            while True:
                data = content.read(self.DEFAULT_CHUNK_SIZE)
                if not data:
                    break
                f.write(data)
            content.close()
        return self.has(path)

    def read(self, path) -> bytes:
        bytes_io = io.BytesIO()
        with open(path, 'rb') as f:
            while True:
                data = f.read(self.DEFAULT_CHUNK_SIZE)
                if not data:
                    break
                bytes_io.write(data)
        value = bytes_io.getvalue()
        bytes_io.close()
        return value

    def get_file_size(self, path: str) -> float:
        return os.path.getsize(path) / 1024

    def get_file_date(self, path: str) -> str:
        return time.strftime("%Y%m%d%H%M%S", time.localtime(os.path.getmtime(path)))

    def get_file_mimetype(self, path: str) -> str:
        return mimetypes.guess_type(path)[0]
