#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  loginModel.py
@Date    :  2021/8/17
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :
"""
import webbrowser

from tidal_gui.view.loginView import LoginView
from tidal_gui.viewModel.viewModel import ViewModel


def __openWeb__():
    webbrowser.open('link.tidal.com', new=0, autoraise=True)


class LoginModel(ViewModel):
    def __init__(self):
        super(LoginModel, self).__init__()
        self.view = LoginView()
        self.view.connectConfirmButton(__openWeb__)
