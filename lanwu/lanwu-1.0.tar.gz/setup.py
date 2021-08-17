from distutils.core import setup

setup(
    name="lanwu" ,    # 对外我们模块的名字
    version = "1.0",  # 版本号
    description = "这是第一个对外发布的模块，尽做测试使用",  # 描述
    author = "xu",   # 作者
    author_email = "luvletter19@outlook.com",
    py_modules = ["yellow_green.wumailan"]  # 要发布的模块
)


# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """
# @Time    ：2021/8/16 22:04
# @Author  ：xu
# @File    ：setup.py
# @Version ：1.0
# @Function：打包项目
# """
#
# from setuptools import setup, find_packages
#
# with open("README.md", "r", encoding='utf-8') as fh:
#     long_description = fh.read()
#
# setup(name='pyutilitytool',  # 包名 别人安装时就是用此名来按照 如：pip install pyutilitytool
#       version='0.0.1',  # 包的版本号
#       description='employee',  # 包的介绍、概述
#       author='雾霾蓝',  # 包的作者
#       author_email='',  # 邮箱
#       # url='https://github.com/JarvisFree/PyUtilityTool',  # 项目源代码地址 一般的填git地址
#       packages=find_packages(),  # Python导入包的列表 可以find_packages() 来自动收集
#       long_description=long_description,  # 项目的描述 读取README.md文件的信息
#       long_description_content_type="text/markdown",  # 描述文档README的格式 一般md
#       license="GPLv3",  # 开源协议
#       # 这 需要去官网查，在下边提供了许可证连接 或者 你可以直接把我的粘贴走
#       classifiers=[
#           "Programming Language :: Python :: 3",
#           "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
#           "Operating System :: OS Independent"],
#
#       python_requires='>=3.9',  # Python的版本约束
#       # 其他依赖的约束
#       install_requires=[],
#       )
