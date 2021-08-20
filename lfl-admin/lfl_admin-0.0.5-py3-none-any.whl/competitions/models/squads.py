import logging

from django.db.models import DateField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class SquadsQuerySet(AuditQuerySet):
    pass


class SquadsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return SquadsQuerySet(self.model, using=self._db)


class Squads(AuditModel):
    tournament = ForeignKeyProtect(Tournaments)
    player = ForeignKeyProtect(Players)
    club = ForeignKeyProtect(Clubs)
    included = DateField()
    deducted = DateField(null=True, blank=True)

    objects = SquadsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Составы команд'
