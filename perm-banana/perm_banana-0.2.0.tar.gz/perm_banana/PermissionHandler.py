from typing import Dict, Union
from copy import deepcopy

from .Permission import Permission


class PermissionHandler:
    """Finds the given permissions of a user and contains them for their respective"""

    def __init__(self, permission: Permission, children: Dict[int, "PermissionHandler"] = None):
        self.permission = permission
        self.children = {} if children is None else children

    @property
    def permissions(self) -> Dict[int, Union["PermissionHandler", Permission]]:
        """Finds all valid permission of itself and its children"""
        return {0: self.permission, **self.children}

    def __repr__(self) -> str:
        if len(self.children):
            return f"{self.__class__.__name__}({self.permission}, children={self.children})"
        else:
            return f"{self.__class__.__name__}({self.permission})"

    def __bool__(self) -> bool:
        for permission in self.permissions.values():
            if permission:
                return True
        return False

    def __invert__(self):
        permission = ~self.permission
        children = {}

        for key, child in self.children.items():
            children[key] = ~child

        return PermissionHandler(permission, children)

    def __and__(self, other):
        children_keys = set(self.children.keys()).intersection(other.children.keys())

        return PermissionHandler(
            self.permission & other.permission,
            {key: self.children[key] & other.children[key] for key in children_keys},
        )

    def __iand__(self, other):
        children_keys = set(self.children.keys()).intersection(other.children.keys())

        # If a key is only present on the left side, delete it
        only_left_keys = set(self.children.keys()).difference(children_keys)
        for key in only_left_keys:
            del self.children[key]

        self.permission &= other.permission
        for key in children_keys:
            self.children[key] &= other.children[key]

        return self

    def __or__(self, other):
        children = {}
        both = {*self.children.keys(), *other.children.keys()}
        for key in both:
            if key in self.children and key in other.children:
                children.update({key: self.children[key] | other.children[key]})
            elif key in self.children:
                children.update({key: self.children[key]})
            else:
                children.update({key: other.children[key]})

        return PermissionHandler(self.permission | other.permission, children)

    def __ior__(self, other):
        self.permission |= other.permission
        both = {*self.children.keys(), *other.children.keys()}
        for key in both:
            if key in self.children and key in other.children:
                self.children.update({key: self.children[key] | other.children[key]})
            elif key in self.children:
                self.children.update({key: self.children[key]})
            else:
                self.children.update({key: other.children[key]})
        return self

    def __add__(self, other):
        return self | other

    def __iadd__(self, other):
        self |= other
        return self

    def __sub__(self, other):
        res = self & ~other

        # If nothing is inside other, then it gets added by default
        # Because this is a copy, the permissions must be deep copied
        children_keys = set(self.children.keys()).intersection(other.children.keys())
        only_left_keys = set(self.children.keys()).difference(children_keys)

        for key in only_left_keys:
            res.children[key] = deepcopy(self.children[key])

        return res

    def __isub__(self, other):
        # If nothing is inside other, then it gets added by default
        children_keys = set(self.children.keys()).intersection(other.children.keys())
        only_left_keys = set(self.children.keys()).difference(children_keys)
        left_dict = {key: self.children[key] for key in only_left_keys}

        self &= ~other
        for key, value in left_dict.items():
            self.children[key] = value

        return self

    def __eq__(self, other):
        if not self.permission == other.permission:
            return False
        if set(self.children.keys()) != set(other.children.keys()):
            return False
        for key in self.children.keys():
            if key not in other.children or self.children[key] != other.children[key]:
                return False
        return True

    def __ne__(self, other):
        return not self == other
