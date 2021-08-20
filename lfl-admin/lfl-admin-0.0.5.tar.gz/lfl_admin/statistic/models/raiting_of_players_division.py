import logging

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from lfl_admin.competitions.models.divisions import Divisions
from lfl_admin.statistic.models.raiting_of_players import Raiting_of_players

logger = logging.getLogger(__name__)


class Raiting_of_players_divisionQuerySet(AuditQuerySet):
    pass


class Raiting_of_players_divisionManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
        }
        return res

    def get_queryset(self):
        return Raiting_of_players_divisionQuerySet(self.model, using=self._db)


class Raiting_of_players_division(AuditModel):
    division = ForeignKeyProtect(Divisions)
    raiting = ForeignKeyCascade(Raiting_of_players)

    objects = Raiting_of_players_divisionManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
