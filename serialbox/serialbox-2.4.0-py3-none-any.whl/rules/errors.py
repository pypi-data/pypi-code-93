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
from rest_framework.exceptions import APIException


class RuleError(APIException):

    def __init__(self, detail=None):
        APIException.__init__(self, detail)


class SizeLimitRuleError(RuleError):
    '''
    Raised when a request size exceeds that which the pool can handle from
    the current region.
    '''
    pass


class ThresholdLimitRuleError(RuleError):
    '''
    Raised if the defined threshold for a Pool is less than the amount of
    numbers requested.
    '''
    pass


class InactiveRuleError(RuleError):
    '''
    Raised when a request is made against an inactive *Pool*.
    '''
    pass
