import logging

from django.db.models import SmallIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldId, AuditManager, AuditQuerySet
from isc_common.models.audit_ex import AuditModelEx
from lfl_admin.competitions.models.calendar import Calendar
from lfl_admin.competitions.models.card_types import Card_types
from lfl_admin.competitions.models.clubs import Clubs
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.referees import Referees
from lfl_admin.competitions.models.tournaments import Tournaments

logger = logging.getLogger(__name__)


class CardsQuerySet(AuditQuerySet):
    pass


class CardsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return CardsQuerySet(self.model, using=self._db)


class Cards(AuditModelEx, Model_withOldId):
    card_type = ForeignKeyProtect(Card_types)
    club = ForeignKeyProtect(Clubs)
    match = ForeignKeyProtect(Calendar)
    minute = SmallIntegerField()
    player = ForeignKeyProtect(Players)
    referee = ForeignKeyProtect(Referees)
    tournament = ForeignKeyProtect(Tournaments)

    objects = CardsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            card_type=Card_types.unknown(),
            club=Clubs.unknown(),
            match=Calendar.unknown(),
            minute=0,
            player=Players.unknown(),
            referee=Referees.unknown(),
            tournament=Tournaments.unknown()
        )
        return res

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Карточки игроков в сыгранных матчах: три типа. 1. жёлтая к. 2. Вторая ж.к. 3. красная карточка'
