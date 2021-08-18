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

from copy import copy
from django.contrib.admin import ModelAdmin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.translation import ugettext as _
from django.db import transaction

def copy_pool(
        modeladmin: ModelAdmin,
        request: HttpRequest,
        queryset: QuerySet
):
    for pool in queryset:
        with transaction.atomic():
            new_pool = copy(pool)
            new_pool.id = None
            new_pool.readable_name = '%s_COPY' % pool.readable_name
            new_pool.machine_name = '%s_COPY' % pool.machine_name
            new_pool.save()
            for region in pool.listbasedregion_set.all():
                new_region = copy(region)
                new_region.id = None
                new_region.pool = new_pool
                new_region.readable_name = '%s_COPY' % region.readable_name
                new_region.machine_name = '%s_COPY' % region.machine_name
                new_region.file_id = None
                new_region.save()

copy_pool.short_description = _('Copy Selected Pools')