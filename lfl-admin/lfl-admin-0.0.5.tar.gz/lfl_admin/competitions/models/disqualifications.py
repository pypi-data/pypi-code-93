import logging

from bitfield import BitField
from django.db.models import DateField, SmallIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, Model_withOldId
from isc_common.models.audit_ex import AuditModelEx
from lfl_admin.competitions.models.cards import Cards
from lfl_admin.competitions.models.disqualification_types import Disqualification_types
from lfl_admin.competitions.models.disqualification_zones import Disqualification_zones
from lfl_admin.competitions.models.leagues import Leagues
from lfl_admin.competitions.models.players import Players
from lfl_admin.competitions.models.tournaments import Tournaments
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class DisqualificationsQuerySet(AuditQuerySet):
    pass


class DisqualificationsManager(AuditManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 1
        ), default=1, db_index=True)

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
        return DisqualificationsQuerySet(self.model, using=self._db)


class Disqualifications(AuditModelEx, Model_withOldId):
    admin = ForeignKeyProtect(User, related_name='Disqualifications_creator_admin')
    card = ForeignKeyProtect(Cards)
    disqualification_type = ForeignKeyProtect(Disqualification_types)
    edit_date = DateField(blank=True, null=True)
    from_date = DateField(blank=True, null=True)
    matches = SmallIntegerField(blank=True, null=True)
    personal_league = ForeignKeyProtect(Leagues)
    personal_region = ForeignKeyProtect(Regions)
    player = ForeignKeyProtect(Players)
    props = DisqualificationsManager.props()
    to_date = DateField(blank=True, null=True)
    tournament = ForeignKeyProtect(Tournaments)
    zone = ForeignKeyProtect(Disqualification_zones)

    objects = DisqualificationsManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Список дисквалификаций'
