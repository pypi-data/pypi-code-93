import logging

from bitfield import BitField
from django.db.models import BigIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, AuditModel
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.formation import Formation
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class Player_historiesQuerySet(AuditQuerySet):
    pass


class Player_historiesManager(AuditManager):
    @classmethod
    def props(cls):
        return BitField(flags=(
            ('game_started', 'game_started'),  # 0
            ('substituted', 'substituted'),  # 1
            ('keeper', 'keeper'),  # 2
            ('hidden', 'Скрывать ФИО'),  # 3
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
        return Player_historiesQuerySet(self.model, using=self._db)


class Player_histories(AuditModel):
    club = ForeignKeyProtect(Clubs)
    club_id_old = BigIntegerField(db_index=True, null=True, blank=True)
    editor = ForeignKeyProtect(User, null=True, blank=True)
    formation = ForeignKeyProtect(Formation)
    match = ForeignKeyProtect(Calendar)
    match_id_old = BigIntegerField(db_index=True, null=True, blank=True)
    num = CodeField(null=True, blank=True)
    player = ForeignKeyProtect(Players)
    player_id_old = BigIntegerField(db_index=True, null=True, blank=True)
    props = Player_historiesManager.props()
    tournament = ForeignKeyProtect(Tournaments)

    objects = Player_historiesManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Данные об участии игрока в конкретном матче'
        unique_together = (('club', 'player', 'match'), ('club_id_old', 'player_id_old', 'match_id_old'),)
        # unique_together = (('club', 'player', 'match'),)
