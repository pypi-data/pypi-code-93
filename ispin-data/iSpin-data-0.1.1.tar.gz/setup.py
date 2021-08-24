#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.test import test as TestCommand
from io import open
import sys


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)

setup(
    name='iSpin-data',
    version='0.1.1',
    author='Rodrigo Hurtado',
    author_email='rel@romowind.com',
    packages=['ispin_data'],
    package_dir={'ispin_data': 'ispin_data'},
    url='https://github.com/rodrigo087/ispin_data',
    description='Gets iSpin data for a turbine ID.',
    long_description=open('README.rst', encoding='utf-8').read(),
)
