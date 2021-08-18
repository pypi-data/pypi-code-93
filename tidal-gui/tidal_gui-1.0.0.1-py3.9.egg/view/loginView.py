#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  loginView.py
@Date    :  2021/04/30
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *

from tidal_gui.control.checkBox import CheckBox
from tidal_gui.control.framelessWidget import FramelessWidget
from tidal_gui.control.label import Label
from tidal_gui.control.layout import createHBoxLayout
from tidal_gui.control.lineEdit import LineEdit
from tidal_gui.control.pushButton import PushButton
from tidal_gui.style import ButtonStyle


class LoginView(FramelessWidget):
    viewWidth = 650
    viewHeight = 400
    logoWidth = 300

    def __init__(self):
        super(LoginView, self).__init__()
        self.setFixedSize(self.viewWidth, self.viewHeight)
        self.__initView__()

    def __initAccountTab__(self):
        self._deviceCodeEdit = LineEdit()
        self._confirmBtn = PushButton("LOGIN", ButtonStyle.Primary)

        grid = QGridLayout()
        grid.setSpacing(15)
        grid.setRowStretch(0, 1)

        grid.addLayout(createHBoxLayout([Label("DeviceCode"), self._deviceCodeEdit]), 1, 0, 1, 2)
        grid.setRowStretch(3, 1)
        grid.addWidget(self._confirmBtn, 5, 0, 1, 2)
        grid.setRowStretch(6, 1)

        widget = QWidget()
        widget.setLayout(grid)
        return widget

    def __initProxyTab__(self):
        self._enableProxyCheck = CheckBox('')
        self._proxyHostEdit = LineEdit()
        self._proxyPortEdit = LineEdit()
        self._proxyUserEdit = LineEdit()
        self._proxyPwdEdit = LineEdit()

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setRowStretch(0, 1)
        grid.addWidget(Label("HttpProxy"), 1, 0)
        grid.addWidget(self._enableProxyCheck, 1, 1)
        grid.addWidget(Label("Host"), 2, 0)
        grid.addWidget(self._proxyHostEdit, 2, 1)
        grid.addWidget(Label("Port"), 3, 0)
        grid.addWidget(self._proxyPortEdit, 3, 1)
        grid.addWidget(Label("UserName"), 4, 0)
        grid.addWidget(self._proxyUserEdit, 4, 1)
        grid.addWidget(Label("Password"), 5, 0)
        grid.addWidget(self._proxyPwdEdit, 5, 1)
        grid.setRowStretch(6, 1)

        widget = QWidget()
        widget.setLayout(grid)
        return widget

    def __initView__(self):
        icon = Label()
        icon.setFixedSize(self.logoWidth, self.viewHeight)
        icon.setStyleSheet("QLabel{background-color:rgb(0,0,0);}")
        icon.setPixmap(QPixmap("./tidal_gui/resource/svg/Down.svg"))
        icon.setAlignment(Qt.AlignCenter)

        tab = QTabWidget(self)
        tab.addTab(self.__initAccountTab__(), "LOGIN")
        tab.addTab(self.__initProxyTab__(), "PROXY")
        tab.setFixedWidth(self.viewWidth - self.logoWidth - 60)

        self.hideMaxWindowButton()
        self.hideMinWindowButton()
        self.setValidMoveWidget(icon)

        grid = self.getGrid()
        grid.setSpacing(15)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.addWidget(icon)
        grid.addWidget(tab, 0, 1, Qt.AlignCenter)

    def setDeviceCode(self, text):
        self._deviceCodeEdit.setText(text)

    def enableHttpProxy(self) -> bool:
        return self._enableProxyCheck.isChecked()

    def getProxyInfo(self) -> dict:
        infos = {'host': self._proxyHostEdit.text(), 'port': self._proxyPortEdit.text(),
                 'username': self._proxyUserEdit.text(), 'password': self._proxyPwdEdit.text()}
        return infos

    def connectConfirmButton(self, func):
        self._confirmBtn.clicked.connect(func)

    def enableConfirmButton(self, enable):
        self._confirmBtn.setEnabled(enable)

    def showErrMessage(self, text: str):
        qmb = QMessageBox(self)
        qmb.setWindowTitle('Error')
        qmb.setIcon(QMessageBox.Warning)
        qmb.setText(text)
        qmb.addButton(QPushButton('OK', qmb), QMessageBox.YesRole)
        qmb.open()
