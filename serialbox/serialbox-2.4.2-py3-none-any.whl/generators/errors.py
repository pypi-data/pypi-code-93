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
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import APIException
from rest_framework import status


class PoolNotFoundException(APIException):
    '''
    Thrown when an inbound request contains a pool machine-name that does
    not match with a configured or active pool.
    '''
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('The Pool machine-name value supplied does not match '
                       'with any known/active Pools in the system.')


class RegionNotFoundException(APIException):
    '''
    Thrown when an inbound request contains a pool machine-name that does
    not match with a configured or active pool.
    '''
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('The Region machine-name value supplied does not match '
                       'with any known/active Regions in the system.')


class NoRegionException(APIException):
    '''
    Thrown when there are no available/active regions available for a pool
    request.
    '''
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('There are no active Sequential Regions available '
                       'to handle the request.')
