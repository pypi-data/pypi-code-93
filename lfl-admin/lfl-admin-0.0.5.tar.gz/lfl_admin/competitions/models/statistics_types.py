import logging

from isc_common.common import undefined
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Statistics_typesQuerySet(BaseRefQuerySet):
    pass


class Statistics_typesManager(BaseRefManager):

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
        return Statistics_typesQuerySet(self.model, using=self._db)


class Statistics_types(BaseRef):
    objects = Statistics_typesManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            code=undefined,
            # priority=0
        )
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Типы турниров'
