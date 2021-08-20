import logging

from django.db.models import SmallIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, AuditModel
from lfl_admin.competitions.models.card_types import Card_types
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class Player_tournament_cards_limitQuerySet(AuditQuerySet):
    pass


class Player_tournament_cards_limitManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'parent': record.parent.id if record.parent else None,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Player_tournament_cards_limitQuerySet(self.model, using=self._db)


class Player_tournament_cards_limit(AuditModel):
    card_type = ForeignKeyProtect(Card_types)
    count = SmallIntegerField()
    player = ForeignKeyProtect(Players)
    tournament = ForeignKeyProtect(Tournaments)

    objects = Player_tournament_cards_limitManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Хранение данных о "переборе" ж.к.'
