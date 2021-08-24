# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import abc

from contrast.extern import six


@six.add_metaclass(abc.ABCMeta)
class BaseResponseWrapper(object):
    @property
    @abc.abstractmethod
    def body(self):
        """
        Response body as bytes
        """
        pass

    @property
    @abc.abstractmethod
    def headers(self):
        """
        Response headers as a dictionary-like object.

        This object must support normalized lowercase lookup. For example:
        my_response_wrapper.headers['content-length']

        In order to properly extract response headers for analysis, we currently expect
        this field to be a multidict that implements a method called `dict_of_lists()`.
        """
        pass

    @property
    @abc.abstractmethod
    def status_code(self):
        """
        Status code as an integer
        """
        pass
