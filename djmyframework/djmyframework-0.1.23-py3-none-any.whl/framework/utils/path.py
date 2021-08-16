# -*- coding: utf-8 -*-
# @Time    : 2019-09-03 11:27
# @Author  : xzr
# @File    : path
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :
import os

from framework.utils import mkdirs
from settings import STATIC_ROOT,TEMPLATE_DIR
class GlobalPathCfg(object):

    def __init__(self):
        self.static_folder_name = 'static'

    def get_static_folder_path(self):
        return STATIC_ROOT

    def get_current_url(self, request):
        current_url = '%s%s' % (request.get_host(), request.get_full_path())
        return current_url

    # ****************创建索引SQL保存文件路径**********
    def get_create_index_save_path(self, file_name):
        static_path = self.get_static_folder_path()
        path = static_path + '/sql'
        mkdirs(path)
        path = path + '/' + file_name
        return path

    # **********公告相关*************
    def get_notice_html_template_path(self):
        return '%s/server/notice_template.html' % TEMPLATE_DIR

    def get_template_path(self):
        return os.path.abspath(TEMPLATE_DIR)


    # 获取公告html访问url
    def get_notice_html_url(self, request, file_name):
        return 'http://%s/%s/notice/html/%s' % (request.get_host(), self.static_folder_name, file_name)

    # 获取公告html保存路径
    def get_notice_html_save_path(self, file_name):
        static_path = self.get_static_folder_path()
        path = os.path.join(STATIC_ROOT, 'notice', 'html')
        mkdirs(path)
        path = os.path.join(path, file_name)
        return path

    def get_static_root(self, *child_dir_names):
        the_dir = os.path.join(STATIC_ROOT, *(str(x) for x in child_dir_names))
        mkdirs(the_dir)
        return the_dir

    # **********公告相关  END **********

# w     以写方式打开，
# a     以追加模式打开 (从 EOF 开始, 必要时创建新文件)
# r+     以读写模式打开
# w+     以读写模式打开 (参见 w )
# a+     以读写模式打开 (参见 a )
# rb     以二进制读模式打开
# wb     以二进制写模式打开 (参见 w )
# ab     以二进制追加模式打开 (参见 a )
# rb+    以二进制读写模式打开 (参见 r+ )
# wb+    以二进制读写模式打开 (参见 w+ )
# ab+    以二进制读写模式打开 (参见 a+ )