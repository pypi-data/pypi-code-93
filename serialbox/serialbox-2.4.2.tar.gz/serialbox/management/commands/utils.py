# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2019 SerialLab Corp.  All rights reserved.
from serialbox.models import Pool, SequentialRegion, BaseModel
from copy import copy

def _get_new_value(value):
    return "%s_%s" % (value, "COPY")

def copy_region(new_pool: Pool, region):
    new_region = copy(region)
    new_region.machine_name = _get_new_value(region.machine_name)
    new_region.readable_name = _get_new_value(region.readable_name)
    new_region.pool = new_pool
    new_region.save()
    return new_region

def copy_pool(pool_machine_name: str) -> None:
    """
    Copies a pool and all of its regions.
    :param pool_machine_name: The pool to copy
    :return: None
    """
    pool_to_copy = Pool.objects.get(machine_name=pool_machine_name)
    new_pool = copy(pool_to_copy)
    new_pool.machine_name = _get_new_value(pool_to_copy.machine_name)
    new_pool.readable_name = _get_new_value(pool_to_copy.readable_name)
    new_pool.save()

    s_regions = getattr(pool_to_copy, "sequentialregion_set", None)
    if s_regions:
        for region in s_regions.all():
            copy_region(new_pool, region)
