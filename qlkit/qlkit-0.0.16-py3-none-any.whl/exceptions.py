#!/usr/bin/env python
# -*- coding: utf-8 -*-


class PyKitError(Exception):
    """PyKit Exception"""
    pass


class InternalError(PyKitError):
    """
    service internal error
    """
    pass
