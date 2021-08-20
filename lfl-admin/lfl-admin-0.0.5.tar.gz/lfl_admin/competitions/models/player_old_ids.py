import logging

from django.db.models import BigIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, AuditModel
from lfl_admin.competitions.models.players import Players

logger = logging.getLogger(__name__)


class Player_old_idsQuerySet(AuditQuerySet):
    pass


class Player_old_idsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Player_old_idsQuerySet(self.model, using=self._db)


class Player_old_ids(AuditModel):
    player = ForeignKeyProtect(Players)
    old_id = BigIntegerField(db_index=True)

    objects = Player_old_idsManager()

    @classmethod
    def get_payer_from_old_player(cls, old_player_id):
        player = cls.objects.getOptional(old_id=old_player_id)
        if player is None:
            return Players.unknown()
        else:
            return player.player

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Ссылки на старых Players'
        unique_together = (('player', 'old_id'),)
