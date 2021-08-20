import logging

from isc_common.common import undefined
from isc_common.models.base_ref import BaseRefQuerySet, BaseRefManager, BaseRef

logger = logging.getLogger(__name__)


class Clothes_typeQuerySet(BaseRefQuerySet):
    pass


class Clothes_typeManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Clothes_typeQuerySet(self.model, using=self._db)


class Clothes_type(BaseRef):
    objects = Clothes_typeManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            code=undefined,
            defaults=dict(
                name='Неопределенный',
            ))
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Вид одежды'
