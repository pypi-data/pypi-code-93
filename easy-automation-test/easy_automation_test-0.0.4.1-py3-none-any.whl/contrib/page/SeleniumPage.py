#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/8/16
from .page import Page
from ..selenium_mixin import SeleniumMixin


class SeleniumPage(Page, SeleniumMixin):
    """
    Web project create project page should extend this
    abstract page class.
    """
    pass


