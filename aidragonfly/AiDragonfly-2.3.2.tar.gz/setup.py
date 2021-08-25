import codecs
import os
import sys
import io
from shutil import rmtree

try:
    from setuptools import find_packages, setup, Command
except:
    from distutils.core import setup


with open("README.rst", "r",encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

NAME = "AiDragonfly"

DESCRIPTION = "AiDragonfly 是爱其科技推出的python编程包，和ONEBOT主控、智能积木主控深度融合，和手机端拖块编程 Dragonfly 一脉相承."

KEYWORDS = "AiDragonfly 是支持ONEBOT主控的python编程包"

AUTHOR = "Beijing IQI Technology Co., LTD"

AUTHOR_EMAIL = "liumingming@iqi-inc.com"

URL = "https://gitee.com/beijing-aiqi/ai-dragonfly.git"

VERSION = "2.3.2"

LICENSE = "MIT"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    install_requires = [
    'bleak >=0.12.1',
    ],
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=find_packages(),
    package_data = {
        # 任何包中含有.dll文件，都包含它
        '': ['*.dll','*.pyd'],
    },
)