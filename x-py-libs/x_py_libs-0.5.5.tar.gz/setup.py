# -*- coding=utf-8 -*-

from distutils.core import setup

from setuptools import setup, find_packages

setup(
    name="x_py_libs",
    version="0.5.5",
    keywords=["pip", "self", "python", "libs"],
    description="self python libs",
    long_description="self python libs",
    license="MIT Licence",

    url="https://github.com/xiaxiazhu119",
    author="xiaxiazhu",
    author_email="xiaxiazhu147@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        'psycopg2', 'pyodbc', 'sqlalchemy',
        'tornado',
        'Flask', 'Flask_Cors', 'Flask_RESTful',
        'redis',
        'six', 'pymediainfo', 'itsdangerous', 'Werkzeug',
        'requests',
        # 'pycrypto',
        'pycryptodome',
        'captcha','graphic-verification-code',
        'mysql_connector_repackaged',
        'pymysql'
    ]
)
