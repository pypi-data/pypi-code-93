import logging

from bitfield import BitField
from django.db.models import SmallIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, AuditModel
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.referees import Referees
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class PenaltiesQuerySet(AuditQuerySet):
    pass


class PenaltiesManager(AuditManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('action', 'action'),  # 1
            ('result', 'result'),  # 1
        ), default=1, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return PenaltiesQuerySet(self.model, using=self._db)


class Penalties(AuditModel):
    club = ForeignKeyProtect(Clubs)
    editor = ForeignKeyProtect(User, null=True, blank=True)
    match = ForeignKeyProtect(Calendar)
    minute = SmallIntegerField()
    player = ForeignKeyProtect(Players)
    props = PenaltiesManager.props()
    referee = ForeignKeyProtect(Referees)
    result = SmallIntegerField()
    tournament = ForeignKeyProtect(Tournaments)

    objects = PenaltiesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Пенальти'
