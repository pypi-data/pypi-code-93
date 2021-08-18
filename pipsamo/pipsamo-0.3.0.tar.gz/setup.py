
#!/usr/bin/env python
import re
import os
from setuptools import setup, find_packages

PACKAGE_NAME = 'pipsamo'

reqs = ['']

for _ in range(2):
    try:
        reqs = [
            lambda: open('./requirements.txt', 'r').readlines(),
            lambda: open(os.path.join(f'{PACKAGE_NAME}.egg-info', 'requires.txt'), 'r').readlines(),
        ][_]()
        break
    except:
        pass

# get version
with open(os.path.join('pips', 'constants.py'), 'rt') as consts_file:
    version = re.search(r'__VERSION__ = \'(.*?)\'', consts_file.read()).group(1)

setup(
    name=PACKAGE_NAME,
    version='0.3.0',
    description='Pips Installs Packages Securely',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='samo',
    author_email='thesamogroup@gmail.com',
    url='https://github.com/samocorp/pips',
    packages=['pips'],
    package_data={'pips': ['*.pem']},
    install_requires=reqs,
    license='MIT',
    entry_points={
        'console_scripts': ['pips = pips.__main__:run']
    },
    keywords=[
        'python',
        'pip',
        'pips',
        'security',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
