# -*- coding: utf-8 -*-

"""
DateTime   : 2021/02/21 16:07
Author     : ZhangYafei
Description: 
"""
from settings import *
import random


class UserAgent:
    def __init__(self):
        self._agent_list = Chrome + FireFox + Opera + UC + Other

    @property
    def random(self):
        return random.choice(self._agent_list)

    @property
    def chrome(self):
        return random.choice(Chrome)

    @property
    def firefox(self):
        return random.choice(FireFox)

    @property
    def uc(self):
        return random.choice(UC)

    @property
    def opera(self):
        return random.choice(Opera)

    @property
    def mobile(self):
        return random.choice(Mobile)
