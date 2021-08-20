import logging

from bitfield import BitField
from django.db.models import SmallIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldId
from isc_common.models.audit_ex import AuditModelEx
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class FoulsQuerySet(AuditQuerySet):
    pass


class FoulsManager(AuditManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('penalty', 'penalty'),  # 1
        ), default=0, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return FoulsQuerySet(self.model, using=self._db)


class Fouls(AuditModelEx, Model_withOldId):
    club = ForeignKeyProtect(Clubs)
    match = ForeignKeyProtect(Calendar)
    minute = SmallIntegerField()
    player = ForeignKeyProtect(Players)
    props = FoulsManager.props()
    tournament = ForeignKeyProtect(Tournaments)

    objects = FoulsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Возможно таблица, хранящяя события, связанные с минутами на которых были исполнены пенальти. '
