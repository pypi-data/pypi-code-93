import logging

from django.db.models import SmallIntegerField, DateField, BigIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId
from isc_common.models.base_ref import BaseRefQuerySet, BaseRefManager, BaseRef
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class MatchdaysQuerySet(BaseRefQuerySet):
    pass


class MatchdaysManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return MatchdaysQuerySet(self.model, using=self._db)


class Matchdays(BaseRef):
    date = DateField(null=True, blank=True)
    tour = SmallIntegerField(null=True, blank=True)
    tournament = ForeignKeyProtect(Tournaments)

    old_tour = BigIntegerField(db_index=True, null=True, blank=True)
    old_tournament_id = BigIntegerField(db_index=True, null=True, blank=True)

    objects = MatchdaysManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Раунды кубкового турнира'
        unique_together = (('tournament', 'tour', 'old_tour', 'old_tournament_id'),)
