'''
    Copyright 2018 SerialLab, CORP

    This file is part of SerialBox.

    SerialBox is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SerialBox is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with SerialBox.  If not, see <http://www.gnu.org/licenses/>.
'''
from abc import ABCMeta, abstractmethod


class Rule(object):
    '''
    Defines the base class for rules.  Override the execute function
    to implement a custom rule.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError('The execute method must be implemented.')


class PreprocessingRule(Rule):
    '''
    Defines the base class for the pre-processing rules that are executed
    when generators are called during runtime.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, request, pool, region, size):
        raise NotImplementedError('The execute method must be implemented.')


class PostprocessingRule(Rule):
    '''
    Defines the base class for the post-processing rules that are exectued
    when generators are called during runtime.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, request, pool, region, size):
        raise NotImplementedError('The execute method must be implemented.')
