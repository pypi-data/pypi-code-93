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
from serialbox import discovery
from serialbox.rules import errors, common, logger


class SizeLimitRule(common.PreprocessingRule):
    '''
    A preprocessing rule to enforce that the size requested is not larger
    than either the number of numbers left in the current pool or greater
    than the defined threshold for the pool.
    '''

    def execute(self, request, pool, region, size):
        return self._check_remaining(region, size)

    def _check_remaining(self, region, size):
        logger.info('Checking pool %s against the requested size of %s',
                    str(region.pool), size)
        remaining = discovery.get_total_pool_size(region.pool)
        if size > remaining:
            raise errors.SizeLimitRuleError(
                'The requested size is '
                'greater than the amount of numbers remaining within the '
                'active regions in "pool" %s' % region.pool)
        return True


class RequestThresholdLimitRule(common.PreprocessingRule):
    '''
    A preprocessing rule to enforce that the request threshold defined on the
    current pool is not exceeded by the request size.  This prevents unusually
    large requests from accidentally or maliciously depleting the
    system of numbers.  This rule is implemented by default in the settings
    and must be disabled by removing it from your django settings file by
    using the GENERATOR_PREPROCESSING_RULES setting.
    '''

    def execute(self, request, pool, region, size):
        return self._check_threshold(pool, size)

    def _check_threshold(self, pool, size):
        logger.info('Checking pool threshold of pool %s for size %s', pool,
                    size)
        if size > pool.request_threshold and pool.request_threshold > 0:
            raise errors.ThresholdLimitRuleError(
                'The request threshold of %s has '
                'been exceeded by the request size of %s' %
                (pool.request_threshold, size))
        return True


class ActiveRule(common.PreprocessingRule):
    '''
    Will raise an exception of the requested pool or region is not marked
    as active.
    '''

    def execute(self, request, pool, region, size):
        if not pool.active or not region.active:
            raise errors.InactiveRuleError(
                'The Pool or Region requested is currently not marked as '
                'active in the system. Pool {0}, Region {1}'.format(pool,
                                                                    region))
