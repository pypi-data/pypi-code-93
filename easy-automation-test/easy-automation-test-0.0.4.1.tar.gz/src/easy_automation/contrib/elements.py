#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/27

from selenium.webdriver.common.by import By
from appium.webdriver.common.mobileby import MobileBy


class BoundElement:

    def __init__(self, element_location):
        """
        :param element_location: element location path
        """
        self._element_location = element_location


class Xpath(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.XPATH, self._element_location


class Id(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.ID, self._element_location


class LinkText(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.LINK_TEXT, self._element_location


class PartialLinkText(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.PARTIAL_LINK_TEXT, self._element_location


class Name(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.NAME, self._element_location


class TagName(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.LINK_TEXT, self._element_location

class ClassName(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.CLASS_NAME, self._element_location


class CssSelector(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return By.CSS_SELECTOR, self._element_location


class IosPredicate(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return MobileBy.IOS_PREDICATE, self._element_location


class AccessibilityId(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return MobileBy.ACCESSIBILITY_ID, self._element_location


class Image(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return MobileBy.IMAGE, self._element_location


class Custom(BoundElement):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __get__(self, instance, owner):
        return MobileBy.CUSTOM, self._element_location

