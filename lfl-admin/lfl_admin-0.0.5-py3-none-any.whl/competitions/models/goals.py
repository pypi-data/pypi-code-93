import logging

from django.db.models import SmallIntegerField, IntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldId
from isc_common.models.audit_ex import AuditModelEx
from lfl_admin.competitions.models.assists import Assists
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.goals_type import Goals_type
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class GoalsQuerySet(AuditQuerySet):
    pass


class GoalsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return GoalsQuerySet(self.model, using=self._db)


class Goals(AuditModelEx, Model_withOldId):
    assist = ForeignKeyProtect(Assists)
    club = ForeignKeyProtect(Clubs, related_name='Goals_club')
    goal_club = ForeignKeyProtect(Clubs, related_name='Goals_goal_club')
    goal_type = ForeignKeyProtect(Goals_type)
    match = ForeignKeyProtect(Calendar)
    minute = IntegerField(null=True, blank=True)
    player = ForeignKeyProtect(Players)
    tournament = ForeignKeyProtect(Tournaments)

    objects = GoalsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Голы'
