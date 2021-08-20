import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRef
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class MatchesQuerySet(BaseRefQuerySet):
    pass


class MatchesManager(BaseRefManager):

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
        return MatchesQuerySet(self.model, using=self._db)


class Matches(BaseRef):
    tournament = ForeignKeyProtect(Tournaments)
    objects = MatchesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Матчи'
