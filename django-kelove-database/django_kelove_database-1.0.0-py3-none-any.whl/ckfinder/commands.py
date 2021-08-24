"""
commands.py 命令解析
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/25/21 5:16 PM
"""

import base64
import io
import json
import os
import re

from .acl import Acl
from .adapter import AdapterInterface
from .exception import AclError, Error
from .response import Response
from .util import build_url, is_allowed_regex, is_allowed_extension


class AbstractCommand:
    need_base_info = True

    check_current_folder = True

    headers = {"X-Frame-Options": "SAMEORIGIN"}

    requires = []

    response_cls = Response

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        """
        初始化
        :param config: 配置
        :param resource_types: 资源目录
        :param acl: 权限控制实例
        """
        self.data = {}
        self.config = config
        self.resource_types = resource_types
        self.acl = acl
        self.GET: dict = kwargs.get('get', {})
        self.POST: dict = kwargs.get('post', {})
        self.FILE: dict = kwargs.get('file', {})

        self.base_info: dict = self._get_base_info() if self.need_base_info else {}

        self.path: str = self.base_info.get('path', None)
        self.url: str = self.base_info.get('url', None)
        self.resource_type: str = self.base_info.get('resource_type', None)
        self.resource_type_info: dict = self.resource_types.get(self.resource_type, {})
        self.current_folder: str = self.base_info.get('current_folder', None)
        self.file_name = self.GET.get('fileName', None)
        self.adapter: str = self.base_info.get('adapter', None)
        self.adapter_obj: AdapterInterface = self.base_info.get('adapter_obj', None)

        if self.check_current_folder:
            self._folder_check(self.current_folder)

        self._permissions_check()

    def response(self) -> dict:
        """
        返回响应信息
        :return:
        """

    def _is_not_hidden_file(self, file_name: str) -> bool:
        """
        判断文件名是否被允许
        :param file_name:
        :return:
        """
        return is_allowed_regex(file_name, self.config['hideFiles'])

    def _is_not_hidden_folder(self, folder_name: str) -> bool:
        """
        判断目录名是否被允许
        :param folder_name:
        :return:
        """
        return is_allowed_regex(folder_name, self.config['hideFolders'])

    def _get_base_info(self, resource_type: str = None, current_folder: str = None):
        """
        获取基础信息
        :param resource_type:
        :param current_folder:
        :return:
        """
        if resource_type is None:
            resource_type = self.GET.get('type', None)
        if current_folder is None:
            current_folder = self.GET.get('currentFolder', None)

        if not resource_type:
            raise ValueError('资源类型有误')

        if not self.resource_types:
            raise ValueError('未配置资源类型')

        resource_type_info: dict = self.resource_types.get(resource_type, None)

        if not resource_type_info:
            raise ValueError('未匹配到资源类型')

        return {
            'path': resource_type_info['path'],
            'url': resource_type_info['url'],
            'resource_type': resource_type,
            'current_folder': current_folder,
            'adapter': resource_type_info['adapter'],
            'adapter_obj': resource_type_info['adapter_obj'],
        }

    def _get_response_base_data(self, resource_type: str, current_folder: str, url: str) -> dict:
        """
        获取通用返回信息
        :param resource_type:
        :param current_folder:
        :param url:
        :return:
        """

        return {
            "resourceType": resource_type,
            "currentFolder": {
                "path": current_folder,
                "acl": self.acl.get_computed_mask(resource_type=resource_type, folder_path=current_folder),
                "url": build_url(url, current_folder, right_index=True)
            }
        }

    def _get_response(self, content, content_type='application/json', status_code=200, headers=None) -> dict:
        """
        拼装完整的 response 信息
        :param content:
        :param content_type:
        :param status_code:
        :param headers:
        :return:
        """
        if headers is None:
            headers = {}

        return self.response_cls.response(
            content=content,
            content_type=content_type,
            status_code=status_code,
            headers=headers
        )

    def _permissions_check(self):
        """
        权限检查
        :return:
        """
        if self.requires:
            acl_mask = self.acl.get_computed_mask(self.resource_type, self.current_folder)
            required_permissions_mask = 0
            for require in self.requires:
                required_permissions_mask += require
            if (acl_mask & required_permissions_mask) != required_permissions_mask:
                raise AclError('权限不足')

    def _folder_check(self, folder_name: str):
        """
        目录检查
        :param folder_name:
        :return:
        """
        if folder_name != '/':
            folder_basename = os.path.basename(folder_name.strip('/'))
            if not self._is_not_hidden_folder(folder_basename):
                raise Error('目录{folder_name}不允许被操作'.format(folder_name=folder_name))

    def _has_children(self, adapter_obj: AdapterInterface, resource_type: str, current_folder: str) -> bool:
        """
        判断是否有下级目录
        :param adapter_obj:
        :param resource_type:
        :param current_folder:
        :return:
        """
        return len([
            i
            for i in adapter_obj.get_folders(current_folder)
            if
            adapter_obj.isdir(adapter_obj.get_full_path(current_folder, i))
            and self._is_not_hidden_folder(i)
            and self.acl.is_allowed(
                resource_type,
                current_folder + '/' + i,
                self.acl.FOLDER_VIEW
            )
        ]) >= 1


class InitCommand(AbstractCommand):
    """
    初始化 Ckfinder
    """

    need_base_info = False

    check_current_folder = False

    def response(self) -> dict:
        data = {
            "enabled": self.config['enabled'],
            "s": self.config['s'],
            "c": self.config['c'],
            "images": self.config['images'],
            "thumbs": self.config['thumbs'],
            "uploadMaxSize": self.config['uploadMaxSize'],
            "uploadCheckImages": self.config['uploadCheckImages'],
            'resourceTypes': [
                {
                    "name": v['name'],
                    "allowedExtensions": ','.join(v['allowedExtensions']),
                    "deniedExtensions": ','.join(v['deniedExtensions']),
                    "hash": v['hash'],
                    "acl": self.acl.get_computed_mask(k, '/'),
                    "maxSize": v['maxSize'],
                    "hasChildren": self._has_children(v['adapter_obj'], v['name'], '/'),
                    "url": v['url']
                }
                for k, v in self.resource_types.items()
                if self.acl.is_allowed(resource_type=k, folder_path='/', permission=self.acl.FOLDER_VIEW)
            ]
        }
        return self._get_response(data)


class GetFoldersCommand(AbstractCommand):
    """
    获取目录列表
    """

    requires = [
        Acl.FOLDER_VIEW,
    ]

    def response(self) -> dict:
        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['folders'] = [
            {
                "name": f,
                "acl": self.acl.get_computed_mask(self.resource_type, self.current_folder + f),
                "hasChildren": self._has_children(
                    adapter_obj=self.adapter_obj,
                    resource_type=self.resource_type,
                    current_folder=self.current_folder + f + '/'
                )
            }
            for f in
            self.adapter_obj.get_folders(self.current_folder)
            if
            self.adapter_obj.isdir(self.adapter_obj.get_full_path(self.current_folder, f))
            and self._is_not_hidden_folder(f)
            and self.acl.is_allowed(self.resource_type, self.current_folder + f, self.acl.FOLDER_VIEW)
        ]
        return self._get_response(data)


class RenameFolderCommand(AbstractCommand):
    """
    重命名目录
    """

    requires = [
        Acl.FOLDER_RENAME
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        # 获取GET请求 newFolderName
        self.new_folder_name = self.GET.get('newFolderName', '')

    def response(self) -> dict:
        # 验证目录名是否为隐藏目录
        if not self._is_not_hidden_folder(self.new_folder_name):
            raise Error('{folder_name}名称不被允许'.format(folder_name=self.new_folder_name))

        # 检查同名目录或文件是否已存在
        if self.adapter_obj.has(
                self.adapter_obj.get_full_path(
                    os.path.dirname(self.current_folder.strip('/')),
                    self.new_folder_name
                )
        ):
            raise Error('{folder_name}目录或文件名已存在'.format(folder_name=self.new_folder_name))

        basename = os.path.basename(self.current_folder.rstrip('/'))
        dirname = os.path.dirname(self.current_folder.rstrip('/'))

        rename_folder = self.adapter_obj.rename(
            self.adapter_obj.get_full_path(dirname, basename),
            self.adapter_obj.get_full_path(dirname, self.new_folder_name),
            True
        )

        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['newName'] = self.new_folder_name
        data['newPath'] = dirname + '/' + self.new_folder_name + '/'
        data['renamed'] = 1 if rename_folder else 0
        return self._get_response(data)


class CreateFolderCommand(AbstractCommand):
    """
    创建子目录
    """

    requires = [
        Acl.FOLDER_CREATE,
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        self.new_folder_name = self.GET.get('newFolderName', None)
        self.new_folder_name = self.adapter_obj.get_new_folder_name(self.current_folder, self.new_folder_name, 0)

    def response(self) -> dict:
        # 验证目录名是否为隐藏目录
        if not self._is_not_hidden_folder(self.new_folder_name):
            raise Error('{folder_name}名称不被允许'.format(folder_name=self.new_folder_name))

        self.adapter_obj.create_folder(self.current_folder, self.new_folder_name)

        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['newFolder'] = self.new_folder_name
        return self._get_response(data)


class DeleteFolderCommand(AbstractCommand):
    """
    删除目录
    """

    requires = [
        Acl.FOLDER_DELETE
    ]

    def response(self) -> dict:
        delete_folder_result = self.adapter_obj.delete(self.adapter_obj.get_full_path(self.current_folder), True)
        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['deleted'] = 1 if delete_folder_result else 0
        return self._get_response(data)


class GetFilesCommand(AbstractCommand):
    """
    获取文件列表
    """

    requires = [
        Acl.FILE_VIEW
    ]

    def response(self) -> dict:
        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['files'] = [
            {
                "name": f,
                "date": self.adapter_obj.get_file_date(self.adapter_obj.get_full_path(self.current_folder, f)),
                "size": self.adapter_obj.get_file_size(self.adapter_obj.get_full_path(self.current_folder, f)),
            }
            for f in
            self.adapter_obj.get_files(self.current_folder)
            if
            self.adapter_obj.isfile(self.adapter_obj.get_full_path(self.current_folder, f))
            and self._is_not_hidden_file(f)
        ]
        return self._get_response(data)


class DeleteFilesCommand(AbstractCommand):
    """
    删除文件
    """

    requires = [
        Acl.FILE_DELETE
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        json_data = json.loads(self.POST.get('jsonData', '{}'))
        self.files = json_data.get('files', [])
        self.allowed_files = []

    def response(self) -> dict:

        for file in self.files:
            if file['type'] != self.resource_type:
                raise Error(
                    '删除{folder}{file}失败，不允许被操作'.format(
                        folder=file['folder'],
                        file=file['name'],
                    )
                )

            if not self._is_not_hidden_file(file['name']):
                raise Error(
                    '删除{folder}{file}失败，不允许被操作'.format(
                        folder=file['folder'],
                        file=file['name'],
                    )
                )

            if not self.acl.is_allowed(file['type'], file['folder'], self.acl.FILE_DELETE):
                raise AclError(
                    '删除{folder}{file}失败，权限不足'.format(
                        folder=file['folder'],
                        file=file['name'],
                    )
                )
            self.allowed_files.append(file)

        for file in self.allowed_files:
            self.adapter_obj.delete(self.adapter_obj.get_full_path(file['folder'], file['name']), False)
        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['deleted'] = 1
        return self._get_response(data)


class MoveFilesCommand(AbstractCommand):
    """
    移动文件
    """

    requires = [
        Acl.FILE_DELETE,
        Acl.FILE_RENAME,
        Acl.FILE_CREATE,
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        json_data = json.loads(self.POST.get('jsonData', '{}'))
        self.files = json_data.get('files', [])
        self.allowed_files = []

    def response(self) -> dict:
        for file in self.files:
            if file['type'] != self.resource_type:
                raise Error(
                    '移动{folder}{file}失败，不允许被操作'.format(
                        folder=file['folder'],
                        file=file['name'],
                    )
                )

            if not self._is_not_hidden_file(file['name']):
                raise Error(
                    '移动{folder}{file}失败，不允许被操作'.format(
                        folder=file['folder'],
                        file=file['name'],
                    )
                )
            if not self.acl.is_allowed(file['type'], file['folder'], self.acl.FILE_VIEW):
                raise AclError('移动{folder}{file}失败，权限不足'.format(
                    folder=file['folder'],
                    file=file['name'],
                ))
            self.allowed_files.append(file)

        moved = 0
        for file in self.allowed_files:
            _file_name, _file_extension = os.path.splitext(file['name'])
            _new_file_name = self.adapter_obj.get_new_file_name(
                self.current_folder,
                _file_name,
                _file_extension,
                0
            )
            if self.adapter_obj.move_file(file['folder'], file['name'], self.current_folder, _new_file_name):
                moved = moved + 1
        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['moved'] = moved
        return self._get_response(data)


class CopyFilesCommand(AbstractCommand):
    """
    复制文件
    """

    requires = [
        Acl.FILE_DELETE,
        Acl.FILE_RENAME,
        Acl.FILE_CREATE,
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        json_data = json.loads(self.POST.get('jsonData', '{}'))
        self.files = json_data.get('files', [])
        self.allowed_files = []

    def response(self) -> dict:
        for file in self.files:
            if file['type'] != self.resource_type:
                raise Error(
                    '复制{folder}{file}失败，不允许被操作'.format(
                        folder=file['folder'],
                        file=file['name'],
                    )
                )

            if not self._is_not_hidden_file(file['name']):
                raise Error(
                    '复制{folder}{file}失败，不允许被操作'.format(
                        folder=file['folder'],
                        file=file['name'],
                    )
                )
            if not self.acl.is_allowed(file['type'], file['folder'], self.acl.FILE_VIEW):
                raise AclError('复制{folder}{file}失败，权限不足'.format(
                    folder=file['folder'],
                    file=file['name'],
                ))
            self.allowed_files.append(file)

        copied = 0
        for file in self.allowed_files:
            _file_name, _file_extension = os.path.splitext(file['name'])
            _new_file_name = self.adapter_obj.get_new_file_name(
                self.current_folder,
                _file_name,
                _file_extension,
                0
            )
            if self.adapter_obj.copy_file(file['folder'], file['name'], self.current_folder, _new_file_name):
                copied = copied + 1
        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['copied'] = copied
        return self._get_response(data)


class FileUploadCommand(AbstractCommand):
    """
    上传文件
    """

    requires = [
        Acl.FILE_CREATE
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        self.file_obj = self.FILE['file']
        self.file_name = self.FILE['name']
        self._file_name, self._file_extension = os.path.splitext(self.file_name)
        self.new_file_name = self.adapter_obj.get_new_file_name(
            self.current_folder, self._file_name,
            self._file_extension,
            0
        )

    def response(self) -> dict:

        # 验证文件名是否为隐藏文件
        if not self._is_not_hidden_file(self.new_file_name):
            raise Error('{file_name}名称不被允许'.format(file_name=self.new_file_name))

        # 验证扩展名是否可用
        if not is_allowed_extension(
                self.new_file_name,
                self.resource_type_info['allowedExtensions'],
                self.resource_type_info['deniedExtensions'],
        ):
            raise Error('{file_name}扩展名不被允许'.format(file_name=self.new_file_name))

        upload_result = self.adapter_obj.file_upload(self.current_folder, self.new_file_name, self.file_obj)
        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['fileName'] = self.new_file_name
        data['uploaded'] = 1 if upload_result else 0
        return self._get_response(data)


class RenameFileCommand(AbstractCommand):
    """
    重命名文件
    """

    requires = [
        Acl.FILE_RENAME
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        self.new_file_name = self.GET.get('newFileName', '')

    def response(self) -> dict:

        # 验证源文件名是否为隐藏文件
        if not self._is_not_hidden_file(self.file_name):
            raise Error('{file_name}名称不被允许'.format(file_name=self.file_name))

        # 验证新文件名是否为隐藏文件
        if not self._is_not_hidden_file(self.new_file_name):
            raise Error('{file_name}名称不被允许'.format(file_name=self.new_file_name))

        # 验证新文件扩展名是否被允许
        if not is_allowed_extension(
                self.new_file_name,
                self.resource_type_info['allowedExtensions'],
                self.resource_type_info['deniedExtensions'],
        ):
            raise Error('{file_name}扩展名不被允许'.format(file_name=self.new_file_name))

        # 判断是否存在同名目录或文件
        if self.adapter_obj.has(self.adapter_obj.get_full_path(self.current_folder, self.new_file_name)):
            raise Error('{file_name}目录或文件名已存在'.format(file_name=self.new_file_name))

        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        rename_file = self.adapter_obj.rename(
            self.adapter_obj.get_full_path(self.current_folder, self.file_name),
            self.adapter_obj.get_full_path(self.current_folder, self.new_file_name),
            False
        )
        data['name'] = self.file_name
        data['newName'] = self.new_file_name
        data['renamed'] = 1 if rename_file else 0
        return self._get_response(data)


class DownloadFileCommand(AbstractCommand):
    """
    下载文件
    """

    requires = [
        Acl.FILE_VIEW
    ]

    def response(self) -> dict:
        # 验证源文件名是否为隐藏文件
        if not self._is_not_hidden_file(self.file_name):
            raise Error('{file_name}名称不被允许'.format(file_name=self.file_name))

        path = self.adapter_obj.get_full_path(self.current_folder, self.file_name)
        content_value = self.adapter_obj.read(path)
        response = self._get_response(content=content_value, content_type='application/octet-stream', headers={
            "Content-Disposition": 'attachment;filename="{file_name}"'.format(
                file_name=self.file_name.encode().decode('ISO-8859-1')
            )
        })
        return response


class GetFileUrlCommand(AbstractCommand):
    """
    获取缩略图文件完整URL
    """

    requires = [
        Acl.FILE_VIEW
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        self.thumbnail = self.GET.get('thumbnail', '')

    def response(self) -> dict:

        # 验证源文件名是否为隐藏文件
        if not self._is_not_hidden_file(self.file_name):
            raise Error('{file_name}名称不被允许'.format(file_name=self.file_name))

        # 验证缩略图文件名是否为隐藏文件
        if not self._is_not_hidden_file(self.thumbnail):
            raise Error('{file_name}名称不被允许'.format(file_name=self.thumbnail))

        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['url'] = build_url(
            self.url,
            self.current_folder,
            self.adapter_obj.THUMBS_NAME,
            self.file_name,
            self.thumbnail,
            right_index=False,
        )
        return self._get_response(data)


class ImageInfoCommand(AbstractCommand):
    """
    获取图片信息
    """

    requires = [
        Acl.FILE_VIEW
    ]

    def response(self) -> dict:
        # 验证源文件名是否为隐藏文件
        if not self._is_not_hidden_file(self.file_name):
            raise Error('{file_name}名称不被允许'.format(file_name=self.file_name))

        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        img_info = self.adapter_obj.image_info(self.current_folder, self.file_name)
        return self._get_response({**data, **img_info})


class GetResizedImagesCommand(AbstractCommand):
    """
    获取缩放的图片
    """

    requires = [
        Acl.FILE_VIEW
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        self.thumbs_folder = self.current_folder + self.adapter_obj.THUMBS_NAME + '/' + self.file_name + '/'

    def response(self) -> dict:
        # 验证源文件名是否为隐藏文件
        if not self._is_not_hidden_file(self.file_name):
            raise Error('{file_name}名称不被允许'.format(file_name=self.file_name))

        adapter_obj = self.adapter_obj
        thumbs_folder = self.thumbs_folder

        # 当前文件的缩略图目录不存在时进行创建
        if not adapter_obj.has(adapter_obj.get_full_path(thumbs_folder)):

            # 先判断缩略图目录是否存在，不存在则先创建缩略图目录
            if not adapter_obj.has(adapter_obj.get_full_path(self.current_folder, adapter_obj.THUMBS_NAME)):
                adapter_obj.create_folder(self.current_folder, adapter_obj.THUMBS_NAME)
            adapter_obj.create_folder(self.current_folder + adapter_obj.THUMBS_NAME, self.file_name)

        resized = adapter_obj.get_resized_images_data(
            [
                f for f in
                adapter_obj.get_files(thumbs_folder)
                if adapter_obj.isdir(adapter_obj.get_full_path(thumbs_folder))
            ],
            self.config['images']['sizes']
        )

        image_info = adapter_obj.image_info(self.current_folder, self.file_name)

        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)

        data['originalSize'] = "{width}x{height}".format(width=image_info['width'], height=image_info['height'])
        data['resized'] = resized
        return self._get_response(data)


class ImageResizeCommand(AbstractCommand):
    """
    缩放图片（修改图片尺寸）
    """

    requires = [
        Acl.FILE_VIEW,
        Acl.IMAGE_RESIZE,
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        self.file_size = self.GET.get('size', None)

    def response(self) -> dict:

        # 验证文件名是否为隐藏文件
        if not self._is_not_hidden_file(self.file_name):
            raise Error('{file_name}名称不被允许'.format(file_name=self.file_name))

        # 验证扩展名是否可用
        if not is_allowed_extension(
                self.file_name,
                self.resource_type_info['allowedExtensions'],
                self.resource_type_info['deniedExtensions'],
        ):
            raise Error('{file_name}扩展名不被允许'.format(file_name=self.file_name))

        if self.file_size:
            width, height = (int(i) for i in self.file_size.split('x', 1))
        else:
            width = height = None

        new_file_name = self.adapter_obj.image_resize(
            self.current_folder,
            self.file_name,
            width,
            height,
        )
        data = self._get_response_base_data(self.resource_type, self.current_folder, self.url)
        data['url'] = build_url(
            self.url,
            self.current_folder,
            self.adapter_obj.THUMBS_NAME,
            self.file_name,
            new_file_name
        )
        return self._get_response(data)


class ThumbnailCommand(AbstractCommand):
    """
    图片预览
    """

    requires = [
        Acl.FILE_VIEW
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        self.file_size = self.GET.get('size', None)

    def response(self) -> dict:
        if self.file_size:
            width, height = (int(i) for i in self.file_size.split('x', 1))
        else:
            width = height = None

        content_value, content_type, file_encoding = self.adapter_obj.thumbnail(
            self.current_folder,
            self.file_name,
            width,
            height
        )
        return self._get_response(content=content_value, content_type=content_type)


class ImagePreviewCommand(ThumbnailCommand):
    """
    图片预览
    """

    requires = [
        Acl.FILE_VIEW
    ]


class SaveImageCommand(AbstractCommand):
    """
    保存 base64 格式文件
    """

    requires = [
        Acl.FILE_CREATE
    ]

    def __init__(self, config: dict, resource_types: dict, acl: Acl, **kwargs):
        super().__init__(config, resource_types, acl, **kwargs)
        self.image_content = self._get_image_content()

    def _get_image_content(self, content=None):
        """
        获取post请求的base64图像
        :param content:
        :return:
        """
        pattern = re.compile(r'data:image/.*?;base64,(.*)', re.I)
        if not content:
            content = self.POST.get('content', '').strip()
        content = re.sub(pattern, r'\1', content)
        content = base64.b64decode(content)
        return content

    def response(self) -> dict:

        # 验证文件名是否为隐藏文件
        if not self._is_not_hidden_file(self.file_name):
            raise Error('{file_name}名称不被允许'.format(file_name=self.file_name))

        # 验证扩展名是否可用
        if not is_allowed_extension(
                self.file_name,
                self.resource_type_info['allowedExtensions'],
                self.resource_type_info['deniedExtensions'],
        ):
            raise Error('{file_name}扩展名不被允许'.format(file_name=self.file_name))

        if not self.image_content:
            raise Error('未获取到图像信息')

        path = self.adapter_obj.get_full_path(self.current_folder, self.file_name)
        bytes_io = io.BytesIO(self.image_content)
        self.adapter_obj.write(path, bytes_io)
        data = self._get_response_base_data(self.current_folder, self.current_folder, self.url)
        img_info = self.adapter_obj.image_info(self.current_folder, self.file_name)
        return self._get_response({**data, **img_info})


allowed_commands = {
    # 初始化
    "Init": InitCommand,

    # 目录操作
    'GetFolders': GetFoldersCommand,
    'RenameFolder': RenameFolderCommand,
    'CreateFolder': CreateFolderCommand,
    'DeleteFolder': DeleteFolderCommand,

    # 文件操作
    'GetFiles': GetFilesCommand,
    'DeleteFiles': DeleteFilesCommand,
    'MoveFiles': MoveFilesCommand,
    'CopyFiles': CopyFilesCommand,
    'FileUpload': FileUploadCommand,
    'RenameFile': RenameFileCommand,
    'DownloadFile': DownloadFileCommand,
    'GetFileUrl': GetFileUrlCommand,

    # 图片处理
    'ImageInfo': ImageInfoCommand,
    'GetResizedImages': GetResizedImagesCommand,
    'ImageResize': ImageResizeCommand,
    'Thumbnail': ThumbnailCommand,
    'ImagePreview': ImagePreviewCommand,
    'SaveImage': SaveImageCommand,
}
