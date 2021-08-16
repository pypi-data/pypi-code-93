#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/8/10
from abc import ABC


class Page(ABC):

    def __init__(self, driver):
        self.driver = driver
