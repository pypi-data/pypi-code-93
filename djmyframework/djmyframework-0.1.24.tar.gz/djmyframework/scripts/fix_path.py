# -*- coding: utf-8 -*-
# @Time    : 2020-07-10 11:46
# @Author  : xzr
# @File    : fix_path
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

import os
import shutil

if __name__ == '__main__':

    dir = os.path.dirname(__file__)
    fix_path_list = ['sdk_center']

    for path in fix_path_list:

        template_file_path = os.path.join(dir, 'templates', path)

        for f in os.listdir(template_file_path):
            old_file_path = os.path.join(template_file_path, f)
            if '-' in f:
                dir_name, file_name = f.split('-', 2)
                new_dir_path = os.path.join(template_file_path, dir_name)
                new_file_path = os.path.join(new_dir_path, file_name)
                if not os.path.isdir(new_dir_path):
                    os.mkdir(new_dir_path)
                if not os.path.isfile(new_file_path):
                    shutil.copyfile(old_file_path, new_file_path)
