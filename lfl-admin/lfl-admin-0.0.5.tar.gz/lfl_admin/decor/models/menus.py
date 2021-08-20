import logging

from django.db.models import SmallIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefHierarcyManager, BaseRefHierarcyQuerySet
from lfl_admin.decor.models.menu_type import Menu_type

logger = logging.getLogger(__name__)


class MenusQuerySet(BaseRefHierarcyQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class MenusManager(BaseRefHierarcyManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'parent': record.parent.id if record.parent else None,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return MenusQuerySet(self.model, using=self._db)


class Menus(BaseRefHierarcy, Model_withOldId):
    position = SmallIntegerField(null=True, blank=True)
    menu_type = ForeignKeyProtect(Menu_type)
    objects = MenusManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Меню'
