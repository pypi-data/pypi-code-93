#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
__author__ = "kuser"

from setuptools import setup, find_packages

# with open("README.md", "r") as fh:
# long_description = fh.read()

setup(name='k_parse_tool',
      version='0.0.9',  # 版本号
      description='parse and extract data from HTML',  # 包的介绍
      author='kuser',  # 作者 就是我啦～
      author_email='xjliu@kland.com.cn',  # 你的邮箱
      url='http://xjliu123@192.168.1.200/v3_personal/k-parse-tools.git',  # 项目地址，一般的填git地址 也可以是任意可用的url 不过我喜欢使用 git
      packages=find_packages(),  # Python导入包的列表，我们使用find_packages() 来自动收集
      long_description='parse and extract data from HTML',  # 项目的描述 一般是 string 上文中定义了它
      long_description_content_type="text/markdown",  # 描述文档 README 的格式 一般我喜欢MD. 也可以是你喜欢的其他格式 支不支持我就不知道了～ 估计HTML 是支持的
      license="GPLv3",  # 开源协议
      # 这 需要去官网查，在下边提供了许可证连接 或者 你可以直接把我的粘贴走
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: OS Independent"],

      python_requires='>=3.6.3',  # Python 的版本约束
      # 其他依赖的约束
      install_requires=[
          "pdfplumber>=0.5.24",
          "python-docx>=0.8.10",
          "regex>=2020.11.13",
          "pandas>=1.1.5",
          "beautifulsoup4>=4.9.3",
          "numpy>=1.18.0",
          "PyDocX>=0.9.10",
      ]
      )
