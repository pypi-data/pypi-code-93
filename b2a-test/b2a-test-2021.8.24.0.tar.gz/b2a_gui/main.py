#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  main.py
@Date    :  2021/07/23
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QInputDialog, QLabel, QTableView, QGridLayout, \
    QAbstractItemView, QHeaderView

import b2a


class MainView(QWidget):

    def __init__(self):
        super().__init__()
        self._fileAttrs = []
        self.__initView__()

    def __initView__(self):
        self.label0 = QLabel("从bdy:")
        self.label1 = QLabel("到aly:")

        self.edit0 = QLineEdit("/")
        self.edit0.setEnabled(False)
        self.edit1 = QLineEdit("/")

        self.btn0 = QPushButton('UP')
        self.btn0.clicked.connect(self.__upSlot__)
        self.btn1 = QPushButton('RUN')
        self.btn1.clicked.connect(self.__runSlot__)

        self.tableView = QTableView()
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.doubleClicked.connect(self.__inSlot__)

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.label0, 0, 0)
        self.layout.addWidget(self.edit0, 0, 1)
        self.layout.addWidget(self.btn0, 0, 2)
        self.layout.addWidget(self.tableView, 1, 0, 1, 3)
        self.layout.addWidget(self.label1, 2, 0)
        self.layout.addWidget(self.edit1, 2, 1)
        self.layout.addWidget(self.btn1, 2, 2)

        self.setWindowTitle('B2A')
        self.setMinimumSize(400,400)
        self.show()

        self.listPath('/')

    def __upSlot__(self):
        path = self.edit0.text()
        if path == '/':
            return
        array = path.rstrip('/').split('/')
        newPath = '/'.join(array[0:-1])
        self.listPath(newPath)

    def __runSlot__(self):
        pass

    def __inSlot__(self):
        index = self.tableView.currentIndex()
        if not index.isValid():
            return
        item = self._fileAttrs[index.row()]
        if item.isfile:
            return
        self.listPath(item.path)

    def listPath(self, path: str):
        self._fileAttrs = b2a.bdyplat.list(path)
        model = QStandardItemModel()
        for index, item in enumerate(self._fileAttrs):
            model.setItem(index, 0, QStandardItem(item.name))
            model.setItem(index, 1, QStandardItem("文件" if item.isfile else "目录"))
        self.tableView.setModel(model)
        self.edit0.setText(path)
        self.edit1.setText(path)

