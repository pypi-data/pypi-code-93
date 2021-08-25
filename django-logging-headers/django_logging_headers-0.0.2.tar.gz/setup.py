# -*-coding:utf-8-*-
from setuptools import setup

setup(
    name='django_logging_headers',
    version='0.0.2',
    author='fcj',
    author_email='709124637@qq.com',
    url='https://www.cnblogs.com/fuchenjie/p/15187593.html',
    description=u'base django you can save headers info to log',
    packages=['django_logging_headers'],
    install_requires=[],
    ong_description=open('README.md').read(),
    entry_points={
        'console_scripts': [
            'jujube=jujube_pill:jujube',
            'pill=jujube_pill:pill'
        ]
    }
)