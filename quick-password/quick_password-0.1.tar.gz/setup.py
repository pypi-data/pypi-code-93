# -*- coding=utf-8 -*-
from os import path
from codecs import open
from setuptools import setup, find_packages


basedir = path.abspath(path.dirname(__file__))

with open(path.join(basedir, 'README.md'), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='quick_password',
    version='0.1',
    url='https://github.com/luxp4588/quick_log.git',
    license='MIT',
    author="python-xp",
    author_email="luxp4588@126.com",
    description="用于快速生成密码",
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms='any',
    packages=["quick_password"],
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
    keywords='password',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)