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
# Copyright 2018 SerialLab Corp.  All rights reserved.

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
# Copyright 2018 SerialLab Corp.  All rights reserved.
from django.utils.translation import gettext as _
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, ContentType
from django.db.utils import IntegrityError
from serialbox import models

class Command(BaseCommand):
    help = _(
        'Loads default groups into the database.'
    )

    def handle(self, *args, **options):
        ct = ContentType.objects.get_for_model(models.Pool)
        pool_allocate, created = Permission.objects.get_or_create(
            codename='allocate_numbers',
            content_type=ct
        )
        if created:
            pool_allocate.name='Can allocate numbers'
            pool_allocate.save()

        group = Group.objects.get_or_create(
            name='Pool API Access'
        )[0]
        allocate_group = Group.objects.get_or_create(
            name='Allocate Numbers Access'
        )[0]
        self._add_permission(allocate_group, pool_allocate)
        self._add_permission(group,
           pool_allocate
        )
        self._add_permission(group,
            Permission.objects.get(codename='add_pool')
        )
        self._add_permission(group,
            Permission.objects.get(codename='change_pool')
        )
        self._add_permission(group,
            Permission.objects.get(codename='delete_pool')
        )
        self._add_permission(group,
            Permission.objects.get(codename='add_sequentialregion')
        )
        self._add_permission(group,
            Permission.objects.get(codename='change_sequentialregion')
        )
        self._add_permission(group,
            Permission.objects.get(codename='delete_sequentialregion')
        )
        for perm in group.permissions.all():
            print(perm.name)

    def _add_permission(self, group: Group, permission: Permission):
        try:
            group.permissions.add(permission)
        except IntegrityError:
            print('Permission %s already exists' % permission.name)
