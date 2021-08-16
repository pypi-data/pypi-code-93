#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/21

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='easy-automation-test',
    version='0.0.4',
    author='jameszhang',
    author_email='18373230129@163.com',
    description='Easy to create a web, mobile or api automation test project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['automation test', 'appium', 'web', 'mobile', 'api'],
    url="https://github.com/zhangjiapeng23/easy_automation_test",
    project_urls={
        "Bug Tracker": "https://github.com/zhangjiapeng23/easy_automation_test/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests>=2.26.0',
        'selenium>=3.141.0',
        'allure-pytest>=2.9.43',
        'PyYAML>=5.4.1',
        'Faker>=8.10.1',
        'Appium-Python-Client>=1.2.0',
        'pytest-xdist>=2.3.0'
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'easy-automation=easy_automation.utils.command_parser:command_parser'
        ]
    }
)