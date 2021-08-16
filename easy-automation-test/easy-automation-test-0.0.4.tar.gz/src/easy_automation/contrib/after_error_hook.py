#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/3/15
from functools import wraps

from selenium.common.exceptions import NoSuchElementException, \
    TimeoutException, StaleElementReferenceException
import allure

from easy_automation.utils.custom_logging import Logs

log = Logs(__name__)

AFTER_ERROR_EVENTS = []


def after_error(func):
    """
    define if location element error, will trigger function
    this function will return false or True.
    execute successfully should return True,
    execute failed should return False.
    note: this func should always not error occurred.
    and only have a param: driver
    :param func:
    :return:
    """
    AFTER_ERROR_EVENTS.append(func)
    return func


def after_error_hook(func):

    @wraps(func)
    def wrap(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except (NoSuchElementException, TimeoutException,
                StaleElementReferenceException) as exc:
            for event in AFTER_ERROR_EVENTS:
                res = event(self.driver)
                if res:
                    # use handle_blacklist decorator call func again,
                    # to deal with multiple blacklist display at same time.
                    return after_error_hook(func)(self, *args, *kwargs)
            else:
                allure.attach(self.screenshot(), attachment_type=allure.attachment_type.PNG)
                log.error(f'Element find failed: {exc}')
                raise exc
    return wrap
