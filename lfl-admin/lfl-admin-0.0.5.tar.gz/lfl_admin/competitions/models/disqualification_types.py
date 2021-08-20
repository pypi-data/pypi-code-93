import logging

from isc_common.common import unknown
from isc_common.models.base_ref import BaseRefManager, BaseRef, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Disqualification_typeQuerySet(BaseRefQuerySet):
    pass


class Disqualification_typeManager(BaseRefManager):

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
        return Disqualification_typeQuerySet(self.model, using=self._db)


class Disqualification_types(BaseRef):
    objects = Disqualification_typeManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(code=unknown)
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Типы дисквалификаций'
