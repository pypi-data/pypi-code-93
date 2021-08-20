import logging

from django.db.models import SmallIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldId
from isc_common.models.audit_ex import AuditModelEx
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class KeepersQuerySet(AuditQuerySet):
    pass


class KeepersManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return KeepersQuerySet(self.model, using=self._db)


class Keepers(AuditModelEx, Model_withOldId):
    club = ForeignKeyProtect(Clubs)
    goals = SmallIntegerField()
    match = ForeignKeyProtect(Calendar)
    player = ForeignKeyProtect(Players)
    tournament = ForeignKeyProtect(Tournaments)

    objects = KeepersManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Хранение пропущенных вратарями голов (мячей)'
        # unique_together = (('match', 'tournament', 'player'),)
