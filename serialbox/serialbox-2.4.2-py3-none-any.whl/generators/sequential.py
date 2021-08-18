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
import logging

from serialbox.generators import common

logger = logging.getLogger(__name__)


class SequentialGenerator(common.Generator):
    '''
    The SequentialGenerator class is responsible for generating sequential
    number pool responses that contain a first, last and fulfilled flag
    which indicates whether or not the supplied region was able to fulfill
    the original request.
    '''

    def generate(self, request, response, region, size):
        '''
        Generates an Response model instance and add the number_list
        attribute which contains a list with the first and last number.
        :param request: The inbound HTTP Request
        :param region: The region to use
        :param size: The size of the request
        '''
        logger.debug('Processing sequential request.')
        response.type = 'sequential'
        size = self._enforce_boundaries(response, size, region)
        number_list = [region.state]
        if size > 1:
            number_list.append(region.state + (size - 1))
        region.state = region.state + size
        logger.debug('Number list: %s', number_list)
        self.set_number_list(response, number_list)

    def _enforce_boundaries(self, response, size, region):
        '''
        Makes sure the count does not exceed the amount remaining.
        '''
        remaining_count = region.end - region.state
        logger.debug('Remaining count for region %s = %s', region,
                     remaining_count)
        if size >= remaining_count:
            logger.debug('Size exceeded remaining count.')
            region.active = False
            response.fulfilled = (size == remaining_count)
            size = remaining_count + 1
            response.size_granted = size
        return size
