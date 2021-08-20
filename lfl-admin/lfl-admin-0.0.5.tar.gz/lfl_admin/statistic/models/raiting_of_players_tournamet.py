import logging

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from lfl_admin.competitions.models.tournaments import Tournaments
from lfl_admin.statistic.models.raiting_of_players import Raiting_of_players

logger = logging.getLogger(__name__)


class Raiting_of_players_tournametQuerySet(AuditQuerySet):
    pass


class Raiting_of_players_tournametManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
        }
        return res

    def get_queryset(self):
        return Raiting_of_players_tournametQuerySet(self.model, using=self._db)


class Raiting_of_players_tournamet(AuditModel):
    tournament = ForeignKeyProtect(Tournaments)
    raiting = ForeignKeyCascade(Raiting_of_players)

    objects = Raiting_of_players_tournametManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
