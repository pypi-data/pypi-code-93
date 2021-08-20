import logging

from django.db.models import DateTimeField, BigIntegerField
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from lfl_admin.competitions.models.players import Players

logger = logging.getLogger(__name__)


class Players_change_historyQuerySet(AuditQuerySet):
    pass


class Players_change_historyManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Players_change_historyQuerySet(self.model, using=self._db)


class Players_change_history(AuditModel):
    date = DateTimeField()
    date_old = DateTimeField()
    editor = ForeignKeyProtect(User, null=True, blank=True)
    editor_id_old = BigIntegerField(db_index=True, null=True, blank=True)
    player = ForeignKeyProtect(Players)
    player_id_old = BigIntegerField(db_index=True, null=True, blank=True)

    objects = Players_change_historyManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Контроль допуска игроков к играм'
        unique_together = (('date', 'editor', 'player', 'date_old', 'editor_id_old', 'player_id_old'),)
