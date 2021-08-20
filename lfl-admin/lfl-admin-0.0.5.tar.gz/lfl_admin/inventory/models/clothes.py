import logging

from bitfield import BitField

from isc_common.common import undefined
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldIds
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet
from lfl_admin.inventory.models.clothes_type import Clothes_type

logger = logging.getLogger(__name__)


class ClothesQuerySet(BaseRefQuerySet):
    pass


class ClothesManager(BaseRefManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'Актуальность'),  # 1
        ), default=1, db_index=True)

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
        return ClothesQuerySet(self.model, using=self._db)


class Clothes(BaseRef, Model_withOldIds):
    clothes_type = ForeignKeyProtect(Clothes_type)
    props = ClothesManager.props()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            code=undefined,
            defaults=dict(
                name='Неопределенный',
                clothes_type=Clothes_type.unknown(),
            ))
        return res

    objects = ClothesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Одежда'
