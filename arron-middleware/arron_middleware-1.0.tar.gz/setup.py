"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/8/21 下午6:44
"""
#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='arron_middleware',
    version='V1.0',
    description=(
        'scrapy middlewares'
    ),
    long_description=open('README.rst').read(),
    author='arron',
    author_email='862187570@qq.com',
    maintainer='arron',
    maintainer_email='862187570@qq.com',
    license='BSD License',
    packages=['middlewares'],
    platforms=["all"],
    url='https://github.com/WalkOnMars/arron_pypi.git',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
            'scrapy'
        ]
)