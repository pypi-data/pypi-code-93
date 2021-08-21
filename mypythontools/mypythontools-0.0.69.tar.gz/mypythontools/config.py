"""This is not module that configure library mypythontools, but module that help create config for your project.

What
====

1) Simple and short syntax.
2) Ability to have docstrings on variables (not dynamically, so visible in IDE) and good for sphinx docs.
3) Type checking, one-of-options checking.
4) Also function evaluation from other config values (not only static value stored).
5) Options hierarchy (nested options).

How
===

Boosted property with simplified implementation. To be able to provide docstrings in IDE, first function is created.

Examples:
=========

>>> class SimpleConfig(ConfigBase):
...     @MyProperty(int)  # Use tuple like (str, int, bool) if more classes.
...     def var() -> int:  # This is for type hints in IDE.
...         '''
...         Type:
...             int
...
...         Default:
...             123
...
...         This is docstrings (also visible in IDE, because not defined dynamically).'''
...
...         return 123  # This is initial value that can be edited.
...
...     @MyProperty()  # Even if you don't need any params, use empty brackets
...     def evaluated(self) -> int:
...         return self.var + 1
...
>>> config = SimpleConfig()
>>> config.var
123
>>> config.var = 665
>>> config.var
665
>>> config['var']  # You can also access params as in a dictionary
665
>>> config.evaluated
666
>>> config.var = "String is problem"
Traceback (most recent call last):
TypeError: ...

This is how help looks like in VS Code

.. image:: /_static/intellisense.png
    :width: 620
    :alt: tasks
    :align: center

You can also use options checker validation.

>>> class SimpleConfig(ConfigBase):
...     @MyProperty(options=[1, 2, 3])
...     def var(self) -> int:
...         2  # This means that value will not be set on init
...
>>> config = SimpleConfig()
>>> config.var = 4
Traceback (most recent call last):
KeyError: ...

You can also edit getter or setter. You can use lambda function (if more logic,
it's better to use normal property and add type checking manually).

Use setattr and name with underscore as prefix or self.private_name self means property, not config object.

>>> class SimpleConfig(ConfigBase):
...     @MyProperty(
...         int,
...         fset=lambda self, object, new: (
...             print("I'm listener, i can call any function on change."),
...             setattr(object, self.private_name, new + 1),
...         ),
...     )
...     def with_setter() -> int:
...         return 1
...
>>> config = SimpleConfig()
>>> config.with_setter
1
>>> config.with_setter = 665
I'm listener, i can call any function on change.
>>> config.with_setter
666

Hierarchical config
-------------------

If last level, do inherit from ConfigBase, else inherit from ConfigStructured

Note:
    Use unique values for all config variables even if they are in various subconfig.

>>> class Config(ConfigStructured):
...     def __init__(self) -> None:
...         self.subconfig1 = self.SubConfiguration1()
...         self.subconfig2 = self.SubConfiguration2()
...
...     class SubConfiguration1(ConfigStructured):
...         def __init__(self) -> None:
...             self.subsubconfig = self.SubSubConfiguration()
...
...         class SubSubConfiguration(ConfigBase):
...             @MyProperty(options=[0, 1, 2, 3])
...             def value1() -> int:
...                 '''Documentation here
...
...                 Options: [0, 1, 2, 3]
...                 '''
...                 return 3
...
...             @MyProperty()
...             def value2(self):
...                 return self.value1 + 1
...
...     class SubConfiguration2(ConfigBase):
...         @MyProperty()
...         def other_val(self):
...             return self.value2 + 1
...
...     # Also subconfig category can contain values itself
...     @MyProperty(options=[0, 1, 2, 3])
...     def value3() -> int:
...         return 3
...
>>> config = Config()
...
>>> config.subconfig1.subsubconfig.value2
4

You can access value from config as well as from subcategory

>>> config.value2
4

Copy
----

Sometimes you need more instances of settings and you need copy of existing configuration. Copy is deepcopy by default.

>>> config2 = config.copy()
>>> config2.value3 = 0
>>> config2.value3
0
>>> config.value3
3

Bulk update
-----------

Sometimes you want to update many values with flat dictionary.

>>> config.update({'value3': 2, 'value1': 0})
>>> config.value3
2

Get flat dictionary
-------------------

There is a function that will export all the values to the flat dictionary (no dynamic anymore, just values).

>>> config.get_dict()
{'value3': 2, 'value1': 0, 'value2': 1, 'other_val': 2}

Reset
-----
You can reset to default values

>>> config.value1 = 1
>>> config.reset()
>>> config.value1
3

Sphinx docs
===========

If you want to have documentation via sphinx, you can add this to conf.py::

    napoleon_custom_sections = [
        ("Types", "returns_style"),
        ("Type", "returns_style"),
        ("Options", "returns_style"),
        ("Default", "returns_style"),
        ("Example", "returns_style"),
        ("Examples", "returns_style"),
    ]

Here is example

.. image:: /_static/config_on_sphinx.png
    :width: 620
    :alt: tasks
    :align: center
"""

from typing import Any
import mylogging
from copy import deepcopy

from .property import MyProperty


class ConfigMeta(type):
    """Metaclass that will edit Config class. Main reason is for being able to define own __init__ but
    still has functionality from parent __init__ that is necessary. With this meta, there is no need
    to use super().__init__ by user.

    As user, you probably will not need it. It's used internaly if inheriting from ConfigStructured."""

    def __init__(cls, name, bases, dct):

        # Avoid base classes here and wrap only user class init
        if name not in ["ConfigBase", "ConfigStructured"]:

            def add_parent__init__(self, dict_values=None, frozen=None, *a, **kw):
                is_structured = True if ConfigStructured in bases else False

                self._base_config_map = {}
                self.myproperties_list = []
                self.properties_list = []

                # Call user defined init
                cls._original__init__(self, *a, **kw)

                # Init all MyProperty values
                for i, j in vars(type(self)).items():
                    if type(j) is MyProperty:
                        self.myproperties_list.append(j.public_name)
                        setattr(self, j.private_name, j.init_function)
                    if type(j) is property:
                        self.properties_list.append(i)

                # If structured config, add proxies to subconfigs
                if is_structured:
                    self._propagate_base_config_map()

                # Update values from dict param in init
                if dict_values:
                    for i, j in dict_values.items():
                        setattr(self, i, j)

                if frozen is None:
                    self.frozen = True
                else:
                    self.frozen = frozen

            cls._original__init__ = cls.__init__
            cls.__init__ = add_parent__init__


class ConfigBase(metaclass=ConfigMeta):
    """Main config class. If need nested config, use ConfigStructured instead.
    You can find working examples in module docstrings."""

    # Usually this config is created from someone else that user using this config. Therefore new attributes
    # should not be created. It is possible to force it (raise error). It is possible to set frozen to False
    # to enable creating new instances.
    frozen = False

    # _base_config_map is used only if using structured config. You can access attribute from subconfig as
    # well as from main config object, there is proxy mapping config dict (same for base and subconfig) if
    # attribute not found on defined object, it will find if it's in this dict where are all config values as
    # key and config object where it's stored. It's poppulated automatically in metaclass during init
    _base_config_map = {}

    def __init__(self, *args, **kwargs) -> None:
        """Init is wrapped in metaclass so __init__ can be overriden by user

        Note:
            You don't need to use parameters from wrapper in your init (but you can use it on instance).
        Args in wrapper:
            dict_values (dict, optional): Values that will updated after init. Defaults to None.
            frozen (bool, optional): If frozen, it's not possible to add new attributes. Defaults to None.
        """
        pass

    def __getattr__(self, name: str):
        try:
            # If structured config. Value may not be in this object, but in another related object.
            return getattr(self._base_config_map[name], name)

        except Exception:
            raise AttributeError(mylogging.return_str(f"Variable {name} not found in config."))

    def __setattr__(self, name: str, value: Any) -> None:
        setter_name = name[1:] if name.startswith("_") else name

        if (
            not self.frozen
            or name == "frozen"
            or name in [*self.myproperties_list, *self.properties_list, *vars(self)]
        ):
            object.__setattr__(self, name, value)

        elif setter_name in self._base_config_map.keys():
            setattr(self._base_config_map[setter_name], name, value)

        else:
            raise AttributeError(
                mylogging.return_str(
                    f"Object {str(self)} is frozen. New attributes cannot be set and attribute < {name} > not found. Maybe you misspelled name. "
                    "If you really need to change the value, set attribute frozen to false."
                )
            )

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def copy(self):
        return deepcopy(self)

    def update(self, dict):

        for i, j in dict.items():
            setattr(self, i, j)

    def reset(self):
        copy = type(self)()

        for i in vars(copy).keys():
            setattr(self, i, copy[i])

        for i in copy.myproperties_list:
            setattr(self, i, copy[i])

        for i in copy.properties_list:
            setattr(self, i, copy[i])

    def get_dict(self):
        normal_vars = {
            key: value
            for key, value in vars(self).items()
            if not key.startswith("__")
            and not callable(value)
            and not hasattr(value, "myproperties_list")
            and key not in ["myproperties_list", "properties_list", "frozen", "_base_config_map"]
        }

        property_vars = {
            # Values from myproperties
            **{key: getattr(self, key) for key in self.myproperties_list},
            # Values from properties
            **{key: getattr(self, key) for key in self.properties_list},
        }

        normal_vars = {
            i: j for i, j in normal_vars.items() if not (i.startswith("_") and i[1:] in property_vars)
        }

        return {**normal_vars, **property_vars}


class ConfigStructured(ConfigBase):
    """Class for creating config. Read why and how in config module docstrings."""

    def __init__(self, dict_values=None, frozen=None) -> None:
        """Init is redefined in metaclass so __init__ can be overriden by user

        Args:
            dict_values (dict, optional): Values that will updated after init. Defaults to None.
            frozen (bool, optional): If frozen, it's not possible to add new attributes. Defaults to None.
        """
        pass

    def get_dict(self):
        # From main class
        dict_of_values = super().get_dict()
        # From sub configs
        for i in vars(self).values():
            if hasattr(i, "myproperties_list"):
                subconfig_dict = i.get_dict()
                dict_of_values.update(subconfig_dict)

        return dict_of_values

    def _propagate_base_config_map(self):

        for i in vars(self).values():
            if hasattr(i, "myproperties_list"):
                for j in i.myproperties_list:
                    self._base_config_map[j] = i

            elif hasattr(i, "properties_list"):
                for j in i.properties_list:
                    self._base_config_map[j] = i

            if isinstance(i, ConfigBase):
                i._base_config_map = self._base_config_map

            if ConfigStructured in type(i).mro():
                i._propagate_base_config_map()
