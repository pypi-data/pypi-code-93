import logging

from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldIds
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet
from lfl_admin.inventory.models.clothes import ClothesManager
from lfl_admin.inventory.models.clothes_type import Clothes_type

logger = logging.getLogger(__name__)


class Clothes_viewQuerySet(BaseRefQuerySet):
    pass


class Clothes_viewManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
            'clothes_type_id': record.clothes_type.id,
            'clothes_type__name': record.clothes_type.name,
        }
        return res

    def get_queryset(self):
        return Clothes_viewQuerySet(self.model, using=self._db)


class Clothes_view(BaseRef, Model_withOldIds):
    clothes_type_code = CodeField()
    clothes_type = ForeignKeyProtect(Clothes_type)
    props = ClothesManager.props()

    objects = Clothes_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Одежда'
        db_table = 'inventory_clothes_view'
        managed = False
