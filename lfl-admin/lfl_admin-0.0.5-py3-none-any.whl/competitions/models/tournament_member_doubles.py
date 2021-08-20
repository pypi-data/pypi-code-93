import logging

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel, Model_withOldId
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class Tournament_member_doublesQuerySet(AuditQuerySet):
    pass


class Tournament_member_doublesManager(AuditManager):
    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Tournament_member_doublesQuerySet(self.model, using=self._db)


class Tournament_member_doubles(AuditModel, Model_withOldId):
    club = ForeignKeyProtect(Clubs, related_name='Tournament_member_club')
    club_double = ForeignKeyProtect(Clubs, related_name='Tournament_member_club_double', null=True, blank=True)
    tournament_double = ForeignKeyProtect(Tournaments, related_name='Tournament_member_doubles_tournament_double', null=True, blank=True)
    tournament = ForeignKeyProtect(Tournaments, related_name='Tournament_member_doubles_tournament')

    objects = Tournament_member_doublesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Списки клубов-участников турнира'
        unique_together = (('club', 'club_double', 'tournament_double', 'tournament'),)
