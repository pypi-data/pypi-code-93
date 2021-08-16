#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/8/13
from .page import Page
from ..appium_mixin import AppiumMixin


class AppiumPage(Page, AppiumMixin):
    """
    Appium project create project page should extend this
    abstract page class.
    """
    pass
