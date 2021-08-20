import logging

from django.db.models import SmallIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, AuditModel
from lfl_admin.competitions.models.matches import Matches
from lfl_admin.competitions.models.players import Players

logger = logging.getLogger(__name__)


class Squads_matchQuerySet(AuditQuerySet):
    pass


class Squads_matchManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Squads_matchQuerySet(self.model, using=self._db)


class Squads_match(AuditModel):
    player = ForeignKeyProtect(Players)
    match = ForeignKeyProtect(Matches)
    number = SmallIntegerField()
    objects = Squads_matchManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Составы команд в конкретных матчах'
