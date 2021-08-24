"""
ckfinder.py Ckfinder for Python
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/25/21 5:16 PM
"""

import hashlib

from .acl import Acl
from .commands import allowed_commands, AbstractCommand
from .exception import AclError, Error
from .response import Response
from .util import load_object


class License:
    """
    Ckfinder License
    """
    CKFINDER_CHARS = '123456789ABCDEFGHJKLMNPQRSTUVWXYZ'

    def __init__(self, ckfinder_license_key: str = '', ckfinder_license_name: str = ''):
        """
        初始化
        :param ckfinder_license_key:
        :param ckfinder_license_name:
        """

        self.ckfinder_license_key = ckfinder_license_key
        self.ckfinder_license_name = ckfinder_license_name

    def create_license(self):
        """
        生成 license
        :return:
        """
        ln = ''
        lc = ''
        try:
            lc = self.ckfinder_license_key.replace('-', '')
            pos = self.CKFINDER_CHARS.find(lc[2]) % 5
            if pos == 1 or pos == 2:
                ln = self.ckfinder_license_name
            lc: str = (
                    '' + lc[1] + lc[8] + lc[17] + lc[22] + lc[3] + lc[13] + lc[11] + lc[20] + lc[5] + lc[24] + lc[27]
            ).strip()
        except IndexError:
            pass
        finally:
            return {'s': ln, 'c': lc}


class Config:
    """
    配置管理
    """

    def __init__(self, **config) -> None:
        """
        初始化
        :param config:
        """

        self._config_images = {
            "max": "20000x20000",
            "sizes": {
                "small": "480x320",
                "medium": "600x480",
                "large": "800x600"
            }
        }

        self._config_thumbs = ["150x150", "300x300", "500x500"]

        self._config = {
            "enabled": True,
            "images": self._config_images,
            "thumbs": self._config_thumbs,
            "uploadMaxSize": 52428800,
            "uploadCheckImages": False,
            'hideFolders': [r'\..*?', 'CVS', '__thumbs'],
            'hideFiles': [r'\..*?'],
        }
        self._config = {
            **self._config,
            **config,
            **(License(
                ckfinder_license_key=config.get('license_key', ''),
                ckfinder_license_name=config.get('license_name', ''),
            ).create_license())
        }

    def set(self, **config) -> None:
        """
        设置配置
        :param config:
        :return:
        """
        self._config.update(config)

    def get(self, *args, **kwargs):
        """
        获取配置
        :param args:
        :param kwargs:
        :return:
        """

        kwargs = {**{arg: None for arg in args}, **kwargs}
        config_len = len(kwargs)

        if config_len == 0:
            return self._config
        elif config_len == 1:
            return self._config.get(
                list(kwargs.keys())[0],
                list(kwargs.values())[0]
            )
        else:
            data = {}
            for key, val in kwargs.items():
                data[key] = self._config.get(key, val)
            return data


class Ckfinder:
    """
    Ckfinder 入口
    """

    def __init__(self, get: dict, post: dict = None, file: dict = None, config: dict = None, **kwargs):
        """
        初始化
        """

        self.GET = get
        self.POST = post if post else {}
        self.FILE = file if file else {}
        self.resource_types: dict = kwargs.get('resource_types', {})
        self.rules = kwargs.get('rules', [])
        self.role_context = None
        self.config = Config(**(config if config else {})).get()
        self.commands = {**allowed_commands, **kwargs.get('commands', {})}

    def add_resource(self, adapter, name: str, path: str = '', url: str = '/', **kwargs):
        """
        添加资源目录
        :param adapter:
        :param name:
        :param path:
        :param url:
        :param kwargs:
        :return:
        """
        resource_type_info = {
            "adapter": adapter,
            "name": name,
            "allowedExtensions": [],
            "deniedExtensions": [],
            "hash": str(hashlib.sha1(name.encode()).hexdigest()),
            "acl": 0,
            "maxSize": self.config.get('uploadMaxSize', 52428800),
            "hasChildren": True,
            "url": url,
            "path": path,
        }
        resource_type_info = {**resource_type_info, **kwargs}
        self.resource_types[name] = resource_type_info
        return self

    def add_rule(self, rule: dict):
        """
        添加权限规则
        :param rule:
        {
            "role": "*",
            "resourceType": "*",
            "folder": "/",
            'FOLDER_VIEW': True,
            'FOLDER_CREATE': True,
            'FOLDER_RENAME': True,
            'FOLDER_DELETE': True,
            'FILE_VIEW': True,
            'FILE_CREATE': True,
            'FILE_RENAME': True,
            'FILE_DELETE': True,
            'IMAGE_RESIZE': True,
            'IMAGE_RESIZE_CUSTOM': True,
        }
        :return:
        """
        self.rules.append(rule)
        return self

    def run(self, role_context=None):
        """
        执行命令
        :param role_context: 角色处理类实体，角色处理类需要继承 AbstractRoleContext
        :return:
        """

        acl = Acl(role_context=role_context)
        acl.set_rules(self.rules)

        self.resource_types = {
            k: {
                **v,
                **{
                    "adapter_obj": (load_object(v['adapter']) if isinstance(v['adapter'], str) else v['adapter'])(
                        config=self.config,
                        resource_type_info=v,
                        acl=acl,
                    ),
                    "acl": acl.get_computed_mask(k, '/'),
                    "hasChildren": True,
                }
            }
            for k, v in self.resource_types.items()
            if acl.is_allowed(resource_type=k, folder_path='/', permission=acl.FOLDER_VIEW)
        }

        command_class = self.commands.get(self.GET.get('command', ''), None)

        try:
            command_object: AbstractCommand = command_class(
                config=self.config,
                resource_types=self.resource_types,
                acl=acl,
                get=self.GET,
                post=self.POST,
                file=self.FILE,
            )

            return command_object.response()
        except AclError as result:
            return Response.acl_error(str(result))
        except Error as result:
            return Response.error(str(result))
