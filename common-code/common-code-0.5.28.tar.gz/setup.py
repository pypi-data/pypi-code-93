# coding=utf-8

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='common-code',

    version="0.5.28",
    description=(
        ''

    ),
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    author='FengJP',
    author_email='852497515@qq.com',
    maintainer='FengJP',
    maintainer_email='852497515@qq.com',
    license='MIT License',
    packages=find_packages(),
    platforms=["ubuntu", 'windows'],
    url='http://git.runjian.com:18080/FengJingPing/common',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'Django',
        'djangorestframework',
        'CMRESHandler',
        'requests',
        'gunicorn',
        'paho-mqtt',
        'pika',
    ]
)
