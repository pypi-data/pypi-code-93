import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet, Model_withOldId

from lfl_admin.competitions.models.leagues import Leagues
from lfl_admin.constructions.models.stadiums import Stadiums

logger = logging.getLogger(__name__)


class Stadium_zonesQuerySet(AuditQuerySet):
    pass


class Stadium_zonesManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Stadium_zonesQuerySet(self.model, using=self._db)


class Stadium_zones(AuditModel, Model_withOldId):
    stadium = ForeignKeyProtect(Stadiums)
    league = ForeignKeyProtect(Leagues)

    objects = Stadium_zonesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Сортировка стадионов'
        unique_together = (('stadium', 'league'),)
