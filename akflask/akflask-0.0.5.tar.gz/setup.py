#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Kuture
# Mail: kuture@163.com
# Blog: http://www.kuture.com.cn
# Created Time:  2021-8-12 12:00:00
#############################################


from setuptools import setup, find_packages

setup(
    name = "akflask",
    version = "0.0.5",
    keywords = ("pip", "AKFlask","flask", "autoflask", "kuture"),
    description = "Function time calculator",
    long_description = "自动生成flask项目，生成的项目中带有日志管理，蓝图模式等，方便快速上手。",
    license = "MIT Licence",

    url = "https://gitee.com/AustinKuture/akflask.git",
    author = "Kuture",
    author_email = "kuture@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['flask']
)