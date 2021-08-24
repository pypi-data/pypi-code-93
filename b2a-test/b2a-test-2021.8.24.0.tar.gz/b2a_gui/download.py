#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  download.py
@Date    :  2021/07/23
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""
import _thread
import threading

import aigpy
from PyQt5.QtWidgets import QWidget, QTableView, QLabel, QGridLayout

import b2a
from b2a.platformImp import FileAttr


class Task(object):
    def __init__(self):
        self.index = 0
        self.fileAttr = None
        self.status = '等待'
        self.isError = False


class TaskManager(object):
    def __init__(self):
        self.tasks = []
        self.waitTasks = []

    def clear(self):
        pass

    def addTask(self, item: FileAttr):
        task = Task()
        task.fileAttr = item
        task.index = len(self.tasks)
        self.tasks.append(task)
        self.waitTasks.append(task)

    def getWaitTask(self) -> Task:
        pass


class LoadThread(threading.Thread):
    def __init__(self, view):
        threading.Thread.__init__(self)
        self.view = view

    def __load__(self, array):
        for item in array:
            if item.isfile:
                self.view.taskManager.addTask(item)
        for item in array:
            if not item.isfile:
                subArray = b2a.bdyplat.list(item.path)
                self.__load__(subArray)

    def run(self):
        print("开始线程：LoadThread")
        self.__load__(self.view.bdyFileAttrs)
        print("退出线程：LoadThread")


class DealThread(threading.Thread):
    def __init__(self, view):
        threading.Thread.__init__(self)
        self.view = view

    def run(self):
        print("开始线程：DealThread")
        while True:
            task = self.view.taskManager.getWaitTask()
            item = task.fileAttr

            localFilePath = b2a.getDownloadPath() + item.path
            uploadFilePath = self.view.aliPath + '/' + item.path[len(self.view.bdyPath):]
            if b2a.aliplat.isFileExist(uploadFilePath):
                b2a.asyncCount.skip += 1
                aigpy.cmd.printInfo(f"[{b2a.asyncCount.index}] 跳过文件: {item.path}")
                continue

            aigpy.cmd.printInfo(f"[{b2a.asyncCount.index}] 迁移文件: {item.path}")
            if aigpy.file.getSize(localFilePath) <= 0:
                check = b2a.bdyplat.downloadFile(item.path, localFilePath)
                if not check:
                    aigpy.cmd.printErr("[错误] 下载失败!")
                    b2a.asyncCount.err += 1
                    continue

            check = b2a.aliplat.uploadFile(localFilePath, uploadFilePath)
            if not check:
                aigpy.cmd.printErr("[错误] 上传失败!")
                b2a.asyncCount.err += 1
            else:
                b2a.asyncCount.success += 1

            aigpy.path.remove(localFilePath)
        print("退出线程：DealThread")


class DownloadView(QWidget):

    def __init__(self):
        super().__init__()
        self.taskManager = TaskManager()
        self.bdyPath = ''
        self.aliPath = ''
        self.bdyFileAttrs = []
        self.__initView__()

    def __initView__(self):
        self.info = QLabel()
        self.status = QLabel()
        self.tableView = QTableView()

        self.layout = QGridLayout(self)
        self.layout.addWidget(self.info, 0, 0)
        self.layout.addWidget(self.tableView, 1, 0)
        self.layout.addWidget(self.status, 2, 0)

        self.hide()

    def updateInfo(self):
        self.info.setText(f"成功：{b2a.asyncCount.success}；失败：{b2a.asyncCount.err}；跳过：{b2a.asyncCount.skip}")

    def start(self, array: [FileAttr], bdyPath: str, aliPath: str):
        self.taskManager.clear()
        self.bdyPath = bdyPath
        self.bdyFileAttrs = array
        self.aliPath = aliPath

        loadThread = LoadThread(self)
        dealThread = DealThread(self)
        loadThread.start()
        dealThread.start()

        self.show()
