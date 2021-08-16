# -*- coding: utf-8 -*-

import os
import shutil
import sys

import setuptools

if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    if os.system("twine check dist/*"):
        print("twine check failed. Packages might be outdated.")
        print("Try using `pip install -U twine wheel`.\nExiting.")
        sys.exit()
    os.system("twine upload dist/*")
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('djmyframework.egg-info')
    sys.exit()

long_description = open('./README.md').read()
from djmyframework import __version__
install_requires = [l.strip() for l in open('./requirements.txt').readlines() if l.strip()]
setuptools.setup(
        name="djmyframework",  # 包的分发名称，使用字母、数字、_、-
        version=__version__,  # 版本号, 版本号规范：https://www.python.org/dev/peps/pep-0440/
        author="xzregg",  # 作者名字
        author_email="xzregg@gmail.com",  # 作者邮箱
        description="django myframework",  # 包的简介描述
        long_description=long_description,  # 包的详细介绍(一般通过加载README.md)
        long_description_content_type='text/markdown',  # 和上条命令配合使用，声明加载的是markdown文件
        url="https://github.com/xzregg/dj_myframework.git",  # 项目开源地址，我这里写的是同性交友官网，大家可以写自己真实的开源网址
        packages=setuptools.find_packages(exclude=['tests*']),
        # 如果项目由多个文件组成，我们可以使用find_packages()自动发现所有包和子包，而不是手动列出每个包，在这种情况下，包列表将是example_pkg
        classifiers=[  # 关于包的其他元数据(metadata)
                "Programming Language :: Python :: 3",  # 该软件包仅与Python3兼容
                "License :: OSI Approved :: MIT License",  # 根据MIT许可证开源
                "Operating System :: OS Independent",  # 与操作系统无关
        ],
        include_package_data=True,
        install_requires=install_requires,  # 依赖的包
        python_requires='>=3.6',
        scripts=['djmyframework/scripts/syncdb.sh'],
        entry_points={
                'console_scripts': [
                        'djmyframework_init = djmyframework.scripts.init:init_djframework',
                        'mysupervisorctl = djmyframework.mysupervisorctl:main'
                ],
        },
)
