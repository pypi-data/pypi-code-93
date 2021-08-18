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

from django.apps import apps
from django.utils.translation import ugettext as _
from rest_framework.exceptions import NotFound
from serialbox.models import Region, Pool, SequentialRegion
from serialbox.flavor_packs import FlavorSaver


def get_all_regions():
    '''
    Returns all of the current models that inherit from
    serialbox.models.Region
    from all of the currently registered
    Django apps.
    '''
    models = apps.get_models()  # get all the region models
    region_models = [model for model in models if issubclass(model, Region)]
    return region_models


def get_all_regions_by_pool(pool, only_active=True):
    '''
    Returns all Region models that are related to the given pool.  This
    includes any Regions that are part of any flavor_packs.

    :param pool: The pool to return regions for.
    :param only_active: Set to True to only return active regions.
    '''
    ret = []
    region_models = get_all_regions()
    kwargs = {'pool': pool}
    if only_active:
        kwargs['active'] = True
    for region in region_models:
        #: :type region: Region
        qs = region.objects.filter(**kwargs).order_by('order')
        if qs.count() > 0:
            ret += list(qs)

    return ret


def get_total_pool_size(pool):
    '''
    Takes the sum of all `remaining` values of each `Region` in a pool and
    returns.
    '''
    size = 0
    regions = get_all_regions_by_pool(pool)
    for region in regions:
        size += region.remaining
    return size


def get_region(pool):
    '''
    Gets the first active Region model in a pool with the lowest order
    number.  Raises an HTTP 404 Not Found if there are no regions.
    '''
    ret = None
    region_models = get_all_regions()

    for region in region_models:
        #: :type region: Region
        qs = region.objects.filter(pool=pool, active=True).order_by('order')
        if qs.count() > 0:
            if not ret:
                ret = qs[0]
            else:
                if qs[0].order < ret.order:
                    ret = qs[0]
    if not ret:
        raise NotFound('SerialBox could not find any active regions for the '
                       'pool with machine name %s.' % pool.machine_name)
    return ret


def get_generator(pool_machine_name):
    try:
        pool = Pool.objects.get(machine_name=pool_machine_name, active=True)
    except Pool.DoesNotExist:
        raise NotFound(
            _('SerialBox could not fine any active pools with the '
              'machine name of %s.' %
              pool_machine_name))
    region = get_region(pool)
    if not isinstance(region, SequentialRegion) and region:
        ret = FlavorSaver.get_generator_by_region(region)
    else:
        from serialbox.generators.sequential import SequentialGenerator
        ret = SequentialGenerator()
    return ret
