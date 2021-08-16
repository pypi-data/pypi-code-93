"""setuptools installation script"""
import io
import sys
from os import path

from setuptools import setup, find_packages


with io.open(path.join(path.abspath(path.dirname(__file__)), 'README.md'),
             encoding='utf-8') as readme:
    LONG_DESCRIPTION = readme.read()

if sys.version_info[0] == 2:
    python2_or_3_deps = ['importlib-metadata==2.1.1', 'decorator==4.4.2']
    python2_or_3_test_deps = ['pytest==4.6.11', 'pytest-mock==1.13.0', 'mock==3.0.5']
elif sys.version_info[0] == 3:
    python2_or_3_deps = []
    python2_or_3_test_deps = ['pytest-mock', 'mock']
    if sys.version_info[1] == 5:
        python2_or_3_deps = ["boto3==1.16.63"]
        python2_or_3_test_deps.insert(0, "pytest==6.1.2")
        python2_or_3_test_deps.append('importlib-metadata==2.1.1')
    else:
        python2_or_3_test_deps.insert(0, "pytest")


setup(
    name='lastpass-aws-login',
    version="0.1.6",
    description='Tool for using AWS CLI with LastPass SAML',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author="Pasi Niemi",
    author_email='pasi.niemi@nitor.com',
    url='https://github.com/NitorCreations/lastpass-aws-login',
    license='GPLv3',
    keywords='lastpass aws awscli boto3',
    packages=['lastpass_aws_login'],
    setup_requires=["pytest-runner"],
    install_requires=[
        'threadlocal-aws==0.10',
        'requests>=2.22.0"',
        'future',
    ] + python2_or_3_deps,
    entry_points={
        'console_scripts': [
            'lastpass-aws-login=lastpass_aws_login.main:main'
        ]
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    tests_require=[
        "requests-mock==1.8.0",
        "pytest-cov==2.11.1",
    ] + python2_or_3_test_deps,
    test_suite="tests",
)
