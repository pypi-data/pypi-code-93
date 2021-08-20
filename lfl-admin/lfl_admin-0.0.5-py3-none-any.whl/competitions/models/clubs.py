import logging

from bitfield import BitField
from django.db.models import DateField, SmallIntegerField

from isc_common.auth.models.user import User
from isc_common.common import undefined
from isc_common.datetime import DateToStr
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import Model_withOldIds
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefHierarcyManager, BaseRefHierarcyQuerySet
from lfl_admin.competitions.models.leagues import Leagues
from lfl_admin.region.models.regions import Regions

logger = logging.getLogger(__name__)


class ClubsQuerySet(BaseRefHierarcyQuerySet):
    pass


class ClubsManager(BaseRefHierarcyManager):

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('active', 'active'),  # 1
            ('national', 'national'),  # 1
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
        return BaseRefHierarcyQuerySet(self.model, using=self._db)


class Clubs(BaseRefHierarcy, Model_withOldIds):
    created_date = DateField(null=True, blank=True)
    editor = ForeignKeyProtect(User, related_name='Clubs_editor', null=True, blank=True)
    interregion = SmallIntegerField(null=True, blank=True)
    league = ForeignKeyProtect(Leagues)
    region = ForeignKeyProtect(Regions)

    props = ClubsManager.props()

    objects = ClubsManager()

    @classmethod
    def unknown(cls):
        res, _ = cls.objects.get_or_create(
            code=undefined,
            defaults=dict(
                name='Неопределенный',
                league=Leagues.unknown(),
                region=Regions.unknown()
            ))
        return res

    def __str__(self):
        return f'ID:{self.id} name: {self.name}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Лиги'
