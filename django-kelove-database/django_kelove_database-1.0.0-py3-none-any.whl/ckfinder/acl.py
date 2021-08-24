"""
acl.py 权限控制
By IT小强xqitw.cn <mail@xqitw.cn>
At 1/25/21 5:12 PM
"""

from abc import ABCMeta, abstractmethod

from .util import Dict, build_url


class RoleContextInterface:
    """
    角色处理接口
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_role(self) -> str:
        """
        获取当前用户角色
        :return:
        """


class MaskBuilder:
    """
    A class used to build access control masks for folder access management.
    Two masks are used to handle access rule inheritance from parent directories.
    """

    def __init__(self):
        self.mask_allowed = 0
        self.mask_disallowed = 0

    def allow(self, permission):
        self.mask_allowed |= permission
        return self

    def disallow(self, permission):
        self.mask_disallowed |= permission
        return self

    def merge_rules(self, input_mask):
        input_mask |= self.mask_allowed
        input_mask &= ~self.mask_disallowed
        return input_mask


class Acl:
    """
    Access Control
    """

    FOLDER_VIEW = 1
    FOLDER_CREATE = 2
    FOLDER_RENAME = 4
    FOLDER_DELETE = 8

    FILE_VIEW = 16
    FILE_CREATE = 32
    FILE_RENAME = 64
    FILE_DELETE = 128

    IMAGE_RESIZE = 256
    IMAGE_RESIZE_CUSTOM = 512

    FILE_UPLOAD = 32

    # 权限编码
    permissions = {
        'FOLDER_VIEW': FOLDER_VIEW,
        'FOLDER_CREATE': FOLDER_CREATE,
        'FOLDER_RENAME': FOLDER_RENAME,
        'FOLDER_DELETE': FOLDER_DELETE,

        'FILE_VIEW': FILE_VIEW,
        'FILE_CREATE': FILE_CREATE,
        'FILE_RENAME': FILE_RENAME,
        'FILE_DELETE': FILE_DELETE,

        'IMAGE_RESIZE': IMAGE_RESIZE,
        'IMAGE_RESIZE_CUSTOM': IMAGE_RESIZE_CUSTOM,

        'FILE_UPLOAD': FILE_UPLOAD,
    }

    def __init__(self, role_context=None):
        """
        初始化
        """
        self.role_context = role_context
        self.rules = Dict()
        self.cached_results = Dict()

    def set_rules(self, acl_config_nodes):
        for node in acl_config_nodes:
            role = node.get('role', '*')
            resource_type = node.get('resourceType', '*')
            folder = node.get('folder', '/')
            for permission_name, permission_value in self.permissions.items():
                allow = node.get(permission_name, None)
                if allow is not None:
                    allow = bool(allow)
                    if allow:
                        self.allow(resource_type, folder, permission_value, role)
                    else:
                        self.disallow(resource_type, folder, permission_value, role)

    def allow(self, resource_type, folder_path, permission, role):
        rule_mask = self._get_rule_mask(resource_type, folder_path, role)
        rule_mask.allow(permission)
        return self

    def disallow(self, resource_type, folder_path, permission, role):
        rule_mask = self._get_rule_mask(resource_type, folder_path, role)
        rule_mask.disallow(permission)
        return self

    def is_allowed(self, resource_type, folder_path, permission, role=None):
        mask = self.get_computed_mask(resource_type, folder_path, role)
        return (mask & permission) == permission

    def get_computed_mask(self, resource_type, folder_path: str, role=None):
        computed_mask = 0

        if not role and self.role_context:
            role = self.role_context.get_role()

        folder_path = folder_path.strip('/')

        cached_result = self.cached_results[resource_type][folder_path]
        if cached_result:
            return cached_result

        path_parts = folder_path.split('/')
        current_path = '/'
        path_parts_count = len(path_parts)

        for i in range(-1, path_parts_count):
            if i >= 0:
                if not path_parts[i]:
                    continue
                if self.rules.get(current_path + '*/', None):
                    computed_mask = self._merge_path_computed_mask(
                        computed_mask,
                        resource_type,
                        role,
                        current_path + '*/'
                    )
                current_path += path_parts[i] + '/'
            if self.rules.get(current_path, None):
                computed_mask = self._merge_path_computed_mask(computed_mask, resource_type, role, current_path)
        self.cached_results[resource_type][folder_path] = computed_mask
        return computed_mask

    def _get_rule_mask(self, resource_type, folder_path, role) -> MaskBuilder:
        folder_path = build_url(folder_path, left_index=True, right_index=True)

        if not isinstance(self.rules[folder_path][role][resource_type], MaskBuilder):
            self.rules[folder_path][role][resource_type] = MaskBuilder()
        rule_mask = self.rules[folder_path][role][resource_type]
        return rule_mask

    def _merge_path_computed_mask(self, current_mask, resource_type, role, folder_path):

        folder_rules = self.rules[folder_path]
        possible_rules = [
            ['*', '*'],
            ['*', resource_type],
            [role, '*'],
            [role, resource_type],
        ]

        for rule in possible_rules:
            _role = rule[0]
            _resource_type = rule[1]

            rule_mask = folder_rules[_role][_resource_type]
            if isinstance(rule_mask, MaskBuilder):
                current_mask = rule_mask.merge_rules(current_mask)
        return current_mask
