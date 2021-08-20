import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldId
from isc_common.models.audit_ex import AuditModelEx
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class AssistsQuerySet(AuditQuerySet):
    pass


class AssistsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return AssistsQuerySet(self.model, using=self._db)


class Assists(AuditModelEx, Model_withOldId):
    club = ForeignKeyProtect(Clubs)
    match = ForeignKeyProtect(Calendar)
    player = ForeignKeyProtect(Players)
    tournament = ForeignKeyProtect(Tournaments)

    objects = AssistsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            club=Clubs.unknown(),
            match=Calendar.unknown(),
            player=Players.unknown(),
            tournament=Tournaments.unknown()
        )
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Голевые пасы в сыгранных матчах. Другое название игрока: ассистент.'
