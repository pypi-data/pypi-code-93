# -*- coding: utf-8-*-
from setuptools import setup, find_packages
setup(
    # 以下为必需参数
    name='scrapy-scheduler-rabbitmq',  # 模块名
    version='1.1.8',  # 当前版本
    description='Rabbitmq for Scrapy Distributed scraping',  # 简短描述
    author='sunny5156',
    author_email='sunny5156@qq.com',
    license='MIT',
    url='https://github.com/bigkennel/scrapy-scheduler-rabbitmq',
    install_requires=[
        'pika',
        'Scrapy>=0.14'
    ],
    packages=['scrapy_scheduler_rabbitmq'],
    package_dir={'': 'src'}
)
