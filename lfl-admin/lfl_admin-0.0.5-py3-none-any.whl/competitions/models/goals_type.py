import logging

from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRef

logger = logging.getLogger(__name__)


class Goals_typeQuerySet(BaseRefQuerySet):
    pass


class Goals_typeManager(BaseRefManager):

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
        return Goals_typeQuerySet(self.model, using=self._db)


class Goals_type(BaseRef):
    objects = Goals_typeManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Типы голов'
