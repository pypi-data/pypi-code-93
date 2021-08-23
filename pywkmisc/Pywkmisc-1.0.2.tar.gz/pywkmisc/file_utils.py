#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


class FileUtils(object):

    def __init__(self, file_path):
        """
        :param file_path:   磁盘文件路径
        """
        self._file_path = file_path
        self._path, self._file_name = os.path.split(self._file_path)
        self._path = os.path.abspath(self._path)
        self._shot_name, self._extension = os.path.splitext(self._file_name)

    def read(self):
        s: dict = {
            'filepath': self.filepath,
            'path': self.path,
            'filename': self.filename,
            'shotname': self.shotname,
            'extension': self.extension,
        }
        return str(s).replace('\'', '"')

    @property
    def filepath(self):
        """获取磁盘文件完整路径，虚拟路径转为完整路径"""
        return '{}{}{}'.format(self._path, os.sep, self.filename)

    @property
    def filesize(self):
        return os.path.getsize(self.filepath)

    @property
    def path(self):
        """获取磁盘文件保存绝对地址"""
        return self._path

    @property
    def filename(self):
        """获取磁盘文件包含扩展名的文件名"""
        return self._file_name

    @property
    def shotname(self):
        """获取磁盘文件不包含扩展名的文件名"""
        return self._shot_name

    @property
    def extension(self):
        """获取磁盘文件的扩展名,包含."""
        return self._extension

    def exists(self):
        """
        判断存放图片的文件夹是否存在
        """
        if self._path is None:
            return False
        return os.path.exists(self._path)

    def makedirs(self):
        """
        判断存放文件夹是否存在,若文件夹不存在就创建
        """
        if self._path is None:
            return
        if not self.exists():
            os.makedirs(self._path)

    def del_file(self):
        """
        删除磁盘文件
        """
        if self._file_path is None:
            return
        if os.path.exists(self._file_path):
            os.remove(self._file_path)


if __name__ == '__main__':
    pass
