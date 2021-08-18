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
from django.apps import apps

from serialbox import models as sb_models
from serialbox.errors import RegionBoundaryException


def check_sequential_region_boundaries(region):
    '''
    Checks all of the regions belonging to the same pool as the supplied Region
    and checks to make sure that the start and end are not within
    the boundaries of another region.

    ## Return ##
    Returns nothing if the boundaries check out fine.  Otherwise it will raise
    a
    '''
    if region.start >= region.end:
        raise RegionBoundaryException(_('The start of the range can not be '
                                        'greater or equal to the end value.'))
    regions = sb_models.SequentialRegion.objects.filter(
        pool=region.pool).exclude(pk=region.pk)
    if regions.count() > 0:
        for current_region in regions:
            if region.start >= current_region.start and \
                    region.start <= current_region.end:
                raise RegionBoundaryException()


def get_region_by_machine_name(machine_name):
    '''
    Searches through all of the models marked as concrete_region
    within all of the loaded SerialBox app and then returns the model with
    the unique machine_name supplied.  Returns the Region model instance or
    None if none is found.

    TODO: set up caching for regions by name once they've been looked up
    '''
    ret = None
    for app in apps.get_app_configs():
        models = app.get_models()
        for model in models:
            if issubclass(model, sb_models.Region):
                try:
                    ret = model.objects.get(machine_name=machine_name)
                    break
                except model.DoesNotExist:
                    pass
    return ret
