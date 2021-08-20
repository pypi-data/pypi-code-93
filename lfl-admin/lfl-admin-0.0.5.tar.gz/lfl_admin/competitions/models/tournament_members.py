import logging

from bitfield import BitField
from django.db.models import SmallIntegerField, IntegerField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from lfl_admin.competitions.models.clubs import Clubs

logger = logging.getLogger(__name__)


class Tournament_membersQuerySet(AuditQuerySet):
    pass


class Tournament_membersManager(AuditManager):
    @classmethod
    def props(cls):
        return BitField(flags=(
            ('game_over', 'game_over'),  # 1
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
        return Tournament_membersQuerySet(self.model, using=self._db)


class Tournament_members(AuditModel):
    club = ForeignKeyProtect(Clubs)
    props = Tournament_membersManager.props()
    position = SmallIntegerField()
    tournament_id_old = IntegerField(db_index=True, null=True, blank=True)
    club_id_old = IntegerField(db_index=True, null=True, blank=True)

    objects = Tournament_membersManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Списки клубов-участников турнира'
        unique_together = (('club', 'props', 'position', 'tournament_id_old', 'club_id_old'),)
