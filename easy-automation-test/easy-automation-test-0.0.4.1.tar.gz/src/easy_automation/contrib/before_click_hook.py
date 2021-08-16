#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/8/6
from appium.webdriver.webdriver import WebDriver

BEFORE_CLICK_EVENT = []


def before_click(func):
    """
    this func only have a  param: driver
    :param func:
    :return:
    """
    BEFORE_CLICK_EVENT.append(func)
    return func


def before_click_hook(driver: WebDriver):
    for event in BEFORE_CLICK_EVENT:
        res = event(driver)
        if res:
            before_click_hook(driver)
            break


