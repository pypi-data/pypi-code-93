# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Provide package.'''

from argparse import ArgumentError, ArgumentTypeError


class ArgufyException(ArgumentError):
    '''Provide exception for parser errors.'''


class ArgufyTypeError(ArgumentTypeError):
    '''Provide exception for argument type errors.'''
