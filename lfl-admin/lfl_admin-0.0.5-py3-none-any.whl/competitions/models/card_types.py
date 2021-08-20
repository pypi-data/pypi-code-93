import logging

from isc_common.common import undefined
from isc_common.models.base_ref import BaseRefQuerySet, BaseRefManager, BaseRef

logger = logging.getLogger(__name__)


class Card_typesQuerySet(BaseRefQuerySet):
    pass


class Card_typesManager(BaseRefManager):

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
        return Card_typesQuerySet(self.model, using=self._db)


class Card_types(BaseRef):
    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(code=undefined)
        return res

    objects = Card_typesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Тип карточки'
