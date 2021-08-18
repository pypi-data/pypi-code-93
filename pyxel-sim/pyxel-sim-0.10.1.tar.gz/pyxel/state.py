#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
import typing as t

__all__ = [
    "get_obj_att",
    "get_obj_by_type",
    "get_value",
    "get_state_ids",
    # "copy_processor",
    "copy_state",
    # "ConfigObjects",
]


# TODO: Remove this function ? See issue #230.
def get_obj_by_type(obj: t.Any, key: str, obj_type: t.Optional[t.Type] = None) -> t.Any:
    """Get the object associated with the class type following the key chain.

    :param obj:
    :param key:
    :param obj_type:
    :return:
    """
    obj, att = get_obj_att(obj, key, obj_type)
    if obj_type is not None:
        if isinstance(obj, obj_type):
            return obj


# TODO: Remove this function ? See issue #230.
def get_obj_att(
    obj: t.Any, key: str, obj_type: t.Optional[t.Type] = None
) -> t.Tuple[t.Any, str]:
    """Get the object associated with the key.

    Example::

        >>> obj = {"processor": {"pipeline": {"models": [1, 2, 3]}}}
        >>> om.get_obj_att(obj, "processor.pipeline.models")
        ({'models': [1, 2, 3]}, 'models')

    The above example works as well for a user-defined object with a attribute
    objects, i.e. configuration object model.

    :param obj:
    :param key:
    :param obj_type:
    :return: the object and attribute name tuple
    """
    *body, tail = key.split(".")
    for part in body:
        try:
            if isinstance(obj, dict):
                obj = obj[part]
            elif isinstance(obj, list):
                try:
                    index = int(part)
                    obj = obj[index]
                except ValueError:
                    for _, obj_i in enumerate(obj):
                        if hasattr(obj_i, part):
                            obj = getattr(obj_i, part)
                            break
                        elif obj_i.__class__.__name__ == part:
                            if hasattr(obj_i, tail):
                                obj = obj_i
                                break
            elif hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise NotImplementedError(
                    f"obj={obj!r}, key={key!r}, obj_type={obj_type!r}, part={part!r}"
                )

            if obj_type and isinstance(obj, obj_type):
                return obj, tail

        except AttributeError:
            # logging.error('Cannot find attribute %r in key %r', part, key)
            obj = None
            break
    return obj, tail


#  t.Any) -> t.Union[t.List[t.Any], t.Dict[str, t.Any]]:
# def get_state_dict(obj):
#     """Recursively re-create the configuration object model as a dictionary tree.
#
#     This routine aids in create a JSON compatible dictionary.
#
#     The dictionary object returned is a deep copy of the original object.
#     """
#     def get_state_helper(val):
#         """TBW."""
#         if hasattr(val, 'get_state_json'):  # TODO: PYXEL specific
#             return val.get_state_json()
#         elif hasattr(val, '__getstate__'):
#             return val.__getstate__()
#         else:
#             return val
#
#     result = {}
#     if isinstance(obj, dict):
#         for key, value in obj.items():
#             result[key] = get_state_dict(value)
#     elif isinstance(obj, list):
#         result = []
#         for value in obj:
#             result.append(get_state_dict(value))
#     else:
#         if not hasattr(obj, '__getstate__'):
#             return result
#         for key, value in obj.__getstate__().items():
#             if isinstance(value, list):
#                 result[key] = [get_state_helper(val) for val in value]
#
#             elif isinstance(value, dict):
#                 result[key] = {key2: get_state_helper(val) for key2, val in value.items()}
#
#             else:
#                 result[key] = get_state_helper(value)
#     return result


# TODO: Remove this function ? See issue #230.
def get_state(obj: t.Any) -> t.Mapping[str, t.Any]:
    """Convert the config object to a embedded dict object.

    The returned value will be a dictionary tree that is JSON
    compatible. Only dict, list, str, numbers will be contained
    in the returned dictionary.

    :param obj: a top level dict object or a object that defines
        the __getstate__ method.

    :return: the dictionary representation of the passed object.
    """
    result = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            result[key] = value.__getstate__()

    elif hasattr(obj, "__getstate__"):
        result = obj.__getstate__()

    return result


# TODO: Remove this function ? See issue #230.
def get_state_ids(
    obj: t.Any,
    parent_key_list: t.Optional[t.Sequence[str]] = None,
    result: t.Optional[t.Dict[str, t.Any]] = None,
) -> t.Any:
    """Retrieve a flat dictionary of the object attribute hierarchy.

    The dot-format is used as the key representation.

    :param obj:
    :param parent_key_list:
    :param result:
    :return:
    """
    if result is None:
        from collections import OrderedDict

        result = OrderedDict()

    if parent_key_list is None:
        parent_key_list = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (str, int, float)):
                key = ".".join(parent_key_list) + "." + key
                result[key] = value
            else:
                list(parent_key_list) + [key]
                get_state_ids(value, list(parent_key_list) + [key], result)

    elif isinstance(obj, list):
        is_primitive = all([isinstance(value, (str, int, float)) for value in obj])
        if is_primitive:
            key = ".".join(parent_key_list)
            result[key] = obj
        else:
            for i, value in enumerate(obj):
                get_state_ids(value, list(parent_key_list) + [str(i)], result)
    return result


# TODO: Remove this function ? See issue #230.
def get_value(obj: t.Any, key: str) -> t.Any:
    """Retrieve the attribute value of the object given the attribute dot formatted key chain.

    Example::

        >>> obj = {"processor": {"pipeline": {"models": [1, 2, 3]}}}
        >>> om.get_value(obj, "processor.pipeline.models")
        [1, 2, 3]

    The above example works as well for a user-defined object with a attribute
    objects, i.e. configuration object model.

    :param obj:
    :param key:
    :return:
    """
    obj, att = get_obj_att(obj, key)

    if isinstance(obj, dict) and att in obj:
        value = obj[att]
    else:
        value = getattr(obj, att)

    return value


# TODO: Remove this function ? See issue #230.
def copy_state(obj: t.Any) -> t.Mapping[str, t.Any]:
    """Deep copy the object as a attribute name/value pairs dictionary.

    :param obj:
    :return:
    """
    kwargs = {}
    for key, _ in obj.__getstate__().items():
        obj_att = getattr(obj, key)
        if obj_att is None:
            cpy_obj = None
        elif hasattr(
            obj_att, "copy"
        ):  # TODO: PYXEL specific: this should be replaced with __copy__
            cpy_obj = obj_att.copy()
        else:
            cpy_obj = type(obj_att)(obj_att)
        kwargs[key] = cpy_obj
    # kwargs = {key: getattr(obj, key).copy() if value else None for key, value in obj.__getstate__().items()}
    return kwargs


# # TODO: Is it still used ?
# def copy_processor(
#     obj: t.Any,
# ) -> t.Any:  # TODO: PYXEL specific: to be renamed to copy_object
#     """Create a deep copy of the object.
#
#     :param obj:
#     :return:
#     """
#     cls = type(obj)
#     if hasattr(obj, "__getstate__"):
#         cpy_kwargs = {}
#         for key, value in obj.__getstate__().items():
#             cpy_kwargs[key] = copy_processor(value)
#         obj = cls(**cpy_kwargs)
#
#     elif isinstance(obj, dict):
#         cpy_obj = cls()
#         for key, value in obj.items():
#             cpy_obj[key] = copy_processor(value)
#         obj = cpy_obj
#
#     elif isinstance(obj, list):
#         cpy_obj = cls()
#         for value in obj:
#             cpy_obj.append(copy_processor(value))
#         obj = cpy_obj
#
#     return obj

#
# class ConfigObjects:
#     """A list of Config objects that can be de-referenced using unique 'class.attribute' keys."""
#
#     def __init__(self, configs: t.Optional[t.List[t.Any]] = None) -> None:
#         """TBW.
#
#         :param configs:
#         """
#         self._configs = []  # type: t.List[t.Any]
#         self.enabled = True
#         self.log = logging.getLogger(__name__)
#         if configs:
#             self._configs.extend(configs)
#
#     def get(self, key: str) -> t.Any:
#         """Object-model getter."""
#         obj, att = get_obj_att(self, key)
#         if not hasattr(obj, "_" + att):
#             raise ValueError("Only properties may be get. att: %r" % att)
#
#         if self.enabled:
#             name = att
#         else:
#             name = "_" + att
#
#         value = None
#         try:
#             value = getattr(obj, name)
#         finally:
#             self.log.info("key: %s, name: %s, value: %r", key, name, value)
#         return value
#
#     def set(self, key: str, value: t.Any) -> None:
#         """Object-model setter."""
#         obj, att = get_obj_att(self, key)
#         if not hasattr(obj, "_" + att):
#             raise ValueError("Only properties may be set. att: %r" % att)
#
#         if self.enabled:
#             name = att
#         else:
#             name = "_" + att
#
#         try:
#             setattr(obj, name, value)
#         finally:
#             self.log.info("key: %s, name: %s, value: %r", key, name, value)
#
#     # def wait(self, key):
#     #     """Object-model wait until operation is finished."""
#     #     obj, att = om.get_obj_att(self, key)
#     #     if hasattr(obj, 'wait'):
#     #         getattr(obj, 'wait')()
#     #
#     # def call_action(self, key):
#     #     """TBW."""
#     #     args = []
#     #     obj, att = om.get_obj_att(self, key)
#     #     action_handler = om.get_meta_data_value(obj, att, 'on_action')
#     #     if callable(action_handler):
#     #         func = action_handler
#     #         args = [obj]
#     #     elif isinstance(action_handler, str):
#     #         func = getattr(obj, action_handler)
#     #     else:
#     #         msg = '%s: invalid action_handler' % key
#     #         self.log.error(msg)
#     #         # signals.progress(key, {'value': 'error: %s' % msg, 'state': -1})
#     #         return
#     #
#     #     func(*args)
#
#     def append(self, config) -> None:
#         """TBW."""
#         self._configs.append(config)
#
#     def __len__(self) -> int:
#         """Retrieve the number of config objects."""
#         return len(self._configs)
#
#     def __iter__(self) -> t.Iterator:
#         """Retrieve the iterator for the config objects."""
#         return iter(self._configs)
#
#     def __getstate__(self) -> t.Dict[str, t.Any]:
#         """TBW."""
#         result = {}
#         for config in self._configs:
#             result[config.__class__.__name__] = config
#         return result
#
#     def __contains__(self, item: str) -> t.Any:
#         """Test if item id is contained in one of the Config objects."""
#         try:
#             getattr(self, item)
#             return True
#         except AttributeError:
#             return False
#
#     def __getitem__(self, item: str) -> t.Any:
#         """Enable the retrieval of the Config object by class name."""
#         return getattr(self, item)
#
#     def __getattr__(self, item: str) -> t.Any:
#         """Enable the retrieval of the Config object by class name."""
#         for config in self._configs:
#             if config.__class__.__name__ == item:
#                 return config
#         raise AttributeError(
#             "AttributeError: unknown %r attribute in ConfigObject" % item
#         )
