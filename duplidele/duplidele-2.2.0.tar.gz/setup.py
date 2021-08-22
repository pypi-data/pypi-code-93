# -*- coding: utf-8 -*-

from setuptools import setup
from codecs import open
from os import path
import re

package_name = "duplidele"

root_dir = path.abspath(path.dirname(__file__))

def _requirements():
    return [name.rstrip() for name in open(path.join(root_dir, 'requirements.txt')).readlines()]

def _test_requirements():
    return [name.rstrip() for name in open(path.join(root_dir, 'test-requirements.txt')).readlines()]

with open(path.join(root_dir, package_name, '__init__.py')) as f:
    init_text = f.read()
    version = re.search(r'__version__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    license = re.search(r'__license__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author = re.search(r'__author__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author_email = re.search(r'__author_email__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    url = re.search(r'__url__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)

assert version
assert license
assert author
assert author_email
assert url

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='duplidele',
    packages=['duplidele'],

    version='2.2.0',

    license='MIT',

    install_requires=_requirements(),
    tests_require=_test_requirements(),

    author='Takao Morita',
    author_email='tmolita077@gmail.com',

    url='https://github.com/taotaotao3/duplidele',

    description='The Duplidele can delete duplicate sentence from your sentence',
    long_description='When you want to delete duplicate sentence from your sentence, Please use duplidele.The first argument is the target sentence, the second argument is the minimum number of characters for the duplicate target, and the third argument is the total number of characters within the entire sentence.',
    keywords='duplicate, delete, sentence',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)