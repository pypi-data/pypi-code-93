"""A decorator to my private attributes read-only instance attributes"""
from functools import partial
from typing import Any


def get_private_attribute_name(name: str, ignore_private: bool = False) -> str:
    """Get a private attribute from public.
    If not ignore_private and the attribute is already private, raise ValueError."""
    if is_private_attribute(name):
        if not ignore_private:
            raise ValueError('The attribute {} is already private'.format(name))
        return name
    return '_{}'.format(name)


def is_private_attribute(name: str) -> bool:
    """Is this attribute private?"""
    return name.startswith('_')


def _get_property_value(name: str, self) -> Any:
    """Get the value of the given property turned private, to be used as partial"""
    return getattr(self, get_private_attribute_name(name))


def _get_meta_dq_tool_value(name: str, self) -> Any:
    """Get the value of the given priperty in ._meta_dq_tool"""
    return self._meta_dq_tool[name]  # pylint: disable=W0212


def add_read_only_auto_attributes(cls) -> 'cls':
    """Add read-only attributes for fields in cls._META_AUTO_FIELDS - only the public ones."""
    for field in cls._META_AUTO_FIELDS:  # pylint: disable=W0212
        if not is_private_attribute(field):
            setattr(cls, field, property(partial(_get_property_value, field)))
    return cls


def add_read_only_user_attributes(cls) -> 'cls':
    """Add read-only attributes for fields in cls._META_USER_FIELDS. Their value is in self._meta_dq_tool"""
    for field in cls._META_USER_FIELDS:  # pylint: disable=W0212
        setattr(cls, field, property(partial(_get_property_value, field)))
    return cls


def validate_meta_fields(
    meta_fields: dict,
    meta_user_fields: tuple,
    meta_auto_fields: tuple
):
    """Validate that the passed meta_fields are a subset of meta_user_fields or meta_auto_fields"""
    invalid_params = set(meta_fields.keys()) - set(meta_user_fields) - set(meta_auto_fields)
    if invalid_params:
        raise ValueError(
            "The following params are invalid: {}. The value user parameters are: {}".format(
                invalid_params,
                meta_user_fields
            )
        )
