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
from django.utils.translation import ugettext as _

from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST


class RegionBoundaryException(APIException):

    def __init__(self, detail=None):
        APIException.__init__(self, detail=detail)
        self.status_code = HTTP_400_BAD_REQUEST
        if detail is None:
            self.detail = _('The new region has been defined within the '
                            'start and end values of another region within '
                            'the same pool. '
                            'Check your region configurations.')
