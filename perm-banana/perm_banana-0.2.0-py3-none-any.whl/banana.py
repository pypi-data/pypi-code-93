from typing import Type, Optional

from .PermissionHandler import PermissionHandler
from .Permission import Permission
from .Check import Check, Perm


def get_check(cls, name) -> Optional[Check]:
    """
    Gets the class variables and converts them to a check if they are not already.
    """
    default = getattr(cls, name, None)
    if isinstance(default, Check):
        check = default
    elif isinstance(default, int):
        check = Check.from_int(permission=default)
    else:
        return None
    return check


def validate_checks(klass: Type[Perm], *args: Check) -> bool:
    """
    Determines if a series of checks are inside a given Permission or Handler.
    """
    for check in args:
        if check not in getattr(klass, "__checks", {}):
            return False
    return True


def from_checks(klass: Type[Perm]):
    def from_checks_permission(cls: Type[Permission], *args: Check) -> Permission:
        """
        Generates a permission from a series of checks.
        """
        permission = cls(0)
        for check in args:
            permission += check.permission
        return permission

    def from_check_handler(cls: Type[PermissionHandler], *args: Check) -> PermissionHandler:
        """
        Generate a permission handler from a series of checks.
        """
        handler = cls(Permission(0))
        for check in args:
            handler += check.permission
        return handler

    for base in klass.__bases__:
        if base is Permission:
            return from_checks_permission
        else:
            return from_check_handler


def banana(cls):
    """
    A decorator for a class that adds the ability to create Permissions and Handlers
    from their Checks.
    """
    cls.__checks = set()

    # Basically tell checks that we are the class, not a medium to pass things through
    cls.__banana = True

    cls_annotations = cls.__dict__.get("__annotations__", {})
    for name in cls_annotations.keys():
        check = get_check(cls, name)
        if check is None:
            continue
        cls.__checks.add(name)
        setattr(cls, name, check)

    for base in cls.__bases__:
        if base is Permission or PermissionHandler:
            setattr(cls, "from_checks", classmethod(from_checks(cls)))
            break

    return cls
