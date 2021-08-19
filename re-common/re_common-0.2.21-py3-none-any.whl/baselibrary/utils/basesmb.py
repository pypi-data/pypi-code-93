# -*- coding: utf-8 -*-
# @Time    : 2020/11/27 16:38
# @Author  : suhong
# @File    : smb_test.py
# @Software: PyCharm
#!/usr/local/bin/python3


import fs.smbfs
from re_common.baselibrary.utils.basedir import BaseDir


class BaseSmb(object):

    def __init__(self, host=None, username=None, password=None):
        self.conn = None
        self.host = host
        self.username = username
        self.password = password

    def set_default(self):
        """
        调用该函数默认链接177
        :return:
        """
        self.host = "192.168.31.177"
        self.username = "administrator"
        self.password = "vip-812"

    def connect(self):
        """
        设置用户名 密码 进行连接
        :return:
        """
        self.conn = fs.smbfs.SMBFS(host=self.host, username=self.username, passwd=self.password)


    def close(self):
        # 关闭链接
        self.conn.close()

    def get_gen_dir(self):
        """
        获取根目录下的文件名
        :return:
        """
        for g in self.conn.listdir(""):
            yield g

    def is_exists(self, pathdir):
        """
        目录是否存在
        :param sPth:
        :return:
        """
        return self.conn.exists(pathdir)

    def is_dir(self, pathdir):
        """
        是否是目录
        :param sPth:
        :return:
        """
        return self.conn.isdir(pathdir)

    def is_file(self, pathfile):
        """
        是否是文件
        :param sPth:
        :return:
        """
        return self.conn.isfile(pathfile)

    def create_dir(self, pathdir):
        """
        创建目录 该方法可以创建多级目录
        :param pathdir:
        :return:
        """
        if not self.is_dir_exists(pathdir):
            self.conn.makedirs(pathdir)

    def get_file_size(self,path):
        """
        获取文件大小
        :param path:
        :return:
        """
        size = 0
        size +=self.conn.getsize(path)
        return size

    def download_file(self,srcpath,dstpath):
        """
        下载smb服务器文件到本地
        :param srcpath:本地文件
        :param dstpath: 服务器文件
        :return:
        """
        BaseDir.create_dir(srcpath)
        with open(dstpath, 'wb') as write_file:
            self.conn.download(srcpath,write_file)

    def upload_file(self,srcpath,dstpath):
        """
        上传本地文件到smb服务器文件
        :param srcpath:本地文件
        :param dstpath: 服务器文件
        :return:
        """
        self.create_dir(dstpath)
        with open(srcpath, 'rb') as read_file:
            self.conn.upload(dstpath,read_file)


    def copy_file_to_file_smb(self,filePath, tarPath,overwrite=False):
        """
        该方法只适合smb服务器地址到smb服务器地址
        :param filePath:  文件路径
        :param tarDirPath: 输出文件路径
        :return:
        """
        assert self.is_exists(filePath), FileNotFoundError("需要copy的文件不存在")
        assert self.conn.isfile(filePath), FileNotFoundError("需要copy的不是一个文件")

        self.conn.copy(filePath,tarPath,overwrite=overwrite)

    def copy_dir_to_dir_smb(self, oldDir, newDir, moudle=0):
        """
        该方法只适合smb服务器地址到smb服务器地址
        olddir和newdir都只能是目录，且newdir必须不存在
        :param oldDir:
        :param newDir:
        :return:
        """
        assert self.is_exists(oldDir), IsADirectoryError(oldDir + "目录不存在")
        assert not self.is_exists(newDir), IsADirectoryError(newDir + "目录存在")
        self.conn.copydir(oldDir, newDir)

    def move_file_to_file_smb(self,src_path, dst_path, overwrite=False):

        assert self.is_exists(src_path), FileNotFoundError("需要move的文件不存在")
        assert self.is_file(dst_path), FileNotFoundError("需要move的不是一个文件")
        self.conn.move(src_path, dst_path, overwrite=overwrite)

    def move_dir_to_dir_smb(self, oldDir, newDir, moudle=0):
        """
        该方法只适合smb服务器地址到smb服务器地址
        olddir和newdir都只能是目录，且newdir必须不存在
        :param oldDir:
        :param newDir:
        :return:
        """
        assert self.is_exists(oldDir), IsADirectoryError(oldDir + "目录不存在")
        assert not self.is_exists(newDir), IsADirectoryError(newDir + "目录存在")
        self.conn.movedir(oldDir, newDir)


    def delete_dir(self, dirpath):
        """
        递归删除smb服务器文件夹
        :param dirpath:
        :return:
        """
        assert self.is_file(dirpath), FileExistsError("该目录是个文件")

        self.conn.removetree(dirpath)

    def delete_file(self,filepath):
        """
       删除smb服务器文件
       :param dirpath:
       :return:
       """
        assert not self.is_file(filepath), FileNotFoundError("该路径不是个文件")

        self.conn.remove(filepath)







# if __name__ == '__main__':
    # bs = BaseSmb()
    # bs.set_default()
    # bs.connect()
    # print(bs.delete_dir("down_data/test.txt"))