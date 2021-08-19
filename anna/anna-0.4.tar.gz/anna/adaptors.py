# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

"""
This module provides adaptor classes for connecting to various configuration sources (e.g. files).
"""

import abc
import collections
import json
import logging
import os
import re
import six
import xml.dom.minidom
import xml.etree.ElementTree
import xml.dom.minidom

from anna.utils import to_json_string, use_docs_from
from anna.exceptions import InvalidPathError


class ConfigurationAdaptor(six.with_metaclass(abc.ABCMeta, object)):
    """
    (Abstract) Base class for configuration adaptors.

    A configuration adaptor connects to a configuration source (e.g. a file,
    database, ...) and retrieves configuration elements from it.
    The specifications of parameter values are internally represented as
    (configuration) :class:`~ConfigurationAdaptor.Element`s. They hold
    the all the information a parameter needs in order to satisfy its declaration.
    """

    PATH_DELIMITER = '/'

    @six.python_2_unicode_compatible
    class Element(object):
        """
        A configuration element represents a parameter specification.
        A specification consists of a text representation and optional meta data
        in form of a dict. The following attributes are available:

        * `name`, the parameter name
        * `text`, the parameter's text representation
        * `meta`, optional meta data
        """
        def __init__(self, name, text=None, meta=None):
            """
            Parameters
            ----------
            name : unicode
            text : unicode, optional
            meta : dict, optional
            """
            self.name = name
            if text is not None and not isinstance(text, six.text_type):
                raise TypeError(
                    'Text must be unicode (got %s instead)' % type(text)
                )
            if meta is not None and not isinstance(meta, dict):
                raise TypeError(
                    'Meta must be dict (got %s instead)' % type(meta)
                )
            self.text = text.strip() if isinstance(text, six.text_type) else ''
            self.meta = meta if meta is not None else {}

        def __repr__(self):
            return '{0}({1}, {2}, {3})'.format(
                self.__class__.__name__,
                self.name, self.text,
                self.meta
            )

        def __str__(self):
            return to_json_string(dict(name=self.name, text=self.text, meta=self.meta))

    def __init__(self):
        super(ConfigurationAdaptor, self).__init__()

    def get_meta(self, path):
        """
        Retrieve the meta data for an element.

        Parameters
        ----------
        path : unicode
            The path pointing to the element that shall be retrieved.

        Returns
        -------
        meta_data : dict

        Raises
        ------
        InvalidPathError
            If the specified path does not point to an element.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax.
        :method:`~ConfigurationAdaptor.get_element` : Retrieve a configuration element.

        Examples
        --------
        >>> config = JSONAdaptor()
        >>> config.insert_element('A', JSONAdaptor.Element('A', meta={'a': 1}))
        >>> config.insert_element('A/B', JSONAdaptor.Element('B', meta={'b': 2}))
        >>> config.get_meta('A')
        {'a': 1}
        >>> config.get_meta('A/B')
        {'b': 2}
        """
        return self.get_element(path).meta

    def get_text(self, path):
        """
        Retrieve the text representation for an element.

        Parameters
        ----------
        path : unicode
            The path pointing to the element that shall be retrieved.

        Returns
        -------
        text : unicode

        Raises
        ------
        InvalidPathError
            If the specified path does not point to an element.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax.
        :method:`~ConfigurationAdaptor.get_element` : Retrieve a configuration element.

        Examples
        --------
        >>> config = JSONAdaptor()
        >>> config.insert_element('A', JSONAdaptor.Element('A', 'a'))
        >>> config.insert_element('A/B', JSONAdaptor.Element('B', 'b'))
        >>> config.get_text('A')
        'a'
        >>> config.get_text('A/B')
        'b'
        """
        return self.get_element(path).text

    def update_text(self, path, value):
        """
        Update the text representation for an element.

        Parameters
        ----------
        path : unicode
            The path pointing to the element that shall be updated.
        value : unicode
            The new text representation of the element.

        Raises
        ------
        InvalidPathError
            If the specified path does not point to an element.

        Examples
        --------
        >>> config = JSONAdaptor()
        >>> config.insert_element('A', JSONAdaptor.Element('A', 'a'))
        >>> config.get_text('A')
        'a'
        >>> config.update_text('A', 'b')
        >>> config.get_text('A')
        'b'
        """
        element = self.get_element(path)
        element.text = value
        self.insert_element(path, element, replace=True)

    @classmethod
    def element_name_from_indexed_path(cls, path):
        """
        Compute the name of an element from its path. The path may contain indices,
        indicating which branch should be followed if multiple, parallel options are
        available. The indexing syntax is ``<element-name>[<index>]``.
        Examples: ``'a/b[1]/c'`` or ``'a/b[1]/c[2]'``.
        Using ``'<some-element-name>[0]'`` is equivalent to ``'<some-element-name>'``.
        Different path elements are separate by a slash ('/').

        Parameters
        ----------
        path : unicode
            The path pointing to the element.

        Returns
        -------
        element_name : unicode
            The element's name without index.

        Examples
        --------
        >>> element_name_from_indexed_path = ConfigurationAdaptor.element_name_from_indexed_path
        >>> element_name_from_indexed_path('path/to/element')
        'element'
        >>> element_name_from_indexed_path('path/to/element[2]')
        'element'
        """
        return re.sub(r'\[\d+\]', '', cls.split_path(path)[-1])

    @classmethod
    def join_paths(cls, *args):
        """
        Join multiple path elements into a single path. Duplicated as well as
        leading and trailing slashes are omitted. Empty path elements are ignored (left-out).

        Parameters
        ----------
        *args
            The path elements.

        Returns
        -------
        joined_path : unicode

        Examples
        --------
        >>> join_paths = ConfigurationAdaptor.join_paths
        >>> join_paths('path/to', 'element')
        'path/to/element'
        >>> join_paths('path/', 'to/', 'element/')
        'path/to/element'
        >>> join_paths('/path/', '/to/', '/element/')
        'path/to/element'
        >>> join_paths('', 'path/to/element', '', '')
        'path/to/element'
        """
        def clear_elements(elements):
            return map(lambda p: p[1:] if p.startswith(cls.PATH_DELIMITER) else p,
                       map(lambda p: p[:-1] if p.endswith(cls.PATH_DELIMITER) else p,
                           filter(None, elements)))
        return cls.PATH_DELIMITER.join(clear_elements(args))

    @classmethod
    def split_path(cls, path, max_number_of_splits=-1):
        """
        Split a path into its elements. Uses :func:`unicode.split` internally.

        Parameters
        ----------
        path : unicode
            The path to be split.
        max_number_of_splits : int
            If >= 0 indicates the maximum number of splits to be performed;
            If < 0 as many splits as possible are performed.

        Returns
        -------
        path_elements : list

        Examples
        --------
        >>> split_path = ConfigurationAdaptor.split_path
        >>> split_path('path/to/element')
        ['path', 'to', 'element']
        >>> split_path('path/to/element', max_number_of_splits=1)
        ['path', 'to/element']
        """
        return path.split(cls.PATH_DELIMITER, max_number_of_splits)

    @abc.abstractmethod
    def get_direct_elements(self):
        """
        Retrieve all direct elements of the configuration.

        A *direct element* is an element whose path contains only the element name
        (+ possible index) without other leading path elements. That is

        * ``'path/to/some_element'`` is not a direct element
        * ``'some_element'`` is a direct element

        .. warning::
        The order of elements from insertion is not necessarily preserved by
        this method (although the example below suggests it, which however
        happens by chance; try changing the order of insertions
        ``Element('B', 'b')`` and ``Element('A', 'a2')``, ``elements`` will
        remain the same however).

        Returns
        -------
        direct_elements : list[:class:`ConfigurationAdaptor.Element`]

        Examples
        --------
        >>> config = JSONAdaptor()
        >>> config.insert_element('A', JSONAdaptor.Element('A', 'a'))
        >>> config.insert_element('A/B', JSONAdaptor.Element('AB', 'ab'))
        >>> config.insert_element('A/B/C', JSONAdaptor.Element('ABC', 'abc'))
        >>> config.insert_element('B', JSONAdaptor.Element('B', 'b'))
        >>> config.insert_element('A', JSONAdaptor.Element('A', 'a2'))
        >>> elements = config.get_direct_elements()
        >>> len(elements)
        3
        >>> print(elements[0])
        {
            "text": "a",
            "meta": {},
            "name": "A"
        }
        >>> print(elements[1])
        {
            "text": "b",
            "meta": {},
            "name": "B"
        }
        >>> print(elements[2])
        {
            "text": "a2",
            "meta": {},
            "name": "A"
        }
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_element(self, path):
        """
        Retrieve an element from the configuration source.

        Parameters
        ----------
        path : unicode
            The path pointing to the element that shall be retrieved.

        Returns
        -------
        element : :class:`ConfigurationAdaptor.Element`

        Raises
        ------
        InvalidPathError
            If the specified path does not point to an element.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax.

        Examples:
        --------
        >>> config = JSONAdaptor()
        >>> config.insert_element('A/B', JSONAdaptor.Element('B', text='b', meta={'b': 2}))
        >>> element = config.get_element('A/B')
        >>> element.name, element.text, element.meta['b']
        ('B', 'b', 2)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_configuration(self, path):
        """
        Retrieve the sub-configuration that matches the specified path.

        Elements residing at the specified path will be omitted. Only elements
        that contain the specified path within their own path (as a qualified
        sub-path, not as the full path) are included.

        Parameters
        ----------
        path : unicode
            The path pointing to the new configuration.

        Returns
        -------
        configuration : self.__class__
            The sub-configuration to which `path` points.

        Raises
        ------
        InvalidPathError
            If no elements are located under the specified path.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax.

        Examples
        --------
        >>> config = JSONAdaptor()
        >>> config.insert_element('A/B', JSONAdaptor.Element('B', 'B'))
        >>> config.insert_element('A/B/C', JSONAdaptor.Element('C', 'C'))
        >>> config.insert_element('A/B/C/D', JSONAdaptor.Element('D', 'D'))
        >>> print(config.get_configuration('A/B'))
        {
            "C": {
                "text": "C",
                "meta": {}
            },
            "C/D": {
                "text": "D",
                "meta": {}
            }
        }
        >>> config.insert_element('A/B[1]/C/D', JSONAdaptor.Element('D2', 'D2'))
        >>> print(config.get_configuration('A/B'))
        {
            "C": {
                "text": "C",
                "meta": {}
            },
            "C/D": {
                "text": "D",
                "meta": {}
            }
        }
        >>> print(config.get_configuration('A/B[1]'))
        {
            "C/D": {
                "text": "D2",
                "meta": {}
            }
        }
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_sibling_configurations(self, path):
        """
        Retrieve all sibling configurations that match the specified path.

        Elements residing at the specified path will be omitted. Only elements
        that contain the specified path within their own path (as a qualified
        sub-path, not as the full path) are included. This method works similarly
        to :method:`~ConfigurationAdaptor.get_configuration` however it returns
        one configuration per branch at for `path`'s leaf element.

        Parameters
        ----------
        path : unicode
            The path pointing to the new configurations.

        Returns
        -------
        sibling_configurations : list[self.__class__]

        Raises
        ------
        InvalidPathError
            If no elements are located under the specified path.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax.

        Examples
        --------
        >>> config = JSONAdaptor()
        >>> config.insert_element('A/B', JSONAdaptor.Element('B', 'B'))
        >>> config.insert_element('A/B/C', JSONAdaptor.Element('C', 'C'))
        >>> config.insert_element('A/B/C/D', JSONAdaptor.Element('D', 'D'))
        >>> sibling_configurations = config.get_sibling_configurations('A/B')
        >>> len(sibling_configurations)
        1
        >>> print(sibling_configurations[0])
        {
            "C": {
                "text": "C",
                "meta": {}
            },
            "C/D": {
                "text": "D",
                "meta": {}
            }
        }
        >>> config.insert_element('A/B[1]/C/D', JSONAdaptor.Element('D2', 'D2'))
        >>> sibling_configurations = config.get_sibling_configurations('A/B')
        >>> len(sibling_configurations)
        2
        >>> print(sibling_configurations[0])
        {
            "C": {
                "text": "C",
                "meta": {}
            },
            "C/D": {
                "text": "D",
                "meta": {}
            }
        }
        >>> print(sibling_configurations[1])
        {
            "C/D": {
                "text": "D2",
                "meta": {}
            }
        }
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_sub_configurations(self, path):
        """
        Retrieve all sub-configurations at the specified path.

        All branches at the specified path are considered paths to separate
        sub-configurations. A list of configurations that match those
        sub-configuration-paths is returned (similarly to
        :method:`~ConfigurationAdaptor.get_configuration`).
        For example, a branch at path ``'path/to'`` is each path that matches
        ``'path/to/<some-element-name>'``.

        Parameters
        ----------
        path : unicode
            The path at which all branches are used as paths to new sub-configurations.

        Returns
        -------
        sub_configurations : list[self.__class__]

        Raises
        ------
        InvalidPathError
            If no elements are located under the specified path.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax.

        Examples
        --------
        >>> config = JSONAdaptor()
        >>> config.insert_element('A/B', JSONAdaptor.Element('B', 'B'))
        >>> config.insert_element('A/B/C', JSONAdaptor.Element('C', 'C'))
        >>> config.insert_element('A/B/C/D', JSONAdaptor.Element('D', 'D'))
        >>> sub_configurations = config.get_sub_configurations('A')
        >>> len(sub_configurations)
        1
        >>> print(sub_configurations[0])
        {
            "C": {
                "text": "C",
                "meta": {}
            },
            "C/D": {
                "text": "D",
                "meta": {}
            }
        }
        >>> config.insert_element('A/B[1]/C/D', JSONAdaptor.Element('D2', 'D2'))
        >>> sub_configurations = config.get_sub_configurations('A')
        >>> len(sub_configurations)
        2
        >>> print(sub_configurations[0])
        {
            "C": {
                "text": "C",
                "meta": {}
            },
            "C/D": {
                "text": "D",
                "meta": {}
            }
        }
        >>> print(sub_configurations[1])
        {
            "C/D": {
                "text": "D2",
                "meta": {}
            }
        }
        """
        raise NotImplementedError

    @abc.abstractmethod
    def insert_element(self, path, element, replace=False, **kwargs):
        """
        Insert an element at the specified path.

        If the index of a path element does not correspond to a branch
        in the configuration then a new branch is used instead.
        If the path points to an existing element then the optional argument
        `replace` controls whether this element is replaced or a new sibling
        element is used instead. In that case the path's leaf (the element's name)
        is duplicated (and correspondingly indexed) in order to create a new sibling element.

        Parameters
        ----------
        path : unicode
            The path at which the element is inserted.
        element : :class:`ConfigurationAdaptor.Element` or unicode
            The element to be inserted; if given as a unicode string
            it is considered the text representation.
        replace : bool
            Controls whether an existing element at the specified path is
            replaced or duplicated.
        **kwargs : optional
            Meta data about the element.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax.

        Examples
        --------
        >>> config = JSONAdaptor()
        >>> config.insert_element('A', 'a')
        >>> print(config)
        {
            "A": {
                "text": "a",
                "meta": {}
            }
        }
        >>> config.insert_element('A/B/C', 'c', some_attribute='Some helpful information')
        >>> print(config)
        {
            "A": {
                "text": "a",
                "meta": {}
            },
            "A/B/C": {
                "text": "c",
                "meta": {
                    "some_attribute": "Some helpful information"
                }
            }
        }
        >>> config.insert_element('A/B/C', 'c2')
        >>> print(config)
        {
            "A": {
                "text": "a",
                "meta": {}
            },
            "A/B/C": {
                "text": "c",
                "meta": {
                    "some_attribute": "Some helpful information"
                }
            },
            "A/B/C__1": {
                "text": "c2",
                "meta": {}
            }
        }
        >>> config.insert_element('A/B/C[1]', 'replaced', replace=True)
        >>> print(config)
        {
            "A": {
                "text": "a",
                "meta": {}
            },
            "A/B/C": {
                "text": "c",
                "meta": {
                    "some_attribute": "Some helpful information"
                }
            },
            "A/B/C__1": {
                "text": "replaced",
                "meta": {}
            }
        }
        >>> config.insert_element('A/B/C[2]', 'c2')
        >>> print(config)
        {
            "A": {
                "text": "a",
                "meta": {}
            },
            "A/B/C": {
                "text": "c",
                "meta": {
                    "some_attribute": "Some helpful information"
                }
            },
            "A/B/C__1": {
                "text": "replaced",
                "meta": {}
            },
            "A/B/C__2": {
                "text": "c2",
                "meta": {}
            }
        }
        >>> config.insert_element('A/B/C[100]', 'c3')
        >>> print(config)
        {
            "A": {
                "text": "a",
                "meta": {}
            },
            "A/B/C": {
                "text": "c",
                "meta": {
                    "some_attribute": "Some helpful information"
                }
            },
            "A/B/C__1": {
                "text": "replaced",
                "meta": {}
            },
            "A/B/C__2": {
                "text": "c2",
                "meta": {}
            },
            "A/B/C__3": {
                "text": "c3",
                "meta": {}
            }
        }
        >>> config.insert_element('A[1]/B[1]/C[1]', 'many indices')
        >>> print(config)
        {
            "A": {
                "text": "a",
                "meta": {}
            },
            "A/B/C": {
                "text": "c",
                "meta": {
                    "some_attribute": "Some helpful information"
                }
            },
            "A/B/C__3": {
                "text": "c3",
                "meta": {}
            },
            "A/B/C__2": {
                "text": "c2",
                "meta": {}
            },
            "A__1/B/C": {
                "text": "many indices",
                "meta": {}
            },
            "A/B/C__1": {
                "text": "replaced",
                "meta": {}
            }
        }
        """
        raise NotImplementedError

    @abc.abstractmethod
    def insert_config(self, path, other, replace=False):
        """
        Extend this configuration by inserting all elements from the other configuration.
        The elements' paths in the extended configuration are compound of the specified
        `path` and the paths in `other`.

        Parameters
        ----------
        path : unicode
            The path at which to insert the other configuration's elements.
        other : self.__class__
            The configuration which holds the elements to be inserted.
        replace : bool, optional
            If `True` then existing elements are replaced by inserted ones
            otherwise they are duplicated.

        Returns
        -------
        self
            The instance.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax.

        Examples
        --------
        >>> config = JSONAdaptor()
        >>> config.insert_element('A', 'a')
        >>> config.insert_element('A/B/C', 'c')
        >>> print(config)
        {
            "A": {
                "text": "a",
                "meta": {}
            },
            "A/B/C": {
                "text": "c",
                "meta": {}
            }
        }
        >>> extended_config = JSONAdaptor().insert_config('X/Y/Z', config)
        >>> print(extended_config)
        {
            "X/Y/Z/A": {
                "text": "a",
                "meta": {}
            },
            "X/Y/Z/A/B/C": {
                "text": "c",
                "meta": {}
            }
        }
        >>> other_config = JSONAdaptor()
        >>> other_config.insert_element('A/D/E', 'e')
        >>> extended_config = config.insert_config('', other_config)
        >>> print(extended_config)
        {
            "A": {
                "text": "a",
                "meta": {}
            },
            "A/B/C": {
                "text": "c",
                "meta": {}
            },
            "A/D/E": {
                "text": "e",
                "meta": {}
            }
        }
        >>> other_config.insert_element('A/D/E', 'e replaced', replace=True)
        >>> extended_config = extended_config.insert_config('', other_config, replace=True)
        >>> print(extended_config)
        {
            "A": {
                "text": "a",
                "meta": {}
            },
            "A/B/C": {
                "text": "c",
                "meta": {}
            },
            "A/D/E": {
                "text": "e replaced",
                "meta": {}
            }
        }
        >>> extended_config = extended_config.insert_config('', other_config)
        >>> print(extended_config)
        {
            "A": {
                "text": "a",
                "meta": {}
            },
            "A/B/C": {
                "text": "c",
                "meta": {}
            },
            "A/D/E": {
                "text": "e replaced",
                "meta": {}
            },
            "A/D/E__1": {
                "text": "e replaced",
                "meta": {}
            }
        }
        """
        if not isinstance(other, self.__class__):
            raise TypeError('Cannot extend %s with %s' % (self.__class__, type(other)))

    @classmethod
    def _head_tail_action(cls, path, head_action=None, tail_action=None):
        """
        Split a path into head and tail and apply different functions to them.

        * If `path` contains a single element then `tail_action` is ignored and
          `head_action` is applied to `path`; the result of `head_action` is returned.
        * If path is compound of multiple elements then the first element
          is considered its head and the remaining elements are considered its tail
          (as a joined sub-path). `head_action` is applied to `head` and if its return value
          is not `None` it will be passed to `tail_action` as an additional argument::

            >>> if head_action_result is not None: return tail_action(tail, head_action_result)
            ... else: return tail_action(tail)

          The result of `tail_action` is returned.

        Parameters
        ----------
        path : unicode
            The path from which head and tail are extracted.
        head_action : callable
            Function that shall be applied to the head; if `None` it will be converted to
            a no-op returning `None`.
        tail_action : callable
            Function that shall be applied to the tail; if `None` it will be converted to
            a no-op returning `None`.

        Returns
        -------
        result
            The result of `head_action` if `path` is a single element
            else the result of `tail_action`.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax.
        """
        if head_action is None:
            def head_action(_): return None
        if tail_action is None:
            # noinspection PyUnusedLocal
            def tail_action(*args): return None

        try:
            head, tail = cls.split_path(path, 1)
        except ValueError:
            # Path consists of a single element.
            return head_action(path)
        else:
            # noinspection PyNoneFunctionAssignment
            head_action_result = head_action(head)
            if head_action_result is not None:
                return tail_action(tail, head_action_result)
            else:
                return tail_action(tail)

    @classmethod
    def _leaf_action(cls, path, leaf_action):
        """
        Split a path into head and leaf and apply an action to the leaf.
        The leaf is the `path`s last element (if `path` contains only a
        single element then it's also the leaf).

        Parameters
        ----------
        path : unicode
            The path from which the leaf element is extracted.
        leaf_action : callable
            Function that shall be applied to the leaf element.

        Returns
        -------
        result
            The return value of ``leaf_action(leaf)``.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax
        """
        return leaf_action(cls.split_path(path)[-1])

    @classmethod
    def _parse_index_from_element_identifier(cls, identifier):
        """
        Retrieve the index from an element identifier (element name with optional index).

        An identifier has the following format:
        ``'<some-element-name>[<optional-index-as-integer>]'``
        If no index is given (that is just an element name) then
        the square brackets must be omitted too.

        Parameters
        ----------
        identifier : unicode
            The element identifier (with index if specified).

        Returns
        -------
        index : None or int
            None if the identifier specifies no index else the index as int.

        Examples
        --------
        >>> parse_index = ConfigurationAdaptor._parse_index_from_element_identifier
        >>> parse_index('SomeElement')  # => None
        >>> parse_index('SomeElement[0]')
        0
        >>> parse_index('SomeElement[1]')
        1
        """
        match = re.search(r'\[(\d+)\]$', identifier)
        if match is None:
            return None
        return int(match.groups()[0])

    @classmethod
    def _parse_name_from_element_identifier(cls, identifier):
        """
        Retrieve the name from an element identifier (element name with optional index).

        An identifier has the following format:
        ``'<some-element-name>[<optional-index-as-integer>]'``
        If no index is given (that is just an element name) then
        the square brackets must be omitted too.

        Parameters
        ----------
        identifier : unicode
            The element identifier (with index if specified).

        Returns
        -------
        element_name : unicode
            The element name without index.

        Examples
        --------
        >>> parse_index = ConfigurationAdaptor._parse_index_from_element_identifier
        >>> parse_index('SomeElement')
        'SomeElement'
        >>> parse_index('SomeElement[0]')
        'SomeElement'
        >>> parse_index('SomeElement[1]')
        'SomeElement'
        """
        return re.sub(r'\[\d+\]', '', identifier)


class FileAdaptor(ConfigurationAdaptor):
    """
    (Abstract) Base class for configuration adaptors that connect to files.
    A file type must be specified via a common suffix, provided as the class
    attribute ``FILE_TYPE``.
    """

    # The file type is indicated by the suffix which files of this type carry (e.g. '.xml').
    FILE_TYPE = None

    def __init__(self):
        super(FileAdaptor, self).__init__()

        if self.FILE_TYPE is None:
            raise TypeError('The file type of a FileAdaptor must be specified via FILE_TYPE')
        if not isinstance(self.FILE_TYPE, six.text_type):
            raise TypeError(
                'The file type of a FileAdaptor must be specified as a string (got %s instead)'
                % type(self.FILE_TYPE)
            )

    @abc.abstractmethod
    def dump_to_file(self, filepath):
        """
        Dump the configuration to a file using the adaptors associated format.
        The format is associated with the file type. If a file exists at the
        specified file path it is overwritten.

        Parameters
        ----------
        filepath : unicode
        """
        if not isinstance(filepath, six.text_type):
            raise TypeError(
                'The file path must be given as a string (got %s instead)'
                % type(filepath)
            )


@six.python_2_unicode_compatible
class XMLAdaptor(FileAdaptor):
    """
    Connects to an XML file as source.

    The configuration must be wrapped in an additional root element whose name
    can be arbitrarily chosen::

        <Root>
            <SomeElement/>
            <SomeOtherElement/>
        </Root>

    Text is stored as XML elements' text and meta data is stored as XML elements' attributes::

        <SomeElement some_meta_data="1">This is the parameter's text representation</SomeElement>
    """

    FILE_TYPE = '.xml'

    def __init__(self, filepath=None, root=None):
        """
        Connect to an existing XML element or an XML file.

        * If filepath is given then the adaptor connects to the corresponding XML file
          (parsing it's DOM tree).
        * If filepath is not given but ``root`` is given then the adaptor connects to
          the specified root element using it as the root element of its DOM tree;
          if ``root`` is a string it creates an empty configuration with root being
          the name of the root element.
        * If neither filepath nor root is given an empty configuration with only
          one root element is created.
        * If both are specified a ``TypeError`` is raised.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element or unicode, optional
            Root element representing the DOM tree or string representing the name
            of the root element in a new DOM tree.
        filepath : unicode, optional
            File path pointing to the XML file which contains the DOM tree.
        """
        super(XMLAdaptor, self).__init__()

        if filepath is not None and root is not None:
            raise TypeError("It's ambiguous to specify both a root element and a file path")
        if filepath is not None and not isinstance(filepath, six.text_type):
            if isinstance(filepath, six.binary_type):
                filepath = filepath.decode('utf-8')
            else:
                raise TypeError(
                    'A file path must be of type unicode (got %s instead)'
                    % type(filepath)
                )
        if root is not None and not isinstance(
                root,
                (xml.etree.ElementTree.Element, six.text_type)):
            raise TypeError(
                'A root element must be of type xml.etree.ElementTree.Element (got %s instead)'
                % type(root)
            )

        if filepath is not None:
            self._root = xml.etree.ElementTree.parse(filepath).getroot()
            self._unicodify()
        elif root is not None:
            if isinstance(root, xml.etree.ElementTree.Element):
                self._root = root
            else:
                self._root = xml.etree.ElementTree.Element(root)
        else:
            self._root = xml.etree.ElementTree.Element('Root')

    def __str__(self):
        return xml.dom.minidom.parseString(
            xml.etree.ElementTree.tostring(self._root)
        ).toprettyxml(indent=4*' ')

    @use_docs_from(FileAdaptor)
    def dump_to_file(self, filepath):
        super(XMLAdaptor, self).dump_to_file(filepath)
        as_string = xml.etree.ElementTree.tostring(self._root, encoding='utf-8')
        parsed = xml.dom.minidom.parseString(as_string)
        with open(filepath, 'w') as fp:
            fp.write(parsed.toprettyxml(indent=4*' '))

    def get_direct_elements(self):
        """
        Retrieve all direct elements of the configuration.

        .. warning::
        An XMLAdaptor behaves differently in a sense that a path is always compound of
        XML elements and so it can't distinguish between XML elements that represent
        a parameter and XML elements that have been inserted only to build the path to
        another element. That is this specific implementation might return elements
        that have no "real" meaning but only act as path elements. Therefore the return value
        from this method might differ from other implementations (such as
        :method:`JSONAdaptor.get_direct_elements`) for example.

        See Also
        --------
        :method:`ConfigurationAdaptor.get_direct_elements`
        """
        return list(map(lambda e: self.Element(*self._inspect_element(e)), self._root))

    @use_docs_from(FileAdaptor)
    def get_element(self, path):
        node = self._find_element_from_indexed_path(self._root, path)
        if node is None:
            raise InvalidPathError(path)
        _, text, attrib = self._inspect_element(node)
        return self.Element(self.element_name_from_indexed_path(path), text, attrib)

    @use_docs_from(FileAdaptor)
    def get_configuration(self, path):
        # If no index is given (None) use 0 instead.
        index = self._leaf_action(path, self._parse_index_from_element_identifier) or 0
        try:
            return self.get_sibling_configurations(path)[index]
        except IndexError:
            raise InvalidPathError(path)

    @use_docs_from(FileAdaptor)
    def get_sibling_configurations(self, path):
        if len(self.split_path(path)) == 1:
            node = self._root
        else:
            head_path = self.join_paths(*self.split_path(path)[:-1])
            node = self._find_element_from_indexed_path(self._root, head_path)
            if node is None:
                raise InvalidPathError(path)
        sibling_configurations = \
            [XMLAdaptor(root=element)
             for element in node.findall(self.element_name_from_indexed_path(path))]
        if not sibling_configurations:
            raise InvalidPathError(path)
        return sibling_configurations

    @use_docs_from(FileAdaptor)
    def get_sub_configurations(self, path):
        node = self._find_element_from_indexed_path(self._root, path)
        if node is None or not list(node):
            raise InvalidPathError(path)
        return [XMLAdaptor(root=element) for element in node]

    def _unicodify(self):
        def from_anchor(anchor):
            anchor.text = six.text_type(anchor.text) if anchor.text is not None else ''
            for child in anchor:
                from_anchor(child)
        from_anchor(self._root)

    @classmethod
    def _check_if_path_exists(cls, anchor, path):
        """
        Check if a path exists from the view of an anchor.

        Parameters
        ----------
        anchor : xml.etree.ElementTree.Element
            The anchor from which the path is considered to start.
        path : unicode
            The (indexed) path to be checked.

        Returns
        -------
        exists : bool
            True if the path exists False otherwise.

        Examples
        --------
        >>> import xml.etree.ElementTree as xml
        >>> root = xml.Element('Root')
        >>> a0 = xml.Element('A')
        >>> root.append(a0)
        >>> b0 = xml.Element('B')
        >>> a0.append(b0)
        >>> c0 = xml.Element('C')
        >>> b0.append(c0)
        >>> XMLAdaptor._check_if_path_exists(root, 'A/B/C')
        True
        >>> XMLAdaptor._check_if_path_exists(root, 'A/B')
        True
        >>> XMLAdaptor._check_if_path_exists(root, 'B/C')
        False
        >>> XMLAdaptor._check_if_path_exists(a0, 'B/C')
        True
        >>> XMLAdaptor._check_if_path_exists(a0, 'C')
        False
        >>> XMLAdaptor._check_if_path_exists(b0, 'C')
        True
        >>> a1 = xml.Element('A')
        >>> root.append(a1)
        >>> a1.append(b0)
        >>> XMLAdaptor._check_if_path_exists(root, 'A[1]/B')
        True
        >>> XMLAdaptor._check_if_path_exists(root, 'A[1]/B[1]')
        False
        """
        return cls._find_element_from_indexed_path(anchor, path) is not None

    @classmethod
    def _build_path(cls, anchor, path):
        """
        Build the specified path starting from the specified anchor.
        This method gradually checks each element along the path and
        if it doesn't exist it will be created.
        If the specified path already exists this is a no-op.

        Parameters
        ----------
        anchor : xml.etree.ElementTree.Element
            The element from which the path shall start.
        path : unicode

        Returns
        -------
        leaf : xml.etree.ElementTree.Element
            The last element of the path.

        Examples
        --------
        >>> import xml.etree.ElementTree as xml
        >>> root = xml.Element('Root')
        >>> XMLAdaptor._check_if_path_exists(root, 'A/B/C')
        False
        >>> XMLAdaptor._build_path(root, 'A/B/C')
        <Element 'C' at 0x7f32128f0490>
        >>> XMLAdaptor._check_if_path_exists(root, 'A/B/C')
        True
        """
        try:
            head, tail = cls.split_path(path, 1)
        except ValueError:
            # Path consists of a single element.
            if not path or path == '.':
                next_element = anchor
            else:
                next_element = cls._find_child_from_identifier(anchor, path)
            if next_element is None:
                next_element = \
                    xml.etree.ElementTree.Element(cls._parse_name_from_element_identifier(path))
                anchor.append(next_element)
            return next_element
        else:
            next_element = cls._find_child_from_identifier(anchor, head)
            if next_element is None:
                next_element = \
                    xml.etree.ElementTree.Element(cls._parse_name_from_element_identifier(head))
                anchor.append(next_element)
            return cls._build_path(next_element, tail)

    @classmethod
    def _find_child_from_identifier(cls, anchor, identifier):
        """
        Find a child of anchor that matches the specified identifier.

        Parameters
        ----------
        anchor : xml.etree.ElementTree.Element
        identifier : unicode
            Name of the element (may be indexed).

        Returns
        -------
        child : None or xml.etree.ElementTree.Element
            The first child that matches the identifier or
            ``None`` if no child matches the identifier.

        Examples
        --------
        >>> import xml.etree.ElementTree as xml
        >>> root = xml.Element('Root')
        >>> root.append(xml.Element('A'))
        >>> root.append(xml.Element('A'))
        >>> XMLAdaptor._find_child_from_identifier(root, 'A')
        <Element 'A' at 0x7f3212b44b10>
        >>> XMLAdaptor._find_child_from_identifier(root, 'A[0]')
        <Element 'A' at 0x7f3212b44b10>
        >>> XMLAdaptor._find_child_from_identifier(root, 'A[1]')
        <Element 'A' at 0x7f32208924d0>
        >>> XMLAdaptor._find_child_from_identifier(root, 'A[1]').append(xml.Element('B'))
        >>> XMLAdaptor._find_child_from_identifier(root, 'B')  # => None
        """
        index = cls._parse_index_from_element_identifier(identifier)
        if index is not None:
            try:
                return anchor.findall(cls._parse_name_from_element_identifier(identifier))[index]
            except IndexError:
                # Element doesn't exist yet.
                return None
        return anchor.find(identifier)

    @classmethod
    def _find_element_from_indexed_path(cls, anchor, path):
        """
        Find an element at the specified path starting at the specified anchor.

        Parameters
        ----------
        anchor : xml.etree.ElementTree.Element
        path : unicode
            The path pointing to the element which may contain indices.

        Returns
        -------
        leaf : None or xml.etree.ElementTree.Element
            The first element that that is found at path or None if no element is found.

        Examples
        --------
        >>> import xml.etree.ElementTree as xml
        >>> root = xml.Element('Root')
        >>> root.append(xml.Element('A'))
        >>> root.find('A').append(xml.Element('B'))
        >>> root.find('A').find('B').append(xml.Element('C'))
        >>> XMLAdaptor._find_element_from_indexed_path(root, 'A')
        <Element 'A' at 0x7f3220892450>
        >>> XMLAdaptor._find_element_from_indexed_path(root, 'A/B/C')
        <Element 'C' at 0x7f32128f04d0>
        >>> XMLAdaptor._find_element_from_indexed_path(root, 'A/X')  # => None
        """
        try:
            head, tail = cls.split_path(path, 1)
        except ValueError:
            # Path contains a single element.
            return cls._find_child_from_identifier(anchor, path)
        else:
            child = cls._find_child_from_identifier(anchor, head)
            if child is not None:
                return cls._find_element_from_indexed_path(child, tail)
            return None

    @classmethod
    def _find_all_leaf_elements(cls, anchor):
        """
        Find all leaf elements of the specified anchor element. A leaf element is
        an element which has no children.

        Parameters
        ----------
        anchor : xml.etree.ElementTree.Element

        Returns
        -------
        leaf_elements : list
            A list containing tuples (path_to_leaf_element, leaf_element).

        Examples
        --------
        >>> import xml.etree.ElementTree as xml
        >>> root = xml.Element('Root')
        >>> a = xml.Element('A')
        >>> a_b = xml.Element('AB')
        >>> a.append(a_b)
        >>> root.append(a)
        >>> b = xml.Element('B')
        >>> root.append(b)
        >>> leafs = XMLAdaptor._find_all_leaf_elements(root)
        >>> len(leafs)
        2
        >>> list(zip(*leafs))[0]
        ('A/AB', 'B')
        >>> tuple(map(lambda x: x.tag, list(zip(*leafs))[1]))
        ('AB', 'B')
        >>> leafs[0][1] is a_b
        True
        >>> leafs[1][1] is b
        True
        >>> leafs = XMLAdaptor._find_all_leaf_elements(a)
        >>> len(leafs)
        1
        >>> leafs[0]
        ('AB', a_b)
        """
        # noinspection PyShadowingNames
        def find_all_leaf_elements(anchor, path_to_anchor=''):
            children = list(anchor)
            if not children:
                return [(path_to_anchor, anchor)]
            else:
                # Need to cast `child.tag` because of backward compatibility
                # with Python2.7 where this is a `str`.
                return sum(
                    map(lambda child:
                        find_all_leaf_elements(
                            child, cls.join_paths(path_to_anchor, six.text_type(child.tag))
                        ),
                        children),
                    []
                )
        return find_all_leaf_elements(anchor)

    @classmethod
    def _find_all_relevant_elements(cls, anchor):
        """
        Find all relevant elements which are descendants of the specified anchor element.
        A relevant element is an element which has a non-empty text, non-empty meta data or
        no children.

        Parameters
        ----------
        anchor : xml.etree.ElementTree.Element

        Returns
        -------
        relevant_elements : list
            A list containing tuples (path_to_relevant_element, relevant_element).

        Examples
        --------
        >>> import xml.etree.ElementTree as xml
        >>> root = xml.Element('Root')
        >>> a = xml.Element('A')
        >>> a.text = 'a'
        >>> a_b = xml.Element('AB')
        >>> a_b_c = xml.Element('ABC')
        >>> a_b_c.text = 'abc'
        >>> a_b.append(a_b_c)
        >>> a.append(a_b)
        >>> root.append(a)
        >>> b = xml.Element('B')
        >>> b.text = 'b'
        >>> root.append(b)
        >>> relevant_elements = XMLAdaptor._find_all_relevant_elements(root)
        >>> len(relevant_elements)
        3
        >>> list(zip(*relevant_elements))[0]
        ('A', 'A/AB/ABC', 'B')
        >>> tuple(map(lambda x: x.tag, list(zip(*relevant_elements))[1]))
        ('A', 'ABC', 'B')
        >>> relevant_elements[0][1] is a
        True
        >>> relevant_elements[1][1] is a_b_c
        True
        >>> relevant_elements[2][1] is b
        True
        """
        # noinspection PyShadowingNames
        def find_relevant_elements(anchor, path_to_anchor=''):
            elements = []
            children = list(anchor)
            if anchor.text or anchor.attrib or not children:
                elements.append((path_to_anchor, anchor))
            child_nrs = collections.defaultdict(int)
            subsequent_relevant_elements = []
            for child in children:
                child_nr = child_nrs[child.tag]
                subsequent_relevant_elements.extend(
                    find_relevant_elements(
                        child,
                        cls.join_paths(
                            path_to_anchor,
                            '%s[%d]' % (six.text_type(child.tag), child_nr)
                        )
                    )
                )
                child_nrs[child.tag] += 1
            return elements + subsequent_relevant_elements
        return find_relevant_elements(anchor)

    @use_docs_from(FileAdaptor)
    def insert_element(self, path, element, replace=False, **kwargs):
        if isinstance(element, six.text_type):
            element = self.Element('', element, kwargs)
        elif not isinstance(element, self.Element):
            raise TypeError(
                'Element must be given as unicode or ConfigurationAdaptor.Element (got %s instead)'
                % type(element)
            )
        element.meta.update(kwargs)
        element_exists = self._check_if_path_exists(self._root, path)
        if element_exists and not replace:
            if len(self.split_path(path)) == 1:
                # Path contains a single element.
                leaf = duplicated_element = \
                    xml.etree.ElementTree.Element(self._parse_name_from_element_identifier(path))
                self._root.append(duplicated_element)
            else:
                head = self.join_paths(*self.split_path(path)[:-1])
                tail = self.split_path(path)[-1]
                parent = self._build_path(self._root, head)
                leaf = duplicated_element = \
                    xml.etree.ElementTree.Element(self._parse_name_from_element_identifier(tail))
                parent.append(duplicated_element)
        elif not element_exists:
            leaf = self._build_path(self._root, path)
        else:
            # Replace the existing element.
            leaf = self._find_element_from_indexed_path(self._root, path)

        leaf.attrib = element.meta.copy()
        leaf.text = element.text

    @use_docs_from(FileAdaptor)
    def insert_config(self, path, other, replace=False):
        """
        Extend this configuration by inserting all elements from the other configuration.
        The elements' paths in the extended configuration are compound of the specified
        `path` and the paths in other.

        .. note::
        This method will only insert elements of `other` which have a non-zero text or non-zero
        meta data, all other elements are considered auxiliary (path building) elements.

        Parameters
        ----------
        path : unicode
            The path at which to insert the other configuration's parameters.
        other : self.__class__
            The configuration which holds the elements to be inserted.
        replace : bool, optional
            If True then existing elements are replaced by inserted ones
            otherwise they are duplicated.

        Returns
        -------
        self
            This instance.

        See Also
        --------
        :method:`~ConfigurationAdaptor.element_name_from_indexed_path` : For the path syntax.
        """
        super(XMLAdaptor, self).insert_config(path, other, replace)
        self._build_path(self._root, path)
        nodes = self._find_all_relevant_elements(other._root)
        for path_to_node, node in nodes:
            element = self.Element(node.tag, node.text, node.attrib)
            self.insert_element(self.join_paths(path, path_to_node), element, replace=replace)
        return self

    @staticmethod
    def _inspect_element(element):
        """
        This method exists for backward compatibility with Python2.7.
        In Python2.7 the `xml` API returns `str` wherever possible
        however unicode is required.

        Parameters
        ----------
        element : xml.etree.ElementTree.Element

        Returns
        -------
        tuple
            (tag, text, attributes), all strings as unicode.
        """
        text = six.text_type(element.text) if element.text is not None else ''
        return (
            six.text_type(element.tag),
            text,
            {six.text_type(k): six.text_type(v) if isinstance(v, six.binary_type) else v
             for k, v in element.attrib.items()}
        )


@six.python_2_unicode_compatible
class JSONAdaptor(FileAdaptor):
    """
    Connects to a JSON file as source.

    The configuration must be contained in a dictionary where the keys represent
    the elements' paths and the values represent the corresponding specification::

        {
            "path/to/some_element": {"text": "This is the parameter's text representation",
                                     "meta": {"some_meta_data": 1},
            ...
        }

    If a parameter has no meta data it's specification can also be represented as a string
    directly::

        {
            "path/to/some_element": "This is the parameter's text repr.; it has no meta data"
        }

    Multiple parameters sharing a similar path are realized by path elements of subsequent
    parameters being escaped appropriately (using a double underscore followed by
    an incrementing integer) and thus indicating a new branch::

        {
            "path/to/some_element": ...,
            "path/to/some_element__1": ...,
            "path/to/some_element__2": ...,
        }

    or

        {
            "path/to/some_element": ...,
            "path/to__1/some_element": ...,
            "path/to__1/some_element__1": ...,
        }

    Just the escaped paths must be unique and the format ``name__\d+`` indicates
    parallel branches (or elements).
    """

    FILE_TYPE = '.json'

    def __init__(self, filepath=None, root=None):
        """
        Connect to an existing JSON element or a JSON file.

        * If `filepath` is given then the adaptor connects to the corresponding JSON file
          (parsing it's content).
        * If `filepath` is not given but `root` is given then the adaptor connects to
          the specified `root` element using it as the underlying JSON object.
        * If neither `filepath` nor `root` is given it will create an empty configuration with
          an empty dict as root.
        * If both are specified a `TypeError` is raised.

        Parameters
        ----------
        filepath : unicode, optional
            File path pointing to the JSON file which contains the configuration.
        root : dict, optional
            JSON object acting as root element.
        """
        super(JSONAdaptor, self).__init__()

        if filepath is not None and root is not None:
            raise TypeError("It's ambiguous to specify both a root element and a file path")
        if filepath is not None and not isinstance(filepath, six.text_type):
            if isinstance(filepath, six.binary_type):
                filepath = filepath.decode('utf-8')
            else:
                raise TypeError(
                    'A file path must be of type unicode (got %s instead)'
                    % type(filepath)
                )
        if root is not None and not isinstance(root, dict):
            raise TypeError(
                'A root element must be of type dict (got %s instead)'
                % type(root)
            )

        if filepath is not None:
            with open(filepath) as fp:
                self._root = json.load(fp)
        elif root is not None:
            self._root = root
        else:
            self._root = {}

    def __str__(self):
        return json.dumps(self._root, indent=4)

    @use_docs_from(FileAdaptor)
    def dump_to_file(self, filepath):
        with open(filepath, 'w') as fp:
            json.dump(self._root, fp, indent=4)

    @use_docs_from(FileAdaptor)
    def get_direct_elements(self):
        element_paths = filter(lambda p: self.PATH_DELIMITER not in p, self._root)
        return list(
            map(lambda x: self.Element(self._parse_name_from_element_identifier(x[0]),
                                       x[1].get('text'),
                                       x[1].get('meta')),
                map(lambda p: (p, self._root[p]), element_paths))
        )

    @use_docs_from(FileAdaptor)
    def get_element(self, path):
        try:
            node = self._root[self._convert_indexed_path_to_escaped_path(path)]
        except KeyError:
            raise InvalidPathError(path)
        if isinstance(node, six.text_type):
            text, meta = node, None
        elif isinstance(node, dict):
            text, meta = node.get('text'), node.get('meta')
        else:
            raise TypeError(
                'Parameters in a JSON configuration must be given either as '
                'dict or unicode (found %s instead)'
                % type(node)
            )
        return self.Element(self.element_name_from_indexed_path(path), text, meta)

    @use_docs_from(FileAdaptor)
    def get_configuration(self, path):
        path = self._convert_indexed_path_to_escaped_path(path)
        # Append path delimiter so post-fixed configuration paths
        # of the form "path__1" are not considered.
        if not path.endswith(self.PATH_DELIMITER):
            path += self.PATH_DELIMITER
        relevant_paths = filter(lambda p: p.startswith(path), self._root)
        new_config = {}
        for element_path in relevant_paths:
            new_path = re.sub(r'^{0}'.format(path), '', element_path)
            new_config[new_path] = self._root[element_path]
        return JSONAdaptor(root=new_config)

    @use_docs_from(FileAdaptor)
    def get_sibling_configurations(self, path):
        # Remove path delimiter so post-fixed configuration paths
        # of the form "path__1" are considered.
        path = self._convert_indexed_path_to_escaped_path(path)
        if path.endswith(self.PATH_DELIMITER):
            path = path[:-1]
        relevant_paths = filter(lambda p: p.startswith(path), self._root)
        path_elements = self.split_path(path)
        head, tail = self.join_paths(*path_elements[:-1]), path_elements[-1]
        numbered_element_names = set(map(
            lambda p: re.match(r'{0}/({1}(__\d+)?)'.format(head, tail), p).groups()[0],
            relevant_paths
        ))

        def sort_by_postfix(name):
            match = re.search(r'__(\d+)$', name)
            return 0 if match is None else int(match.groups()[0])

        numbered_element_names = sorted(numbered_element_names, key=sort_by_postfix)
        paths_to_configs = map(lambda name: self.join_paths(head, name), numbered_element_names)
        return list(map(lambda p: self.get_configuration(p), paths_to_configs))

    @use_docs_from(FileAdaptor)
    def get_sub_configurations(self, path):
        path = self._convert_indexed_path_to_escaped_path(path)
        if not path.endswith(self.PATH_DELIMITER):
            path += self.PATH_DELIMITER
        relevant_paths = filter(lambda p: p.startswith(path), self._root)
        relevant_elements = map(lambda p: self.split_path(p.replace(path, ''))[0], relevant_paths)
        relevant_elements = set(map(lambda e: re.sub(r'__\d+', '', e), relevant_elements))
        # Concatenate the lists of configurations.
        return sum(map(
            lambda e: self.get_sibling_configurations(self.join_paths(path, e)),
            relevant_elements
        ), [])

    def _check_if_path_exists(self, path):
        """
        Check if the specified path exists in the configuration.

        Parameters
        ----------
        path : unicode
            The path to be checked (may contain indices).

        Returns
        -------
        exists : bool
            True if the path exists False otherwise.

        Examples
        --------
        >>> config = JSONAdaptor(root={
        ... 'A/B/C': None
        ... })
        >>> config._check_if_path_exists('A')
        False
        >>> config._check_if_path_exists('A/B')
        False
        >>> config._check_if_path_exists('A/B/C')
        True
        """
        return self._convert_indexed_path_to_escaped_path(path) in self._root

    @classmethod
    def _convert_indexed_path_to_escaped_path(cls, path):
        """
        Convert a path containing indices ('\[\d+\]') to a path containing escapes ('__\d+').

        Parameters
        ----------
        path : unicode
            The path to be converted (may contain indices).

        Returns
        -------
        escaped_path : unicode
            The escaped path where each index has been replaced by the corresponding
            escape with the exception of zero indices ('\[0\]') which are just omitted.

        Examples
        --------
        >>> JSONAdaptor._convert_indexed_path_to_escaped_path('A/B/C')
        'A/B/C'
        >>> JSONAdaptor._convert_indexed_path_to_escaped_path('A[0]/B[1]/C[2]')
        'A/B__1/C__2'
        """
        return re.sub(r'(\[(\d+)\])', r'__\2', re.sub(r'\[0\]', r'', path))

    @classmethod
    def _convert_path_to_bare_tail_path(cls, path):
        """
        Strips the index (if present) from the last path element (i.e. ensuring
        that it has a "bare tail").

        Parameters
        ----------
        path : unicode
            The path to be converted (may contain indices).

        Returns
        -------
        bare_tail_path : unicode
            Similar as path but the last path element is guaranteed to be without index.

        Examples
        --------
        >>> JSONAdaptor._convert_path_to_bare_tail_path('A/B/C')
        'A/B/C'
        >>> JSONAdaptor._convert_path_to_bare_tail_path('A[0]/B[1]/C[2]')
        'A[0]/B[1]/C'
        """
        if len(cls.split_path(path)) > 1:
            head = cls.join_paths(*cls.split_path(path)[:-1])
            tail = cls._parse_name_from_element_identifier(cls.split_path(path)[-1])
            return cls.join_paths(head, tail)
        else:
            return cls._parse_name_from_element_identifier(path)

    def _get_max_escape_index_for_leaf(self, path):
        """
        Retrieve the maximum escape index that is currently present for
        the leaf element of the specified path.

        .. note::
        The path may also denote a sub-path corresponding to elements of the configuration.
        The method checks for duplicated (parallel) **path** elements at the specified
        `path`'s leaf (see Examples).

        Parameters
        ----------
        path : unicode
            May contain indices.

        Returns
        -------
        index : None or int
            If one or more elements are found at the specified path returns
            the maximum escape index of all siblings (0 if only one element
            is present); returns None if no element is found at the specified path.

        Examples
        --------
        >>> config = JSONAdaptor(root={
        ... 'A/B': None,
        ... 'A/B/C': None,
        ... 'A/B/C__1': None,
        ... })
        >>> config._get_max_escape_index_for_leaf('A')
        0
        >>> config._get_max_escape_index_for_leaf('A/B')
        0
        >>> config._get_max_escape_index_for_leaf('A/B/C')
        1
        """
        bare_tail_path = \
            self._convert_indexed_path_to_escaped_path(self._convert_path_to_bare_tail_path(path))
        siblings_escape_ids = map(int,
                                  map(lambda x: 0 if x.groups()[0] is None else x.groups()[0][2:],
                                      filter(lambda x: x is not None,
                                             map(lambda x: re.match(
                                                 r'^{0}(__\d+)?'.format(bare_tail_path), x),
                                                 self._root))))
        siblings_escape_ids = tuple(siblings_escape_ids)
        if not siblings_escape_ids:
            return None
        else:
            return max(siblings_escape_ids)

    def _gradually_check_and_adjust_path_indices(self, path):
        """
        Adjusts the path's escape indices in a way that their differences to
        the greatest corresponding existing indices is not greater than 1.
        This ensures that no gaps are introduced to the path for elements' escape indices.

        .. note::
        This method should be used to prepare a path before inserting it into
        the configuration in order to ensure that escape indices are consistently
        incremented.

        .. note::
        Zero indices ('\[0\]') are omitted from the adjusted path.

        Parameters
        ----------
        path : unicode
            May contain indices.

        Returns
        -------
        adjusted_path : unicode
            A path for which escape index differences to the greatest existing counterparts
            is guaranteed to be at maximum 1.

        Examples
        --------
        >>> config = JSONAdaptor(root={
        ... 'A/B': None,
        ... 'A/B/C': None,
        ... 'A/B/C__1': None,
        ... })
        >>> config._gradually_check_and_adjust_path_indices('A/B/C')
        'A/B/C'
        >>> config._gradually_check_and_adjust_path_indices('A[0]/B[1]/C[0]')
        'A/B[1]/C'
        >>> config._gradually_check_and_adjust_path_indices('A[0]/B[2]/C[1]')
        'A/B[1]/C'
        >>> config._gradually_check_and_adjust_path_indices('A[1]/B[1]/C[1]')
        'A[1]/B/C'
        >>> config._gradually_check_and_adjust_path_indices('A/B/C[2]')
        'A/B/C[2]'
        >>> config._gradually_check_and_adjust_path_indices('A/B/C[3]')
        'A/B/C[2]'
        """
        path_elements = self.split_path(path)

        max_index = self._get_max_escape_index_for_leaf(path_elements[0])
        index = self._parse_index_from_element_identifier(path_elements[0])
        if index is not None and max_index is not None and index > max_index + 1:
            adjusted_id = re.sub(r'\[\d+\]', r'[%d]' % (max_index + 1), path_elements[0])
        elif max_index is None:
            adjusted_id = re.sub(r'\[\d+\]', r'', path_elements[0])
        else:
            adjusted_id = re.sub(r'\[0\]', r'', path_elements[0])

        gradual_path = adjusted_id
        # gradual_bare_path = self.element_name_from_indexed_path(path_elements[0])

        for path_element in path_elements[1:]:
            max_index = \
                self._get_max_escape_index_for_leaf(self.join_paths(gradual_path, path_element))
            index = self._parse_index_from_element_identifier(path_element)
            if index is not None and max_index is not None and index > max_index + 1:
                adjusted_id = re.sub(r'\[\d+\]', r'[%d]' % (max_index + 1), path_element)
            elif max_index is None:
                adjusted_id = re.sub(r'\[\d+\]', r'', path_element)
            else:
                adjusted_id = re.sub(r'\[0\]', r'', path_element)
            gradual_path = self.join_paths(gradual_path, adjusted_id)
            # gradual_bare_path = \
            # self.join_paths(gradual_bare_path, self.element_name_from_indexed_path(path_element))
        return gradual_path

    @use_docs_from(FileAdaptor)
    def insert_element(self, path, element, replace=False, **kwargs):
        if isinstance(element, six.text_type):
            element = self.Element('', element, None)
        elif not isinstance(element, self.Element):
            raise TypeError(
                'Element must be given as unicode or ConfigurationAdaptor.Element '
                '(got %s instead)'
                % type(element)
            )
        element.meta.update(kwargs)
        if not replace and self._check_if_path_exists(path):
            bare_tail_path = \
                self._convert_indexed_path_to_escaped_path(
                    self._convert_path_to_bare_tail_path(path)
                )
            max_index = self._get_max_escape_index_for_leaf(path)
            if max_index is None:
                self._root[bare_tail_path] = {
                    'text': element.text,
                    'meta': element.meta,
                }
            else:
                self._root['%s__%d' % (bare_tail_path, max_index + 1)] = {
                    'text': element.text,
                    'meta': element.meta,
                }
        else:
            path = \
                self._convert_indexed_path_to_escaped_path(
                    self._gradually_check_and_adjust_path_indices(path)
                )
            self._root[path] = {
                'text': element.text,
                'meta': element.meta,
            }

    @use_docs_from(FileAdaptor)
    def insert_config(self, path, other, replace=False):
        super(JSONAdaptor, self).insert_config(path, other, replace)
        for other_path, element in iter(other._root.items()):
            element = self.Element(self.element_name_from_indexed_path(other_path),
                                   element.get('text'),
                                   element.get('meta'))
            self.insert_element(self.join_paths(path, other_path), element, replace=replace)
        return self

    @classmethod
    def _parse_name_from_element_identifier(cls, identifier):
        """
        Get an element's name from it's identifier. The identifier may contain
        an index ('\[\d+\]') or an escape index ('__\d+').

        Parameters
        ----------
        identifier : unicode
            May contain an index or an escape index.

        Returns
        -------
        name : unicode
            The name without any indices.

        See Also
        --------
        :py:meth:`ConfigurationAdaptor._parse_name_from_element_identifier` : Parse name from
        a (regularly) indexed identifier.

        Examples
        --------
        >>> JSONAdaptor._parse_name_from_element_identifier('SomeElement')
        'SomeElement'
        >>> JSONAdaptor._parse_name_from_element_identifier('SomeElement[0]')
        'SomeElement'
        >>> JSONAdaptor._parse_name_from_element_identifier('SomeElement__1')
        'SomeElement'
        """
        return re.sub(
            r'__\d+', r'',
            super(JSONAdaptor, cls)._parse_name_from_element_identifier(identifier)
        )


def load_from_file(filepath):
    """
    Load the specifications from the file source at `filepath` using the appropriate
    configuration file adaptor. The file adaptor is determined from `filepath`'s suffix.

    Parameters
    ----------
    filepath : unicode

    Returns
    -------
    configuration : :class:`ConfigurationAdaptor` derived class

    Examples
    --------
    >>> type(load_from_file('config.json'))
    <class JSONAdaptor>
    >>> type(load_from_file('config.xml'))
    <class XMLAdaptor>
    """
    _, extension = os.path.splitext(filepath)

    file_adaptors = filter(
        lambda obj: isinstance(obj, type) and issubclass(obj, FileAdaptor),
        globals().values()
    )

    try:
        config_adaptor = tuple(filter(
            lambda file_adaptor: file_adaptor.FILE_TYPE == extension,
            file_adaptors)
        )[0]
    except IndexError:
        raise TypeError('No adaptor available for file type "%s"' % extension)

    logging.getLogger(__name__).info('Loading configuration from "%s" using adaptor %s',
                                     filepath, config_adaptor)

    return config_adaptor(filepath=filepath)
