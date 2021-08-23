#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  __init__.py
@Date    :  2021/07/23
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton

import b2a
from b2a_gui.main import MainView


def login() -> bool:
    if not b2a.loginAli(b2a.config.aliKey):
        return False
    if not b2a.loginBdy(b2a.config.bdyKey):
        return False
    return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not login():
        qmb = QMessageBox()
        qmb.setWindowTitle('错误')
        qmb.setText('<h2>登录失败</h2>')
        qmb.setInformativeText('请先正确登录阿里云与百度云！')
        qmb.addButton(QPushButton('确定', qmb), QMessageBox.YesRole)
        qmb.open()
    else:
        ex = MainView()
    sys.exit(app.exec_())
