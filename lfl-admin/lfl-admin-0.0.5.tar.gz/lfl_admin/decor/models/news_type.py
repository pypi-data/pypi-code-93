import logging

from isc_common.common import undefined
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class News_typeQuerySet(BaseRefQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class News_typeManager(BaseRefManager):

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
        return News_typeQuerySet(self.model, using=self._db)


class News_type(BaseRef):
    objects = News_typeManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(code=undefined)
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Типы банеров'
