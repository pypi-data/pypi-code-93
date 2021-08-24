# -*- coding: utf-8 -*-

import ssl
import setuptools

from hagworm import __version__


ssl._create_default_https_context = ssl._create_unverified_context

with open(r'README.md', r'r', encoding=r'utf8') as stream:
    long_description = stream.read()

setuptools.setup(
    name=r'hagworm',
    version=__version__,
    license=r'Apache License Version 2.0',
    platforms=[r'all'],
    author=r'Shaobo.Wang',
    author_email=r'wsb310@gmail.com',
    description=r'Network Development Suite',
    long_description=long_description,
    long_description_content_type=r'text/markdown',
    url=r'https://gitee.com/wsb310/hagworm',
    packages=setuptools.find_packages(),
    package_data={r'hagworm': [r'static/*.*']},
    python_requires=r'>= 3.8',
    install_requires=[
        r'APScheduler==3.7.0',
        r'Jinja2==3.0.1',
        r'Pillow==8.2.0',
        r'PyJWT==2.1.0',
        r'PyYAML==5.4.1',
        r'SQLAlchemy==1.3.24',
        r'WTForms==2.3.3',
        r'aiohttp==3.7.4',
        r'aiomysql==0.0.21',
        r'aioredis==1.3.1',
        r'aiosmtplib==1.1.6',
        r'async-timeout==3.0.1',
        r'cachetools==4.2.2',
        r'cryptography==3.4.7',
        r'fastapi==0.65.1',
        r'gunicorn==20.1.0',
        r'hiredis==2.0.0',
        r'httptools==0.2.0',
        r'loguru==0.5.3',
        r'motor==2.4.0',
        r'aliyun-log-python-sdk==0.6.54',
        r'mq-http-sdk==1.0.3',
        r'ntplib==0.3.4',
        r'numpy==1.20.3',
        r'protobuf==3.17.1',
        r'psutil==5.8.0',
        r'pyahocorasick==1.4.2',
        r'pytest-asyncio==0.15.1',
        r'pytest==6.2.4',
        r'python-multipart==0.0.5',
        r'python-stdnum==1.16',
        r'pyzmq==22.0.3',
        r'qrcode==6.1',
        r'terminal-table==2.0.1',
        r'tornado-jinja2==0.2.4',
        r'tornado==6.1.0',
        r'ujson==4.0.2',
        r'uvicorn==0.13.4',
        r'uvloop==0.15.3;sys_platform!="win32"',
        r'wtforms-tornado==0.0.2',
        r'xlwt==1.3.0',
        r'xmltodict==0.12.0',
    ],
    classifiers=[
        r'Programming Language :: Python :: 3.8',
        r'License :: OSI Approved :: Apache Software License',
        r'Operating System :: POSIX :: Linux',
    ],
    ext_modules=[
        setuptools.Extension(
            r'hagworm.extend.math', [r'./c_extend/math.c']
        ),
    ],
)
