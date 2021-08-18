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
import six
from abc import ABCMeta, abstractmethod

from django.db.models import Q

from serialbox.generators import logger, errors
from serialbox.rules import get_preprocessing_rules, get_postprocessing_rules
from serialbox.models import Pool, SequentialRegion, Response
from serialbox.discovery import get_region


@six.add_metaclass(ABCMeta)
class Generator(object):
    '''
    Base class for all pool generators.
    '''

    def get_response(self, request, size, pool, region=None):
        '''
        First gets a Pool reference, then determines the proper region to
        use.  After that initial logic is complete, the generate function
        will be executed.  Will raise a Pool or Region DoesNotExist exception
        if the requested Pool/Region can not be found.
        '''
        self.pool = self._get_pool(request, pool)
        if region:
            region = self._get_region(self.pool, region)
        else:
            region = get_region(self.pool)
        logger.debug('Using region %s', region)
        response = Response(region=str(region.machine_name),
                            pool=str(region.pool.machine_name),
                            size_granted=size, fulfilled=True,
                            remote_host=request.get_host())
        self._execute_pre_processing_rules(request, size, self.pool, region)
        self.generate(request, response, region, size)
        self._execute_post_processing_rules(request, response,
                                            size, self.pool, region)
        region.save()
        return response

    @abstractmethod
    def generate(self, request, response, region, size):
        '''
        Override for generation.
        '''
        raise NotImplementedError()

    def __init__(self):
        # load pre and post processing rules from the configuration file
        self.preprocessing_rules = \
            get_preprocessing_rules(self,
                                    self.get_settings_module())
        self.postprocessing_rules = \
            get_postprocessing_rules(self,
                                     self.get_settings_module())

    def get_settings_module(self):
        '''
        Returns the default settings module to use during initialization.
        Override this to provide the default pre and post processing rules
         configuration for your Generator.
        :return: None
        '''
        return None

    def _get_pool(self, request, pool):
        '''
        Returns a pool instance based on the machine name or primary key
        of the pool.  Override to provide custom behavior.
        '''
        try:
            kwargs = {"pk": pool} if isinstance(pool, int) else \
                {"machine_name": pool}
            kwargs['active'] = True
            pool = Pool.objects.get(**kwargs)
            return pool
        except Pool.DoesNotExist:
            raise errors.PoolNotFoundException

    def _get_region(self, pool_instance, region_id):
        '''
        Returns a Region instance from the supplied pool_instance.  Cascades
        through the different types of regions in the following order:
            *    SequentialRegion
            *    RandomRegion
            *    ListRegion
        '''
        try:
            SequentialRegion.objects.get(machine_name=region_id)
        except SequentialRegion.DoesNotExist:
            # TODO: cascade to other types of regions when implemented
            raise

    def _determine_sequential_region(self, pool, size):
        '''
        Grabs the first available region that is active or raises a
        serialbox.pools.generators.errors.NoRegionException.
        :param pool: The pool to get the regions for
        :param size: The size of the request
        :return: Returns a Region model.
        '''
        regions = SequentialRegion.objects.filter(
            Q(active=True) &
            Q(pool=pool)).order_by('-order')
        if regions.count() == 0:
            raise errors.NoRegionException()
        return regions[0]

    def _execute_pre_processing_rules(self, request, size, pool, region):
        '''
        Gets the preprocessing rules defined in the settings and executes them.
        '''
        for rule in self.preprocessing_rules:
            rule.execute(request, pool, region, size)

    def _execute_post_processing_rules(self, request, response,
                                       size, pool, region):
        '''
        Gets the post-processing rules defined in the settings and executes
        them in order.
        '''
        for rule in self.postprocessing_rules:
            # TODO: add post processing rules
            pass

    def set_number_list(self, response, number_list):
        '''
        Set the number list attribute of the response object by calling this.
        This must be executed in order to return numbers in the response.
        '''
        setattr(response, 'number_list', number_list)
